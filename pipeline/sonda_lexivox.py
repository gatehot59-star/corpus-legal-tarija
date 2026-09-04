"""Que dice LexiVox sobre la vigencia de una norma? Medido, no supuesto.

Un caso de control con respuesta conocida: el Codigo de Familia de 1972 (DL 10426)
esta ABROGADO por la Ley 603 (Codigo de las Familias, 2014). Si LexiVox lo declara,
hay fuente para las 15 nacionales. Si no lo declara, esta via esta cerrada y se dice.
"""
import re, ssl, urllib.request
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
CASOS = [
    ("Codigo de Familia 1972 (ABROGADO por Ley 603)", "https://www.lexivox.org/norms/BO-COD-DL10426.xhtml"),
    ("Codigo Procesal Civil 2013 (VIGENTE)", "https://www.lexivox.org/norms/BO-L-N439.xhtml"),
    ("Codigo de Procedimiento Civil 1975 (ABROGADO por Ley 439)", "https://www.lexivox.org/norms/BO-COD-DL12760.xhtml"),
]
PISTAS = ("abrog", "derog", "vigenc", "vigente", "modificad", "reemplaz", "sustitu")
for etq, u in CASOS:
    print("=" * 78)
    print(etq)
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=50, context=ctx)
        h = r.read().decode("utf8", "replace")
        print("  http", r.status, "| bytes", len(h))
    except Exception as e:
        print("  ERROR", type(e).__name__, str(e)[:120]); continue
    txt = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S | re.I)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = re.sub(r"\s+", " ", txt)
    print("  primeros 700 caracteres de texto visible:")
    print("   ", txt[:700])
    print("  --- pistas de vigencia en TODO el documento ---")
    for p in PISTAS:
        n = len(re.findall(p, txt, re.I))
        if n:
            m = re.search(r".{120}" + p + r".{160}", txt, re.I | re.S)
            print("   '%s' x%d" % (p, n), "->", (m.group(0)[:280] if m else ""))
