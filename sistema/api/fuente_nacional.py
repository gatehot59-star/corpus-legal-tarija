"""National source adapter recovered from PR1, with fail-closed text integrity.

The declared digest applies to exact UTF-8 text bytes, not the official PDF.
Legal status is still unknown; a valid digest is not a legal assessment.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
import re
from typing import Mapping


def _lineas_json(ruta: Path) -> list[dict[str, object]]:
    if not ruta.exists():
        return []
    salida: list[dict[str, object]] = []
    for number, line in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"manifest line {number} is invalid") from exc
        if not isinstance(row, dict):
            raise ValueError(f"manifest line {number} must be an object")
        salida.append(row)
    return salida


class FuenteNacional:
    """Read national records with exact digests; rejection enters faltantes.

    Compatible resolver result: {'texto': str, 'ruta': Path} or None.
    No downloads, writes or production migrations are performed here.
    Local source directories must remain immutable during an ingestion batch.
    """

    def __init__(self, base: Path):
        self.base = Path(base)
        self.normas = _lineas_json(self.base / 'normas.jsonl')
        self.faltantes: list[dict[str, object]] = []
        self.resueltas = 0

    @property
    def censo(self) -> int:
        """Return manifest records, not successful extractions."""
        return len(self.normas)

    def resolver(self, fila: Mapping[str, object]) -> dict[str, object] | None:
        """Read and verify exact text bytes, rejecting missing/malformed hashes.

        Records a bounded failure reason, never the file contents. Malformed
        manifest rows fail loading rather than silently reducing the census.
        """
        if not isinstance(fila, Mapping):
            raise TypeError('manifest row must be a mapping')
        name = fila.get('archivo_texto')
        expected = fila.get('sha256')
        reason = None
        root = (self.base / 'texto').resolve()
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
        """Report counts plus the first twenty rejection diagnostics."""
        return {'censo_manifest': self.censo, 'resueltos_por_ocr': 0,
                'resueltos_por_extraccion': self.resueltas,
                'sin_texto': len(self.faltantes), 'faltantes': self.faltantes[:20]}


def revisiones_de(fila: Mapping[str, object]) -> list[dict[str, str]]:
    """Keep amendment signals as human-review hints, never status decisions."""
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
