#!/usr/bin/env python3
"""Vigencia de las nacionales, leyendo la relacion DECLARADA por LexiVox.

Historia de dos instrumentos rotos, los dos cazados por un guard y no por mi:
  v1 leyo la clausula 'Abrogada por' que estaba en la pagina del CANDIDATO y concluyo
     sobre MI norma. E-01: sujeto equivocado. Lo delato la evidencia cruda.
  v2 busco la etiqueta y los enlaces pegados a ella. Pero la etiqueta vive en el
     INDICE de relaciones y su contenido esta en otra parte, anclado por id. El control
     positivo (BO-L-1455, que sabemos declara 'Abrogada por') dio ROJO y aborto.

v3: del indice se saca el ancla (href="#idmNNN"), y el contenido se lee en el elemento
con ese id. El control positivo tiene que pasar o el script no mide nada.
"""
import os, re, ssl, sqlite3, sys, urllib.request

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
CACHE = "/workspace/ab-probe-20260903/cache_lexivox"
os.makedirs(CACHE, exist_ok=True)
DB = os.environ.get("RAG_DB", "/workspace/bolivia-v7.db")
MUERTE = ("Abrogada por", "Derogada por", "Abrogado por", "Derogado por")
CAMBIO = ("Modificada por", "Modificado por")

def baja(ident):
    p = os.path.join(CACHE, ident.replace("/", "_"))
    if os.path.exists(p):
        return open(p, encoding="utf8").read()
    try:
        h = urllib.request.urlopen(urllib.request.Request(
            "https://www.lexivox.org/norms/" + ident, headers=H), timeout=60, context=ctx).read().decode("utf8", "replace")
    except Exception as e:
        return "ERROR:" + type(e).__name__
    open(p, "w", encoding="utf8").write(h)
    return h

def bloque_de(h, etiqueta):
    """Del indice saca el ancla y devuelve el contenido del elemento con ese id."""
    m = re.search(r'href="#([\w.\-]+)"[^>]*>\s*' + re.escape(etiqueta), h)
    if not m:
        return None
    ancla = m.group(1)
    m2 = re.search(r'id="' + re.escape(ancla) + r'"', h)
    if not m2:
        return None
    reg = h[m2.end():m2.end() + 4000]
    # el bloque real es: <a name="idmN" id="idmN"></a>ETIQUETA</h2><dl>...</dl>
    # o sea la etiqueta viene DESPUES del ancla. La v3 cortaba en "el siguiente
    # encabezado" y el primero que encontraba era la etiqueta misma, a 6 caracteres:
    # el bloque quedaba vacio y el control positivo daba rojo. Hay que saltarla.
    i = reg.find(etiqueta)
    if i >= 0:
        reg = reg[i + len(etiqueta):]
    cortes = [reg.find(e) for e in (MUERTE + CAMBIO + ("Nota importante", "Referencias a esta norma", "Véase también")) if reg.find(e) > 0]
    if cortes:
        reg = reg[:min(cortes)]
    return reg

def normas(reg):
    out = []
    for m in re.finditer(r'href="[^"]*norms/([^"/]+)"[^>]*>(.{0,160}?)</a>', reg or "", re.S | re.I):
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()
        if t:
            out.append((m.group(1), t))
    return out

def leer(ident):
    h = baja(ident)
    if h.startswith("ERROR:"):
        return None, h
    muertes, cambios = [], []
    for e in MUERTE:
        for i, t in normas(bloque_de(h, e)):
            muertes.append((e, i, t))
    for e in CAMBIO:
        for i, t in normas(bloque_de(h, e)):
            cambios.append((e, i, t))
    return (muertes, cambios), None

def main():
    print("== CONTROL POSITIVO: BO-L-1455 debe declarar que esta abrogada")
    r, err = leer("BO-L-1455.xhtml")
    if err or not r[0]:
        print("   ROJO: el instrumento no ve la relacion que sabemos que existe:", err or "sin muertes")
        return 1
    for e, i, t in r[0]:
        print("   VERDE:", e, "->", i, "|", t[:70])
    print()
    c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True); c.row_factory = sqlite3.Row
    filas = c.execute("SELECT uid,tipo_norma,numero,anio,titulo,fuente_url FROM documentos "
                      "WHERE jurisdiccion='nacional' ORDER BY anio").fetchall()
    c.close()
    ab = mod = nada = 0
    print("== las 15 nacionales")
    for f in filas:
        ident = (f["fuente_url"] or "").rstrip("/").split("/")[-1]
        etq = "%-26s %s" % ((f["tipo_norma"] or "") + " " + str(f["numero"] or ""), f["anio"] or "")
        if not ident:
            print(" ", etq, "| NO MEDIDO (sin url)"); nada += 1; continue
        r, err = leer(ident)
        if err:
            print(" ", etq, "| NO MEDIDO (", err, ")"); nada += 1; continue
        muertes, cambios = r
        if muertes:
            ab += 1
            print(" ", etq, "| *** ABROGADA:", "; ".join("%s -> %s" % (e, t[:62]) for e, i, t in muertes))
        elif cambios:
            mod += 1
            print(" ", etq, "| VIGENTE con", len(cambios), "modificaciones declaradas:",
                  "; ".join(t[:46] for e, i, t in cambios[:3]))
        else:
            nada += 1
            print(" ", etq, "| sin relacion declarada -> NO MEDIDO")
    print()
    print("RESUMEN: abrogadas", ab, "| con modificaciones (o sea NO abrogadas)", mod, "| NO MEDIDO", nada)
    return 0

if __name__ == "__main__":
    sys.exit(main())
