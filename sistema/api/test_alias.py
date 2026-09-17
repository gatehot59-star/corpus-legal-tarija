"""Falsador de la tabla de procedencia.

Cada caso existe por un modo de falla concreto, y dos de ellos tienen que poder dar ROJO: si la
unicidad se define mal, una procedencia legitima desaparece en silencio, y el silencio es lo que
ya costó 333 documentos en este proyecto.
"""
import sqlite3
import unittest

from alias import auditar, instalar, por_hash, por_uid, registrar, sha256_de

TEXTO = "ARTICULO 1. Texto de prueba."


class AliasTest(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.con.executescript(
            "CREATE TABLE documentos (doc_id INTEGER PRIMARY KEY, uid TEXT, titulo TEXT, "
            "tipo_norma TEXT, numero TEXT);"
        )
        instalar(self.con)
        self.con.execute(
            "INSERT INTO documentos(uid,titulo,tipo_norma,numero) VALUES(?,?,?,?)",
            ("dep-tar-ley-022-abcd1234", "Ley 022", "Ley Departamental", "022"))
        self.con.commit()

    def tearDown(self):
        self.con.close()

    def _reg(self, **kw):
        base = dict(doc_id=1, uid="dep-tar-ley-022-abcd1234", fuente_id="tarija_gaceta",
                    fuente_url="https://www.tarija.gob.bo/gaceta-oficial", texto=TEXTO)
        base.update(kw)
        return registrar(self.con, **base)

    def test_dos_fuentes_distintas_conservan_las_dos(self):
        self.assertTrue(self._reg(fuente_url="https://a/022.pdf", archivo="a.txt"))
        self.assertTrue(self._reg(fuente_id="tsj_genesis", fuente_url="https://b/022.pdf",
                                  archivo="b.txt"))
        self.assertEqual(len(por_hash(self.con, sha256_de(TEXTO))), 2)

    def test_misma_url_generica_con_archivos_distintos_no_se_pisa(self):
        """El caso real: la Gaceta cae al fallback de URL y el archivo es lo unico que distingue."""
        self.assertTrue(self._reg(archivo="rpa-022-2015.txt"))
        self.assertTrue(self._reg(archivo="rpa-022-2019.txt"))
        self.assertEqual(len(por_uid(self.con, "dep-tar-ley-022-abcd1234")), 2)

    def test_reintento_exacto_es_idempotente(self):
        self.assertTrue(self._reg(archivo="a.txt"))
        self.assertFalse(self._reg(archivo="a.txt"))
        self.assertEqual(auditar(self.con)["alias_procedencia"], 1)

    def test_auditoria_ve_el_documento_sin_procedencia(self):
        self.assertEqual(auditar(self.con)["documentos_sin_procedencia"], 1)
        self._reg(archivo="a.txt")
        self.assertEqual(auditar(self.con)["documentos_sin_procedencia"], 0)

    def test_hash_de_la_fuente_gana_al_del_texto(self):
        """El uid usa el sha de la fuente cuando existe; el alias tiene que usar el mismo."""
        self.assertTrue(self._reg(archivo="a.txt", sha256="f" * 64))
        self.assertEqual(por_uid(self.con, "dep-tar-ley-022-abcd1234")[0]["sha256"], "f" * 64)


if __name__ == "__main__":
    unittest.main()
