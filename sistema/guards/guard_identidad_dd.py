#!/usr/bin/env python3
"""guard_identidad_dd.py - el numero del catalogo tiene que coincidir con el sello
del propio documento.

Por que existe: el portal de la Gaceta de Tarija sirve, para el id 3396
catalogado como Decreto Departamental 071/2021, un PDF cuyo sello interno dice
070/2021 y cuyo sha256 es identico al del id 2049 (que SI es el 070/2021). Sin
esta comprobacion, el 070 entraba dos veces, una de ellas firmada como 071, con
hash correcto sobre el texto equivocado. Es la misma trampa del Codigo Procesal
Civil de 1975: la identidad no se hereda del nombre del archivo.

El instrumento es el SELLO: la linea "Corresponde al Decreto Departamental
<N> <numero>/<anio>" que la Gobernacion estampa en la cabecera, y como respaldo
el encabezado "DECRETO DEPARTAMENTAL <N> <numero>/<anio>".

TRES VERSIONES MIAS FALLARON ANTES DE ESTA, y las tres las caceria el control:

1. Buscar el primer numero de decreto del texto. Los decretos CITAN otros
   decretos en el CONSIDERANDO, asi que medi la cita y concluí sobre el sujeto.
   Daba 13 falsos positivos.
2. Exigir el simbolo de grado. El OCR lo destroza: N9, N2, h12, N 9, W, N5,
   hig, N", N?. 101 documentos quedaban "sin sello" cuando el sello estaba ahi.
3. Comodin \\S{0,4} para la basura. Es goloso y se comia los digitos del numero:
   sobre "N0020/2026" devolvia 0/2026. 27 falsos positivos.

La version que anda ancla en el ANIO valido (1980-2039) y toma los ultimos 3
digitos que lo preceden, asi la basura no puede robarle digitos al numero.

Uso:
    python3 guard_identidad_dd.py <recibo.jsonl> <dir_cache_txt>

Salida: 0 si no hay ningun DIFIERE, 1 si hay alguno.
"""
import collections
import json
import os
import re
import sys

# Ancla en el anio y toma los ultimos 3 digitos previos. El separador admite
# hasta 4 caracteres no numericos, porque el OCR mete ")", " ", "-" y comas.
PAR = re.compile(r"(\d{1,5})[^\d]{0,4}(19[89]\d|20[0-3]\d)")
FRASE_SELLO = r"Corresponde\s+al\s+Decreto\s+Departamental"
FRASE_ENCAB = r"DECRETO\s*DEPARTAMENTAL"
VENTANA = 26

# Sellos reales, tal como el OCR los dejo en el corpus. Si el parser no los lee,
# no sale a medir nada.
CONTROLES = [
    ("N\u00b0 020/2026", 20, "2026"),
    ("N0020/2026", 20, "2026"),
    ("N9 004/2026", 4, "2026"),
    ("h12 059/2023", 59, "2023"),
    ("W 052/2021", 52, "2021"),
    ('N" 057 2022', 57, "2022"),
    ("N? 129/2019", 129, "2019"),
    ("N2 0101)/2025", 101, "2025"),
    ("N5 013/2022", 13, "2022"),
    ("hig 012/2022", 12, "2022"),
    ("N 9 051/2023", 51, "2023"),
    ("N 2 065/2022", 65, "2022"),
]


def _tras(texto, frase, ventana=VENTANA):
    hallado = re.search(frase, texto, re.I)
    if not hallado:
        return None
    par = PAR.search(texto[hallado.end():hallado.end() + ventana])
    if not par:
        return None
    return int(par.group(1)[-3:]), par.group(2)


def sello(texto):
    """Devuelve (numero, anio, via). via='SIN_SELLO' cuando no se pudo leer."""
    res = _tras(texto[:6000], FRASE_SELLO)
    if res:
        return res[0], res[1], "corresponde_al"
    res = _tras(texto[:3000], FRASE_ENCAB)
    if res:
        return res[0], res[1], "encabezado"
    return None, None, "SIN_SELLO"


def control():
    print("=== CONTROL: %d sellos reales destrozados por el OCR ===" % len(CONTROLES))
    todo = True
    for basura, num, anio in CONTROLES:
        texto = ("GOBERNACION Corresponde al Decreto Departamental %s DECRETO..."
                 % basura)
        leido_n, leido_a, _ = sello(texto)
        ok = (leido_n == num and leido_a == anio)
        todo = todo and ok
        print("   %-16s -> %-10s esperado %-10s %s"
              % (basura, "%s/%s" % (leido_n, leido_a), "%s/%s" % (num, anio),
                 "ok" if ok else "FALLA"))
    print("   CONTROL DEL PARSER: %s"
          % ("%d/%d VERDE" % (len(CONTROLES), len(CONTROLES)) if todo
             else "HAY FALLAS"))
    return todo


def main():
    if len(sys.argv) < 3:
        print("uso: guard_identidad_dd.py <recibo.jsonl> <dir_cache_txt>")
        return 2
    recibo, cache = sys.argv[1], sys.argv[2]

    if not control():
        print("VEREDICTO: ROJO -> el parser no lee sus propios controles. "
              "No se mide nada mas.")
        return 1
    print()

    registros = [json.loads(l) for l in open(recibo) if l.strip()]
    buenos = [x for x in registros if x.get("estado") == "ok"]
    cuenta = collections.Counter()
    difieren = []
    por_sha = collections.defaultdict(list)
    for x in buenos:
        por_sha[x["sha256"]].append(x["id"])

    for x in buenos:
        ruta = os.path.join(cache, "%s.json" % x["id"])
        if not os.path.exists(ruta):
            cuenta["sin_cache"] += 1
            continue
        texto = json.load(open(ruta)).get("texto") or ""
        num, anio, via = sello(texto)
        cat_n = int(x["numero"]) if str(x["numero"]).isdigit() else None
        cat_a = str(x.get("anio") or "")
        if num is None:
            cuenta["SIN_SELLO_anexo" if x.get("anexo") else "SIN_SELLO_cuerpo"] += 1
            continue
        cuenta["via_" + via] += 1
        if num == cat_n and (not cat_a or anio == cat_a):
            cuenta["coincide"] += 1
            if not cat_a:
                cuenta["anio_recuperado_del_sello"] += 1
        else:
            cuenta["DIFIERE"] += 1
            gemelos = [i for i in por_sha[x["sha256"]] if i != x["id"]]
            difieren.append((x, num, anio, via, gemelos))

    print("=== IDENTIDAD sobre %d documentos extraidos ===" % len(buenos))
    for clave, valor in cuenta.most_common():
        print("   %-28s %s" % (clave, valor))
    print()
    if difieren:
        print("=== EL CATALOGO Y EL SELLO NO COINCIDEN ===")
        for x, num, anio, via, gemelos in difieren:
            print("   id=%-6s catalogo=%-10s SELLO=%s/%s (%s)%s"
                  % (x["id"], "%s/%s" % (x["numero"], x.get("anio")), num, anio,
                     via, "  MISMO TEXTO QUE %s" % gemelos if gemelos else ""))
            print("        %s" % x["slug"][:130])
        print()
        print("VEREDICTO: ROJO -> %d documentos no pueden ingestarse con el numero "
              "del catalogo" % len(difieren))
        return 1
    print("VEREDICTO: VERDE -> ningun documento contradice su propio sello")
    return 0


if __name__ == "__main__":
    sys.exit(main())
