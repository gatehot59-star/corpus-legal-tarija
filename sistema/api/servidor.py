"""API del corpus legal boliviano. Solo biblioteca estandar, a proposito.

**Por que sin framework:** el que va a correr esto es un estudio juridico en Tarija, no un
equipo de plataforma. `python3 servidor.py` y anda. Un backend que necesita instalar y mantener
dependencias es un backend que en tres meses nadie levanta, y el corpus muere con el.

**Esta pensado para que lo use un agente, y eso cambia el diseno, no solo la documentacion:**

1. **Toda respuesta trae `cita` completa**: uid estable, fuente_url oficial y sha256. Un agente
   legal que no puede citar la fuente no deberia responder, y este proyecto ya midio lo caro que
   sale afirmar sin procedencia.
2. **`confianza` y `vigente` viajan en cada resultado.** `vigente: null` significa NO MEDIDO, no
   "vigente". Un agente que asume vigencia por ausencia de dato da un consejo peligroso.
3. **`/agente/consultar` respeta un presupuesto de caracteres** y devuelve el contexto ya
   recortado con su procedencia. Sin eso, el agente recibe 140.000 caracteres y trunca por su
   cuenta, que es como se pierde justo el articulo que importaba.
4. **Cero resultados es una respuesta legitima y explicita** (`hallado: false`), no una lista
   vacia ambigua. El modo de falla peligroso de un buscador legal es inventar.
5. **`/openapi.json` y `/agente/manifiesto`** describen la API a la maquina, asi que un agente
   nuevo la descubre sin que nadie le explique nada.
6. **La cita lleva TODAS sus procedencias, no una.** La ingesta deduplica por contenido y
   registra cada aparicion: el AS/0140/2025 de Sala Penal entra al corpus una vez y tiene **diez
   ids de indice de GENESIS** apuntando al mismo pdf. Devolver una sola fuente es correcto y
   ademas incompleto, y un agente que cita una de diez no puede ser auditado por el que recibe
   el consejo. `cita.fuentes` trae todas; `cita.fuente_url` se mantiene por compatibilidad.
7. **`procedencias: null` es NO MEDIDO tambien.** Si la base es anterior a la tabla de
   procedencia, el campo viaja como `null` y no como `0` o como lista vacia: cero fuentes y
   "todavia no se registran fuentes" son estados distintos y confundirlos es como se firma un
   dato que nadie midio.
"""
import argparse
import json
import re
import sqlite3
import traceback
import unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

VERSION = "1.1.0"
DB = None
WEB = None
TOPE_LIMITE = 100
TOPE_PRESUPUESTO = 60000


def plano(s) -> str:
    s = unicodedata.normalize("NFD", str(s or ""))
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def a_consulta_fts(q: str) -> str:
    """Consulta del usuario -> sintaxis FTS5, sin que un caracter la rompa.

    FTS5 trata `.` `/` `-` `"` como sintaxis: "AS/0122/2026" o "Art. 17.I" crudos explotan el
    parser. Cada token va citado, y las frases entre comillas se respetan como frase.
    """
    q = (q or "").strip()
    frases = re.findall(r'"([^"]+)"', q)
    resto = re.sub(r'"[^"]+"', " ", q)
    partes = ['"' + f.replace('"', "") + '"' for f in frases if f.strip()]
    for token in re.split(r"\s+", resto):
        token = token.strip()
        if token:
            partes.append('"' + token.replace('"', "") + '"')
    return " ".join(partes)


def conectar():
    con = sqlite3.connect(DB, timeout=15)
    con.row_factory = sqlite3.Row
    return con


def hay_procedencias(con) -> bool:
    """Si la tabla no existe, la respuesta correcta es NO MEDIDO y no una lista vacia.

    Se consulta en vivo y no se cachea en un global: la base puede cambiarse por debajo entre
    reinicios, y un cache que sobrevive a eso es una afirmacion vieja con cara de dato.
    """
    return con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='documento_aliases'"
    ).fetchone() is not None


def procedencias_de(con, uids) -> dict:
    """uid -> lista de procedencias. Una sola consulta para todos los resultados de la pagina.

    Devuelve `{}` cuando la tabla no existe, y el llamador traduce eso a `null`. Hacerlo en una
    consulta y no una por resultado no es microoptimizacion: con limite 100 serian 100 idas a
    la base por busqueda, en una maquina de 2 nucleos.
    """
    uids = [u for u in dict.fromkeys(uids) if u]
    if not uids or not hay_procedencias(con):
        return {}
    out = {u: [] for u in uids}
    for i in range(0, len(uids), 400):
        lote = uids[i:i + 400]
        marcas = ",".join("?" * len(lote))
        for r in con.execute(
            "SELECT uid, fuente_id, fuente_url, archivo, sha256 FROM documento_aliases "
            "WHERE uid IN (" + marcas + ") ORDER BY alias_id", lote
        ).fetchall():
            out[r["uid"]].append({"fuente_id": r["fuente_id"], "fuente_url": r["fuente_url"],
                                  "archivo": r["archivo"], "sha256": r["sha256"]})
    return out


CAMPOS_FILTRO = {
    "jurisdiccion": "d.jurisdiccion", "departamento": "d.departamento",
    "tipo_norma": "d.tipo_norma", "materia": "d.materia", "sala": "d.sala",
    "anio": "d.anio", "fuente_id": "d.fuente_id", "numero": "d.numero",
    "organo": "d.organo",
}


def cita_de(f, fuentes=None, medido=True) -> dict:
    """La cita es parte del contrato, no un extra: sin esto el agente no puede citar.

    `fuentes` es la lista completa de procedencias y `procedencias` su conteo. Cuando la base no
    las registra, los dos viajan como `null` con su advertencia, porque una lista vacia se lee
    como "no tiene fuentes" y eso seria falso.
    """
    cita = {
        "uid": f["uid"], "tipo_norma": f["tipo_norma"], "numero": f["numero"],
        "anio": f["anio"], "fecha": f["fecha"], "organo": f["organo"],
        "jurisdiccion": f["jurisdiccion"], "departamento": f["departamento"],
        "fuente_url": f["fuente_url"], "sha256": f["sha256"],
        "referencia": " ".join(str(x) for x in
                               (f["tipo_norma"], f["numero"],
                                ("de " + f["anio"]) if f["anio"] else "") if x).strip(),
    }
    if not medido:
        cita["fuentes"] = None
        cita["procedencias"] = None
        cita["advertencia_procedencia"] = (
            "NO MEDIDO: esta base no registra procedencias (es anterior a documento_aliases). "
            "No concluir que el documento tiene una sola fuente oficial.")
        return cita
    fuentes = fuentes or []
    cita["fuentes"] = fuentes
    cita["procedencias"] = len(fuentes)
    if len(fuentes) > 1:
        cita["advertencia_procedencia"] = (
            "la fuente publica este mismo texto en " + str(len(fuentes)) + " entradas de "
            "indice distintas: citar `fuentes` completo, no una sola.")
    return cita


def buscar(q, limite=10, desplazamiento=0, filtros=None, presupuesto=0):
    filtros = filtros or {}
    fts = a_consulta_fts(q)
    if not fts:
        return {"hallado": False, "motivo": "consulta vacia", "total": 0, "resultados": []}

    con = conectar()
    where, params = ["chunks MATCH ?"], [fts]
    for clave, valor in filtros.items():
        if valor and clave in CAMPOS_FILTRO:
            where.append(CAMPOS_FILTRO[clave] + " = ?")
            params.append(valor)
    sql_base = ("FROM chunks c JOIN documentos d ON d.doc_id = c.doc_id WHERE "
                + " AND ".join(where))

    try:
        total = con.execute("SELECT COUNT(*) " + sql_base, params).fetchone()[0]
        filas = con.execute(
            "SELECT d.*, c.nro, bm25(chunks, 1.0, 3.0, 5.0) AS puntaje, "
            "snippet(chunks, 0, '<<', '>>', ' ... ', 20) AS fragmento, "
            "c.cuerpo AS cuerpo " + sql_base + " ORDER BY puntaje LIMIT ? OFFSET ?",
            params + [min(int(limite), TOPE_LIMITE), int(desplazamiento)]).fetchall()
        medido = hay_procedencias(con)
        proc = procedencias_de(con, [f["uid"] for f in filas]) if medido else {}
    except sqlite3.OperationalError as e:
        con.close()
        return {"hallado": False, "motivo": "consulta invalida: " + str(e)[:120],
                "total": 0, "resultados": []}
    con.close()

    resultados, gastado = [], 0
    for f in filas:
        cuerpo = f["cuerpo"] or ""
        if presupuesto:
            if gastado >= presupuesto:
                break
            cuerpo = cuerpo[:max(presupuesto - gastado, 0)]
            gastado += len(cuerpo)
        resultados.append({
            "uid": f["uid"], "titulo": f["titulo"], "materia": f["materia"],
            "sala": f["sala"], "magistrado": f["magistrado"], "partes": f["partes"],
            "fragmento": re.sub(r"\s+", " ", f["fragmento"] or "").strip(),
            "texto": cuerpo, "chunk": f["nro"], "puntaje_bm25": round(f["puntaje"], 3),
            "vigente": f["vigente"],            # None = NO MEDIDO, no "vigente"
            "confianza_texto": f["confianza"], "via_texto": f["via_texto"],
            "cita": cita_de(f, proc.get(f["uid"]), medido),
        })

    return {"hallado": bool(resultados), "consulta": q, "filtros": filtros,
            "total": total, "devueltos": len(resultados),
            "desplazamiento": int(desplazamiento), "resultados": resultados,
            "advertencia": None if resultados else
            "sin resultados: el corpus no contiene esta expresion. NO inferir que la norma no "
            "existe: puede estar fuera del alcance actual (ver /api/v1/alcance)."}


def documento(uid, con_texto=True):
    con = conectar()
    f = con.execute("SELECT * FROM documentos WHERE uid = ?", (uid,)).fetchone()
    if not f:
        con.close()
        return None
    d = {k: f[k] for k in f.keys()}
    medido = hay_procedencias(con)
    fuentes = procedencias_de(con, [uid]).get(uid, []) if medido else None
    d["cita"] = cita_de(f, fuentes, medido)
    d["procedencias"] = fuentes
    if con_texto:
        partes = con.execute("SELECT cuerpo FROM chunks WHERE doc_id = ? ORDER BY nro",
                             (f["doc_id"],)).fetchall()
        d["texto"] = "\n".join(p["cuerpo"] for p in partes)
    d["revision_pendiente"] = [
        {k: r[k] for k in r.keys()} for r in
        con.execute("SELECT tipo, detalle, contexto FROM revision WHERE uid = ? AND resuelto = 0",
                    (uid,)).fetchall()]
    con.close()
    return d


def procedencia_de_uid(uid: str):
    """Todas las fuentes oficiales de un documento citable. None si el uid no existe."""
    con = conectar()
    f = con.execute("SELECT uid, tipo_norma, numero, anio FROM documentos WHERE uid = ?",
                    (uid,)).fetchone()
    if not f:
        con.close()
        return None
    medido = hay_procedencias(con)
    fuentes = procedencias_de(con, [uid]).get(uid, []) if medido else None
    con.close()
    out = {"uid": uid,
           "referencia": " ".join(str(x) for x in (f["tipo_norma"], f["numero"]) if x).strip(),
           "procedencias": None if not medido else len(fuentes),
           "fuentes": fuentes}
    if not medido:
        out["advertencia"] = ("NO MEDIDO: esta base no registra procedencias. No concluir que el "
                             "documento tiene una sola fuente.")
    elif len(fuentes) > 1:
        out["advertencia"] = ("la fuente oficial publica este mismo texto en " +
                             str(len(fuentes)) + " entradas de indice: citar todas.")
    return out


def procedencias_multiples(limite=50):
    """Los documentos que la fuente publica mas de una vez. Es dato de auditoria, no un error."""
    con = conectar()
    if not hay_procedencias(con):
        con.close()
        return {"medido": False, "total": None, "documentos": None,
                "advertencia": "NO MEDIDO: esta base no registra procedencias."}
    filas = con.execute(
        "SELECT uid, COUNT(*) n FROM documento_aliases GROUP BY uid HAVING n > 1 "
        "ORDER BY n DESC, uid LIMIT ?", (min(int(limite), 500),)).fetchall()
    total = con.execute(
        "SELECT COUNT(*) FROM (SELECT uid FROM documento_aliases GROUP BY uid HAVING COUNT(*) > 1)"
    ).fetchone()[0]
    con.close()
    return {"medido": True, "total": total,
            "documentos": [{"uid": r["uid"], "procedencias": r["n"]} for r in filas],
            "nota": "mas de una procedencia NO significa duplicado en el corpus: el documento "
                    "esta una sola vez y la fuente lo publica en varias entradas de indice."}


def catalogos():
    con = conectar()
    out = {}
    for nombre, col in (("jurisdicciones", "jurisdiccion"), ("departamentos", "departamento"),
                        ("tipos_norma", "tipo_norma"), ("materias", "materia"),
                        ("salas", "sala"), ("anios", "anio")):
        out[nombre] = [r[0] for r in con.execute(
            "SELECT DISTINCT " + col + " FROM documentos WHERE " + col +
            " IS NOT NULL AND " + col + " != '' ORDER BY 1").fetchall()]
    out["fuentes"] = [{k: r[k] for k in r.keys()} for r in
                      con.execute("SELECT * FROM fuentes ORDER BY fuente_id").fetchall()]
    con.close()
    return out


def alcance():
    """Que contiene el corpus y que NO. Un agente que no sabe su alcance responde de mas."""
    con = conectar()
    porj = {r[0]: r[1] for r in con.execute(
        "SELECT jurisdiccion, COUNT(*) FROM documentos GROUP BY 1").fetchall()}
    tot = con.execute("SELECT COUNT(*) FROM documentos").fetchone()[0]
    chars = con.execute("SELECT COALESCE(SUM(chars),0) FROM documentos").fetchone()[0]
    rev = con.execute(
        "SELECT tipo, COUNT(*) FROM revision WHERE resuelto = 0 GROUP BY 1").fetchall()
    if hay_procedencias(con):
        proc = con.execute("SELECT COUNT(*) FROM documento_aliases").fetchone()[0]
        varias = con.execute(
            "SELECT COUNT(*) FROM (SELECT uid FROM documento_aliases GROUP BY uid "
            "HAVING COUNT(*) > 1)").fetchone()[0]
    else:
        proc = varias = None
    con.close()
    return {
        "version_api": VERSION, "documentos": tot, "caracteres": chars,
        "por_jurisdiccion": porj,
        "procedencias_registradas": proc,
        "documentos_con_varias_procedencias": varias,
        "cola_revision_humana": {r[0]: r[1] for r in rev},
        "cubre": ["normativa departamental de Tarija 2010-2026",
                  "jurisprudencia del Tribunal Supremo de Justicia filtrada por Tarija 2015-2026"],
        "NO_cubre": [
            "codigos nacionales (Civil, Penal, Procesal Civil, Procesal Penal, Familia, Tributario)",
            "Constitucion Politica del Estado (texto completo)",
            "leyes nacionales (Ley General del Trabajo, Ley 1178, Ley 025, Ley 348, Ley 031)",
            "Sentencias del Tribunal Constitucional Plurinacional",
            "normativa municipal",
            "los otros ocho departamentos",
        ],
        "advertencia_para_agentes":
            "Este corpus es PARCIAL. Si la respuesta depende de normativa nacional, de "
            "jurisprudencia constitucional o de otro departamento, decilo explicitamente en vez "
            "de responder con lo que hay. Y 'vigente: null' significa NO MEDIDO: no asumas "
            "vigencia. Lo mismo con 'procedencias: null'.",
    }


def manifiesto_agente(base_url=""):
    """Contrato para un agente legal: que herramientas hay y como NO usarlas."""
    return {
        "nombre": "corpus-legal-bolivia",
        "version": VERSION,
        "descripcion": "Corpus legal boliviano consultable: normativa y jurisprudencia con "
                       "procedencia verificable (fuente oficial + sha256).",
        "herramientas": [
            {"nombre": "buscar", "metodo": "GET", "ruta": "/api/v1/buscar",
             "parametros": {"q": "expresion a buscar (exacta o frase entre comillas)",
                            "limite": "1-100, default 10", "desplazamiento": "para paginar",
                            "jurisdiccion|departamento|tipo_norma|materia|sala|anio":
                                "filtros exactos"},
             "devuelve": "resultados con fragmento, texto del chunk y cita completa con todas "
                         "sus fuentes"},
            {"nombre": "documento", "metodo": "GET", "ruta": "/api/v1/documento/{uid}",
             "devuelve": "el documento completo con su cita, sus procedencias y su cola de "
                         "revision"},
            {"nombre": "procedencias", "metodo": "GET", "ruta": "/api/v1/procedencias/{uid}",
             "devuelve": "todas las fuentes oficiales de ese documento, con url, archivo y "
                         "sha256. Sin uid, lista los documentos que la fuente publica mas de "
                         "una vez"},
            {"nombre": "consultar", "metodo": "GET", "ruta": "/api/v1/agente/consultar",
             "parametros": {"q": "pregunta o expresion", "presupuesto": "caracteres maximos"},
             "devuelve": "contexto ya recortado al presupuesto, con procedencia por fragmento"},
            {"nombre": "alcance", "metodo": "GET", "ruta": "/api/v1/alcance",
             "devuelve": "que cubre y que NO cubre el corpus"},
            {"nombre": "catalogos", "metodo": "GET", "ruta": "/api/v1/catalogos",
             "devuelve": "valores validos de cada filtro"},
        ],
        "reglas_de_uso": [
            "Citar SIEMPRE con `cita.referencia` y `cita.fuente_url`. Sin fuente, no responder.",
            "Si `cita.procedencias` es mayor a 1, citar `cita.fuentes` COMPLETO: la fuente "
            "oficial publica el mismo texto en varias entradas y una sola no es auditable.",
            "`procedencias: null` es NO MEDIDO, no cero: esa base no registra fuentes todavia.",
            "`vigente: null` es NO MEDIDO. No afirmar que una norma esta vigente sin verificarlo.",
            "`confianza_texto: revision_humana` significa que el OCR no paso el control: "
            "advertirlo antes de citar textual.",
            "Si `hallado` es false, decir que el corpus no lo contiene. NO inferir que la norma "
            "no existe: leer /api/v1/alcance y nombrar el limite.",
            "Antes de opinar sobre materia nacional, consultar /api/v1/alcance: este corpus no "
            "tiene los codigos.",
            "Varias procedencias NO son un duplicado del corpus: el documento esta una sola vez.",
        ],
        "openapi": (base_url or "") + "/openapi.json",
    }


def openapi(base_url=""):
    def p(nombre, desc, requerido=False):
        return {"name": nombre, "in": "query", "required": requerido,
                "description": desc, "schema": {"type": "string"}}
    filtros = [p(k, "filtro exacto") for k in CAMPOS_FILTRO]
    return {
        "openapi": "3.0.3",
        "info": {"title": "Corpus Legal Bolivia", "version": VERSION,
                 "description": "Normativa y jurisprudencia boliviana con procedencia "
                                "verificable."},
        "servers": [{"url": base_url or "/"}],
        "paths": {
            "/api/v1/buscar": {"get": {
                "operationId": "buscar", "summary": "Busqueda lexica con ranking BM25",
                "parameters": [p("q", "expresion", True), p("limite", "1-100"),
                               p("desplazamiento", "paginacion")] + filtros,
                "responses": {"200": {"description": "resultados con cita verificable"}}}},
            "/api/v1/documento/{uid}": {"get": {
                "operationId": "documento", "summary": "Documento completo por uid estable",
                "parameters": [{"name": "uid", "in": "path", "required": True,
                                "schema": {"type": "string"}}],
                "responses": {"200": {"description": "documento con sus procedencias"},
                              "404": {"description": "no existe"}}}},
            "/api/v1/procedencias/{uid}": {"get": {
                "operationId": "procedencias",
                "summary": "Todas las fuentes oficiales de un documento",
                "parameters": [{"name": "uid", "in": "path", "required": True,
                                "schema": {"type": "string"}}],
                "responses": {"200": {"description": "fuentes con url, archivo y sha256"},
                              "404": {"description": "no existe"}}}},
            "/api/v1/procedencias": {"get": {
                "operationId": "procedenciasMultiples",
                "summary": "Documentos que la fuente publica en mas de una entrada de indice",
                "parameters": [p("limite", "1-500, default 50")],
                "responses": {"200": {"description": "uids con su cantidad de procedencias"}}}},
            "/api/v1/agente/consultar": {"get": {
                "operationId": "consultar",
                "summary": "Contexto recortado a un presupuesto de caracteres, con procedencia",
                "parameters": [p("q", "pregunta", True), p("presupuesto", "caracteres maximos")],
                "responses": {"200": {"description": "contexto citable"}}}},
            "/api/v1/alcance": {"get": {"operationId": "alcance",
                "summary": "Que cubre y que NO cubre el corpus",
                "responses": {"200": {"description": "alcance declarado"}}}},
            "/api/v1/catalogos": {"get": {"operationId": "catalogos",
                "summary": "Valores validos de los filtros",
                "responses": {"200": {"description": "catalogos"}}}},
        },
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "corpus-legal-bolivia/" + VERSION
    protocol_version = "HTTP/1.1"

    def log_message(self, formato, *args):
        print("[api] " + (formato % args), flush=True)

    def responder(self, codigo, cuerpo, tipo="application/json; charset=utf-8"):
        datos = (json.dumps(cuerpo, ensure_ascii=False, indent=1).encode("utf-8")
                 if not isinstance(cuerpo, bytes) else cuerpo)
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        # CORS abierto: el corpus es publico y un agente puede vivir en otro origen.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(datos)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        try:
            self.enrutar()
        except Exception:
            traceback.print_exc()
            self.responder(500, {"error": "error interno",
                                 "detalle": traceback.format_exc(limit=1)})

    def enrutar(self):
        u = urlparse(self.path)
        ruta = u.path.rstrip("/") or "/"
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        base = "http://" + self.headers.get("Host", "localhost")

        if ruta in ("/", "/index.html"):
            html = (WEB / "index.html") if WEB else None
            if html and html.exists():
                return self.responder(200, html.read_bytes(), "text/html; charset=utf-8")
            return self.responder(200, {"api": "corpus-legal-bolivia", "version": VERSION,
                                        "manifiesto": base + "/api/v1/agente/manifiesto"})

        if ruta == "/openapi.json":
            return self.responder(200, openapi(base))
        if ruta == "/api/v1/agente/manifiesto":
            return self.responder(200, manifiesto_agente(base))
        if ruta == "/api/v1/alcance":
            return self.responder(200, alcance())
        if ruta == "/api/v1/catalogos":
            return self.responder(200, catalogos())
        if ruta == "/api/v1/salud":
            return self.responder(200, {"estado": "ok", "version": VERSION, "db": DB})

        if ruta == "/api/v1/buscar":
            filtros = {k: q[k] for k in CAMPOS_FILTRO if k in q}
            return self.responder(200, buscar(q.get("q", ""), q.get("limite", 10),
                                              q.get("desplazamiento", 0), filtros))

        if ruta == "/api/v1/agente/consultar":
            pres = min(int(q.get("presupuesto", 12000) or 12000), TOPE_PRESUPUESTO)
            filtros = {k: q[k] for k in CAMPOS_FILTRO if k in q}
            r = buscar(q.get("q", ""), q.get("limite", 6), 0, filtros, presupuesto=pres)
            r["presupuesto_caracteres"] = pres
            al = alcance()
            r["instrucciones"] = manifiesto_agente(base)["reglas_de_uso"]
            r["alcance"] = {"cubre": al["cubre"], "NO_cubre": al["NO_cubre"]}
            return self.responder(200, r)

        if ruta == "/api/v1/procedencias":
            return self.responder(200, procedencias_multiples(q.get("limite", 50)))

        if ruta.startswith("/api/v1/procedencias/"):
            uid = unquote(ruta[len("/api/v1/procedencias/"):])
            pr = procedencia_de_uid(uid)
            if not pr:
                return self.responder(404, {"error": "no existe", "uid": uid,
                                            "sugerencia": "buscar por /api/v1/buscar?q=..."})
            return self.responder(200, pr)

        if ruta.startswith("/api/v1/documento/"):
            uid = unquote(ruta[len("/api/v1/documento/"):])
            d = documento(uid, con_texto=q.get("texto", "1") != "0")
            if not d:
                return self.responder(404, {"error": "no existe", "uid": uid,
                                            "sugerencia": "buscar por /api/v1/buscar?q=..."})
            return self.responder(200, d)

        if ruta == "/api/v1/revision":
            con = conectar()
            filas = con.execute(
                "SELECT uid, tipo, detalle, contexto FROM revision WHERE resuelto = 0 "
                "LIMIT ?", (min(int(q.get("limite", 50)), 500),)).fetchall()
            con.close()
            return self.responder(200, {"pendientes": [dict(f) for f in filas]})

        self.responder(404, {"error": "ruta inexistente", "ruta": ruta,
                             "manifiesto": base + "/api/v1/agente/manifiesto"})


def main() -> int:
    global DB, WEB
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--web", default=str(Path(__file__).resolve().parent.parent / "web"))
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--puerto", type=int, default=8080)
    a = ap.parse_args()

    DB = a.db
    WEB = Path(a.web) if a.web else None
    if not Path(DB).exists():
        print("ROJO: no existe la base", DB, "-> correr ingesta.py primero")
        return 2

    al = alcance()
    print("corpus-legal-bolivia " + VERSION)
    print("  documentos:", al["documentos"], "| caracteres:", al["caracteres"])
    print("  por jurisdiccion:", al["por_jurisdiccion"])
    print("  procedencias:", al["procedencias_registradas"],
          "| con varias fuentes:", al["documentos_con_varias_procedencias"])
    print("  escuchando en http://" + a.host + ":" + str(a.puerto), flush=True)
    ThreadingHTTPServer((a.host, a.puerto), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
