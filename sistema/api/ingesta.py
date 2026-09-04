"""Ingesta generica al corpus legal boliviano: cualquier fuente entra por aca.

Existe para que sumar la normativa nacional, otro departamento o un municipio sea escribir un
ADAPTADOR de ~30 lineas, no tocar el indice ni el buscador. La version anterior tenia las dos
fuentes de Tarija cableadas dentro del indexador; con eso, el primer Codigo nacional obligaba a
migrar 3.646 documentos.

Un adaptador recibe un directorio y devuelve `Documento`s. Nada mas. El resto (uid unico y
estable, chunks con solape, citas, cola de revision, procedencia y la VERIFICACION de que no se
perdio nada) es comun y vive aca, asi que ninguna fuente nueva puede olvidarse de la parte que
importa.

**Por que el uid termina en un hash, con el caso medido:** la primera version lo armaba con
tipo+numero+anio, y para la Gaceta de Tarija `anio` viene vacio. Tres RPA con numero 022 de
gestiones distintas generaban el mismo uid y el ultimo pisaba a los otros dos: entraron 3.646
documentos y quedaron 3.313. **Peor que fallar: borraba datos y reportaba exito.** Ahora el uid
lleva los 8 primeros caracteres del sha256, que no cambia entre corridas y es unico por
construccion, y la ingesta verifica el conteo al cerrar.

**Y por que el uid repetido ya NO reescribe:** con el hash dentro del uid, un uid repetido
significa "el mismo texto ofrecido otra vez", no una colision. El codigo anterior borraba el
documento y lo reinsertaba, asi que la fuente de la copia anterior desaparecia y el contador la
llamaba `reemplazados`. Eran 40 procedencias legitimas sin registrar. Ahora el documento canonico
queda intacto y cada aparicion deja su fila en `documento_aliases`.

**Y el invariante del CENSO, que es la correccion mas cara del proyecto.** El guard anterior
comparaba *lo que el adaptador ofrece* contra lo que quedo en la base. Eso **compara el error
consigo mismo**: el adaptador de Tarija listaba un directorio, 247 documentos descargados vivian
en otro, y la verificacion cerro en VERDE con `perdidos: 0` mientras faltaba el 24% del corpus
departamental (2.928.976 caracteres, 2019 al 24%, 2020 y 2026 en cero). Ahora `verificar()`
acepta el **censo de la fuente** y exige que el adaptador haya ofrecido ese numero.
"""
import argparse
import hashlib
import json
import re
import sqlite3
import sys
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

# El modulo hermano se importa por ruta explicita para que la ingesta funcione tanto ejecutada
# como script desde cualquier directorio como importada desde los tests.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import alias as procedencia  # noqa: E402
import fuente_nacional  # noqa: E402
import fuente_tarija  # noqa: E402
import normalizar  # noqa: E402

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

    def hash(self) -> str:
        return self.sha256 or hashlib.sha256(self.texto.encode("utf-8")).hexdigest()

    def uid(self) -> str:
        """Identificador estable Y UNICO. Legible para el humano, citable para el agente.

        El sufijo de hash no es adorno: sin el, dos documentos distintos con el mismo numero y
        sin ano colisionan y uno desaparece. Medido: 333 documentos perdidos asi.
        """
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
        partes += [limpiar(self.tipo_norma, "doc")[:12], limpiar(self.numero, "sn")]
        anio = limpiar(self.anio or self.fecha[:4])
        if anio:
            partes.append(anio)
        partes.append(self.hash()[:8])
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
    """Escritura al corpus. Idempotente por uid, y sin destruir procedencias."""

    def __init__(self, ruta: str, esquema: str = ""):
        nuevo = not Path(ruta).exists()
        self.con = sqlite3.connect(ruta)
        self.con.row_factory = sqlite3.Row
        if nuevo or esquema:
            sql = Path(esquema or (Path(__file__).parent / "esquema.sql")).read_text(encoding="utf-8")
            self.con.executescript(sql)
        # La tabla de procedencia se instala siempre: una base vieja la gana sin migracion.
        procedencia.instalar(self.con)
        self.ofrecidos = 0
        self.escritos = 0
        self.chunks = 0
        self.duplicados_contenido = 0
        self.alias_nuevos = 0
        self.alias_repetidos = 0
        self.sin_rastro = []
        self.docs_inicial = self.con.execute("SELECT COUNT(*) FROM documentos").fetchone()[0]
        self.alias_inicial = self.con.execute(
            "SELECT COUNT(*) FROM documento_aliases").fetchone()[0]

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

    def _anotar_procedencia(self, doc_id: int, uid: str, d: Documento):
        nueva = procedencia.registrar(
            self.con, doc_id=doc_id, uid=uid, fuente_id=d.fuente_id,
            fuente_url=d.fuente_url, archivo=d.archivo, sha256=d.hash())
        if nueva:
            self.alias_nuevos += 1
        else:
            self.alias_repetidos += 1

    def agregar(self, d: Documento):
        self.ofrecidos += 1
        uid = d.uid()
        fila = self.con.execute("SELECT doc_id FROM documentos WHERE uid = ?", (uid,)).fetchone()
        if fila:
            # Mismo uid = MISMO TEXTO (el hash esta dentro del uid). No es una colision y no es
            # una perdida: es el mismo documento listado otra vez, en otro archivo, en otra
            # gestion o en otra fuente. Antes se borraba y se reinsertaba, y con eso la
            # procedencia anterior desaparecia. Ahora el canonico no se toca y la aparicion
            # queda registrada, asi que la cita puede nombrar TODAS sus fuentes.
            self.duplicados_contenido += 1
            self._anotar_procedencia(fila["doc_id"], uid, d)
            return

        cur = self.con.execute(
            "INSERT INTO documentos (uid, fuente_id, jurisdiccion, departamento, organo, "
            "tipo_norma, numero, anio, fecha, titulo, materia, sala, magistrado, partes, "
            "vigente, derogada_por, fuente_url, sha256, via_texto, confianza, chars, archivo) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (uid, d.fuente_id, d.jurisdiccion, d.departamento, d.organo, d.tipo_norma,
             d.numero, d.anio, d.fecha, (d.titulo or "")[:400], d.materia, d.sala,
             d.magistrado, (d.partes or "")[:400], d.vigente, d.derogada_por, d.fuente_url,
             d.hash(), d.via_texto, d.confianza, len(d.texto), d.archivo))
        doc_id = cur.lastrowid
        self._anotar_procedencia(doc_id, uid, d)

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

    def verificar(self, censo: int = 0) -> dict:
        """Todo documento ofrecido tiene que dejar RASTRO, y el adaptador tiene que ofrecer TODO.

        Cinco chequeos, y el primero es el que faltaba:

        1. **el adaptador ofrecio tantos documentos como declara el censo de la fuente.** Sin
           esto, un adaptador que no ve un documento nunca lo ofrece y el conteo cierra en VERDE:
           asi 247 documentos quedaron afuera y la verificacion dijo `perdidos: 0`;
        2. cada ofrecido dejo un alias nuevo o repitio uno exacto -> `sin_rastro` en 0;
        3. los alias nuevos contados en memoria coinciden con las filas escritas en la base;
        4. los documentos canonicos nuevos coinciden con los insertados;
        5. ningun documento quedo sin al menos una procedencia.
        """
        self.con.commit()
        en_base = self.con.execute("SELECT COUNT(*) FROM documentos").fetchone()[0]
        alias_en_base = self.con.execute(
            "SELECT COUNT(*) FROM documento_aliases").fetchone()[0]
        aud = procedencia.auditar(self.con)
        rastro = self.alias_nuevos + self.alias_repetidos
        sin_rastro = self.ofrecidos - rastro
        delta_docs = en_base - self.docs_inicial
        delta_alias = alias_en_base - self.alias_inicial

        motivos = []
        if censo and self.ofrecidos != censo:
            motivos.append("el adaptador ofrecio " + str(self.ofrecidos) + " de " + str(censo) +
                           " que declara el censo de la fuente: faltan " +
                           str(censo - self.ofrecidos))
        if sin_rastro != 0:
            motivos.append("hay " + str(sin_rastro) + " documentos ofrecidos sin procedencia "
                                                      "registrada")
        if delta_alias != self.alias_nuevos:
            motivos.append("los alias escritos (" + str(delta_alias) + ") no coinciden con los "
                           "contados (" + str(self.alias_nuevos) + ")")
        if delta_docs != self.escritos:
            motivos.append("los documentos escritos (" + str(delta_docs) + ") no coinciden con "
                           "los insertados (" + str(self.escritos) + ")")
        if aud["documentos_sin_procedencia"]:
            motivos.append(str(aud["documentos_sin_procedencia"]) + " documentos quedaron sin "
                           "ninguna fuente")

        return {
            "censo_de_la_fuente": censo or None,
            "ofrecidos": self.ofrecidos,
            "canonicos_nuevos": self.escritos,
            "duplicados_por_contenido": self.duplicados_contenido,
            "alias_nuevos": self.alias_nuevos,
            "alias_reintento_exacto": self.alias_repetidos,
            "sin_rastro": sin_rastro,
            "en_base": en_base,
            "alias_en_base": alias_en_base,
            "documentos_sin_procedencia": aud["documentos_sin_procedencia"],
            "contenidos_con_varias_fuentes": aud["hashes_con_multiples_procedencias"],
            "veredicto": "VERDE" if not motivos else "ROJO: " + "; ".join(motivos),
        }

    def cerrar(self):
        self.con.commit()
        self.con.execute("INSERT INTO chunks(chunks) VALUES('optimize')")
        self.con.commit()


# --------------------------------------------------------------------------------------
# Adaptadores. Uno por fuente. Agregar la normativa nacional = escribir otro de este tamano.
# --------------------------------------------------------------------------------------

INFORMES = {}


def citas_de(p: Path) -> str:
    idx = p.with_name(p.stem + ".indice.txt")
    if not idx.exists():
        return ""
    m = re.search(r"\[CITAS-NORMALIZADAS\](.*)$",
                  idx.read_text(encoding="utf-8", errors="replace"), re.S)
    return m.group(1).strip() if m else ""


def adaptador_gaceta_tarija(base: Path):
    """Leyes y resoluciones de la Asamblea Legislativa Departamental de Tarija.

    **Recorre el MANIFEST, no un directorio.** La version anterior hacia `glob` de una carpeta y
    los 247 documentos que viven en otra no existian para ella: entraron 784 de 1.031. El detalle
    de la resolucion de texto y de la confianza esta en `fuente_tarija.py`.
    """
    fuente = fuente_tarija.FuenteTarija(base)
    if not fuente.censo:
        print("  AVISO: no hay indices/manifest.jsonl -> se corre SIN CENSO y no se puede "
              "detectar un documento que el adaptador no vea", flush=True)
    for fila in fuente.manifest:
        hallado = fuente.resolver(fila)
        if not hallado:
            continue
        r = hallado["registro"]
        meta = normalizar.metadatos_de(fila.get("titulo") or r.get("titulo"))
        comp = meta["compilado"]

        revisiones = [{"tipo": "cita_ambigua",
                       "detalle": str(c.get("crudo", "")) + " -> " + str(c.get("canonico_probable", "")),
                       "contexto": c.get("contexto", "")}
                      for c in (r.get("revision_citas") or [])]
        if comp:
            # Este archivo NO es una norma: contiene un rango de resoluciones. Se declara para
            # que ningun agente lo cite como si fuera una sola.
            revisiones.append({
                "tipo": "unidad_no_citable",
                "detalle": ("compilado de resoluciones " + str(comp["desde"]) + " al " +
                            str(comp["hasta"]) + ": contiene " + str(comp["contiene"]) +
                            " resoluciones que no tienen registro propio"),
                "contexto": meta.get("gestion", "")})
        if hallado["via"] == "extraido":
            # Se declara la via: este texto no paso el OCR masivo ni su gate de calidad.
            revisiones.append({
                "tipo": "texto_sin_gate",
                "detalle": "texto de la etapa extraer, sin OCR masivo ni control de calidad "
                           "ni citas normalizadas",
                "contexto": str(fila.get("ruta_texto") or "")})

        tipo_manifest = str(fila.get("tipo_norma") or "")
        es_ley = ("ley" in tipo_manifest.lower()
                  or (r.get("fuente_id") or "") == "tarija_leyes")
        tipo = ("Ley Departamental" if es_ley else
                ("Compilado de Resoluciones del Pleno" if comp else "Resolucion del Pleno"))

        yield Documento(
            fuente_id="tarija_gaceta", jurisdiccion="departamental", departamento="Tarija",
            organo="Asamblea Legislativa Departamental de Tarija",
            tipo_norma=tipo,
            numero=str(fila.get("numero") or r.get("numero") or ""),
            # `gestion` viene del manifest y esta en 1.000 de 1.031. Medido: coincide EXACTAMENTE
            # con lo que sale del titulo (754 = 754, mismo desglose por anio), o sea dos vias
            # independientes con el mismo resultado. Se prefiere el campo de la fuente.
            anio=str(fila.get("gestion") or "") or meta["anio"],
            fecha=str(fila.get("fecha_promulgacion") or ""),
            titulo=str(fila.get("titulo") or r.get("titulo") or ""),
            texto=hallado["texto"],
            fuente_url=str(fila.get("fuente_url") or r.get("fuente_url")
                           or "https://www.tarija.gob.bo/gaceta-oficial"),
            sha256=str(fila.get("sha256") or r.get("sha256_real") or ""),
            via_texto=("ocr" if hallado["via"] == "ocr" else "texto_extraido"),
            confianza=fuente_tarija.confianza_de(fila, r, hallado["via"]),
            archivo=hallado["ruta"].name, citas=hallado["citas"], revision=revisiones)

    INFORMES["tarija_gaceta"] = fuente.informe()


def adaptador_nacional(base: Path):
    """Normas del Estado Plurinacional, verificadas una por una contra su titulo real.

    El censo es `nacional/normas.jsonl`, que produce `pipeline/nacional_lexivox.py`. Ahi cada
    norma ya paso el control de identidad: no se acepta por su numero, se acepta porque el titulo
    que devolvio LexiVox coincide con el esperado.
    """
    fuente = fuente_nacional.FuenteNacional(base / "nacional")
    if not fuente.censo:
        print("  AVISO: no hay nacional/normas.jsonl -> la fuente nacional queda vacia",
              flush=True)
    for fila in fuente.normas:
        hallado = fuente.resolver(fila)
        if not hallado:
            continue
        yield Documento(
            fuente_id="lexivox_nacional", jurisdiccion="nacional", departamento="",
            organo="Estado Plurinacional de Bolivia",
            tipo_norma=str(fila.get("tipo_norma") or "Norma"),
            numero=str(fila.get("numero") or ""), anio=str(fila.get("anio") or ""),
            titulo=str(fila.get("titulo") or ""), materia=str(fila.get("materia") or ""),
            texto=hallado["texto"],
            fuente_url=str(fila.get("fuente_url") or ""),
            sha256=str(fila.get("sha256") or ""),
            via_texto="html_oficial",
            # `alta` porque es el texto publicado, sin OCR en el medio. La confianza es del
            # TEXTO, no de la vigencia: son dos cosas distintas y el campo `vigente` sigue en
            # None para las 15.
            confianza="alta",
            archivo=hallado["ruta"].name,
            revision=fuente_nacional.revisiones_de(fila))
    INFORMES["lexivox_nacional"] = fuente.informe()


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
    vistos = 0
    for p in sorted((base / "jurisprudencia" / "texto").glob("*.txt")):
        if p.name.endswith(".indice.txt"):
            continue
        r = porarch.get(p.name, {})
        vistos += 1
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
    # El censo de GENESIS es su propio jsonl de resoluciones: si un texto no esta en disco, se
    # nota aca y no en una lectura de directorio.
    INFORMES["tsj_genesis"] = {
        "censo_manifest": sum(1 for l in regs.read_text(encoding="utf-8").splitlines()
                              if l.strip()),
        "resueltos_por_ocr": vistos, "resueltos_por_extraccion": 0,
        "sin_texto": 0, "faltantes": []}


ADAPTADORES = {
    "tarija_gaceta": (adaptador_gaceta_tarija,
                      ("tarija_gaceta",
                       "Gaceta Oficial del Gobierno Autonomo Departamental de Tarija",
                       "departamental", "Tarija", "Asamblea Legislativa Departamental",
                       "https://www.tarija.gob.bo/gaceta-oficial")),
    "lexivox_nacional": (adaptador_nacional,
                        ("lexivox_nacional",
                         "LexiVox - normativa del Estado Plurinacional de Bolivia",
                         "nacional", "", "Estado Plurinacional de Bolivia",
                         "https://www.lexivox.org")),
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
    censo_total = 0
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
        inf = INFORMES.get(fid)
        if inf:
            print("    censo de la fuente:", inf["censo_manifest"],
                  "| por OCR:", inf["resueltos_por_ocr"],
                  "| por extraccion:", inf["resueltos_por_extraccion"],
                  "| SIN TEXTO:", inf["sin_texto"], flush=True)
            if inf["sin_texto"]:
                print("    faltantes (muestra):",
                      json.dumps(inf["faltantes"][:3], ensure_ascii=False), flush=True)
            # Lo que la fuente entrego MENOS lo que no tiene texto en ninguna via. Los que no
            # tienen texto quedan declarados arriba, no escondidos en el total.
            censo_total += inf["censo_manifest"] - inf["sin_texto"]

    ver = corpus.verificar(censo=censo_total if not a.limite else 0)
    corpus.cerrar()

    con = corpus.con
    tot = con.execute("SELECT COUNT(*) FROM documentos").fetchone()[0]
    ch = con.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    rev = con.execute("SELECT COUNT(*) FROM revision WHERE resuelto = 0").fetchone()[0]
    porj = con.execute("SELECT jurisdiccion, COUNT(*) FROM documentos GROUP BY 1").fetchall()
    al = con.execute("SELECT COUNT(*) FROM documento_aliases").fetchone()[0]
    con.close()

    print()
    print("documentos canonicos:", tot, "| chunks:", ch, "| procedencias:", al)
    print("por jurisdiccion:", dict(porj))
    print("cola de revision humana:", rev)
    print("segundos:", round(time.time() - t0, 1),
          "| indice:", round(Path(a.db).stat().st_size / 1e6, 1), "MB")
    print()
    print("VERIFICACION:", json.dumps(ver, ensure_ascii=False))
    if ver["veredicto"] != "VERDE":
        print("ROJO: la ingesta no pudo dar cuenta de todos los documentos. NO usar esta base.")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
