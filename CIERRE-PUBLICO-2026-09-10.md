# CIERRE DEL ACCESO PÚBLICO · hecho y verificado

**Orden:** Abraham, 2026-09-10 · *"Cerrá el acceso público hasta decidir la anonimización"*
**Ejecutado:** 2026-09-10 06:29 UTC · **Verificado:** 06:31 UTC

---

## §1 · Qué se hizo

Se reemplazó el vhost de nginx por uno que devuelve **503** en toda ruta. **Nada más se tocó.**

```
nginx: configuration file /etc/nginx/nginx.conf test is successful
RELOAD_OK
nginx active · corpus-api active
```

**Backup antes de tocar:** `/etc/nginx/conf.d/corpus-legal.conf.antes-del-cierre-privacidad`, md5 `a8dd458aebf7457024056cc11efb3774`.

**Cerrar no es borrar.** La base `rag-abogacia-v7.db` intacta, `/var/www/corpus` intacto, `corpus-api` sigue corriendo. Reversible en un comando:

```bash
sudo cp /etc/nginx/conf.d/corpus-legal.conf.antes-del-cierre-privacidad \
        /etc/nginx/conf.d/corpus-legal.conf \
  && sudo nginx -t && sudo systemctl reload nginx
```

## Por qué se cerró TODO y no solo `/buscar`

**`/texto?uid=&nro=` devuelve el documento completo.** Cerrar la búsqueda y dejar la lectura abierta habría sido un guard que no protege lo que dice proteger: con un `uid` (que aparece en cualquier resultado ya cacheado o indexado por un buscador) se sigue leyendo la causa entera.

---

## §2 · Verificación, con salida cruda

`instrumentos/falsador_cierre_publico.py`:

```
    503     228 B  /
    503     228 B  /index.html
    503     228 B  /estado
    503     228 B  /estado.html
    503     228 B  /estado-del-corpus
    503     228 B  /censo
    503     228 B  /verificar
    503     228 B  /buscar?q=Mamani
    503     228 B  /buscar?q=asistencia+familiar
    503     228 B  /texto?uid=jur-tar-auto-supremo-as-0099-2013-2013-e6c79f3b&nro=1
    503     228 B  /openapi.json
    503     228 B  /agente/manifiesto

CONTROL POSITIVO
  servicios en la VM: ['active', 'active']
  vivo por dentro: True

VERDE: 12 rutas barridas, cero nombres, cero datos servidos
```

### El control positivo, y por qué el falsador no sirve sin él

**Si la VM estuviera caída, las 12 rutas fallarían y el falsador diría "cerrado" con toda razón aparente.** Un 503 en todo se ve **igual** que una VM muerta. Por eso el instrumento exige que `nginx` y `corpus-api` sigan `active` verificado **por SSH** antes de afirmar "cerrado": sin eso, el veredicto sería *"no llegué"* y no *"está cerrado"*, que son cosas distintas.

Además el falsador sondea **seis apellidos comunes** y busca marcadores de datos (`total_pasajes`, `resultados`, `uid`). **Cero apariciones en 12 rutas.**

### Antes y después, medido

| | Antes | Ahora |
|---|---|---|
| `/buscar?q=Mamani` | **1.232 pasajes**, primer resultado con **las dos partes nombradas** en una causa de violación de un menor | **503**, 228 bytes |
| `/buscar?q=asistencia+familiar` | 184 pasajes en 10,26 ms | **503** |
| `/` (frontend) | 38.887 bytes | **503** |
| `/estado` | conteos completos | **503** |

---

## §3 · UN HUECO QUE EL CIERRE DE NGINX NO TAPA

Al verificar apareció esto, y no lo iba a buscar:

```
$ ss -tlnp
LISTEN 0 5    0.0.0.0:8080   users:(("python3",pid=724))
LISTEN 0 511  0.0.0.0:80     users:(("nginx",...))
```

**`corpus-api` escucha en `0.0.0.0:8080`, no en `127.0.0.1`.** Confirmado en el fuente:

```python
ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
```

**Qué sí medí:** desde internet **no se llega**. `http://150448fcc6.abacusai.cloud:8080/estado` devuelve **522** (Cloudflare: timeout al origen), y por HTTPS falla el handshake. El ingress solo proxea el 80/443, así que **el cierre público es efectivo**.

**Qué NO medí, y va como riesgo abierto:** si algo dentro de la red de la VM alcanza el 8080, el 503 de nginx **no lo protege**, porque le pega al backend directo. Es defensa en profundidad que hoy no existe.

**El arreglo cuesta una línea** (`("127.0.0.1", PORT)`) más un reinicio del servicio. **No lo hice**: Abraham pidió cerrar el acceso público y eso está hecho y verificado; tocar el bind del backend es un cambio de producción que no pidió, y quiero que lo decida sabiendo el dato.

---

## §4 · Trampa del entorno cazada, otra vez la misma

Mi primera verificación fue un bucle:

```bash
for R in / /buscar /estado ...; do curl ... "https://...$R"; done
```

Devolvió **siete 503** y el `printf` salió **vacío**: el shell del gateway se comió `$R`, así que **curl consultó siete veces la misma URL**. Habría declarado 7 rutas cerradas midiendo una.

Lo cacé porque el nombre de la ruta no se imprimió. Es la **tercera vez** que el mismo defecto aparece en esta campaña (los años de la Gaceta, los paquetes de apt, y ahora esto). Por eso el falsador definitivo es un script commiteado con las rutas en una lista de Python, no un bucle de shell.

---

## §5 · Lo que sigue abierto, y es de Abraham

1. **La anonimización.** El corpus **sigue teniendo** los nombres: solo dejó de servirlos. Opciones, sin medir cuál prefiere: reemplazar nombres de personas naturales por iniciales en el texto indexado, dejar el crudo intacto y anonimizar solo el índice, o exigir login y aceptar el riesgo por escrito.
2. **Qué hacer con la jurisprudencia** (5.030 Autos Supremos): es la fuente con nombres. La normativa (1.034 + 15) **no tiene partes** y podría reabrirse sola.
3. **El bind en `0.0.0.0`** del §3.
4. **Si algo quedó cacheado afuera.** No medí si un buscador indexo páginas del corpus antes del cierre. Cerrar hoy no borra lo que otro ya copió.
