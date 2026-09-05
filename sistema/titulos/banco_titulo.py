#!/usr/bin/env python3
"""Banco del extractor de titulos. Positivos Y NEGATIVOS.

Hoy mismo un control de puros positivos (17/17) me dejo pasar 2 falsos positivos en
la vigencia: casi mate la Ley de Administracion del Presupuesto y la Ley de
Autonomia Regional del Gran Chaco. Un control de puros positivos mide recall, no
precision, y no puede cazar un invento por construccion.

Aca los negativos son casos reales de este corpus donde NO hay titulo detras de la
formula de sancion. El extractor tiene que devolver None en todos.

Uso:  python3 banco_titulo.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from titulo_sancionado import extraer

POSITIVOS = [
    ("caso limpio entre comillas",
     'LEY DEPARTAMENTAL N*089\n\nLA ASAMBLEA LEGISLATIVA DEPARTAMENTAL DE TARIJA\n'
     'SANCIONA:\n\n\u201cPROMOCI\u00d3N DEL RIEGO TECNIFICADO EN EL DEPARTAMENTO DE\n'
     'TARIJA\u201d\n\nART\u00cdCULO 1. (Objeto).',
     "PROMOCI\u00d3N DEL RIEGO TECNIFICADO EN EL DEPARTAMENTO DE TARIJA"),
    ("decreta en vez de sanciona",
     'LEY DEPARTAMENTAL N*65\nLA ASAMBLEA LEGISLATIVA DEPARTAMENTAL DECRETA:\n'
     '\u201cPERSONALIDAD Y NATURALEZA JURIDICA DE LA EMPRESA P\u00daBLICA DEPARTAMENTAL '
     'DE SERVICIOS ELECTRICOS DE TARIJA SETAR\u201d\nART\u00cdCULO 1.- (Personalidad).',
     "PERSONALIDAD Y NATURALEZA JURIDICA DE LA EMPRESA P\u00daBLICA DEPARTAMENTAL "
     "DE SERVICIOS ELECTRICOS DE TARIJA SETAR"),
    ("membrete con ruido de OCR antes del marcador",
     '" ASAMBLEA LEGISLATIVA DEPARTAMENTAL TARIJA Somos Todos \u00d1ande aparte vaz lar\n'
     'LEY DEPARTAMENTAL N* 125\nLA ASAMBLEA LEGISLATIVA DEPARTAMENTAL DE TARIJA\n'
     'SANCIONA:\n"PROMOCION Y FOMENTO CON LA ASIGNACION DE RECURSOS AL CARNAVAL '
     'CHAPACO\u201d\nArt\u00edculo 1.- (Objeto)',
     "PROMOCION Y FOMENTO CON LA ASIGNACION DE RECURSOS AL CARNAVAL CHAPACO"),
    ("sin comillas, bloque en mayusculas",
     'LEY DEPARTAMENTAL N* 200\nLA ASAMBLEA LEGISLATIVA DEPARTAMENTAL DE TARIJA\n'
     'SANCIONA:\n\nLEY DE FOMENTO A LA PRODUCCION DE VID EN EL VALLE CENTRAL\n\n'
     'ARTICULO 1. (Objeto)',
     "LEY DE FOMENTO A LA PRODUCCION DE VID EN EL VALLE CENTRAL"),
]

NEGATIVOS = [
    ("no hay formula de sancion: NO inventar",
     'GOBERNACION DEL DEPARTAMENTO DE TARIJA\n'
     'Corresponde al Decreto Departamental N 070/2021\n'
     'CONSIDERANDO: Que el Articulo 277'),
    ("tras el marcador solo viene la fecha (LD 012 real)",
     'LEY DEPARTAMENTAL N* 012\nSANCIONA:\n\nLEY DE 20 DE ENERO DE 2011\n\n'
     'POR CUANTO: La Asamblea'),
    ("tras el marcador solo un nombre propio corto (LD 016 real)",
     'LEY DEPARTAMENTAL N* 016\nSANCIONA:\n\u201cSAN LORENZO\u201d\nARTICULO 1.'),
    ("tras el marcador viene el organo, no el titulo (LD 005 real)",
     'LEY N* 005\nSANCIONA:\n\nLA ASAMBLEA LEGISLATIVA DEPARTAMENTAL DE TARIJA\n\n'
     'ARTICULO 1.'),
    ("cita entre comillas que no es titulo (LD 006 real)",
     'LEY DEPARTAMENTAL N* 006\nSANCIONA:\n'
     '\u201cy el par\u00e1grafo II del mismo Art\u00edculo se\u00f1ala que:\u201d\nARTICULO 1.'),
    ("texto vacio", ""),
]


def main():
    todo = True
    print("=== POSITIVOS: tiene que devolver el titulo exacto ===")
    for nombre, texto, esperado in POSITIVOS:
        titulo, via = extraer(texto)
        ok = (titulo == esperado)
        todo = todo and ok
        print("   %-56s %-6s (%s)" % (nombre, "ok" if ok else "FALLA", via))
        if not ok:
            print("        esperaba: %r" % esperado)
            print("        obtuvo  : %r" % titulo)
    print()
    print("=== NEGATIVOS: tiene que devolver None ===")
    for nombre, texto in NEGATIVOS:
        titulo, via = extraer(texto)
        ok = (titulo is None)
        todo = todo and ok
        print("   %-56s %-6s (%s)" % (nombre, "ok" if ok else "FALLA", via))
        if not ok:
            print("        invento: %r" % titulo)
    print()
    total = len(POSITIVOS) + len(NEGATIVOS)
    print("BANCO DEL EXTRACTOR: %s"
          % ("%d/%d VERDE" % (total, total) if todo else "HAY FALLAS"))
    return 0 if todo else 1


if __name__ == "__main__":
    sys.exit(main())
