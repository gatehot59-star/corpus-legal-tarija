"""Falsador del normalizador. El caso central es el que refuta al auditor.

Si alguien vuelve a leer el ano del nombre de archivo, `test_el_hash_nunca_es_un_anio` da ROJO
con los nombres reales que enganaron al regex propuesto.
"""
import unittest

from normalizar import anios_de, compilado_de, limpiar_titulo, metadatos_de

# Titulos reales del corpus, copiados de registros.jsonl.
LEY = "ley departamental 142 2016&start=360"
RPA = "r p a n 074 2021 2022 aprobar la resolucion de distincion con insignia"
COMPILADO = "resoluciones del pleno de la asamblea 141 al 177 del 2014 2015&start=5"
SIN_ANIO = "ley departamental n 476 ley de modificacion presupuestaria intrainstitucional"

# Nombres de archivo reales cuyo HASH parece un ano. Son la refutacion del "fix de una tarde".
HASHES_TRAMPOSOS = [
    "tarija_leyes-047-a5771928.txt",   # -> 1928
    "tarija_leyes-200-2c1a2054.txt",   # -> 2054, futuro
    "tarija_leyes-269-8d190942.txt",   # -> 1909
    "tarija_leyes-106-7811932f.txt",   # -> 1932
    "tarija_leyes-226-1959667d.txt",   # -> 1959
]


class NormalizarTest(unittest.TestCase):
    def test_ley_con_un_anio(self):
        m = metadatos_de(LEY)
        self.assertEqual(m["anio"], "2016")
        self.assertEqual(m["gestion"], "")
        self.assertEqual(m["unidad"], "norma")
        self.assertEqual(m["fuente_del_anio"], "titulo")

    def test_rpa_con_gestion_de_dos_anios(self):
        m = metadatos_de(RPA)
        self.assertEqual(m["anio"], "2021")
        self.assertEqual(m["gestion"], "2021-2022")
        self.assertEqual(m["fuente_del_anio"], "titulo:gestion")

    def test_sin_anio_queda_vacio_y_lo_declara(self):
        """Vacio es NO MEDIDO. Inventar un ano probable seria el error grave."""
        m = metadatos_de(SIN_ANIO)
        self.assertEqual(m["anio"], "")
        self.assertIn("NO MEDIDO", m["fuente_del_anio"])

    def test_el_hash_nunca_es_un_anio(self):
        """LA refutacion: el nombre de archivo NO es fuente de anio. 16 de 784 eran el hash."""
        for nombre in HASHES_TRAMPOSOS:
            self.assertEqual(anios_de(nombre), [], nombre)
            self.assertEqual(metadatos_de(nombre)["anio"], "", nombre)

    def test_rechaza_anios_imposibles(self):
        self.assertEqual(anios_de("ley departamental 200 del 2054"), [])
        self.assertEqual(anios_de("ley departamental 047 de 1928"), [])
        self.assertEqual(anios_de("ley departamental 007 2010"), ["2010"])

    def test_detecta_el_compilado_y_cuenta_lo_que_contiene(self):
        c = compilado_de(COMPILADO)
        self.assertEqual((c["desde"], c["hasta"], c["contiene"]), (141, 177, 37))
        self.assertEqual(metadatos_de(COMPILADO)["unidad"], "compilado")

    def test_una_norma_individual_no_es_compilado(self):
        self.assertIsNone(compilado_de(LEY))
        self.assertIsNone(compilado_de(RPA))
        self.assertEqual(metadatos_de(RPA)["unidad"], "norma")

    def test_rango_invertido_es_NO_MEDIDO_no_cero(self):
        c = compilado_de("resoluciones del pleno de la asamblea 177 al 141 del 2014")
        self.assertIsNone(c["contiene"])
        self.assertIn("NO MEDIDO", c["advertencia"])

    def test_limpia_la_paginacion_del_scraping(self):
        self.assertNotIn("start", limpiar_titulo(LEY))
        self.assertEqual(anios_de("ley 1 2016&start=1999"), ["2016"])

    def test_titulo_vacio_no_explota(self):
        for entrada in (None, "", "   "):
            m = metadatos_de(entrada)
            self.assertEqual(m["anio"], "")
            self.assertIsNone(m["compilado"])


if __name__ == "__main__":
    unittest.main()
