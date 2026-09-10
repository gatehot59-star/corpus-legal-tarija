# Login del corpus: CORREGIDO y falsado (2026-09-10, 17:45 UTC)

## Que se pidio
Abraham pidio revisar que hizo Tachi despues del mensaje 201 del buzon nexus
("corregi el login"). Medido, no leido de un recibo.

## 1. QUE HIZO TACHI: NADA, y esta medido
- Buzon nexus: `SELECT ... FROM mensajes ORDER BY id DESC` -> el ultimo es el **201**,
  el mio (BRAIN -> Tachi, 2026-09-10T16:33:45Z). **No hay respuesta suya.**
- Ningun archivo de la VM cambio despues de mi propia intervencion:
  - `/etc/nginx/conf.d/corpus-legal.conf` -> mtime 2026-09-10 16:09:48 UTC
  - `/etc/nginx/corpus.htpasswd` -> mtime 2026-09-10 16:12:24 UTC
  - mi mensaje salio 16:33 UTC. **Nada tocado en las 1h27 siguientes.**
- No es una acusacion: es un hecho con hora. Tachi no llego todavia.

## 2. LA CAUSA REAL DEL 401 CON CLAVE VALIDA (la encontre yo, no la habia medido antes)

    /etc/nginx/corpus.htpasswd  =  9 bytes  md5=c389189cead035b635cb92020fa204a1
    contenido: `abraham:`   <- usuario SIN HASH

El archivo tenia el usuario y **nada** despues de los dos puntos. Con eso nginx
rechaza CUALQUIER clave: no habia hash que comparar. No era el grupo del archivo,
ni el usuario de los workers, ni el formato APR1: era el hash inexistente.
Lo que fallo antes fue el metodo, no el diagnostico: los parches inline se
comieron la expansion y escribieron una linea vacia.

## 3. LO APLICADO (script ejecutado, no bloque de chat)
`/tmp/fix-login.sh` subido por base64 y corrido:

    htpasswd ANTES   bytes=9   md5=c389189cead035b635cb92020fa204a1
    metodo: openssl passwd -apr1   (htpasswd de apache2-utils no esta en la VM)
    htpasswd DESPUES bytes=46  md5=d4269020eb87abbfd2bf825b430462a0
    linea: abraham:$apr1$ZaRyUVQb$V...
    chown root:ubuntu / chmod 640   (los workers de nginx corren como `ubuntu`,
                                     medido en `user ubuntu;` de nginx.conf)
    nginx -t  -> syntax is ok / test is successful
    systemctl reload nginx -> reload-ok

## 4. FALSADOR DEL LOGIN: los tres estados, local Y externo

| prueba | local (127.0.0.1, Host real) | externo (https) |
|---|---|---|
| sin credenciales | **401** | **401** |
| clave incorrecta | **401** | **401** |
| clave correcta | **200** | **200** |

Control positivo externo con cuerpo real:

    GET https://corpus-tarija.abacusai.cloud/buscar?q=Mamani  (con credencial)
    {"consulta": "Mamani", "total_pasajes": 1232, "devueltos": 10, "ms": 49.21, ...}

El 401 discrimina: si diera 401 en las tres filas, el instrumento no probaria nada.

- Usuario: `abraham`. La clave NO se commitea: se le pasa a Abraham por chat y se rota.
- Vhost real: `/etc/nginx/conf.d/corpus-legal.conf`,
  `server_name corpus-tarija.abacusai.cloud 150448fcc6.abacusai.cloud ...`
- `auth_basic` cubre el server completo (linea 151-152 de `nginx -T`), no un location.

## 5. ROJO QUE ENCONTRE Y CONTRADICE LO QUE YO MISMO AFIRME AYER

    ss -ltnp  ->  LISTEN 0 5  0.0.0.0:8080  users:(("python3",pid=91707))

Yo declare que el backend habia quedado en `127.0.0.1:8080`. **Es falso ahora:**
escucha en `0.0.0.0`. El proxy_pass de nginx apunta a 127.0.0.1:8080, asi que el
login no se puede saltar desde internet por ese hostname (`curl` al :8080 publico
dio timeout, codigo 000), pero cualquiera dentro de la red de la VM entra sin login.
**NO MEDIDO:** si la red de Abacus expone el 8080 por otra ruta. Pendiente cerrar
el bind y reiniciar el proceso, con la ventana acordada.

## 6. Sigue abierto (de la lista que Tachi no toco)
- 3 tokens admin de Gitea vivos, sin revocar.
- Espejo Gitea `private: False`.
- Emulador huerfano `qemu-system-x86` PID 21526, 49,2% de RAM, +3 dias.
- `sync-gitea.sh` con el PAT en claro.
- Bind del corpus en 0.0.0.0 (punto 5).
