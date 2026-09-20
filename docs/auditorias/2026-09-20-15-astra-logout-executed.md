# Astra Auditor: logout ejecutado, revocación persistente y segunda sesión intacta

## Pedido y veredicto

Pedido de Abraham, 20-sep-2026 13:20 ART: /Astra Auditor Corpus ejecuta. Tu eres astra auditor.

**Sin nuevos reparos de producto en los seis escenarios ejecutados.** Instrumento nuevo: 183 comprobaciones con esperado/observado, repetidas en otro archive y fixtures nuevas:183/183. Dos mutantes causales fallan en las propiedades previstas. Banco publicado del autor:88 comprobaciones, exit0, separado de la prueba nueva.

No es revisión ciega ni aprobación externa: esta conversación contiene implementación y pruebas anteriores. La identidad Astra no borra esa historia. El instrumento y las expectativas de esta ejecución se escribieron de nuevo y no calculan el esperado con la función juzgada, pero la selección de casos ya conocía antecedentes. **G2, entendido como revisión por otro autor, no se cierra con esta corrida.** Se ejecutó el pedido en lugar de devolver otro pase.

## Sujeto, contrato y permisos

[PR20](https://github.com/gatehot59-star/corpus-legal-tarija/pull/20): head `ca503377760a8dcd7965689a2853420785a83d94`, base PR19 `31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05`. Inicio16:20:31UTC; reconsulta16:24:44UTC del20-sep: mismo head/base, abierto y sin merge.

Productor/consumidor: `sistema/web/discovery_spike.html` en Chromium real, CLI `sistema/api/demo_discovery.py` y logout persistente `sistema/api/isolated_session.py`, por HTTP loopback. No emulación WSGI ni solo SQL como veredicto. SQL se usa para intervención controlada en stores sintéticos propios y lectura independiente de revocación, nunca en bases reales.

Contrato previo: limpiar contenido/selección/resultados/referencia al iniciar cierre; impedir otras acciones y duplicados; no convertir rechazo/error/cuerpo inválido en confirmación; conservar el bearer original para reintento explícito; confirmar solo boolean true; comprobar revocación persistente de A y supervivencia de una sesión B del MISMO usuario. Dos pestañas del mismo contexto Chromium, dos logins reales de Ana; bearer diferente medido, nunca publicado.

Solo lectura del repo, fixtures propias, pruebas y documentación. No cambios remotos de producto/workflow/permisos, mensajes, asignaciones, review requests, merge o despliegue. No se ejecutó Actions. No se esperó a otro agente para realizar estas pruebas.

## Preparación y entorno medido

brain-env por Gateway build/run. Python3.12.14, Node24.18.0, Playwright1.63.0, Chromium153.0.8010.12. Disco libre124578738176bytes al inicio. Inventario y método existentes leídos; no se atribuye a Corpus el estado histórico de MUDH. Nexus no tenía reportes posteriores al84 al empezar.

Archive propio de ca503377, repetición en segundo archive. Matriz guardada antes de correr, incluida en evidencia. La fixture se inicializa mediante el CLI del producto y su manifiesto sintético: no se presenta como un generador independiente del producto. El texto esperado es un literal del instrumento; las expectativas de estado, HTTP y revocación están fijadas fuera de las funciones juzgadas. El control positivo establece login real, lectura Unicode exacta, referencia disponible, dos bearers distintos y HTTP200 para ambas sesiones antes de cada intervención.

## Seis escenarios y resultados

| Caso | Intervención declarada | Resultado del candidato |
| --- | --- | --- |
| 403 real | Retener primera petición logout en Playwright; retirar marcador en store propio; liberar al servidor; restaurar marcador después de respuesta403 | UI no confirma, conserva reintento con bearer A; A sigue activa antes de reintento; luego revocada. B permanece autorizada. |
| 503 real | Otro proceso mantiene BEGIN IMMEDIATE en SQLite; liberar petición logout; esperar503; liberar y cerrar conexión | UI no confirma y reintenta después con el mismo bearer. Revocación persistente de A sin afectar B. No es un503 inventado. |
| Abortada antes del servidor | Intercepción aborta la primera petición antes de enviarla | UI no confirma; A sigue activa; reintento explícito revoca; B intacta. Fallo de transporte inyectado, no espontáneo del backend. |
| Respuesta perdida tras revocar | route.fetch ejecuta logout real y registra200/boolean true; se aborta la entrega al navegador | UI no confirma aunque A ya está denegada; reintento idempotente confirma, B intacta. La respuesta real está registrada sin token. |
| 200 con string true | Se responde al navegador con logged_out:"true", sin invocar backend en ese intento | UI rechaza confirmación; A sigue activa hasta reintento real. No se atribuye ese cuerpo inválido al servidor. |
| Expiración durante cierre pendiente | Con petición retenida, cambiar solo la ventana temporal de A a valid_from=0/valid_until=1 en store propio; medir403 de A y200 de B; liberar logout | Logout confirma y persiste revoked_at pese a expiración. Restaurar ventana válida después NO resucita A: sigue403. B mantiene revoked_at NULL, HTTP200 y búsqueda usable en su pestaña. |

La expiración es una transición de estado inyectada en el store mientras el cierre espera, no una espera natural de15min ni manipulación del reloj del proceso. Restaurar validez temporal después de confirmar separa denegación por expiración de denegación por revocación: el403 solo no habría bastado.

En cada escenario, mientras se retuvo la primera petición: texto vacío, cero resultados, versión ninguna, todos los controles deshabilitados. Eventos programáticos de login/search/read/save/logout no dispararon acciones ajenas ni logout duplicado en la ventana observada80ms. Tras un fallo, se esperaron150ms sin reintento automático y se pulsó el reintento explícitamente. Estas ventanas no prueban ausencia durante tiempo infinito.

Después de confirmar, se midió revoked_at de A no NULL y B NULL; A403/B200 por HTTP independiente. La pestaña B volvió a buscar con dos resultados. Un segundo logout HTTP de A devolvió true y B siguió200. Confirma aislamiento entre dos sesiones del mismo usuario en estos casos, no toda concurrencia entre pestañas.

## Falsadores y referencia del autor

Los mutantes se sirven exclusivamente al navegador de control mediante interceptación de HTML; ningún archivo del candidato ni rama se edita.

- **Pérdida de handle:** al recibir403, borrar también logoutToken. El mismo instrumento sale1 exactamente en `marker403:retry_available`, actualfalse/expectedtrue, después de14 comprobaciones pasadas incluyendo preparación y limpieza (15 comprobaciones totales). La propiedad pasa en positivo y repetición.
- **Confirmación permisiva:** sustituir la comparación estricta por `if (!r.logged_out)`. El instrumento sale1 en `string_true:failure_not_confirmed`, actualfalse/expectedtrue.14 comprobaciones totales, una propiedad fallida. La propiedad pasa en el candidato.

Cada falla también genera un registro scenario_error con stack: no se cuentan esos duplicados como dos defectos. Se preservan sustituciones exactas, hashes original/mutado y stdout/stderr completos.

`node tests/browser_discovery.cjs` del head exacto:88 comprobaciones, exit0; no se suma al183 para inflar cobertura. Las diez suites Python y CI no se relanzaron en este turno. Los dos falsadores validan sensibilidad para esas dos propiedades, no todas las183 ni toda la seguridad.

## Repetición, recursos y recomprobación

Primera corrida183 comprobaciones, cero fallos. Segunda183, cero fallos, archive y fixtures nuevos, mismo instrumento. Verificación posterior recalcula igualdad actual/expected y compara con los flags guardados; detecta exactamente una propiedad rota por mutante y ninguna en candidatos.

14 servidores propios (6+6+1+1) terminaron exit0;14puertos rechazaron conexión al cierre. Ambos procesos de bloqueo SQLite de las corridas completas salieron0. Conexiones SQL cerradas explícitamente. Limpieza final de stores sintéticos deja cero sesiones no revocadas; está separada de las aserciones de producto, ejecutadas antes de esa limpieza. Contextos y navegador cerrados; scan acotado de procesos propios vacío. No se afirma inspección universal de Chromium ni per-port del banco del autor, que usa su limpieza heredada.

Los cuatro archivos relevantes del archive permanecen byte por byte iguales al Git de ca503377. HTML SHA256 `69eba91fcf88b5c0547e263276cfc1a9f0da2703b91a1601397e8fffb0b5efdb`; banco SHA256 `0c1f34694b9e8de2a28985b3078222292406c30027ae50200aaaaa6f47d43984`. Instrumento ejecutado12970bytes SHA256 `c9f41d47d5dcaeb938bd5451add74916f33969701694cd8b220d0043caed4fa0`.

No hubo corridas inválidas de este instrumento: primera completa exit0, repetición exit0, controles exit1 en propiedades previstas. Se normalizaron prefijos '+' de transferencia y se añadió captura de HTTP antes de ejecutar; no son correcciones de producto ni resultados experimentales.

## Evidencia y reproducción

Paquete hermano [evidence.xz.b64](2026-09-20-15-astra-logout-executed/evidence.xz.b64): base64 de xz, JSON decodificado **138159 bytes**, SHA256 `f701085562ebe44a0ec4216033a5a3617dd34fefeb984345bde5b4ab252da022`.

Contiene state.json, matrix-before.json, fuente review.cjs, cinco capturas de subprocess con comando/exit/stdout/stderr íntegros (positivo,repetición,dosmutantes,bancodelautor), verificación de recursos/refs/hashes. Las salidas incluyen esperado y observado congelados. No tokens ni Authorization reales; se registran solo igualdades. Bases sintéticas, video y browser trace excluidos. Fuentes del CLI/fixture y producto se recuperan del SHA fijado, no se duplican.

Reproducción: decodificar base64 estricto y xz, verificar bytes/hash; extraer files["review.cjs"] a scratch propio. Archive limpio del head; directorio de salida NUEVO por ejecución. `node review.cjs <archive> <output-nuevo> normal`; modos `lose_handle` y `trust_string` deben fallar en las aserciones especificadas. Dependencias/runtime anteriores; en brain-env NODE_PATH=/workspace/corpus-browser-spike-u6wwk669/.browser-tools/node_modules y LD_LIBRARY_PATH=/workspace/corpus-browser-spike-u6wwk669/.browser-tools/sysroot/usr/lib/x86_64-linux-gnu. Comprobar existencia en otra máquina, no asumirla.

## Estados, límites y gates

CONFIRMADO en alcance: conservación del reintento, limpieza/bloqueo inmediato, rechazo de string true, respuesta perdida e idempotencia, revocación aunque A expire con petición pendiente, aislamiento de B del mismo usuario. REFUTADO: los dos candidatos mutados satisfacen el contrato; el instrumento los rechaza. Sin fallo nuevo en el candidato original.

Qué no se midió que importaba: selección de casos por otro autor sin esta historia; expiración natural por reloj en vez de transición controlada; BFCache/restauración; todas las carreras entre pestañas, navegadores distintos, producción/TLS/carga/validez jurídica. No repetir un límite como nuevo bug. Recargar sigue sin equivaler a revocar. El resultado no aprueba toda la pila PR18/19/20 ni autoriza merge.

TITAN LIGERO para verificación experimental focalizada. Rúbrica numérica N/A. Gate I PASA en sujeto, esperado separado, positivos, dos falsadores, repetición, captura y recursos propios; independencia externa NO MEDIDA, explícita. Gate II PASA con causalidad y límites. Gate III se completa con informe/evidencia publicados y recuperados, comparación remota, pertenencia a main, Doc público leído y reporte Nexus. El cierre verificable quedará registrado en Doc/Nexus; no usar este párrafo como sustituto de las comprobaciones.
