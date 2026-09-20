# Corpus: revisión de SOL y Astra contra PR20 actual

Fecha: 20-sep-2026, ART. Pedido: «Revisa las auditorias de sol y astra auditor».

> Corrección documental posterior, 20-sep-2026: Astra corrige en §2 `revoked===true` por `logged_out===true`, el campo real del cliente. El resto del informe conserva el snapshot histórico cc2ca307 y su autoría BRAIN; sus menciones de «actual» se refieren al momento de aquella revisión. El head posterior es ca503377760a8dcd7965689a2853420785a83d94, con banco de88 comprobaciones y CI run35515778571/job106091355198. Véase la [contraauditoría11](https://github.com/gatehot59-star/corpus-legal-tarija/blob/29f393570c72cc65dd43747af6ffb18f3745de88/docs/auditorias/2026-09-20-11-audit-astra-brain.md). Esta corrección no reejecuta producto, no altera la evidencia06 ni cierra la revisión externa de logout. La versión original queda preservada en ad2badf1a8dee2d89470f405c0c90593875bad09.

## Veredicto breve

Astra encontró un fallo real de cierre de sesión: después de un logout rechazado con 403, la interfaz perdía el bearer necesario para reintentar mientras la sesión seguía activa en el servidor. El cambio cc2ca307 lo corrigió. Las verificaciones posteriores publicadas sostienen el arreglo en los escenarios ejecutados, pero no son aprobación externa del autor del fix ni certificación del piloto.

SOL dejó una auditoría histórica útil, no una auditoría nueva de PR20 que haya localizado en esta revisión. Su observación sobre el marcador de aislamiento no debe arrastrarse como defecto actual: el despacho actual consulta el marcador antes de login y reader. BFCache sigue NO MEDIDO para la restauración del documento real de PR20; un control sí restauró, pero el producto no alcanzó esa precondición.

Hallazgo documental actual: la descripción de PR20 sigue llamando «head final» a a8aeb301 y cita su CI de anoche. El head real es cc2ca307 y tiene otro CI exitoso. No corregí la descripción ni modifiqué producto en esta revisión.

## Autoría, alcance y fuentes

Soy BRAIN, autor de la implementación inicial de PR20. Esta entrega revisa auditorías y evidencia publicada; no simula ser un auditor independiente de mi propio producto. Astra fue autor del arreglo posterior y declara esa autoría en sus revisiones 03-05. La independencia del instrumento permite recomputar resultados, no elimina el sesgo de selección de casos.

Lectura de Git, páginas públicas de los informes, Nexus 71-75, búsquedas acotadas de Docs y mensajes, diff real a8aeb301→cc2ca307, guard actual de aislamiento y API de GitHub. No se ejecutó de nuevo el producto ni los 140 tests Python ni Chromium en este turno. Sí se ejecutó un recomputador nuevo sobre registros publicados y se consultó el CI actual.

Snapshot de main: d76ec10c365e568bd890c1fdea43a399ef350a36. PR20 abierto, merged=false; head cc2ca30760c486cad3154c619a20f94cf75cc691; base PR19 31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05. La diferencia posterior al cierre anterior modifica solo sistema/web/discovery_spike.html y tests/browser_discovery.cjs.

Fuentes primarias, todas bajo el snapshot indicado salvo el código del PR:

- [SOL, auditoría histórica PR8-PR11](https://github.com/gatehot59-star/corpus-legal-tarija/blob/d76ec10c365e568bd890c1fdea43a399ef350a36/docs/auditorias/2026-09-17-22-sol-pr8-pr11.md).
- [Astra01, hallazgo logout](https://github.com/gatehot59-star/corpus-legal-tarija/blob/d76ec10c365e568bd890c1fdea43a399ef350a36/docs/auditorias/2026-09-20-01-astra-pr20-independent.md).
- [Arreglo02](https://github.com/gatehot59-star/corpus-legal-tarija/blob/d76ec10c365e568bd890c1fdea43a399ef350a36/docs/agents/respuestas/2026-09-20-02-logout-retry.md).
- [Astra03, auditoría del arreglo](https://github.com/gatehot59-star/corpus-legal-tarija/blob/d76ec10c365e568bd890c1fdea43a399ef350a36/docs/auditorias/2026-09-20-03-pr20-logout-fix-audit.md).
- [Astra04, navegación y respuesta demorada](https://github.com/gatehot59-star/corpus-legal-tarija/blob/d76ec10c365e568bd890c1fdea43a399ef350a36/docs/auditorias/2026-09-20-04-delayed-logout-navigation.md).
- [Astra05, BFCache](https://github.com/gatehot59-star/corpus-legal-tarija/blob/d76ec10c365e568bd890c1fdea43a399ef350a36/docs/auditorias/2026-09-20-05-bfcache-pending-logout.md).
- [Código actual de la interfaz](https://github.com/gatehot59-star/corpus-legal-tarija/blob/cc2ca30760c486cad3154c619a20f94cf75cc691/sistema/web/discovery_spike.html).

No apareció un informe nuevo de SOL/OPUS sobre PR20 en el árbol de auditorías de main, los reportes Nexus revisados y la búsqueda acotada. No es una afirmación de ausencia en todo ClickUp o en otras ramas. Los mensajes antiguos de Custos no son evidencia de Corpus. No atribuyo a SOL los informes de Astra ni reabro la deuda histórica del agregador OPUS como defecto nuevo.

## Afirmaciones contrastadas

### 1. SOL: hallazgo histórico del marcador

CONFIRMADO el alcance histórico: probó lectura y autorización en la etapa PR8-PR11. La evidencia comprimida histórica se decodificó estrictamente: 281045 bytes, SHA256 f30b997bc58d13e1eb19d42aa71d9ae543d9d1fdee449e1bdbc42996f1652562.

REFUTADO como descripción de la estructura actual que el marcador solo se compruebe al emitir login. En sistema/api/isolated_login.py, IsolatedLoginApp.__call__ consulta la marca antes del despacho; falta de marca devuelve 403 ISOLATED_LOGIN_DISABLED y error SQLite devuelve 503 ISOLATION_UNAVAILABLE. Lo sostengo por lectura del llamador actual y por los experimentos posteriores publicados, no por una nueva corrida del producto aquí. No reabrir ese defecto por leer el informe antiguo fuera de fecha.

### 2. Astra01 y arreglo02: logout 403

CONFIRMADO el hallazgo histórico y su corrección delimitada. El caso original quitaba la marca, provocaba 403 en logout, la restauraba y demostraba que el mismo bearer aún obtenía 200. No era un supuesto ataque remoto; requería intervención en la fixture local.

El diff actual separa logoutToken del token ordinario, limpia inmediatamente resultados/texto/selección y restringe la interfaz a reintentar logout. Las acciones de login/búsqueda/lectura/guardar tienen guards durante ese estado. Confirmar logged_out===true borra ambos handles. pagehide/reload olvida la memoria local, pero no revoca por sí mismo en el servidor. El bearer retenido sigue teniendo privilegios del lado servidor: la restricción es del consumidor, no un nuevo tipo de token.

No confundir el paquete publicado de 34024 bytes de Astra01 con la captura local más extensa. La publicación es enfocada, y sus exclusiones están declaradas. El arreglo02 acredita sus propios reruns; no los cuento como tests nuevos de esta revisión.

### 3. Astra03: resultados recomputables, con un error inicial preservado

CONFIRMADO: independent-final y independent-repeat contienen 163 aserciones cada uno, todas con actual igual a expected y sin discrepancias de pass. Recalculé desde los registros, no desde el total del informe.

El primer instrumento independent-first sí tiene dos registros incompatibles con pass=true: real_failure_status conserva [403,200] frente a [403] y [503,200] frente a [503]. Es el error de referencia mutable ya declarado por Astra, no un hallazgo nuevo oculto ni evidencia de que el fix de producto falle. Las capturas corregidas no conservan ese defecto.

Los mutantes pueden dar rojo por la propiedad buscada: mutant_forget falla marker403:failure_retry_enabled, actual=true frente a expected=false (el actual es el estado disabled del botón); mutant_stale falla marker403:pending_content_cleared, ['',2,'ninguna'] frente a ['',0,'ninguna']. No se acredita detección por exit=1 solamente.

### 4. Astra04: navegación real no equivale a restauración BFCache

CONFIRMADO: definitive y repeat contienen 110 aserciones cada uno, todas consistentes. El control que escribe un estado STALE falla return_200:new_document_unchanged. Es un control del detector, no un mutante de producto.

Los ensayos usaron navegación real, pero el documento volvió con identidad nueva. No demuestran ejecución tardía en el mismo contexto JavaScript restaurado, ni prueban cancelación de socket por el simple retorno de fulfill. El primer requisito erróneo old_request_canceled está conservado y se descartó como instrumento, no como defecto de producto.

### 5. Astra05: el rojo significa precondición no alcanzada

CONFIRMADO: control-history-back y control-repeat tienen tres aserciones cada uno, incluida restauración del mismo documento y pageshow.persisted. El control con BFCache deshabilitado da rojo en same_document_restored, como debe.

NO MEDIDO: el comportamiento tardío de PR20 restaurado desde BFCache. Los cuatro intentos publicados del producto, pending200 y pending403 con repetición, tienen seis aserciones alcanzadas y fallan en same_document_restored porque cambió el UUID. Las comprobaciones posteriores de sesión B/callback no llegaron a ejecutarse. El control no-store también falla la restauración. Se registran razones nativas relacionadas con no-store y BrowsingInstanceNotSwapped; no se infiere una imposibilidad universal de BFCache.

Los rojos no prueban una vulnerabilidad del producto ni permiten decir que ese caso está aprobado. Tampoco justifican debilitar Cache-Control para conseguir un verde. No recomiendo otra ronda idéntica sin cambiar una pregunta concreta y pertinente.

### 6. CI actual y documentación vencida

CONFIRMADO por consulta nueva de la API: [job106060447751](https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35503942903/job/106060447751), head_sha cc2ca30760c486cad3154c619a20f94cf75cc691, completed/success. Diez pasos completed/success, ninguno skipped. Intervalo 20-sep 10:02:32..10:03:51 UTC, equivalente a 07:02:32..07:03:51 ART.

REFUTADO como estado actual el «Head final:a8aeb301» del cuerpo de PR20. Ese cierre fue verdadero anoche, antes del fix. No hay que borrar el recibo histórico; sí evitar usarlo como estado vivo. Conservé la respuesta completa del PR y del job en el paquete de esta revisión. La descripción no fue editada bajo este pedido.

No se descargó stdout de Actions: los conteos de tests siguen siendo de las evidencias locales publicadas, no del log remoto. CI exitoso no autoriza merge, piloto ni despliegue.

## Qué no se midió y qué conviene hacer

No nueva ejecución de producto, nueva selección externa de casos del fix, otros navegadores, accesibilidad, carga, expiración durante cierre, autorización legal del piloto o preparación operacional. El código inicial es mío y el fix es de Astra; repetir con esos mismos autores no convierte el proceso en selección externa.

Prioridad recomendada, sin emitir órdenes: actualizar el estado vivo de PR20 con el fix y CI vigentes; obtener una revisión externa acotada del cambio de logout, no otra certificación completa del proyecto; continuar las decisiones humanas de muestra/roles/consentimiento que separan una demo de un piloto. No convertir BFCache no alcanzado, las 169 omisiones históricas de cierre de fixtures o un score interno en bloqueadores automáticos del objetivo.

No cambié core, interfaz, tests, workflow, PR body ni estados de merge. No contacté auditores. No abrí un piloto ni emití credenciales. La entrega remota es únicamente este informe, su evidencia, un Doc público y el asiento de continuidad.

## Evidencia de esta revisión

Paquete: docs/agents/evidencia/2026-09-20-06-revision-sol-astra.json. Codec xz+base64; decodificado 32816 bytes; SHA256 a27d028cb3101c252c2ec702efb060a867ff18cd54ecb803d3ec199147b6ed28.

Contiene comando exacto Python y fuente embebida, exit=0, stdout íntegro, stderr vacío, manifiesto de los cinco paquetes de entrada, respuesta API completa del PR y del job. El comparador usa serialización JSON canónica para no confundir true con 1; comprueba el rechazo de una población vacía y casos negativos. No ejecuta el código del producto. Los registros originales permanecen en las cinco evidencias publicadas de Astra bajo docs/agents/evidencia/, con los mismos nombres base que sus informes.

Recomputación reproducible: decodificar los cinco paquetes originales a una carpeta; extraer el array command del paquete de esta revisión; adaptar únicamente la carpeta de entrada si no se usa brain-env; ejecutar Python. El programa imprime registros fallidos completos, no solo un total. Los resultados adversos iniciales no se borran ni se suman a los positivos finales.

Inventario histórico leído en sus secciones relevantes y método §5 consultado: documentación puede publicarse directamente, código no. No transfiero el estado viejo de MUDH a Corpus ni uso su lista de binarios como una medición nueva. El instrumento efectivamente usado aquí fue Python del servicio build de brain-env y la API pública de GitHub.

## QA del informe, no del producto

TITAN FULL. Completitud 14/15: alcance y exclusiones explícitos; búsqueda SOL acotada, no exhaustiva. Razonamiento 9/10: separa regresión corregida, error del instrumento y precondición no alcanzada; sin rerun de producto. Documentación 10/10: fuentes versionadas, estados y captura recuperable. Innovación 4/5: comparación estructural tipada y contraste del estado vivo sin repetir todos los bancos. Proceso QA 5/5: positivos y negativos se recalculan y el CI se verifica contra el head exacto. Total 42/45 = 93.33/100. N/A 55: ejecutabilidad15, seguridad15, testing15 y DevOps10 de producto, porque esta entrega es un informe, no una nueva versión del sistema. El score no aprueba PR20 ni sustituye review externo.

Errores propios de la revisión: una lectura combinada se truncó; no usé la cola no leída de OPUS para nuevas conclusiones. Un git diff sin separador de ruta falló y fue repetido con el separador correcto. La recomputación final devolvió exit0 con stderr vacío. No hay nueva medición de capacidad ni nuevos tests de producto que atribuirse.

--- METODO TITAN ---
Accion delicada: NO, solo documentación y recomputación de evidencia
Modo aplicado: TITAN FULL
Rubrica: 42/45 -> 93.33/100 del informe
N/A declarados: 55, criterios de producto fuera de esta entrega
Review externo: sin hallazgos emitidos sobre esta revisión (deuda), no aprobación
Instrumento: Python en brain-env, exit0; evidencia cruda recuperable y API GitHub contra cc2ca307
