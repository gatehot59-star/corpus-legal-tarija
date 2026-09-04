#!/usr/bin/env python3
"""Vigencia de las 15 nacionales, con el sujeto y el instrumento correctos.

MEDIDO ANTES DE ELEGIR LA VIA (y descarta dos):
  a) El texto propio NO sirve: una norma no declara su propia muerte.
  b) LexiVox NO marca 'abrogada' en la pagina de la victima: medido en el Codigo de
     Familia de 1972, que esta abrogado y su pagina no lo dice.
  c) Buscar 'abrog' en la seccion 'Referencias a esta norma' da FALSOS POSITIVOS:
     en el Codigo de Familia el unico 'abrog' es el DS 22773 abrogando OTROS decretos.

LA VIA QUE SI SIRVE: la seccion de referencias entrantes da CANDIDATOS. Un Codigo
solo lo puede abrogar una LEY o otro CODIGO posterior, nunca un Decreto Supremo. Se
descargan esos candidatos y se busca en SU texto una clausula abrogatoria que NOMBRE
a la nuestra: por titulo (>=22 caracteres de coincidencia) o por su numero exacto.

Tres estados. Sin clausula que la nombre: NO MEDIDO, y no se escribe nada.
"""
import difflib, json, os, re, ssl, sqlite3, sys, time, unicodedata, urllib.request

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
CACHE = "/workspace/ab-probe-20260903/cache_lexivox"
os.makedirs(CACHE, exist_ok=True)
DB = os.environ.get("RAG_DB", "/workspace/bolivia-v7.db")
MIN_TIT = 22
TOPE_CAND = 26

def sin(s):
    return "".join(ch for ch in unicodedata.normalize("NFD", s or "") if unicodedata.category(ch) != "Mn").lower()

def baja(ident):
    p = os.path.join(CACHE, ident.replace("/", "_"))
    if os.path.exists(p):
        return open(p, encoding="utf8").read()
    u = "https://www.lexivox.org/norms/" + ident
    try:
        h = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60, context=ctx).read().decode("utf8", "replace")
    except Exception as e:
        return "ERROR:" + type(e).__name__
    open(p, "w", encoding="utf8").write(h)
    time.sleep(0.7)
    return h

def texto(h):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t)

def refs_entrantes(h):
    ult = None
    for mm in re.finditer(r"Referencias\s+a\s+esta\s+norma", h):
        ult = mm
    if not ult:
        return []
    reg = h[ult.start():ult.start() + 40000]
    corte = re.search(r"(Nota\s+importante|Deroga\s+a|Modifica\s+a)", reg[60:])
    if corte:
        reg = reg[:60 + corte.start()]
    out = []
    for m in re.finditer(r'href="([^"]*norms/([^"/]+))"[^>]*>(.{0,170}?)</a>', reg, re.S | re.I):
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(3))).strip()
        out.append((m.group(2), t))
    return out

ANIO = re.compile(r"(19|20)\d\d")
VERBO = r"(?:se\s+)?(?:abrog|derog)\w*"
CLAUS = re.compile(VERBO + r"[^.;]{0,500}", re.I)

def parecido(a, b):
    a, b = sin(a), sin(b)
    if not a or not b:
        return 0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).find_longest_match(0, len(a), 0, len(b)).size

def main():
    c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True); c.row_factory = sqlite3.Row
    filas = c.execute("SELECT uid,tipo_norma,numero,anio,titulo,fuente_url FROM documentos "
                      "WHERE jurisdiccion='nacional' ORDER BY anio").fetchall()
    c.close()
    veredicto = {}
    for f in filas:
        etq = "%s %s de %s" % (f["tipo_norma"], f["numero"] or "", f["anio"] or "")
        print("=" * 78); print(etq, "|", (f["titulo"] or "")[:70])
        ident = (f["fuente_url"] or "").rstrip("/").split("/")[-1]
        if not ident:
            print("  sin identificador: NO MEDIDO"); veredicto[f["uid"]] = ("NO MEDIDO", "sin url"); continue
        h = baja(ident)
        if h.startswith("ERROR:"):
            print("  no se pudo bajar:", h); veredicto[f["uid"]] = ("NO MEDIDO", h); continue
        refs = refs_entrantes(h)
        # solo LEYES y CODIGOS posteriores: un Decreto Supremo no abroga un Codigo
        mi_anio = int(f["anio"] or 0)
        cand = []
        for i, t in refs:
            if not re.match(r"BO-(L|COD|CPE)-", i, re.I):
                continue
            m = ANIO.search(t)
            if m and mi_anio and int(m.group(0)) <= mi_anio:
                continue
            cand.append((i, t))
        print("  referencias entrantes:", len(refs), "| candidatos (ley/codigo posterior):", len(cand))
        hallado = None
        for i, t in cand[:TOPE_CAND]:
            hc = baja(i)
            if hc.startswith("ERROR:"):
                continue
            tc = texto(hc)
            for mc in CLAUS.finditer(tc):
                cl = mc.group(0)
                sim = parecido((f["titulo"] or "").split(",")[0][:80], cl)
                num = f["numero"] and re.search(r"\b" + re.escape(str(f["numero"]).lstrip("0") or "0") + r"\b", cl)
                if sim >= MIN_TIT or (num and sim >= 12):
                    hallado = (i, t, sim, bool(num), cl[:300])
                    break
            if hallado:
                break
        if hallado:
            i, t, sim, num, cl = hallado
            print("  *** ABROGADA por", i, "->", t[:80])
            print("      coincidencia de titulo:", sim, "car | numero citado:", num)
            print("      CRUDO:", cl)
            veredicto[f["uid"]] = ("ABROGADA", t)
        else:
            print("  sin clausula que la nombre en", min(len(cand), TOPE_CAND), "candidatos -> NO MEDIDO")
            veredicto[f["uid"]] = ("NO MEDIDO", "%d candidatos revisados" % min(len(cand), TOPE_CAND))
    json.dump({k: list(v) for k, v in veredicto.items()},
              open("/workspace/ab-probe-20260903/vig_nac.json", "w"), ensure_ascii=False, indent=0)
    ab = sum(1 for v in veredicto.values() if v[0] == "ABROGADA")
    print()
    print("RESUMEN: abrogadas", ab, "| NO MEDIDO", len(veredicto) - ab, "| total", len(veredicto))

if __name__ == "__main__":
    main()
