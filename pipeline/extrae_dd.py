#!/usr/bin/env python3
"""FASE 1 · extraccion de texto de los decretos departamentales. Paralela, resumible.

NO toca la base. Cada documento deja /dd_txt/<id>.json con:
  {id, slug, numero, anio, sha256, via, pags, chars, texto}

Por que separado: el OCR es CPU pura y paralelizable; escribir en SQLite es transaccional
y va en un solo hilo. Mezclarlos hacia que la parte caras bloqueara la base 16 horas.

Medido antes de escribir esto: 90,9 s por decreto escaneado en un hilo. Con 2 procesos en
las 2 vCPU de brain-env baja a la mitad, y quitar el reintento ciego de psm 3 (solo se
reintenta si psm 4 devuelve casi nada) recorta otro tanto.
"""
import hashlib, json, multiprocessing as mp, os, re, subprocess, sys, time

os.environ["PATH"] = "/workspace/ocrenv/bin:" + os.environ["PATH"]
BASE = "/workspace/ab-probe-20260903"
PDFS = os.path.join(BASE, "dd_pdf")
TXT = os.path.join(BASE, "dd_txt")
CENSO = os.path.join(BASE, "censo_dd.json")
os.makedirs(PDFS, exist_ok=True)
os.makedirs(TXT, exist_ok=True)

NUM = [re.compile(r"decreto-departamental-n-(\d{1,4})(?:-a)?-(\d{4})"),
       re.compile(r"decreto-departamental-(\d{1,4})-(\d{4})"),
       re.compile(r"decreto-departamental-n-(\d{1,4})\b")]
ANEXO = re.compile(r"^anexo|anexo-\d|-anexo-")
largo = lambda s: len(re.sub(r"\s+", " ", s or "").strip())

def ident(slug):
    for p in NUM:
        m = p.search(slug)
        if m:
            g = m.groups()
            return (g[0].lstrip("0") or "0"), (g[1] if len(g) > 1 else None)
    return None, None

def corre(cmd, t=900):
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=t)
        return p.returncode, p.stdout
    except Exception:
        return -1, b""

def uno(v):
    """Un documento de punta a punta. Devuelve el dict del recibo."""
    t0 = time.time()
    dst = os.path.join(TXT, "%s.json" % v["id"])
    if os.path.exists(dst):
        return {"id": v["id"], "estado": "ya"}
    ruta = os.path.join(PDFS, "dd-%s-%s-%s.pdf" % (v["anio"] or "sa", (v["numero"] or "sn").zfill(3), v["id"]))
    if not (os.path.exists(ruta) and os.path.getsize(ruta) > 2000):
        corre(["curl", "-sL", "-A", "Mozilla/5.0", "--max-time", "180", v["url"], "-o", ruta])
    if not os.path.exists(ruta):
        return {"id": v["id"], "slug": v["slug"], "estado": "sin_descarga"}
    b = open(ruta, "rb").read()
    if b[:5] != b"%PDF-":
        return {"id": v["id"], "slug": v["slug"], "estado": "no_pdf", "bytes": len(b)}
    sha = hashlib.sha256(b).hexdigest()
    rc, out = corre(["pdfinfo", ruta])
    m = re.search(rb"Pages:\s+(\d+)", out or b"")
    pags = int(m.group(1)) if m else 1
    rc, out = corre(["pdftotext", "-layout", ruta, "-"])
    nat = (out or b"").decode("utf8", "replace")
    if largo(nat) >= 350 * max(pags, 1):
        txt, via = nat, "texto_nativo_pdf"
    else:
        tmp = os.path.join(BASE, "ocr_%d_%s" % (os.getpid(), v["id"]))
        os.makedirs(tmp, exist_ok=True)
        for f in os.listdir(tmp):
            try:
                os.remove(os.path.join(tmp, f))
            except OSError:
                pass
        corre(["pdftoppm", "-r", "200", "-png", ruta, os.path.join(tmp, "p")], t=1800)
        pngs = sorted(x for x in os.listdir(tmp) if x.endswith(".png"))
        partes = []
        for g in pngs:
            rc, o = corre(["tesseract", os.path.join(tmp, g), "stdout", "-l", "spa", "--psm", "4"], t=900)
            partes.append((o or b"").decode("utf8", "replace"))
        ocr = "\n".join(partes)
        # el reintento con psm 3 solo si psm 4 devolvio casi nada: reintentar siempre
        # duplicaba el costo de toda la corrida por un caso de cada veinte.
        if largo(ocr) < 200 and pngs:
            partes = []
            for g in pngs:
                rc, o = corre(["tesseract", os.path.join(tmp, g), "stdout", "-l", "spa", "--psm", "3"], t=900)
                partes.append((o or b"").decode("utf8", "replace"))
            if largo("\n".join(partes)) > largo(ocr):
                ocr = "\n".join(partes)
        for f in os.listdir(tmp):
            try:
                os.remove(os.path.join(tmp, f))
            except OSError:
                pass
        try:
            os.rmdir(tmp)
        except OSError:
            pass
        if largo(ocr) < largo(nat):
            txt, via = nat, "texto_nativo_pdf"
        else:
            txt, via, pags = ocr, "ocr_pdf_escaneado", (len(pngs) or pags)
    rec = {"id": v["id"], "slug": v["slug"], "numero": v["numero"], "anio": v["anio"],
           "anexo": v["anexo"], "url": v["url"], "sha256": sha, "via": via, "pags": pags,
           "chars": largo(txt), "seg": round(time.time() - t0, 1),
           "estado": "ok" if largo(txt) >= 200 else "texto_insuficiente"}
    if rec["estado"] == "ok":
        d = dict(rec)
        d["texto"] = txt
        tmpf = dst + ".parcial"
        with open(tmpf, "w", encoding="utf8") as f:
            json.dump(d, f, ensure_ascii=False)
        os.replace(tmpf, dst)   # atomico: un corte no deja un json a medias
    return rec

def main(workers, limite):
    reg = [v for v in json.load(open(CENSO)) if "decreto-departamental" in v["slug"]]
    trabajo, vistos = [], set()
    for v in reg:
        n, a = ident(v["slug"])
        if not n:
            continue
        es_anexo = bool(ANEXO.search(v["slug"]))
        k = (n, a, es_anexo, v["id"])
        if k in vistos:
            continue
        vistos.add(k)
        v["numero"], v["anio"], v["anexo"] = n, a, es_anexo
        trabajo.append(v)
    hechos = {f[:-5] for f in os.listdir(TXT) if f.endswith(".json")}
    pend = [v for v in trabajo if v["id"] not in hechos]
    print("decretos totales:", len(trabajo), "| ya extraidos:", len(hechos), "| pendientes:", len(pend), flush=True)
    if limite:
        pend = pend[:limite]
    log = open(os.path.join(BASE, "extrae_dd.jsonl"), "a")
    t0 = time.time()
    ok = pobres = fallos = 0
    with mp.Pool(workers) as pool:
        for i, rec in enumerate(pool.imap_unordered(uno, pend, chunksize=1), 1):
            log.write(json.dumps(rec, ensure_ascii=False) + "\n"); log.flush()
            if rec["estado"] == "ok":
                ok += 1
            elif rec["estado"] == "texto_insuficiente":
                pobres += 1
            elif rec["estado"] != "ya":
                fallos += 1
            if i % 20 == 0 or i <= 4:
                el = time.time() - t0
                resta = (len(pend) - i) * el / max(i, 1) / 60
                print("  [%4d/%d] ok=%d pobres=%d fallos=%d | %.1f doc/min | faltan ~%.0f min" %
                      (i, len(pend), ok, pobres, fallos, 60 * i / max(el, 1), resta), flush=True)
    log.close()
    print(flush=True)
    print("EXTRAIDOS ok:", ok, "| texto pobre:", pobres, "| fallos:", fallos,
          "| minutos:", round((time.time() - t0) / 60, 1), flush=True)

if __name__ == "__main__":
    w, lim = 2, None
    for a in sys.argv[1:]:
        if a.startswith("--workers="):
            w = int(a.split("=")[1])
        if a.startswith("--limite="):
            lim = int(a.split("=")[1])
    main(w, lim)
