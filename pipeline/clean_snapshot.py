"""Build an isolated full-corpus candidate with reviewed, UID-preserving cleanup.

No network, migration of a live database or publication. Source database and
mapping are trusted inputs and must stay immutable during this operation.
Existing UID/doc_id and provenance aliases are retained. Old document/chunk
rows and the new extraction are archived in a separate version ledger.
"""
from __future__ import annotations
import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'sistema/api'))
from ingesta import trozar
from legal_html import extract, MAX_BYTES


class CandidateError(ValueError):
    """Candidate cannot preserve the requested identity or source conditions."""


def uid_digest(connection: sqlite3.Connection) -> tuple[int, str]:
    """Return count and SHA256 of ordered UID set, not a content digest."""
    ids = [r[0] for r in connection.execute('SELECT uid FROM documentos ORDER BY uid')]
    return len(ids), hashlib.sha256('\n'.join(ids).encode()).hexdigest()


def build(source_db: Path, output: Path, changes: list[dict], expected_count: int,
          expected_uid_sha256: str) -> dict:
    """Create a NEW full-copy candidate; reject any failed precondition.

    Each change supplies uid, old_text_sha256, source_url, original_sha256,
    expected_title and original_html(bytes). The old digest is the currently
    indexed text digest for national LexiVox records only. Legal validity is not
    inferred; candidate reader/API compatibility must be tested before release.
    """
    if type(expected_count) is not int or expected_count < 1 or not changes:
        raise CandidateError('explicit nonempty scope required')
    if os.path.lexists(output):
        raise CandidateError('destination exists')
    if not source_db.is_file() or source_db.is_symlink():
        raise CandidateError('regular source database required')
    if not isinstance(changes, list) or len(changes) > 100:
        raise CandidateError('batch must contain 1 to 100 mappings')
    with tempfile.TemporaryDirectory(prefix='.corpus-clean-', dir=output.parent) as td:
        candidate = Path(td) / 'candidate.db'
        with closing(sqlite3.connect('file:' + quote(str(source_db.resolve())) + '?mode=ro', uri=True)) as source:
            source.execute('PRAGMA query_only=ON')
            with closing(sqlite3.connect(candidate)) as target:
                source.backup(target)
        with closing(sqlite3.connect(candidate)) as db:
            db.row_factory = sqlite3.Row
            if uid_digest(db) != (expected_count, expected_uid_sha256):
                raise CandidateError('source identity set mismatch')
            db.execute('PRAGMA foreign_keys=ON')
            db.execute('BEGIN IMMEDIATE')
            db.execute('CREATE TABLE IF NOT EXISTS corpus_cleanup_versions (uid TEXT NOT NULL, version_sha256 TEXT NOT NULL, prior_document_json TEXT NOT NULL, prior_chunks_json TEXT NOT NULL, extraction_json TEXT NOT NULL, PRIMARY KEY(uid,version_sha256))')
            db.execute('CREATE TABLE IF NOT EXISTS corpus_candidate_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
            seen = set()
            summaries = []
            for mapping in changes:
                uid = mapping['uid']
                if uid in seen:
                    raise CandidateError('duplicate mapping')
                seen.add(uid)
                row = db.execute('SELECT * FROM documentos WHERE uid=?', (uid,)).fetchone()
                if row is None or row['fuente_id'] != 'lexivox_nacional':
                    raise CandidateError('unknown or unsupported source identity')
                if row['sha256'] != mapping['old_text_sha256'] or row['fuente_url'] != mapping['source_url']:
                    raise CandidateError('stale mapping or source mismatch')
                result = extract(mapping['original_html'], mapping['original_sha256'], mapping['expected_title'])
                if result['text_sha256'] == row['sha256']:
                    raise CandidateError('no new text version')
                chunks = [dict(r) for r in db.execute('SELECT * FROM chunks WHERE uid=? ORDER BY CAST(nro AS INTEGER)', (uid,))]
                if not chunks:
                    raise CandidateError('prior chunks unavailable')
                db.execute('INSERT INTO corpus_cleanup_versions VALUES (?,?,?,?,?)',
                           (uid, result['text_sha256'], json.dumps(dict(row), ensure_ascii=False, sort_keys=True),
                            json.dumps(chunks, ensure_ascii=False, sort_keys=True),
                            json.dumps(result, ensure_ascii=False, sort_keys=True)))
                db.execute('DELETE FROM chunks WHERE uid=?', (uid,))
                heading = ' | '.join(str(row[k] or '') for k in ('numero','tipo_norma','titulo','materia','sala','anio','partes'))
                cleaned = trozar(result['text'])
                if not cleaned:
                    raise CandidateError('empty extraction')
                for number, text in enumerate(cleaned, 1):
                    # Old citation expansions referred to old offsets/text. Do not reuse.
                    db.execute('INSERT INTO chunks(cuerpo,citas,encabezado,uid,doc_id,nro) VALUES(?,?,?,?,?,?)',
                               (text, '', heading if number == 1 else '', uid, row['doc_id'], number))
                db.execute('UPDATE documentos SET sha256=?,chars=?,via_texto=?,confianza=? WHERE uid=?',
                           (result['text_sha256'],len(result['text']),'html','no_verificada',uid))
                db.execute('INSERT INTO revision(uid,tipo,detalle,contexto,resuelto) VALUES(?,?,?,?,0)',
                           (uid,'cleanup_release_review','New text version; source/HTML authority and release review required',''))
                summaries.append({'uid':uid,'doc_id':row['doc_id'],'old_sha256':row['sha256'],
                                  'new_sha256':result['text_sha256'],'old_chunks':len(chunks),
                                  'new_chunks':len(cleaned),'new_chars':len(result['text'])})
            if uid_digest(db) != (expected_count, expected_uid_sha256):
                raise CandidateError('identity changed')
            if db.execute('PRAGMA foreign_key_check').fetchall():
                raise CandidateError('foreign key violation')
            info = {'profile':'corpus-cleanup-candidate-v1','document_count':expected_count,
                    'uid_set_sha256':expected_uid_sha256,'changed':summaries,'publication_authorized':False,
                    'warning':'Old links keep UID, but offset-based links are revision-specific. Legacy API authority labeling is NOT fixed.'}
            db.execute('INSERT OR REPLACE INTO corpus_candidate_state VALUES (?,?)', ('cleanup',json.dumps(info,sort_keys=True)))
            db.commit()
            if [r[0] for r in db.execute('PRAGMA quick_check')] != ['ok']:
                raise CandidateError('SQLite integrity failed')
            db.execute("INSERT INTO chunks(chunks) VALUES('integrity-check')")
            db.commit()
        os.chmod(candidate,0o600)
        with candidate.open('rb') as stream:
            os.fsync(stream.fileno())
        os.link(candidate,output)
    return info


def main() -> int:
    """Run a pinned local mapping and emit a redacted outcome, no existing writes."""
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-db',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--mapping',type=Path,required=True)
    ap.add_argument('--mapping-sha256',required=True)
    ap.add_argument('--expected-count',type=int,required=True)
    ap.add_argument('--expected-uid-sha256',required=True)
    args=ap.parse_args()
    try:
        with args.mapping.open('rb') as f:raw=f.read(1024*1024+1)
        if len(raw)>1024*1024 or hashlib.sha256(raw).hexdigest()!=args.mapping_sha256:
            raise CandidateError('mapping digest or size mismatch')
        mappings=json.loads(raw)
        if not isinstance(mappings,list) or not 1<=len(mappings)<=100:
            raise CandidateError('invalid mapping list')
        for item in mappings:
            name=item.pop('html_file')
            if not isinstance(name,str) or Path(name).name!=name or '\\' in name or name in ('.','..'):
                raise CandidateError('invalid input filename')
            path=args.mapping.parent/name
            if path.is_symlink():raise CandidateError('symlink input forbidden')
            with path.open('rb') as f:item['original_html']=f.read(MAX_BYTES+1)
        info=build(args.source_db,args.output,mappings,args.expected_count,args.expected_uid_sha256)
    except (ValueError,OSError,sqlite3.Error,KeyError,TypeError) as exc:
        print(json.dumps({'ok':False,'error':type(exc).__name__}));return 2
    print(json.dumps({'ok':True,**info},sort_keys=True));return 0


if __name__=='__main__':raise SystemExit(main())
