import json, re, sqlite3
reg = json.load(open("/workspace/ab-probe-20260903/censo_dd.json"))
for etq, pat in [("DD 16/2026 (reglamenta la LD 500)", "n-016-2026-reglamento-a-la-ley-departamental-n-500"),
                 ("DD 20/2026 (VACATIO LEGIS)", "n-020-2026-ampliar-el-plazo-de-la-vacatio"),
                 ("DD 12/2026 (transicion de gestion)", "n-012-2026-transicion")]:
    for v in reg:
        if pat in v["slug"]:
            print("%-36s id %s" % (etq, v["id"]))
print()
c = sqlite3.connect("file:/workspace/bolivia-v7.db?mode=ro", uri=True); c.row_factory = sqlite3.Row
for n in ("500", "519", "520", "521", "523"):
    for r in c.execute("SELECT numero,anio,fecha,fuente_url,vigente,derogada_por FROM documentos "
                       "WHERE tipo_norma='Ley Departamental' AND numero=?", (n,)):
        m = re.search(r"download=(\d+):", r["fuente_url"] or "")
        print("LD %-4s anio %-6s fecha %-12s id %-6s vig %s  %s" % (
            r["numero"], r["anio"], repr(r["fecha"]), m.group(1) if m else "?", r["vigente"], r["derogada_por"] or ""))
c.close()
print()
print("Los ids de LEYES y DECRETOS son de catalogos distintos: NO son comparables entre si.")
print("O sea que el orden decreto-vs-ley NO se puede resolver por id. Hace falta la FECHA")
print("del decreto, y esa esta dentro del PDF, que es justo lo que no baje.")
