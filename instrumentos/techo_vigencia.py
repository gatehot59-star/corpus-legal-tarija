#!/usr/bin/env python3
"""Mide el TECHO de la via del texto propio. NO ESCRIBE NADA.

La pregunta que decide si seguir: de las secciones abrogatorias que NO nombran
ninguna ley departamental, cuantas es porque la ley dice "se abrogan todas las
disposiciones contrarias" (generico, IRRESOLUBLE por cualquier metodo
automatico, es interpretacion juridica) y cuantas es porque MI REGEX no las
lee (arreglable).

Es la diferencia entre "la fuente no lo dice" y "yo no lo se leer", y las dos
se ven igual en un conteo.

Ademas mide dos defectos de precision que aparecieron al LEER los hallazgos:
  P1. "Ley Departamental N' 094" con APOSTROFO en vez de grado: mi regex no lo
      matchea, asi que la LD 094 abrogada por la 517/2026 NO se detecto.
  P2. Titulo anidado: "se deroga ... de la Ley Departamental N 202 Modificatoria
      a la Ley Departamental N 139" -> el objeto es la 202, pero mi extractor
      tambien reporta 139, que aparece solo dentro del TITULO de la 202.

Uso: python3 techo_vigencia.py <ruta.db>
"""
import json
import re
import sqlite3
import sys

DEP = "jurisdiccion = 'departamental'"
RE_SECCION = re.compile(r"DISPOSICI[O\u00d3]N(?:ES)?\s+(?:ABROGATORIA|DEROGATORIA)", re.I)
RE_CORTE = re.compile(r"DISPOSICI[O\u00d3]N(?:ES)?\s+(?:FINAL|TRANSITORIA|ADICIONAL)", re.I)
RE_VERBO = re.compile(r"\b(se\s+)?(abrog\w*|derog\w*)", re.I)

# v1 (estricto): solo grado o punto entre la N y el numero
RE_V1 = re.compile(r"[Ll]ey(?:es)?\s+[Dd]epartamental(?:es)?"
                   r"(?:\s*(?:N|W|M|H|Nro|Num|No)\b)?\s*[.\u00ba\u00b0]?\s*(\d{1,4})")
# v2 (tolerante): acepta apostrofo, comilla, coma y espacios raros del OCR
RE_V2 = re.compile(r"[Ll]ey(?:es)?\s+[Dd]epartamental(?:es)?"
                   r"(?:\s*(?:N|W|M|H|Nro|Num|No)\b)?"
                   r"[\s.,;:'\u00b4\u2019\"\u00ba\u00b0\)\(-]{0,6}(\d{1,4})")

GENERICO = re.compile(
    r"(todas?\s+las?\s+disposiciones?|disposiciones?\s+contrarias|"
    r"cuanto\s+sea\s+contrario|en\s+lo\s+que\s+(?:sea\s+)?contrar)", re.I)
RE_OTRO_TIPO = re.compile(
    r"(Resoluci[o\u00f3]n\s+(?:del\s+)?Consejo|Decreto|Reglamento|Estatuto|Ordenanza)", re.I)


def secciones(t):
    out = []
    for m in RE_SECCION.finditer(t):
        resto = t[m.start():m.start() + 2500]
        c = RE_CORTE.search(resto, 30)
        out.append(resto[:c.start()] if c else resto)
    return out


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/rag-abogacia-v7.db"
    con = sqlite3.connect("file:%s?mode=ro" % ruta, uri=True)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    textos = {}
    for r in cur.execute("SELECT c.doc_id AS d, c.cuerpo AS t FROM chunks c"
                         " JOIN documentos x ON x.doc_id = c.doc_id WHERE x.%s" % DEP):
        textos.setdefault(r["d"], []).append(r["t"] or "")

    clases = {"nombra_ley_v1": 0, "solo_v2_la_lee": 0, "generico": 0,
              "otro_tipo_de_norma": 0, "sin_clasificar": 0}
    ganados_por_v2 = []
    sin_clasificar = []
    secs_totales = 0

    for d, partes in textos.items():
        for s in secciones("\n".join(partes)):
            if not RE_VERBO.search(s):
                continue
            secs_totales += 1
            v1 = {m.group(1).lstrip("0") or "0" for m in RE_V1.finditer(s)}
            v2 = {m.group(1).lstrip("0") or "0" for m in RE_V2.finditer(s)}
            if v1:
                clases["nombra_ley_v1"] += 1
                if v2 - v1:
                    ganados_por_v2.append({"doc_id": d, "nuevos": sorted(v2 - v1),
                                           "seccion": " ".join(s.split())[:260]})
                continue
            if v2:
                clases["solo_v2_la_lee"] += 1
                ganados_por_v2.append({"doc_id": d, "nuevos": sorted(v2),
                                       "seccion": " ".join(s.split())[:260]})
            elif GENERICO.search(s):
                clases["generico"] += 1
            elif RE_OTRO_TIPO.search(s):
                clases["otro_tipo_de_norma"] += 1
            else:
                clases["sin_clasificar"] += 1
                if len(sin_clasificar) < 6:
                    sin_clasificar.append(" ".join(s.split())[:260])

    res = {
        "secciones_con_verbo": secs_totales,
        "clasificacion": clases,
        "numeros_que_solo_v2_lee": ganados_por_v2[:15],
        "muestras_sin_clasificar": sin_clasificar,
        "LECTURA": ("'generico' es IRRESOLUBLE por cualquier metodo automatico:"
                    " es interpretacion juridica, no extraccion. 'solo_v2_la_lee'"
                    " es hueco MIO y se arregla. Los dos se veian igual en un conteo."),
    }
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
