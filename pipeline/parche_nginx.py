#!/usr/bin/env python3
"""Agrega /verificar y /estado al nginx. Sin esto los endpoints existen en el servicio
y NO se pueden llamar desde afuera, que es exactamente el error del primer despliegue
de /texto. Entrada corpus-legal.conf md5 9a8107b7827af0db68a6a9c0d4207599"""
import hashlib, sys

VIEJO = "9a8107b7827af0db68a6a9c0d4207599"
ANCLA = """    location = /buscar {
        proxy_pass http://127.0.0.1:8080/buscar$is_args$args;
    }"""
NUEVO = """    location = /buscar {
        proxy_pass http://127.0.0.1:8080/buscar$is_args$args;
    }
    location = /verificar {
        proxy_pass http://127.0.0.1:8080/verificar$is_args$args;
    }
    location = /estado {
        proxy_pass http://127.0.0.1:8080/estado;
    }"""

def main(ruta):
    h = open(ruta, encoding="utf8").read()
    a = hashlib.md5(h.encode()).hexdigest()
    print("entrada md5", a)
    if a != VIEJO:
        print("ROJO: esperaba", VIEJO); return 1
    if h.count(ANCLA) != 1:
        print("ROJO: el ancla aparece", h.count(ANCLA), "veces"); return 1
    h = h.replace(ANCLA, NUEVO, 1)
    for t in ("/verificar$is_args$args", "location = /estado"):
        if t not in h:
            print("ROJO: falta", t); return 1
    open(ruta, "w", encoding="utf8").write(h)
    print("VERDE salida md5", hashlib.md5(h.encode()).hexdigest())
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "corpus-legal.conf"))
