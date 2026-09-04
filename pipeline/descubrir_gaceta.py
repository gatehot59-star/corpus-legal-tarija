"""Descubre el censo REAL de la Gaceta de Tarija, pagina por pagina.

**Por que existe.** En las 1.031 filas del manifest la etapa `descubrir` figura **PENDIENTE**.
O sea: nunca se midio cuanto publica la fuente, solo cuanto se habia bajado. Y sin un censo
externo, "el corpus esta completo" es una afirmacion sobre nuestra propia carpeta, que es
exactamente el error que dejo 247 documentos afuera durante un dia entero.

**El listado es Joomla y pagina de 20 en 20** con `?start=N`. Cada item de descarga aparece como
`?download=<id>:<slug>`, y ese id es la clave estable de la fuente. Medido: la primera pagina de
leyes trae 21 ids y su paginacion llega a 500, o sea que hay del orden de 500+ items por seccion.

**Dos guards que este script necesita por lo que ya paso en este proyecto:**

1. **Se detiene cuando una pagina no aporta ids nuevos**, no cuando devuelve vacio: un Joomla mal
   configurado repite la ultima pagina para siempre y un `while` ingenuo no termina nunca.
2. **Distingue "pagina vacia" de "pagina que fallo".** Un timeout que se cuenta como fin de
   listado corta el censo silenciosamente y despues se lee como "la fuente no tiene mas".

Uso:

```bash
python3 pipeline/descubrir_gaceta.py --salida descubierto.jsonl
```
"""
import argparse
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request

BASE = "https://www.tarija.gob.bo"
SECCIONES = {
    "tarija_leyes": "/gaceta-oficial/leyes-departamentales",
    "tarija_rpa": "/gaceta-oficial/resoluciones-del-pleno-de-la-asamblea",
}
UA = {"User-Agent": "Mozilla/5.0 (compatible; corpus-legal-tarija/1.0; +publico)"}

_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE   # el certificado del sitio no valida en este entorno

_RX_ITEM = re.compile(r"download=(\d+):([^\"'&]+)")


def pagina(url: str, intentos: int = 3):
    """Devuelve (html, error). Nunca confunde un fallo con una pagina vacia."""
    ultimo = ""
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45, context=_CTX) as r:
                return r.read().decode("utf-8", "replace"), ""
        except urllib.error.HTTPError as e:
            return "", "HTTP " + str(e.code)
        except Exception as e:
            ultimo = type(e).__name__ + ": " + str(e)[:60]
            time.sleep(2 * (i + 1))
    return "", ultimo


def descubrir(seccion: str, ruta: str, paso: int = 20, tope: int = 2000):
    """Recorre la paginacion hasta que una pagina no aporte ids nuevos."""
    vistos = {}
    errores = []
    start = 0
    while start <= tope:
        url = BASE + ruta + ("?start=" + str(start) if start else "")
        html, err = pagina(url)
        if err:
            errores.append({"start": start, "error": err})
            print("  ROJO start=%d -> %s" % (start, err), flush=True)
            start += paso
            continue
        nuevos = 0
        for ident, slug in _RX_ITEM.findall(html):
            if ident not in vistos:
                vistos[ident] = slug
                nuevos += 1
        print("  start=%-5d ids_nuevos=%-3d total=%d" % (start, nuevos, len(vistos)), flush=True)
        if nuevos == 0 and start > 0:
            # Fin del listado: la pagina no aporta nada. No se corta por pagina vacia, porque
            # Joomla repite la ultima pagina en vez de devolver vacio.
            break
        start += paso
    return vistos, errores


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", required=True)
    ap.add_argument("--paso", type=int, default=20)
    a = ap.parse_args()

    total = 0
    with open(a.salida, "w", encoding="utf-8") as f:
        f.write("# censo descubierto de la Gaceta de Tarija " +
                time.strftime("%Y-%m-%dT%H:%M:%S") + "\n")
        for seccion, ruta in SECCIONES.items():
            print(seccion, flush=True)
            vistos, errores = descubrir(seccion, ruta, paso=a.paso)
            for ident, slug in sorted(vistos.items(), key=lambda kv: int(kv[0])):
                f.write(json.dumps({
                    "fuente_id": seccion, "id_gaceta": ident, "slug": slug,
                    "fuente_url": BASE + ruta + "?download=" + ident + ":" + slug,
                }, ensure_ascii=False) + "\n")
            total += len(vistos)
            print("  %s: %d items | paginas con error: %d" %
                  (seccion, len(vistos), len(errores)), flush=True)
            if errores:
                print("  ATENCION: hubo paginas con error, el censo es un MINIMO no un total",
                      flush=True)
                for e in errores[:5]:
                    print("    ", e, flush=True)
    print("CENSO DESCUBIERTO:", total, "items ->", a.salida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
