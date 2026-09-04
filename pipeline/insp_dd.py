import json, re
reg = json.load(open("/workspace/ab-probe-20260903/censo_dd.json"))
sin = [v for v in reg if not v["numero"]]
print("total", len(reg), "| sin numero/anio parseado:", len(sin))
print()
print("== 20 slugs SIN parsear, para ver la forma real")
for v in sin[:20]:
    print("   ", v["slug"][:105])
print()
print("== cuantos de los 'sin parsear' son realmente decretos departamentales")
pats = {
    "decreto-departamental": 0, "decreto-ejecutivo": 0, "resolucion": 0,
    "ley-departamental": 0, "otro": 0,
}
otros = []
for v in sin:
    s = v["slug"]
    for k in pats:
        if k != "otro" and k in s:
            pats[k] += 1
            break
    else:
        pats["otro"] += 1
        otros.append(s)
for k, n in pats.items():
    print("   %-24s %4d" % (k, n))
print()
print("== los 'otro' (12)")
for s in otros[:12]:
    print("   ", s[:105])
print()
print("== formas de numeracion que aparecen en los slugs de decreto")
formas = {}
for v in reg:
    s = v["slug"]
    for pat, etq in [(r"decreto-departamental-n-\d+-\d{4}", "n-NNN-AAAA"),
                     (r"decreto-departamental-nro-\d+", "nro-NNN"),
                     (r"decreto-departamental-\d+-\d{4}", "NNN-AAAA"),
                     (r"decreto-departamental-n-\d+(?!-\d{4})", "n-NNN sin anio"),
                     (r"decreto-departamental-n\d+", "nNNN")]:
        if re.search(pat, s):
            formas[etq] = formas.get(etq, 0) + 1
            break
    else:
        formas.setdefault("no reconocida", 0)
        formas["no reconocida"] += 1
for k in sorted(formas, key=lambda x: -formas[x]):
    print("   %-18s %4d" % (k, formas[k]))
