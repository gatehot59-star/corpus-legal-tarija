# Corpus: demo local aislada, sin despliegue

Este punto de entrada conecta `IsolatedSessionApp` sin modificar `servidor.py`.
Solo crea su propio candidato **ficticio** versionado y un store separado con dos
usuarios `fixture-*`. No acepta una base existente ni carga el corpus real.
El marcador, los permisos y la URL `example.invalid` identifican datos sintéticos;
los campos de procedencia compatibles con el lector no representan una norma real.

## Requisitos y arranque

Python 3.10+ con SQLite 3.37+ (tablas STRICT), scrypt/OpenSSL y POSIX.
Sin paquetes adicionales. Ejecutar desde la raíz del repositorio:

```sh
python3 sistema/api/demo_aislada.py init --directory ./corpus-demo-local --isolated-demo
python3 sistema/api/demo_aislada.py serve --directory ./corpus-demo-local --isolated-demo --port 8765
```

`init` exige una carpeta que **no exista** y un padre existente, crea permisos
0700/0600 y falla antes de sobrescribir nada. Una inicialización interrumpida se
conserva para inspección: no se repara ni borra automáticamente. Elegí otro
directorio nuevo para repetir. No uses carpetas que contienen datos reales.

`serve` valida antes de escuchar, no crea tablas, cuentas ni grants y no resetea
sesiones. Siempre escucha en **127.0.0.1**; no hay opción `--host`, proxy,
producción, systemd ni daemon. Sin `--isolated-demo` no escribe ni escucha.
Sin `--port`, usa un puerto efímero y lo imprime en un evento JSON `ready`.
Un puerto ocupado falla con código 2, no mata procesos ajenos.

El servidor rechaza Host diferente de `127.0.0.1:PUERTO` y cualquier Origin.
No hay CORS, UI ni acceso por `localhost`. Está pensado para un cliente local
de confianza. No lo publiques con túneles, NAT, reverse proxy o reenvío de puertos.

## Recorrido de ejemplo, sin imprimir el token

Con el servidor en 8765, ejecutar en otra terminal:

```sh
python3 - <<'PY'
import json
from http.client import HTTPConnection

def request(method, path, token=None, body=None):
    headers = {}
    if token:
        headers["Authorization"] = "Bearer " + token
    if body is not None:
        headers["Content-Type"] = "application/json"
    connection = HTTPConnection("127.0.0.1", 8765, timeout=5)
    try:
        connection.request(method, path,
                           json.dumps(body) if body is not None else "", headers)
        response = connection.getresponse()
        return response.status, json.loads(response.read())
    finally:
        connection.close()

status, login = request("POST", "/api/v2/login",
                       body={"username": "ana", "password": "solo-demo-ficticia"})
assert status == 200, (status, login)
token = login["access_token"]
# Obtain the immutable synthetic version without deriving it from HTTP output.
import hashlib
text = "DEMO FICTICIA, SIN VALOR JURIDICO\nArtículo único: Ñ, ⚖ y e\u0301.\r\n"
version = hashlib.sha256(text.encode()).hexdigest()
path = "/api/v2/documento/fixture-demo/texto?version=" + version
status, document = request("GET", path, token)
assert status == 200 and document["text"] == text
print("read:", status, "exact:", document["text"] == text)
status, result = request("POST", "/api/v2/logout", token)
assert status == 200 and result["logged_out"] is True
print("logout:", status)
status, result = request("GET", path, token)
assert status == 403
print("read after logout:", status)
PY
```

Esperado: `read: 200 exact: True`, `logout: 200`, `read after logout: 403`.
Las cuentas ficticias `ana` y `ben` comparten la contraseña pública
`solo-demo-ficticia`: **no es un secreto ni una contraseña para producción**.
Los tokens se emiten normalmente y solo sus hashes van al store.
Los grants sintéticos duran 24 horas desde `init`; cada sesión dura 15 minutos.
Login no renueva grants. El presupuesto compartido es cinco intentos por minuto,
incluidos passwords erróneos; 429 implica esperar, no resetear la base.

## Parada, reinicio y límites

Ctrl+C o SIGTERM cierran el listener. Volvé a ejecutar `serve` sobre la misma
carpeta para conservar revocaciones y presupuesto. No vuelvas a ejecutar `init`.
El cierre ordenado se prueba; crash recovery y reinicio de máquina NO MEDIDOS.
Los pedidos incompletos tienen timeout de socket de 2 segundos.

La validación rechaza symlinks, hardlinks, FIFO, permisos amplios, archivos
inesperados/sidecars, candidato ajeno o alterado, marcador ausente y esquema
incompleto. Es una prevención de errores operativos, no una frontera contra un
operador malicioso con tu mismo UID o root que modifique archivos mientras corre.
El servidor WSGI estándar es monohilo y **no apto para producción**.
No se certifican TLS, carga, privacidad/vigencia jurídica, ni utilidad comercial.
Los logs no imprimen requests, contraseñas ni tokens. No se crean archivos binarios
en Git; los dos SQLite se generan en la carpeta local elegida.

## Verificación desde fuente

```sh
python3 -m py_compile sistema/api/demo_aislada.py tests/test_demo_aislada.py
python3 tests/test_demo_aislada.py
python3 tests/test_login_guards.py
python3 tests/test_isolated_session.py
```

El banco invoca el CLI real, no un servidor construido exclusivamente dentro del
test. Comprueba lectura exacta, logout selectivo, otro proceso sobre el mismo
store, permisos retirados, rechazo de rutas peligrosas y ausencia de overwrite.
PR1 y el arranque histórico permanecen fuera de este cambio.
