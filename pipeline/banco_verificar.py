"""Banco de /verificar. Tiene que poder dar ROJO: incluye casos donde la respuesta
correcta es 'no lo se' y casos donde la respuesta correcta es 'no esta'."""
import importlib.util, json, os, sys
os.environ["RAG_DB"] = "/workspace/bolivia-v7.db"
s = importlib.util.spec_from_file_location("m", "/workspace/ab-probe-20260903/api_v4.py")
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)

CASOS = [
    ("Ley Departamental 129",          "derogada"),
    ("LD 500/2025",                    "derogada"),
    ("ley departamental 139 de 2016",  "no_verificada"),   # parcial: la ley VIVE
    ("Ley Departamental 029",          "derogada"),
    ("Ley Departamental 519",          "no_verificada"),
    ("Ley 1970",                       "no_verificada"),   # el Codigo Penal: NO derogada
    ("Ley Departamental 9999",         "ausente_del_corpus"),
    ("una ley cualquiera",             "cita_no_interpretable"),
    ("",                               "cita_no_interpretable"),
]
fallos = 0
for cita, esperado in CASOS:
    r, _ = m.verificar(cita)
    ok = r["estado"] == esperado
    if not ok:
        fallos += 1
    print("%-6s %-32s -> %-22s (esperado %s)" % ("OK" if ok else "ROJO", repr(cita)[:30], r["estado"], esperado))
    if r.get("cadena_de_derogacion"):
        for p in r["cadena_de_derogacion"]:
            suc = p["sucesora_en_el_corpus"]
            print("          cadena: LD %s %s -> %s%s" % (
                p["norma"]["numero"], p["norma"]["anio"], p["nota"][:60],
                ("  [sucesora en corpus: %s %s]" % (suc["numero"], suc["anio"])) if suc else ""))
    print("          aviso:", r["advertencia"][:135])
print()
print("banco:", len(CASOS) - fallos, "/", len(CASOS))
print()
print("== ejemplo de respuesta completa (lo que consume un agente externo)")
r, _ = m.verificar("Ley Departamental 129")
print(json.dumps(r, ensure_ascii=False, indent=1)[:1500])
print()
print("== /estado")
e = m.estado_corpus()
print(json.dumps({k: v for k, v in e.items() if k != "fuentes"}, ensure_ascii=False, indent=1)[:1100])
sys.exit(1 if fallos else 0)
