"""Falsador del invariante de la ingesta.

Dos casos son los que importan y los dos tienen que poder dar **ROJO**:

- `test_SABOTAJE_procedencia_que_no_escribe_da_ROJO`: el registro de procedencia miente y dice
  que escribio sin escribir.
- `test_SABOTAJE_censo_el_adaptador_que_saltea_un_documento_da_ROJO`: **reproduce en miniatura el
  bug de los 247.** El adaptador ofrece menos de lo que la fuente declara, y el guard viejo
  cerraba en VERDE porque comparaba lo ofrecido contra la base, o sea el error consigo mismo.

Un guard que no puede dar rojo no mide nada, y este proyecto ya tuvo tres: un `grep -c` que
imprimia 0 y salia 1, un centinela de idempotencia que decia "ya esta" sobre una raya
horizontal, y este.

**Y una restriccion que este archivo midio al fallar:** el esquema corre con
`PRAGMA foreign_keys=ON` y `documentos.fuente_id` referencia a `fuentes`, asi que ingerir sin
registrar la fuente muere con `IntegrityError`.
"""
import sqlite3
import tempfile
import unittest
from pathlib import Path

import alias as procedencia
from ingesta import Corpus, Documento

TEXTO = "ARTICULO 1. La presente ley departamental regula el uso del suelo.\n" * 40
FUENTE = ("tarija_gaceta", "Gaceta Oficial de Tarija", "departamental", "Tarija")


def doc(**kw) -> Documento:
    base = dict(fuente_id="tarija_gaceta", jurisdiccion="departamental",
                departamento="Tarija", tipo_norma="Ley Departamental", numero="022",
                texto=TEXTO, fuente_url="https://www.tarija.gob.bo/gaceta-oficial",
                archivo="rpa-022-2015.txt")
    base.update(kw)
    return Documento(**base)


class IngestaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "prueba.db")
        self.corpus = Corpus(self.db)
        self.corpus.registrar_fuente(*FUENTE)

    def tearDown(self):
        self.corpus.con.close()
        self.tmp.cleanup()

    def test_un_documento_deja_un_canonico_y_una_procedencia(self):
        self.corpus.agregar(doc())
        v = self.corpus.verificar()
        self.assertEqual(v["veredicto"], "VERDE")
        self.assertEqual((v["ofrecidos"], v["canonicos_nuevos"], v["alias_nuevos"]), (1, 1, 1))
        self.assertEqual(v["documentos_sin_procedencia"], 0)

    def test_mismo_texto_en_dos_archivos_no_borra_al_primero(self):
        """Antes esto era un `reemplazado`: el canonico se borraba y su fuente se perdia."""
        self.corpus.agregar(doc(archivo="rpa-022-2015.txt"))
        self.corpus.agregar(doc(archivo="rpa-022-2019.txt"))
        v = self.corpus.verificar()
        self.assertEqual(v["veredicto"], "VERDE")
        self.assertEqual(v["ofrecidos"], 2)
        self.assertEqual(v["canonicos_nuevos"], 1)
        self.assertEqual(v["duplicados_por_contenido"], 1)
        self.assertEqual(v["alias_en_base"], 2)
        self.assertEqual(v["contenidos_con_varias_fuentes"], 1)
        self.assertEqual(v["sin_rastro"], 0)
        self.assertEqual(len(procedencia.por_hash(self.corpus.con, doc().hash())), 2)

    def test_los_chunks_no_se_duplican_por_una_segunda_procedencia(self):
        self.corpus.agregar(doc(archivo="a.txt"))
        chunks = self.corpus.chunks
        self.corpus.agregar(doc(archivo="b.txt"))
        self.assertEqual(self.corpus.chunks, chunks)
        self.corpus.con.commit()
        self.assertEqual(
            self.corpus.con.execute("SELECT COUNT(*) FROM chunks").fetchone()[0], chunks)

    def test_reingesta_identica_es_idempotente(self):
        self.corpus.agregar(doc())
        self.corpus.agregar(doc())
        v = self.corpus.verificar()
        self.assertEqual(v["veredicto"], "VERDE")
        self.assertEqual(v["alias_reintento_exacto"], 1)
        self.assertEqual(v["alias_en_base"], 1)

    def test_dos_textos_distintos_son_dos_canonicos(self):
        self.corpus.agregar(doc())
        self.corpus.agregar(doc(texto=TEXTO + "ARTICULO 2. Otro texto.", archivo="otro.txt"))
        v = self.corpus.verificar()
        self.assertEqual(v["veredicto"], "VERDE")
        self.assertEqual(v["canonicos_nuevos"], 2)
        self.assertEqual(v["duplicados_por_contenido"], 0)

    def test_la_vigencia_sin_medir_entra_a_la_cola(self):
        self.corpus.agregar(doc())
        self.corpus.con.commit()
        filas = self.corpus.con.execute(
            "SELECT tipo FROM revision WHERE tipo = 'vigencia_no_medida'").fetchall()
        self.assertEqual(len(filas), 1)

    def test_una_fuente_no_registrada_no_entra_en_silencio(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.corpus.agregar(doc(fuente_id="fuente_inexistente"))

    # ---------------- los dos sabotajes ----------------

    def test_SABOTAJE_procedencia_que_no_escribe_da_ROJO(self):
        """El guard tiene que poder dar rojo, o no es un guard."""
        original = procedencia.registrar
        procedencia.registrar = lambda con, **kw: True   # dice que registro y no registra nada
        try:
            self.corpus.agregar(doc())
            v = self.corpus.verificar()
        finally:
            procedencia.registrar = original
        self.assertTrue(v["veredicto"].startswith("ROJO"), v["veredicto"])
        self.assertEqual(v["alias_en_base"], 0)
        self.assertEqual(v["documentos_sin_procedencia"], 1)

    def test_SABOTAJE_censo_el_adaptador_que_saltea_un_documento_da_ROJO(self):
        """El bug de los 247, en miniatura.

        La fuente declara 3 documentos y el adaptador solo ofrece 2, porque el tercero vive en un
        directorio que el adaptador no lee. **Sin el censo esto es VERDE**, y esa fue la lectura
        que dejo 247 documentos afuera con `perdidos: 0` durante un dia entero.
        """
        self.corpus.agregar(doc(archivo="a.txt"))
        self.corpus.agregar(doc(texto=TEXTO + "ARTICULO 2.", archivo="b.txt"))

        sin_censo = self.corpus.verificar()
        self.assertEqual(sin_censo["veredicto"], "VERDE")   # el guard viejo se quedaba aca
        self.assertIsNone(sin_censo["censo_de_la_fuente"])

        con_censo = self.corpus.verificar(censo=3)
        self.assertTrue(con_censo["veredicto"].startswith("ROJO"), con_censo["veredicto"])
        self.assertIn("faltan 1", con_censo["veredicto"])
        self.assertEqual(con_censo["censo_de_la_fuente"], 3)
        self.assertEqual(con_censo["ofrecidos"], 2)

    def test_el_censo_exacto_da_VERDE(self):
        """El otro lado del guard: si el censo coincide, no molesta."""
        self.corpus.agregar(doc(archivo="a.txt"))
        self.corpus.agregar(doc(texto=TEXTO + "ARTICULO 2.", archivo="b.txt"))
        v = self.corpus.verificar(censo=2)
        self.assertEqual(v["veredicto"], "VERDE")
        self.assertEqual(v["censo_de_la_fuente"], 2)

    def test_un_censo_mayor_al_real_tambien_da_ROJO(self):
        """Un censo mal calculado no puede pasar como si nada: es un estado que hay que ver."""
        self.corpus.agregar(doc())
        self.assertTrue(self.corpus.verificar(censo=99)["veredicto"].startswith("ROJO"))


if __name__ == "__main__":
    unittest.main()
