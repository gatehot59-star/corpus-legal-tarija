#!/usr/bin/env python3
"""Vigencia departamental v2, con el falsador ADENTRO y no despues.

Tres correcciones sobre la v1, cada una por un caso medido:

1. La v1 tomaba UN numero por clausula. "Se abrogan las Leyes Departamentales
   N 109 ... y N 029" son DOS leyes muertas y solo entraba una.
2. La v1 aceptaba el numero sin mirar el titulo. Dos de cinco hallazgos eran
   OCR mintiendo: "Estructura de Cargos 17 2024" no es la LD 17 de 2011.
   Ahora exige que el texto NOMBRE el titulo del objetivo (>=25 caracteres de
   coincidencia) o su FECHA. Sin eso: NO MEDIDO.
3. difflib con autojunk=True devuelve 0 coincidencias en textos largos porque
   trata los caracteres frecuentes como basura. Va autojunk=False.
"""
import difflib, os, re, shutil, sqlite3, sys, unicodedata

DB = os.environ.get("RAG_DB", "/workspace/bolivia-v7.db")
BACKUP = DB + ".antes-de-vigencia-v2"
MIN_TITULO = 25

def sin(s):
    return "".join(ch for ch in unicodedata.normalize("NFD", s or "") if unicodedata.category(ch) != "Mn").lower()

VERBO = r"(?:se\s+)?(?:abrog|derog)\w*"
CLAUSULA = re.compile(VERBO + r"[^.;]{0,400}", re.I)
LEY_DEPT = re.compile(r"ley(?:es)?\s+departamental(?:es)?", re.I)
NUM = re.compile(r"n[o\u00b0\u00ba*.\s\"'\u201c\u201d\)\u007e]{0,4}(\d{1,4})", re.I)
PARCIAL = re.compile(VERBO + r"\s+(?:el|los|la|las)?\s*"
                     r"(art[i\u00ed]culo|par[a\u00e1]grafo|inciso|numeral)", re.I)
PARCIAL2 = re.compile(VERBO + r"[^.;]{0,40}parcial", re.I)
MES = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre"

def parecido(titulo, frag):
    a, b = sin(titulo), sin(frag)
    if not a or not b:
        return 0
    m = difflib.SequenceMatcher(None, a, b, autojunk=False).find_longest_match(0, len(a), 0, len(b))
    return m.size

def main(aplicar):
    c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True); c.row_factory = sqlite3.Row
    porn, quien = {}, {}
    for r in c.execute("SELECT uid,numero,anio,titulo,vigente,derogada_por FROM documentos "
                       "WHERE jurisdiccion='departamental' AND tipo_norma='Ley Departamental'"):
        try:
            n = int(str(r["numero"]).strip())
        except (TypeError, ValueError):
            continue
        porn.setdefault(n, []).append(dict(r))
        quien[r["uid"]] = (n, r["anio"])
    print("leyes departamentales con numero:", len(quien), "| numeros distintos:", len(porn))
    plan, rechazos = {}, []
    for r in c.execute("SELECT uid,cuerpo FROM chunks"):
        if r["uid"] not in quien:
            continue
        t = r["cuerpo"] or ""
        if "brog" not in sin(t) and "erog" not in sin(t):
            continue
        n_em, anio_em = quien[r["uid"]]
        for mc in CLAUSULA.finditer(re.sub(r"\s+", " ", t)):
            cl = mc.group(0)
            if not LEY_DEPT.search(cl):
                continue
            parcial = bool(PARCIAL.search(cl) or PARCIAL2.search(cl))
            for mn in NUM.finditer(cl):
                objetivo = int(mn.group(1))
                if objetivo == n_em or objetivo not in porn:
                    continue
                for f in porn[objetivo]:
                    try:
                        ao, ae = int(f["anio"] or 0), int(anio_em or 0)
                    except ValueError:
                        ao = ae = 0
                    if ao and ae and ao > ae:
                        continue
                    # EL FALSADOR: el texto tiene que nombrar el titulo o la fecha
                    sim = parecido((f["titulo"] or "")[:90], cl)
                    fecha_ok = bool(f["anio"]) and re.search(
                        r"\d{1,2}\s+de\s+(?:%s)\s+de\s+%s" % (MES, re.escape(str(f["anio"]))), cl, re.I)
                    if sim < MIN_TITULO and not fecha_ok:
                        rechazos.append((objetivo, n_em, sim, bool(fecha_ok), cl[:130]))
                        continue
                    v = plan.get(f["uid"])
                    if v and not v["parcial"]:
                        continue
                    plan[f["uid"]] = {"numero": f["numero"], "anio": f["anio"], "parcial": parcial,
                                      "por": n_em, "anio_por": anio_em, "sim": sim,
                                      "fecha": bool(fecha_ok), "cl": cl[:170],
                                      "ya": (f["vigente"], f["derogada_por"])}
    c.close()
    print("CONFIRMADOS:", len(plan), "| RECHAZADOS por el falsador:", len(rechazos))
    print()
    for uid, p in sorted(plan.items(), key=lambda kv: str(kv[1]["anio"])):
        print(" ", "PARCIAL" if p["parcial"] else "TOTAL  ", "LD", p["numero"], p["anio"],
              "<- LD", p["por"], p["anio_por"],
              "| titulo coincide en", p["sim"], "car", "| fecha:", p["fecha"],
              "| ya estaba" if p["ya"][1] else "| NUEVO")
    print()
    print("== RECHAZADOS, verbatim, para que se pueda contradecir")
    vistos = set()
    for o, e, s, fo, cl in rechazos:
        if (o, e) in vistos:
            continue
        vistos.add((o, e))
        print("  LD", o, "<- LD", e, "| coincidencia", s, "car | fecha", fo)
        print("     ", cl)
    if not aplicar:
        print("\npara escribir: vig_v2.py --aplicar")
        return 0
    nuevos = {u: p for u, p in plan.items() if not p["ya"][1]}
    if not nuevos:
        print("nada nuevo"); return 0
    shutil.copy2(DB, BACKUP)
    w = sqlite3.connect(DB)
    for u, p in nuevos.items():
        etq = ("parcialmente por Ley Departamental %s" % p["por"]) if p["parcial"] \
              else ("Ley Departamental %s de %s" % (p["por"], p["anio_por"]))
        w.execute("UPDATE documentos SET vigente=?, derogada_por=? WHERE uid=?",
                  (None if p["parcial"] else 0, etq, u))
    w.commit(); w.close()
    v = sqlite3.connect("file:" + DB + "?mode=ro", uri=True); v.row_factory = sqlite3.Row
    malos = 0
    for u, p in nuevos.items():
        g = v.execute("SELECT vigente,derogada_por FROM documentos WHERE uid=?", (u,)).fetchone()
        if g["vigente"] != (None if p["parcial"] else 0) or not g["derogada_por"]:
            malos += 1; print("ROJO", u, dict(g))
    print("escritos:", len(nuevos), "| discrepancias:", malos)
    print("ahora vigente=0:", v.execute("SELECT count(*) n FROM documentos WHERE vigente=0").fetchone()["n"],
          "| con derogada_por:", v.execute("SELECT count(*) n FROM documentos WHERE derogada_por IS NOT NULL AND derogada_por<>''").fetchone()["n"])
    v.close()
    return 1 if malos else 0

if __name__ == "__main__":
    sys.exit(main("--aplicar" in sys.argv))
