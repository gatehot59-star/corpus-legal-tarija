#!/usr/bin/env python3
"""Censa el estado de vigencia de las normas departamentales. NO ESCRIBE NADA.

HISTORIAL DE DEFECTOS DE ESTE INSTRUMENTO:
  v1 busco la columna de texto en la tabla `documentos` y no la encontro, asi
     que reporto "columna_texto: NO EXISTE" y dejo SIN MEDIR el numero que
     decide todo (cuantos pasajes de abrogacion hay). El texto vive en
     `chunks.cuerpo`, particionado, y se une por doc_id. Un instrumento que
     mira la tabla equivocada devuelve "no hay" igual que una ausencia real.
  v1 tampoco desglosaba por tipo_norma, y por eso yo vengo diciendo "las 512"
     cuando las departamentales son 1.034: 512 es otro sujeto.

Que mide:
  A) el esquema real
  B) desglose por tipo_norma, para saber DE QUE hablamos
  C) vigencia, fecha, materia y titulo por campo
  D) pasajes de abrogacion sobre el texto REAL (chunks), con tolerancia a OCR
  E) de los numeros de ley mencionados como derogados, cuantos estan en el corpus

Uso: python3 censo_vigencia_512.py <ruta.db>
"""
import json
import re
import sqlite3
import sys

DEP = "jurisdiccion = 'departamental'"

# El OCR confunde la N de "N 500" con W, M y H. Medido: la abrogacion mas
# importante del corpus (LD 520 abroga LD 500) estaba escrita "W 500" y un
# regex que exigia 'n' la perdio entera.
RE_LEY = re.compile(
    r"[Ll]ey(?:es)?\s+[Dd]epartamental(?:es)?"
    r"(?:\s*(?:N|W|M|H|Nro|Num|No)\b)?\s*[.\u00ba\u00b0]?\s*(\d{1,4})")
RE_ABROGA = re.compile(r"(abrog|derog)", re.I)


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/rag-abogacia-v7.db"
    con = sqlite3.connect("file:%s?mode=ro" % ruta, uri=True)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    out = {"db": ruta}

    # B) DE QUE hablamos: desglose por tipo_norma
    out["por_tipo_norma"] = [
        {"tipo": r[0], "n": r[1]}
        for r in cur.execute(
            "SELECT tipo_norma, COUNT(*) FROM documentos WHERE %s"
            " GROUP BY tipo_norma ORDER BY 2 DESC" % DEP)
    ]
    out["departamentales"] = cur.execute(
        "SELECT COUNT(*) FROM documentos WHERE %s" % DEP).fetchone()[0]

    # C) campos, contando vacio Y nulo como lo mismo (un '' no es un dato)
    campos = {}
    for c in ("vigente", "derogada_por", "fecha", "anio", "materia", "titulo"):
        vac = cur.execute(
            "SELECT COUNT(*) FROM documentos WHERE %s AND"
            " (\"%s\" IS NULL OR TRIM(CAST(\"%s\" AS TEXT))='')" % (DEP, c, c)
        ).fetchone()[0]
        campos[c] = {"vacios": vac, "con_dato": out["departamentales"] - vac}
    out["campos"] = campos

    # solo las LEYES departamentales, que es el sujeto que importa para vigencia
    n_leyes = cur.execute(
        "SELECT COUNT(*) FROM documentos WHERE %s AND tipo_norma LIKE '%%Ley%%'" % DEP
    ).fetchone()[0]
    out["leyes_departamentales"] = n_leyes

    # D) EL NUMERO QUE DECIDE: pasajes de abrogacion en el texto real.
    #    El texto esta en chunks.cuerpo y se une por doc_id.
    docs = {}
    for r in cur.execute(
            "SELECT doc_id, uid, numero, anio, tipo_norma, titulo"
            " FROM documentos WHERE %s" % DEP):
        docs[r["doc_id"]] = dict(r)

    textos = {}
    q = ("SELECT c.doc_id AS d, c.cuerpo AS t FROM chunks c"
         " JOIN documentos x ON x.doc_id = c.doc_id WHERE x.%s" % DEP)
    for r in cur.execute(q):
        textos.setdefault(r["d"], []).append(r["t"] or "")

    hallazgos = []
    con_marca = 0
    pasajes = 0
    chars = 0
    mencionados = set()
    for d, partes in textos.items():
        t = "\n".join(partes)
        chars += len(t)
        hits = list(RE_ABROGA.finditer(t))
        if not hits:
            continue
        con_marca += 1
        pasajes += len(hits)
        for m in hits:
            ventana = t[max(0, m.start() - 250):m.start() + 350]
            for mm in RE_LEY.finditer(ventana):
                num = mm.group(1).lstrip("0") or "0"
                mencionados.add(num)
                hallazgos.append({
                    "doc_id": d,
                    "uid": docs.get(d, {}).get("uid"),
                    "numero_propio": docs.get(d, {}).get("numero"),
                    "anio_propio": docs.get(d, {}).get("anio"),
                    "ley_mencionada": num,
                    "pasaje": " ".join(ventana.split())[:300],
                })

    # E) de los numeros mencionados, cuantos ESTAN en el corpus. Este es el que
    #    dice si la via del texto propio es aplicable sin salir a internet.
    en_corpus = []
    for num in sorted(mencionados, key=lambda x: int(x)):
        n = cur.execute(
            "SELECT COUNT(*) FROM documentos WHERE %s AND tipo_norma LIKE '%%Ley%%'"
            " AND CAST(numero AS INTEGER) = ?" % DEP, (int(num),)).fetchone()[0]
        if n:
            en_corpus.append(num)

    out["texto"] = {
        "documentos_con_texto": len(textos),
        "caracteres": chars,
        "documentos_con_abrogar_o_derogar": con_marca,
        "pasajes": pasajes,
        "leyes_mencionadas": len(mencionados),
        "leyes_mencionadas_lista": sorted(mencionados, key=lambda x: int(x)),
        "de_esas_en_el_corpus": len(en_corpus),
        "en_corpus_lista": en_corpus,
    }
    # GUARD que puede dar rojo: si no hay texto, todo lo de arriba es un cero
    # que miente, y hay que decirlo en vez de reportar "0 abrogaciones".
    if not textos:
        out["texto"]["VEREDICTO"] = "ROJO: cero texto unido. El join esta mal, no es que no haya abrogaciones."

    # hallazgos deduplicados por (documento, ley mencionada)
    vistos = set()
    unicos = []
    for h in hallazgos:
        k = (h["doc_id"], h["ley_mencionada"])
        if k in vistos:
            continue
        vistos.add(k)
        unicos.append(h)
    out["hallazgos"] = unicos

    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
