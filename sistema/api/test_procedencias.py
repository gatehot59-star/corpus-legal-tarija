"""Falsador del tercer estado de la API: NO MEDIDO.

Una base anterior a `documento_aliases` **no tiene cero fuentes**: no las registra. Si la API
devuelve `procedencias: 0` o una lista vacia, un agente concluye "este documento tiene una sola
fuente oficial" con tono seguro y nadie lo nota. Estos casos exigen `null` mas advertencia.

Corre sin levantar el servidor: se apunta el modulo a una base temporal y se llaman las mismas
funciones que sirven las rutas.
"""
import sqlite3
import tempfile
import unittest
from pathlib import Path

import servidor
from ingesta import Corpus, Documento

TEXTO = "ARTICULO 1. Texto de prueba del corpus legal.\n" * 30
FUENTE = ("tarija_gaceta", "Gaceta Oficial de Tarija", "departamental", "Tarija")


def doc(**kw) -> Documento:
    base = dict(fuente_id="tarija_gaceta", jurisdiccion="departamental", departamento="Tarija",
                tipo_norma="Ley Departamental", numero="022", texto=TEXTO,
                fuente_url="https://www.tarija.gob.bo/gaceta-oficial", archivo="a.txt")
    base.update(kw)
    return Documento(**base)


class ProcedenciaEnLaApiTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "api.db")
        c = Corpus(self.db)
        c.registrar_fuente(*FUENTE)
        c.agregar(doc(archivo="rpa-022-2015.txt"))
        c.agregar(doc(archivo="rpa-022-2019.txt"))   # mismo texto, otra entrada de indice
        c.agregar(doc(texto=TEXTO + "ARTICULO 2.", numero="023", archivo="otra.txt"))
        c.cerrar()
        self.uid = doc().uid()
        c.con.close()
        servidor.DB = self.db

    def tearDown(self):
        servidor.DB = None
        self.tmp.cleanup()

    def test_la_cita_trae_las_dos_fuentes(self):
        pr = servidor.procedencia_de_uid(self.uid)
        self.assertEqual(pr["procedencias"], 2)
        self.assertEqual(len(pr["fuentes"]), 2)
        self.assertIn("citar todas", pr["advertencia"].lower())

    def test_la_busqueda_lleva_las_fuentes_en_cada_resultado(self):
        r = servidor.buscar("ARTICULO", limite=5)
        self.assertTrue(r["hallado"])
        cita = r["resultados"][0]["cita"]
        self.assertEqual(cita["procedencias"], len(cita["fuentes"]))
        self.assertGreaterEqual(cita["procedencias"], 1)

    def test_el_documento_expone_su_procedencia(self):
        d = servidor.documento(self.uid)
        self.assertEqual(len(d["procedencias"]), 2)
        self.assertEqual(len(d["procedencias"][0]["sha256"]), 64)

    def test_alcance_cuenta_procedencias(self):
        al = servidor.alcance()
        self.assertEqual(al["procedencias_registradas"], 3)
        self.assertEqual(al["documentos_con_varias_procedencias"], 1)

    def test_uid_inexistente_devuelve_None(self):
        self.assertIsNone(servidor.procedencia_de_uid("no-existe-123"))

    def test_BASE_VIEJA_dice_NO_MEDIDO_y_no_cero(self):
        """El caso que separa los tres estados: sin tabla, `null`, nunca 0 ni lista vacia."""
        con = sqlite3.connect(self.db)
        con.execute("DROP TABLE documento_aliases")
        con.commit()
        con.close()

        pr = servidor.procedencia_de_uid(self.uid)
        self.assertIsNone(pr["procedencias"])
        self.assertIsNone(pr["fuentes"])
        self.assertIn("NO MEDIDO", pr["advertencia"])

        d = servidor.documento(self.uid)
        self.assertIsNone(d["procedencias"])
        self.assertIsNone(d["cita"]["procedencias"])
        self.assertIn("NO MEDIDO", d["cita"]["advertencia_procedencia"])

        r = servidor.buscar("ARTICULO", limite=3)
        self.assertTrue(r["hallado"])
        self.assertIsNone(r["resultados"][0]["cita"]["procedencias"])

        al = servidor.alcance()
        self.assertIsNone(al["procedencias_registradas"])

        m = servidor.procedencias_multiples()
        self.assertIs(m["medido"], False)
        self.assertIsNone(m["total"])


if __name__ == "__main__":
    unittest.main()
