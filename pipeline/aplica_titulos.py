#!/usr/bin/env python3
"""Reemplaza el titulo-slug por el titulo REAL leido del texto oficial.

Sin --aplicar solo mide y no toca la base. Con --aplicar: backup, escritura,
y relectura que sale con codigo 1 si algo no calza.

Guard de tres estados: si el extractor devuelve None el documento NO se toca.
Un titulo inventado es peor que un slug feo, porque el slug se ve mal y no engana.
"""
import json, os, shutil, sqlite3, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from titulos_desde_texto import extraer

DB = os.environ.get("RAG_DB", "/workspace/bolivia-v7.db")
BACKUP = DB + ".antes-de-titulos-reales"
PATRON = "%start=%"

def cabezas(c, objetivo):
    """chunks es FTS5: filtrar por uid es un scan. Una sola pasada para todos."""
    out = {}
    for r in c.execute("SELECT uid,nro,cuerpo FROM chunks"):
        u = r["uid"]
        if u not in objetivo:
            continue
        n = int(r["nro"])
        if u not in out or n < out[u][0]:
            out[u] = (n, r["cuerpo"])
    return out

def plan(c):
    objetivo = {r["uid"]: (r["numero"], r["anio"], r["titulo"]) for r in c.execute(
        "SELECT uid,numero,anio,titulo FROM documentos WHERE titulo LIKE ?", (PATRON,))}
    cab = cabezas(c, objetivo)
    res, nulo = {}, []
    for u, (n, cuerpo) in cab.items():
        t = extraer(cuerpo)
        if t:
            res[u] = t
        else:
            nulo.append(u)
    return objetivo, res, nulo

def main(aplicar):
    c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True); c.row_factory = sqlite3.Row
    t0 = time.time()
    objetivo, res, nulo = plan(c)
    c.close()
    print("candidatos con titulo-slug:", len(objetivo))
    print("titulo real extraido:      ", len(res))
    print("NO MEDIDO (no se tocan):   ", len(nulo))
    print("medido en", round(time.time() - t0, 1), "s")
    if not aplicar:
        print()
        print("MUESTRA (sin escribir nada):")
        for u in sorted(res, key=lambda k: (objetivo[k][1] or "", objetivo[k][0] or ""))[:12]:
            print("  LD", objetivo[u][0], objetivo[u][1], "->", res[u][:100])
        print()
        print("para escribir: aplica_titulos.py --aplicar")
        return 0
    if not res:
        print("ROJO: nada que aplicar"); return 1
    shutil.copy2(DB, BACKUP)
    print("backup:", BACKUP, os.path.getsize(BACKUP), "bytes")
    w = sqlite3.connect(DB)
    w.executemany("UPDATE documentos SET titulo=? WHERE uid=?", [(t, u) for u, t in res.items()])
    w.commit()
    # relectura contra lo que se pidio escribir: el guard tiene que poder dar ROJO
    v = sqlite3.connect("file:" + DB + "?mode=ro", uri=True); v.row_factory = sqlite3.Row
    malos = 0
    for u, t in res.items():
        got = v.execute("SELECT titulo FROM documentos WHERE uid=?", (u,)).fetchone()["titulo"]
        if got != t:
            malos += 1
            if malos <= 5:
                print("ROJO", u, "esperado", repr(t[:60]), "leido", repr(got)[:60])
    quedan = v.execute("SELECT count(*) n FROM documentos WHERE titulo LIKE ?", (PATRON,)).fetchone()["n"]
    total = v.execute("SELECT count(*) n FROM documentos").fetchone()["n"]
    v.close(); w.close()
    print("escritos:", len(res), "| discrepancias:", malos)
    print("quedan con titulo-slug:", quedan, "(esperado", len(nulo), ") | documentos:", total)
    if malos or quedan != len(nulo) or total != len(objetivo) + (total - len(objetivo)):
        print("ROJO: la relectura no calza"); return 1
    json.dump(res, open(os.path.join(os.path.dirname(BACKUP), "titulos_aplicados.json"), "w"),
              ensure_ascii=False, indent=0)
    print("VERDE")
    return 0

if __name__ == "__main__":
    sys.exit(main("--aplicar" in sys.argv))
