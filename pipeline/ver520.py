import json, sqlite3
reg = json.load(open("/workspace/ab-probe-20260903/censo_dd.json"))
print("== decretos de 2026 en la Gaceta")
for v in reg:
    if "2026" in v["slug"] and "decreto-departamental" in v["slug"]:
        print("  ", v["slug"][:108])
print()
print("== las leyes 516-523 en el corpus")
c = sqlite3.connect("file:/workspace/bolivia-v7.db?mode=ro", uri=True); c.row_factory = sqlite3.Row
for n in ("516", "517", "518", "519", "520", "521", "522", "523"):
    filas = c.execute("SELECT numero,anio,fecha,titulo,vigente,derogada_por,fuente_url FROM documentos "
                      "WHERE tipo_norma='Ley Departamental' AND numero=?", (n,)).fetchall()
    if not filas:
        print("  LD %-4s AUSENTE del corpus" % n)
    for r in filas:
        print("  LD %-4s | anio %-6s | fecha %-12s | vig %-5s | %s" % (
            r["numero"], repr(r["anio"]), repr(r["fecha"]), r["vigente"], (r["titulo"] or "")[:56]))
        print("           url: %s" % (r["fuente_url"] or "")[:110])
c.close()
