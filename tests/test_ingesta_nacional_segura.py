"""Integration tests invoking the real CLI and SQLite writer on synthetic data."""
from pathlib import Path
import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'sistema/api/ingesta_nacional_segura.py'


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve(); self.source = self.root / 'source'
        (self.source / 'texto').mkdir(parents=True)
        self.output = self.root / 'candidate.db'; self.rows = []
        for i in (1, 2):
            data = f'ARTICULO 1. Texto sintetico {i}.'.encode()
            (self.source / 'texto' / f'{i}.txt').write_bytes(data)
            self.rows.append({'clave': str(i), 'archivo_texto': f'{i}.txt',
                              'sha256': hashlib.sha256(data).hexdigest(), 'tipo_norma': 'Ley',
                              'numero': str(i), 'titulo': f'Fixture {i}', 'fuente_url': f'https://example.org/{i}'})
        self.write_manifest()

    def write_manifest(self):
        self.manifest = self.source / 'normas.jsonl'
        self.manifest.write_text('\n'.join(json.dumps(r) for r in self.rows))
        self.digest = hashlib.sha256(self.manifest.read_bytes()).hexdigest()

    def run_cli(self, expected=2):
        p = subprocess.run([sys.executable, str(SCRIPT), '--source', str(self.source),
                            '--output', str(self.output), '--expected-records', str(expected),
                            '--manifest-sha256', self.digest], capture_output=True, text=True, timeout=20)
        self.assertNotIn('Traceback', p.stderr)
        return p.returncode, json.loads(p.stdout)

    def assert_rejected(self, expected=2):
        code, result = self.run_cli(expected)
        self.assertEqual(code, 2); self.assertFalse(result['ok']); self.assertFalse(self.output.exists())

    def test_valid_two_records_and_reader_sqlite(self):
        code, result = self.run_cli(); self.assertEqual(code, 0); self.assertEqual(result['written'], 2)
        with sqlite3.connect(self.output) as c:
            self.assertEqual(c.execute('select count(*) from documentos').fetchone()[0], 2)
            self.assertEqual(c.execute('select count(*) from documentos where vigente is null').fetchone()[0], 2)
            self.assertEqual(c.execute('pragma quick_check').fetchone()[0], 'ok')
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o600)
        self.assertFalse(result['publication_authorized'])

    def test_one_bad_record_does_not_publish_partial_candidate(self):
        (self.source / 'texto/2.txt').write_bytes(b'changed')
        self.assert_rejected()

    def test_missing_manifest_is_not_empty_success(self):
        self.manifest.unlink(); self.assert_rejected()

    def test_expected_count_not_adjusted_to_available_rows(self):
        self.assert_rejected(3)

    def test_explicit_empty_requires_zero_expected(self):
        self.rows = []; self.write_manifest(); self.assert_rejected(2)
        code, result = self.run_cli(0); self.assertEqual(code, 0); self.assertEqual(result['written'], 0)

    def test_manifest_digest_mismatch(self):
        self.digest = '0' * 64; self.assert_rejected()

    def test_duplicate_key_rejected(self):
        self.rows[1]['clave'] = '1'; self.write_manifest(); self.assert_rejected()

    def test_uid_collision_rejected(self):
        self.rows[1] = dict(self.rows[0], clave='other'); self.write_manifest(); self.assert_rejected()

    def test_existing_destination_is_not_overwritten(self):
        self.output.write_bytes(b'keep-me'); code, result = self.run_cli()
        self.assertEqual(code, 2); self.assertEqual(self.output.read_bytes(), b'keep-me')

    def test_text_root_symlink_rejected(self):
        (self.source / 'texto').rename(self.root / 'outside')
        (self.source / 'texto').symlink_to(self.root / 'outside', target_is_directory=True)
        self.assert_rejected()

    def test_incomplete_metadata_rejected(self):
        self.rows[1]['titulo'] = ''; self.write_manifest(); self.assert_rejected()


if __name__ == '__main__':
    unittest.main(verbosity=2)
