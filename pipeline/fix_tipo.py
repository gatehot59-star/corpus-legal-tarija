#!/usr/bin/env python3
"""Segundo ROJO del mismo caso: 'Ley 1970' ahora se interpreta bien pero da
ausente_del_corpus, porque en la base ese documento esta catalogado tipo_norma='Codigo'
(es el Codigo de Procedimiento Penal). El filtro de tipo era demasiado estricto.

El arreglo NO puede ser aflojar el filtro y callarse: 'Ley 129' nacional matchearia la
Ley Departamental 129 y eso es exactamente el falso positivo del 67% de la primera
version del extractor de vigencia. Asi que se busca sin tipo COMO SEGUNDO INTENTO y la
respuesta DECLARA que el tipo no coincide.

Entrada api_v4.py md5 2c7368192983886db696472d7dc026df
"""
import hashlib, sys

VIEJO = "2c7368192983886db696472d7dc026df"

V1 = '''    filas = buscar_norma(tipo, numero, anio)
    if not filas:
        return dict(base, estado="ausente_del_corpus", coincidencias=0,'''
N1 = '''    filas = buscar_norma(tipo, numero, anio)
    tipo_difiere = False
    if not filas and tipo:
        # segundo intento sin el tipo: la Ley 1970 esta catalogada como 'Codigo'.
        # Se acepta pero se DECLARA, porque aflojar el tipo en silencio es como se
        # confunde una ley nacional con una departamental del mismo numero.
        filas = buscar_norma(None, numero, anio)
        tipo_difiere = bool(filas)
    if not filas:
        return dict(base, estado="ausente_del_corpus", coincidencias=0,'''

V2 = '''    out = dict(base, estado=est, coincidencias=len(filas), norma=ficha_min(principal),'''
N2 = '''    out = dict(base, estado=est, coincidencias=len(filas), tipo_difiere=tipo_difiere,
               norma=ficha_min(principal),'''

V3 = '''    if est == "derogada":
        out["advertencia"] = ("DEROGADA. No la cites como vigente. Sucesora declarada: %s"
                              % (principal["derogada_por"] or "no registrada"))'''
N3 = '''    prefijo = ""
    if tipo_difiere:
        prefijo = ("ATENCION: la cita dice '%s' y en el corpus esta catalogada como '%s'. "
                   "Confirma que sea la misma norma antes de usarla. " % (tipo, principal["tipo_norma"]))
    if est == "derogada":
        out["advertencia"] = (prefijo + "DEROGADA. No la cites como vigente. Sucesora declarada: %s"
                              % (principal["derogada_por"] or "no registrada"))'''

V4 = '''        out["advertencia"] = "Vigencia verificada contra la fuente oficial al momento de la carga."'''
N4 = '''        out["advertencia"] = prefijo + "Vigencia verificada contra la fuente oficial al momento de la carga."'''

V5 = '''        out["advertencia"] = ("NO VERIFICADA. El corpus no midio la vigencia de esta norma. "'''
N5 = '''        out["advertencia"] = (prefijo + "NO VERIFICADA. El corpus no midio la vigencia de esta norma. "'''

R = [(V1, N1), (V2, N2), (V3, N3), (V4, N4), (V5, N5)]
VERDES = ["tipo_difiere", "ATENCION: la cita dice", "prefijo + "]

def main(ruta):
    h = open(ruta, encoding="utf8").read()
    a = hashlib.md5(h.encode()).hexdigest()
    print("entrada md5", a)
    if a != VIEJO:
        print("ROJO: esperaba", VIEJO); return 1
    for i, (v, n) in enumerate(R, 1):
        c = h.count(v)
        if c != 1:
            print("ROJO: ancla", i, "aparece", c, "veces"); return 1
        h = h.replace(v, n, 1)
        print("  ancla", i, "aplicada")
    for t in VERDES:
        if t not in h:
            print("ROJO: falta", t); return 1
    open(ruta, "w", encoding="utf8").write(h)
    print("VERDE salida md5", hashlib.md5(h.encode()).hexdigest())
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "api.py"))
