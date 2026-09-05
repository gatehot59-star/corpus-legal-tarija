#!/usr/bin/env python3
"""Reemplaza el slug de descarga por el titulo real, solo donde el texto lo dice.

Toca UNICAMENTE documentos cuyo titulo actual contiene el fragmento de URL
"&start=", que no es un titulo sino el parametro de paginacion de la Gaceta. Si el
extractor no encuentra titulo, el documento queda como esta: tres estados.

Uso:
    python3 aplica_titulo_sancionado.py <base.db>              # solo plan
    python3 aplica_titulo_sancionado.py <base.db> --aplicar    # escribe
"""
import os
import shutil
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from titulo_sancionado import extraer

MARCA_BASURA = "&start="


def main():
    if len(sys.argv) < 2:
        print("uso: aplica_titulo_sancionado.py <base.db> [--aplicar]")
        return 2
    base = sys.argv[1]
    aplicar = "--aplicar" in sys.argv
    if not os.path.exists(base):
        print("ROJO: no existe %s" % base)
        return 1

    con = sqlite3.connect("file:%s?mode=ro" % base, uri=True)
    objetivos = con.execute(
        "SELECT uid, numero, anio, titulo FROM documentos"
        " WHERE tipo_norma=? AND titulo LIKE ?",
        ("Ley Departamental", "%" + MARCA_BASURA + "%")).fetchall()
    print("base: %s" % base)
    print("titulos con fragmento de URL: %d" % len(objetivos))

    plan = []
    nulos = []
    vias = {}
    for uid, numero, anio, viejo in objetivos:
        fila = con.execute(
            "SELECT cuerpo FROM chunks WHERE uid=? ORDER BY nro LIMIT 1",
            (uid,)).fetchone()
        titulo, via = extraer(fila[0] if fila else "")
        vias[via] = vias.get(via, 0) + 1
        if titulo:
            plan.append((uid, numero, anio, viejo, titulo, via))
        else:
            nulos.append((numero, anio, via))
    con.close()

    print("RESUELTOS: %d | NO MEDIDO (no se tocan): %d" % (len(plan), len(nulos)))
    print("vias: %s" % vias)
    print()
    for _, numero, anio, _, titulo, via in sorted(plan, key=lambda x: int(x[1])):
        print("   LD %-5s %-5s [%s] %s" % (numero, anio, via, titulo[:110]))
    print()
    print("NO MEDIDO, siguen con el slug:")
    for numero, anio, via in nulos:
        print("   LD %-5s %-5s %s" % (numero, anio, via))
    print()

    if not aplicar:
        print("modo plan. Nada escrito. Volver con --aplicar")
        return 0
    if not plan:
        print("nada que aplicar")
        return 0

    respaldo = base + ".antes-de-titulos-sancionados"
    tmp = sqlite3.connect(base)
    tmp.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    tmp.close()
    shutil.copy2(base, respaldo)
    print("respaldo: %s" % respaldo)

    con = sqlite3.connect(base)
    con.executemany("UPDATE documentos SET titulo=? WHERE uid=?",
                    [(t, u) for u, _, _, _, t, _ in plan])
    con.commit()
    con.execute("PRAGMA wal_checkpoint(TRUNCATE)")

    # Verificacion: lo escrito es lo planificado, y nada mas quedo tocado.
    malas = 0
    for uid, _, _, _, titulo, _ in plan:
        leido = con.execute("SELECT titulo FROM documentos WHERE uid=?",
                            (uid,)).fetchone()[0]
        if leido != titulo:
            malas += 1
    quedan = con.execute(
        "SELECT COUNT(*) FROM documentos WHERE tipo_norma=? AND titulo LIKE ?",
        ("Ley Departamental", "%" + MARCA_BASURA + "%")).fetchone()[0]
    con.close()

    print("escritos: %d | discrepancias: %d" % (len(plan), malas))
    print("titulos con fragmento de URL que quedan: %d (esperado %d)"
          % (quedan, len(nulos)))
    if malas or quedan != len(nulos):
        print("VEREDICTO: ROJO")
        return 1
    print("VEREDICTO: VERDE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
