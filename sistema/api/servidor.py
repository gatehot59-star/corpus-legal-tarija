#!/usr/bin/env python3
"""CORPUS · API de busqueda del corpus legal boliviano. Solo stdlib.
Devuelve el pasaje Y su procedencia verificable: fuente, sha256, via de
extraccion y estado de vigencia en TRES estados (si / no / NO MEDIDO)."""
import json, os, re, sqlite3, time, unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

DB = os.environ.get("RAG_DB", "/home/ubuntu/rag-abogacia-v7.db")
PORT = int(os.environ.get("RAG_PORT", "8080"))
MAX_LIMIT, MAX_Q, FACET_POOL, MAX_OFFSET = 40, 200, 400, 10000
M0, M1 = "\u0001", "\u0002"
FTS_UNSAFE = re.compile(r'[\"\'\(\)\*\^\:\-\+\{\}\[\]\u0001\u0002]')
FACETS = (("materia", "materia"), ("tipo", "tipo_norma"), ("anio", "anio"), ("jurisdiccion", "jurisdiccion"), ("via", "via_texto"))
WEIGHTS = "1.0, 1.5, 3.0"

def limpiar(q):
    q = FTS_UNSAFE.sub(" ", unicodedata.normalize("NFC", q)[:MAX_Q])
    toks = [t for t in q.split() if t]
    return " ".join('"%s"' % t for t in toks) if toks else None

def abrir():
    c = sqlite3.connect(DB, check_same_thread=False); c.execute("PRAGMA query_only = ON"); c.row_factory = sqlite3.Row; return c
DBC = abrir()
def vigencia(v):
    if v == 1: return "vigente"
    if v == 0: return "derogada"
    return "no_verificada"
def censo():
    t0=time.time(); out={"documentos":DBC.execute("SELECT count(*) n FROM documentos").fetchone()["n"],"pasajes":DBC.execute("SELECT count(*) n FROM chunks").fetchone()["n"],"caracteres":DBC.execute("SELECT coalesce(sum(CAST(chars AS INTEGER)),0) n FROM documentos").fetchone()["n"],"facetas":{}}
    for nombre,col in FACETS:
        rows=DBC.execute("SELECT %s v,count(*) n FROM documentos WHERE %s IS NOT NULL AND %s <> '' GROUP BY 1 ORDER BY n DESC LIMIT 14"%(col,col,col)).fetchall(); out["facetas"][nombre]=[{"v":r["v"],"n":r["n"]} for r in rows]
    out["vigencia_no_verificada"]=DBC.execute("SELECT count(*) n FROM documentos WHERE vigente IS NULL").fetchone()["n"]; out["ms"]=round((time.time()-t0)*1000,2); return out
SEL=("SELECT c.rowid rid,c.uid uid,c.nro nro,snippet(chunks,0,?,?,' … ',26) pasaje,bm25(chunks,"+WEIGHTS+") score,d.tipo_norma,d.numero,d.anio,d.fecha,d.titulo,d.materia,d.jurisdiccion,d.departamento,d.organo,d.sala,d.magistrado,d.vigente,d.derogada_por,d.fuente_url,d.sha256,d.via_texto,d.confianza,f.nombre fuente FROM chunks c JOIN documentos d ON d.uid=c.uid LEFT JOIN fuentes f ON f.fuente_id=d.fuente_id WHERE chunks MATCH ? ")
def buscar(q,limit,filtros,offset=0):
    m=limpiar(q)
    if m is None:return None,"la consulta queda vacia despues de sanitizarla"
    where="";args=[M0,M1,m]
    for nombre,col in FACETS:
        val=filtros.get(nombre)
        if val:where += " AND d.%s = ?"%col;args.append(val)
    t0=time.time()
    try:
        # El total tiene que contar lo MISMO que se devuelve: si el filtro entra en
        # las filas y no en el conteo, la interfaz calcula paginas que no existen.
        total=DBC.execute("SELECT count(*) n FROM chunks c JOIN documentos d ON d.uid=c.uid WHERE chunks MATCH ?"+where,[m]+args[3:]).fetchone()["n"]
        rows=DBC.execute(SEL+where+" ORDER BY bm25(chunks,"+WEIGHTS+") LIMIT ? OFFSET ?",args+[limit,offset]).fetchall()
        fac={}
        for nombre,col in FACETS:
            fr=DBC.execute("SELECT d.%s v,count(*) n FROM (SELECT uid FROM chunks WHERE chunks MATCH ? ORDER BY bm25(chunks,%s) LIMIT %d) s JOIN documentos d ON d.uid=s.uid WHERE d.%s IS NOT NULL AND d.%s <> '' GROUP BY 1 ORDER BY n DESC LIMIT 10"%(col,WEIGHTS,FACET_POOL,col,col),(m,)).fetchall();fac[nombre]=[{"v":r["v"],"n":r["n"]} for r in fr]
    except sqlite3.OperationalError as e:return None,"consulta invalida: %s"%e
    res=[]
    for r in rows:
        x=dict(r);x["vigencia"]=vigencia(x.pop("vigente"));x["sha256_corto"]=(x.get("sha256") or "")[:12];x["oficial"]=not (x.get("via_texto") or "").startswith("ocr");res.append(x)
    return {"consulta":q,"expresion":m,"total_pasajes":total,"devueltos":len(res),"limit":limit,"offset":offset,"ms":round((time.time()-t0)*1000,2),"filtros":filtros,"facetas":fac,"resultados":res},None
# The continuous reader implementation follows the committed v2; it is preserved verbatim in the repo.
def fusionar(trozos):
    if not trozos:return ""
    out=trozos[0]
    for t in trozos[1:]:
        k=min(600,len(out),len(t))
        while k>8:
            if out[-k:]==t[:k]:out+=t[k:];break
            k-=1
        else:out+=t
    return out
_CACHE={};_CACHE_MAX=12;VENTANA=2600;MAXSOL=600
def documento(uid):
    if uid in _CACHE:return _CACHE[uid]
    tr=[r["cuerpo"] or "" for r in DBC.execute("SELECT cuerpo FROM chunks WHERE uid=? ORDER BY CAST(nro AS INTEGER)",(uid,))];txt=fusionar(tr)
    if len(_CACHE)>=_CACHE_MAX:_CACHE.pop(next(iter(_CACHE)))
    _CACHE[uid]=txt;return txt
def cortar(txt,ini,fin):
    if ini>0:
        p=txt.rfind("\n\n",max(0,ini-900),ini)
        if p!=-1:ini=p+2
        else:
            e=max(txt.rfind(". ",max(0,ini-700),ini),txt.rfind("; ",max(0,ini-700),ini));ini=e+2 if e!=-1 else (txt.rfind(" ",max(0,ini-60),ini)+1)
    if fin<len(txt):
        p=txt.find("\n\n",fin,min(len(txt),fin+400))
        if p!=-1:fin=p
        else:
            for sig in (". ","; "):
                e=txt.find(sig,fin,min(len(txt),fin+300))
                if e!=-1:fin=e+1;break
            else:
                e=txt.find(" ",fin,min(len(txt),fin+60));fin=e if e!=-1 else fin
    return ini,fin
def texto(uid,nro,desde=None):
    d=DBC.execute("SELECT d.tipo_norma,d.numero,d.anio,d.fecha,d.titulo,d.materia,d.sala,d.magistrado,d.organo,d.departamento,d.jurisdiccion,d.vigente,d.derogada_por,d.fuente_url,d.sha256,d.via_texto,d.chars,f.nombre fuente FROM documentos d LEFT JOIN fuentes f ON f.fuente_id=d.fuente_id WHERE d.uid=?",(uid,)).fetchone()
    if d is None:return None,"documento inexistente"
    doc=dict(d);doc["vigencia"]=vigencia(doc.pop("vigente"));doc["sha256_corto"]=(doc.get("sha256") or "")[:12];doc["oficial"]=not (doc.get("via_texto") or "").startswith("ocr");txt=documento(uid)
    if not txt:return None,"documento sin texto"
    if desde is None:
        r=DBC.execute("SELECT cuerpo FROM chunks WHERE uid=? AND CAST(nro AS INTEGER)=CAST(? AS INTEGER)",(uid,nro)).fetchone()
        if r is None:return None,"pasaje inexistente"
        pos=txt.find((r["cuerpo"] or "")[:80]);centro=max(0,pos)
    else:
        try:centro=max(0,min(int(desde),len(txt)))
        except ValueError:centro=0
    ini,fin=cortar(txt,centro,min(len(txt),centro+VENTANA));return {"uid":uid,"nro":nro,"total_caracteres":len(txt),"desde":ini,"hasta":fin,"anterior":max(0,ini-VENTANA) if ini>0 else None,"siguiente":fin if fin<len(txt) else None,"porcentaje":round(100.0*fin/len(txt),1),"cuerpo":txt[ini:fin],"documento":doc},None
MAX_CADENA = 12
TIPOS = ((r"ley\s+departamental|^\s*l\.?d\.?\b|ley\s+dep\b", "Ley Departamental"),
         (r"auto\s+supremo|^\s*a\.?s\.?\b", "Auto Supremo"),
         (r"c[o\u00f3]digo", "Codigo"),
         (r"decreto\s+ley|^\s*d\.?l\.?\b", "Decreto Ley"),
         (r"constituci[o\u00f3]n", "Constitucion Politica del Estado"),
         (r"\bley\b", "Ley"))
NUM_CITA = re.compile(r"(\d{1,4})\s*(?:/\s*(\d{4}))?")
ANIO_CITA = re.compile(r"\b(19\d\d|20\d\d)\b")

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
    # 'Ley 1970' es el Codigo de Procedimiento Penal, no una ley del ano 1970. Con UN
    # solo numero en la cita, ese numero es el NUMERO. El ano solo existe si hay otro
    # numero, o si viene precedido de 'de'/'del'.
    anio = None
    numero = None
    m_barra = re.search(r"\b(\d{1,4})\s*/\s*(19\d\d|20\d\d)\b", plano)
    if m_barra:
        return tipo, int(m_barra.group(1)), m_barra.group(2)
    m_de = re.search(r"\bde[l]?\s+(?:\d{1,2}\s+de\s+\w+\s+de\s+)?(19\d\d|20\d\d)\b", plano)
    if m_de:
        anio = m_de.group(1)
        plano_sin = plano[:m_de.start()] + " " + plano[m_de.end():]
    else:
        plano_sin = plano
    nums = re.findall(r"\d{1,4}", plano_sin)
    if not nums and anio:
        # la cita era solo el ano: no alcanza para identificar una norma
        return tipo, None, anio
    if len(nums) >= 2 and not anio:
        for i, n in enumerate(nums):
            if re.fullmatch(r"19\d\d|20\d\d", n) and i > 0:
                anio = n
                nums = nums[:i] + nums[i + 1:]
                break
    if nums:
        numero = int(nums[0])
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
        m = re.search(r"(\d{1,4})", nota)
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
    tipo_difiere = False
    if not filas and tipo:
        # segundo intento sin el tipo: la Ley 1970 esta catalogada como 'Codigo'.
        # Se acepta pero se DECLARA, porque aflojar el tipo en silencio es como se
        # confunde una ley nacional con una departamental del mismo numero.
        filas = buscar_norma(None, numero, anio)
        tipo_difiere = bool(filas)
    if not filas:
        return dict(base, estado="ausente_del_corpus", coincidencias=0,
                    advertencia="Esta norma NO esta en el corpus. Eso no dice nada sobre su "
                                "vigencia: el corpus no la tiene, no la declara muerta."), None
    principal = dict(filas[0])
    est = vigencia(principal["vigente"])
    out = dict(base, estado=est, coincidencias=len(filas), tipo_difiere=tipo_difiere,
               norma=ficha_min(principal),
               otras_coincidencias=[ficha_min(f) for f in filas[1:6]],
               cadena_de_derogacion=cadena_de(principal))
    prefijo = ""
    if tipo_difiere:
        prefijo = ("ATENCION: la cita dice '%s' y en el corpus esta catalogada como '%s'. "
                   "Confirma que sea la misma norma antes de usarla. " % (tipo, principal["tipo_norma"]))
    if est == "derogada":
        out["advertencia"] = (prefijo + "DEROGADA. No la cites como vigente. Sucesora declarada: %s"
                              % (principal["derogada_por"] or "no registrada"))
    elif est == "vigente":
        out["advertencia"] = prefijo + "Vigencia verificada contra la fuente oficial al momento de la carga."
    else:
        nota = principal["derogada_por"] or ""
        out["advertencia"] = (prefijo + "NO VERIFICADA. El corpus no midio la vigencia de esta norma. "
                              "NO significa que este vigente: significa que no lo sabemos. "
                              "Confirmalo en la fuente oficial antes de citar."
                              + ((" Observacion registrada: " + nota) if nota else ""))
    return out, None

def estado_corpus():
    q = lambda s: DBC.execute(s).fetchone()["n"]
    normas = q("SELECT count(*) n FROM documentos WHERE jurisdiccion IN ('departamental','nacional')")
    medidas = q("SELECT count(*) n FROM documentos WHERE vigente IS NOT NULL")
    con_nota = q("SELECT count(*) n FROM documentos WHERE derogada_por IS NOT NULL AND derogada_por <> ''")
    leyes_nac = q("SELECT count(*) n FROM documentos WHERE tipo_norma='Ley Departamental' OR jurisdiccion='nacional'")
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
                         "solo_leyes_y_nacionales": leyes_nac,
                         "cobertura_solo_leyes_por_ciento": round(100.0 * medidas / leyes_nac, 2) if leyes_nac else 0,
                         "nota": "Un Auto Supremo no se abroga: la vigencia normativa no le aplica. Se publican DOS denominadores porque los dos son defendibles: 1.049 incluye las Resoluciones del Pleno, y el mas estricto son las %d leyes departamentales mas las nacionales." % leyes_nac},
            "fuentes": fuentes,
            "limites_declarados": [
                "La busqueda es literal sobre el texto: no hay expansion semantica.",
                "Las facetas cuentan sobre una muestra de %d pasajes, no sobre el total." % FACET_POOL,
                "El desplazamiento corta en %d pasajes." % MAX_OFFSET]}

class H(BaseHTTPRequestHandler):
    protocol_version="HTTP/1.1";server_version="corpus/2"
    def _json(self,code,obj):
        body=json.dumps(obj,ensure_ascii=False).encode("utf8");self.send_response(code);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Content-Length",str(len(body)));self.send_header("Access-Control-Allow-Origin","*");self.send_header("Access-Control-Allow-Headers","*");self.send_header("X-Content-Type-Options","nosniff");self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(body)
    def do_GET(self):
        u=urlparse(self.path);qs=parse_qs(u.query);one=lambda k:(qs.get(k) or [""])[0].strip()[:60]
        if u.path in ("/salud","/censo"):return self._json(200,dict(censo(),estado="vivo"))
        if u.path=="/estado":return self._json(200,estado_corpus())
        if u.path=="/verificar":
            cita=(qs.get("cita") or qs.get("q") or [""])[0].strip()[:MAX_Q]
            if not cita:return self._json(400,{"error":"falta el parametro cita"})
            res,err=verificar(cita);return self._json(400 if err else 200,{"error":err} if err else res)
        if u.path=="/texto":
            uid=(qs.get("uid") or [""])[0].strip()[:120];nro=(qs.get("nro") or [""])[0].strip()[:8]
            if not uid or not (nro or (qs.get("desde") or [""])[0]):return self._json(400,{"error":"faltan uid y nro"})
            res,err=texto(uid,nro,(qs.get("desde") or [None])[0]);return self._json(404 if err else 200,{"error":err} if err else res)
        if u.path=="/buscar":
            q=one("q")
            if not q:return self._json(400,{"error":"falta el parametro q"})
            try:limit=min(max(int(one("limit") or 10),1),MAX_LIMIT)
            except ValueError:limit=10
            try:offset=min(max(int(one("offset") or 0),0),MAX_OFFSET)
            except ValueError:offset=0
            filtros={n:one(n) for n,_ in FACETS if one(n)};res,err=buscar(q,limit,filtros,offset);return self._json(400 if err else 200,{"error":err} if err else res)
        return self._json(404,{"error":"ruta desconocida","rutas":["/censo","/estado","/buscar","/texto","/verificar"]})
    def log_message(self,*a):pass
if __name__=="__main__":print("corpus/2 en 0.0.0.0:%d sobre %s"%(PORT,DB),flush=True);ThreadingHTTPServer(("0.0.0.0",PORT),H).serve_forever()
