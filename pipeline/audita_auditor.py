#!/usr/bin/env python3
"""Audito al auditor con el mismo criterio: cada afirmacion, medida.

1. Deduplicacion de los 935: el auditor dice 780-880 reales. Se mide.
2. Anexos listados como items: se cuentan.
3. Duplicados por numero+anio: se cuentan.
4. Huecos de numeracion: se listan.
"""
import json, re
from collections import defaultdict
reg = json.load(open("/workspace/ab-probe-20260903/censo_dd.json"))
print("registros del censo:", len(reg))
anexos = [v for v in reg if v["slug"].startswith("anexo") or re.search(r"\banexo\b", v["slug"][:14])]
print("ANEXOS (el auditor tiene razon en que existen):", len(anexos))
for v in anexos:
    print("   ", v["slug"][:96])
noticia = [v for v in reg if "decreto-departamental" not in v["slug"]]
print()
print("registros que NO son decretos:", len(noticia))
for v in noticia:
    print("   ", v["slug"][:96])
print()
NUM = [re.compile(r"decreto-departamental-n-(\d{1,4})(?:-a)?-(\d{4})"),
       re.compile(r"decreto-departamental-(\d{1,4})-(\d{4})"),
       re.compile(r"decreto-departamental-n-(\d{1,4})\b")]
def ident(s):
    for p in NUM:
        m = p.search(s)
        if m:
            g = m.groups()
            return (g[0].lstrip("0") or "0"), (g[1] if len(g) > 1 else None)
    return None, None
utiles = [v for v in reg if "decreto-departamental" in v["slug"] and v not in anexos]
clave = defaultdict(list)
for v in utiles:
    n, a = ident(v["slug"])
    clave[(n, a)].append(v)
dups = {k: v for k, v in clave.items() if len(v) > 1}
print("decretos (sin anexos ni ruido):", len(utiles))
print("claves numero+anio distintas:", len(clave))
print("claves con MAS de un registro (duplicados):", len(dups))
extra = sum(len(v) - 1 for v in dups.values())
print("registros duplicados de mas:", extra)
for k, v in list(dups.items())[:10]:
    print("   DD %s/%s x%d" % (k[0], k[1], len(v)))
    for x in v:
        print("        id %-5s %s" % (x["id"], x["slug"][:80]))
print()
print("== VEREDICTO SOBRE EL AUDITOR")
print("   el auditor estimo 780-880 decretos unicos.")
print("   MEDIDO: %d claves numero+anio distintas (de %d registros)" % (len(clave), len(reg)))
sinanio = [k for k in clave if not k[1]]
print("   claves sin anio (no deduplicables por este metodo):", len(sinanio))
print()
print("== HUECOS de numeracion en 2026, que el auditor senalo")
n2026 = sorted(int(k[0]) for k in clave if k[1] == "2026" and k[0])
print("   numeros presentes:", n2026)
faltan = [i for i in range(1, max(n2026) + 1) if i not in n2026] if n2026 else []
print("   huecos:", faltan)
