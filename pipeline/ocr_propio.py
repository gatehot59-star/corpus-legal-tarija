#!/usr/bin/env python3
"""EL USUARIO TIENE RAZON Y YO ESTABA EQUIVOCADO: no hay que pagar ningun OCR.

Tesseract 5.5.3 con 125 idiomas ya esta en /workspace/ocrenv, instalado hace dias, junto
con pdftoppm y pdftotext de poppler. Escribi 'pagar el OCR' sin consultar mi propio
inventario, que es el patron 3 del registro de errores: afirmar un limite sin verificar.

Este script MIDE lo que cuesta con lo que ya tenemos, en tres pasos y sobre decretos
reales del piloto:
  1. pdftotext primero: si el PDF trae texto nativo, el OCR no hace falta.
  2. si no, pdftoppm a PNG y tesseract -l spa.
  3. se cronometra cada etapa para proyectar los 932 decretos con numeros, no con fe.
"""
import glob, os, re, subprocess, time
os.environ["PATH"] = "/workspace/ocrenv/bin:" + os.environ["PATH"]
TMP = "/workspace/ab-probe-20260903/ocr_tmp"
os.makedirs(TMP, exist_ok=True)

def corre(cmd, t=600):
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, timeout=t)
    return p.returncode, p.stdout, p.stderr, time.time() - t0

pdfs = sorted(glob.glob("/workspace/ab-probe-20260903/dd_pdf/*.pdf"))
print("PDFs del piloto:", len(pdfs))
print("tesseract:", subprocess.run(["tesseract", "--version"], capture_output=True).stdout.split()[1].decode())
print()
print("%-26s %8s %6s %8s %7s %s" % ("archivo", "bytes", "pags", "nativo", "seg", "via"))
res = []
for p in pdfs[:12]:
    b = os.path.getsize(p)
    # paginas
    rc, so, se, _ = corre(["pdfinfo", p])
    m = re.search(rb"Pages:\s+(\d+)", so)
    pags = int(m.group(1)) if m else 0
    # 1) texto nativo
    rc, so, se, t1 = corre(["pdftotext", "-layout", p, "-"])
    nativo = len(re.sub(rb"\s+", b" ", so).strip())
    if nativo > 400 * max(pags, 1):
        res.append({"p": p, "bytes": b, "pags": pags, "chars": nativo, "seg": t1, "via": "pdftotext"})
        print("%-26s %8d %6d %8d %7.1f %s" % (os.path.basename(p)[:26], b, pags, nativo, t1, "TEXTO NATIVO"))
        continue
    # 2) OCR
    base = os.path.join(TMP, "pg")
    for f in glob.glob(base + "*"):
        os.remove(f)
    rc, so, se, t2 = corre(["pdftoppm", "-r", "200", "-png", "-f", "1", "-l", "3", p, base], t=900)
    pngs = sorted(glob.glob(base + "*.png"))
    chars, t3 = 0, 0.0
    for g in pngs:
        rc, so, se, dt = corre(["tesseract", g, "stdout", "-l", "spa", "--psm", "4"], t=900)
        chars += len(re.sub(rb"\s+", b" ", so).strip())
        t3 += dt
    res.append({"p": p, "bytes": b, "pags": pags, "chars": chars, "seg": t1 + t2 + t3,
                "via": "ocr", "pgs_ocr": len(pngs), "seg_por_pag": (t2 + t3) / max(len(pngs), 1)})
    print("%-26s %8d %6d %8d %7.1f %s (%d pags, %.1f s/pag)" % (
        os.path.basename(p)[:26], b, pags, chars, t1 + t2 + t3, "OCR", len(pngs), (t2 + t3) / max(len(pngs), 1)))
print()
nat = [r for r in res if r["via"] == "pdftotext"]
ocr = [r for r in res if r["via"] == "ocr"]
print("texto nativo:", len(nat), "| OCR:", len(ocr))
if ocr:
    spp = sum(r["seg_por_pag"] for r in ocr) / len(ocr)
    pags_prom = sum(r["pags"] for r in ocr) / len(ocr)
    print("segundos por pagina de OCR: %.1f" % spp)
    print("paginas promedio por decreto escaneado: %.1f" % pags_prom)
    n_ocr = int(932 * len(ocr) / len(res))
    horas = n_ocr * pags_prom * spp / 3600
    print()
    print("== COSTO REAL con NUESTRO tesseract, 2 vCPU")
    print("   decretos que necesitarian OCR: ~%d de 932" % n_ocr)
    print("   horas de CPU en 1 hilo: %.0f" % horas)
    print("   con 2 hilos: %.0f horas" % (horas / 2))
    print("   COSTO EN DINERO: 0. El OCR es nuestro.")
    print("   COSTO EN CREDITOS de Abacus: 0 tambien, porque corre en brain-env, no en la VM.")
