"""Censa el universo REAL de jurisprudencia de GENESIS para un departamento.

**Por que existe, con el numero que lo obligo.** El corpus tiene 2.862 resoluciones y ese numero
venia de nuestro propio archivo, no de la fuente. Medido hoy contra `/catalogos/gestiones`:

```plain
gestiones que la API declara: 26 -> [2026 ... 2001]
las que bajamos:              12 -> 2015-2026
NUNCA CONSULTADAS:            14 -> 2001-2014
```

Y una prueba puntual antes de escribir esto: `Sala Civil 1 / 2012 / Auto Supremo` devolvio **535
resoluciones, 37 de Tarija**. O sea que hay material en las gestiones que nunca se pidieron, y el
"corpus completo 2015-2026" era completo **respecto de lo que preguntamos**, no de lo que existe.

Es el mismo agujero que se cerro en la Gaceta esta noche: **el censo tiene que venir de la
fuente**. Ahi eran 247 documentos en la carpeta equivocada; aca son 14 gestiones que nadie pidio.

**Cuatro decisiones con su motivo:**

1. **Recorre TODAS las gestiones del catalogo, TODAS las salas y los TRES tipos.** La primera
   corrida de este proyecto uso solo `idTipoRes=1` y bajo un tercio del universo creyendo que era
   todo; ese error ya esta pagado y no se repite.
2. **Escribe checkpoint por combinacion.** 26x15x3 = 1.170 llamadas: si se corta a la mitad, se
   reanuda en vez de empezar de cero.
3. **Un error NO se cuenta como cero.** Cada combinacion que falla queda declarada, y el resumen
   dice si el censo es un total o un minimo. Un timeout leido como "no hay nada" es exactamente
   como se firma un corpus incompleto.
4. **Solo censa: no baja PDFs ni OCRea.** El descargador es `genesis_bajar.py` y ya funciona; lo
   que faltaba era saber **cuanto** hay que bajar.

Uso:

```bash
python3 pipeline/censar_genesis.py --departamento Tarija --salida censo-genesis.jsonl
```
"""
import argparse
import json
import os
import time
import urllib.error
import urllib.request

BASE = "https://apigenesis.tsj.bo/api/v1"
# Credencial del SPA publico del TSJ, la misma que usa genesis_bajar.py.
H = {"username": "buscadorgenesis",
     "apikey": "CiAYFxnN4GwYgtDv+0jo8MSm1VuTZ53ah8aJ2L8GkgI=",
     "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}


def pedir(url, cuerpo=None, intentos=3):
    """Devuelve (status, bytes). El 'ERR' es explicito: nunca se confunde con una lista vacia."""
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    ultimo = ""
    for i in range(intentos):
        req = urllib.request.Request(url, data=datos, headers=H,
                                     method="POST" if cuerpo is not None else "GET")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()[:200]
        except Exception as e:
            ultimo = type(e).__name__ + ": " + str(e)[:60]
            time.sleep(3 * (i + 1))
    return "ERR", ultimo.encode()


def lista(b):
    d = json.loads(b)
    if isinstance(d, list):
        return d
    return d.get("data", []) if isinstance(d, dict) else []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--departamento", default="Tarija")
    ap.add_argument("--salida", required=True)
    ap.add_argument("--gestiones", default="", help="coma separadas; vacio = todas las del catalogo")
    ap.add_argument("--tipos", default="1,2,3")
    a = ap.parse_args()

    s, b = pedir(BASE + "/catalogos/gestiones")
    if s != 200:
        print("ROJO: /catalogos/gestiones dio", s, b[:120])
        return 2
    gestiones = [int(x) for x in lista(b)]
    if a.gestiones:
        pedidas = [int(x) for x in a.gestiones.split(",") if x.strip()]
        gestiones = [g for g in gestiones if g in pedidas]

    s, b = pedir(BASE + "/catalogos/salas")
    salas = lista(b) if s == 200 else []
    s, b = pedir(BASE + "/catalogos/tipos_resoluciones")
    nombres_tipo = {t["id"]: t["nombre"] for t in (lista(b) if s == 200 else [])}
    tipos = [int(x) for x in a.tipos.split(",") if x.strip()]

    print("gestiones:", len(gestiones), "| salas:", len(salas), "| tipos:", len(tipos),
          "| combinaciones:", len(gestiones) * len(salas) * len(tipos), flush=True)

    # Checkpoint: se relee lo ya hecho para poder reanudar sin repetir 1.170 llamadas.
    hechas = set()
    if os.path.exists(a.salida):
        for linea in open(a.salida, encoding="utf-8", errors="replace"):
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            try:
                d = json.loads(linea)
                hechas.add((d["gestion"], d["id_sala"], d["id_tipo"]))
            except Exception:
                continue
        print("reanudando: ya habia", len(hechas), "combinaciones", flush=True)

    objetivo = a.departamento.upper()
    total_dep, total_todos, errores = 0, 0, []
    por_gestion = {}
    with open(a.salida, "a", encoding="utf-8") as f:
        if not hechas:
            f.write("# censo de GENESIS " + a.departamento + " " +
                    time.strftime("%Y-%m-%dT%H:%M:%S") + "\n")
        for g in gestiones:
            en_gestion = 0
            for sala in salas:
                for tipo in tipos:
                    clave = (g, sala["id"], tipo)
                    if clave in hechas:
                        continue
                    st, cuerpo = pedir(BASE + "/resoluciones/busqueda_por_gestion",
                                       {"idSala": sala["id"], "gestion": g, "idTipoRes": tipo})
                    if st != 200:
                        # Guard 3: un error NO es un cero. Queda declarado.
                        errores.append({"gestion": g, "id_sala": sala["id"], "id_tipo": tipo,
                                        "error": str(st)})
                        f.write(json.dumps({"gestion": g, "id_sala": sala["id"],
                                            "id_tipo": tipo, "error": str(st),
                                            "ids": None}, ensure_ascii=False) + "\n")
                        f.flush()
                        continue
                    filas = lista(cuerpo)
                    mios = [x for x in filas
                            if str(x.get("departamento") or "").upper().startswith(objetivo)]
                    total_todos += len(filas)
                    total_dep += len(mios)
                    en_gestion += len(mios)
                    f.write(json.dumps({
                        "gestion": g, "id_sala": sala["id"], "sala": sala["nombre"],
                        "id_tipo": tipo, "tipo": nombres_tipo.get(tipo, "?"),
                        "total_sala": len(filas), "del_departamento": len(mios),
                        "ids": [x.get("id") for x in mios],
                        "nros": [x.get("nro_resolucion") for x in mios],
                    }, ensure_ascii=False) + "\n")
                    f.flush()
            por_gestion[g] = en_gestion
            print("  gestion %s -> %s de %s" % (g, en_gestion, a.departamento), flush=True)

    print()
    print("CENSO", a.departamento, ":", total_dep, "resoluciones | universo consultado:",
          total_todos)
    print("por gestion:", json.dumps(por_gestion))
    print("combinaciones con error:", len(errores))
    if errores:
        print("ATENCION: el censo es un MINIMO, no un total. Errores:",
              json.dumps(errores[:8], ensure_ascii=False))
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
