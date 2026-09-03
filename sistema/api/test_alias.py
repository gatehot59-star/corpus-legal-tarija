import sqlite3
import unittest

from alias import auditar, instalar, por_hash, registrar


class AliasTest(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.con.executescript("""
        CREATE TABLE documentos (
          doc_id INTEGER PRIMARY KEY, uid TEXT, titulo TEXT,
          tipo_norma TEXT, numero TEXT
        );
        """)
        instalar(self.con)
        self.con.execute(
            "INSERT INTO documentos(uid,titulo,tipo_norma,numero) VALUES(?,?,?,?)",
            ("dep-tar-ley-022-abcd1234", "Ley 022", "Ley", "022"),
        )
        self.con.commit()

    def tearDown(self):
        self.con.close()

    def test_same_text_keeps_two_sources(self):
        self.assertTrue(registrar(self.con, doc_id=1, uid="dep-tar-ley-022-abcd1234",
                                  fuente_id="gaceta", fuente_url="https://a/022.pdf",
                                  texto="ARTICULO 1\nTexto", archivo="a.pdf"))
        self.assertTrue(registrar(self.con, doc_id=1, uid="dep-tar-ley-022-abcd1234",
                                  fuente_id="genesis", fuente_url="https://b/022.pdf",
                                  texto="ARTICULO 1\nTexto", archivo="b.pdf"))
        self.assertEqual(len(por_hash(self.con, por_hash(self.con,
                         __import__('hashlib').sha256(b"ARTICULO 1\nTexto").hexdigest())[0]["sha256"])), 2)
        self.assertEqual(auditar(self.con), {
            "documentos_canonicos": 1,
            "alias_procedencia": 2,
            "hashes_con_multiples_procedencias": 1,
        })

    def test_exact_retry_is_idempotent(self):
        args = dict(doc_id=1, uid="u", fuente_id="gaceta", fuente_url="https://a",
                    texto="igual")
        self.assertTrue(registrar(self.con, **args))
        self.assertFalse(registrar(self.con, **args))
        self.assertEqual(auditar(self.con)["alias_procedencia"], 1)


if __name__ == "__main__":
    unittest.main()
