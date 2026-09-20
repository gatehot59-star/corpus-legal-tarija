# PR20: regresión de selección integrada en el banco de CI

20-sep-2026 ART. Pedido: Add the selection regression test to PR20’s CI.

## Cambio autorizado

Rol de este turno: implementación de tests, no revisión externa del propio cambio. Un único archivo de la rama `titan/protected-discovery`: `tests/browser_discovery.cjs`, 56 líneas añadidas. No se cambió producto, autenticación, interfaz, configuración del workflow, dependencias ni permisos.

Base inicial `cc2ca30760c486cad3154c619a20f94cf75cc691`; head entregado `ca503377760a8dcd7965689a2853420785a83d94`; base PR19 sin cambio `31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05`. Se consultaron los PRs abiertos y sus archivos antes de editar: solo PR20 tocaba este banco.

El workflow existente `.github/workflows/clean-snapshot.yml` ya dispara por este archivo y ejecuta `node --check tests/browser_discovery.cjs` y `timeout 120s node tests/browser_discovery.cjs` con shell `set -euo pipefail`. Integrar las aserciones en ese entry point basta para que CI las ejecute; no hacía falta otro workflow ni otro archivo ejecutable.

## Lo que ahora protege

Se agrega un flujo en fixture nueva, sin consumir el presupuesto de login de las anteriores: Ana selecciona, lee y descarga a1; cambia a a2 sin volver a buscar; hace logout confirmado; Ben entra, selecciona, lee y descarga b2 y cierra sesión.

Cada documento tiene un golden literal independiente del callback, del catálogo del producto y de la descarga. El hash esperado se calcula desde ese texto literal. Se compara versión elegida, texto exacto Unicode/CRLF, UID/hash, filename, URL de fuente, cantidad de puntos de código y etiquetas de procedencia. Cambiar selección debe vaciar texto anterior y deshabilitar guardar hasta terminar la lectura nueva.

`checkExact` conserva actual/expected con copias y lanza `assert.deepEqual`, no solo imprime un rojo. Un fallo termina el proceso con exit1 mediante el manejo existente. La espera de descarga tiene timeout explícito y tratamiento inmediato del rechazo. Sin nuevos tokens en logs ni nuevas credenciales.

## Prueba y falsadores

Banco ampliado real Chromium153.0.8010.12, Playwright1.63.0, Node24.18.0 y Python3.12.14 en brain-env. `node --check`: exit0. Banco completo: **88/88**, repetición con fixtures nuevas: **88/88**, ambos exit0. Son59 comprobaciones heredadas y29 añadidas; la repetición no duplica casos únicos.

Dos mutantes solo en copias scratch del HTML, tests idénticos:

- Todos los botones seleccionan `r.results[0]`: exit1 en `selection_fixture-a2_pins_clicked_version`, actual hash de a1 frente a esperado de a2.
- Solo botones de Ben seleccionan el primer resultado: exit1 en `selection_fixture-b2_pins_clicked_version`, actual hash de b1 frente a esperado de b2. Esta variante atraviesa positivamente el caso de Ana antes del rojo de Ben.

Las mismas aserciones pasan en ambas corridas positivas. No son fallos de arranque, timeout o imports. Los mutantes no se publicaron como producto ni se ejecutaron en una rama remota; el rojo específico fue local usando el mismo entry point que corre CI. No se afirma haber enviado código intencionalmente roto a Actions.

## Error de publicación detectado y corregido

El primer commit `3a327a72a4d4775aaccd792b9eae538500576ba3` omitió por transcripción `json` de un import Python heredado dentro del test. La comparación byte a byte contra el archivo que había pasado detectó esa diferencia. Se repuso en `ca503377760a8dcd7965689a2853420785a83d94`, sin cambiar lo probado.

Readback final:16114bytes, SHA256 `0c1f34694b9e8de2a28985b3078222292406c30027ae50200aaaaa6f47d43984`, idéntico al archivo ejecutado. Delta desde la base inicial: solo56inserciones en el banco, ninguna eliminación ni cambio productivo. El primer commit no se usa como evidencia verde.

## CI remoto y cierre

CI final: run35515778571 / job106091355198, head exacto `ca503377760a8dcd7965689a2853420785a83d94`, completed/success. Diez pasos completed/success, incluido Chromium; intervalo14:12:42 a14:13:57UTC (11:12:42 a11:13:57ART). Se consultó el objeto job y sus pasos, no solo el estado combinado. El job del primer head,106091200899, terminó failure y queda preservado; no se usa como verde. No se atribuye88 a stdout remoto: ese conteo es local, no se descargaron logs de Actions.

Evidencia hermana `2026-09-20-09-selection-ci/evidence.xz.b64`: base64 estricto+xz, JSON87207bytes SHA256 `122761d300daacff795c6cc7e7473625e3c56b5ddffcbc60cf02b805f72672ba`; transporte11832caracteres.

Captura: fuentes completas del banco y workflow, diff, comandos/salidas completas de positivo/repetición/ambos mutantes, syntax check, comparación remota inicial/final, versiones y proceso scan. SQLite, bearer y valores de contraseñas emitidas no se publican. La contraseña fixture literal heredada no es una credencial real. La limpieza del banco cierra navegador y servidores y borra solo sus fixtures; scan propio posterior no encontró procesos del banco ni servidores. No se agregó telemetría de puertos ni se certifica ausencia global de procesos Chromium.

La entrega documental en main y el Doc público acreditan publicación, no merge de PR20. La revisión externa del fix de logout señalada como G2 en el informe08 sigue pendiente. G1 queda cubierto por el banco versionado y debe juzgarse con el CI del nuevo head. BFCache, producción y piloto no cambian de estado.

Gate I: PASA acotado, positivos y falsadores dirigidos. Gate II: separa implementación, medición local, CI y revisión externa. Gate III al escribir: pendiente de cerrar estado remoto, publicar/releer captura e informe, Doc y Nexus; el cierre efectivo quedará en el Doc y continuidad.

--- METODO TITAN ---
Accion delicada: NO, test puntual; workflow, permisos y producto intactos.
Modo aplicado: TITAN LIGERO.
Rubrica: N/A (modo ligero); no score de producto.
Review externo: sin nueva aprobación emitida, deuda separada.
Instrumento: banco Chromium88/88 repetido, dos mutantes rojos dirigidos y readback byte a byte. No merge, deploy, comentarios, issues ni asignaciones.
