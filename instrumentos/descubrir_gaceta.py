#!/usr/bin/env python3
"""Descubre los tomos publicados de una gestion de la Gaceta Constitucional.

POR QUE EXISTE, y no es sobre-ingenieria: el patron de URL NO ES UNIFORME.
Medido el 2026-09-05 en el portal del TCP:

  2018 -> pagina plana, 5 tomos:      TomoI2018.pdf ... TomoV2018.pdf
  2019 -> CUATRO subpaginas t1..t4:   TomoItrim12019.pdf ... TomoVtrim42019.pdf  (20 tomos)
  2020 -> DOS subpaginas s1, s2
  2022 -> DOS subpaginas s1, s2:      TomoIs12022.pdf ... TomoVs22022  (10 tomos)

Si hubiera generalizado el patron de 2022 a 2019, habria pedido 10 URLs
inexistentes y concluido que la gestion no existe. El descubridor LEE el
indice y sus subpaginas, y devuelve lo que hay.

Salida: JSON [{"nombre": ..., "url": ...}, ...] a stdout.
Uso: python3 descubrir_gaceta.py 2019
"""
import json
import re
import ssl
import sys
import urllib.request as U

CTX = ssl._create_unverified_context()
HD = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}


def traer(url):
    try:
        r = U.urlopen(U.Request(url, headers=HD), timeout=60, context=CTX)
        if r.status != 200:
            return ""
        return r.read().decode("utf-8", "replace")
    except Exception:
        return ""


def paginas_de(gestion):
    """El indice de la gestion mas sus subpaginas, leidas del propio HTML."""
    raiz = "https://tcpbolivia.bo/gaceta%s/" % gestion
    html = traer(raiz)
    if not html:
        return [], ""
    subs = set(re.findall(r'href="(https://tcpbolivia\.bo/gaceta%s[a-z0-9]+/)"' % gestion, html))
    return [raiz] + sorted(subs), html


def tomos_en(html):
    """URLs de tomos. Acepta con y sin .pdf: el portal sirve TomoIII sin extension."""
    crudas = re.findall(r'href="(https://tcpbolivia\.bo/wp-content/uploads/[^"]+)"', html)
    out = {}
    for u in crudas:
        base = u.rsplit("/", 1)[-1]
        # solo tomos: descarta guia*.pdf, logos y las miniaturas .jpg
        if not base.lower().startswith("tomo"):
            continue
        if re.search(r"\.(jpg|jpeg|png|webp)$", base, re.I):
            continue
        nombre = re.sub(r"\.pdf$", "", base, flags=re.I)
        # miniaturas redimensionadas del tipo tomo1trim12019-230x300
        if re.search(r"-\d+x\d+$", nombre):
            continue
        out[nombre] = u
    return out


def main():
    gestion = sys.argv[1] if len(sys.argv) > 1 else "2022"
    paginas, _ = paginas_de(gestion)
    if not paginas:
        print("[]")
        sys.stderr.write("ROJO: el indice de la gestion %s no responde 200\n" % gestion)
        raise SystemExit(2)
    encontrados = {}
    for p in paginas:
        encontrados.update(tomos_en(traer(p)))
    filas = [{"nombre": n, "url": u} for n, u in sorted(encontrados.items())]
    sys.stderr.write("paginas leidas: %d | tomos: %d\n" % (len(paginas), len(filas)))
    for f in filas:
        sys.stderr.write("  %s\n" % f["nombre"])
    # GUARD que puede dar rojo: una gestion sin tomos es un rojo, no un vacio
    if not filas:
        sys.stderr.write("ROJO: cero tomos en %s\n" % gestion)
        print("[]")
        raise SystemExit(3)
    print(json.dumps(filas, ensure_ascii=False))


if __name__ == "__main__":
    main()
