#!/usr/bin/env python3
"""Agrega /verificar y /estado, mas CORS. Entrada api.py md5 64ea272d2c6deed4a0ed36f99a93e3f3

/verificar recibe una cita como la escribe un abogado ("Ley Departamental 129",
"LD 500/2025", "Ley 1970") y devuelve el estado con la CADENA de derogacion.

La honestidad es el producto, asi que el contrato tiene TRES estados explicitos y el
tercero no se disfraza:
  vigente        -> verificado contra la fuente
  derogada       -> con su norma sucesora y la cadena completa
  no_verificada  -> el corpus NO lo midio. NO significa vigente, y el campo
                    'advertencia' lo dice con palabras, no con un null.
Y un cuarto caso que la competencia no distingue: ausente del corpus.

/estado publica el censo con su cobertura de vigencia, para que la honestidad sea
verificable desde afuera y no una promesa.
"""
import hashlib, sys

VIEJO = "64ea272d2c6deed4a0ed36f99a93e3f3"

BLOQUE = '''MAX_CADENA = 12
TIPOS = ((r"ley\\s+departamental|^\\s*l\\.?d\\.?\\b|ley\\s+dep\\b", "Ley Departamental"),
         (r"auto\\s+supremo|^\\s*a\\.?s\\.?\\b", "Auto Supremo"),
         (r"c[o\\u00f3]digo", "Codigo"),
         (r"decreto\\s+ley|^\\s*d\\.?l\\.?\\b", "Decreto Ley"),
         (r"constituci[o\\u00f3]n", "Constitucion Politica del Estado"),
         (r"\\bley\\b", "Ley"))
NUM_CITA = re.compile(r"(\\d{1,4})\\s*(?:/\\s*(\\d{4}))?")
ANIO_CITA = re.compile(r"\\b(19\\d\\d|20\\d\\d)\\b")

def interpretar(cita):
    """De la cita a (tipo, numero, anio). Sin numero no hay nada que verificar."""
    t = unicodedata.normalize("NFC", cita or "").strip()[:MAX_Q]
    plano = "".join(ch for ch in unicodedata.normalize("NFD", t)
                    if unicodedata.category(ch) != "Mn").lower()
    tipo = None
    for pat, nombre in TIPOS:
        if re.search(pat, plano):
            tipo = nombre
            break
    anio = None
    ma = ANIO_CITA.search(plano)
    numero = None
    sin_anio = ANIO_CITA.sub(" ", plano) if ma else plano
    mn = NUM_CITA.search(sin_anio)
    if mn:
        numero = int(mn.group(1))
        if mn.group(2):
            anio = mn.group(2)
    if ma and not anio:
        anio = ma.group(1)
    return tipo, numero, anio

SEL_DOC = ("SELECT uid,tipo_norma,numero,anio,fecha,titulo,materia,jurisdiccion,departamento,"
           "organo,sala,vigente,derogada_por,fuente_url,sha256,via_texto,chars FROM documentos ")

def ficha_min(r):
    d = dict(r)
    return {"uid": d["uid"], "tipo_norma": d["tipo_norma"], "numero": d["numero"], "anio": d["anio"],
            "titulo": d["titulo"], "vigencia": vigencia(d["vigente"]), "derogada_por": d["derogada_por"],
            "fuente_url": d["fuente_url"], "sha256_corto": (d["sha256"] or "")[:12],
            "via_texto": d["via_texto"], "caracteres": d["chars"]}

def buscar_norma(tipo, numero, anio):
    args, where = [], []
    if tipo:
        where.append("tipo_norma = ?"); args.append(tipo)
    where.append("numero GLOB '[0-9]*' AND CAST(numero AS INTEGER) = ?"); args.append(numero)
    if anio:
        where.append("anio = ?"); args.append(anio)
    filas = DBC.execute(SEL_DOC + "WHERE " + " AND ".join(where), args).fetchall()
    if not filas and anio:
        return buscar_norma(tipo, numero, None)
    return filas

def cadena_de(fila):
    """Sigue la derogacion hacia adelante: 129 -> 500 -> 520. Corta en MAX_CADENA para
    que un ciclo de datos malos no cuelgue el servicio."""
    pasos, vistos, actual = [], set(), dict(fila)
    while actual and actual["uid"] not in vistos and len(pasos) < MAX_CADENA:
        vistos.add(actual["uid"])
        nota = actual.get("derogada_por") or ""
        if not nota:
            break
        parcial = "parcial" in nota.lower()
        m = re.search(r"(\\d{1,4})", nota)
        sig = None
        if m and not parcial:
            cand = buscar_norma(actual["tipo_norma"], int(m.group(1)), None)
            cand = [c for c in cand if c["uid"] not in vistos]
            sig = dict(cand[0]) if cand else None
        pasos.append({"norma": ficha_min(actual), "nota": nota, "parcial": parcial,
                      "sucesora_en_el_corpus": ficha_min(sig) if sig else None})
        if parcial or not sig:
            break
        actual = sig
    return pasos

def verificar(cita):
    tipo, numero, anio = interpretar(cita)
    base = {"cita_consultada": cita, "interpretacion": {"tipo": tipo, "numero": numero, "anio": anio},
            "consultado_el": time.strftime("%Y-%m-%d")}
    if numero is None:
        return dict(base, estado="cita_no_interpretable",
                    advertencia="No se reconocio un numero de norma en la cita. Escribila como "
                                "'Ley Departamental 129' o 'Ley 1970 de 1999'."), None
    filas = buscar_norma(tipo, numero, anio)
    if not filas:
        return dict(base, estado="ausente_del_corpus", coincidencias=0,
                    advertencia="Esta norma NO esta en el corpus. Eso no dice nada sobre su "
                                "vigencia: el corpus no la tiene, no la declara muerta."), None
    principal = dict(filas[0])
    est = vigencia(principal["vigente"])
    out = dict(base, estado=est, coincidencias=len(filas), norma=ficha_min(principal),
               otras_coincidencias=[ficha_min(f) for f in filas[1:6]],
               cadena_de_derogacion=cadena_de(principal))
    if est == "derogada":
        out["advertencia"] = ("DEROGADA. No la cites como vigente. Sucesora declarada: %s"
                              % (principal["derogada_por"] or "no registrada"))
    elif est == "vigente":
        out["advertencia"] = "Vigencia verificada contra la fuente oficial al momento de la carga."
    else:
        nota = principal["derogada_por"] or ""
        out["advertencia"] = ("NO VERIFICADA. El corpus no midio la vigencia de esta norma. "
                              "NO significa que este vigente: significa que no lo sabemos. "
                              "Confirmalo en la fuente oficial antes de citar."
                              + ((" Observacion registrada: " + nota) if nota else ""))
    return out, None

def estado_corpus():
    q = lambda s: DBC.execute(s).fetchone()["n"]
    normas = q("SELECT count(*) n FROM documentos WHERE jurisdiccion IN ('departamental','nacional')")
    medidas = q("SELECT count(*) n FROM documentos WHERE vigente IS NOT NULL")
    con_nota = q("SELECT count(*) n FROM documentos WHERE derogada_por IS NOT NULL AND derogada_por <> ''")
    fuentes = [{"fuente": r["nombre"], "documentos": r["n"]} for r in DBC.execute(
        "SELECT f.nombre nombre, count(*) n FROM documentos d LEFT JOIN fuentes f ON f.fuente_id=d.fuente_id "
        "GROUP BY 1 ORDER BY n DESC")]
    return {"documentos": q("SELECT count(*) n FROM documentos"),
            "pasajes": q("SELECT count(*) n FROM chunks"),
            "caracteres": q("SELECT coalesce(sum(CAST(chars AS INTEGER)),0) n FROM documentos"),
            "texto_oficial": q("SELECT count(*) n FROM documentos WHERE via_texto NOT LIKE 'ocr%'"),
            "texto_por_ocr": q("SELECT count(*) n FROM documentos WHERE via_texto LIKE 'ocr%'"),
            "vigencia": {"normas_con_vigencia_aplicable": normas,
                         "con_estado_medido": medidas,
                         "con_observacion_de_derogacion": con_nota,
                         "cobertura_por_ciento": round(100.0 * medidas / normas, 2) if normas else 0,
                         "jurisprudencia_sin_vigencia_aplicable":
                             q("SELECT count(*) n FROM documentos WHERE jurisdiccion='jurisprudencia'"),
                         "nota": "Un Auto Supremo no se abroga: la vigencia normativa no le aplica. "
                                 "El denominador honesto son las normas, no el corpus entero."},
            "fuentes": fuentes,
            "limites_declarados": [
                "La busqueda es literal sobre el texto: no hay expansion semantica.",
                "Las facetas cuentan sobre una muestra de %d pasajes, no sobre el total." % FACET_POOL,
                "El desplazamiento corta en %d pasajes." % MAX_OFFSET]}

'''

R = [
    # 1. el bloque de funciones, antes del handler
    ("class H(BaseHTTPRequestHandler):", BLOQUE + "class H(BaseHTTPRequestHandler):"),
    # 2. CORS: sin esto ningun agente externo puede consumir la API desde un navegador
    ('self.send_header("X-Content-Type-Options","nosniff")',
     'self.send_header("Access-Control-Allow-Origin","*");self.send_header("Access-Control-Allow-Headers","*");self.send_header("X-Content-Type-Options","nosniff")'),
    # 3. las rutas
    ('        if u.path in ("/salud","/censo"):return self._json(200,dict(censo(),estado="vivo"))',
     '        if u.path in ("/salud","/censo"):return self._json(200,dict(censo(),estado="vivo"))\n'
     '        if u.path=="/estado":return self._json(200,estado_corpus())\n'
     '        if u.path=="/verificar":\n'
     '            cita=(qs.get("cita") or qs.get("q") or [""])[0].strip()[:MAX_Q]\n'
     '            if not cita:return self._json(400,{"error":"falta el parametro cita"})\n'
     '            res,err=verificar(cita);return self._json(400 if err else 200,{"error":err} if err else res)'),
    # 4. las rutas nuevas en el 404, para que se descubran solas
    ('{"error":"ruta desconocida","rutas":["/censo","/buscar","/texto"]}',
     '{"error":"ruta desconocida","rutas":["/censo","/estado","/buscar","/texto","/verificar"]}'),
]

VERDES = ["def verificar(", "def estado_corpus(", "def cadena_de(", "def interpretar(",
          "Access-Control-Allow-Origin", '"/verificar"', "cita_no_interpretable",
          "ausente_del_corpus", "NO VERIFICADA"]

def main(ruta):
    h = open(ruta, encoding="utf8").read()
    a = hashlib.md5(h.encode()).hexdigest()
    print("entrada md5", a, len(h), "caracteres")
    if a != VIEJO:
        print("ROJO: entrada inesperada, esperaba", VIEJO); return 1
    for i, (v, n) in enumerate(R, 1):
        c = h.count(v)
        if c != 1:
            print("ROJO: ancla", i, "aparece", c, "veces:", v[:60]); return 1
        h = h.replace(v, n, 1)
        print("  ancla", i, "aplicada")
    for t in VERDES:
        if t not in h:
            print("ROJO: falta en la salida:", t); return 1
    open(ruta, "w", encoding="utf8").write(h)
    print("VERDE salida md5", hashlib.md5(h.encode()).hexdigest(), len(h), "caracteres")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "api.py"))
