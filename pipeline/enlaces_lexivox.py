"""LexiVox tiene un bloque 'Enlaces con otros documentos' con relaciones DECLARADAS:
'Deroga a', 'Referencias a esta norma'. Si existe la relacion inversa ('Derogada por',
'Abrogada por'), ahi esta la fuente de vigencia para las nacionales.

Este script NO concluye: extrae el bloque crudo para poder leerlo.
"""
import re, ssl, urllib.request
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
CASOS = [
    ("Codigo de Familia 1972 (deberia estar ABROGADO por Ley 603)", "https://www.lexivox.org/norms/BO-COD-DL10426.xhtml"),
    ("Codigo Procesal Civil 2013 (VIGENTE, y el que abroga)", "https://www.lexivox.org/norms/BO-L-N439.xhtml"),
]
for etq, u in CASOS:
    print("=" * 78); print(etq)
    try:
        h = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=50, context=ctx).read().decode("utf8", "replace")
    except Exception as e:
        print("  ERROR", type(e).__name__); continue
    i = h.lower().find("enlaces con otros")
    if i < 0:
        print("  no hay bloque de enlaces"); continue
    # el bloque de enlaces: desde ahi hasta el siguiente cierre de seccion grande
    bloque = h[i:i + 9000]
    plano = re.sub(r"<[^>]+>", " | ", bloque)
    plano = re.sub(r"(\s*\|\s*)+", " | ", plano)
    print("  BLOQUE DE ENLACES, texto crudo (1400 car):")
    print("   ", plano[:1400])
    print("  --- href hacia otras normas dentro del bloque ---")
    vistos = []
    for m in re.finditer(r'href="([^"]*(?:norms|BO-)[^"]*)"[^>]*>([^<]{0,90})', bloque, re.I):
        par = (m.group(1)[-46:], re.sub(r"\s+", " ", m.group(2)).strip())
        if par not in vistos:
            vistos.append(par)
    for a, b in vistos[:22]:
        print("     ", a, "->", b)
