#!/usr/bin/env python3
"""Refuto mi propia conclusion de hace un minuto: dije que los ids de leyes y decretos
son de catalogos distintos y que el orden no se podia resolver. Es FALSO, y se ve con
mirar los ids intercalados: la Gaceta corre en Joomla, y Joomla usa UN contador global
de articulos para todo el sitio.

Prueba: si los ids fueran por categoria, los de leyes y decretos se solaparian. Si son
globales, ordenar por id reproduce el orden cronologico MEZCLANDO los dos tipos.
"""
import json, re, sqlite3
reg = [v for v in json.load(open("/workspace/ab-probe-20260903/censo_dd.json")) if "decreto-departamental" in v["slug"]]
c = sqlite3.connect("file:/workspace/bolivia-v7.db?mode=ro", uri=True); c.row_factory = sqlite3.Row
items = []
for r in c.execute("SELECT numero,anio,fecha,fuente_url FROM documentos WHERE tipo_norma='Ley Departamental'"):
    m = re.search(r"download=(\d+):", r["fuente_url"] or "")
    if m:
        items.append((int(m.group(1)), "LEY", r["numero"], r["anio"], (r["fecha"] or "")))
c.close()
NUM = [re.compile(r"decreto-departamental-n-(\d{1,4})(?:-a)?-(\d{4})"), re.compile(r"decreto-departamental-(\d{1,4})-(\d{4})")]
for v in reg:
    for p in NUM:
        m = p.search(v["slug"])
        if m:
            items.append((int(v["id"]), "DEC", m.group(1).lstrip("0"), m.group(2), ""))
            break
items.sort()
print("total items con id:", len(items), "| leyes", sum(1 for i in items if i[1] == "LEY"), "| decretos", sum(1 for i in items if i[1] == "DEC"))
print()
print("== los ids se INTERCALAN entre leyes y decretos? (ventana 3400-3620)")
for i in items:
    if 3400 <= i[0] <= 3620:
        print("   id %-5s %s %-5s anio %s %s" % (i[0], i[1], i[2], i[3], i[4]))
print()
print("== GUARD: el id ordena cronologicamente? Se prueba con los que tienen FECHA real.")
conf = [i for i in items if i[1] == "LEY" and re.match(r"\d{4}-\d\d-\d\d", i[4])]
inv = sum(1 for a, b in zip(conf, conf[1:]) if a[4] > b[4])
print("   leyes con fecha exacta:", len(conf), "| pares fuera de orden:", inv,
      "(%.1f%%)" % (100.0 * inv / max(len(conf) - 1, 1)))
print()
ld520 = [i for i in items if i[1] == "LEY" and i[2] == "520"]
dd16 = [i for i in items if i[1] == "DEC" and i[2] == "16" and i[3] == "2026"]
if ld520 and dd16:
    print("== EL CASO: DD 16/2026 id %s vs LD 520 id %s" % (dd16[0][0], ld520[0][0]))
    if dd16[0][0] < ld520[0][0]:
        print("   El decreto se publico ANTES que la LD 520 -> CONSISTENTE.")
        print("   La LD 500 estaba viva cuando el DD 16/2026 la reglamento, y la LD 520 la")
        print("   abrogo despues. La contradiccion se disuelve y mi dato de vigencia AGUANTA.")
    else:
        print("   El decreto es POSTERIOR: la derogacion de la LD 500 queda en duda.")
