#!/usr/bin/env python3
"""El auditor senala tres cosas verificables y las mido:
  1. existe una seccion de DECRETOS EJECUTIVOS en la Gaceta? (dice que si y que traen
     la cadena de derogacion en sus considerandos)
  2. los dominios de Yacuiba que yo NO probe
  3. los otros municipios con el patron gam<municipio>.gob.bo
"""
import re, socket, ssl, urllib.request
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
socket.setdefaulttimeout(30)
URLS = [
    ("GACETA · decretos ejecutivos", "https://www.tarija.gob.bo/gaceta-oficial/decretos-ejecutivos"),
    ("GACETA · resoluciones", "https://www.tarija.gob.bo/gaceta-oficial/resoluciones"),
    ("GACETA · leyes departamentales", "https://www.tarija.gob.bo/gaceta-oficial/leyes-departamentales"),
    ("YACUIBA · concejo/gaceta", "https://concejomunicipalyacuiba.gob.bo/gaceta"),
    ("YACUIBA · gamyacuiba", "https://www.gamyacuiba.gob.bo/"),
    ("YACUIBA · gamy/gacetamunicipal", "http://www.gamy.gob.bo/gacetamunicipal/decretoMunicipal.htm"),
    ("VILLA MONTES · gamvillamontes", "https://www.gamvillamontes.gob.bo/"),
    ("BERMEJO · gambermejo", "https://www.gambermejo.gob.bo/"),
    ("CERCADO · gamtarija", "https://www.gamtarija.gob.bo/"),
]
for etq, u in URLS:
    host = re.sub(r"^https?://", "", u).split("/")[0]
    try:
        ip = socket.gethostbyname(host)
    except Exception as e:
        print("%-34s DNS NO RESUELVE (%s)" % (etq, host))
        continue
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=35, context=ctx)
        h = r.read().decode("utf8", "replace")
        txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)).lower()
        pdfs = len(re.findall(r'href="[^"]*\.pdf', h, re.I))
        dl = len(re.findall(r"download=\d+", h, re.I))
        pistas = [p for p in ("ley municipal", "decreto municipal", "decreto edil", "ordenanza",
                              "gaceta", "decreto ejecutivo", "resolucion") if p in txt]
        pag = re.search(r"p[aá]gina\s+\d+\s+de\s+(\d+)", txt)
        print("%-34s ip=%-15s http=%s bytes=%-7d pdf=%-4d download=%-4d paginas=%s %s" % (
            etq, ip, r.status, len(h), pdfs, dl, pag.group(1) if pag else "-", pistas[:4]))
    except Exception as e:
        print("%-34s ip=%-15s ERROR %s %s" % (etq, ip, getattr(e, "code", type(e).__name__), str(e)[:44]))
