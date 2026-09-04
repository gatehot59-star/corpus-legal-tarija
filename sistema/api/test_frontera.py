"""Falsador de la frontera de confianza, por HTTP real y no por llamadas a funciones.

Un gate se prueba **desde afuera**: lo que importa no es que la funcion `autorizado()` devuelva
False, es que el servidor conteste 401 antes de tocar la base. Cada caso levanta un servidor de
verdad en un puerto libre y le habla por socket.

El caso que mas importa es `test_el_log_no_registra_la_consulta`: en un estudio juridico la
consulta es el nombre del cliente y la caratula del caso. Si eso queda en un log, el sistema
creo un expediente que nadie declaro.
"""
import io
import json
import socket
import threading
import time
import unittest
import urllib.error
import urllib.request
from contextlib import redirect_stdout
from pathlib import Path

import frontera
import servidor
from ingesta import Corpus, Documento

TEXTO = "ARTICULO 1. Prueba de la frontera de confianza del corpus legal.\n" * 20
FUENTE = ("tarija_gaceta", "Gaceta Oficial de Tarija", "departamental", "Tarija")


def puerto_libre() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def pedir(url, token="", cookie="", metodo="GET"):
    """Devuelve (codigo, cuerpo, cabeceras). No levanta excepcion en 4xx."""
    req = urllib.request.Request(url, method=metodo)
    if token:
        req.add_header("Authorization", "Bearer " + token)
    if cookie:
        req.add_header("Cookie", cookie)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read().decode(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(), dict(e.headers)


class FronteraTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = __import__("tempfile").TemporaryDirectory()
        cls.db = str(Path(cls.dir.name) / "frontera.db")
        c = Corpus(cls.db)
        c.registrar_fuente(*FUENTE)
        c.agregar(Documento(fuente_id="tarija_gaceta", jurisdiccion="departamental",
                            departamento="Tarija", tipo_norma="Ley Departamental",
                            numero="007", texto=TEXTO, archivo="ley007.txt",
                            fuente_url="https://www.tarija.gob.bo/gaceta-oficial"))
        c.cerrar()
        c.con.close()

    @classmethod
    def tearDownClass(cls):
        cls.dir.cleanup()

    def levantar(self, token="", limite=120, origen="*"):
        servidor.DB = self.db
        servidor.WEB = None
        frontera.TOKEN = token
        frontera.ORIGEN = origen
        frontera.LIMITADOR = frontera.Limitador(limite)
        p = puerto_libre()
        srv = servidor.ThreadingHTTPServer(("127.0.0.1", p), frontera.Guardia)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.shutdown)
        return "http://127.0.0.1:%d" % p

    # ---------------- limite de pedidos ----------------

    def test_pasarse_del_limite_da_429_con_retry_after(self):
        base = self.levantar(limite=3)
        vistos = [pedir(base + "/api/v1/salud")[0] for _ in range(3)]
        self.assertEqual(vistos, [200, 200, 200])
        codigo, cuerpo, cab = pedir(base + "/api/v1/salud")
        self.assertEqual(codigo, 429)
        self.assertIn("Retry-After", cab)
        self.assertGreaterEqual(int(cab["Retry-After"]), 1)
        self.assertEqual(json.loads(cuerpo)["limite_por_minuto"], 3)

    def test_limite_cero_lo_desactiva(self):
        base = self.levantar(limite=0)
        self.assertEqual([pedir(base + "/api/v1/salud")[0] for _ in range(6)], [200] * 6)

    def test_la_ventana_es_deslizante_y_no_cubeta_de_reloj(self):
        lim = frontera.Limitador(2, ventana=1.0)
        t = 1000.0
        self.assertTrue(lim.permitido("a", t)[0])
        self.assertTrue(lim.permitido("a", t + 0.1)[0])
        self.assertFalse(lim.permitido("a", t + 0.2)[0])
        self.assertTrue(lim.permitido("a", t + 1.5)[0])

    def test_el_limite_es_por_cliente(self):
        lim = frontera.Limitador(1)
        self.assertTrue(lim.permitido("1.1.1.1")[0])
        self.assertFalse(lim.permitido("1.1.1.1")[0])
        self.assertTrue(lim.permitido("2.2.2.2")[0])

    # ---------------- token ----------------

    def test_sin_token_configurado_todo_abierto(self):
        base = self.levantar()
        self.assertEqual(pedir(base + "/api/v1/alcance")[0], 200)

    def test_con_token_sin_credencial_da_401(self):
        base = self.levantar(token="clave-secreta-larga")
        codigo, cuerpo, cab = pedir(base + "/api/v1/alcance")
        self.assertEqual(codigo, 401)
        self.assertIn("WWW-Authenticate", cab)
        self.assertIn("no autorizado", cuerpo)

    def test_token_correcto_por_cabecera_entra(self):
        base = self.levantar(token="clave-secreta-larga")
        self.assertEqual(pedir(base + "/api/v1/alcance", token="clave-secreta-larga")[0], 200)

    def test_token_equivocado_no_entra(self):
        base = self.levantar(token="clave-secreta-larga")
        self.assertEqual(pedir(base + "/api/v1/alcance", token="clave-secreta-larg")[0], 401)
        self.assertEqual(pedir(base + "/api/v1/alcance", token="otra")[0], 401)

    def test_cookie_de_acceso_entra(self):
        base = self.levantar(token="clave-secreta-larga")
        self.assertEqual(pedir(base + "/api/v1/alcance",
                               cookie="acceso=clave-secreta-larga")[0], 200)

    def test_salud_queda_abierta_para_el_monitor(self):
        base = self.levantar(token="clave-secreta-larga")
        self.assertEqual(pedir(base + "/api/v1/salud")[0], 200)

    def test_la_busqueda_tambien_esta_protegida(self):
        base = self.levantar(token="clave-secreta-larga")
        self.assertEqual(pedir(base + "/api/v1/buscar?q=articulo")[0], 401)
        self.assertEqual(pedir(base + "/api/v1/buscar?q=articulo",
                               token="clave-secreta-larga")[0], 200)

    # ---------------- cabeceras ----------------

    def test_cabeceras_de_seguridad_en_toda_respuesta(self):
        base = self.levantar()
        for ruta in ("/api/v1/salud", "/api/v1/alcance"):
            _, _, cab = pedir(base + ruta)
            self.assertEqual(cab.get("X-Content-Type-Options"), "nosniff")
            self.assertEqual(cab.get("X-Frame-Options"), "DENY")
            self.assertEqual(cab.get("Referrer-Policy"), "no-referrer")
            self.assertIn("frame-ancestors 'none'", cab.get("Content-Security-Policy", ""))

    def test_una_sola_cabecera_de_cada_una(self):
        """Duplicar CSP no es cosmetico: navegadores distintos resuelven el empate distinto."""
        base = self.levantar()
        import http.client
        u = base.replace("http://", "").split(":")
        con = http.client.HTTPConnection(u[0], int(u[1]), timeout=10)
        con.request("GET", "/api/v1/salud")
        r = con.getresponse()
        r.read()
        self.assertEqual(len(r.headers.get_all("Content-Security-Policy") or []), 1)
        self.assertEqual(len(r.headers.get_all("Access-Control-Allow-Origin") or []), 1)
        con.close()

    def test_cors_se_puede_acotar_a_un_origen(self):
        base = self.levantar(origen="https://estudio.example")
        _, _, cab = pedir(base + "/api/v1/salud")
        self.assertEqual(cab.get("Access-Control-Allow-Origin"), "https://estudio.example")

    # ---------------- privacidad del log ----------------

    def test_el_log_no_registra_la_consulta(self):
        """La consulta de un estudio es el nombre del cliente. No va al log, ni la IP en claro."""
        sensible = "Elsa+Choque+Miranda"
        salida = io.StringIO()
        base = self.levantar()
        with redirect_stdout(salida):
            codigo, _, _ = pedir(base + "/api/v1/buscar?q=" + sensible + "&limite=1")
            time.sleep(0.3)
        self.assertEqual(codigo, 200)
        log = salida.getvalue()
        self.assertNotIn("Choque", log)
        self.assertNotIn(sensible, log)
        self.assertIn("/api/v1/buscar", log)
        self.assertIn("2 parametros", log)
        self.assertNotIn("127.0.0.1", log)
        self.assertIn("cliente=", log)

    def test_el_anonimo_es_estable_y_distinto_por_ip(self):
        self.assertEqual(frontera.anonimo("1.2.3.4"), frontera.anonimo("1.2.3.4"))
        self.assertNotEqual(frontera.anonimo("1.2.3.4"), frontera.anonimo("1.2.3.5"))

    # ---------------- confianza en el proxy ----------------

    def test_x_forwarded_for_solo_se_cree_desde_loopback(self):
        """Si se creyera siempre, cualquiera saltea el limite mandando una IP nueva por pedido."""
        class Falso:
            def __init__(self, ip, reenviado):
                self.client_address = (ip, 1)
                self.headers = {"X-Forwarded-For": reenviado}
                self.path = "/"
        self.assertEqual(frontera.cliente_de(Falso("127.0.0.1", "9.9.9.9")), "9.9.9.9")
        self.assertEqual(frontera.cliente_de(Falso("8.8.8.8", "9.9.9.9")), "8.8.8.8")


if __name__ == "__main__":
    unittest.main()
