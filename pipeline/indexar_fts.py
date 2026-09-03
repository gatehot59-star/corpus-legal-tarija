"""Indice de busqueda del corpus legal, con SQLite FTS5 y ranking BM25.

**Por que FTS5 antes que embeddings, y no como consuelo:** un estudio juridico busca
"Ley 007", "Art. 17.I", "prescripcion adquisitiva", "AS/0122/2026". Eso es busqueda
LEXICA EXACTA, y ahi BM25 le gana a la similitud semantica: un embedding puede traer un fallo
parecido y no el que lleva ese numero. Los embeddings sirven para "casos como este", que es
otra pregunta y se agrega despues sin tirar esto.

Ademas, medido: SQLite 3.46.1 con FTS5 ya esta en `brain-env`, cero dependencias, y el indice
es un archivo unico que se copia. Un buscador que necesita un servicio prendido es un buscador
que el estudio no va a tener prendido.

Decisiones con su motivo:

1. **`remove_diacritics 2`**: buscar "prescripcion" tiene que encontrar "prescripcion" con
   tilde. Sin esto el usuario tiene que acertar las tildes de un OCR, que es pedirle lo
   imposible.
2. **Se indexa el crudo Y las citas normalizadas** en columnas distintas. Asi "Art. 17.I"
   encuentra el documento cuyo OCR escribio "Art. 17.1", sin haber alterado el texto legal.
3. **Chunks con solape** de 200 caracteres: un articulo cortado al medio por el limite del
   chunk desaparece de las dos mitades si no hay solape.
4. **Los metadatos van en una tabla aparte**, no dentro del FTS: filtrar por sala o gestion es
   un WHERE sobre columnas, no una busqueda de texto.
"""
import argparse
import json
import re
import sqlite3
import time
import unicodedata
from pathlib import Path

TAM_CHUNK = 1800
SOLAPE = 200

ESQUEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS documentos (
  doc_id      INTEGER PRIMARY KEY,
  archivo     TEXT UNIQUE NOT NULL,
  fuente      TEXT,            -- gaceta_tarija | jurisprudencia_tsj
  tipo_norma  TEXT,
  numero      TEXT,
  gestion     TEXT,
  fecha       TEXT,
  sala        TEXT,
  materia     TEXT,
  magistrado  TEXT,
  partes      TEXT,
  titulo      TEXT,
  chars       INTEGER,
  via         TEXT             -- html_oficial | texto_nativo_pdf | ocr_pdf_escaneado
);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(
  cuerpo,
  citas,
  encabezado,
  doc_id UNINDEXED,
  nro_chunk UNINDEXED,
  tokenize = "unicode61 remove_diacritics 2"
);
"""


def plano(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def trozar(texto: str, tam: int = TAM_CHUNK, solape: int = SOLAPE):
    """Corta en chunks con solape, prefiriendo cortar en un limite de parrafo o de articulo."""
    texto = texto.replace("\f", "\n")
    if len(texto) <= tam:
        return [texto] if texto.strip() else []
    trozos, i = [], 0
    while i < len(texto):
        fin = min(i + tam, len(texto))
        if fin < len(texto):
            # Se busca hacia atras un corte limpio: primero articulo, despues parrafo.
            ventana = texto[i:fin]
            corte = max(ventana.rfind("\nARTICULO"), ventana.rfind("\nArticulo"),
                        ventana.rfind("\nArt\u00edculo"), ventana.rfind("\n\n"))
            if corte > tam // 3:
                fin = i + corte
        trozo = texto[i:fin]
        if trozo.strip():
            trozos.append(trozo)
        if fin >= len(texto):
            break
        i = max(fin - solape, i + 1)
    return trozos


def citas_de(indice_txt: Path) -> str:
    """Las citas normalizadas que dejo el pipeline, si existen. No se recalculan aca."""
    if not indice_txt.exists():
        return ""
    t = indice_txt.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\[CITAS-NORMALIZADAS\](.*)$", t, re.S)
    return m.group(1).strip() if m else ""


def cargar_metadatos(base: Path) -> dict:
    """Une los registros de las dos fuentes en un mapa archivo -> metadatos."""
    meta = {}
    j = base / "jurisprudencia" / "resoluciones.jsonl"
    if j.exists():
        for l in j.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            r = json.loads(l)
            if r.get("archivo_texto"):
                meta[r["archivo_texto"]] = {
                    "fuente": "jurisprudencia_tsj", "tipo_norma": r.get("tipo_norma"),
                    "numero": r.get("nro_resolucion"), "gestion": str(r.get("gestion") or ""),
                    "fecha": r.get("fecha_emision"), "sala": r.get("sala"),
                    "materia": r.get("materia"), "magistrado": r.get("magistrado"),
                    "partes": " c/ ".join(x for x in (r.get("demandante"), r.get("demandado")) if x),
                    "titulo": r.get("procesos"), "via": r.get("via"),
                }
    g = base / "corpus" / "registros.jsonl"
    if g.exists():
        for l in g.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            r = json.loads(l)
            if r.get("archivo_texto"):
                meta[r["archivo_texto"]] = {
                    "fuente": "gaceta_tarija", "tipo_norma": r.get("fuente_id"),
                    "numero": r.get("numero"), "gestion": "", "fecha": "",
                    "sala": "", "materia": "", "magistrado": "", "partes": "",
                    "titulo": r.get("titulo"), "via": "ocr" if r.get("segundos") else "nativo",
                }
    return meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True, help="directorio con jurisprudencia/ y corpus/")
    ap.add_argument("--salida", required=True, help="archivo .db a crear")
    ap.add_argument("--limite", type=int, default=0)
    a = ap.parse_args()

    base = Path(a.corpus)
    salida = Path(a.salida)
    if salida.exists():
        salida.unlink()
    con = sqlite3.connect(salida)
    con.executescript(ESQUEMA)

    meta = cargar_metadatos(base)
    print("metadatos cargados:", len(meta), flush=True)

    archivos = []
    for sub in ("jurisprudencia/texto", "corpus/texto"):
        d = base / sub
        if d.exists():
            archivos += [p for p in sorted(d.glob("*.txt")) if not p.name.endswith(".indice.txt")]
    if a.limite:
        archivos = archivos[:a.limite]
    print("documentos a indexar:", len(archivos), flush=True)

    t0 = time.time()
    doc_id = 0
    total_chunks = 0
    sin_meta = 0
    for p in archivos:
        texto = p.read_text(encoding="utf-8", errors="replace")
        m = meta.get(p.name)
        if m is None:
            sin_meta += 1
            m = {"fuente": "?", "tipo_norma": "", "numero": "", "gestion": "", "fecha": "",
                 "sala": "", "materia": "", "magistrado": "", "partes": "", "titulo": "",
                 "via": ""}
        doc_id += 1
        con.execute(
            "INSERT INTO documentos (doc_id, archivo, fuente, tipo_norma, numero, gestion, "
            "fecha, sala, materia, magistrado, partes, titulo, chars, via) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (doc_id, p.name, m["fuente"], m["tipo_norma"], m["numero"], m["gestion"],
             m["fecha"], m["sala"], m["materia"], m["magistrado"], m["partes"],
             (m["titulo"] or "")[:300], len(texto), m["via"]))

        citas = citas_de(p.with_name(p.stem + ".indice.txt"))
        encabezado = " | ".join(str(x) for x in
                                (m["numero"], m["tipo_norma"], m["sala"], m["materia"],
                                 m["gestion"], m["partes"], m["titulo"]) if x)
        for n, trozo in enumerate(trozar(texto), start=1):
            con.execute("INSERT INTO chunks (cuerpo, citas, encabezado, doc_id, nro_chunk) "
                        "VALUES (?,?,?,?,?)",
                        (trozo, citas if n == 1 else "", encabezado if n == 1 else "", doc_id, n))
            total_chunks += 1
        if doc_id % 500 == 0:
            con.commit()
            print(f"  {doc_id}/{len(archivos)} docs, {total_chunks} chunks, "
                  f"{time.time() - t0:.0f}s", flush=True)

    con.commit()
    con.execute("INSERT INTO chunks(chunks) VALUES('optimize')")
    con.commit()
    con.close()

    seg = time.time() - t0
    print()
    print("documentos:", doc_id, "| chunks:", total_chunks, "| sin metadatos:", sin_meta)
    print("segundos:", round(seg, 1), "| tamano del indice:",
          round(salida.stat().st_size / 1e6, 1), "MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
