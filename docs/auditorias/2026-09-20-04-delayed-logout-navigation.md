# PR20: respuesta de logout tardía tras navegar, sin contaminación observada

## Pedido y conclusión

Probar respuestas demoradas de logout después de navegar fuera de la página. **No se observó contaminación de la nueva página ni de una sesión nueva al volver**, tanto si el servidor había aceptado el cierre como si lo había rechazado. Alcance: Chromium, navegación real entre documentos nuevos; no BFCache.

[PR20](https://github.com/gatehot59-star/corpus-legal-tarija/pull/20), head probado y reconsultado `cc2ca30760c486cad3154c619a20f94cf75cc691`, base `31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05`. Sigue abierto y no mergeado. El sujeto es `sistema/web/discovery_spike.html` servido por el CLI real `demo_discovery.py`, consumidor Chromium. No se cambió producto, workflow, permisos, PRs ni servicios reales. Sin merge ni despliegue.

Astra implementó el arreglo previo y opera estas pruebas. Son un instrumento y expectativas nuevos, no una revisión por otro autor. El pedido actual es el ensayo de navegación, no aprobar PR20 completo.

## Método y oráculo

brain-env por Gateway MUDH; GitHub para refs y documentación; ClickUp público y Nexus para entrega. Node24.18.0, Python3.12.14, Playwright1.63.0. Chromium real del runtime ya utilizado en la jornada. Archives aislados, fixtures nuevas por caso, conexiones SQL cerradas y servidores detenidos.

El instrumento obtiene con `route.fetch` la respuesta real del backend y la retiene mediante una promesa antes de entregarla con `route.fulfill`. Es demora inyectada por Playwright, no un proxy de red ni una respuesta inventada. El servidor responde200 tras revocar o403 real después de retirar temporalmente el marcador de la fixture; este se restaura antes de la siguiente acción.

Esperado fijado antes: sin navegar, liberar la respuesta debe actualizar la UI según200/403; después de navegar, liberarla no debe alterar el documento visible ni el bearer de una sesión nueva. Se observa una ventana de300ms después de liberar, más verificaciones HTTP y cierre posterior de la sesión nueva. No se afirma ausencia de efectos durante tiempo ilimitado.

La página auxiliar `/audit-away` es HTML fijo servido por el instrumento. Se usa `page.goto` para salir y `page.goBack` para volver: no se sustituye navegación por disparar manualmente pagehide. Se registran eventos pagehide/pageshow y un UUID por documento. La clave de prueba `sessionStorage.auditLifecycle` almacena solo eventos, paths y UUIDs, nunca credenciales; ese es un agregado del instrumento, no del cliente.

## Matriz ejecutada

Seis escenarios: quedarse, salir y permanecer fuera, salir y volver antes de liberar; cada uno con respuesta real200 y403. **110 comprobaciones explícitas**, exit0. Repetición con el mismo instrumento final, otro archive y nuevas fixtures: **110 comprobaciones**, exit0. El conteo incluye positivos, preparación y limpieza; no son110 escenarios ni porcentaje de cobertura.

1. Quedarse +200: respuesta retenida no confirma antes de tiempo; liberada, llega el evento de respuesta de la sesiónA y la UI confirma el cierre.
2. Quedarse +403: respuesta real rechazada liberada produce cierre no confirmado y reintento disponible.
3. Salir +200: la página auxiliar permanece idéntica tras liberar. La sesiónA ya estaba revocada antes de liberar la respuesta.
4. Salir +403: página auxiliar intacta; la sesiónA seguía autorizada antes de liberar. Navegar no convierte el rechazo en revocación.
5. Salir, volver e iniciar sesiónB con la otra identidad + respuesta vieja200: el documento nuevo y el contenido deB permanecen iguales; B sigue autorizada y puede cerrar normalmente; A continúa revocada.
6. Misma secuencia con respuesta vieja403: B no se borra ni pierde acceso; cerrarB no revocaA. La sesiónA continúa activa hasta la limpieza explícita del ensayo. Este es el límite conocido de abandonar un cierre rechazado, no una regresión nueva.

Al volver se midió un UUID de documento diferente y todos los eventos `persisted` fueronfalse. **BFCache NO MEDIDO**: no se conservó el contexto JavaScript viejo. En los casos navegados, Playwright no emitió evento `response` paraA durante la observación ni `requestfailed`; `fulfill` retornó sin error. No se interpreta ese retorno como entrega efectiva al documento destruido. Los200 observados después al cerrarB están etiquetados comoB, no como respuesta tardía deA.

La conclusión es sobre la pantalla/sesión nuevas bajo navegación completa. No atribuye causalidad exclusiva a `generation` ni demuestra que ese guard funcione si un documento fuera restaurado desde BFCache.

## Control de sensibilidad y error propio

Control `detector_control`: después de volver, iniciarB y liberar la respuesta vieja, el instrumento escribe deliberadamente `STALE RESPONSE DETECTOR CONTROL` en el status del documento actual. Sale1 exactamente en `return_200:new_document_unchanged`; el mismo comparador pasa en las corridas normales. Esto prueba sensibilidad del detector a contaminación visible, **no es un mutante del producto ni un bug encontrado**.

El primer intento exigía un evento `requestfailed` después de navegar. Ese supuesto no se sostuvo: salió1 en `away_200:old_request_canceled`. La API de observación no garantiza esa señal para una ruta interceptada después de destruir el documento. Se retiró esa exigencia ajena al contrato, se conservaron ambos booleanos como observaciones y se juzgó la propiedad pedida mediante snapshot y autorizaciones reales.

Primera salida y versiones del instrumento quedan preservadas. El logger inicial no guardó el timeline del caso que falló; no se reconstruye ni se llama íntegro ese dato ausente. Las versiones posteriores registran los timelines en finally, también para el control rojo. Un segundo ajuste etiquetó cada respuesta A/B para no confundir el cierre nuevo con el viejo. Las dos corridas definitivas usan exactamente esa versión final.

## Custodia y reproducción

[Evidencia](https://github.com/gatehot59-star/corpus-legal-tarija/blob/main/docs/agents/evidencia/2026-09-20-04-delayed-logout-navigation.json): xz+base64, **126.702 bytes decodificados**, SHA256 `30814e05e02e7ac6af5ea4b2432d6e14d87a7776636588d7d39f09429bfc43ef`. Incluye script completo, deltas de versiones previas, stdout/stderr completos de todas las ejecuciones capturadas, comandos, entorno, snapshots, eventos, estado final de PR y scan de procesos. Los bearers se comparan con booleanos y no se registran.

Instrumento final `logout_navigation.cjs`, SHA256 `78bead8611e7d33c82abc416c9d1cdd6ae50bc36f513147c82a61a865ce185e4`. Extraer el head indicado, decodificar/verificar el JSON y guardar `instrument.source`; ejecutar `node logout_navigation.cjs <archive> all`. El modo `detector_control` debe fallar en el comparador indicado. La copia de producto nunca es reescrita por el script.

Cada caso cierra sus sesiones ficticias mediante POST, detiene el servidor con exit0 y comprueba que el listener cerró. Scan final de procesos propios vacío. No se usan hashes físicos SQLite ni se infiere consistencia del WAL.

## Veredicto y límites

CONFIRMADO: las respuestas tardías ensayadas no cambian la página auxiliar ni el documento nuevo con sesiónB; el servidor conserva la distinción entreA yB; controles positivos sin navegación prueban que liberar la respuesta puede cambiar una UI viva; control negativo prueba que el comparador puede detectar contaminación.

NO MEDIDO: BFCache real, callbacks del contexto viejo restaurado, cancelación de red a nivel socket, matriz Firefox/WebKit, navegación entre orígenes, efectos posteriores a la ventana observada, concurrencia entre pestañas y producción. Tampoco se reejecutó aquí toda la suitePython ni se inició CI nuevo. El propósito fue cerrar el hueco concreto de navegación, no elevar el alcance de la auditoría anterior.

GateI PASA en alcance con la corrección del supuesto de transporte, positivos y repetición; mutación causal de guard de producto N/A, no se afirma. GateII distingue efecto observado, simulación de demora, límite conocido y datos ausentes. GateIII se completa con readback remoto, pertenencia a main, Doc público y Nexus antes del chat final.

--- METODO PROMETEO ---
Pedido acotado de prueba; sin acción delicada de producto. Máquina: brain-env. ASTRA AUDITOR CORPUS, oráculo fijado y gates separados; sin nota usada como aprobación. Mismo autor del arreglo, revisión externa pendiente. Artefactos: este informe y evidencia en git, Doc público y registro Nexus enlazados al cerrar. Sin merge ni despliegue.
