"""sistema/api/fuente_nacional.py: fail-closed national-source integrity.

The digest applies to exact UTF-8 text bytes, not the official PDF. A selected
source requires a real base directory, a real texto directory and an existing
regular normas.jsonl. Explicit empty manifests are allowed. Symlinks in source
paths (including parent directories) are forbidden. The source tree must remain
immutable for the batch: these checks do not promise race-free same-UID access.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
import re
from typing import Mapping


class SourceConfigurationError(ValueError):
    """The selected source cannot be loaded; callers must abort its ingestion."""


def _require_real_path(path: Path, *, directory: bool) -> Path:
    """Validate every lexical component before resolving; reject symlinks.

    Return the resolved existing path of the required type. Missing paths,
    inaccessible paths and nonregular manifests raise SourceConfigurationError.
    This is startup configuration validation, not filesystem race protection.
    """
    absolute = path.absolute()
    try:
        for component in (absolute, *absolute.parents):
            if component.is_symlink():
                raise SourceConfigurationError('source path must not contain symlinks')
        resolved = absolute.resolve(strict=True)
        valid = resolved.is_dir() if directory else resolved.is_file()
        if not valid:
            raise SourceConfigurationError('source path has wrong filesystem type')
        return resolved
    except (OSError, RuntimeError) as exc:
        raise SourceConfigurationError('source path missing or inaccessible') from exc


def _lineas_json(ruta: Path) -> list[dict[str, object]]:
    """Load an existing regular manifest, retaining an explicit empty census.

    Missing manifests are configuration failures, never an empty list. Invalid
    UTF-8, malformed JSON and non-object rows raise ValueError rather than
    silently reducing the census. Comments and blank lines are permitted.
    """
    manifest = _require_real_path(ruta, directory=False)
    try:
        content = manifest.read_text(encoding='utf-8', errors='strict')
    except (OSError, UnicodeError) as exc:
        raise SourceConfigurationError('manifest unreadable or not strict UTF-8') from exc
    salida: list[dict[str, object]] = []
    for number, line in enumerate(content.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f'manifest line {number} is invalid') from exc
        if not isinstance(row, dict):
            raise ValueError(f'manifest line {number} must be an object')
        salida.append(row)
    return salida


class FuenteNacional:
    """Read a mandatory manifest from an immutable, symlink-free source tree.

    Constructor errors must propagate: an expected source is not optional just
    because its directory or manifest is missing. An existing empty manifest
    deliberately means zero records. Resolver retains texto/ruta or None.
    """

    def __init__(self, base: Path):
        """Load source configuration or raise ValueError; perform no writes."""
        self.base = _require_real_path(Path(base), directory=True)
        self._text_root = _require_real_path(self.base / 'texto', directory=True)
        self.normas = _lineas_json(self.base / 'normas.jsonl')
        self.faltantes: list[dict[str, object]] = []
        self.resueltas = 0

    @property
    def censo(self) -> int:
        """Return manifest record count, including an explicitly empty manifest."""
        return len(self.normas)

    def resolver(self, fila: Mapping[str, object]) -> dict[str, object] | None:
        """Verify exact text bytes; record row failures without file contents.

        Source configuration failures raise ValueError. Individual bad names,
        digests, files and text return None and append a bounded reason.
        """
        if not isinstance(fila, Mapping):
            raise TypeError('manifest row must be a mapping')
        root = _require_real_path(self.base / 'texto', directory=True)
        if root != self._text_root:
            raise SourceConfigurationError('source text root changed')
        name = fila.get('archivo_texto')
        expected = fila.get('sha256')
        reason = None
        if (not isinstance(name, str) or not name or len(name) > 255
                or '/' in name or '\\' in name or '\x00' in name or name in ('.', '..')):
            reason = 'invalid text filename'
        elif not isinstance(expected, str) or re.fullmatch(r'[0-9a-f]{64}', expected) is None:
            reason = 'missing or malformed full text SHA256'
        else:
            path = root / name
            try:
                if path.is_symlink() or path.resolve().parent != root:
                    reason = 'text path outside immutable source directory'
                else:
                    payload = path.read_bytes()
                    actual = hashlib.sha256(payload).hexdigest()
                    if not hmac.compare_digest(actual, expected):
                        reason = 'text SHA256 mismatch'
                    else:
                        text = payload.decode('utf-8', errors='strict')
                        if not text.strip():
                            reason = 'empty text'
                        else:
                            self.resueltas += 1
                            return {'texto': text, 'ruta': path}
            except (OSError, UnicodeError):
                reason = 'text unavailable or not strict UTF-8'
        self.faltantes.append({'clave': fila.get('clave'), 'motivo': reason})
        return None

    def informe(self) -> dict[str, object]:
        """Report counts and the first twenty row failures for a loaded source."""
        return {'censo_manifest': self.censo, 'resueltos_por_ocr': 0,
                'resueltos_por_extraccion': self.resueltas,
                'sin_texto': len(self.faltantes), 'faltantes': self.faltantes[:20]}


def revisiones_de(fila: Mapping[str, object]) -> list[dict[str, str]]:
    """Return amendment hints for human review, never infer legal status."""
    signals = fila.get('senales_de_cambio') or {}
    if not isinstance(signals, dict):
        raise ValueError('senales_de_cambio must be an object')
    present = {k: v for k, v in signals.items() if v}
    title = str(fila.get('titulo') or '')[:200]
    if present:
        return [{'tipo': 'posible_cambio_normativo',
                 'detalle': 'el texto menciona ' + ', '.join(k + ' x' + str(v) for k, v in sorted(present.items())) + ': revisar si esta norma abroga o modifica a otras, y si otra la abroga',
                 'contexto': title}]
    return [{'tipo': 'vigencia_sin_senales',
             'detalle': 'el texto no menciona abrogaciones NI eso prueba que este vigente: una norma no declara su propia abrogacion por una ley posterior',
             'contexto': title}]
