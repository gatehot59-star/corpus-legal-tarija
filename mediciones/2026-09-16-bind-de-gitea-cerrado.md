# El bind que faltaba era el de Gitea (2026-09-16, 10:54 UTC)

Abraham pidio aplicar el parche del bind. Antes de tocar nada medi cual bind
seguia abierto, porque el del corpus ya estaba cerrado desde el 10-sep.

## Lo que estaba abierto, y no era el corpus

    ss -ltn
    LISTEN  127.0.0.1:8080    <- corpus-api, ya en loopback
    LISTEN  0.0.0.0:80        <- nginx, tiene que estar asi
    LISTEN  *:3000            <- GITEA, ABIERTO A TODA LA RED

`/etc/gitea/app.ini` tenia `HTTP_PORT = 3000` y **ningun `HTTP_ADDR`**. Sin esa
clave Gitea escucha en `0.0.0.0` por default. Asi que el espejo del repo estaba
privado y sin tokens desde el 10-sep, pero **su puerto seguia expuesto a
cualquier cosa dentro de la red de la VM**.

## Y un segundo hallazgo: un log que MENTIA

    api.py:293  print("corpus/2 en 0.0.0.0:%d ...")   ...   ThreadingHTTPServer(("127.0.0.1", PORT))

El bind era loopback y **el mensaje de arranque declaraba `0.0.0.0`**. Cualquiera
que leyera el log del servicio concluia que el backend estaba expuesto, o al
reves: si manana alguien lo abre de verdad, el log dice lo mismo y no avisa nada.
Un log que no puede contradecir al codigo no sirve de instrumento.

## Lo aplicado

Script `/tmp/bind.sh`, subido por base64 y ejecutado. Backups antes de tocar:
`/etc/gitea/app.ini.bak-bind-20260916T105426Z` y
`/home/ubuntu/api.py.bak-log-20260916T105426Z`.

    HTTP_ADDR no existia: insertado antes de HTTP_PORT
    12:HTTP_ADDR = 127.0.0.1
    13:HTTP_PORT = 3000

    api.py:293  print("corpus/2 en 127.0.0.1:%d (loopback; nginx expone) ...")

## Despues

    LISTEN  127.0.0.1:3000   pid=201501   <- gitea
    LISTEN  127.0.0.1:8080   pid=201508   <- corpus-api

## FALSADOR, con nginx como control positivo

El punto flojo de "lo cerre" es que un `000` puede significar "cerrado" o
"mi instrumento no llega a ninguna parte". Como **nginx sigue en `0.0.0.0:80`**,
sirve de control: si nginx tampoco responde por la IP privada, la medicion no
discrimina y no concluyo nada.

    IP privada medida: [10.51.4.106]

    CONTROL nginx por IP:80           401   <- llega, o sea que el instrumento SIRVE
    gitea por IP:3000                 conexion-rehusada
    corpus por IP:8080                conexion-rehusada
    --- y por loopback los tres tienen que vivir
    gitea loopback:3000               200
    corpus loopback:8080              200

Y el primer intento de este falsador **no discrimino**: el `awk` se rompio por
el quoting del transporte, la IP salio vacia y los tres dieron `000`, incluido
nginx. Ese resultado se descarto en vez de reportarlo. Un `000` con la IP vacia
no mide un bind, mide una URL mal armada.

## Control positivo de que no rompi nada

    systemctl is-active gitea corpus-api nginx  ->  active / active / active
    gitea por loopback ............ 200
    corpus por loopback ........... 200
    corpus por nginx CON login .... 200
    corpus por nginx SIN login .... 401

El login sigue discriminando, que es lo que importa: reiniciar `corpus-api` podia
romper el `proxy_pass` y dejar el corpus caido detras de un 502.

## NO MEDIDO

- Si la red de Abacus expone esos puertos por alguna ruta que no sea la IP
  privada de la VM. Desde brain-env no llego a la red interna, asi que la
  medicion es DESDE la VM. Es mejor que antes y no es todo.
- El emulador huerfano `qemu-system-x86` sigue consumiendo RAM y espera
  autorizacion. No lo toque.
