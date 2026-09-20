# Astra PR20: paginación protegida sin éxito parcial ante corrupción autorizada

20-sep-2026 ART. Pedido: «Astra Auditor Corpus audita corpus». Auditoría acotada del incremento actual PR20, no de los Docs históricos seleccionados en el turno anterior.

## Veredicto

**Sin nuevo defecto demostrado en las propiedades ensayadas.** Por CLI y HTTP reales, un documento autorizado corrupto invalida toda la búsqueda con 503 aunque quede fuera de la página solicitada. Un documento corrupto de otra colección no cambia las páginas autorizadas. El mutante que retorna éxito parcial fue detectado por tres aserciones específicas.

La paginación se recalcula por request: después de retirar el primer documento, el offset anterior puede quedar vacío. Es una observación de semántica de offset, no pérdida de texto ni promesa de snapshot incumplida. No aprobar merge ni producción por este resultado.

## Sujeto y selección

PR20 abierto, sin merge, head `cc2ca30760c486cad3154c619a20f94cf75cc691`, base PR19 `31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05`; consultas específicas antes/después sin cambios. Main inicial y previo a publicar: `ad2badf1a8dee2d89470f405c0c90593875bad09`. El producto se probó en el head del PR, NO en main.

Consumidor: `demo_discovery.py init/serve` real -> `ProtectedSearchApp` -> política persistente y lector versionado. Archivos leídos: `sistema/api/protected_search.py`, `sistema/api/demo_discovery.py`, guard de `isolated_login.py`, `tests/test_protected_search.py`. El servidor usa loopback, dos cuentas fixture y stores propios.

Se recuperaron Nexus 68 a 76, revisión06, auditoría01 y descripción actual de PR20. El reparo documental de la descripción antigua ya fue corregido: la API actual cita cc2ca307 y separa el CI viejo del actual. No lo reabrí como hallazgo. Logout y navegación/BFCache ya tienen pruebas específicas publicadas; no repetí esos bancos por rutina.

La nueva pregunta cruza el contrato de integridad con páginas que no devuelven el registro dañado, más retiradas entre requests y versión explícita. Algunas propiedades ya tenían unit tests: el aporte es su recorrido compuesto HTTP real con oráculo propio y un falsador de respuesta parcial, no pretender descubrir todos esos casos por primera vez.

Autoría: el historial atribuye implementación inicial a BRAIN y fix logout a Astra. Este operador no se presenta como tercero personalmente independiente. El golden, resultados esperados y falsador son explícitos y no se calculan desde helpers de tests del productor.

## Instrumento, preparación y resultados

Brain-env por Gateway build: Python3.12.14, SQLite3.46.1, dos CPU, 124674465792 bytes libres en la comprobación. Inventario y método §8 releídos. Sin Actions, GPU, VM, cuentas reales ni bases vivas.

Banco nuevo `search_page_audit.py`: esperado literal Unicode/CRLF, versión SHA256 propia, lista fija de IDs permitidos, comparación JSON tipada con copias de los valores, requests reales, SQL directo solamente sobre fixtures del auditor. Tokens emitidos por login real; sin sesión insertada para simular autenticación.

Primer intento INVÁLIDO: el cliente omitió Origin en POST y recibió correctamente 403 antes del login. No se culpó al producto. Además el registro de init retenía por referencia la lista args luego modificada a serve; stdout conserva initialized. Se preservó ese intento y su fuente, se corrigieron SOLO Origin y copia de lista, y se abrió otra fixture. No se interpretó ese primer baseline como un positivo.

Banco corregido: 33 aserciones, cero fallos, exit0. Repetición con nueva copia de fuente y fixture: 33/0, exit0. No son 66 casos independientes. Suite del autor seleccionada `python3 tests/test_protected_search.py`: 15 tests, exit0 en6.594s; referencia separada, no banco propio. No se repitieron140Python ni Chromium.

### Propiedades confirmadas

1. Dos logins reales200. Ana recibe a1/a2 en dos páginas ordenadas, total2 y next_offset1/None. Ben recibe solo su colección; no se derivó esa lista desde CATALOG.
2. STRASSE, é, e+acento combinante y 😀 encuentran a1 manteniendo el snippet EXACTO Unicode/CRLF. Buscar literalmente `%64erecho` produce total0: no se aplica una segunda decodificación.
3. Corromper b1 después del arranque no cambia los cuerpos JSON de ninguna de las dos páginas de Ana. Ben obtiene503 SEARCH_UNAVAILABLE. Restaurar b1 recupera su respuesta original.
4. Corromper a2, que NO aparece en la primera página limit1, devuelve503 genérico para Ana. También falla con offset8 aunque la página sería vacía. No hay200 parcial, snippets parciales ni falsa lista vacía.
5. La misma corrupción de a2 no cambia la búsqueda de Ben. Al revocar el grant de Ana, responde403 ACCESS_DENIED antes de procesar el contenido dañado. Restauración explícita de fixture recupera el baseline.
6. Retirar a1 recalcula total1 y devuelve a2 en offset0; offset1 queda vacío. El UID/version retirado se rechaza403 por el lector. Se restituye la retirada solo en la fixture.
7. Cambiar el sha256 de la fila actual de a1 no cambia la búsqueda versionada ni el texto de la versión explícita original. No hay fallback silencioso a la fila actual.
8. Expirar la sesión por SQL en la fixture niega búsqueda403, pero permite logout200 con logged_out true; SQL confirma revoked_at no nulo. Es expiración ya aplicada antes del request, NO expiración durante un cierre demorado en navegador.

## Falsador causal

Solo en copia scratch de `protected_search.py`, sustituir:

`except Exception: return 503, {"error": "SEARCH_UNAVAILABLE"}`

por `except Exception: pass`, preservando el resto del camino. El diff exacto está en la captura. Se deja así continuar el armado de una respuesta200 parcial tras fallar el lector.

Mismo instrumento:33 aserciones, tres fallos, exit1. `authorized_corruption_no_partial` observa200 vacío en vez de503; `offpage_authorized_corruption_no_partial` observa200 con a1 parcial; `empty_page_still_validates_authorized_content` observa200 vacío/total1 en vez de503. Los restantes30 controles pasan, incluidos login, aislamiento y restauraciones. En el positivo esas MISMAS tres aserciones pasan. No es un rojo por import, timeout o precondición rota.

## Recursos, evidencia y reproducción

Conexiones propias SQL y HTTP cerradas explícitamente; transacciones separadas de closing. No agregué contador de conexiones internas del producto ni afirmo ausencia global de fugas. Todos los servidores propios terminaron exit0; comprobación posterior independiente: cuatro PID ausentes y cuatro puertos connect_ex111, incluyendo el intento inválido. La limpieza intentó logout de ambos bearer antes de detener cada servidor; respuestas conservadas.

Evidencia hermana `2026-09-20-07-search-pagination/evidence.xz.b64`: archivo único base64 estricto+xz; JSON112353bytes, SHA256 `8ccac44aa8d36dcdcd8c5db8f99aa17043c743f705296047cfe35304d3972cdc`; payload9200caracteres. Incluye ambos instrumentos, error inicial completo, corridas corregida/repetida/mutada, diff, comandos y stdout/stderr completos, cuerpos/headers HTTP completos con tokens redactados, suite del autor y comprobación de recursos.

Excluidos desde captura: valores Authorization, passwords de requests, tokens emitidos, archivos SQLite. Los metadatos PR son campos seleccionados, no copia completa de la API. No es un archivo de toda la conversación.

Reproducir: extraer el repo al SHA cc2ca307 en un directorio nuevo; decodificar evidencia con base64.b64decode(validate=True), lzma.decompress y comprobar longitud/hash; guardar `sources["probe-v2.py"]`. Ejecutar `python3 probe-v2.py REPO NUEVO_OUTPUT`, volver a ejecutar con otro output. Para falsador, aplicar el diff únicamente en otra copia; no sobrescribir fixtures existentes. Requiere POSIX, Python/SQLite compatibles y puertos loopback.

## Gates y límites

Gate I PASA para el banco corregido: sujeto exacto, oráculo explícito,33/0 positivo, repetición, falsador dirigido y recursos propios cerrados. Banco inicial INVÁLIDO y preservado. Gate II PASA acotado: no confundir offset vivo con snapshot, expiración preaplicada con carrera, dato ficticio con corpus jurídico ni clon con main.

Gate III al escribir: pendiente de publicación/relectura, comparación byte por byte, Doc público y Nexus. Esos pasos se comprobarán antes del chat; el cierre de Doc/Nexus registrará el estado posterior sin alterar estos resultados.

NO MEDIDO: revocación simultánea dentro del mismo request, canales temporales, cargas, otros navegadores, BFCache restaurado, callback tardío, accesibilidad, nuevas variantes de logout UI, producción/TLS, cuentas humanas, vigencia jurídica o piloto. Ningún resultado de este turno convierte en medido el BFCache que no alcanzó precondición antes.

Prioridad: no hay arreglo de producto nuevo justificado por este banco. No propongo otro bucle idéntico de tests ni convierto el recuento de aserciones en avance de piloto. Persisten la revisión externa según autoría y las decisiones humanas/operativas del piloto. No merge, deploy, mensajes, issues, cambios del PR ni cambios de producto fuera de copias descartables.