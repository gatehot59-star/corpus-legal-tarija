"""Baja la jurisprudencia del Tribunal Supremo filtrada por departamento, desde GENESIS.

Medido el 2026-09-03 antes de escribir esto:
  - `apigenesis.tsj.bo/api/v1` responde 200 con la credencial del SPA publico del TSJ, 401 sin ella.
  - `GET /resoluciones/{id}/pdf` sigue ROTO (500 de Puppeteer del TSJ). NO se usa.
  - El detalle trae `url_pdf_escaneado` en otro host (`apigestortsj.organojudicial.gob.bo`), y
    ese PDF baja **200 sin credencial**. Esa es la via.
  - Hay **TRES** tipos de resolucion: Auto Supremo (1), Sentencia (2), Resolucion (3). La
    primera corrida uso solo el 1 sin preguntar, asi que bajo un tercio del universo creyendo
    que era todo.
  - De 2.664 resoluciones reales: 2.539 por HTML oficial, 120 con texto nativo en el PDF, y
    solo **5 necesitaron OCR**. Total: 312,8 s de OCR para once gestiones.

**Por que hay timeout y tope de paginas, con el caso medido:** la gestion 2025 colgo un job de
Actions por casi dos horas. Yo primero "refute" la hipotesis del PDF gigante mirando las
paginas de los documentos que YA habian terminado, que es sesgo de supervivencia: el que cuelga
no esta en esa muestra. Reproducido en brain-env, el culpable era el documento 48 de 198: un
PDF de 1.977.159 bytes, 22 paginas y **cero texto nativo**, OCReandose pagina por pagina. No
hacia falta un monstruo de cientos de paginas; alcanzan varios de veinte en serie.

Tres decisiones de diseno con su motivo:

1. **El HTML gana sobre el PDF cuando existe.** Es el texto oficial tal cual lo emitio el TSJ,
   sin un OCR en el medio. Preferir el escaneo cuando hay texto limpio es agregar error gratis.
2. **Se guarda el JSON crudo de cada resolucion, siempre.** Los metadatos (magistrado, materia,
   demandante, forma de resolucion) son la mitad del valor para un estudio, y sobreviven aunque
   el texto falle.
3. **El PDF no se commitea.** Se guarda su URL y su sha256; el texto es el producto.
"""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://apigenesis.tsj.bo/api/v1"
# Credencial del SPA publico del TSJ. Viaja en claro en su propio bundle; no fue entregada,
# fue encontrada. Se centraliza aca para que sea una linea a cambiar si el estudio consigue
# acceso formal.
CRED = {"username": "buscadorgenesis",
        "apikey": "CiAYFxnN4GwYgtDv+0jo8MSm1VuTZ53ah8aJ2L8GkgI="}
H = dict(CRED, **{"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})


def pedir(url, cuerpo=None, headers=None, intentos=3):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    ultimo = None
    for i in range(intentos):
        req = urllib.request.Request(url, data=datos,
                                     headers=headers if headers is not None else H,
                                     method="POST" if cuerpo is not None else "GET")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()[:400]
        except Exception as e:
            ultimo = e
            time.sleep(2 * (i + 1))
    return "ERR", str(ultimo)[:200].encode()


def lista(b):
    d = json.loads(b)
    if isinstance(d, list):
        return d
    return d.get("data", []) if isinstance(d, dict) else []


def uno(b):
    d = json.loads(b)
    d = d.get("data", d) if isinstance(d, dict) else d
    return d[0] if isinstance(d, list) and d else d


def plano_html(html: str) -> str:
    """Saca el texto de un HTML del TSJ sin traer una dependencia: son divs y <p>, no una web."""
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</(p|div|tr|h[1-6])>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = (s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<")
          .replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'"))
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def stem_seguro(*partes) -> str:
    fuera = []
    for p in partes:
        s = unicodedata.normalize("NFD", str(p or ""))
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        s = re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_.-")
        fuera.append(s or "x")
    return "-".join(fuera)


def ocr_pdf(datos: bytes, args) -> tuple:
    """Extrae texto del PDF. Devuelve (texto, paginas, segundos, motivo).

    El timeout NO es prolijidad: un solo documento escaneado de 22 paginas colgo un job de
    Actions casi dos horas, con 198 documentos en serie detras esperandolo.
    """
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        pdf = tmp / "r.pdf"
        pdf.write_bytes(datos)
        cp = subprocess.run([args.pdfinfo, str(pdf)], capture_output=True, text=True)
        pags = 0
        for l in cp.stdout.splitlines():
            if l.startswith("Pages:"):
                pags = int(l.split(":", 1)[1].strip() or 0)
        # Primero la capa nativa: si el PDF ya trae texto, OCRearlo es tirar plata.
        # Medido: 120 de 2.664 la tenian, y esas salieron en 0,0 s.
        cp = subprocess.run([args.pdftotext, str(pdf), "-"], capture_output=True, text=True)
        if len(cp.stdout.strip()) > 200 * max(pags, 1):
            return cp.stdout, pags, 0.0, ""
        if pags > args.max_paginas:
            return "", pags, 0.0, "tope de paginas: " + str(pags) + " > " + str(args.max_paginas)
        t0 = time.time()
        try:
            subprocess.run([args.pdftoppm, "-r", str(args.dpi), "-gray", "-png",
                            str(pdf), str(tmp / "p")], capture_output=True, text=True,
                           timeout=args.timeout_doc)
            textos = []
            for png in sorted(tmp.glob("p-*.png"), key=lambda p: int(p.stem.split("-")[-1])):
                restante = args.timeout_doc - (time.time() - t0)
                if restante <= 5:
                    return ("\n\f\n".join(textos), pags, round(time.time() - t0, 1),
                            "timeout de " + str(args.timeout_doc) + " s en la pagina " + png.stem)
                subprocess.run([args.tesseract, str(png), str(png.with_suffix("")),
                                "-l", args.lang, "--psm", str(args.psm)],
                               capture_output=True, text=True, timeout=restante)
                t = png.with_suffix(".txt")
                textos.append(t.read_text(encoding="utf-8", errors="replace") if t.exists() else "")
        except subprocess.TimeoutExpired:
            return "", pags, round(time.time() - t0, 1), "timeout de " + str(args.timeout_doc) + " s"
        return "\n\f\n".join(textos), pags, round(time.time() - t0, 1), ""


def procesar(meta: dict, salida: Path, args) -> dict:
    rid = meta.get("id")
    reg = {"id": rid, "nro_resolucion": meta.get("nro_resolucion"),
           "fecha_emision": meta.get("fecha_emision"),
           "departamento": meta.get("departamento"), "sala": meta.get("sala"),
           "gestion": args.gestion, "jurisdiccion": "nacional_tsj",
           "tipo_norma": meta.get("tipo_resolucion") or meta.get("_tipo_nombre") or "?",
           "confidencialidad": "PUBLICO", "estado": "", "motivo": "", "via": ""}

    s, b = pedir(BASE + "/resoluciones/" + str(rid))
    if s != 200:
        reg.update(estado="DETALLE_FALLIDO", motivo="HTTP " + str(s))
        return reg
    d = uno(b)
    for k in ("demandante", "demandado", "magistrado", "materia", "procesos",
              "formas_resoluciones", "nro_expediente", "subtipo_resolucion"):
        reg[k] = d.get(k)
    reg["url_pdf_escaneado"] = d.get("url_pdf_escaneado") or ""

    stem = stem_seguro("tsj", meta.get("departamento"), args.gestion,
                       meta.get("nro_resolucion"), rid)
    (salida / "meta").mkdir(parents=True, exist_ok=True)
    (salida / "meta" / (stem + ".json")).write_text(
        json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

    # Via 1: el HTML oficial, cuando trae cuerpo. Es el texto del TSJ sin OCR en el medio.
    texto = plano_html(d.get("contenido") or "")
    if len(texto) > 500:
        reg.update(estado="OK", via="html_oficial", chars=len(texto), paginas=None, segundos=0.0)
    else:
        url = reg["url_pdf_escaneado"]
        if not url:
            reg.update(estado="SIN_TEXTO_NI_PDF",
                       motivo="contenido HTML vacio y sin url_pdf_escaneado")
            return reg
        # El PDF escaneado NO pide credencial: se pide sin ella a proposito.
        s2, b2 = pedir(url, headers={"User-Agent": "Mozilla/5.0"})
        if s2 != 200 or b2[:4] != b"%PDF":
            reg.update(estado="PDF_FALLIDO", motivo="HTTP " + str(s2) + " " + repr(b2[:60]))
            return reg
        reg["sha256_pdf"] = hashlib.sha256(b2).hexdigest()
        reg["bytes_pdf"] = len(b2)
        texto, pags, seg, motivo = ocr_pdf(b2, args)
        reg.update(paginas=pags, segundos=seg, chars=len(texto),
                   via="ocr_pdf_escaneado" if seg else "texto_nativo_pdf")
        if motivo:
            reg.update(estado="TIMEOUT_OCR" if "timeout" in motivo else "DEMASIADAS_PAGINAS",
                       motivo=motivo)
            if not texto:
                return reg
        else:
            reg["estado"] = "OK" if len(texto) > 500 else "REVISION_HUMANA"
            if reg["estado"] != "OK":
                reg["motivo"] = "el texto extraido tiene " + str(len(texto)) + " chars"

    (salida / "texto").mkdir(parents=True, exist_ok=True)
    (salida / "texto" / (stem + ".txt")).write_text(texto, encoding="utf-8")
    reg["archivo_texto"] = stem + ".txt"
    return reg


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--departamento", default="Tarija")
    ap.add_argument("--gestion", type=int, default=2026)
    ap.add_argument("--tipos", default="1,2,3",
                    help="ids de tipo de resolucion; 1=Auto Supremo 2=Sentencia 3=Resolucion")
    ap.add_argument("--salida", default="salida-genesis")
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--psm", type=int, default=3)
    ap.add_argument("--lang", default="spa")
    ap.add_argument("--max-paginas", type=int, default=150)
    ap.add_argument("--timeout-doc", type=int, default=900,
                    help="segundos maximos de extraccion por documento")
    ap.add_argument("--tesseract", default="tesseract")
    ap.add_argument("--pdftoppm", default="pdftoppm")
    ap.add_argument("--pdfinfo", default="pdfinfo")
    ap.add_argument("--pdftotext", default="pdftotext")
    args = ap.parse_args()

    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)

    s, b = pedir(BASE + "/catalogos/salas")
    if s != 200:
        print("ROJO: /catalogos/salas dio", s, b[:120])
        return 2
    salas = lista(b)
    s, b = pedir(BASE + "/catalogos/tipos_resoluciones")
    catalogo_tipos = {t["id"]: t["nombre"] for t in (lista(b) if s == 200 else [])}
    tipos = [int(x) for x in args.tipos.split(",") if x.strip()]
    print("salas: " + str(len(salas)) + " | tipos: "
          + ", ".join(str(t) + "=" + catalogo_tipos.get(t, "?") for t in tipos), flush=True)

    objetivo = args.departamento.upper()
    pendientes = []
    for tipo in tipos:
        for sala in salas:
            s2, b2 = pedir(BASE + "/resoluciones/busqueda_por_gestion",
                           {"idSala": sala["id"], "gestion": args.gestion, "idTipoRes": tipo})
            if s2 != 200:
                print("  " + str(sala["nombre"]) + " tipo " + str(tipo) + ": HTTP " + str(s2), flush=True)
                continue
            mios = [dict(f, sala=sala["nombre"], _tipo_nombre=catalogo_tipos.get(tipo, "?"))
                    for f in lista(b2)
                    if str(f.get("departamento") or "").upper().startswith(objetivo)]
            pendientes += mios

    # Reparto estable por id: un re-run del shard 3 procesa exactamente lo mismo.
    pendientes.sort(key=lambda f: f["id"])
    mios = [d for i, d in enumerate(pendientes) if i % args.shards == args.shard]
    if args.limite:
        mios = mios[:args.limite]
    print("total " + args.departamento + " gestion " + str(args.gestion) + ": "
          + str(len(pendientes)) + " | shard " + str(args.shard) + "/" + str(args.shards)
          + ": " + str(len(mios)), flush=True)

    jsonl = salida / ("resoluciones-%s-%02d.jsonl" % (args.gestion, args.shard))
    registros = []
    for i, meta in enumerate(mios, start=1):
        reg = procesar(meta, salida, args)
        registros.append(reg)
        print("  [" + str(i) + "/" + str(len(mios)) + "] " + str(reg["nro_resolucion"])
              + ": " + reg["estado"] + " via " + (reg["via"] or "-")
              + " " + str(reg.get("chars", 0)) + "ch"
              + (" " + str(reg.get("segundos")) + "s" if reg.get("segundos") else "")
              + (" -> " + reg["motivo"][:70] if reg["motivo"] else ""), flush=True)
        with jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(reg, ensure_ascii=False) + "\n")

    conteo, vias, portipo = {}, {}, {}
    for r in registros:
        conteo[r["estado"]] = conteo.get(r["estado"], 0) + 1
        if r["via"]:
            vias[r["via"]] = vias.get(r["via"], 0) + 1
        portipo[r["tipo_norma"]] = portipo.get(r["tipo_norma"], 0) + 1
    resumen = {"departamento": args.departamento, "gestion": args.gestion, "tipos": tipos,
               "shard": args.shard, "shards": args.shards, "resoluciones": len(registros),
               "estados": conteo, "vias": vias, "por_tipo": portipo,
               "caracteres": sum(r.get("chars", 0) or 0 for r in registros),
               "paginas_ocr": sum(r.get("paginas") or 0 for r in registros),
               "segundos": round(sum(r.get("segundos") or 0 for r in registros), 1)}
    (salida / ("resumen-%s-%02d.json" % (args.gestion, args.shard))).write_text(
        json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nRESUMEN:", json.dumps(resumen, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
