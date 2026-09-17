"""Regression of the actual national reader using only synthetic text."""
import hashlib
import importlib.util
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
        self.base = Path(self.temp.name)
        (self.base / 'texto').mkdir()
        self.payload = 'Artículo sintético: 390000'.encode()
        (self.base / 'texto/law.txt').write_bytes(self.payload)
        self.row = {'archivo_texto': 'law.txt', 'sha256': hashlib.sha256(self.payload).hexdigest(), 'clave': 'synthetic'}

    def test_valid(self):
        f = m.FuenteNacional(self.base)
        self.assertEqual(f.resolver(self.row)['texto'], self.payload.decode())
        self.assertEqual(f.resueltas, 1)

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
        outside = self.base / 'outside.txt'
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
        b = b'\xff'
        (self.base / 'texto/law.txt').write_bytes(b)
        self.assertIsNone(m.FuenteNacional(self.base).resolver({**self.row, 'sha256': hashlib.sha256(b).hexdigest()}))

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


if __name__ == '__main__':
    unittest.main(verbosity=2)
