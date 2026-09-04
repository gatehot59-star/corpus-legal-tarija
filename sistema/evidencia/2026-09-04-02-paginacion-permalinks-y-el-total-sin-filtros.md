# Paginación, permalinks y estado en la URL · evidencia cruda

Fecha de la corrida: 2026-09-04. Instrumentos: navegador real (Chromium vía Playwright,
servicio `playwright` del gateway) contra `https://corpus-tarija.abacusai.cloud`, y `curl`
contra la API pública desde brain-env. Nada de esto se corrió contra un doble: el HTML
medido es el que sirve nginx, con md5 comprobado en disco y en el cable.

## Lo desplegado, con su sello

| Artefacto | Antes | Después |
| --- | --- | --- |
| `/var/www/corpus/index.html` | `447a4fd5682ad051b5903ce6f62a9b58` (32.925 B, versión con las dos inyecciones) | `a1c126f8757f7746162023e677ed42e7` (34.776 B) |
| Servido por HTTPS | — | `a1c126f8757f7746162023e677ed42e7`, http=200, 34.776 B |
| `/home/ubuntu/api.py` | `d12b1a59a847541d19885df10fb34c84` | `585447696a1bb3f84c6b21b018abce6e` |
| `corpus-api.service` | active | active tras `systemctl restart` |

El HTML se produjo con `pipeline/parche_paginacion_v5.py`: **15 anclas exactas, cada una
verificada por conteo == 1 antes de reemplazar**, entrada `9881bb62a5394ce596b208d398ec0c4c`
(27.572 caracteres) → salida `a1c126f8757f7746162023e677ed42e7` (34.684 caracteres). El
script aborta y no escribe si cualquier ancla falta o aparece dos veces. Asserts de salida:
un solo bloque `<script>` (medido: 1), y cero rastros de `paginacion_inject` / `permalink_inject`.
Los respaldos quedaron en la VM: `index.html.antes-del-parche-v5` y `api.py.antes-del-total-filtrado`.

## Test 1 · el backend honra `offset` y la interfaz pagina de verdad

Backend, `curl` directo:

```
sin filtro   total_pasajes=1741  rid=17211  (offset=0)
offset=24    total_pasajes=1741  rid=51305  offset devuelto=24
```

Navegador, misma consulta `usucapion`:

```
página 1: ?q=usucapion        1.741 pasajes · mostrando 1–12  · página 1 de 146 · 37.27 ms  órdenes 01..12
página 3: ?q=usucapion&p=3    1.741 pasajes · mostrando 25–36 · página 3 de 146 · 41.87 ms  órdenes 25..36
claves compartidas entre página 1 y página 3: 0
botón activo: 3
```

Las 12 claves de cada página están en el log de la corrida y **no se repite ninguna**: el
solapamiento es cero, que es la única forma de probar que el offset viajó hasta el SQL y no
se quedó en el rótulo. La numeración es **global** (25–36), no 01–12 otra vez.

## Test 2 · el permalink abre el pasaje exacto, en frío

URL pegada en una pestaña nueva, sin pasar por la portada:

```
https://corpus-tarija.abacusai.cloud/?q=usucapion&p=3&abrir=jur-tar-auto-supremo-as-0616-2020-2020-066dd4e7%7C14

medición   1.741 pasajes · mostrando 25–36 · página 3 de 146 · 47.63 ms
apuntado   jur-tar-auto-supremo-as-0616-2020-2020-066dd4e7|14   (ficha número 25)
lector     abierto, uid jur-tar-auto-supremo-as-0616-2020-2020-066dd4e7
           texto continuo · 14.943–17.854 de 42.769 caracteres · 41.7%
           2.911 caracteres en pantalla, 7 términos resaltados
lectores abiertos: 1     bloques de script en la página: 1
```

Y con filtro puesto, el enlace que genera el propio botón:

```
https://corpus-tarija.abacusai.cloud/?q=usucapion&anio=2018&abrir=jur-tar-auto-supremo-as-1030-2018-2018-103ffb8b%7C20

medición        230 pasajes para el término · filtrado por 2018 · mostrando 1–12 · página 1 de 20
filtro activo   anio=2018 (la faceta vuelve marcada)
apuntado        jur-tar-auto-supremo-as-1030-2018-2018-103ffb8b|20
lector          texto continuo · 22.381–25.511 de 34.012 caracteres · 75%
```

## Test 3 · atrás y adelante del navegador devuelven la página que se estaba leyendo

```
carga            ?q=usucapion&p=3   mostrando 25–36 · página 3   primera: as-0616-2020|14   activo 3
click siguiente  ?q=usucapion&p=4   mostrando 37–48 · página 4   primera: as-0088-2017|17   activo 4
atrás 1          ?q=usucapion&p=3   mostrando 25–36 · página 3   primera: as-0616-2020|14   activo 3
atrás 2          ?q=usucapion       mostrando 1–12  · página 1   primera: as-0361-2012|9    activo 1
adelante 1       ?q=usucapion&p=3   mostrando 25–36 · página 3   primera: as-0616-2020|14   activo 3
```

No se recarga la página: `pushState` al paginar, `popstate` para volver, y la primera clave
de cada estado coincide con la que tenía antes. Los estados restaurados usan `replaceState`,
así que atrás no queda atrapado en un bucle.

## Test 4 · tocar un filtro vuelve a la página 1

```
antes            ?q=usucapion&p=3     mostrando 25–36 · página 3 de 146   orden inicial 25
filtro 2018      ?q=usucapion&anio=2018   230 pasajes · mostrando 1–12 · página 1 de 20   orden inicial 01
quitar filtro    ?q=usucapion             1.741 pasajes · mostrando 1–12 · página 1 de 146
```

Borde, página que no existe: `?q=usucapion&anio=2018&p=99` cae en
`?q=usucapion&p=20&anio=2018`, "mostrando 229–230 · página 20 de 20", 2 fichas, sin cartel de
"sin coincidencias". Antes eso servía una página vacía.

## El ROJO que destapó el test 4, y su arreglo

Con el filtro puesto la interfaz decía **"página 1 de 146"** sobre 230 pasajes reales. No era
un error del frontend: `/buscar` contaba el total **sin el where de los filtros**.

```
API vieja:  q=usucapion&anio=2018&limit=1   ->  total_pasajes 1741   (el total del término)
            q=usucapion&anio=2018&offset=60 ->  devueltos 12         (había filas, sí, pero
                                                 el total mentía y las páginas del final
                                                 servían vacío)
```

`pipeline/parche_total_filtrado.py` hace que el contador comparta el MISMO `where` que las
filas. Medido en brain-env, en proceso, sin servidor de por medio:

```
VIVO_v2 sin filtro                        1741   (no cambió: el fix no toca el caso base)
VIVO_v2 anio=2018                          230
VIVO_v2 anio=2018 offset=60 devueltos       12
VIVO_v2 jurisdiccion=departamental           0
```

Y ya desplegado, contra la API pública:

```
censo                       6079 documentos · 78.930 pasajes · 102.620.935 caracteres
q=usucapion                 total 1741
q=usucapion&anio=2018       total 230
```

## Portapapeles: las dos ramas medidas

El botón viejo decía "cita copiada ✓" **siempre**, incluso cuando el navegador bloqueaba el
portapapeles: el abogado pegaba en el escrito lo que tenía antes. Ahora:

```
sin permiso de portapapeles   rótulo "no se pudo copiar", clase .falla puesta,
                              title que manda a copiar de la barra de direcciones
con permiso concedido         rótulo "enlace copiado ✓", clase .falla ausente
```

NO MEDIDO: el **contenido** del portapapeles. `navigator.clipboard.readText()` sigue
bloqueado en este navegador automatizado. Lo que sí está medido es el string que se le pasa
a `writeText`, visible en `data-enlace`, y que una URL de esa forma exacta abre el pasaje
correcto (test 2).

## Estado de la consola

`0` mensajes, `0` errores, `0` advertencias en toda la sesión de pruebas.

---

```
--- METODO TITAN ---
Accion delicada: SI (reinicio de un servicio publico en vivo)
Modo aplicado:   TITAN FULL
Rubrica:         Completitud 15/15 · Ejecutabilidad 15/15 · Seguridad N/A (no toca
                 frontera de confianza: sin auth nueva, sin entrada nueva al SQL, el
                 offset entra por parametro ligado) · Testing 13/15 (los 4 tests de
                 aceptacion mas 2 bordes corrieron en navegador real; falta suite
                 automatizada que los repita sin un humano) · Arquitectura 9/10 ·
                 DevOps N/A (no cambia infraestructura) · Documentacion 9/10 ·
                 Innovacion 5/5 (fallback de portapapeles, tope de la API declarado,
                 pagina fuera de rango, permalink con filtro) · Proceso QA 5/5
                 = 71/76 aplicables -> 93/100
N/A declarados:  2 criterios (Seguridad 15, DevOps 10) por tipo de entrega
Review externo:  no pedido en este turno (deuda declarada)
Instrumento:     Chromium real via el servicio playwright del gateway + curl desde
                 brain-env. Evidencia cruda: este archivo, verbatim, con los md5 de
                 entrada y salida y los rid distintos por offset.
```
