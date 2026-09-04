"""Completa el corpus: baja y digitaliza lo que el censo dice que falta.

Entra con el censo descubierto (`descubrir_gaceta.py`) y el manifest actual, saca la diferencia,
baja cada PDF y extrae su texto. Escribe filas nuevas al manifest y los textos en `11_TEXTO/`,
que es el mismo formato que ya consume el adaptador.

**Cuatro guards, cada uno por algo que ya paso en este proyecto:**

1. **Verifica que lo bajado sea un PDF** (`%PDF` en los primeros bytes). Un portal Joomla que
   pide sesion devuelve una pagina HTML con 200, y guardarla como `.pdf` mete una pagina de
   error dentro del corpus legal con procedencia verificable.
2. **Declara `OCR_REQUERIDO` cuando el texto nativo no alcanza**, en vez de escribir un texto
   vacio. Un documento con 12 caracteres se indexa igual y despues se lee como "la norma no dice
   nada", que es peor que no tenerlo.
3. **Escribe el sha256 de lo que realmente bajo**, no el esperado. Es la unica forma de que la
   cita sea verificable por un tercero.
4. **No sobreescribe filas existentes del manifest**: agrega. El manifest es append-only, y una
   corrida que lo reescribe entero puede perder lo que no volvio a ver.

Uso:

```bash
python3 pipeline/descubrir_gaceta.py --salida descubierto.jsonl
python3 pipeline/completar_gaceta.py --censo descubierto.jsonl \
        --manifest indices/manifest.jsonl --destino <raiz-del-corpus>
```
"""
import argparse
import hashlib
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; corpus-legal-tarija/1.0; +publico)"}
_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE

# Menos de esto no es un texto legal: es una portada, una pagina de error o un escaneo.
MINIMO_CARACTERES = 400


def cargar_jsonl(ruta):
    filas = []
    if not os.path.exists(ruta):
        return filas
    for linea in open(ruta, encoding="utf-8", errors="replace"):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        try:
            filas.append(json.loads(linea))
        except json.JSONDecodeError:
            continue
    return filas


def bajar(url, intentos=3):
    ultimo = ""
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90, context=_CTX) as r:
                return r.read(), r.headers.get("Content-Type", ""), ""
        except urllib.error.HTTPError as e:
            return b"", "", "HTTP " + str(e.code)
        except Exception as e:
            ultimo = type(e).__name__ + ": " + str(e)[:60]
            time.sleep(3 * (i + 1))
    return b"", "", ultimo


def texto_de_pdf(ruta):
    """Texto nativo. Devuelve (texto, paginas, herramienta). Nunca inventa: si no hay, vacio."""
    try:
        import pdfplumber
        partes = []
        with pdfplumber.open(ruta) as pdf:
            for pagina in pdf.pages:
                partes.append(pagina.extract_text() or "")
            return "\n".join(partes), len(pdf.pages), "pdfplumber"
    except Exception as e:
        try:
            import pypdf
            lector = pypdf.PdfReader(ruta)
            partes = [(p.extract_text() or "") for p in lector.pages]
            return "\n".join(partes), len(lector.pages), "pypdf"
        except Exception as e2:
            return "", 0, "ninguna (" + str(e)[:30] + " / " + str(e2)[:30] + ")"


def numero_de(slug):
    """Numero de norma desde el slug. Vacio si no se puede: no se adivina."""
    m = re.search(r"(?:ley-departamental-n?-?|ley-n-|r-p-a-n-)0*(\d+)", slug)
    return m.group(1).zfill(3) if m else ""


def gestion_de(slug):
    m = re.findall(r"(20[0-4]\d)", slug)
    return m[0] if m else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--censo", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--destino", required=True, help="raiz del corpus (contiene 11_TEXTO/)")
    ap.add_argument("--limite", type=int, default=0)
    a = ap.parse_args()

    censo = cargar_jsonl(a.censo)
    manifest = cargar_jsonl(a.manifest)
    rx = re.compile(r"download=(\d+):")
    tengo = set()
    for f in manifest:
        m = rx.search(str(f.get("fuente_url") or ""))
        if m:
            tengo.add(m.group(1))
    faltan = [d for d in censo if d["id_gaceta"] not in tengo]
    print("censo:", len(censo), "| ya en el manifest:", len(tengo),
          "| FALTAN:", len(faltan), flush=True)
    if a.limite:
        faltan = faltan[:a.limite]

    dir_pdf = os.path.join(a.destino, "10_PDF")
    dir_txt = os.path.join(a.destino, "11_TEXTO")
    os.makedirs(dir_pdf, exist_ok=True)
    os.makedirs(dir_txt, exist_ok=True)

    nuevas, resumen = [], {"ok": 0, "ocr_requerido": 0, "no_es_pdf": 0, "error_red": 0}
    for i, d in enumerate(faltan, start=1):
        crudo, tipo, err = bajar(d["fuente_url"])
        if err or not crudo:
            resumen["error_red"] += 1
            print("  %2d/%d ROJO red  id=%-6s %s" % (i, len(faltan), d["id_gaceta"], err),
                  flush=True)
            continue
        if not crudo[:5].startswith(b"%PDF"):
            # Guard 1: un HTML de error con 200 no entra al corpus legal.
            resumen["no_es_pdf"] += 1
            print("  %2d/%d ROJO no-pdf id=%-6s content-type=%s primeros=%r" %
                  (i, len(faltan), d["id_gaceta"], tipo[:30], crudo[:12]), flush=True)
            continue

        sha = hashlib.sha256(crudo).hexdigest()
        md5 = hashlib.md5(crudo).hexdigest()
        pdf = os.path.join(dir_pdf, md5 + ".pdf")
        open(pdf, "wb").write(crudo)
        texto, paginas, herr = texto_de_pdf(pdf)
        rel_txt = os.path.join("11_TEXTO", md5 + ".txt")
        estado = "OK"
        if len(texto.strip()) < MINIMO_CARACTERES:
            # Guard 2: se declara, no se escribe un texto vacio como si fuera la norma.
            estado = "OCR_REQUERIDO"
            resumen["ocr_requerido"] += 1
        else:
            open(os.path.join(a.destino, rel_txt), "w", encoding="utf-8").write(texto)
            resumen["ok"] += 1

        nuevas.append({
            "articulos": len(re.findall(r"[Aa]rt\u00edculo\s*\d+", texto)),
            "bytes": len(crudo), "caracteres": len(texto),
            "confidencialidad": "PUBLICO", "derogada_por": "",
            "etapas": {"descubrir": {"estado": "OK", "cuando": time.strftime("%Y-%m-%dT%H:%M:%S")},
                       "bajar": {"estado": "OK", "evidencia": "bytes=" + str(len(crudo)) +
                                 " sha256=" + sha[:12]},
                       "extraer": {"estado": estado, "evidencia": herr + " paginas=" + str(paginas)},
                       "estructurar": {"estado": "PENDIENTE"},
                       "indexar": {"estado": "PENDIENTE"}},
            "fecha_promulgacion": "", "fuente_id": d["fuente_id"],
            "fuente_url": d["fuente_url"], "gestion": gestion_de(d["slug"]),
            "jurisdiccion": "departamental_tarija", "md5": md5,
            "nombre_servidor": d["slug"], "numero": numero_de(d["slug"]),
            "paginas": paginas, "rubro": "legislacion_departamental_tarija",
            "ruta_local": os.path.join("10_PDF", md5 + ".pdf"),
            "ruta_texto": rel_txt if estado == "OK" else "",
            "sha256": sha,
            "tipo_norma": ("Ley Departamental" if d["fuente_id"] == "tarija_leyes"
                           else "Resolucion del Pleno de la Asamblea"),
            "titulo": d["slug"].replace("-", " "), "vigente": None,
        })
        print("  %2d/%d %-13s id=%-6s paginas=%-3s chars=%-7d %s" %
              (i, len(faltan), estado, d["id_gaceta"], paginas, len(texto), herr), flush=True)

    # Guard 4: append, nunca reescritura del manifest completo.
    with open(a.manifest, "a", encoding="utf-8") as f:
        for fila in nuevas:
            f.write(json.dumps(fila, ensure_ascii=False, sort_keys=True) + "\n")

    print()
    print("AGREGADAS AL MANIFEST:", len(nuevas), "|", json.dumps(resumen))
    print("manifest ahora:", len(cargar_jsonl(a.manifest)), "filas")
    if resumen["error_red"] or resumen["no_es_pdf"]:
        print("ATENCION: quedaron items sin bajar. El corpus NO esta completo y esto lo declara.")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
