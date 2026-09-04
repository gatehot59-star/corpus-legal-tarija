#!/usr/bin/env python3
"""EL ATAJO QUE LA MEDICION DESTAPO: la concordancia no esta en los PDFs, esta en los
SLUGS del catalogo, y bajarlos costo 0 bytes de descarga adicional.

Los 935 slugs de decretos declaran a QUE ley departamental reglamentan o modifican. Eso
es exactamente el grafo que /verificar necesita, y no requiere ni el OCR de 2,8 GB ni
una sola descarga mas.

Tres estados: si el slug no nombra una ley, este decreto no aporta concordancia y se
declara, no se infiere.
"""
import json, re, sqlite3
from collections import defaultdict

REL = [
    (re.compile(r"reglamento-(?:parcial-)?(?:a-la|de-la|a|de)-ley-departamental-n-?(\d{1,4})"), "reglamenta"),
    (re.compile(r"reglamento-(?:parcial-)?(?:a-la|de-la|a|de)-la-ley-departamental-n-?(\d{1,4})"), "reglamenta"),
    (re.compile(r"reglamenta(?:cion)?-(?:a-la-|de-la-)?ley-departamental-n-?(\d{1,4})"), "reglamenta"),
    (re.compile(r"modificacion(?:es)?-al-reglamento-a-la-ley-departamental-n-?(\d{1,4})"), "modifica el reglamento de"),
    (re.compile(r"modifica(?:torio|toria|cion)?-(?:a-la-|de-la-)?ley-departamental-n-?(\d{1,4})"), "modifica"),
    (re.compile(r"ley-departamental-n-?(\d{1,4})"), "menciona"),
]

reg = [v for v in json.load(open("/workspace/ab-probe-20260903/censo_dd.json")) if "decreto-departamental" in v["slug"]]
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

hallados, sin_rel = [], 0
for v in reg:
    s = v["slug"]
    dn, da = ident(s)
    rel = None
    for p, tipo in REL:
        m = p.search(s)
        if m:
            rel = (tipo, m.group(1).lstrip("0") or "0")
            break
    if rel:
        hallados.append({"decreto": dn, "anio_decreto": da, "relacion": rel[0], "ley": rel[1],
                         "slug": s, "id": v["id"]})
    else:
        sin_rel += 1

print("decretos analizados:", len(reg))
print("con concordancia declarada en el slug:", len(hallados))
print("sin concordancia (no aporta, DECLARADO):", sin_rel)
print()
tipos = defaultdict(int)
for h in hallados:
    tipos[h["relacion"]] += 1
for k in sorted(tipos, key=lambda x: -tipos[x]):
    print("   %-28s %4d" % (k, tipos[k]))
print()
# cruce contra el corpus: la ley que el decreto nombra, existe?
c = sqlite3.connect("file:/workspace/bolivia-v7.db?mode=ro", uri=True); c.row_factory = sqlite3.Row
leyes = {}
for r in c.execute("SELECT uid,numero,anio,titulo,vigente,derogada_por FROM documentos "
                   "WHERE tipo_norma='Ley Departamental' AND numero GLOB '[0-9]*'"):
    leyes.setdefault(str(int(r["numero"])), []).append(dict(r))
c.close()
enc = [h for h in hallados if h["ley"] in leyes]
print("concordancias cuya LEY esta en el corpus:", len(enc), "de", len(hallados))
print("leyes distintas alcanzadas:", len(set(h["ley"] for h in enc)))
print()
print("== MUESTRA: la ley, su estado, y el decreto que la reglamenta")
vistas = set()
for h in sorted(enc, key=lambda x: (x["ley"], str(x["anio_decreto"])))[:16]:
    if h["ley"] in vistas:
        continue
    vistas.add(h["ley"])
    f = leyes[h["ley"]][0]
    est = "derogada" if f["vigente"] == 0 else ("vigente" if f["vigente"] == 1 else "no verificada")
    print("   LD %-4s (%s) [%s] <- DD %s/%s %s" % (h["ley"], f["anio"] or "?", est,
          h["decreto"], h["anio_decreto"] or "?", h["relacion"]))
    print("        %s" % (f["titulo"] or "")[:88])
json.dump(hallados, open("/workspace/ab-probe-20260903/concordancia_dd.json", "w"), ensure_ascii=False, indent=0)
print()
print("escrito concordancia_dd.json con", len(hallados), "relaciones")
