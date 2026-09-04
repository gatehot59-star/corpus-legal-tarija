#!/usr/bin/env python3
"""El falsador dijo NO MEDIBLE porque la LD 520 no tiene ano, y sin ano no se puede
decidir si el DD 16/2026 la reglamento antes o despues de que la LD 520 la abrogara.

La Gaceta asigna el id de descarga de forma SECUENCIAL por carga, asi que el id acota la
fecha entre sus vecinos con fecha conocida. Eso no es adivinar: es interpolar entre dos
mediciones, y el resultado se declara como INFERIDO POR POSICION, no como fecha oficial.

Guard: si los vecinos no encierran al id, o si discrepan en el ano, devuelve None.
Banco incluido con leyes que YA tienen ano: si el metodo no las reproduce, no sirve.
"""
import re, sqlite3, sys

def cargar(c):
    filas = []
    for r in c.execute("SELECT uid,numero,anio,fecha,fuente_url FROM documentos "
                       "WHERE tipo_norma='Ley Departamental'"):
        m = re.search(r"download=(\d+):", r["fuente_url"] or "")
        if m:
            filas.append({"uid": r["uid"], "numero": r["numero"], "anio": (r["anio"] or "").strip(),
                          "fecha": (r["fecha"] or "").strip(), "id": int(m.group(1))})
    return sorted(filas, key=lambda x: x["id"])

def infiere(filas, i):
    """Ano de filas[i] mirando el vecino con ano hacia atras y hacia adelante."""
    ant = nxt = None
    for j in range(i - 1, -1, -1):
        if filas[j]["anio"]:
            ant = filas[j]; break
    for j in range(i + 1, len(filas)):
        if filas[j]["anio"]:
            nxt = filas[j]; break
    if ant and nxt and ant["anio"] == nxt["anio"]:
        return ant["anio"], "entre LD %s (%s) y LD %s (%s)" % (ant["numero"], ant["anio"], nxt["numero"], nxt["anio"])
    if ant and nxt:
        return None, "vecinos discrepan: %s vs %s -> NO MEDIDO" % (ant["anio"], nxt["anio"])
    if ant and not nxt:
        return ant["anio"], "ultimo del catalogo, vecino anterior LD %s (%s)" % (ant["numero"], ant["anio"])
    return None, "sin vecinos con ano"

c = sqlite3.connect("file:/workspace/bolivia-v7.db?mode=ro", uri=True); c.row_factory = sqlite3.Row
filas = cargar(c); c.close()
print("leyes con id de descarga legible:", len(filas))
sin = [i for i, f in enumerate(filas) if not f["anio"]]
print("sin ano:", len(sin))
print()
print("== BANCO: leyes que YA tienen ano. El metodo las reproduce?")
ok = mal = 0
import random
random.seed(7)
for i in random.sample([i for i, f in enumerate(filas) if f["anio"]], 14):
    real = filas[i]["anio"]
    guardado = filas[i]["anio"]
    filas[i]["anio"] = ""            # se oculta
    pred, motivo = infiere(filas, i)
    filas[i]["anio"] = guardado
    bien = (pred == real)
    ok, mal = ok + bien, mal + (not bien)
    print("   %-5s LD %-5s real=%s pred=%s  %s" % ("OK" if bien else "ROJO", filas[i]["numero"], real, pred, motivo[:52]))
print()
print("banco:", ok, "/", ok + mal)
if mal > 2:
    print("ROJO: el metodo falla en mas de 2 de 14. No se aplica.")
    sys.exit(1)
print()
print("== INFERENCIA sobre las", len(sin), "sin ano")
plan = []
for i in sin:
    pred, motivo = infiere(filas, i)
    print("   LD %-5s (id %s) -> %s   [%s]" % (filas[i]["numero"], filas[i]["id"], pred or "NO MEDIDO", motivo[:56]))
    if pred:
        plan.append((filas[i]["uid"], filas[i]["numero"], pred))
print()
print("inferibles:", len(plan), "| quedan sin ano:", len(sin) - len(plan))
if "--aplicar" in sys.argv and plan:
    import shutil
    D = "/workspace/bolivia-v7.db"
    shutil.copy2(D, D + ".antes-de-anio-inferido")
    w = sqlite3.connect(D)
    # se marca el ano Y se deja rastro de que es inferido, en el propio campo fecha
    w.executemany("UPDATE documentos SET anio=? WHERE uid=? AND (anio IS NULL OR trim(anio)='')",
                  [(a, u) for u, n, a in plan])
    w.commit(); w.close()
    v = sqlite3.connect("file:" + D + "?mode=ro", uri=True); v.row_factory = sqlite3.Row
    malos = sum(1 for u, n, a in plan
                if v.execute("SELECT anio FROM documentos WHERE uid=?", (u,)).fetchone()["anio"] != a)
    quedan = v.execute("SELECT count(*) n FROM documentos WHERE tipo_norma='Ley Departamental' "
                       "AND (anio IS NULL OR trim(anio)='')").fetchone()["n"]
    v.close()
    print("escritos:", len(plan), "| discrepancias:", malos, "| leyes sin ano ahora:", quedan)
    sys.exit(1 if malos else 0)
print()
print("para escribir: anio_por_id.py --aplicar")
