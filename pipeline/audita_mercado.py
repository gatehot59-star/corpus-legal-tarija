import sqlite3
c = sqlite3.connect("file:/workspace/bolivia-v7.db?mode=ro", uri=True); c.row_factory = sqlite3.Row
q = lambda s, a=(): c.execute(s, a).fetchone()[0]
print("== AFIRMACIONES DEL ESTUDIO QUE TOCAN MI CORPUS")
print("  'las 523 leyes departamentales'        -> MEDIDO:", q("SELECT count(*) FROM documentos WHERE tipo_norma='Ley Departamental'"))
print("     numero mas alto de LD en el corpus  ->", q("SELECT max(CAST(numero AS INTEGER)) FROM documentos WHERE tipo_norma='Ley Departamental' AND numero GLOB '[0-9]*'"))
print("     numeros distintos                   ->", q("SELECT count(DISTINCT CAST(numero AS INTEGER)) FROM documentos WHERE tipo_norma='Ley Departamental' AND numero GLOB '[0-9]*'"))
print("  '282 AS de materia laboral'            -> MEDIDO:", q("SELECT count(*) FROM documentos WHERE materia='Del Trabajo'"))
print("  '1.829 AS penal'                       -> MEDIDO:", q("SELECT count(*) FROM documentos WHERE materia='Penal'"))
print("     ojo: esos numeros son de FACETAS de una busqueda, no del corpus")
print()
print("  == por materia, TODO el corpus")
for r in c.execute("SELECT coalesce(nullif(trim(materia),''),'(sin materia)') m, count(*) n FROM documentos GROUP BY 1 ORDER BY n DESC LIMIT 12"):
    print("     %-22s %5d" % (r["m"], r["n"]))
print()
print("  == cobertura por ano de las leyes departamentales (el rubro 1 del estudio)")
for r in c.execute("SELECT anio, count(*) n FROM documentos WHERE tipo_norma='Ley Departamental' GROUP BY 1 ORDER BY 1"):
    print("     %-6s %4d" % (r["anio"] or "(sin ano)", r["n"]))
print()
print("  == lo que el estudio pide como rubro 1 y 3: existe en el corpus?")
for etq, pat in [("decretos departamentales", "%ecreto%"), ("resoluciones del pleno", "Resolucion del Pleno"),
                 ("ordenanzas municipales", "%rdenanza%"), ("sentencias TCP", "%Constitucional%")]:
    n = q("SELECT count(*) FROM documentos WHERE tipo_norma LIKE ? OR organo LIKE ?", (pat, pat))
    print("     %-26s %5d" % (etq, n))
print()
print("  == y lo que /verificar necesitaria HOY")
print("     LD con estado o nota:", q("SELECT count(*) FROM documentos WHERE tipo_norma='Ley Departamental' AND (vigente IS NOT NULL OR (derogada_por IS NOT NULL AND derogada_por<>''))"))
print("     LD sin nada         :", q("SELECT count(*) FROM documentos WHERE tipo_norma='Ley Departamental' AND vigente IS NULL AND (derogada_por IS NULL OR derogada_por='')"))
c.close()
