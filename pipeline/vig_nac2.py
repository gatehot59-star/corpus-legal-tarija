#!/usr/bin/env python3
"""E-01 me morde otra vez, y la evidencia cruda lo cazo: vig_nac.py declaro el Codigo
de Familia 1972 'ABROGADA por Ley 1455' leyendo la clausula "Abrogada por [BO-L-N25]"
que estaba en la pagina de la LEY 1455, no en la del Codigo. Medi el candidato y
concluí sobre mi norma.

Pero el falso positivo destapo el instrumento correcto: LexiVox SI declara la relacion
'Abrogada por' / 'Derogada por' en la pagina de la propia norma. Antes concluí que no
existia porque el Codigo de Familia no la trae; lo correcto era 'esa norma no la trae',
no 'LexiVox no la tiene'.

Este script lee la relacion DECLARADA en la pagina de cada norma. Sin inferencia.
Control positivo incluido: BO-L-1455, que sabemos dice 'Abrogada por BO-L-N25'.
"""
import os, re, ssl, sqlite3, sys, urllib.request

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
CACHE = "/workspace/ab-probe-20260903/cache_lexivox"
os.makedirs(CACHE, exist_ok=True)
DB = os.environ.get("RAG_DB", "/workspace/bolivia-v7.db")
# la relacion tiene que estar en la pagina de la PROPIA norma
RELS = ("Abrogada por", "Derogada por", "Abrogado por", "Derogado por",
        "Modificada por", "Modificado por")

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

def relaciones(h):
    """Cada relacion es una etiqueta seguida de enlaces a normas. Se corta en la
    siguiente etiqueta para no arrastrar la relacion de al lado."""
    out = []
    for r in RELS:
        for m in re.finditer(re.escape(r), h):
            reg = h[m.end():m.end() + 900]
            sig = min([reg.find(x) for x in RELS if reg.find(x) > 0] or [len(reg)])
            reg = reg[:sig]
            for mm in re.finditer(r'href="[^"]*norms/([^"/]+)"[^>]*>(.{0,150}?)</a>', reg, re.S | re.I):
                t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", mm.group(2))).strip()
                out.append((r, mm.group(1), t))
            break
    return out

def main():
    print("== CONTROL POSITIVO: BO-L-1455, que debe declarar 'Abrogada por'")
    h = baja("BO-L-1455.xhtml")
    if h.startswith("ERROR:"):
        print("   no se pudo bajar:", h)
    else:
        rr = relaciones(h)
        print("   relaciones halladas:", rr or "NINGUNA")
        if not any(r[0].startswith("Abrog") for r in rr):
            print("   ROJO: el instrumento no ve la relacion que sabemos que existe. Aborto.")
            return 1
        print("   VERDE: el instrumento detecta la relacion declarada")
    print()
    c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True); c.row_factory = sqlite3.Row
    filas = c.execute("SELECT uid,tipo_norma,numero,anio,titulo,fuente_url FROM documentos "
                      "WHERE jurisdiccion='nacional' ORDER BY anio").fetchall()
    c.close()
    ab = mod = nada = 0
    print("== las 15 nacionales, relacion DECLARADA en su propia pagina")
    for f in filas:
        ident = (f["fuente_url"] or "").rstrip("/").split("/")[-1]
        etq = "%-28s %s" % ((f["tipo_norma"] or "") + " " + str(f["numero"] or ""), f["anio"] or "")
        h = baja(ident) if ident else "ERROR:sin_url"
        if h.startswith("ERROR:"):
            print(" ", etq, "| NO MEDIDO (", h, ")"); nada += 1; continue
        rr = relaciones(h)
        muertes = [x for x in rr if x[0].startswith(("Abrog", "Derog"))]
        cambios = [x for x in rr if x[0].startswith("Modific")]
        if muertes:
            ab += 1
            print(" ", etq, "| *** ABROGADA/DEROGADA:", "; ".join("%s -> %s" % (x[0], x[2][:60]) for x in muertes))
        elif cambios:
            mod += 1
            print(" ", etq, "| modificada por", len(cambios), ":", "; ".join(x[2][:52] for x in cambios[:3]))
        else:
            nada += 1
            print(" ", etq, "| sin relacion declarada -> NO MEDIDO")
    print()
    print("RESUMEN: abrogadas/derogadas", ab, "| con modificaciones declaradas", mod, "| NO MEDIDO", nada)
    return 0

if __name__ == "__main__":
    sys.exit(main())
