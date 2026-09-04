"""Falsador de la API. Prueba el contrato que un agente va a depender, no que el server arranque.

Seis cosas que tienen que ser ciertas o el sistema miente:
  1. Toda respuesta con resultado trae cita con fuente_url y uid. Sin eso no se puede citar.
  2. Cero resultados dice `hallado: false` Y una advertencia, en vez de una lista vacia ambigua.
  3. `vigente: null` se preserva como null en el JSON. Si el serializador lo convierte en 0 o en
     "no", un agente lee "derogada" donde dice NO MEDIDO.
  4. Los filtros filtran de verdad: pedir sala X no puede devolver sala Y.
  5. El presupuesto de caracteres se RESPETA. Si no, el agente recibe mas de lo que pidio y
     trunca por su cuenta, justo donde estaba el articulo.
  6. **La cita trae TODAS las procedencias.** El AS/0140/2025 tiene diez entradas de indice en
     GENESIS apuntando al mismo pdf; una API que devuelve una sola es correcta e incompleta, y
     el agente que cita una de diez no puede ser auditado.
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8099"
fallos = []


def get(ruta):
    with urllib.request.urlopen(BASE + ruta, timeout=30) as r:
        return r.status, json.load(r)


def ok(nombre, condicion, detalle=""):
    print(("VERDE " if condicion else "ROJO  ") + nombre
          + (("  -> " + detalle) if not condicion and detalle else ""))
    if not condicion:
        fallos.append(nombre)


s, salud = get("/api/v1/salud")
ok("salud responde 200", s == 200 and salud.get("estado") == "ok")

s, al = get("/api/v1/alcance")
ok("alcance declara documentos", al.get("documentos", 0) > 0, str(al)[:80])
ok("alcance declara lo que NO cubre", len(al.get("NO_cubre", [])) >= 5)
ok("alcance advierte a los agentes", "NO MEDIDO" in (al.get("advertencia_para_agentes") or ""))
ok("alcance cuenta las procedencias registradas",
   (al.get("procedencias_registradas") or 0) >= al.get("documentos", 0),
   str(al.get("procedencias_registradas")))

s, man = get("/api/v1/agente/manifiesto")
ok("manifiesto lista herramientas", len(man.get("herramientas", [])) >= 5)
ok("manifiesto prohibe citar sin fuente",
   any("fuente" in r.lower() for r in man.get("reglas_de_uso", [])))
ok("manifiesto obliga a citar TODAS las fuentes",
   any("fuentes" in r and "COMPLETO" in r for r in man.get("reglas_de_uso", [])))

s, oa = get("/openapi.json")
ok("openapi valido",
   oa.get("openapi", "").startswith("3.") and "/api/v1/buscar" in oa.get("paths", {}))
ok("openapi declara procedencias", "/api/v1/procedencias/{uid}" in oa.get("paths", {}))

s, r = get("/api/v1/buscar?q=prescripcion+adquisitiva&limite=5")
ok("busqueda encuentra", r.get("hallado") and r.get("total", 0) > 0, str(r)[:120])
if r.get("resultados"):
    p = r["resultados"][0]
    ok("cada resultado trae cita citable",
       bool(p.get("cita", {}).get("fuente_url")) and bool(p.get("cita", {}).get("uid")))
    ok("cada resultado declara confianza del texto", "confianza_texto" in p)
    ok("vigente se preserva (null = NO MEDIDO)", "vigente" in p)
    ok("cada resultado trae sus procedencias",
       (p["cita"].get("procedencias") or 0) >= 1
       and bool((p["cita"].get("fuentes") or [{}])[0].get("fuente_url")),
       str(p["cita"].get("procedencias")))
    crudo = urllib.request.urlopen(BASE + "/api/v1/buscar?q=prescripcion&limite=1",
                                   timeout=30).read().decode()
    ok("null viaja como null en el JSON",
       '"vigente": null' in crudo or '"vigente":null' in crudo,
       "el serializador podria estar convirtiendo null en otra cosa")

s, r = get("/api/v1/buscar?q=zzqxwvkjnoexiste")
ok("cero resultados dice hallado=false", r.get("hallado") is False)
ok("cero resultados trae advertencia", bool(r.get("advertencia")))
ok("la advertencia prohibe inferir inexistencia", "NO inferir" in (r.get("advertencia") or ""))

s, r = get("/api/v1/buscar?q=casacion&sala=Sala+Penal&limite=5")
salas = {x.get("sala") for x in r.get("resultados", [])}
ok("el filtro por sala filtra de verdad", r.get("hallado") and salas <= {"Sala Penal"}, str(salas))

s, r = get("/api/v1/buscar?q=casacion&jurisdiccion=departamental&limite=5")
jur = {x["cita"].get("jurisdiccion") for x in r.get("resultados", [])}
ok("el filtro por jurisdiccion filtra", jur <= {"departamental"}, str(jur))

s, r = get("/api/v1/agente/consultar?q=beneficios+sociales&presupuesto=3000")
gastado = sum(len(x.get("texto") or "") for x in r.get("resultados", []))
ok("el presupuesto se respeta", gastado <= 3000, str(gastado) + " > 3000")
ok("consultar incluye instrucciones", len(r.get("instrucciones", [])) >= 4)
ok("consultar incluye el alcance", "NO_cubre" in (r.get("alcance") or {}))

uid = None
s, r = get("/api/v1/buscar?q=prescripcion&limite=1")
if r.get("resultados"):
    uid = r["resultados"][0]["uid"]
if uid:
    s, d = get("/api/v1/documento/" + urllib.parse.quote(uid))
    ok("documento por uid estable", s == 200 and d.get("uid") == uid)
    ok("documento trae texto completo", len(d.get("texto") or "") > 500)
    ok("documento trae su cita", bool(d.get("cita", {}).get("fuente_url")))
    ok("documento trae sus procedencias con sha256",
       isinstance(d.get("procedencias"), list) and len(d["procedencias"]) >= 1
       and len(d["procedencias"][0].get("sha256") or "") == 64,
       str(d.get("procedencias"))[:120])

try:
    get("/api/v1/documento/no-existe-nada-123")
    ok("documento inexistente da 404", False, "devolvio 200")
except urllib.error.HTTPError as e:
    ok("documento inexistente da 404", e.code == 404, "codigo " + str(e.code))

# --- Procedencias. El caso decisivo: un documento con varias entradas de indice tiene que
# --- devolver TODAS. Si la API vuelve a mandar una sola, esto da rojo.
s, m = get("/api/v1/procedencias?limite=5")
ok("la API lista los documentos con varias fuentes",
   m.get("medido") is True and (m.get("total") or 0) > 0, str(m)[:120])
ok("y aclara que varias fuentes NO es un duplicado del corpus",
   "una sola vez" in (m.get("nota") or ""))
if m.get("documentos"):
    peor = m["documentos"][0]
    s, pr = get("/api/v1/procedencias/" + urllib.parse.quote(peor["uid"]))
    ok("procedencias devuelve TODAS las fuentes del documento",
       pr.get("procedencias") == peor["procedencias"] and len(pr.get("fuentes") or []) == peor["procedencias"],
       str(peor["procedencias"]) + " declaradas vs " + str(len(pr.get("fuentes") or [])))
    ok("cada fuente trae url oficial, archivo y sha256",
       all(f.get("fuente_url") and f.get("archivo") and len(f.get("sha256") or "") == 64
           for f in (pr.get("fuentes") or [])))
    ok("un documento con varias fuentes lo ADVIERTE",
       "citar todas" in (pr.get("advertencia") or "").lower(), str(pr.get("advertencia")))
    s, d = get("/api/v1/documento/" + urllib.parse.quote(peor["uid"]))
    ok("y el documento advierte lo mismo en su cita",
       (d["cita"].get("procedencias") or 0) == peor["procedencias"]
       and bool(d["cita"].get("advertencia_procedencia")))

try:
    get("/api/v1/procedencias/no-existe-nada-123")
    ok("procedencias de un uid inexistente da 404", False, "devolvio 200")
except urllib.error.HTTPError as e:
    ok("procedencias de un uid inexistente da 404", e.code == 404, "codigo " + str(e.code))

s, c = get("/api/v1/catalogos")
ok("catalogos trae jurisdicciones y materias",
   len(c.get("jurisdicciones", [])) >= 1 and len(c.get("materias", [])) >= 1)
ok("catalogos declara las fuentes", len(c.get("fuentes", [])) >= 2)

# Consultas que rompen el parser de FTS5 si no se citan los tokens.
for q in ("AS/0122/2026", "Art. 17.I", 'ley "007"', "casacion OR", "NEAR(", "*", '"'):
    try:
        s, r = get("/api/v1/buscar?q=" + urllib.parse.quote(q))
        ok("consulta hostil no rompe: " + repr(q), s == 200 and "resultados" in r)
    except Exception as e:
        ok("consulta hostil no rompe: " + repr(q), False, type(e).__name__)

print()
if fallos:
    print("ROJO: fallaron " + str(len(fallos)) + " -> " + ", ".join(fallos))
    raise SystemExit(1)
print("VERDE: la API cumple el contrato que un agente necesita")
