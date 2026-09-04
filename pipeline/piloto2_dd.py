#!/usr/bin/env python3
"""El piloto 1 tomo 2 por ano ORDENADO y solo llego a 2016: midio los escaneos viejos y
proyecto 1 GB con 71% de OCR. Eso es un sesgo de seleccion, no un resultado.

Los anos 2017-2026 son 561 de los 935 decretos, o sea el 60% del material, y son los que
un abogado consulta. Se miden esos, y la proyeccion se hace POR TRAMO, no con un promedio
que mezcla un escaneo de 5 MB con un PDF nativo de 200 KB.
"""
import json, os, re, ssl, time, urllib.request
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
DEST = "/workspace/ab-probe-20260903/dd_pdf"
os.makedirs(DEST, exist_ok=True)
NUM = [re.compile(r"decreto-departamental-n-(\d{1,4})(?:-a)?-(\d{4})"),
       re.compile(r"decreto-departamental-(\d{1,4})-(\d{4})"),
       re.compile(r"decreto-departamental-n-(\d{1,4})\b")]
def ident(slug):
    for p in NUM:
        m = p.search(slug)
        if m:
            g = m.groups()
            return (g[0].lstrip("0") or "0"), (g[1] if len(g) > 1 else None)
    return None, None
reg = [v for v in json.load(open("/workspace/ab-probe-20260903/censo_dd.json")) if "decreto-departamental" in v["slug"]]
por = {}
for v in reg:
    n, a = ident(v["slug"])
    v["numero"], v["anio"] = n, a
    por.setdefault(a, []).append(v)
MODERNOS = [a for a in por if a and int(a) >= 2017]
print("decretos 2017-2026:", sum(len(por[a]) for a in MODERNOS), "de", len(reg))
muestra = []
for a in sorted(MODERNOS):
    muestra += por[a][:2]
print("piloto 2:", len(muestra), "descargas sobre el tramo moderno")
print()
res = []
for v in muestra:
    try:
        b = urllib.request.urlopen(urllib.request.Request(v["url"], headers=H), timeout=70, context=ctx).read()
    except Exception as e:
        print("  DD %-4s %-5s ERROR %s" % (v["numero"], v["anio"], type(e).__name__)); continue
    fonts, imgs = b.count(b"/Font"), b.count(b"/Image")
    p = os.path.join(DEST, "dd-%s-%s-%s.pdf" % (v["anio"], (v["numero"] or "sn").zfill(3), v["id"]))
    open(p, "wb").write(b)
    res.append({"anio": v["anio"], "bytes": len(b), "fonts": fonts})
    print("  DD %-4s %-5s %8d B  /Font=%-4d /Image=%-4d %s" % (v["numero"], v["anio"], len(b), fonts, imgs,
          "TEXTO NATIVO" if fonts else "escaneo -> OCR"))
    time.sleep(0.35)
print()
nat = [r for r in res if r["fonts"]]
esc = [r for r in res if not r["fonts"]]
print("tramo moderno: texto nativo", len(nat), "| escaneo", len(esc))
if res:
    prom = sum(r["bytes"] for r in res) / len(res)
    print("promedio moderno: %.0f B" % prom)
    n_mod = sum(len(por[a]) for a in MODERNOS)
    n_viejo = len(reg) - n_mod
    print()
    print("== PROYECCION POR TRAMO (el promedio global mentia)")
    print("   2017-2026: %4d decretos x %.0f B = %.0f MB" % (n_mod, prom, n_mod * prom / 1e6))
    print("   2010-2016: %4d decretos x 1109633 B (medido en piloto 1) = %.0f MB" % (n_viejo, n_viejo * 1109633 / 1e6))
    print("   TOTAL estimado: %.0f MB" % ((n_mod * prom + n_viejo * 1109633) / 1e6))
    print("   OCR necesario: %d de %d en el tramo moderno (%.0f%%)" % (len(esc), len(res), 100 * len(esc) / len(res)))
