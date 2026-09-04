"""Falsador: el texto que abroga NOMBRA el titulo de la ley que mata. Si ese
titulo no se parece al de la LD que el numero senala, el numero lo leyo mal el OCR
y el hallazgo es NO MEDIDO. Este es el paso que falto la vez que dio 67% de falsos.
"""
import difflib, re, sqlite3, unicodedata
c = sqlite3.connect("file:/workspace/bolivia-v7.db?mode=ro", uri=True); c.row_factory = sqlite3.Row
sin = lambda s: "".join(ch for ch in unicodedata.normalize("NFD", s or "") if unicodedata.category(ch) != "Mn").lower()
CASOS = [("017", "504"), ("049", "454"), ("109", "519"), ("202", "454"), ("206", "443")]
def busca(n):
    for r in c.execute("SELECT uid,numero,anio,titulo FROM documentos WHERE jurisdiccion='departamental' AND tipo_norma='Ley Departamental'"):
        try:
            if int(str(r["numero"]).strip()) == int(n):
                return dict(r)
        except (TypeError, ValueError):
            pass
    return None
def cuerpo(uid):
    return " ".join((r["cuerpo"] or "") for r in c.execute(
        "SELECT cuerpo FROM chunks WHERE uid=? ORDER BY CAST(nro AS INTEGER)", (uid,)))
for objetivo, emisor in CASOS:
    o, e = busca(objetivo), busca(emisor)
    print("=" * 78)
    print("OBJETIVO LD", objetivo, "| anio", o and o["anio"], "| titulo:", (o and o["titulo"] or "?")[:88])
    print("EMISOR   LD", emisor, "| anio", e and e["anio"], "| titulo:", (e and e["titulo"] or "?")[:88])
    if not e:
        print("  el emisor no esta en el corpus"); continue
    t = cuerpo(e["uid"])
    for m in re.finditer(r"(?:se\s+)?(?:abrog|derog)\w*", t, re.I):
        frag = re.sub(r"\s+", " ", t[max(0, m.start() - 60):m.start() + 320])
        if "epartamental" not in frag:
            continue
        print("  TEXTO CRUDO:", frag[:300])
        # parecido entre el titulo que el texto nombra y el titulo real del objetivo
        if o and o["titulo"]:
            r = difflib.SequenceMatcher(None, sin(o["titulo"])[:70], sin(frag)).find_longest_match(0, min(70, len(sin(o["titulo"]))), 0, len(sin(frag)))
            print("  coincidencia mas larga con el titulo del objetivo:", r.size, "caracteres ->",
                  repr(sin(o["titulo"])[r.a:r.a + r.size][:70]))
        break
c.close()
