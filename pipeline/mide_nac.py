import sqlite3
c = sqlite3.connect("file:/workspace/bolivia-v7.db?mode=ro", uri=True); c.row_factory = sqlite3.Row
print("== los 15 nacionales, con todo lo que hay")
for r in c.execute("SELECT uid,tipo_norma,numero,anio,fecha,titulo,fuente_url,chars,vigente FROM documentos WHERE jurisdiccion='nacional' ORDER BY anio"):
    print("--", r["tipo_norma"], r["numero"] or "", r["anio"] or "", "| chars", r["chars"], "| vigente", r["vigente"])
    print("   titulo:", (r["titulo"] or "-")[:100])
    print("   url:", (r["fuente_url"] or "-")[:120])
c.close()
