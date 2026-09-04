#!/usr/bin/env python3
"""guard_base.py - la base que se va a desplegar no puede haber perdido nada.

Nace de un dano real: la corrida de ingesta que corrio dos veces sobre el mismo
directorio temporal dejo bolivia-v8.db con el btree roto y 43 leyes
departamentales MENOS, y el COUNT(*) igual devolvia un numero: 5991. Un conteo
que contesta no prueba que la base este sana.

Segundo dano, este mio: la primera version preguntaba los documentos sin chunk
con un NOT EXISTS correlacionado. `chunks` es una tabla FTS5 sin indice por
uid, asi que eso son 6.079 barridos completos y el guard se colgaba. Un guard
que no termina es un guard que nadie corre. Se mide con una diferencia de
conjuntos: 1,5 s.

Uso:
    python3 guard_base.py <base.db> [--baseline baseline.json]
    python3 guard_base.py <base.db> --baseline b.json --escribir-baseline
    python3 guard_base.py <base.db> --rapido   # saltea integrity_check

Salida: 0 si TODO verde, 1 si algo rojo o NO MEDIDO.
"""
import argparse
import json
import os
import sqlite3
import sys
import time

BASELINE_POR_DEFECTO = {
    "documentos_min": 6079,
    "leyes_departamentales_exacto": 512,
    "chunks_min": 78930,
    "vigencia_escrita_min": 13,
    "chars_totales_min": 102620935,
}


def medir(db, rapido=False):
    """Devuelve (medidas, error_de_apertura). Nunca inventa un cero."""
    medidas = {}
    try:
        con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    except Exception as exc:
        return medidas, "no se pudo abrir: %s" % exc

    def q(sql, args=()):
        try:
            return con.execute(sql, args).fetchone()[0]
        except Exception as exc:
            return "NO_MEDIDO:%s" % type(exc).__name__

    if rapido:
        medidas["integrity_check"] = "NO_MEDIDO:saltado_por_--rapido"
    else:
        medidas["integrity_check"] = q("PRAGMA integrity_check(20)")
    medidas["documentos"] = q("SELECT COUNT(*) FROM documentos")
    medidas["leyes_departamentales"] = q(
        "SELECT COUNT(*) FROM documentos WHERE tipo_norma=?",
        ("Ley Departamental",))
    medidas["decretos_departamentales"] = q(
        "SELECT COUNT(*) FROM documentos WHERE tipo_norma=?",
        ("Decreto Departamental",))
    medidas["chunks"] = q("SELECT COUNT(*) FROM chunks")
    medidas["vigencia_escrita"] = q(
        "SELECT COUNT(*) FROM documentos WHERE vigente IS NOT NULL")
    medidas["chars_totales"] = q("SELECT SUM(chars) FROM documentos")
    medidas["uids_duplicados"] = q(
        "SELECT COUNT(*) FROM (SELECT uid FROM documentos"
        " GROUP BY uid HAVING COUNT(*) > 1)")

    # chunks es FTS5: sin indice por uid. Un barrido de cada lado y se comparan
    # en memoria, en vez de 6.079 barridos correlacionados.
    try:
        docs = set(r[0] for r in con.execute("SELECT uid FROM documentos"))
        conchunk = set(r[0] for r in con.execute("SELECT DISTINCT uid FROM chunks"))
        medidas["docs_sin_chunk"] = len(docs - conchunk)
        medidas["chunks_huerfanos"] = len(conchunk - docs)
    except Exception as exc:
        medidas["docs_sin_chunk"] = "NO_MEDIDO:%s" % type(exc).__name__
        medidas["chunks_huerfanos"] = "NO_MEDIDO:%s" % type(exc).__name__
    return medidas, None


def juzgar(medidas, base):
    """Tres estados: ok, ROJO y NO MEDIDO. El NO MEDIDO nunca es verde."""
    filas = []

    def fila(nombre, valor, ok, esperado):
        if isinstance(valor, str) and valor.startswith("NO_MEDIDO"):
            estado = "NO MEDIDO"
        else:
            estado = "ok" if ok else "ROJO"
        filas.append((nombre, valor, esperado, estado))

    ic = medidas.get("integrity_check")
    fila("integrity_check", str(ic)[:60], ic == "ok", "ok")
    for clave, minimo in (("documentos", "documentos_min"),
                          ("chunks", "chunks_min"),
                          ("vigencia_escrita", "vigencia_escrita_min"),
                          ("chars_totales", "chars_totales_min")):
        valor = medidas.get(clave)
        fila(clave, valor, isinstance(valor, int) and valor >= base[minimo],
             ">= %s" % base[minimo])
    valor = medidas.get("leyes_departamentales")
    exacto = base["leyes_departamentales_exacto"]
    fila("leyes_departamentales", valor, valor == exacto, "== %s" % exacto)
    for clave in ("docs_sin_chunk", "chunks_huerfanos", "uids_duplicados"):
        valor = medidas.get(clave)
        fila(clave, valor, valor == 0, "== 0")
    return filas


def main():
    par = argparse.ArgumentParser()
    par.add_argument("base")
    par.add_argument("--baseline", default=None)
    par.add_argument("--rapido", action="store_true",
                     help="saltea integrity_check; deja NO MEDIDO, no verde")
    par.add_argument("--escribir-baseline", action="store_true",
                     dest="escribir_baseline")
    arg = par.parse_args()

    base = dict(BASELINE_POR_DEFECTO)
    if arg.baseline and os.path.exists(arg.baseline):
        base.update(json.load(open(arg.baseline)))

    if not os.path.exists(arg.base):
        print("ROJO: la base no existe: %s" % arg.base)
        return 1

    inicio = time.time()
    medidas, error = medir(arg.base, rapido=arg.rapido)
    print("base: %s (%s bytes)" % (arg.base, os.path.getsize(arg.base)))
    if error:
        print("ROJO: %s" % error)
        return 1

    if arg.escribir_baseline:
        nuevo = {
            "documentos_min": medidas["documentos"],
            "leyes_departamentales_exacto": medidas["leyes_departamentales"],
            "chunks_min": medidas["chunks"],
            "vigencia_escrita_min": medidas["vigencia_escrita"],
            "chars_totales_min": medidas["chars_totales"],
        }
        destino = arg.baseline or "baseline.json"
        json.dump(nuevo, open(destino, "w"), indent=2)
        print("baseline escrito en %s: %s" % (destino, nuevo))
        return 0

    filas = juzgar(medidas, base)
    ancho = max(len(f[0]) for f in filas)
    for nombre, valor, esperado, estado in filas:
        print("  %-*s %-14s esperado %-16s %s"
              % (ancho, nombre, str(valor)[:14], esperado, estado))
    print("  (informativo) decretos_departamentales: %s"
          % medidas.get("decretos_departamentales"))
    print("  medido en %.1f s" % (time.time() - inicio))
    malas = [f for f in filas if f[3] != "ok"]
    if malas:
        print("VEREDICTO: ROJO -> "
              + ", ".join("%s=%s" % (f[0], f[3]) for f in malas))
        return 1
    print("VEREDICTO: VERDE %d/%d" % (len(filas), len(filas)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
