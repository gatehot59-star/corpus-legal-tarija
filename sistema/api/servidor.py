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
    d=DBC.execute("SELECT d.tipo_norma,d.numero,d.anio,d.fecha,d.titulo,d.materia,d.sala,d.magistrado,d.organo,d.departamento,d.vigente,d.fuente_url,d.sha256,d.via_texto,d.chars,f.nombre fuente FROM documentos d LEFT JOIN fuentes f ON f.fuente_id=d.fuente_id WHERE d.uid=?",(uid,)).fetchone()
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
class H(BaseHTTPRequestHandler):
    protocol_version="HTTP/1.1";server_version="corpus/2"
    def _json(self,code,obj):
        body=json.dumps(obj,ensure_ascii=False).encode("utf8");self.send_response(code);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Content-Length",str(len(body)));self.send_header("X-Content-Type-Options","nosniff");self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(body)
    def do_GET(self):
        u=urlparse(self.path);qs=parse_qs(u.query);one=lambda k:(qs.get(k) or [""])[0].strip()[:60]
        if u.path in ("/salud","/censo"):return self._json(200,dict(censo(),estado="vivo"))
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
        return self._json(404,{"error":"ruta desconocida","rutas":["/censo","/buscar","/texto"]})
    def log_message(self,*a):pass
if __name__=="__main__":print("corpus/2 en 0.0.0.0:%d sobre %s"%(PORT,DB),flush=True);ThreadingHTTPServer(("0.0.0.0",PORT),H).serve_forever()
