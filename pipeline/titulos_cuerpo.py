#!/usr/bin/env python3
"""Segunda clase de titulo basura: NO es un slug, es TEXTO DEL CUERPO.

La LD 129 tenia como titulo "2. Coordinacion y lealtad institucional: El Gobierno
Autonomo Departamental debera desarrollar..." o sea el articulo 2. Ese caso es PEOR
que el slug: el slug se ve mal y no engana, este parece un titulo.

Criterio, y es falsable: el titulo de una norma departamental EMPIEZA con su especie
(ley / estatuto / reglamento). Si no empieza asi, y el extractor encuentra en el texto
oficial un titulo que si empieza asi, se reemplaza. Si el extractor devuelve None, no
se toca: tres estados.

Sin --aplicar solo mide.
"""
import os, shutil, sqlite3, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from titulos_desde_texto import extraer, PALABRAS_TITULO, _sin_tildes

DB = os.environ.get("RAG_DB", "/workspace/bolivia-v7.db")
BACKUP = DB + ".antes-de-titulos-cuerpo"

def empieza_bien(t):
    p = _sin_tildes(t or "").lower().split()
    return bool(p) and p[0] in PALABRAS_TITULO

def main(aplicar):
    c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True); c.row_factory = sqlite3.Row
    cand = {}
    for r in c.execute("SELECT uid,numero,anio,titulo FROM documentos "
                       "WHERE jurisdiccion='departamental' AND titulo IS NOT NULL AND trim(titulo)<>'' "
                       "AND titulo NOT LIKE '%start=%'"):
        if not empieza_bien(r["titulo"]):
            cand[r["uid"]] = (r["numero"], r["anio"], r["titulo"])
    print("titulos que NO empiezan por su especie:", len(cand))
    cab = {}
    for r in c.execute("SELECT uid,nro,cuerpo FROM chunks"):
        u = r["uid"]
        if u not in cand:
            continue
        n = int(r["nro"])
        if u not in cab or n < cab[u][0]:
            cab[u] = (n, r["cuerpo"])
    res, nulo = {}, []
    for u, (n, cuerpo) in cab.items():
        t = extraer(cuerpo)
        if t and empieza_bien(t):
            res[u] = t
        else:
            nulo.append(u)
    c.close()
    print("con titulo real en el texto:", len(res), "| NO MEDIDO:", len(nulo))
    for u in list(res)[:15]:
        nro, anio, viejo = cand[u]
        print("  LD", nro, anio)
        print("     ANTES:", repr(viejo)[:100])
        print("     AHORA:", repr(res[u])[:100])
    if not aplicar:
        print("\npara escribir: titulos_cuerpo.py --aplicar")
        return 0
    if not res:
        print("nada que aplicar"); return 0
    shutil.copy2(DB, BACKUP)
    w = sqlite3.connect(DB)
    w.executemany("UPDATE documentos SET titulo=? WHERE uid=?", [(t, u) for u, t in res.items()])
    w.commit(); w.close()
    v = sqlite3.connect("file:" + DB + "?mode=ro", uri=True); v.row_factory = sqlite3.Row
    malos = sum(1 for u, t in res.items()
                if v.execute("SELECT titulo FROM documentos WHERE uid=?", (u,)).fetchone()["titulo"] != t)
    v.close()
    print("escritos:", len(res), "| discrepancias:", malos)
    return 1 if malos else 0

if __name__ == "__main__":
    sys.exit(main("--aplicar" in sys.argv))
