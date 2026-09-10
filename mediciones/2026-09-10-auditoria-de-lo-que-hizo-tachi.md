# Lo que hizo Tachi, medido contra la VM y no leido de su recibo (2026-09-10, 22:05 UTC)

Respondio el mensaje 204 al buzon nexus declarando los 4 pedidos hechos.
Verifique los 4 yo mismo. **Tres se sostienen. Uno queda a medias, y encontre
un rojo que su recibo no nombra.**

## 1. Bind del backend: VERDE, y el login no se rompio

    ss -ltn -> LISTEN 0 5  127.0.0.1:8080
    systemctl is-active corpus-api -> active

Era `0.0.0.0:8080` con pid 91707; ahora es loopback con proceso nuevo. Cambio en
`api.py` con backup (`api.py.bak-bind-202609102153`), no a mano sobre el proceso.

El riesgo real de este cambio era romper el `proxy_pass`. Lo falsé desde afuera:

| prueba | externo |
|---|---|
| sin credenciales | 401 |
| clave incorrecta | 401 |
| clave correcta | **200** |

Y con cuerpo real: `total_pasajes: 1232` para `q=Mamani`. El corpus sigue vivo
detras del login.

Su 1a queda **NO MEDIDO y esta bien declarado**: el `:8080` por el hostname de
Cloudflare devuelve 200, pero el `ingress` del tunel solo tiene `ssh://localhost:22`,
asi que ese 200 es del edge y no del backend. No afirmo ni lo contrario.

## 2. Tokens de Gitea: VERDE, falsado con el token viejo

    GET /api/v1/users/brain/tokens          -> []
    Authorization: token 267571a7...0ad3    -> 401

No me quede en la lista vacia: use el token filtrado y ya no autentica.

## 3. Espejo privado: VERDE, falsado sin credenciales

    GET /api/v1/repos/brain/mudh-mobile (anonimo) -> "The target couldn't be found"
    GET /brain/mudh-mobile (anonimo)              -> 404

Un 404 anonimo es la prueba de que es privado; el `private:true` de la respuesta
al PATCH por si solo no lo era.

## 4. Scripts con el secreto: VERDE en filesystem, y su NO MEDIDO se resuelve

Los tres archivos borrados (`/tmp/sync-mudh-gitea.sh`, `gitea-install.sh`,
`gitea-install2.sh`): `ls` da `No such file or directory`.

El dejo como NO MEDIDO si el token quedaba en `.bash_history`. **Lo medi y la
respuesta es que ese archivo NO EXISTE:**

    ls -la /home/ubuntu/.bash_history -> No such file or directory

OJO CON EL METODO: mi primer `grep -c` sobre ese archivo imprimio nada y salio 1,
que es identico a "cero coincidencias". Si me quedaba ahi, declaraba limpio un
archivo que no existe. Es el mismo patron que ya me costo cinco falsos: **un grep
sin match y un archivo ausente son indistinguibles si no se testea la existencia.**

El `sync-gitea.sh` commiteado: busque el token y el nombre del archivo en
`user:gatehot59-star` y los dos dieron 0 resultados. Evidencia **debil**: el indice
de busqueda de GitHub puede atrasarse. No lo declaro cerrado.

## ROJO QUE SU RECIBO NO NOMBRA: la password admin sigue viva y esta filtrada

    curl -u brain:mudh-brain-2026 http://localhost:3000/api/v1/users/brain/tokens -> []

Ese `[]` es la prueba: para devolverlo, **Gitea autentico la password**. Sigue siendo
valida, y viajo en texto claro por el buzon nexus (mensajes 198 y 199) igual que los
tokens que si se revocaron.

Revocar los 3 tokens y dejar la password que **acuña tokens nuevos** cierra la puerta
y deja la llave puesta. Falta rotarla. El propio mensaje 198 decia "rotala en el
primer login" y nadie lo hizo.

## Tambien sigue abierto

- El buzon `nexus.db` guarda el token y la password en texto claro en los mensajes
  198, 199 y 200. Sanearlos es un UPDATE sobre una base compartida: no lo hago sin orden.
- Emulador huerfano `qemu-system-x86` PID 21526, 49,2% de RAM. Es mio y espera autorizacion.
