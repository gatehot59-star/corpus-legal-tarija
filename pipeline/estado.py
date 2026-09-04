import json, sqlite3, time, urllib.parse, urllib.request
API = "https://corpus-tarija.abacusai.cloud"
def P(u):
    t = time.time()
    d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "brain"}), timeout=40))
    return d, round((time.time() - t) * 1000)
c = sqlite3.connect("file:/workspace/bolivia-v7.db?mode=ro", uri=True); c.row_factory = sqlite3.Row
q = lambda s: c.execute(s).fetchone()[0]
print("== CORPUS")
print("  documentos      ", q("SELECT count(*) FROM documentos"))
print("  pasajes         ", q("SELECT count(*) FROM chunks"))
print("  caracteres      ", q("SELECT sum(CAST(chars AS INTEGER)) FROM documentos"))
print("  texto oficial   ", q("SELECT count(*) FROM documentos WHERE via_texto NOT LIKE 'ocr%'"),
      "| OCR", q("SELECT count(*) FROM documentos WHERE via_texto LIKE 'ocr%'"))
print("== VIGENCIA (denominador real = normas, no jurisprudencia)")
print("  leyes departamentales   ", q("SELECT count(*) FROM documentos WHERE tipo_norma='Ley Departamental'"))
print("  nacionales              ", q("SELECT count(*) FROM documentos WHERE jurisdiccion='nacional'"))
print("  con estado real (vig=0) ", q("SELECT count(*) FROM documentos WHERE vigente=0"))
print("  con nota de derogacion  ", q("SELECT count(*) FROM documentos WHERE derogada_por IS NOT NULL AND derogada_por<>''"))
print("  jurisprudencia (no aplica)", q("SELECT count(*) FROM documentos WHERE jurisdiccion='jurisprudencia'"))
print("== TITULOS")
print("  slug de descarga        ", q("SELECT count(*) FROM documentos WHERE titulo LIKE '%start=%'"))
print("  vacios                  ", q("SELECT count(*) FROM documentos WHERE titulo IS NULL OR trim(titulo)=''"))
c.close()
print("== SERVICIO PUBLICO")
d, ms = P(API + "/censo")
print("  /censo   ", ms, "ms | documentos", d["documentos"], "| sin vigencia verificada", d["vigencia_no_verificada"])
for term in ("usucapion", "asistencia familiar", "despido injustificado", "prescripcion"):
    d, ms = P(API + "/buscar?limit=12&q=" + urllib.parse.quote(term))
    print("  /buscar %-24s %4d ms | %6d pasajes | %d ms interno" % (term, ms, d["total_pasajes"], int(d["ms"])))
