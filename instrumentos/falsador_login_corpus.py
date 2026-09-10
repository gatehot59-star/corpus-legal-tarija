#!/usr/bin/env python3
"""Falsador del acceso CON LOGIN al corpus. Solo stdlib.

--------------------------------------------------------------------------------
POR QUE UN FALSADOR Y NO UN curl A MANO
--------------------------------------------------------------------------------
El falsador del cierre anterior (`falsador_cierre_publico.py`) tenia que probar
UNA cosa: que todo diera 503. Este tiene que probar DOS, y son opuestas:

  A. SIN credenciales -> 401 en todas las rutas, y CERO nombres en el cuerpo.
  B. CON credenciales -> 200 y datos servidos.

**Si solo se prueba (A), un login roto que devuelve 401 a todo el mundo se ve
igual que un login que funciona.** Eso ya paso en este proyecto con el 503: un
503 en todo se ve igual que una VM caida, y hubo que agregar control positivo por
SSH. Aca el control positivo es (B): si con credenciales validas NO entra, el
login no esta protegiendo, esta ROTO, y son cosas distintas.

Y una tercera, que es la que se olvida: **con clave INCORRECTA tiene que seguir
dando 401.** Un `auth_basic` mal configurado puede aceptar cualquier cosa.

--------------------------------------------------------------------------------
COMO SE VERIFICO ESTE INSTRUMENTO
--------------------------------------------------------------------------------
No pude correrlo contra la VM: el taller donde se escribio no tiene red. Se
verifico su LOGICA reemplazando `pedir()` por un doble y corriendo cuatro
escenarios. Resultado medido:

  todo 401 sin credencial, 200 con credencial ...... rc=0, VERDE
  SIN LOGIN: devuelve datos igual .................. rc=1, DATOS-SIN-LOGIN,
                                                     NOMBRES-SIN-LOGIN
  LOGIN ROTO: 401 tambien con credencial ........... rc=1, LOGIN-ROTO
  CLAVE MALA pasa igual ............................ rc=1, CLAVE-MALA-PASA

Eso prueba que el instrumento DISCRIMINA. NO prueba nada sobre el corpus.

Uso:
    python3 falsador_login_corpus.py --usuario abraham --clave 'LA-CLAVE'
    python3 falsador_login_corpus.py            # solo la mitad (A), y lo dice

Salida: exit 0 verde, exit 1 rojo. En rojo imprime ETIQUETAS_ROJAS.
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.error
import urllib.request

BASE = "https://150448fcc6.abacusai.cloud"

# Las rutas van en una LISTA DE PYTHON y no en un bucle de shell. Motivo medido:
# la primera verificacion del cierre uso `for R in / /buscar ...; do curl "$R"`,
# el shell del gateway se comio la variable, y curl consulto SIETE VECES la misma
# URL. Habria declarado 7 rutas cerradas midiendo una.
RUTAS = (
    "/", "/index.html", "/estado", "/censo", "/verificar",
    "/buscar?q=Mamani", "/buscar?q=asistencia+familiar",
    "/texto?uid=jur-tar-auto-supremo-as-0099-2013-2013-e6c79f3b&nro=1",
    "/openapi.json", "/agente/manifiesto",
)
# Rutas que a proposito NO piden login. Si estas dieran 401, el vhost esta mal.
RUTAS_ABIERTAS = ("/robots.txt", "/_salud_borde")

APELLIDOS = ("Mamani", "Quispe", "Choque", "Villca", "Gutierrez", "Vargas")
MARCADORES = ("total_pasajes", "resultados", "uid", "pasaje")


def pedir(ruta: str, usuario: str | None = None, clave: str | None = None,
          timeout: int = 20) -> tuple[int, bytes]:
    req = urllib.request.Request(
        BASE + ruta, headers={"User-Agent": "falsador-login-corpus/1.0"})
    if usuario:
        cred = base64.b64encode(f"{usuario}:{clave}".encode()).decode()
        req.add_header("Authorization", f"Basic {cred}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:  # noqa: BLE001
        # Se distingue "no llegue" de "me rechazaron". No son lo mismo, y
        # confundirlos seria declarar cerrado lo que no se pudo medir.
        return -1, f"{type(e).__name__}: {e}".encode()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--usuario")
    ap.add_argument("--clave")
    a = ap.parse_args()

    rojos: list[str] = []
    etiquetas: set[str] = set()

    print("=== A. SIN credenciales: 401 y cero datos ===")
    for ruta in RUTAS:
        cod, cuerpo = pedir(ruta)
        txt = cuerpo.decode("utf-8", "replace")
        nombres = [n for n in APELLIDOS if n.lower() in txt.lower()]
        datos = [m for m in MARCADORES if m in txt]
        estado = "OK  " if cod == 401 else "ROJO"
        if cod == -1:
            estado = "??? "
            rojos.append(f"{ruta}: no se pudo medir ({txt[:60]})")
            etiquetas.add("NO-LLEGUE")
        elif cod != 401:
            rojos.append(f"{ruta}: dio {cod}, se esperaba 401")
            etiquetas.add("SIN-LOGIN-NO-401")
        if nombres:
            rojos.append(f"{ruta}: APARECEN NOMBRES {nombres}")
            etiquetas.add("NOMBRES-SIN-LOGIN")
        if datos:
            rojos.append(f"{ruta}: sirve datos {datos}")
            etiquetas.add("DATOS-SIN-LOGIN")
        print(f"  {estado} {cod:>4}  {len(cuerpo):>6} B  {ruta}")

    print("\n=== A2. Las rutas que a proposito NO piden login ===")
    for ruta in RUTAS_ABIERTAS:
        cod, cuerpo = pedir(ruta)
        ok = cod == 200
        if not ok:
            rojos.append(f"{ruta}: dio {cod}, se esperaba 200 (es abierta)")
            etiquetas.add("ABIERTA-BLOQUEADA")
        txt = cuerpo.decode("utf-8", "replace")
        if any(n.lower() in txt.lower() for n in APELLIDOS):
            rojos.append(f"{ruta}: una ruta abierta trae nombres")
            etiquetas.add("NOMBRES-SIN-LOGIN")
        print(f"  {'OK  ' if ok else 'ROJO'} {cod:>4}  {len(cuerpo):>6} B  {ruta}")

    print("\n=== B. CONTROL POSITIVO: con credenciales SI entra ===")
    if not a.usuario:
        print("  SIN MEDIR: no se pasaron credenciales.")
        print("  ATENCION: sin esta mitad, un login ROTO que devuelve 401 a")
        print("  todo el mundo se ve IGUAL que un login que funciona. El")
        print("  veredicto de abajo es PARCIAL y se declara como tal.")
        etiquetas.add("CONTROL-POSITIVO-AUSENTE")
    else:
        cod, cuerpo = pedir("/estado", a.usuario, a.clave)
        txt = cuerpo.decode("utf-8", "replace")
        if cod != 200:
            rojos.append(f"/estado con credenciales dio {cod}, no 200: el login "
                         "no protege, esta ROTO")
            etiquetas.add("LOGIN-ROTO")
            print(f"  ROJO {cod} con credenciales validas")
        else:
            try:
                docs = json.loads(txt).get("documentos")
            except Exception:
                docs = None
            print(f"  OK   200 con credenciales, {len(cuerpo)} B, "
                  f"documentos={docs}")
            if not any(m in txt for m in MARCADORES) and docs is None:
                rojos.append("/estado autenticado no trajo datos reconocibles")
                etiquetas.add("LOGIN-ROTO")
        # Y una credencial MALA tiene que seguir dando 401.
        cod2, _ = pedir("/estado", a.usuario, (a.clave or "") + "-mal")
        if cod2 != 401:
            rojos.append(f"clave incorrecta dio {cod2}, no 401")
            etiquetas.add("CLAVE-MALA-PASA")
        print(f"  {'OK  ' if cod2 == 401 else 'ROJO'} {cod2} con clave incorrecta")

    print("\n" + "=" * 62)
    if rojos:
        print(f"ROJO: {len(rojos)} problema(s)")
        for r in rojos:
            print("  " + r)
        print("ETIQUETAS_ROJAS: " + " ".join(sorted(etiquetas)))
        return 1
    if "CONTROL-POSITIVO-AUSENTE" in etiquetas:
        print("VERDE PARCIAL: nadie entra sin credenciales, pero NO se verifico")
        print("que con credenciales SI se entre. Correr con --usuario/--clave.")
        return 0
    print("VERDE: sin credenciales nadie ve nada; con credenciales el corpus "
          "responde; con clave mala, 401.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
