#!/usr/bin/env python3
"""Vigencia de las LEYES DEPARTAMENTALES, con el sujeto correcto.

E-01 aplicado al denominador: "0 de 6.079 sin vigencia" mide el sujeto equivocado.
De los 6.079, **5.030 son jurisprudencia** (Autos Supremos, Sentencias): un Auto
Supremo NO se abroga, es una resolucion judicial. Preguntarle su "vigencia" es
como preguntarle su numero de articulos. El denominador real de la vigencia
normativa son las **512 leyes departamentales + 15 normas nacionales = 527**.

Este script mide solo las departamentales, y solo con derogaciones EXPLICITAS
de la misma jurisdiccion: una LD solo puede abrogar otra LD. Confundir "Ley 439"
nacional con "Ley Departamental 439" fue el error que dio 67% de falsos positivos.

Sin --aplicar solo mide.
"""
import os, re, shutil, sqlite3, sys, unicodedata

DB = os.environ.get("RAG_DB", "/workspace/bolivia-v7.db")
BACKUP = DB + ".antes-de-vigencia-dept"

def sin_tildes(s):
    return "".join(ch for ch in unicodedata.normalize("NFD", s or "") if unicodedata.category(ch) != "Mn").lower()

# "se abroga la Ley Departamental N 129", "quedan derogadas las Leyes Departamentales 7 y 13"
VERBO = r"(?:se\s+)?(?:abrog|derog)\w*"
# la clave: EXIGE la palabra departamental. Sin eso entra la Ley 439 nacional.
LEY_DEPT = r"ley(?:es)?\s+departamental(?:es)?"
NUM = r"n?[o\u00b0\u00ba*.\s\"'\u201c\u201d]*(\d{1,4})"
TOTAL = re.compile(VERBO + r"[^.;]{0,80}?" + LEY_DEPT + r"[^.;]{0,40}?" + NUM, re.I)
# PARCIAL solo si el OBJETO del verbo es un articulo/paragrafo, o sea VERBO ->
# objeto, no objeto -> verbo. La version anterior daba objeto->verbo y "DISPOSICION
# ABROGATORIA" (el ENCABEZADO estandar de una abrogacion TOTAL) la marcaba como
# parcial: 4 de 8 hallazgos mal clasificados. Y marcar "parcial" una abrogacion
# total es peor que no marcarla, porque la ley queda como si siguiera viva.
PARCIAL = re.compile(VERBO + r"\s+(?:el|los|la|las)?\s*"
                     r"(art[i\u00ed]culo|par[a\u00e1]grafo|inciso|numeral)", re.I)
PARCIAL2 = re.compile(VERBO + r"[^.;]{0,40}parcial", re.I)

def frases(t):
    return re.split(r"(?<=[.;])\s+", t)

def main(aplicar):
    c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True); c.row_factory = sqlite3.Row
    leyes = {}
    for r in c.execute("SELECT uid,numero,anio,titulo,vigente,derogada_por FROM documentos "
                       "WHERE jurisdiccion='departamental' AND tipo_norma='Ley Departamental'"):
        try:
            n = int(str(r["numero"]).strip())
        except (TypeError, ValueError):
            continue
        leyes.setdefault(n, []).append(dict(r))
    print("leyes departamentales con numero legible:", sum(len(v) for v in leyes.values()),
          "| numeros distintos:", len(leyes))
    # los uid de las leyes, para saber quien habla
    quien = {}
    for n, filas in leyes.items():
        for f in filas:
            quien[f["uid"]] = (n, f["anio"])
    hallazgos = []
    for r in c.execute("SELECT uid,cuerpo FROM chunks"):
        if r["uid"] not in quien:
            continue
        t = r["cuerpo"] or ""
        if "brog" not in sin_tildes(t) and "erog" not in sin_tildes(t):
            continue
        n_emisor, anio_emisor = quien[r["uid"]]
        for fr in frases(t):
            plano = re.sub(r"\s+", " ", fr)
            for m in TOTAL.finditer(plano):
                objetivo = int(m.group(1))
                if objetivo == n_emisor:
                    continue                      # no se abroga a si misma
                parcial = bool(PARCIAL.search(plano) or PARCIAL2.search(plano))
                hallazgos.append({"emisor": n_emisor, "anio_emisor": anio_emisor,
                                  "objetivo": objetivo, "parcial": parcial,
                                  "frase": plano[max(0, m.start() - 90):m.end() + 40]})
    print("menciones de abrogacion de una LD por otra LD:", len(hallazgos))
    # solo se aplica si el objetivo EXISTE en el corpus y es anterior al emisor
    plan = {}
    descartes = {"objetivo ausente del corpus": 0, "objetivo posterior o igual": 0}
    for h in hallazgos:
        filas = leyes.get(h["objetivo"])
        if not filas:
            descartes["objetivo ausente del corpus"] += 1
            continue
        for f in filas:
            try:
                ao, ae = int(f["anio"] or 0), int(h["anio_emisor"] or 0)
            except ValueError:
                ao = ae = 0
            if ao and ae and ao > ae:
                descartes["objetivo posterior o igual"] += 1
                continue
            v = plan.get(f["uid"])
            # una derogacion TOTAL manda sobre una parcial
            if v and not v["parcial"]:
                continue
            plan[f["uid"]] = {"numero": f["numero"], "anio": f["anio"], "parcial": h["parcial"],
                              "por": h["emisor"], "anio_por": h["anio_emisor"],
                              "frase": h["frase"], "ya": (f["vigente"], f["derogada_por"])}
    print("descartes:", descartes)
    print("documentos con derogacion aplicable:", len(plan))
    print()
    for uid, p in sorted(plan.items(), key=lambda kv: str(kv[1]["anio"])):
        est = "PARCIAL" if p["parcial"] else "TOTAL  "
        marca = "  (ya estaba)" if p["ya"][1] else ""
        print(" ", est, "LD", p["numero"], p["anio"], "<- LD", p["por"], p["anio_por"], marca)
        print("       ...", p["frase"][:150].replace("\n", " "))
    c.close()
    if not aplicar:
        print("\npara escribir: vigencia_dept.py --aplicar")
        return 0
    nuevos = {u: p for u, p in plan.items() if not p["ya"][1]}
    if not nuevos:
        print("nada nuevo que aplicar"); return 0
    shutil.copy2(DB, BACKUP)
    w = sqlite3.connect(DB)
    for u, p in nuevos.items():
        etiqueta = ("parcialmente por Ley Departamental %s" % p["por"]) if p["parcial"] \
                   else ("Ley Departamental %s de %s" % (p["por"], p["anio_por"]))
        w.execute("UPDATE documentos SET vigente=?, derogada_por=? WHERE uid=?",
                  (None if p["parcial"] else 0, etiqueta, u))
    w.commit(); w.close()
    v = sqlite3.connect("file:" + DB + "?mode=ro", uri=True); v.row_factory = sqlite3.Row
    malos = 0
    for u, p in nuevos.items():
        g = v.execute("SELECT vigente,derogada_por FROM documentos WHERE uid=?", (u,)).fetchone()
        esperado = None if p["parcial"] else 0
        if g["vigente"] != esperado or not g["derogada_por"]:
            malos += 1; print("ROJO", u, dict(g))
    tot0 = v.execute("SELECT count(*) n FROM documentos WHERE vigente=0").fetchone()["n"]
    totp = v.execute("SELECT count(*) n FROM documentos WHERE derogada_por IS NOT NULL AND derogada_por<>''").fetchone()["n"]
    v.close()
    print("escritos:", len(nuevos), "| discrepancias:", malos)
    print("ahora: vigente=0 ->", tot0, "| con derogada_por ->", totp)
    return 1 if malos else 0

if __name__ == "__main__":
    sys.exit(main("--aplicar" in sys.argv))
