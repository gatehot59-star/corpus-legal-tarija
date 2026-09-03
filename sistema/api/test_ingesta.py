"""Falsador del invariante de la ingesta.

El caso que importa es el último: **sabotea el registro de procedencia y exige que la
verificación salga en ROJO.** Un guard que no puede dar rojo no mide nada, y este proyecto ya
tuvo dos: un `grep -c` que imprimía 0 y salía 1, y un centinela de idempotencia que decía "ya
está" sobre una raya horizontal.
"""
import tempfile
import unittest
from pathlib import Path

import alias as procedencia
from ingesta import Corpus, Documento

TEXTO = "ARTICULO 1. La presente ley departamental regula el uso del suelo.\n" * 40


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


if __name__ == "__main__":
    unittest.main()
