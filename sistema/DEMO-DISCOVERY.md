# Buscar, leer y guardar una referencia, solo con datos ficticios

`sistema/DEMO-DISCOVERY.md` corresponde a la rama apilada sobre PR19, no a
un servicio publicado. No importa datos, no crea cuentas reales y no habilita
un piloto. Los lectores, login, logout y política heredados no se modifican.

## Arranque

Desde la raíz del repositorio, con Python 3.12, SQLite con tablas STRICT y POSIX:

```bash
set -euo pipefail
parent="$(mktemp -d)"
python3 sistema/api/demo_discovery.py init --isolated-demo --directory "$parent/fixture"
python3 sistema/api/demo_discovery.py serve --isolated-demo --directory "$parent/fixture"
```

Abrí la URL `http://127.0.0.1:<puerto>` que devuelve `ready`. No se publica
en interfaces externas. `--port 0`, predeterminado, asigna un puerto libre;
`--port N` permite elegir uno entre 0 y 65535. Sin `--isolated-demo`, aborta
antes de crear archivos. No se leen variables de entorno para configuración.
No pases un directorio ya existente a `init`: no hay reset ni sobreescritura.

Elegí Ana o Ben, entrá, buscá `derecho`, seleccioná un resultado, leé y guardá
la referencia. Cerrá sesión y esperá confirmación antes de cambiar de identidad.
Ana y Ben tienen dos documentos ficticios cada uno en dos colecciones distintas.
No hay entrada de contraseñas: la contraseña pública `solo-demo-ficticia`
pertenece exclusivamente al fixture, nunca debe reutilizarse en una cuenta real.
La página pública no lleva el catálogo de UID/versiones ni sus títulos.

La referencia descargada contiene 16 campos permitidos: esquema, entorno,
UID, versión, hashes de texto y fuente distintos, URL y alcance de fuente,
alcance de hash, autoridad, oficialidad, validez jurídica NO_MEDIDA,
cantidad de caracteres, instantes de lectura/comprobación y advertencias.
No contiene texto, sesión, contraseña ni notas. Guardar vuelve a consultar
el lector protegido y compara procedencia con la lectura terminada.
No importa referencias. No concede acceso ni certifica vigencia jurídica.

## Límites del contrato18 enmendado

`GET /api/v2/buscar` exige `q`, admite solo `offset` y `limit` adicionales.
Una sola decodificación UTF-8 estricta; claves duplicadas, parámetros extra,
escapes inválidos y controles Unicode se rechazan. `+` significa espacio.
`q` tiene 1 a 128 puntos de código y como máximo 256 bytes UTF-8, sin recortar
espacios. NFC seguido de casefold se usa únicamente para coincidencia literal.
El texto mostrado conserva caracteres originales, CRLF y secuencias combinadas.
No se usan expresiones regulares ni SQL de búsqueda.

Offset predeterminado 0, rango 0..8. Limit predeterminado 5, rango 1..5.
Los números no admiten signo, espacios, ceros iniciales, exponentes ni decimales.
La cadena de consulta cruda tiene límite de 2048 bytes antes de decodificar.
Una consulta de 815 bytes con todos sus bytes válidos escapados puede superar
la gramática; no hay una consulta positiva de 2048 bytes bajo los otros límites.

Hasta ocho locators configurados, una versión fija por UID. Se completan todas
las decisiones de permiso antes de leer contenido. Solo literal True permite
leer. Una excepción de política descarta todo, incluso después de otro permiso.
El catálogo vacío igualmente verifica sesión y devuelve rechazo genérico.
Los títulos y snippets se crean exclusivamente desde versiones autorizadas.
Orden ASCII por UID y luego versión, sin estadísticas de documentos prohibidos.
El total cuenta coincidencias autorizadas, nunca el corpus completo.

La página muestra las primeras cinco coincidencias y pide acotar la consulta
si hay más. El fixture actual tiene cuatro documentos. El endpoint sí tiene
paginación probada. Cada resultado enlaza la misma versión explícita al lector.
No se usa el buscador v1 ni el índice público existente.

Límites por documento: 4096 puntos de código y 16384 bytes UTF-8. Archivos
candidato y política separados, regulares, privados 0600 y de hasta 1 MiB
al arrancar; directorio 0700. Manifiesto fijo y marca de identidad propios.
Los errores no muestran consultas, tokens, rutas, SQL ni resultados parciales.
El cuerpo JSON compacto completo no puede exceder 16384 bytes.

La precedencia es: guardas de transporte/aislamiento, método, cuerpo,
tamaño crudo, gramática/valores, sesión, permisos y por último contenido.
HEAD sobre la ruta exacta no envía contenido, Content-Length ni Transfer-Encoding,
incluso si una guarda anterior responde 403 o 503. Si alcanza el método,
devuelve 405 con Allow: GET. Los métodos heredados de login/logout conservan
Allow: POST. Esto no corrige ni certifica HEAD en otras rutas.

Todos los resultados de búsqueda, también los rechazos tempranos, llevan
JSON UTF-8, no-store, nosniff y no-referrer. Sin CORS, cookies ni refresco
automático. Duplicados sensibles se detectan antes de despachar la aplicación.
Una petición cuyo destino no pudo parsearse queda fuera de esa clasificación.

## Errores y recuperación

403: acceso o aislamiento rechazado. La UI descarta resultados, texto y
referencia pendiente; requiere iniciar una sesión nueva o intervención del
operador. 503: indisponible; se puede reintentar explícitamente, con nuevas
comprobaciones de permisos. Nunca se sirve un resultado parcial como fallback.

400 INVALID_QUERY: corregí consulta o parámetros. 400 EMPTY_REQUEST_REQUIRED:
la búsqueda no admite cuerpo. 414 QUERY_TOO_LONG: acortá la consulta cruda.
405 METHOD_NOT_ALLOWED: usá GET. 503 SEARCH_UNAVAILABLE: el operador debe
inspeccionar integridad/versión; no se sustituye silenciosamente texto actual.
503 ACCESS_POLICY_UNAVAILABLE o ISOLATION_UNAVAILABLE: inspeccionar el store
privado y sus bloqueos. 503 RESPONSE_LIMIT_EXCEEDED: no se trunca.

Si el arranque falla, queda el directorio para inspección; no hay borrado
automático. No cambies permisos de bases reales para hacerlas pasar como fixture.
El manifiesto solo acepta los documentos ficticios de este lanzador.
SIGINT o SIGTERM termina el bucle y cierra el listener. Recargar la página
olvida el token local, pero no revoca la sesión del servidor.

## Verificación local y CI

```bash
set -euo pipefail
python3 tests/test_protected_search.py
python3 tests/test_demo_discovery.py
tools="$(mktemp -d)"
npm install --prefix "$tools" --no-audit --no-fund --ignore-scripts playwright@1.63.0
"$tools/node_modules/.bin/playwright" install chromium
NODE_PATH="$tools/node_modules" node tests/browser_discovery.cjs
```

Chromium requiere sus bibliotecas de sistema; CI usa Ubuntu 24.04 y
`playwright install --with-deps chromium`. La versión exacta heredada no
cambia. El workflow existente mantiene todos los bancos anteriores y añade
los dos bancos Python nuevos y el navegador. No hay workflow adicional,
secretos nuevos, permisos de escritura ni despliegue.

El banco unitario inyecta sesiones sintéticas para aislar decisiones. El
banco de red y Chromium usan login real del fixture y verifican cierre.
Los tests de HEAD inspeccionan bytes crudos después del separador HTTP.
Los mutantes locales de permisos, versión, HEAD y headers se documentan
en el recibo17; no forman parte del producto ni se publican como código activo.

## Lo que esto no demuestra

No es revisión externa del autor, producción, capacidad bajo carga, tiempo
constante, autorización atómica durante toda la respuesta ni revocación de
bytes ya entregados. Socket timeout de 2 segundos significa inactividad;
espera SQLite de 1 segundo no es un plazo total de petición. El presupuesto
de login heredado sigue en cinco intentos por 60 segundos; no hay nuevo
limitador de búsqueda. Grants ficticios duran 24 horas; sesiones, 15 minutos.

No hay TLS/cookies/CSRF/reset productivos, muestra legal aprobada, contacto
institucional, consentimiento, presupuesto ni apertura del piloto. Merge,
despliegue y datos reales requieren permisos separados.
