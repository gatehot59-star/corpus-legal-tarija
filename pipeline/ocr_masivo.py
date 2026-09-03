"""OCR de los 784 documentos escaneados, shardeado para correr en paralelo en Actions.

Decisiones de arquitectura, con su motivo medido:

1. **No se commitean los PDFs.** Cada shard RE-DESCARGA desde la fuente oficial usando la
   `fuente_url` del manifiesto y **verifica el sha256** que ya se midio el 2026-09-02. Si
   el hash no coincide, el documento se marca `HASH_DISTINTO` y NO se OCRea: un PDF que
   cambio en el servidor es una noticia, no un archivo a procesar en silencio.
2. **Un shard por job, 20 jobs.** Medido en la corrida real: **5,08 s/pagina** en Actions
   x64, o sea 2.624 paginas son 3,7 h de CPU y ~11 min de reloj shardeado. (La estimacion
   previa de 11,1 s/pagina venia del A/B con dos PSM y salio pesimista por mas del doble.)
   El taller, a 51,3 s/pagina, tardaria 37 h; por eso esto no corre ahi.
3. **El conteo de paginas se toma de `pdfinfo`, no de pdfplumber.** Medido: los 19
   documentos que figuraban con 0 paginas son PDFs SANOS que `pdfinfo` abre y cuenta
   (1-2 paginas cada uno). El cero era del lector, no del archivo.
4. **Los nombres de archivo se normalizan con `stem_seguro()`.** Esto no es prolijidad: 18
   de 20 shards murieron subiendo su artefacto porque 41 documentos no traen `numero` y el
   codigo escribia "?" literal, que upload-artifact rechaza. El OCR estaba bien; el nombre, no.
5. **Cada shard escribe su propio JSONL y su propio directorio de texto.** Nada de un
   manifiesto compartido entre 20 jobs concurrentes: se consolidan despues.
6. **El gate de calidad corre por documento y su veredicto queda en el registro.** Es
   `gate_v2`: el v1 media densidad de lexico legal y rechazaba leyes sustantivas con OCR
   perfecto, incluida la Ley 007 que tiene 38/40 datos juridicos verificados.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

import gate_v2
import normalizar_citas as nc

UA = "Mozilla/5.0 (corpus-legal-tarija; OCR masivo; +https://github.com/gatehot59-star)"


def stem_seguro(fuente_id, numero, sha_prefijo: str) -> str:
    """Nombre de archivo que sobrevive a upload-artifact, a Windows y al glob del consolidador.

    Escrito despues de que 18 de 20 shards fallaran al subir su artefacto: 41 de los 784
    documentos no traen `numero` y el codigo escribia "?" literal, que upload-artifact v4
    rechaza junto con * : " < > | y la barra.
    """
    def limpiar(valor, respaldo):
        s = str(valor or "").strip()
        s = unicodedata.normalize("NFD", s)
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        s = re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_.-")
        return s or respaldo

    return limpiar(fuente_id, "sin-fuente") + "-" + limpiar(numero, "sin-numero") + "-" + sha_prefijo


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def bajar(url: str, intentos: int = 3) -> bytes:
    ultimo = None
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            ultimo = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"descarga fallida tras {intentos} intentos: {ultimo}")


def contar_paginas(pdf: Path, pdfinfo: str) -> int:
    """pdfinfo, no pdfplumber: medido que pdfplumber devuelve 0 en PDFs sanos."""
    cp = subprocess.run([pdfinfo, str(pdf)], capture_output=True, text=True)
    if cp.returncode != 0:
        return 0
    for linea in cp.stdout.splitlines():
        if linea.startswith("Pages:"):
            try:
                return int(linea.split(":", 1)[1].strip())
            except ValueError:
                return 0
    return 0


def procesar(doc: dict, tmp: Path, salida_txt: Path, args) -> dict:
    """Un documento de punta a punta. Nunca lanza: devuelve el registro con su estado."""
    num = doc.get("numero") or ""
    reg = {"numero": num or "(sin numero)", "fuente_id": doc.get("fuente_id"),
           "md5": doc.get("md5"), "sha256_esperado": doc.get("sha256"),
           "titulo": (doc.get("titulo") or "")[:180],
           "confidencialidad": doc.get("confidencialidad"), "estado": "", "motivo": "",
           "maquina": args.maquina, "instrumento": f"tesseract {args.lang} psm {args.psm}"}

    # Guarda de privacidad: nada PRIVADO sale a una etapa con red ni a un repo publico.
    if str(doc.get("confidencialidad", "")).upper() != "PUBLICO":
        reg.update(estado="OMITIDO_PRIVADO",
                   motivo="confidencialidad != PUBLICO: no se descarga ni se publica")
        return reg

    url = doc.get("fuente_url") or ""
    if not url:
        reg.update(estado="SIN_URL", motivo="el manifiesto no tiene fuente_url")
        return reg

    try:
        crudo = bajar(url)
    except Exception as e:
        reg.update(estado="DESCARGA_FALLIDA", motivo=str(e)[:250])
        return reg

    real = sha256_bytes(crudo)
    reg["sha256_real"] = real
    reg["bytes"] = len(crudo)
    esperado = doc.get("sha256") or ""
    if esperado and not esperado.startswith(real[:12]) and real != esperado:
        reg.update(estado="HASH_DISTINTO",
                   motivo=f"el servidor devolvio otro archivo: esperado {esperado[:12]} real {real[:12]}")
        return reg

    stem = stem_seguro(doc.get("fuente_id"), num, real[:8])
    pdf = tmp / (stem + ".pdf")
    pdf.write_bytes(crudo)
    paginas = contar_paginas(pdf, args.pdfinfo)
    reg["paginas"] = paginas
    if paginas < 1:
        reg.update(estado="PDF_ILEGIBLE", motivo="pdfinfo no pudo contar paginas")
        return reg
    if paginas > args.max_paginas:
        reg.update(estado="DEMASIADAS_PAGINAS",
                   motivo=f"{paginas} > tope {args.max_paginas}: va a una tanda aparte")
        return reg

    t0 = time.time()
    base = tmp / ("img-" + stem)
    cp = subprocess.run([args.pdftoppm, "-r", str(args.dpi), "-gray", "-png",
                         str(pdf), str(base)], capture_output=True, text=True)
    if cp.returncode != 0:
        reg.update(estado="RASTERIZADO_FALLIDO", motivo=cp.stderr.strip()[:250])
        return reg

    pngs = sorted(base.parent.glob(base.name + "-*.png"))
    textos, exits = [], []
    for png in pngs:
        cp = subprocess.run([args.tesseract, str(png), str(png.with_suffix("")),
                             "-l", args.lang, "--psm", str(args.psm)],
                            capture_output=True, text=True)
        exits.append(cp.returncode)
        t = png.with_suffix(".txt")
        textos.append(t.read_text(encoding="utf-8", errors="replace") if t.exists() else "")
        png.unlink(missing_ok=True)

    segundos = time.time() - t0
    texto = "\n\f\n".join(textos)
    g = gate_v2.evaluar(textos)
    citas = nc.extraer(texto, documento=stem)

    salida_txt.mkdir(parents=True, exist_ok=True)
    (salida_txt / (stem + ".txt")).write_text(texto, encoding="utf-8")
    (salida_txt / (stem + ".indice.txt")).write_text(citas["texto_indice"], encoding="utf-8")

    reg.update(estado="OK" if g["veredicto"] == "APTO" else "REVISION_HUMANA",
               motivo="" if g["veredicto"] == "APTO" else g["motivo"],
               chars=len(texto), segundos=round(segundos, 1),
               seg_por_pagina=round(segundos / max(paginas, 1), 1),
               exits_tesseract=exits, gate=g,
               citas=citas["total_citas"], citas_a_revisar=citas["total_revision"],
               revision_citas=citas["revision_humana"], archivo_texto=stem + ".txt")
    return reg


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifiesto", required=True)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--salida", default="salida-masivo")
    ap.add_argument("--limite", type=int, default=0, help="0 = sin limite; para validar")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--psm", type=int, default=3)
    ap.add_argument("--lang", default="spa")
    ap.add_argument("--max-paginas", type=int, default=120)
    ap.add_argument("--tesseract", default="tesseract")
    ap.add_argument("--pdftoppm", default="pdftoppm")
    ap.add_argument("--pdfinfo", default="pdfinfo")
    ap.add_argument("--maquina", default="actions-x64")
    args = ap.parse_args()

    pendientes = []
    for linea in Path(args.manifiesto).read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        d = json.loads(linea)
        if d.get("etapas", {}).get("extraer", {}).get("estado") == "OCR_REQUERIDO":
            pendientes.append(d)

    # Reparto estable: el indice manda, asi que un re-run del shard 3 procesa lo mismo.
    mios = [d for i, d in enumerate(pendientes) if i % args.shards == args.shard]
    if args.limite:
        mios = mios[:args.limite]

    print(f"shard {args.shard}/{args.shards}: {len(mios)} de {len(pendientes)} pendientes", flush=True)

    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    jsonl = salida / f"shard-{args.shard:02d}.jsonl"
    registros = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for i, doc in enumerate(mios, start=1):
            reg = procesar(doc, tmp, salida / "texto", args)
            registros.append(reg)
            print(f"  [{i}/{len(mios)}] {reg['numero']}: {reg['estado']}"
                  + (f" ({reg.get('paginas')}p, {reg.get('segundos')}s)" if reg.get("segundos") else "")
                  + (f" -> {reg['motivo'][:90]}" if reg["motivo"] else ""), flush=True)
            with jsonl.open("a", encoding="utf-8") as f:
                f.write(json.dumps(reg, ensure_ascii=False) + "\n")

    conteo = {}
    for r in registros:
        conteo[r["estado"]] = conteo.get(r["estado"], 0) + 1
    resumen = {
        "shard": args.shard, "shards": args.shards, "docs": len(registros),
        "estados": conteo,
        "paginas_ocr": sum(r.get("paginas", 0) for r in registros if r["estado"] in ("OK", "REVISION_HUMANA")),
        "segundos": round(sum(r.get("segundos", 0) for r in registros), 1),
        "citas_a_revisar": sum(r.get("citas_a_revisar", 0) for r in registros),
    }
    (salida / f"resumen-{args.shard:02d}.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nRESUMEN:", json.dumps(resumen, ensure_ascii=False), flush=True)

    # Solo un fallo de infraestructura tira el job. Un documento raro es un estado, no un error.
    duros = conteo.get("DESCARGA_FALLIDA", 0) + conteo.get("RASTERIZADO_FALLIDO", 0)
    if duros and duros == len(registros):
        print("ROJO: fallaron TODOS los documentos del shard", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
