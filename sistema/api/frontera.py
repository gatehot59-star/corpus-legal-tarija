"""Frontera de confianza del corpus legal. Envuelve la API sin tocarla.

**Por que un archivo aparte y no un parche en **`servidor.py`**:** una frontera de confianza que
vive desparramada en 700 lineas no se puede auditar. Esto se lee entero de una sentada, y
`servidor.py` sigue siendo el que sabe de corpus y no sabe de seguridad.

Se usa igual que el otro, y este es el que va cuando la API sale del taller:

```bash
python3 frontera.py --db bolivia.db --puerto 8080                    # abierto, con limite
python3 frontera.py --db bolivia.db --token "$CLAVE" --puerto 8080   # con clave
```

Cuatro cosas que hace, y cada una existe por un modo de falla concreto:

1. **Limite de pedidos por IP.** Sin esto, un solo cliente mal escrito (o un scraper) hace 200
   busquedas por segundo y la maquina es un Celeron de 2 nucleos: el estudio se queda sin
   buscador. Devuelve **429** con `Retry-After`, no un cuelgue.
2. **Token opcional.** El corpus es publico y esto no cambia eso: existe para cuando la API se
   exponga a internet y no se quiera que cualquiera consuma la CPU. `hmac.compare_digest` y no
   `==`, porque comparar strings de a byte filtra el token por tiempo.
3. **Cabeceras de seguridad y CORS acotable.** `Access-Control-Allow-Origin: *` esta bien para
   un corpus publico de lectura y **mal** el dia que haya token: se puede restringir a un origen.
4. **El log NO registra la consulta.** Esta es la que importa y no es teorica: en un estudio
   juridico la consulta **es el caso**. `servidor.py` loguea la linea de pedido completa, o sea
   `?q=nombre+del+cliente`, y eso queda escrito en un archivo que nadie penso como expediente.
   Aca se loguea ruta y estado, la IP va **hasheada con una sal del proceso**, y la query se
   reemplaza por la cantidad de parametros.

**Lo que esto NO es:** no es cifrado en transito. TLS lo pone el reverse proxy (Caddy o nginx),
y esta en el README. Un token sobre HTTP plano viaja en claro, asi que exponerlo sin TLS es
peor que no tenerlo.
"""
import argparse
import hashlib
import hmac
import os
import sys
import threading
import time
from collections import deque
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import servidor  # noqa: E402

# Rutas que quedan abiertas incluso con token: un monitor externo tiene que poder preguntar
# "esta vivo?" sin credenciales, o el healthcheck se convierte en otra cosa que puede fallar.
ABIERTAS = ("/api/v1/salud",)

CABECERAS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
    "Cross-Origin-Opener-Policy": "same-origin",
    # `unsafe-inline` es una concesion REAL y se declara: el frontend es un solo archivo con su
    # estilo y su script adentro, a proposito, para que un estudio no necesite un build. La
    # alternativa honesta seria hashear cada bloque, y se rompe en cada edicion.
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com data:; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "form-action 'none'; "
        "base-uri 'none'; "
        "object-src 'none'; "
        "frame-ancestors 'none'"
    ),
}


class Limitador:
    """Ventana deslizante por cliente. Thread-safe porque el servidor es multihilo.

    Ventana deslizante y no cubeta fija: con cubeta por minuto de reloj, un cliente gasta todo
    en el segundo 59 y todo otra vez en el 00, o sea el doble del limite en dos segundos.
    """

    def __init__(self, por_minuto: int, ventana: float = 60.0):
        self.tope = int(por_minuto)
        self.ventana = float(ventana)
        self.visitas: dict[str, deque] = {}
        self.candado = threading.Lock()

    def permitido(self, cliente: str, ahora: float | None = None):
        """Devuelve (permitido, segundos_para_reintentar)."""
        if self.tope <= 0:
            return True, 0
        ahora = time.monotonic() if ahora is None else ahora
        with self.candado:
            d = self.visitas.setdefault(cliente, deque())
            while d and ahora - d[0] > self.ventana:
                d.popleft()
            if len(d) >= self.tope:
                return False, max(1, int(self.ventana - (ahora - d[0])) + 1)
            d.append(ahora)
            # Higiene: sin esto, un scan de miles de IPs deja un dict que solo crece.
            if len(self.visitas) > 4096:
                for k in [k for k, v in self.visitas.items() if not v or ahora - v[-1] > self.ventana]:
                    self.visitas.pop(k, None)
            return True, 0


LIMITADOR = Limitador(120)
TOKEN = ""
ORIGEN = "*"
SAL = os.urandom(16)


def cliente_de(handler) -> str:
    """Identidad del cliente para el limite. Detras de proxy, el socket es siempre el proxy.

    `X-Forwarded-For` se acepta SOLO si el pedido viene de loopback, que es donde vive el
    reverse proxy. Confiar en esa cabecera desde cualquier origen es regalarle a cualquiera la
    forma de saltear el limite: manda una IP distinta en cada pedido.
    """
    ip = handler.client_address[0] if handler.client_address else "?"
    if ip in ("127.0.0.1", "::1"):
        reenviado = handler.headers.get("X-Forwarded-For", "")
        if reenviado:
            ip = reenviado.split(",")[0].strip() or ip
    return ip


def anonimo(ip: str) -> str:
    """IP hasheada con sal del proceso: sirve para agrupar, no para identificar ni para siempre."""
    return hashlib.blake2s(ip.encode(), key=SAL, digest_size=4).hexdigest()


def autorizado(handler, ruta: str) -> bool:
    if not TOKEN or ruta in ABIERTAS:
        return True
    cab = handler.headers.get("Authorization", "")
    if cab.startswith("Bearer ") and hmac.compare_digest(cab[7:].strip(), TOKEN):
        return True
    galleta = SimpleCookie(handler.headers.get("Cookie", ""))
    if "acceso" in galleta and hmac.compare_digest(galleta["acceso"].value, TOKEN):
        return True
    clave = parse_qs(urlparse(handler.path).query).get("clave", [""])[0]
    return bool(clave) and hmac.compare_digest(clave, TOKEN)


class Guardia(servidor.Handler):
    server_version = "corpus-legal-bolivia-frontera/" + servidor.VERSION

    def log_message(self, formato, *args):
        """Log sin la consulta. En un estudio juridico la consulta ES el caso."""
        linea = args[0] if args else ""
        try:
            metodo, destino, _ = str(linea).split(" ", 2)
            u = urlparse(destino)
            n = len(parse_qs(u.query))
            destino = u.path + ((" (%d parametros)" % n) if n else "")
        except ValueError:
            metodo, destino = "?", "?"
        codigo = args[1] if len(args) > 1 else "?"
        print("[api] %s %s %s cliente=%s" % (metodo, destino, codigo,
                                             anonimo(cliente_de(self))), flush=True)

    def responder(self, codigo, cuerpo, tipo="application/json; charset=utf-8"):
        self._extra = CABECERAS
        return super().responder(codigo, cuerpo, tipo)

    def end_headers(self):
        for k, v in CABECERAS.items():
            self.send_header(k, v)
        super().end_headers()

    def send_header(self, clave, valor):
        # CORS acotado: el padre manda `*` y aca gana el origen configurado.
        if clave == "Access-Control-Allow-Origin":
            valor = ORIGEN
        if clave in CABECERAS and getattr(self, "_ya", None) and clave in self._ya:
            return
        self._ya = getattr(self, "_ya", set()) | {clave}
        super().send_header(clave, valor)

    def do_GET(self):
        self._ya = set()
        ruta = urlparse(self.path).path.rstrip("/") or "/"

        ok, reintentar = LIMITADOR.permitido(cliente_de(self))
        if not ok:
            self.send_response(429)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Retry-After", str(reintentar))
            cuerpo = ('{"error": "demasiados pedidos", "reintentar_en_segundos": %d, '
                      '"limite_por_minuto": %d}' % (reintentar, LIMITADOR.tope)).encode()
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)
            return

        if not autorizado(self, ruta):
            cuerpo = (b'{"error": "no autorizado", "como": "Authorization: Bearer <token>", '
                      b'"abierto_sin_token": "/api/v1/salud"}')
            self.send_response(401)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("WWW-Authenticate", 'Bearer realm="corpus-legal"')
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)
            return

        # Entrada con clave por URL: deja la cookie y saca la clave de la barra, para que no
        # quede en el historial ni se copie en un link compartido.
        clave = parse_qs(urlparse(self.path).query).get("clave", [""])[0]
        if TOKEN and clave and hmac.compare_digest(clave, TOKEN) and ruta in ("/", "/index.html"):
            self.send_response(303)
            self.send_header("Location", "/")
            self.send_header("Set-Cookie",
                             "acceso=%s; Path=/; HttpOnly; SameSite=Strict" % TOKEN)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        return super().do_GET()

    def do_OPTIONS(self):
        self._ya = set()
        return super().do_OPTIONS()


def main() -> int:
    global TOKEN, ORIGEN, LIMITADOR
    ap = argparse.ArgumentParser(description="API del corpus legal con frontera de confianza")
    ap.add_argument("--db", required=True)
    ap.add_argument("--web", default=str(Path(__file__).resolve().parent.parent / "web"))
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--puerto", type=int, default=8080)
    ap.add_argument("--token", default=os.environ.get("CORPUS_TOKEN", ""),
                    help="si se define, se exige para todo menos /api/v1/salud")
    ap.add_argument("--limite-por-minuto", type=int, default=120,
                    help="pedidos por IP por minuto; 0 lo desactiva")
    ap.add_argument("--origen", default="*", help="valor de Access-Control-Allow-Origin")
    a = ap.parse_args()

    servidor.DB = a.db
    servidor.WEB = Path(a.web) if a.web else None
    TOKEN = a.token
    ORIGEN = a.origen
    LIMITADOR = Limitador(a.limite_por_minuto)

    if not Path(a.db).exists():
        print("ROJO: no existe la base", a.db, "-> correr ingesta.py primero")
        return 2
    if TOKEN and a.host not in ("127.0.0.1", "::1"):
        print("AVISO: con token y escuchando fuera de loopback, poner TLS adelante "
              "(ver README). Un token sobre HTTP plano viaja en claro.")

    al = servidor.alcance()
    print("corpus-legal-bolivia " + servidor.VERSION + " (con frontera)")
    print("  documentos:", al["documentos"], "| procedencias:", al["procedencias_registradas"])
    print("  token:", "si" if TOKEN else "no", "| limite:", a.limite_por_minuto,
          "pedidos/min por IP | origen CORS:", ORIGEN)
    print("  el log NO registra la consulta")
    print("  escuchando en http://" + a.host + ":" + str(a.puerto), flush=True)
    servidor.ThreadingHTTPServer((a.host, a.puerto), Guardia).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
