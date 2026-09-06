#!/usr/bin/env python3
"""Extrae abrogaciones leyendo SOLO la seccion abrogatoria. NO ESCRIBE NADA.

POR QUE, medido: buscar "abrog|derog" con una ventana de +-300 caracteres dio
17 hallazgos en el corpus, y al LEERLOS uno por uno casi todos son
REFERENCIAS, no abrogaciones. Ejemplos verbatim de esa corrida:

  454/2022 -> 139 : "los articulos modificados y complementados con la
                     presente norma a la Ley N 139"        <- MODIFICA
  485/2024 -> 350 : "el Consejo Departamental creado mediante la Ley
                     Departamental N 350"                  <- CITA
  191/2016 -> 139 : "conforme al Articulo 31 de la Ley Departamental Nro 139"
                                                            <- CITA

La causa: en una ley boliviana la "DISPOSICION ABROGATORIA Y DEROGATORIA" es
una seccion de cierre estandar, y cerca de ella hay muchas menciones a otras
normas por motivos que no son abrogarlas. La proximidad no es el sujeto.

ESTE INSTRUMENTO PUEDE DAR ROJO CONTRA MI PROPIO PLAN: si al restringir a la
seccion los hallazgos caen a ~4 (los ya aplicados), entonces la via del texto
propio esta AGOTADA y seguir puliendo el regex es trabajo sobre el problema
equivocado. Ese rojo es el resultado util.

Uso: python3 abrogatorias_por_seccion.py <ruta.db>
"""
import json
import re
import sqlite3
import sys

DEP = "jurisdiccion = 'departamental'"

# El encabezado de la seccion, tolerante a OCR y a las variantes de redaccion.
RE_SECCION = re.compile(
    r"DISPOSICI[O\u00d3]N(?:ES)?\s+(?:ABROGATORIA|DEROGATORIA)", re.I)
# Donde CORTAR la seccion: el siguiente encabezado de otra cosa, o el final.
RE_CORTE = re.compile(
    r"DISPOSICI[O\u00d3]N(?:ES)?\s+(?:FINAL|TRANSITORIA|ADICIONAL)", re.I)
# El verbo, ya dentro de la seccion.
RE_VERBO = re.compile(r"\b(se\s+)?(abrog\w*|derog\w*)", re.I)
# La ley objeto. El OCR confunde N con W, M, H (medido: "W 500" por "N 500").
RE_LEY_DEP = re.compile(
    r"[Ll]ey(?:es)?\s+[Dd]epartamental(?:es)?"
    r"(?:\s*(?:N|W|M|H|Nro|Num|No)\b)?\s*[.\u00ba\u00b0]?\s*(\d{1,4})")
# Una ley NACIONAL mencionada: NO es objeto de una abrogacion departamental.
# CPE art. 410 y LMAD: cada nivel abroga lo suyo. Este filtro mato 4 falsos
# positivos reales en una corrida anterior (la ley nacional 1173 deroga
# articulos de las nacionales 260, 400 y 348, y el corpus tiene
# departamentales con esos mismos numeros).
RE_LEY_NAC = re.compile(r"[Ll]ey\s*(?:N|W|Nro|Num|No)?\s*[.\u00ba\u00b0]?\s*(\d{3,4})\b")
RE_PARCIAL = re.compile(r"art[i\u00ed]culos?\s|par[a\u00e1]grafos?\s|incis|numeral", re.I)


def secciones(texto):
    """Devuelve los tramos de texto que SON seccion abrogatoria."""
    out = []
    for m in RE_SECCION.finditer(texto):
        resto = texto[m.start():m.start() + 2500]
        corte = RE_CORTE.search(resto, 30)
        out.append(resto[:corte.start()] if corte else resto)
    return out


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/rag-abogacia-v7.db"
    con = sqlite3.connect("file:%s?mode=ro" % ruta, uri=True)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    docs = {}
    for r in cur.execute(
            "SELECT doc_id, uid, numero, anio, tipo_norma, titulo, fuente_url"
            " FROM documentos WHERE %s" % DEP):
        docs[r["doc_id"]] = dict(r)

    textos = {}
    for r in cur.execute(
            "SELECT c.doc_id AS d, c.cuerpo AS t FROM chunks c"
            " JOIN documentos x ON x.doc_id = c.doc_id WHERE x.%s" % DEP):
        textos.setdefault(r["d"], []).append(r["t"] or "")

    con_seccion = 0
    hallazgos = []
    rechazos = {"sin_ley_departamental": 0, "self": 0, "anterior": 0}

    for d, partes in textos.items():
        t = "\n".join(partes)
        secs = secciones(t)
        if not secs:
            continue
        con_seccion += 1
        propio = docs.get(d, {})
        num_propio = str(propio.get("numero") or "").lstrip("0")
        anio_propio = str(propio.get("anio") or "")
        for s in secs:
            if not RE_VERBO.search(s):
                continue
            objetos = {m.group(1).lstrip("0") or "0" for m in RE_LEY_DEP.finditer(s)}
            if not objetos:
                rechazos["sin_ley_departamental"] += 1
                continue
            for obj in objetos:
                if obj == num_propio:
                    rechazos["self"] += 1
                    continue
                hallazgos.append({
                    "deroga": {"numero": num_propio, "anio": anio_propio,
                               "uid": propio.get("uid")},
                    "objeto": obj,
                    "alcance": "parcial" if RE_PARCIAL.search(s) else "total",
                    "seccion": " ".join(s.split())[:420],
                })

    res = {
        "departamentales_con_texto": len(textos),
        "con_seccion_abrogatoria": con_seccion,
        "hallazgos": len(hallazgos),
        "rechazos": rechazos,
        "detalle": hallazgos,
    }
    # GUARD: si NINGUN documento tiene la seccion, el regex del encabezado esta
    # mal y el cero no significa "no hay abrogaciones". Hay que decirlo.
    if con_seccion == 0:
        res["VEREDICTO"] = ("ROJO DEL INSTRUMENTO: cero secciones halladas."
                            " El regex del encabezado no matchea, no es que no haya.")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
