#!/usr/bin/env python3
"""Borra el parametro de paginacion "&start=N" del final de los titulos.

Medido: 355 documentos del corpus tienen ese fragmento de URL pegado al titulo, no
solo las 64 leyes departamentales que reporte antes. El reparto real es
298 Resoluciones del Pleno, 39 Compilados y 18 leyes departamentales.

DIFERENCIA CON aplica_titulo_sancionado.py, y es la razon de que sean dos scripts:
aquel RECONSTRUYE el titulo leyendo el texto oficial, y por eso puede equivocarse y
necesita banco. Este solo BORRA un parametro de URL. No infiere, no lee el texto, no
inventa: recorta y nada mas. Por eso es seguro correrlo sobre los 355 aunque el
resto del titulo siga siendo pobre.

En las Resoluciones del Pleno lo que queda detras del recorte SI describe el acto
("r p a n 115 2022 2023 aprobar el acta de la sesion ordinaria n 020 2022 2023"),
asi que el recorte ya deja un titulo buscable. Reconstruirlas desde la clausula
RESUELVE es trabajo aparte y queda NO MEDIDO.

Uso:
    python3 limpia_start.py <base.db>              # solo plan
    python3 limpia_start.py <base.db> --aplicar    # escribe
"""
import os
import re
import shutil
import sqlite3
import sys

COLA = re.compile(r"\s*&start=\d+\s*$", re.I)


def main():
    if len(sys.argv) < 2:
        print("uso: limpia_start.py <base.db> [--aplicar]")
        return 2
    base = sys.argv[1]
    aplicar = "--aplicar" in sys.argv
    if not os.path.exists(base):
        print("ROJO: no existe %s" % base)
        return 1

    con = sqlite3.connect("file:%s?mode=ro" % base, uri=True)
    filas = con.execute(
        "SELECT uid, tipo_norma, numero, anio, titulo FROM documentos"
        " WHERE titulo LIKE ?", ("%&start=%",)).fetchall()
    print("base: %s" % base)
    print("titulos con el parametro de URL: %d" % len(filas))

    plan = []
    raros = []
    reparto = {}
    for uid, tipo, numero, anio, viejo in filas:
        nuevo = COLA.sub("", viejo or "").strip()
        if not nuevo or nuevo == viejo:
            # el fragmento no estaba al final: no se toca a ciegas
            raros.append((tipo, numero, anio, viejo))
            continue
        reparto[tipo] = reparto.get(tipo, 0) + 1
        plan.append((uid, tipo, numero, anio, viejo, nuevo))
    con.close()

    print("recortables: %d | el fragmento NO esta al final (no se tocan): %d"
          % (len(plan), len(raros)))
    print("reparto: %s" % reparto)
    print()
    for _, tipo, numero, anio, viejo, nuevo in plan[:8]:
        print("   %-24s %-6s %-6s" % (tipo, numero, anio))
        print("      ANTES: %s" % viejo[:120])
        print("      AHORA: %s" % nuevo[:120])
    if raros:
        print()
        print("NO TOCADOS:")
        for tipo, numero, anio, viejo in raros[:8]:
            print("   %-24s %-6s %-6s %s" % (tipo, numero, anio, (viejo or "")[:90]))
    print()

    if not aplicar:
        print("modo plan. Nada escrito. Volver con --aplicar")
        return 0
    if not plan:
        print("nada que aplicar")
        return 0

    respaldo = base + ".antes-de-limpiar-start"
    tmp = sqlite3.connect(base)
    tmp.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    tmp.close()
    shutil.copy2(base, respaldo)
    print("respaldo: %s" % respaldo)

    con = sqlite3.connect(base)
    con.executemany("UPDATE documentos SET titulo=? WHERE uid=?",
                    [(n, u) for u, _, _, _, _, n in plan])
    con.commit()
    con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    quedan = con.execute(
        "SELECT COUNT(*) FROM documentos WHERE titulo LIKE ?",
        ("%&start=%",)).fetchone()[0]
    vacios = con.execute(
        "SELECT COUNT(*) FROM documentos WHERE titulo IS NULL OR trim(titulo)=?",
        ("",)).fetchone()[0]
    con.close()

    print("escritos: %d" % len(plan))
    print("quedan con el parametro: %d (esperado %d)" % (quedan, len(raros)))
    print("titulos vacios tras el recorte: %d (esperado 0)" % vacios)
    if quedan != len(raros) or vacios:
        print("VEREDICTO: ROJO")
        return 1
    print("VEREDICTO: VERDE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
