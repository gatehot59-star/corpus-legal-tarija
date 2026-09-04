#!/usr/bin/env python3
"""GUARD: un abrogador muerto no mata. Antes de escribir 'derogada', se verifica que
la norma que abroga siga viva.

El caso que lo obliga, medido hoy: LexiVox declara que el Codigo de Procedimiento Penal
(Ley 1970 de 1999) y la Ley 1768 estan 'Abrogadas por el Codigo del Sistema Penal,
20 de diciembre de 2017'. Y el Codigo del Sistema Penal (Ley 1005) fue ABROGADO por la
Ley 1027 del 25 de enero de 2018, 36 dias despues, antes de entrar en vigencia:
'Abrogacion Del Codigo del Sistema Penal. Articulo Unico'.

O sea: la abrogacion NUNCA surtio efecto y el Codigo de Procedimiento Penal es el que
rige TODO proceso penal en Bolivia hoy. Escribir 'derogada' ahi le hace descartar al
abogado el codigo que si tiene que aplicar. Es el peor error posible de este corpus.

Este guard tiene que poder dar ROJO. Se prueba con los dos casos:
  - abrogador VIVO   -> la abrogacion vale
  - abrogador MUERTO -> la abrogacion NO vale
"""
import sys
sys.path.insert(0, "/workspace/ab-probe-20260903")
from vig_nac3 import leer

def abrogacion_vale(ident_abrogador):
    """(vale, motivo). Tres estados: True, False, o None si no se pudo medir."""
    r, err = leer(ident_abrogador.replace(".html", ".xhtml"))
    if err:
        return None, "no se pudo medir el abrogador: " + err
    muertes, _ = r
    if muertes:
        quien = "; ".join("%s %s" % (e, t) for e, i, t in muertes)
        return False, "el abrogador esta abrogado (" + quien + ")"
    return True, "el abrogador no declara abrogacion propia"

if __name__ == "__main__":
    CASOS = [
        ("BO-L-N1005.html", "Codigo del Sistema Penal 2017", False),
        ("BO-L-N25.html", "Ley del Organo Judicial 2010", True),
        ("BO-L-N439.html", "Codigo Procesal Civil 2013", True),
    ]
    fallos = 0
    for ident, etq, esperado in CASOS:
        vale, motivo = abrogacion_vale(ident)
        ok = (vale == esperado)
        if not ok:
            fallos += 1
        print("%-6s %-34s vale=%-5s esperado=%-5s | %s" % ("OK" if ok else "ROJO", etq, vale, esperado, motivo))
    print()
    print("banco:", len(CASOS) - fallos, "/", len(CASOS))
    sys.exit(1 if fallos else 0)
