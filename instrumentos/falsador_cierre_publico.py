#!/usr/bin/env python3
"""Falsador del cierre publico del corpus. NO escribe nada.

QUE PRUEBA: que ninguna ruta publica devuelve datos del corpus, y que no aparece
ningun nombre de parte en ninguna respuesta.

POR QUE TIENE CONTROL POSITIVO, y es la parte que se suele olvidar: si la VM
estuviera CAIDA, todas las rutas fallarian y este falsador daria "cerrado" con
toda razon aparente. Un 503 en todo se ve IGUAL que una VM muerta. Asi que el
script exige que el servicio siga VIVO por dentro (nginx y corpus-api activos,
verificado por SSH) para poder afirmar "cerrado" en vez de "no llegue".

Sin ese control, cerrar y romper serian indistinguibles.

Uso:
  python3 falsador_cierre_publico.py            # solo el barrido HTTP
  python3 falsador_cierre_publico.py --con-ssh  # + control positivo por SSH
"""
import json
import subprocess
import sys
import urllib.error
import urllib.request

BASE = "https://150448fcc6.abacusai.cloud"
UID_CONOCIDO = "jur-tar-auto-supremo-as-0099-2013-2013-e6c79f3b"

# Rutas que el vhost anterior servia, mas las estaticas y las de agente.
RUTAS = [
    "/",
    "/index.html",
    "/estado",
    "/estado.html",
    "/estado-del-corpus",
    "/censo",
    "/verificar",
    "/buscar?q=Mamani",
    "/buscar?q=asistencia+familiar",
    f"/texto?uid={UID_CONOCIDO}&nro=1",
    "/openapi.json",
    "/agente/manifiesto",
]

# Apellidos comunes en Bolivia. Si alguno aparece en una respuesta, hay fuga.
# NO son datos personales: son apellidos frecuentes usados como sonda.
SONDAS = ("Mamani", "Quispe", "Choque", "Condori", "Flores", "Vargas")

# Marcadores de que el corpus esta sirviendo datos de verdad.
MARCADORES = ("total_pasajes", "resultados", "documentos", "pasajes", "uid")


def pedir(ruta: str) -> tuple[object, int, str]:
    req = urllib.request.Request(BASE + ruta, headers={"User-Agent": "falsador"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            b = r.read()
            return r.status, len(b), b.decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        b = e.read()
        return e.code, len(b), b.decode("utf-8", "replace")
    except Exception as e:
        return "ERR:" + type(e).__name__, 0, str(e)[:120]


def main() -> int:
    filas = []
    fugas = []
    print("=== barrido de rutas publicas ===")
    for ruta in RUTAS:
        st, n, cuerpo = pedir(ruta)
        sondas = [s for s in SONDAS if s in cuerpo]
        marc = [m for m in MARCADORES if m in cuerpo]
        abierto = (st == 200 and bool(marc))
        if sondas or abierto:
            fugas.append({"ruta": ruta, "status": st,
                          "nombres": sondas, "marcadores": marc})
        filas.append({"ruta": ruta, "status": st, "bytes": n,
                      "nombres_hallados": sondas, "sirve_datos": abierto})
        print(f"  {str(st):>5}  {n:>6} B  {ruta}"
              + (f"   <-- NOMBRES: {sondas}" if sondas else "")
              + ("   <-- SIRVE DATOS" if abierto else ""))

    print("\n=== CONTROL POSITIVO ===")
    if "--con-ssh" in sys.argv:
        # Sin esto, "todo da 503" es indistinguible de "la VM esta muerta".
        try:
            p = subprocess.run(
                ["bash", "/workspace/bin/vm-corpus.sh",
                 "systemctl is-active nginx corpus-api"],
                capture_output=True, timeout=120)
            salida = p.stdout.decode("utf-8", "replace")
            vivo = salida.count("active") >= 2
            print(f"  servicios en la VM: {salida.split()}")
            print(f"  vivo por dentro: {vivo}")
            if not vivo:
                print("  ROJO: el servicio NO esta vivo. Esto no es un cierre,"
                      " es una caida, y son cosas distintas.")
                return 3
        except Exception as e:
            print(f"  NO MEDIDO: no pude verificar por SSH ({type(e).__name__})")
            print("  El veredicto de abajo dice 'no llegue', no 'esta cerrado'.")
    else:
        print("  NO MEDIDO: correr con --con-ssh para distinguir"
              " 'cerrado' de 'caido'.")

    print("\n" + "=" * 60)
    res = {"rutas": len(filas), "fugas": len(fugas), "detalle": filas}
    if fugas:
        print("ROJO: hay rutas que exponen datos o nombres:")
        print(json.dumps(fugas, ensure_ascii=False, indent=1))
        return 1
    print(f"VERDE: {len(filas)} rutas barridas, cero nombres, cero datos servidos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
