#!/usr/bin/env python3
"""ROJO medido en produccion: /texto devolvia vigencia "derogada" pero
derogada_por=None, porque su SELECT no traia la columna. Resultado: el lector
mostraba DEROGADA sin decir por que norma, justo en las 4 leyes que son toda la
vidriera de la vigencia. /buscar si la traia, asi que la ficha estaba bien y el
lector mal: dos vistas del mismo dato con distinta verdad.

Agrega derogada_por Y jurisdiccion (la cita formal la usa para el departamento).
Entrada api.py md5 585447696a1bb3f84c6b21b018abce6e
"""
import hashlib, sys

VIEJO = "585447696a1bb3f84c6b21b018abce6e"
ANCLA = "SELECT d.tipo_norma,d.numero,d.anio,d.fecha,d.titulo,d.materia,d.sala,d.magistrado,d.organo,d.departamento,d.vigente,d.fuente_url,d.sha256,d.via_texto,d.chars,f.nombre fuente FROM documentos d"
NUEVO = "SELECT d.tipo_norma,d.numero,d.anio,d.fecha,d.titulo,d.materia,d.sala,d.magistrado,d.organo,d.departamento,d.jurisdiccion,d.vigente,d.derogada_por,d.fuente_url,d.sha256,d.via_texto,d.chars,f.nombre fuente FROM documentos d"

def main(ruta):
    h = open(ruta, encoding="utf8").read()
    a = hashlib.md5(h.encode()).hexdigest()
    print("entrada md5", a)
    if a != VIEJO:
        print("ROJO: entrada inesperada, esperaba", VIEJO); return 1
    if h.count(ANCLA) != 1:
        print("ROJO: el ancla aparece", h.count(ANCLA), "veces"); return 1
    h = h.replace(ANCLA, NUEVO, 1)
    for t in ("d.derogada_por,d.fuente_url", "d.jurisdiccion,d.vigente"):
        if t not in h:
            print("ROJO: falta en la salida:", t); return 1
    open(ruta, "w", encoding="utf8").write(h)
    print("VERDE salida md5", hashlib.md5(h.encode()).hexdigest())
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "api.py"))
