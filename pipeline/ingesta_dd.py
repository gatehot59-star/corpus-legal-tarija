#!/usr/bin/env python3
"""PRODUCCION · ingesta de los decretos departamentales de Tarija.

Trabaja sobre una COPIA (bolivia-v8.db). La base en servicio no se toca hasta que los
guards pasen. Resumible: si se corta, arranca donde quedo mirando los uid ya presentes.

Por documento:
  1. descarga (cache en disco, no se vuelve a bajar lo que ya esta)
  2. pdftotext -layout; si el texto es pobre, OCR con pdftoppm 200dpi + tesseract -l spa
  3. chunks de 1800 con 200 de solape, cortados en frontera de parrafo (convencion medida)
  4. inserta en documentos + chunks con sha256 del PDF, URL de origen y via_texto

via_texto: 'texto_nativo_pdf' o 'ocr_pdf_escaneado'. Nunca se marca oficial un OCR.
Cada documento deja una linea en el JSONL: es el recibo, y permite recomputar todo.
"""
import hashlib, json, os, re, shutil, sqlite3, subprocess, sys, time, unicodedata

os.environ["PATH"] = "/workspace/ocrenv/bin:" + os.environ["PATH"]
BASE = "/workspace/ab-probe-20260903"
ORIG = "/workspace/bolivia-v7.db"
DEST = "/workspace/bolivia-v8.db"
PDFS = os.path.join(BASE, "dd_pdf")
TMP = os.path.join(BASE, "ocr_run")
LOG = os.path.join(BASE, "ingesta_dd.jsonl")
CENSO = os.path.join(BASE, "censo_dd.json")
MAXC, SOLAPE = 1800, 200
FUENTE = "tarija_gaceta"
os.makedirs(PDFS, exist_ok=True); os.makedirs(TMP, exist_ok=True)

NUM = [re.compile(r"decreto-departamental-n-(\d{1,4})(?:-a)?-(\d{4})"),
       re.compile(r"decreto-departamental-(\d{1,4})-(\d{4})"),
       re.compile(r"decreto-departamental-n-(\d{1,4})\b")]
ANEXO = re.compile(r"^anexo|anexo-\d|-anexo-")
CITA = re.compile(r"[Aa]rt[íi]?c?u?l?o?s?\.?\s*(\d+[\w.\u00ba\u00b0]*)")

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

def baja(url, destino):
    if os.path.exists(destino) and os.path.getsize(destino) > 2000:
        return open(destino, "rb").read(), "cache"
    rc, out = corre(["curl", "-sL", "-A", "Mozilla/5.0", "--max-time", "180", url, "-o", destino])
    if rc != 0 or not os.path.exists(destino):
        return None, "error"
    b = open(destino, "rb").read()
    if b[:5] != b"%PDF-":
        return None, "no_pdf"
    return b, "descargado"

def texto_de(ruta, pdf_bytes):
    """pdftotext primero. El umbral es por pagina: un PDF de 8 paginas con 300 caracteres
    es un escaneo con un sello, no un texto."""
    rc, out = corre(["pdfinfo", ruta])
    m = re.search(rb"Pages:\s+(\d+)", out or b"")
    pags = int(m.group(1)) if m else 1
    rc, out = corre(["pdftotext", "-layout", ruta, "-"])
    nat = (out or b"").decode("utf8", "replace")
    if len(re.sub(r"\s+", " ", nat).strip()) >= 350 * max(pags, 1):
        return nat, "texto_nativo_pdf", pags
    for f in os.listdir(TMP):
        os.remove(os.path.join(TMP, f))
    base = os.path.join(TMP, "p")
    corre(["pdftoppm", "-r", "200", "-png", ruta, base], t=1800)
    partes = []
    for g in sorted(os.listdir(TMP)):
        rc, out = corre(["tesseract", os.path.join(TMP, g), "stdout", "-l", "spa", "--psm", "4"], t=900)
        partes.append((out or b"").decode("utf8", "replace"))
    ocr = "\n".join(partes)
    # si el OCR sale peor que el texto nativo, gana el nativo: no se degrada un documento
    if len(re.sub(r"\s+", " ", ocr).strip()) < len(re.sub(r"\s+", " ", nat).strip()):
        return nat, "texto_nativo_pdf", pags
    return ocr, "ocr_pdf_escaneado", pags

def trozos(txt):
    """1800 con 200 de solape, cortando en frontera de parrafo o de frase."""
    t = re.sub(r"\r\n?", "\n", txt).strip()
    out, i = [], 0
    while i < len(t):
        fin = min(i + MAXC, len(t))
        if fin < len(t):
            for sep in ("\n\n", "\n", ". ", " "):
                j = t.rfind(sep, i + MAXC // 2, fin)
                if j > 0:
                    fin = j + len(sep)
                    break
        out.append(t[i:fin])
        if fin >= len(t):
            break
        i = max(fin - SOLAPE, i + 1)
    return [x for x in out if x.strip()]

def titulo_de(slug, numero, anio):
    """El slug ES el titulo oficial abreviado que publica la Gaceta. Se limpia el prefijo
    de identificacion, que ya vive en tipo_norma/numero/anio."""
    s = slug
    for p in NUM:
        s = p.sub("", s, count=1)
    s = re.sub(r"^-+|-+$", "", s).replace("-", " ").strip()
    return (s[:1].upper() + s[1:]) if s else ""

def main(limite=None):
    if not os.path.exists(DEST):
        print("copiando la base a", DEST, flush=True)
        shutil.copy2(ORIG, DEST)
    con = sqlite3.connect(DEST)
    con.row_factory = sqlite3.Row
    ya = {r[0] for r in con.execute("SELECT uid FROM documentos WHERE tipo_norma='Decreto Departamental'")}
    maxdoc = con.execute("SELECT coalesce(max(doc_id),0) FROM documentos").fetchone()[0]
    print("decretos ya ingestados:", len(ya), "| doc_id maximo:", maxdoc, flush=True)
    reg = [v for v in json.load(open(CENSO)) if "decreto-departamental" in v["slug"]]
    trabajo = []
    vistos = set()
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
    print("decretos a procesar:", len(trabajo), flush=True)
    if limite:
        trabajo = trabajo[:limite]
    log = open(LOG, "a")
    hechos = fallos = 0
    t0 = time.time()
    for k, v in enumerate(trabajo, 1):
        ruta = os.path.join(PDFS, "dd-%s-%s-%s.pdf" % (v["anio"] or "sa", (v["numero"] or "sn").zfill(3), v["id"]))
        b, via_bajada = baja(v["url"], ruta)
        if b is None:
            fallos += 1
            log.write(json.dumps({"id": v["id"], "slug": v["slug"], "estado": via_bajada}) + "\n"); log.flush()
            print("  [%4d/%d] DD %-5s %-5s FALLO %s" % (k, len(trabajo), v["numero"], v["anio"], via_bajada), flush=True)
            continue
        sha = hashlib.sha256(b).hexdigest()
        uid = "dep-tar-decreto-dept-%s-%s-%s" % ((v["numero"] or "sn").zfill(3), v["anio"] or "sa", sha[:8])
        if uid in ya:
            continue
        ti = time.time()
        txt, via, pags = texto_de(ruta, b)
        txt = unicodedata.normalize("NFC", txt)
        limpio = re.sub(r"\s+", " ", txt).strip()
        if len(limpio) < 200:
            fallos += 1
            log.write(json.dumps({"id": v["id"], "slug": v["slug"], "estado": "texto_insuficiente",
                                  "chars": len(limpio), "via": via}) + "\n"); log.flush()
            print("  [%4d/%d] DD %-5s %-5s TEXTO POBRE (%d car, %s)" % (k, len(trabajo), v["numero"], v["anio"], len(limpio), via), flush=True)
            continue
        ch = trozos(txt)
        maxdoc += 1
        titulo = titulo_de(v["slug"], v["numero"], v["anio"])
        con.execute("INSERT INTO documentos (doc_id,uid,fuente_id,jurisdiccion,departamento,organo,"
                    "tipo_norma,numero,anio,fecha,titulo,materia,sala,magistrado,partes,vigente,"
                    "derogada_por,fuente_url,sha256,via_texto,confianza,chars,archivo) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (maxdoc, uid, FUENTE, "departamental", "Tarija",
                     "Organo Ejecutivo del Gobierno Autonomo Departamental de Tarija",
                     "Decreto Departamental", v["numero"], v["anio"] or "", "", titulo, "", "", "", "",
                     None, "", v["url"], sha, via,
                     "alta" if via == "texto_nativo_pdf" else "media", len(txt), os.path.basename(ruta)))
        for i, cu in enumerate(ch, 1):
            enc = ""
            if i == 1:
                enc = "%s | Decreto Departamental | %s" % (v["numero"], titulo[:180])
            citas = " ".join(sorted(set("Art. " + m.group(1) for m in CITA.finditer(cu)))[:14])
            con.execute("INSERT INTO chunks (cuerpo,citas,encabezado,uid,doc_id,nro) VALUES (?,?,?,?,?,?)",
                        (cu, citas, enc, uid, maxdoc, str(i)))
        con.commit()
        ya.add(uid)
        hechos += 1
        dt = time.time() - ti
        log.write(json.dumps({"id": v["id"], "uid": uid, "numero": v["numero"], "anio": v["anio"],
                              "sha256": sha, "via": via, "pags": pags, "chars": len(txt),
                              "chunks": len(ch), "seg": round(dt, 1), "bajada": via_bajada,
                              "anexo": v["anexo"], "estado": "ok"}) + "\n"); log.flush()
        if hechos % 10 == 0 or k <= 5:
            resta = (len(trabajo) - k) * (time.time() - t0) / max(k, 1) / 60
            print("  [%4d/%d] DD %-5s %-5s %-18s %6d car %3d ch %5.1fs | faltan ~%.0f min" %
                  (k, len(trabajo), v["numero"], v["anio"], via, len(txt), len(ch), dt, resta), flush=True)
    log.close()
    print(flush=True)
    print("INGESTADOS:", hechos, "| FALLOS:", fallos, "| minutos:", round((time.time() - t0) / 60, 1), flush=True)
    q = lambda s: con.execute(s).fetchone()[0]
    print("base v8: documentos", q("SELECT count(*) FROM documentos"), "| chunks", q("SELECT count(*) FROM chunks"), flush=True)
    print("decretos departamentales:", q("SELECT count(*) FROM documentos WHERE tipo_norma='Decreto Departamental'"), flush=True)
    print("  por via:", flush=True)
    for r in con.execute("SELECT via_texto,count(*) n FROM documentos WHERE tipo_norma='Decreto Departamental' GROUP BY 1"):
        print("    %-20s %4d" % (r[0], r[1]), flush=True)
    con.close()

if __name__ == "__main__":
    lim = None
    for a in sys.argv[1:]:
        if a.startswith("--limite="):
            lim = int(a.split("=")[1])
    main(lim)
