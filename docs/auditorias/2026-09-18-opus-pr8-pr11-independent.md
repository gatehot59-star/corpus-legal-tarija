# OPUS Auditor Corpus: verificación independiente PR8 a PR11

**Fecha:** 2026-09-18 UTC, 17-sep-2026 ART  
**Sujeto:** `gatehot59-star/corpus-legal-tarija`, cadena PR8 `cc8c33562a4adb9976db81478b8cac6f353152f8` a PR11 `3a60627101859ca92c9b0a4fdd436205b99bb504`.  
**Base de comparación:** head PR7 `d78ad5977ec723fa39a421d4eb2f80d19a2a5f62`.  
**Alcance:** fixtures sintéticos propios, copia candidata local de PR7, HTTP loopback y suites publicadas. Sin producción, despliegue, cuentas reales, permisos ni merges.

## Resultado corto

**CONFIRMADO:** el lector versionado conserva texto exacto en el alcance ensayado; los límites HTTP, integridad de hash y controles de autorización probados fallan cerrados.  
**CONFIRMADO:** las cuatro suites publicadas reejecutan 63 tests y terminan exit 0: 21 `test_clean_snapshot_sol`, 15 `test_exact_http`, 15 `test_access_policy`, 12 `test_isolated_login`. CI `stable_identity` también figura success en los heads PR8, PR9, PR10 y PR11.  
**REFUTADO:** interpretar que la marca `isolated_test` corta toda lectura. Al borrar esa fila, un login nuevo devuelve 403, pero una sesión ya emitida conserva lectura 200. El opt-in global apagado sí corta login y lectura.  
**NO MEDIDO:** Corpus vivo, publicación, calidad jurídica, búsqueda/citas/exportación, cuentas humanas, proxy/TLS, concurrencia hostil y recuperación de cuenta.

## Pruebas independientes

Instrumento propio, separado de fixtures y clases de test del productor: `opus_bench.py`, con oráculo sintético de 13.000 puntos de código, texto multibyte, CRLF y 40 repeticiones de la misma cláusula. Sirvió por HTTP real en loopback y paginó con límites 137, 250 y 1. Veredictos: 19/19 casos verdes, hash de reensamblado exacto, 40/40 repeticiones preservadas, límites y offsets rechazados correctamente, uid autorizado pero inexistente devuelve 404.

Banco de permisos: 23 casos, con ventanas exactas de sesión/grant, usuario/grupo/colección/documento retirado, revocación, versión no cubierta, store roto, colección cruzada y texto alterado manteniendo hash. 22 casos verdes del producto; el único rojo del instrumento fue un espacio final en `Authorization` enviado por `urllib`, que el transporte normaliza antes de llegar a WSGI. Repetido directamente contra la política WSGI, espacio y tab devuelven `False`: **no es defecto del producto**.

Banco de login: 12/12 verdes. Credencial ficticia correcta, password/usuario desconocidos, JSON duplicado, Origin, Content-Type, origen no loopback, H1 de la marca y rate limit 5+1. Scrypt y sesión fueron creados por el código real, pero sólo con identidades fixture.

Cuatro mutantes independientes fueron detectados por el banco: truncar cada página, quitar el filtro de retiro, ampliar la ventana de sesión y aceptar cualquier password. Esto valida que los oráculos podían ponerse rojos.

## Afirmación -> instrumento -> posibilidad de rojo -> veredicto

1. **“La lectura nueva conserva el texto completo”** -> oráculo propio multibyte/CRLF, HTTP paginado y SHA256 -> mutante `drop_char` detectado -> **CONFIRMADO en fixture y camino PR11**.
2. **“Login no equivale a autorización y las revocaciones cortan”** -> stores propios, HTTP, ventanas exactas y mutantes `allow_all` -> retiros, revocaciones, usuario/grupo/colección y grant de otra versión devuelven 403 -> **CONFIRMADO en casos probados**.
3. **“La marca aislada protege cada lectura”** -> eliminar `login_environment` después de emitir sesión -> login nuevo 403, lectura preexistente 200 -> **REFUTADO como contrato global**; queda confirmado sólo como guardrail de emisión.
4. **“El incremento está servido a usuarios”** -> grep de llamadores y rutas, consulta de main -> `servidor.py` no importa `exact_http`, `version_text`, `access_policy` ni `isolated_login`; main no contiene esos módulos -> **NO MEDIDO/NO demostrado; el árbol auditado no prueba publicación**.

## Cobertura medida y brecha de producto

En la copia candidata local `corpus-clean-copy/results/corpus-candidate.db`, sólo lectura, había 6.079 documentos: 5.030 `tsj_genesis`, 1.034 `tarija_gaceta` y 15 `lexivox_nacional`. `corpus_cleanup_versions` tenía 3 filas, las tres legibles por `version_text`: 1.153.164 caracteres en total. Cobertura del lector exacto sobre documentos: **3/6.079 = 0,0494%**.

La API legacy `documento()` une chunks con saltos de línea sin reconstrucción exacta. En esos tres documentos reales de la copia, el resultado quedó inflado entre **15,03% y 15,42%** frente al texto versionado exacto. Es evidencia de una copia candidata, no una afirmación sobre el servicio vivo. El arreglo aislado no puede presentarse como cobertura del corpus ni como publicación lista para usuarios.

## Evidencia y límites

Se verificó de forma independiente el bundle previo de SOL: 281.045 bytes descomprimidos, SHA256 `f30b997bc58d13e1eb19d42aa71d9ae543d9d1fdee449e1bdbc42996f1652562`, coincidente con el declarado. El bundle de esta corrida incluye el banco propio, resultados JSON, mutantes, cobertura, comparación legacy/exacto y hashes de instrumentos; su manifiesto local registra SHA256 `6983abd5aa2c0556b6947625b224b16c928092e4b26f75e5096b2195d71177ba`.

No se corrigió producto ni se cambió una rama de trabajo durante la auditoría. No se autoriza merge, publicación, piloto ni cuentas reales. La independencia es del instrumento, no del operador: estos resultados no certifican los instrumentos históricos de SOL como revisión de terceros.

**Archivo commiteado:** `docs/auditorias/2026-09-18-opus-pr8-pr11-independent.md`.
