"""Build a NEW national-only SQLite candidate; never replace a live database.

Requires externally selected manifest digest and expected record count. Uses
PR3's reader unchanged. Byte identity does not establish legal validity. The
source tree is trusted and immutable throughout the batch (no same-UID race
protection). The legacy API must not serve this file without release approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
from typing import Sequence
from fuente_nacional import FuenteNacional, SourceConfigurationError, revisiones_de
from ingesta import Corpus, Documento


class BatchRejected(ValueError):
    """An expected source is incomplete or inconsistent; no candidate is published."""


def build(base: Path, output: Path, expected_count: int, manifest_sha256: str) -> dict:
    """Verify all records, build in temporary space and publish without overwrite.

    Raises ValueError/OSError on rejection. Destination is a national-only
    candidate, not a full Corpus replacement. Never modifies original files.
    """
    if type(expected_count) is not int or expected_count < 0:
        raise BatchRejected('invalid expected count')
    if not isinstance(manifest_sha256, str) or len(manifest_sha256) != 64 or any(c not in '0123456789abcdef' for c in manifest_sha256):
        raise BatchRejected('full manifest digest required')
    if os.path.lexists(output):
        raise BatchRejected('destination already exists')
    source = FuenteNacional(base)
    manifest = source.base / 'normas.jsonl'
    if hashlib.sha256(manifest.read_bytes()).hexdigest() != manifest_sha256:
        raise BatchRejected('manifest digest mismatch')
    if source.censo != expected_count:
        raise BatchRejected('manifest count mismatch')
    documents = []
    keys, uids = set(), set()
    for number, row in enumerate(source.normas, 1):
        key = row.get('clave')
        if not isinstance(key, str) or not key.strip() or key in keys:
            raise BatchRejected(f'row {number}: missing or duplicate identity')
        keys.add(key)
        result = source.resolver(row)
        if result is None:
            raise BatchRejected(f'row {number}: text rejected')
        for field in ('fuente_url', 'tipo_norma', 'numero', 'titulo'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise BatchRejected(f'row {number}: incomplete metadata')
        doc = Documento(fuente_id='lexivox_nacional', jurisdiccion='nacional',
                        tipo_norma=row['tipo_norma'], numero=row['numero'],
                        texto=result['texto'], fuente_url=row['fuente_url'],
                        anio=str(row.get('anio') or ''), titulo=row['titulo'],
                        materia=str(row.get('materia') or ''),
                        organo='Estado Plurinacional de Bolivia',
                        sha256=row['sha256'], archivo=result['ruta'].name,
                        via_texto='html', confianza='no_verificada',
                        revision=revisiones_de(row))
        if doc.uid() in uids:
            raise BatchRejected(f'row {number}: legacy UID collision; reconcile aliases first')
        uids.add(doc.uid()); documents.append(doc)
    if len(documents) != expected_count or source.faltantes:
        raise BatchRejected('incomplete batch')
    if hashlib.sha256(manifest.read_bytes()).hexdigest() != manifest_sha256:
        raise BatchRejected('manifest changed during verification')
    # All records have been checked before the writer sees the first document.
    with tempfile.TemporaryDirectory(prefix='.national-candidate-', dir=output.parent) as tmp:
        staging = Path(tmp) / 'work.db'
        writer = Corpus(str(staging))
        try:
            writer.registrar_fuente('lexivox_nacional', 'LexiVox (secondary transcription)',
                                    'nacional', '', 'Estado Plurinacional de Bolivia', 'https://www.lexivox.org')
            for doc in documents:
                writer.agregar(doc)
            writer.cerrar()
            actual = {r[0] for r in writer.con.execute('SELECT uid FROM documentos')}
            if actual != uids or writer.reemplazados:
                raise BatchRejected('database identity mismatch')
            if writer.con.execute('PRAGMA quick_check').fetchall()[0][0] != 'ok':
                raise BatchRejected('database consistency check failed')
            summary = {'scope': 'national-only candidate, not production',
                       'expected': expected_count, 'written': len(actual),
                       'rejected': len(source.faltantes), 'manifest_sha256': manifest_sha256,
                       'uid_set_sha256': hashlib.sha256('\n'.join(sorted(actual)).encode()).hexdigest(),
                       'legal_validity': 'NOT_MEASURED', 'authority': 'secondary',
                       'publication_authorized': False}
            writer.con.execute('CREATE TABLE candidate_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
            writer.con.execute('INSERT INTO candidate_metadata VALUES (?, ?)', ('contract', json.dumps(summary, sort_keys=True)))
            writer.con.commit()
            final = Path(tmp) / 'complete.db'
            with sqlite3.connect(final) as target:
                writer.con.backup(target)
            os.chmod(final, 0o600)
            with final.open('rb') as stream:
                os.fsync(stream.fileno())
            summary['database_sha256'] = hashlib.sha256(final.read_bytes()).hexdigest()
            os.link(final, output)  # Exclusive: an existing destination is never replaced.
        finally:
            writer.con.close()
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    """CLI returning JSON and nonzero status for every rejected source."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expected-records', type=int, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    args = parser.parse_args(argv)
    try:
        result = build(args.source, args.output, args.expected_records, args.manifest_sha256)
    except (ValueError, OSError, sqlite3.Error) as exc:
        # Never print document contents or filesystem exception details.
        print(json.dumps({'ok': False, 'error': type(exc).__name__, 'candidate_published': False}))
        return 2
    print(json.dumps({'ok': True, **result}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
