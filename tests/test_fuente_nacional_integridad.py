"""tests/test_fuente_nacional_integridad.py: synthetic reader regressions.

Run unchanged against the historical reader to demonstrate R1/R2 failures.
All filesystem paths and symlink targets belong to this test's temporary tree.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('national', ROOT / 'sistema/api/fuente_nacional.py')
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class NationalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.base = self.root / 'source'
        self.base.mkdir()
        (self.base / 'texto').mkdir()
        self.payload = 'Artículo sintético: 390000'.encode()
        (self.base / 'texto/law.txt').write_bytes(self.payload)
        self.row = {'archivo_texto': 'law.txt', 'sha256': hashlib.sha256(self.payload).hexdigest(), 'clave': 'synthetic'}
        (self.base / 'normas.jsonl').write_text(json.dumps(self.row) + '\n', encoding='utf-8')

    def test_valid(self):
        f = m.FuenteNacional(self.base)
        self.assertEqual(f.resolver(self.row)['texto'], self.payload.decode())
        self.assertEqual(f.resueltas, 1)
        self.assertEqual(f.censo, 1)

    def test_changed_text(self):
        (self.base / 'texto/law.txt').write_bytes(b'changed')
        f = m.FuenteNacional(self.base)
        self.assertIsNone(f.resolver(self.row))
        self.assertEqual(f.resueltas, 0)
        self.assertEqual(f.informe()['sin_texto'], 1)

    def test_bad_hashes(self):
        for h in [None, '', 'a'*12, 'g'*64, '0'*64, 'A'*64]:
            with self.subTest(h=h):
                self.assertIsNone(m.FuenteNacional(self.base).resolver({**self.row, 'sha256': h}))

    def test_traversal_and_absolute_paths(self):
        outside = self.root / 'outside.txt'
        outside.write_bytes(self.payload)
        for name in ['../outside.txt', str(outside), 'x\\law.txt', '', '..']:
            with self.subTest(name=name):
                self.assertIsNone(m.FuenteNacional(self.base).resolver({**self.row, 'archivo_texto': name}))

    def test_symlink(self):
        (self.base / 'texto/link.txt').symlink_to(self.base / 'texto/law.txt')
        self.assertIsNone(m.FuenteNacional(self.base).resolver({**self.row, 'archivo_texto': 'link.txt'}))

    def test_missing_file(self):
        self.assertIsNone(m.FuenteNacional(self.base).resolver({**self.row, 'archivo_texto': 'absent.txt'}))

    def test_invalid_utf8(self):
        payload = b'\xff'
        (self.base / 'texto/law.txt').write_bytes(payload)
        self.assertIsNone(m.FuenteNacional(self.base).resolver({**self.row, 'sha256': hashlib.sha256(payload).hexdigest()}))

    def test_empty_text(self):
        (self.base / 'texto/law.txt').write_bytes(b' ')
        self.assertIsNone(m.FuenteNacional(self.base).resolver({**self.row, 'sha256': hashlib.sha256(b' ').hexdigest()}))

    def test_manifest_comments_and_count(self):
        (self.base / 'normas.jsonl').write_text('# comment\n{"clave":"one"}\n')
        self.assertEqual(m.FuenteNacional(self.base).censo, 1)

    def test_malformed_manifest_not_silently_skipped(self):
        for content in ['{broken', '[]']:
            (self.base / 'normas.jsonl').write_text(content)
            with self.assertRaises(ValueError):
                m.FuenteNacional(self.base)

    def test_unknown_status_is_not_inferred(self):
        self.assertEqual(m.revisiones_de({})[0]['tipo'], 'vigencia_sin_senales')
        self.assertEqual(m.revisiones_de({'senales_de_cambio': {'modificad': 1}})[0]['tipo'], 'posible_cambio_normativo')

    def test_missing_manifest_rejected_before_source_is_available(self):
        (self.base / 'normas.jsonl').unlink()
        with self.assertRaises(ValueError):
            m.FuenteNacional(self.base)

    def test_explicit_empty_manifest_is_a_valid_empty_census(self):
        for text in ['', '\n# deliberately empty source\n']:
            with self.subTest(text=text):
                (self.base / 'normas.jsonl').write_text(text)
                f = m.FuenteNacional(self.base)
                self.assertEqual(f.censo, 0)
                self.assertEqual(f.informe()['sin_texto'], 0)

    def test_text_directory_symlink_is_rejected_even_when_static(self):
        outside = self.root / 'outside'
        (self.base / 'texto').rename(outside)
        (self.base / 'texto').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            m.FuenteNacional(self.base)

    def test_base_directory_symlink_is_rejected(self):
        alias = self.root / 'alias'
        alias.symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(ValueError):
            m.FuenteNacional(alias)

    def test_parent_directory_symlink_is_rejected(self):
        parent = self.root / 'parent'
        parent.mkdir()
        self.base.rename(parent / 'source')
        alias = self.root / 'alias'
        alias.symlink_to(parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            m.FuenteNacional(alias / 'source')

    def test_manifest_symlink_is_rejected(self):
        outside = self.root / 'outside.jsonl'
        (self.base / 'normas.jsonl').rename(outside)
        (self.base / 'normas.jsonl').symlink_to(outside)
        with self.assertRaises(ValueError):
            m.FuenteNacional(self.base)

    def test_missing_text_directory_is_configuration_error(self):
        (self.base / 'texto/law.txt').unlink()
        (self.base / 'texto').rmdir()
        with self.assertRaises(ValueError):
            m.FuenteNacional(self.base)

    def test_manifest_directory_is_configuration_error(self):
        (self.base / 'normas.jsonl').unlink()
        (self.base / 'normas.jsonl').mkdir()
        with self.assertRaises(ValueError):
            m.FuenteNacional(self.base)

    def test_replaced_text_root_rejected_on_next_read(self):
        f = m.FuenteNacional(self.base)
        outside = self.root / 'outside'
        (self.base / 'texto').rename(outside)
        (self.base / 'texto').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            f.resolver(self.row)


if __name__ == '__main__':
    unittest.main(verbosity=2)
