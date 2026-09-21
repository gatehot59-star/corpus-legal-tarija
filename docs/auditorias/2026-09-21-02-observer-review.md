# Astra: el observador sigue certificando ventanas que no observó

21-sep-2026, ART. Revisión del pase de auditoría y ejecución focalizada sobre el instrumento de Brain. No implementación, merge, despliegue ni nuevos eventos de Actions.

## Resultado e impacto

**CONFIRMADO:** el hallazgo del pase01 es reproducible sobre la fuente publicada. Además, se ejercitaron dos formas explícitas de hueco temporal: ocho consultas con un salto interior de210 segundos y solamente dos consultas en los extremos de cinco minutos. Ambas producen BOUNDED_ABSENCE cuando el contrato exige INCOMPLETE.

Esto impide usar este observador para cerrar la comparación del filtro de CI según el protocolo aprobado. No demuestra un fallo del workflow ni que Brain haya aprobado falsamente el experimento: su informe33 lo declara INCOMPLETO y PR21 sigue abierto. No son cinco vulnerabilidades independientes: son cinco escenarios de una familia de defectos de cobertura, reinicio y parada.

La intervención siguiente es de **Brain implementador**: persistir y validar cobertura por episodio y estado de error/parada antes de emitir veredictos. Esta auditoría no modificó el observador. Una consulta de hoy no reconstruye las muestras perdidas ayer.

## Qué se leyó primero y qué se ejecutó

El Doc seleccionado por Abraham, auditoría integrada del18-sep, se leyó como antecedente exacto. No se sustituyó su conclusión histórica por una afirmación sobre el producto actual. Nexus87 a104 permitió localizar el pase nuevo en docs/auditorias/2026-09-21-01-brain-lab-observer.md, commit a7544842862f2798790bb2f00ab4687e9b8ee27f. El pase localizado es de Astra, no una entrega nueva atribuible a SOL.

Se leyeron el pase, Brain33 y el observador completo; se consultaron refs vivas y las afirmaciones operativas del método/inventario de MUDH sin trasladar deuda de ese producto a Corpus. El contrato temporal se contrastó con docs/adr/2026-09-20-docs-only-trigger-test.md en architect1d14895c75468953ee3e1d3d0554d1c63907684a: líneas65/69 exigen lecturas cada15 segundos, ventana completa y cierre; una única consulta ausente no alcanza. Las correcciones posteriores sobre inicialización del laboratorio no eliminan ese requisito.

El antecedente01 ya había sido leído al fijar la matriz nueva. **No es un ensayo ciego** ni una nueva instancia libre de antecedentes. Los esperados se registraron antes de la ejecución actual, derivados del contrato de cobertura y no del resultado que devuelve observe().

Sujeto exacto: observe() de observer.py,6802bytes, SHA256 2a727b5c2a21e9d9f197352501bfd1ffdb5aa038a64a1851396b9789eb151a3d. Se recuperó de la evidencia publicada01 y se comprobó igualdad con el archivo operativo antes y después. No se encontró una corrección posterior en las refs consultadas. Main inicial a7544842862f2798790bb2f00ab4687e9b8ee27f; architect1d14895c75468953ee3e1d3d0554d1c63907684a; PR21 3b92dc432f285c00d5a45e717883c5c6e3fe46f9.

Se ejecutó observe() real en copias nuevas con ROOT propio. Solo reloj, espera y lectura de API se sustituyeron por fixtures deterministas; el tratamiento de episodios, errores, escritura de resultados y parada es el del sujeto. Son pruebas de lógica del observador, no nuevas observaciones temporales de GitHub.

## Matriz y resultados nuevos

Cada nombre corresponde a un escenario, no a cada consulta interna:

| Escenario | Entrada | Esperado | Observado |
|---|---|---|---|
| complete | 21 consultas vacías de1000 a1300, cada15s | BOUNDED_ABSENCE | BOUNDED_ABSENCE |
| first_late | Una consulta vacía en1301 | INCOMPLETE | BOUNDED_ABSENCE |
| interior_gap | 1000,1015,1030,1240,1255,1270,1285,1300 | INCOMPLETE | BOUNDED_ABSENCE |
| two_endpoints | 1000 y1300 solamente | INCOMPLETE | BOUNDED_ABSENCE |
| persisted_error | Error403 persistido y consulta nueva en1301 | INCOMPLETE | BOUNDED_ABSENCE, errors=[] |
| preexisting_stop | Stop preexistente y consulta en1301 | INCOMPLETE | BOUNDED_ABSENCE, después retorna |
| same_process_error | Error en segunda consulta de una ventana de21 intentos | INCOMPLETE | INCOMPLETE, conserva el error |
| positive_run | Run completado/success correctamente asociado | PASS | PASS |
| wrong_head | Mismo run con head incorrecto | INCOMPLETE | INCOMPLETE |

Cinco de nueve escenarios incumplen la propiedad esperada. Esto NO se presenta como banco verde: el supervisor termina0 porque conserva los resultados de la exploración; el veredicto por caso está en conforms y las columnas expected/actual.

Se repitieron complete, interior_gap y persisted_error en tres scratches nuevos: mismo resultado. En un falsador local, verdict se reemplazó por una función que siempre devuelve INCOMPLETE: la MISMA aserción de complete pasa en el original y falla en esa copia. El oráculo no aprueba cualquier salida. Este falsador comprueba el instrumento de revisión; no es una corrección del producto.

La suite del autor selftest pasó sus26 controles por separado. Eso no contradice el hallazgo: esos controles cubren asociación/paginación/verdict, pero no las trazas temporales de observe() aquí ejercitadas. El control same_process_error distingue el mecanismo: el error sí bloquea durante la misma llamada; al reentrar, errors vuelve a una lista vacía y no recupera lo persistido.

## Causalidad y aceptación de una corrección

observe() decide closed por now >= started+300, sin exigir primera muestra o continuidad temporal por episodio. Inicializa samples/errors en memoria al entrar y verifica stop después de escribir el veredicto. Es suficiente para explicar las salidas observadas; no hace falta atribuirlas a la API ni cambiar el workflow.

Gravedad operativa: bloqueante para certificar este experimento bajo SU protocolo, no vulnerabilidad remota de Corpus. Dueño propuesto: Brain, sin nueva asignación ni mensaje.

Una corrección aceptable debe preservar el positivo completo y el run válido; mantener INCOMPLETE ante inicio tardío, huecos grandes, error persistido y parada previa; conservar historial y errores por episodio al reiniciar; y comprobar la parada antes de emitir un veredicto concluyente. Debe mantener el rechazo de head/evento/base ajenos. La política de tolerancia a latencia debe ser explícita: este ensayo no decide si16 segundos es aceptable, porque los contraejemplos tienen huecos de210 o300 segundos.

No basta agregar un contador global de21 consultas: la cobertura debe pertenecer a cada episodio y a sus timestamps. Esta última frase es criterio de diseño, no una nueva prueba ejecutada de ese hipotético arreglo. No se implementó ninguna solución.

## Estado remoto consultado

API paginada con per_page100, sin Link next en las respuestas obtenidas: cuatro PRs del laboratorio, total_count3 runs y tres filas. Los tres jobs se consultaron con sus pasos; cada uno muestra siete pasos exitosos, incluidos los tres bloques de compilación/tests. No se descargó stdout de Actions ni se atribuyen111 tests remotos a la API de jobs.

- PRlab1 NEW-CODE: head531e500ae8b073003d73f7020fd6cfd50e7dde29, basefdf2519ecb12fcb3e1fcb7eedc1151c23d0d04cc; run35548189544/job106177854186, success,00:35:36..00:36:19UTC21-sep.
- PRlab2 OLD-DOCS: head85635ef92e8a0a72937ca55e5b507b6ceed62103, basec82c684f71a235960504cf46092053c653fd7f48; sin run asociado en este corte. NO acredita cobertura de la ventana anterior.
- PRlab3 NEW-DOCS: headf39c3e93ef1bdcdcf4630fae56a6f7cd60695cee, basefdf2519ecb12fcb3e1fcb7eedc1151c23d0d04cc; run35548190401/job106177856329, success,00:35:37..00:36:19UTC.
- PRlab4 OLD-CODE: head48eb96eff0219414ccaf1eb9b45d959ab7cf36f7, basec82c684f71a235960504cf46092053c653fd7f48; run35548189753/job106177854805, success,00:35:36..00:36:13UTC.

Los campos de asociación exactos se preservan, no solo nombres de brazos. El matcher histórico se reutilizó para asociar el snapshot y sus claves head/base/PR se contrastaron directamente. No se afirma un nuevo ensayo independiente de toda su semántica de asociación.

Corpus PR1/17/18/19/20/21 aparecen abiertos en el corte. Reviews18/20/21 devuelven listas vacías. Es evidencia de esas superficies, no demostración de ausencia de una revisión privada. Heads18=2231ca8edbe4c0b6eba88156d5abd087bbf9e51f y20=c1e54ad0035f23d8ab549e9b16e3a6751bc1b2d2 no cambiaron. PR21 conserva3b92dc43. No se produjeron synchronize ni otros eventos remotos.

## Autoría y qué queda pendiente

Esta conversación contiene implementación previa de logout y tests de PR20. Esta auditoría del observador no cierra G2 de logout ni una revisión personal independiente de PR18. Los bancos anteriores de sesión no se volvieron a ejecutar por ceremonia; sus resultados siguen siendo históricos y ligados a sus revisiones. El hold sobre17/18/19 y las condiciones de21 permanecen.

El pase pedía atender también esos bloqueos: se comprobó su estado, pero NO se presenta esta medición como una nueva revisión de login/logout ni como aprobación ajena. Para levantar independencia personal hace falta la revisión realmente separada, no otra etiqueta en el mismo historial.

Prioridad accionable: Brain corrige el observador; se revisa el delta con estos positivos/negativos; se resuelve explícitamente cómo tratar el episodio cuya cobertura se perdió antes de consumir los dos eventos restantes. Consultar tarde no repara la ventana y esta orden no autoriza nuevos episodios de reemplazo. Después corresponde integración bajo autorización y piloto pequeño con muestra/permisos aprobados, no otra ronda genérica de111 tests.

NO MEDIDO: cobertura temporal real perdida, synchronize pendientes, corrección del observador aún inexistente en el corte, review personal independiente18/logout, stdout de los jobs históricos y aptitud de un piloto jurídico real. Tampoco se vuelve a publicar como propia la captura histórica integral local de Brain33.

## Evidencia, reproducción y custodia

[Evidencia canónica](https://github.com/gatehot59-star/corpus-legal-tarija/blob/48bcab7afd681be34046707f55b43f2e5829169a/docs/auditorias/2026-09-21-02-observer-review/evidence.xz.b64). Base64 estricto de XZ, un bloque de13352bytes; JSON original74494bytes, SHA256 d97a3f76fed283bc44e6871c1037c238ca478dc47e61d445bb901eaa6c9c279b. Recuperado desde Git, codificado y decodificado comparados BYTE_EQUAL con el original; commit perteneciente a main, merge-base exit0.

Incluye fuente completa de observer_review.py y observer.py, matriz previa, nueve escenarios, tres repeticiones, falsador, archivos iniciales/finales de cada copia, tiempos de consultas, stdout/stderr completos de las ejecuciones nuevas, selftest del autor, salida completa del supervisor, refs de cierre y estado remoto proyectado. La captura API excluye cuerpos globales: conserva campos pertinentes, URLs, estado, Link, timestamp y hash del cuerpo. Un hash de cuerpo excluido NO equivale a publicarlo completo. No secretos ni credenciales; no listeners ni procesos desacoplados iniciados; requests cerrados por context manager.

La evidencia anterior01 se decodificó:111342bytes, SHA25689b922bc7ec093f9ba9b5761e76baaf1c60b31194cd0f711ce1a45eab59a67d6. Se usó como fuente del sujeto, no como sustituto de estas nuevas corridas.

Reproducción: extraer los campos source y observer_source del JSON; leer sus efectos antes de ejecutar. El runner usa lectura Git del paquete01 y APIs públicas, y crea solo temporales propios. En este entorno se ejecutó python3 /workspace/astra-observer-review-2102.py, exit0; fuente ejecutada10296bytes SHA2562bdfd13a3f16f3f45f24e8929a8bd41388e6158b81f186c07aac79dbcb5574fb. Para otra máquina deben adaptarse GIT y el prefijo temporal; no se afirma portabilidad sin cambios. La extracción de los casos permite recomputar expected==actual sin red.

Recuperación local: /workspace/astra-observer-review-s52s5i0b, puntero /workspace/astra-observer-review-current.txt. Error propio de preparación: el transporte del archivo auxiliar agregó signos+ al inicio de líneas; py_compile falló antes de transferir/ejecutar. Se normalizó la copia exportada, compiló y verificó su hash antes de correr. Ninguna corrida de candidato se ocultó o invalidó por ese error. Primer intento de lectura de Brain33 carecía del objeto local; fetch explícito lo recuperó antes de usarlo.

## Control final

Modo LIGERO por revisión focalizada de un instrumento ya identificado, no implementación de una frontera de confianza. Revisor, verificador y control final son funciones del mismo operador. Sin nota global del producto.

Gate I PASA para validez de esta auditoría: sujeto exacto, expectativa por contrato antes de ejecutar, positivo/falsador pertinentes, tres repeticiones frescas, fuentes y capturas completas según exclusiones declaradas. El candidato FALLA cinco escenarios; no confundir gate experimental con aprobación del sujeto. HTTP de eventos nuevos y SQLite N/A: no se emitieron eventos ni abrieron bases.

Gate II PASA en alcance: no inventa aprobación de Brain, distingue defecto del instrumento, persistencia vs misma corrida, evidencia actual vs histórica y revisión personal pendiente. La matriz no pretende exhaustividad temporal.

Gate III EN CIERRE al commitear este informe: evidencia ya publicada y verificada; lectura remota del informe, Doc público en Space validado y Nexus se completan después en orden. El registro final de continuidad y el Doc acreditarán esas operaciones, sin anticiparlas acá. Este orden de publicación no extiende la cobertura ni autoriza un merge.
