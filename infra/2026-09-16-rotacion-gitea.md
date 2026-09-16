# Password admin de Gitea rotada y medida

**2026-09-16, 15:22 UTC.** Ordenado por Abraham. Ejecutado por Brain en la VM
`corpus-vm.icca-engine.com`.

## Por que habia que rotarla

La password `mudh-brain-2026` del unico usuario admin de Gitea (`brain`) **viajo
en claro por el buzon nexus compartido** (mensajes 198-200), que leen Tachi y
Sol. Un secreto que paso por un canal compartido esta comprometido aunque nadie
lo haya usado: **la exposicion es el hecho, el uso es una hipotesis.** Y la
encontre yo mismo verificando el trabajo de Tachi, no me la reporto nadie.

## Lo medido

Instrumento: [`rotar-password-gitea.sh`](rotar-password-gitea.sh), commiteado
tal como corrio.

| chequeo | esperado | medido |
|---|---|---|
| 1. CONTROL POSITIVO: la vieja anda **antes** de rotar | 200 | **200** |
| 2. rotacion | `password has been successfully updated!` | idem |
| 3. la VIEJA despues de rotar | 401 | **401** |
| 4. la NUEVA | 200 | **200** |
| 5. CONTROL NEGATIVO: una password inventada | 401 | **401** |

**Veredicto: VERDE, exit 0.**

Los chequeos 1 y 5 son los que hacen que esto no sea teatro. Sin el **1**, si la
password ya hubiera estado rota, los 401 del paso 3 serian un verde vacio y el
script aborta antes de tocar nada. Sin el **5**, si la API no autenticara nada,
los 200 no probarian que la credencial sirve. El 401 de la vieja se remidio
despues **desde una medicion aparte**, no reusando la de este script.

La nueva quedo en `/home/ubuntu/.gitea-admin-brain` con permisos `600`
(verificado con `ls -l`) y se le paso a Abraham por su canal privado. **No esta
en este repo, ni en el buzon nexus, ni en ningun Doc.** El error que se corrige
hoy no se repite en el acto de corregirlo.

## Lo que una rotacion de password NO mata, y por eso se midio aparte

Una password rotada **no revoca** tokens de API, llaves SSH ni sesiones. Si
quedara cualquiera de las tres, el acceso seguiria vivo y la rotacion no serviria
de nada. Medido por la API de Gitea:

| superficie | medido |
|---|---|
| tokens de API de `brain` | `[]` |
| llaves SSH de `brain` | `[]` |
| control del instrumento: `GET /user` | devuelve el usuario, o sea que el `[]` es real |

Ese control positivo importa: **un `[]` puede ser "no hay ninguno" o "la consulta
no llego"**, y son cosas distintas. Como la misma credencial en la misma corrida
si trajo datos del usuario y del repo, el `[]` es un cero medido.

## Un verde falso MIO, cazado en el camino

Mi primer medidor de tokens consultaba la base con `sqlite3`. **`sqlite3` no esta
instalado en la VM**, y mi script imprimia esto:

```
sudo: sqlite3: command not found
(vacio = ninguno)
```

Ese `(vacio = ninguno)` era un `echo` incondicional escrito por mi mano **debajo**
del error. Si lo hubiera leido rapido, habria declarado "cero tokens" sobre una
consulta que nunca corrio. Es el mismo patron del `grep -c` que ya tengo
documentado: **la ausencia de salida no es la ausencia del hecho.** Descarte esa
corrida y la rehice por la API, con control positivo adentro.

## Superficie que sigue abierta, y NO la toque

`gitea` escucha en dos puertos:

```
LISTEN 127.0.0.1:3000   <- HTTP, cerrado a loopback (arreglado el 2026-09-16)
LISTEN         *:2222   <- SSH de git, en TODAS las interfaces
```

Y la politica de `iptables` es `-P INPUT ACCEPT`, o sea que **no hay regla que
filtre el 2222**. Hoy el riesgo real es bajo porque las llaves SSH de Gitea son
`[]`: no hay con que autenticarse. Pero es una superficie expuesta que depende de
que esa lista siga vacia, y eso es una condicion que nadie vigila.

**No lo cambie**: cerrar el 2222 puede cortar clones por SSH y esa es una
decision de Abraham, no mia. Queda anotado como pendiente con su medicion.

## NO MEDIDO

- **Sesiones web abiertas.** No las pude contar (era la consulta que necesitaba
  `sqlite3`) y la API no expone un listado de sesiones. Si habia una sesion de
  navegador viva, la rotacion **no** la corta. No lo declaro cubierto.
- Si alguien uso la credencial expuesta entre los mensajes 198-200 y hoy. Los
  logs de Gitea no se auditaron para eso.
- El `2222` desde una IP externa real: mire la politica de `iptables` y el bind,
  no intente la conexion desde afuera.
