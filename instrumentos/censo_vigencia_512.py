#!/usr/bin/env python3
"""Censa el estado de vigencia de las leyes departamentales. NO ESCRIBE NADA.

Por que un censo antes de un extractor: la vez pasada arranque a construir el
aparato y despues descubri que la fuente no podia contestar la pregunta. Esto
mide primero:

  A) el esquema real (que columnas hay, no las que recuerdo)
  B) cuantas departamentales hay y cuantas tienen vigencia declarada
  C) cuantas tienen TEXTO suficiente para que un extractor las lea
  D) cuantos pasajes con abroga/deroga hay, con tolerancia a OCR
  E) el titulo: cuantos son basura extraida del cuerpo

Cada numero sale con su consulta al lado para que se pueda recomputar.
Uso: python3 censo_vigencia_512.py <ruta.db>
"""
import json
import re
import sqlite3
import sys


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/rag-abogacia-v7.db"
    con = sqlite3.connect("file:%s?mode=ro" % ruta, uri=True)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    out = {"db": ruta}

    # A) esquema REAL, no el que recuerdo
    tablas = [r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    out["tablas"] = tablas
    principal = None
    for cand in ("documentos", "docs", "documento"):
        if cand in tablas:
            principal = cand
            break
    if principal is None:
        # elegir la tabla con mas filas que no sea fts
        mejor, n_mejor = None, -1
        for t in tablas:
            if "fts" in t or t.startswith("sqlite_"):
                continue
            try:
                n = cur.execute("SELECT COUNT(*) FROM \"%s\"" % t).fetchone()[0]
            except Exception:
                continue
            if n > n_mejor:
                mejor, n_mejor = t, n
        principal = mejor
    out["tabla_principal"] = principal
    cols = [r[1] for r in cur.execute('PRAGMA table_info("%s")' % principal)]
    out["columnas"] = cols

    def tiene(c):
        return c in cols

    # B) cuantas departamentales y su vigencia declarada
    filtro_dep = None
    for c, v in (("jurisdiccion", "departamental"),):
        if tiene(c):
            filtro_dep = "%s = '%s'" % (c, v)
    if filtro_dep is None and tiene("tipo_norma"):
        filtro_dep = "tipo_norma LIKE '%Departamental%'"
    out["filtro_departamental"] = filtro_dep

    total = cur.execute("SELECT COUNT(*) FROM \"%s\"" % principal).fetchone()[0]
    out["documentos_total"] = total

    if filtro_dep:
        n_dep = cur.execute("SELECT COUNT(*) FROM \"%s\" WHERE %s"
                            % (principal, filtro_dep)).fetchone()[0]
        out["departamentales"] = n_dep

    for c in ("vigente", "derogada_por", "fecha", "anio", "materia", "titulo", "numero"):
        if not tiene(c):
            out["campo_%s" % c] = "NO EXISTE"
            continue
        base = "FROM \"%s\"" % principal + (" WHERE %s" % filtro_dep if filtro_dep else "")
        nulos = cur.execute(
            "SELECT COUNT(*) %s AND \"%s\" IS NULL" % (base, c)
            if filtro_dep else
            "SELECT COUNT(*) %s WHERE \"%s\" IS NULL" % (base, c)).fetchone()[0]
        vacios = cur.execute(
            "SELECT COUNT(*) %s AND (\"%s\" IS NULL OR TRIM(CAST(\"%s\" AS TEXT))='')"
            % (base, c, c) if filtro_dep else
            "SELECT COUNT(*) %s WHERE (\"%s\" IS NULL OR TRIM(CAST(\"%s\" AS TEXT))='')"
            % (base, c, c)).fetchone()[0]
        out["campo_%s" % c] = {"nulos": nulos, "nulos_o_vacios": vacios}

    # C) hay texto para leer?
    col_texto = None
    for cand in ("texto", "cuerpo", "contenido"):
        if tiene(cand):
            col_texto = cand
            break
    out["columna_texto"] = col_texto or "NO EXISTE EN LA TABLA PRINCIPAL"

    # D) pasajes de abrogacion, con tolerancia a OCR (N confundida con W/M/H)
    #    Este es el numero que decide si la via del texto propio sirve.
    if col_texto and filtro_dep:
        q = ("SELECT uid, \"%s\" AS t FROM \"%s\" WHERE %s"
             % (col_texto, principal, filtro_dep)) if tiene("uid") else (
             "SELECT rowid AS uid, \"%s\" AS t FROM \"%s\" WHERE %s"
             % (col_texto, principal, filtro_dep))
        RE_ABROGA = re.compile(r"(se\s+)?(abrog|derog)", re.I)
        # ley departamental N/W/M/H/nro/num + numero, tolerante al OCR
        RE_LEY = re.compile(
            r"[Ll]ey\s+[Dd]epartamental(?:es)?\s*(?:N|W|M|H|Nro|Num|No|\u00b0|\u00ba)?\s*[.\u00ba\u00b0]?\s*(\d{1,4})")
        con_marca = 0
        pasajes = 0
        numeros = set()
        chars = 0
        for r in cur.execute(q):
            t = r["t"] or ""
            chars += len(t)
            hits = list(RE_ABROGA.finditer(t))
            if hits:
                con_marca += 1
                pasajes += len(hits)
                for m in hits:
                    ventana = t[max(0, m.start() - 200):m.start() + 300]
                    for mm in RE_LEY.finditer(ventana):
                        numeros.add(mm.group(1).lstrip("0") or "0")
        out["texto"] = {
            "caracteres_departamentales": chars,
            "documentos_con_abroga_o_deroga": con_marca,
            "pasajes_totales": pasajes,
            "numeros_de_ley_mencionados": len(numeros),
            "numeros": sorted(numeros, key=lambda x: int(x))[:60],
        }

    # E) el titulo es basura? heuristica: empieza con digito+punto, o es muy largo,
    #    o no contiene la palabra ley/decreto/resolucion
    if tiene("titulo") and filtro_dep:
        q = "SELECT titulo FROM \"%s\" WHERE %s" % (principal, filtro_dep)
        n, sospechosos, muestras = 0, 0, []
        for r in cur.execute(q):
            t = (r["titulo"] or "").strip()
            n += 1
            malo = (
                not t
                or len(t) > 160
                or re.match(r"^\s*\d+[.)]", t)
                or not re.search(r"ley|decreto|resoluci|reglamento|estatuto", t, re.I)
            )
            if malo:
                sospechosos += 1
                if len(muestras) < 8:
                    muestras.append(t[:110])
        out["titulo"] = {"evaluados": n, "sospechosos": sospechosos, "muestras": muestras}

    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
