#!/usr/bin/env python3
"""ROJO encontrado por el test 4: /buscar contaba el total SIN los filtros.
Con anio=2018 la API devolvia total_pasajes 1741 (el total del termino) y la
interfaz calculaba 146 paginas cuando el filtro tiene muchas menos: las paginas
del final servian vacio. El contador ahora comparte el MISMO where que las filas.

Entrada api.py md5 d12b1a59a847541d19885df10fb34c84
"""
import hashlib, sys

VIEJO = "d12b1a59a847541d19885df10fb34c84"

ANCLA = '        total=DBC.execute("SELECT count(*) n FROM chunks WHERE chunks MATCH ?",(m,)).fetchone()["n"]'
NUEVO = ('        # El total tiene que contar lo MISMO que se devuelve: si el filtro entra en\n'
         '        # las filas y no en el conteo, la interfaz calcula paginas que no existen.\n'
         '        total=DBC.execute("SELECT count(*) n FROM chunks c JOIN documentos d ON d.uid=c.uid WHERE chunks MATCH ?"+where,[m]+args[3:]).fetchone()["n"]')

def main(ruta):
    h = open(ruta, encoding="utf8").read()
    a = hashlib.md5(h.encode()).hexdigest()
    print("entrada md5", a)
    if a != VIEJO:
        print("ROJO: entrada inesperada, esperaba", VIEJO); return 1
    if h.count(ANCLA) != 1:
        print("ROJO: el ancla aparece", h.count(ANCLA), "veces"); return 1
    h = h.replace(ANCLA, NUEVO, 1)
    if 'JOIN documentos d ON d.uid=c.uid WHERE chunks MATCH ?"+where' not in h:
        print("ROJO: la salida no quedo con el where en el conteo"); return 1
    open(ruta, "w", encoding="utf8").write(h)
    print("VERDE salida md5", hashlib.md5(h.encode()).hexdigest())
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "api.py"))
