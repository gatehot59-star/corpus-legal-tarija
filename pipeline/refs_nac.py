#!/usr/bin/env python3
"""Vigencia de las 15 nacionales: la fuente es la seccion 'Referencias a esta norma'
de LexiVox, que lista las normas POSTERIORES que la citan.

Por que asi y no leyendo su propio texto: una norma no declara su propia muerte.
El Codigo de Familia de 1972 no dice que la Ley 603 lo abrogo en 2014. Y medido:
LexiVox NO pone una marca 'abrogada' en la pagina de la victima. Lo que si tiene es
la relacion INVERSA: quien la cita. Si una de esas citas dice abroga/deroga, ahi esta.

Este script NO escribe en la base. Solo mide y muestra la evidencia cruda.
"""
import re, ssl, sqlite3, urllib.request
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
c = sqlite3.connect("file:/workspace/bolivia-v7.db?mode=ro", uri=True); c.row_factory = sqlite3.Row
filas = c.execute("SELECT uid,tipo_norma,numero,anio,titulo,fuente_url FROM documentos "
                  "WHERE jurisdiccion='nacional' ORDER BY anio").fetchall()
c.close()

def seccion_refs(h):
    """La seccion de referencias vive tras un <div id=...> apuntado desde el indice.
    Se localiza por su encabezado y se corta en el siguiente encabezado."""
    m = re.search(r"Referencias\s+a\s+esta\s+norma", h)
    if not m:
        return None
    # el encabezado del indice aparece primero; busco la ULTIMA aparicion, que es el cuerpo
    ult = None
    for mm in re.finditer(r"Referencias\s+a\s+esta\s+norma", h):
        ult = mm
    reg = h[ult.start():ult.start() + 26000]
    corte = re.search(r"(Nota\s+importante|Deroga\s+a|Modifica\s+a)", reg[60:])
    if corte:
        reg = reg[:60 + corte.start()]
    return reg

def normas_citadas(reg):
    out = []
    for m in re.finditer(r'href="([^"]*norms/[^"]+)"[^>]*>(.{0,160}?)</a>', reg, re.S | re.I):
        t = re.sub(r"<[^>]+>", " ", m.group(2))
        t = re.sub(r"\s+", " ", t).strip()
        out.append((m.group(1).split("/")[-1], t))
    return out

print("== 15 nacionales: quien las cita, y si esa cita abroga")
for f in filas:
    u = f["fuente_url"]
    print("=" * 78)
    print(f["tipo_norma"], f["numero"] or "", f["anio"] or "", "|", (f["titulo"] or "")[:74])
    if not u or "lexivox" not in u:
        print("  sin URL de LexiVox: NO MEDIBLE por esta via"); continue
    try:
        h = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60, context=ctx).read().decode("utf8", "replace")
    except Exception as e:
        print("  ERROR", type(e).__name__, str(e)[:90]); continue
    reg = seccion_refs(h)
    if reg is None:
        print("  la pagina no trae seccion de referencias -> NO MEDIDO"); continue
    cit = normas_citadas(reg)
    plano = re.sub(r"<[^>]+>", " ", reg); plano = re.sub(r"\s+", " ", plano)
    pistas = [w for w in ("abrog", "derog", "sustituy", "reemplaz") if re.search(w, plano, re.I)]
    print("  referencias entrantes:", len(cit), "| pistas de abrogacion en la seccion:", pistas or "NINGUNA")
    for ident, t in cit[:8]:
        print("     ", ident, "->", t[:104])
    if pistas:
        for w in pistas:
            m = re.search(r".{130}" + w + r".{190}", plano, re.I | re.S)
            if m:
                print("   CRUDO [%s]:" % w, re.sub(r"\s+", " ", m.group(0)))
