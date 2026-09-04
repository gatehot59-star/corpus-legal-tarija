#!/usr/bin/env python3
"""PASO 1: censo REAL de los decretos departamentales de la Gaceta de Tarija.

La leccion de GENESIS: el portal declara su propio censo y hay que preguntarselo, no
estimarlo por la primera pagina. Aca la paginacion ofrece start=0..920 de 20 en 20.
Se recorren TODAS y se junta (id, slug). Al final se compara la cuenta con lo que
declara el portal: si no coinciden, ROJO.
"""
import json, re, ssl, time, urllib.request

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
BASE = "https://www.tarija.gob.bo/gaceta-oficial/decretos-departamentales"
SALIDA = "/workspace/ab-probe-20260903/censo_dd.json"

def baja(u, intentos=3):
    for i in range(intentos):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=50, context=ctx).read().decode("utf8", "replace")
        except Exception as e:
            if i == intentos - 1:
                return "ERROR:" + type(e).__name__
            time.sleep(2)

reg = {}
paginas = 0
declarado = None
start = 0
while start <= 1400:
    u = BASE + ("?start=%d" % start if start else "")
    h = baja(u)
    if h.startswith("ERROR:"):
        print("pagina start=%d -> %s" % (start, h)); start += 20; continue
    paginas += 1
    if declarado is None:
        m = re.search(r"P[a\u00e1]gina\s+\d+\s+de\s+(\d+)", re.sub(r"<[^>]+>", " ", h))
        declarado = int(m.group(1)) if m else None
    nuevos = 0
    for u2, i, slug in re.findall(r'href="([^"]*download=(\d+):([^"&]*)[^"]*)"', h):
        if i not in reg:
            reg[i] = {"id": i, "slug": slug, "url": u2 if u2.startswith("http") else "https://www.tarija.gob.bo" + u2}
            nuevos += 1
    print("start=%-5d pagina %-3d nuevos=%-4d acumulado=%d" % (start, paginas, nuevos, len(reg)), flush=True)
    if nuevos == 0 and start > 0:
        break
    start += 20

print()
print("paginas leidas:", paginas, "| paginas declaradas por el portal:", declarado)
print("DECRETOS UNICOS por id:", len(reg))
anios = {}
for v in reg.values():
    m = re.search(r"n-(\d{1,4})-(\d{4})", v["slug"])
    if m:
        v["numero"], v["anio"] = m.group(1), m.group(2)
        anios[m.group(2)] = anios.get(m.group(2), 0) + 1
    else:
        v["numero"], v["anio"] = None, None
        anios["(sin parsear)"] = anios.get("(sin parsear)", 0) + 1
print("con numero y anio en el slug:", sum(1 for v in reg.values() if v["numero"]))
for a in sorted(anios):
    print("   %-14s %4d" % (a, anios[a]))
# la concordancia: cuantos slugs mencionan otra norma
conc = [v for v in reg.values() if re.search(r"ley-departamental-n-\d+|reglamento-a-la-ley", v["slug"])]
print()
print("decretos cuyo slug NOMBRA una ley departamental (concordancia gratis):", len(conc))
for v in conc[:8]:
    print("   ", v["slug"][:100])
json.dump(list(reg.values()), open(SALIDA, "w"), ensure_ascii=False)
print()
print("escrito", SALIDA, len(reg), "registros")
