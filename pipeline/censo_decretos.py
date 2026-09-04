#!/usr/bin/env python3
"""Censo de los DECRETOS DEPARTAMENTALES de la Gaceta de Tarija.

El item 3 del plan ("decretos departamentales, decretos ejecutivos, RE-SABS") depende de
que exista material. La sonda dio 162 enlaces de descarga en la primera pagina: hay que
saber CUANTOS son en total antes de prometer.

La leccion del GENESIS aplica: el portal declara su propio censo en la paginacion. Se lee
ese numero, no se estima por la primera pagina.
"""
import re, ssl, time, urllib.request
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
BASE = "https://www.tarija.gob.bo/gaceta-oficial/decretos-departamentales"

def baja(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=45, context=ctx).read().decode("utf8", "replace")

h = baja(BASE)
txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h))
# el portal declara el total en el contador de resultados o en la paginacion
for pat in (r"(\d+)\s*[-–]\s*(\d+)\s+de\s+(\d+)", r"Total[^\d]{0,20}(\d+)",
            r"P[aá]gina\s+\d+\s+de\s+(\d+)", r"start=(\d+)"):
    m = re.findall(pat, txt if "start" not in pat else h)
    if m:
        print("patron", repr(pat), "->", sorted(set(str(x) for x in m), key=lambda s: len(s))[-6:])
enlaces = re.findall(r'href="([^"]*download=(\d+):([^"&]*)[^"]*)"', h)
print()
print("enlaces de descarga en la primera pagina:", len(enlaces))
vistos = set()
for u, i, slug in enlaces[:14]:
    if slug in vistos:
        continue
    vistos.add(slug)
    print("   id", i, "|", slug[:78])
starts = sorted(set(int(x) for x in re.findall(r"start=(\d+)", h)))
print()
print("valores de start ofrecidos:", starts[:12], "... max", starts[-1] if starts else None)
