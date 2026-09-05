#!/usr/bin/env python3
"""aplica_vigencia_adjudicada.py - escribe la vigencia de las leyes departamentales.

EL GRAFO PROPONE, LA LECTURA VERBATIM ADJUDICA.

El extractor automatico encontro 26 aristas abrogador->abrogada y su banco daba
10/10 y su control 17/17. Igual me equivoque en 2 de 18, y el control no podia
cazarlo porque **solo tenia casos positivos**: 17 pares que SI existen. Un
control sin casos negativos no mide falsos positivos, mide recall. Por eso los
18 pares totales se leyeron uno por uno y solo entran los 16 que sobreviven.

LOS DOS FALSOS POSITIVOS, para que no vuelvan:

1. LD 139 (Administracion del Presupuesto). La clausula de la LD 454 dice:
   "Se abroga la Ley Departamental 204 de Modificacion al articulo 27 de la Ley
   Departamental 139 de Administracion del Presupuesto...". Muere la 204. La 139
   es solo la ley QUE LA 204 MODIFICABA. Sigue viva.
   Forma general de la trampa: "Se abroga la Ley X de Modificacion a la Ley Y"
   mata a X, nunca a Y.

2. LD 010 (Reconocimiento a la Autonomia Regional del Gran Chaco Tarijeno). La
   clausula de la LD 519 nombra unicamente la 109 y la 029. El "10" salio del
   propio "109". Leido el texto completo, la 010 no aparece. Sigue viva.

REGLA LEGAL APLICADA: la abrogacion es instantanea y definitiva. Que el
abrogador muera despues NO revive a la abrogada, salvo clausula expresa de
restitucion. Medido: ni la LD 520 ni la LD 500 tienen clausula de restitucion,
asi que la LD 129 y la LD 432 quedan muertas aunque su verdugo (LD 500) tambien
lo este.

Uso:
    python3 aplica_vigencia_adjudicada.py <base.db> [--aplicar]

Sin --aplicar solo muestra el plan. Hace respaldo antes de escribir.
"""
import os
import shutil
import sqlite3
import sys

# 16 pares leidos verbatim en la clausula abrogatoria del abrogador.
# (ley_abrogada, abrogador, anio_abrogador)
ABROGADAS = [
    ("7", "129", "2015"),
    ("29", "519", "2026"),
    ("94", "517", "2026"),
    ("109", "519", "2026"),
    ("129", "500", "2025"),
    ("204", "454", "2022"),
    ("206", "443", "2021"),
    ("279", "517", "2026"),
    ("293", "517", "2026"),
    ("300", "517", "2026"),
    ("420", "517", "2026"),
    ("432", "500", "2025"),
    ("484", "517", "2026"),
    ("500", "520", "2026"),
    ("504", "523", "2026"),
    ("505", "523", "2026"),
]

# Vigentes con articulos derogados: la ley respira, partes de ella no.
PARCIALES = [
    ("151", "276", "2017"),
    ("202", "454", "2022"),
    ("438", "444", "2021"),
]

# Nombradas por el extractor y RECHAZADAS por la lectura verbatim.
RECHAZADAS = {
    "139": "la LD 454 abroga la LD 204, que modificaba a la 139. La 139 no es la abrogada",
    "10": "la LD 519 nombra solo la 109 y la 029. El '10' salio del propio '109'",
}


def fila(con, numero):
    cur = con.execute(
        "SELECT uid, numero, anio, titulo, vigente, derogada_por"
        " FROM documentos WHERE tipo_norma=? AND CAST(numero AS INTEGER)=?",
        ("Ley Departamental", int(numero)))
    return cur.fetchall()


def main():
    if len(sys.argv) < 2:
        print("uso: aplica_vigencia_adjudicada.py <base.db> [--aplicar]")
        return 2
    base = sys.argv[1]
    aplicar = "--aplicar" in sys.argv
    if not os.path.exists(base):
        print("ROJO: no existe %s" % base)
        return 1

    con = sqlite3.connect(base)
    antes_estado = con.execute(
        "SELECT COUNT(*) FROM documentos WHERE vigente IS NOT NULL").fetchone()[0]
    antes_nota = con.execute(
        "SELECT COUNT(*) FROM documentos WHERE derogada_por IS NOT NULL"
        " AND derogada_por<>?", ("",)).fetchone()[0]
    print("base: %s" % base)
    print("ANTES  con estado: %d | con nota: %d" % (antes_estado, antes_nota))
    print()

    plan = []
    faltan = []
    for numero, ab, anio in ABROGADAS:
        filas = fila(con, numero)
        if not filas:
            faltan.append((numero, "abrogada"))
            continue
        for f in filas:
            plan.append((f[0], 0, "Ley Departamental %s de %s" % (ab, anio),
                         "LD %s" % numero))
    for numero, ab, anio in PARCIALES:
        filas = fila(con, numero)
        if not filas:
            faltan.append((numero, "parcial"))
            continue
        for f in filas:
            plan.append((f[0], 1,
                         "parcialmente por Ley Departamental %s de %s" % (ab, anio),
                         "LD %s" % numero))

    print("PLAN: %d escrituras (%d abrogadas + %d parciales)"
          % (len(plan), len(ABROGADAS), len(PARCIALES)))
    for uid, vig, nota, etiqueta in plan:
        print("   %-8s vigente=%s  %s" % (etiqueta, vig, nota))
    if faltan:
        print()
        print("NO ESTAN EN EL CORPUS (no se inventan): %s" % faltan)
    print()
    print("RECHAZADAS por lectura verbatim, quedan sin tocar:")
    for numero, motivo in RECHAZADAS.items():
        print("   LD %-4s %s" % (numero, motivo))
    print()

    if not aplicar:
        print("modo plan. Nada escrito. Volver con --aplicar")
        return 0

    respaldo = base + ".antes-de-vigencia-masiva"
    con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    con.close()
    shutil.copy2(base, respaldo)
    print("respaldo: %s" % respaldo)

    con = sqlite3.connect(base)
    for uid, vig, nota, _ in plan:
        con.execute("UPDATE documentos SET vigente=?, derogada_por=? WHERE uid=?",
                    (vig, nota, uid))
    con.commit()
    con.execute("PRAGMA wal_checkpoint(TRUNCATE)")

    despues_estado = con.execute(
        "SELECT COUNT(*) FROM documentos WHERE vigente IS NOT NULL").fetchone()[0]
    despues_nota = con.execute(
        "SELECT COUNT(*) FROM documentos WHERE derogada_por IS NOT NULL"
        " AND derogada_por<>?", ("",)).fetchone()[0]
    print()
    print("DESPUES con estado: %d | con nota: %d" % (despues_estado, despues_nota))

    # Comprobacion: las rechazadas no pueden haber quedado marcadas muertas.
    malas = []
    for numero in RECHAZADAS:
        for f in fila(con, numero):
            if f[4] == 0:
                malas.append((numero, f[5]))
    if malas:
        print("ROJO: una rechazada quedo marcada como abrogada: %s" % malas)
        return 1
    print("ok: las %d rechazadas siguen sin estado de abrogacion" % len(RECHAZADAS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
