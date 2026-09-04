import re, sqlite3, unicodedata
c = sqlite3.connect("file:/workspace/bolivia-v7.db?mode=ro", uri=True); c.row_factory = sqlite3.Row
sin = lambda s: "".join(ch for ch in unicodedata.normalize("NFD", s or "") if unicodedata.category(ch) != "Mn").lower()
print("== corpus por jurisdiccion y tipo")
for r in c.execute("SELECT jurisdiccion,tipo_norma,count(*) n FROM documentos GROUP BY 1,2 ORDER BY n DESC"):
    print("  %-16s %-24s %5d" % (r["jurisdiccion"], r["tipo_norma"] or "-", r["n"]))
print()
print("== estado de vigencia hoy")
for r in c.execute("SELECT jurisdiccion,vigente,count(*) n FROM documentos GROUP BY 1,2 ORDER BY 1"):
    print("  %-16s vigente=%-6s %5d" % (r["jurisdiccion"], r["vigente"], r["n"]))
print()
# quien ABROGA a quien: recorro todos los chunks una vez
PAT = re.compile(r"\b(abrog|derog)\w*", re.I)
NORMA = re.compile(r"\b(ley|leyes)\s+(departamental(?:es)?\s+)?"
                   r"(n[\u00b0\u00ba\u201c\u201d\"'o*.\s]*)?(\d{1,4})\b", re.I)
tocan = {}
cuerpos = 0
for r in c.execute("SELECT uid,cuerpo FROM chunks"):
    t = r["cuerpo"] or ""
    if not PAT.search(t):
        continue
    cuerpos += 1
    tocan.setdefault(r["uid"], 0)
    tocan[r["uid"]] += 1
print("== quien menciona abrogar/derogar")
print("  chunks con la palabra:", cuerpos, "| documentos distintos:", len(tocan))
q = ",".join("?" * min(len(tocan), 900))
for r in c.execute("SELECT jurisdiccion,count(*) n FROM documentos WHERE uid IN (%s) GROUP BY 1" % q, list(tocan)[:900]):
    print("   (muestra 900)", r["jurisdiccion"], r["n"])
c.close()
