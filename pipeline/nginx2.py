#!/usr/bin/env python3
"""La pagina de estado necesita su ruta: el nginx cierra todo lo que no conoce con un
404 JSON. Entrada corpus-legal.conf md5 f8780f939ed06a8f05f17f4c0ec3be95"""
import hashlib, sys
VIEJO = "f8780f939ed06a8f05f17f4c0ec3be95"
ANCLA = """    location = /estado {
        proxy_pass http://127.0.0.1:8080/estado;
    }"""
NUEVO = """    location = /estado {
        proxy_pass http://127.0.0.1:8080/estado;
    }
    location = /estado-del-corpus {
        try_files /estado.html =404;
    }"""
def main(ruta):
    h = open(ruta, encoding="utf8").read()
    a = hashlib.md5(h.encode()).hexdigest()
    print("entrada md5", a)
    if a != VIEJO:
        print("ROJO: esperaba", VIEJO); return 1
    if h.count(ANCLA) != 1:
        print("ROJO: ancla x", h.count(ANCLA)); return 1
    h = h.replace(ANCLA, NUEVO, 1)
    if "estado-del-corpus" not in h or h.count("location = /estado ") + h.count("location = /estado {") < 1:
        print("ROJO: salida mal"); return 1
    open(ruta, "w", encoding="utf8").write(h)
    print("VERDE salida md5", hashlib.md5(h.encode()).hexdigest())
    return 0
if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "corpus-legal.conf"))
