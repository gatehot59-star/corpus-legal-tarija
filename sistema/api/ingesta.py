"""Ingesta generica al corpus legal boliviano: cualquier fuente entra por aca.

Existe para que sumar la normativa nacional, otro departamento o un municipio sea escribir un
ADAPTADOR de ~30 lineas, no tocar el indice ni el buscador. La version anterior tenia las dos
fuentes de Tarija cableadas dentro del indexador; con eso, el primer Codigo nacional obligaba a
migrar 3.646 documentos.

Un adaptador recibe un directorio y devuelve `Documento`s. Nada mas. El resto (uid estable,
chunks con solape, citas, cola de revision) es comun y vive aca, asi que ninguna fuente nueva
puede olvidarse de la parte que importa.
"""
import argparse
import hashlib
import json
import re
import sqlite3
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

TAM_CHUNK = 1800
SOLAPE = 200


@dataclass
class Documento:
    """Lo minimo que un documento legal tiene que traer para ser citable."""
    fuente_id: str
    jurisdiccion: str                  # nacional | departamental | municipal | jurisprudencia
    tipo_norma: str
    numero: str
    texto: str
    fuente_url: str
    anio: str = ""
    fecha: str = ""
    titulo: str = ""
    departamento: str = ""
    organo: str = ""
    materia: str = ""
    sala: str = ""
    magistrado: str = ""
    partes: str = ""
    vigente: object = None             # None = NO MEDIDO, y se declara como tal
    derogada_por: str = ""
    sha256: str = ""
    via_texto: str = ""
    confianza: str = "media"
    archivo: str = ""
    citas: str = ""
    revision: list = field(default_factory=list)

    def uid(self) -> str:
        """Identificador estable y legible. Un agente que cita necesita que no cambie."""
        def limpiar(v, respaldo=""):
            s = unicodedata.normalize("NFD", str(v or ""))
            s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
            s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
            return s or respaldo
        prefijo = {"nacional": "nac", "jurisprudencia": "jur",
                   "departamental": "dep", "municipal": "mun"}.get(self.jurisdiccion, "otr")
        partes = [prefijo]
        if self.departamento:
            partes.append(limpiar(self.departamento)[:3])
        partes += [limpiar(self.tipo_norma, "doc")[:12], limpiar(self.numero, "sn"),
                   limpiar(self.anio or self.fecha[:4], "sa")]
        return "-".join(p for p in partes if p)


def trozar(texto: str, tam: int = TAM_CHUNK, solape: int = SOLAPE) -> list:
    """Chunks con solape, cortando en limite de articulo o parrafo cuando se puede.

    El solape no es paranoia: un articulo que cae justo en el borde desaparece de las dos
    mitades si los chunks no se pisan, y en un corpus legal eso es un articulo invisible.
    """
    texto = texto.replace("\f", "\n")
    if len(texto) <= tam:
        return [texto] if texto.strip() else []
    trozos, i = [], 0
    while i < len(texto):
        fin = min(i + tam, len(texto))
        if fin < len(texto):
            ventana = texto[i:fin]
            corte = max(ventana.rfind("\nARTICULO"), ventana.rfind("\nArticulo"),
                        ventana.rfind("\nArt\u00edculo"), ventana.rfind("\nART\u00cdCULO"),
                        ventana.rfind("\n\n"))
            if corte > tam // 3:
                fin = i + corte
        trozo = texto[i:fin]
        if trozo.strip():
            trozos.append(trozo)
        if fin >= len(texto):
            break
        i = max(fin - solape, i + 1)
    return trozos


class Corpus:
    """Escritura al corpus. Idempotente por uid: reingerir una fuente no duplica."""

    def __init__(self, ruta: str, esquema: str = ""):
        nuevo = not Path(ruta).exists()
        self.con = sqlite3.connect(ruta)
        self.con.row_factory = sqlite3.Row
        if nuevo or esquema:
            sql = Path(esquema or (Path(__file__).parent / "esquema.sql")).read_text(encoding="utf-8")
            self.con.executescript(sql)
        self.escritos = 0
        self.chunks = 0
        self.reemplazados = 0

    def registrar_fuente(self, fuente_id, nombre, jurisdiccion, departamento="", organo="",
                         url_base="", licencia="fuente oficial del Estado boliviano"):
        self.con.execute(
            "INSERT INTO fuentes (fuente_id, nombre, jurisdiccion, departamento, organo, "
            "url_base, licencia, actualizado) VALUES (?,?,?,?,?,?,?,?) "
            "ON CONFLICT(fuente_id) DO UPDATE SET nombre=excluded.nombre, "
            "actualizado=excluded.actualizado",
            (fuente_id, nombre, jurisdiccion, departamento, organo, url_base, licencia,
             time.strftime("%Y-%m-%d")))
        self.con.commit()

    def agregar(self, d: Documento):
        uid = d.uid()
        fila = self.con.execute("SELECT doc_id FROM documentos WHERE uid = ?", (uid,)).fetchone()
        if fila:
            # Reingesta: se borran sus chunks y se reescribe. Idempotente a proposito, para que
            # una actualizacion mensual no duplique el corpus.
            self.con.execute("DELETE FROM chunks WHERE doc_id = ?", (fila["doc_id"],))
            self.con.execute("DELETE FROM documentos WHERE doc_id = ?", (fila["doc_id"],))
            self.con.execute("DELETE FROM revision WHERE uid = ?", (uid,))
            self.reemplazados += 1

        sha = d.sha256 or hashlib.sha256(d.texto.encode("utf-8")).hexdigest()
        cur = self.con.execute(
            "INSERT INTO documentos (uid, fuente_id, jurisdiccion, departamento, organo, "
            "tipo_norma, numero, anio, fecha, titulo, materia, sala, magistrado, partes, "
            "vigente, derogada_por, fuente_url, sha256, via_texto, confianza, chars, archivo) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (uid, d.fuente_id, d.jurisdiccion, d.departamento, d.organo, d.tipo_norma,
             d.numero, d.anio, d.fecha, (d.titulo or "")[:400], d.materia, d.sala,
             d.magistrado, (d.partes or "")[:400], d.vigente, d.derogada_por, d.fuente_url,
             sha, d.via_texto, d.confianza, len(d.texto), d.archivo))
        doc_id = cur.lastrowid

        encabezado = " | ".join(str(x) for x in (d.numero, d.tipo_norma, d.titulo, d.materia,
                                                d.sala, d.anio, d.partes) if x)
        for n, trozo in enumerate(trozar(d.texto), start=1):
            self.con.execute(
                "INSERT INTO chunks (cuerpo, citas, encabezado, uid, doc_id, nro) "
                "VALUES (?,?,?,?,?,?)",
                (trozo, d.citas if n == 1 else "", encabezado if n == 1 else "",
                 uid, doc_id, n))
            self.chunks += 1

        for r in d.revision:
            self.con.execute(
                "INSERT INTO revision (uid, tipo, detalle, contexto) VALUES (?,?,?,?)",
                (uid, r.get("tipo", "?"), r.get("detalle", ""), r.get("contexto", "")))

        # Vigencia sin medir es un hecho pendiente, no un detalle: entra a la cola.
        if d.vigente is None:
            self.con.execute(
                "INSERT INTO revision (uid, tipo, detalle) VALUES (?,?,?)",
                (uid, "vigencia_no_medida",
                 "no se verifico si la norma esta vigente o fue derogada"))

        self.escritos += 1
        if self.escritos % 500 == 0:
            self.con.commit()

    def cerrar(self):
        self.con.commit()
        self.con.execute("INSERT INTO chunks(chunks) VALUES('optimize')")
        self.con.commit()
        self.con.close()


# --------------------------------------------------------------------------------------
# Adaptadores. Uno por fuente. Agregar la normativa nacional = escribir otro de este tamano.
# --------------------------------------------------------------------------------------

def citas_de(p: Path) -> str:
    idx = p.with_name(p.stem + ".indice.txt")
    if not idx.exists():
        return ""
    m = re.search(r"\[CITAS-NORMALIZADAS\](.*)$",
                  idx.read_text(encoding="utf-8", errors="replace"), re.S)
    return m.group(1).strip() if m else ""


def adaptador_gaceta_tarija(base: Path):
    """Leyes y resoluciones de la Asamblea Legislativa Departamental de Tarija."""
    regs = base / "corpus" / "registros.jsonl"
    if not regs.exists():
        return
    porarch = {}
    for l in regs.read_text(encoding="utf-8").splitlines():
        if l.strip():
            r = json.loads(l)
            if r.get("archivo_texto"):
                porarch[r["archivo_texto"]] = r
    for p in sorted((base / "corpus" / "texto").glob("*.txt")):
        if p.name.endswith(".indice.txt"):
            continue
        r = porarch.get(p.name, {})
        es_ley = (r.get("fuente_id") or "") == "tarija_leyes"
        yield Documento(
            fuente_id="tarija_gaceta", jurisdiccion="departamental", departamento="Tarija",
            organo="Asamblea Legislativa Departamental de Tarija",
            tipo_norma="Ley Departamental" if es_ley else "Resolucion del Pleno",
            numero=str(r.get("numero") or ""), anio="",
            titulo=r.get("titulo") or "", texto=p.read_text(encoding="utf-8", errors="replace"),
            fuente_url=r.get("fuente_url") or "https://www.tarija.gob.bo/gaceta-oficial",
            sha256=r.get("sha256_real") or "", via_texto=r.get("via") or "ocr",
            confianza="revision_humana" if r.get("estado") == "REVISION_HUMANA" else "media",
            archivo=p.name, citas=citas_de(p),
            revision=[{"tipo": "cita_ambigua",
                       "detalle": str(c.get("crudo", "")) + " -> " + str(c.get("canonico_probable", "")),
                       "contexto": c.get("contexto", "")}
                      for c in (r.get("revision_citas") or [])])


def adaptador_jurisprudencia_tsj(base: Path):
    """Autos Supremos, Sentencias y Resoluciones del Tribunal Supremo de Justicia."""
    regs = base / "jurisprudencia" / "resoluciones.jsonl"
    if not regs.exists():
        return
    porarch = {}
    for l in regs.read_text(encoding="utf-8").splitlines():
        if l.strip():
            r = json.loads(l)
            if r.get("archivo_texto"):
                porarch[r["archivo_texto"]] = r
    for p in sorted((base / "jurisprudencia" / "texto").glob("*.txt")):
        if p.name.endswith(".indice.txt"):
            continue
        r = porarch.get(p.name, {})
        yield Documento(
            fuente_id="tsj_genesis", jurisdiccion="jurisprudencia",
            departamento=r.get("departamento") or "", organo="Tribunal Supremo de Justicia",
            tipo_norma=r.get("tipo_norma") or "Auto Supremo",
            numero=str(r.get("nro_resolucion") or ""), anio=str(r.get("gestion") or ""),
            fecha=r.get("fecha_emision") or "", materia=r.get("materia") or "",
            sala=r.get("sala") or "", magistrado=r.get("magistrado") or "",
            partes=" c/ ".join(x for x in (r.get("demandante"), r.get("demandado")) if x),
            titulo=r.get("procesos") or "",
            texto=p.read_text(encoding="utf-8", errors="replace"),
            fuente_url=r.get("url_pdf_escaneado") or "https://genesis.tsj.bo/jurisprudencia",
            sha256=r.get("sha256_pdf") or "", via_texto=r.get("via") or "",
            confianza="alta" if r.get("via") == "html_oficial" else "media",
            archivo=p.name, citas=citas_de(p))


ADAPTADORES = {
    "tarija_gaceta": (adaptador_gaceta_tarija,
                      ("tarija_gaceta",
                       "Gaceta Oficial del Gobierno Autonomo Departamental de Tarija",
                       "departamental", "Tarija", "Asamblea Legislativa Departamental",
                       "https://www.tarija.gob.bo/gaceta-oficial")),
    "tsj_genesis": (adaptador_jurisprudencia_tsj,
                    ("tsj_genesis", "Buscador GENESIS del Tribunal Supremo de Justicia",
                     "jurisprudencia", "", "Tribunal Supremo de Justicia",
                     "https://genesis.tsj.bo/jurisprudencia")),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--origen", required=True, help="directorio con los corpus crudos")
    ap.add_argument("--db", required=True)
    ap.add_argument("--fuentes", default="", help="ids separados por coma; vacio = todas")
    ap.add_argument("--limite", type=int, default=0)
    a = ap.parse_args()

    base = Path(a.origen)
    corpus = Corpus(a.db)
    pedidas = [x.strip() for x in a.fuentes.split(",") if x.strip()] or list(ADAPTADORES)

    t0 = time.time()
    for fid in pedidas:
        if fid not in ADAPTADORES:
            print("ROJO: no hay adaptador para", fid, "| disponibles:", ", ".join(ADAPTADORES))
            return 2
        gen, meta = ADAPTADORES[fid]
        corpus.registrar_fuente(*meta)
        n = 0
        for d in gen(base):
            corpus.agregar(d)
            n += 1
            if a.limite and n >= a.limite:
                break
        print("  " + fid + ": " + str(n) + " documentos", flush=True)

    corpus.cerrar()
    con = sqlite3.connect(a.db)
    tot = con.execute("SELECT COUNT(*) FROM documentos").fetchone()[0]
    ch = con.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    rev = con.execute("SELECT COUNT(*) FROM revision WHERE resuelto = 0").fetchone()[0]
    porj = con.execute("SELECT jurisdiccion, COUNT(*) FROM documentos GROUP BY 1").fetchall()
    con.close()
    print()
    print("documentos:", tot, "| chunks:", ch, "| reemplazados:", corpus.reemplazados)
    print("por jurisdiccion:", dict(porj))
    print("cola de revision humana:", rev)
    print("segundos:", round(time.time() - t0, 1),
          "| indice:", round(Path(a.db).stat().st_size / 1e6, 1), "MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
