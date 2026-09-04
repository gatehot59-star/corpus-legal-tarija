#!/usr/bin/env python3
"""Antes de prometer los items 3, 4 y 5 del plan: las fuentes RESPONDEN?

Sin esto, "agregar decretos departamentales" es una promesa, no una tarea. Mide y
declara: si un portal no contesta o no publica el material, se dice y no se planifica
sobre humo.
"""
import re, socket, ssl, urllib.request

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
socket.setdefaulttimeout(25)

FUENTES = [
    # item 3: decretos departamentales y ejecutivos, RE-SABS
    ("DECRETOS DEPT · Gaceta Tarija", "https://www.tarija.gob.bo/gaceta-oficial/decretos-departamentales"),
    ("DECRETOS DEPT · Gaceta raiz", "https://www.tarija.gob.bo/gaceta-oficial"),
    ("ALDT Asamblea Legislativa", "https://www.aldt.gob.bo/"),
    # item 4: municipios
    ("GAM Cercado (Tarija)", "https://www.tarija.bo/"),
    ("GAM Yacuiba", "https://www.yacuiba.gob.bo/"),
    ("GAM Villa Montes", "https://www.villamontes.gob.bo/"),
    ("GAM Bermejo", "https://www.bermejo.gob.bo/"),
    # item 5: TCP
    ("TCP buscador jurisprudencia", "https://buscador.tcpbolivia.bo/"),
    ("TCP portal", "https://www.tcpbolivia.bo/tcp/"),
    # control positivo: fuentes que YA uso
    ("[control] LexiVox", "https://www.lexivox.org/"),
    ("[control] GENESIS TSJ", "https://jurisprudencia.tsj.bo/"),
]
PISTAS = ("decreto", "ordenanza", "ley municipal", "resoluci", "gaceta", "sentencia constitucional")

for etq, u in FUENTES:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=30, context=ctx)
        h = r.read().decode("utf8", "replace")
        txt = re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>", " ", h, flags=re.S | re.I))
        txt = re.sub(r"\s+", " ", txt)
        pdfs = len(re.findall(r'href="[^"]*\.pdf', h, re.I))
        desc = len(re.findall(r"download=\d+", h, re.I))
        pistas = [p for p in PISTAS if p in txt.lower()]
        print("%-32s http=%s  bytes=%-8d pdf=%-4d download=%-4d %s" % (etq, r.status, len(h), pdfs, desc, pistas[:4]))
    except Exception as e:
        cod = getattr(e, "code", None) or type(e).__name__
        print("%-32s NO RESPONDE: %s %s" % (etq, cod, str(e)[:60]))
