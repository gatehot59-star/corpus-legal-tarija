#!/usr/bin/env python3
"""PASO 2: piloto de descarga. Antes de lanzar 939 descargas, medir 14 y responder
tres preguntas que deciden todo el trabajo:

  1. el portal entrega PDF de verdad, o HTML de error con http 200?
  2. el PDF trae texto nativo, o hace falta OCR? (el OCR cambia el costo por 20x)
  3. el numero y el anio se extraen del slug con las DOS formas medidas?

Se eligen 14 repartidos por ano, no los 14 primeros: si solo pruebo 2026 no se nada
de los escaneos de 2019.
"""
import hashlib, io, json, os, re, ssl, time, urllib.request

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
DEST = "/workspace/ab-probe-20260903/dd_pdf"
os.makedirs(DEST, exist_ok=True)

NUM = [re.compile(r"decreto-departamental-n-(\d{1,4})(?:-a)?-(\d{4})"),
       re.compile(r"decreto-departamental-(\d{1,4})-(\d{4})"),
       re.compile(r"decreto-departamental-n-(\d{1,4})\b")]

def id_norma(slug):
    for i, p in enumerate(NUM):
        m = p.search(slug)
        if m:
            g = m.groups()
            return g[0].lstrip("0") or "0", (g[1] if len(g) > 1 else None), i + 1
    return None, None, 0

reg = json.load(open("/workspace/ab-probe-20260903/censo_dd.json"))
reg = [v for v in reg if "decreto-departamental" in v["slug"]]
print("decretos reales en el censo:", len(reg), "(de 940 registros; 1 era formulario-de-residencia)")
ok = sum(1 for v in reg if id_norma(v["slug"])[0])
print("numero extraible del slug:", ok, "| sin numero:", len(reg) - ok)
por_anio = {}
for v in reg:
    n, a, via = id_norma(v["slug"])
    por_anio.setdefault(a, []).append(v)
print("anios:", {k: len(v) for k, v in sorted(por_anio.items(), key=lambda kv: str(kv[0]))})
print()
# muestra repartida: 2 por ano
muestra = []
for a in sorted(por_anio, key=lambda x: str(x)):
    muestra += por_anio[a][:2]
muestra = muestra[:14]
print("== PILOTO de", len(muestra), "descargas, repartidas por ano")
tot_bytes = 0
res = []
for v in muestra:
    n, a, via = id_norma(v["slug"])
    try:
        r = urllib.request.urlopen(urllib.request.Request(v["url"], headers=H), timeout=70, context=ctx)
        b = r.read()
        ct = r.headers.get("Content-Type", "?")
    except Exception as e:
        print("  DD %-5s %-5s ERROR %s" % (n, a, type(e).__name__)); continue
    tot_bytes += len(b)
    es_pdf = b[:5] == b"%PDF-"
    # texto nativo: los objetos de texto del PDF sin descomprimir ya delatan si hay fuentes
    tiene_font = b.count(b"/Font")
    tiene_img = b.count(b"/Image")
    p = os.path.join(DEST, "dd-%s-%s-%s.pdf" % (a or "sa", (n or "sn").zfill(3), v["id"]))
    open(p, "wb").write(b)
    res.append({"id": v["id"], "numero": n, "anio": a, "via_slug": via, "bytes": len(b),
                "pdf": es_pdf, "fonts": tiene_font, "images": tiene_img,
                "sha256": hashlib.sha256(b).hexdigest()[:12], "archivo": p})
    print("  DD %-5s %-5s %8d B  pdf=%-5s /Font=%-4d /Image=%-4d ct=%s" %
          (n, a, len(b), es_pdf, tiene_font, tiene_img, ct[:24]))
    time.sleep(0.4)
print()
print("descargados:", len(res), "| bytes", tot_bytes, "| promedio", tot_bytes // max(len(res), 1))
print("proyeccion para %d decretos: %.1f MB" % (len(reg), len(reg) * (tot_bytes / max(len(res), 1)) / 1e6))
print("con /Font (texto nativo probable):", sum(1 for r in res if r["fonts"]))
print("sin /Font (escaneo, requiere OCR):", sum(1 for r in res if not r["fonts"]))
json.dump(res, open("/workspace/ab-probe-20260903/dd_piloto.json", "w"), ensure_ascii=False, indent=0)
