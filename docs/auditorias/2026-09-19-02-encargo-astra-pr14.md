# Encargo para Astra: auditoría posterior al merge de PR14

19-sep-2026 ART. Pedido confirmado: audit_merged_pr14 / prepare_astra_pr14_post_merge_audit. Esta entrega prepara el encargo; NO ejecuta la auditoría, NO la delega a un agente y NO autoriza otro merge. Abrir este encargo en una conversación con el skill ASTRA AUDITOR CORPUS.

## Sujeto congelado y situación comprobada

Repositorio gatehot59-star/corpus-legal-tarija. PR14 https://github.com/gatehot59-star/corpus-legal-tarija/pull/14 figura closed/merged:true en la consulta de este turno. Integración histórica: 9913d8dd5074d6aedd0d261c42caea6480e794fe, 18-sep-2026 22:43:01 ART. Incluye PR15 de CI; no auditar solamente la cabeza inicial 5ac0da7.

Main observado por fetch: 7d506fe5f51fc90fc2a7e5c47ed3a665f0cc5f4a. merge-base --is-ancestor desde 9913d8d devuelve0; diff --name-status entre ambos contiene únicamente diez archivos bajo docs/. El producto y workflow no cambiaron entre esas revisiones. Congelar 9913d8d para reproducir lo integrado, y comparar contra main recuperado al inicio y al cierre; si cambió el producto, separar los resultados por revisión.

Archivos directos: sistema/api/demo_aislada.py, tests/test_demo_aislada.py, sistema/DEMO-AISLADA.md y .github/workflows/clean-snapshot.yml. Consumidor real: CLI init/serve -> IsolatedSessionApp -> login, política y lector. Servidor histórico, PR1, PR16, bases reales y despliegue quedan fuera. No sustituir el sujeto por el PR abierto más reciente.

## Contexto que evita repetir trabajo

Leer docs/agents/respuestas/2026-09-18-08-demo-integrada-main.md y las capturas 2026-09-18-08-demo-main-tests.json / 2026-09-18-08-demo-merges-ci.json en docs/agents/evidencia/. Las 97 pruebas y CI success son antecedentes del implementador, NO resultados nuevos de este encargo. CI medido sobre la cabeza combinada de PR14; el workflow tiene pull_request/workflow_dispatch, no push a main. No transformar la ausencia de una corrida en main en verde ni en defecto por sí sola.

Nexus49 y docs/auditorias/2026-09-19-01-astra-pr16-cuarentena.md documentan una auditoría posterior de PR16: no sustituye esta auditoría del lanzador. Reusar sólo evidencia cuyo instrumento, revisión y propiedad coincidan. Allí se midió falta de cierre explícito en fixtures heredados de tests/test_exact_http.py: 41 conexiones,24close,17sinclose, con observador que retiene referencias. Es deuda del instrumento, NO fuga productiva demostrada ni defecto nuevo de PR14. No repetir una acusación sin atribuir el caller.

La copia ingenua de un backup viejo que reabre accesos ya está documentada en recibo09 y en la auditoría de PR16. No presentarla como hallazgo nuevo del reinicio de PR14: reiniciar sobre el mismo store no equivale a restaurar un estado anterior. Recuperación y reapertura siguen fuera de este encargo.

## Encargo listo para ejecutar en Astra Auditor

Auditá PR14 ya integrado, no lo implementes ni lo mergees. Usá el núcleo común del skill: Control final, Entorno y continuidad, Pruebas independientes y Evidencia y cierre. Recuperá inventario y método en git, Nexus y los antecedentes anteriores. La independencia es del oráculo, no de tu nombre: este encargo lo prepara el mismo operador que implementó PR14. Fijá expectativas antes de ejecutar, sin importar helpers ni constantes del banco del autor como fuente de verdad.

1. Compilación y arranque real. En scratch nuevo extraído del SHA congelado, compilar y ejecutar init/serve como procesos CLI reales con puerto efímero. Comprobar ready, PID vivo, listener literal127.0.0.1 y primera lectura autenticada. No alcanza instanciar la clase en el proceso del test. No dejar servidor permanente.
2. Recorrido útil e identidad. Dos identidades y dos sesiones de una identidad; golden independiente con Unicode/CRLF y paginado completo. Login no concede permiso: retirar el grant en fixture propio debe negar lectura aun con login válido. Logout de una sesión ->403 para ella,200 para las otras; logout repetido conserva la negación. SQL independiente contrasta revocación y concesiones, sin exponer secretos.
3. Persistencia sin reaprovisionar. Terminar procesoA por SIGTERM, verificar salida y puerto cerrado, iniciar procesoB con PID distinto sobre el mismo store. La sesión revocada sigue403 y las otras conservan acceso si no expiraron. Comparar estado lógico antes/después y candidato frío; serve no resetea sesiones, renueva grants ni migra esquemas. Repetir el caso decisivo en fixture nuevo. No llamar crash-test a un apagado ordenado.
4. Fallo cerrado antes de escuchar. Sin --isolated-demo, init no crea archivos y serve no escucha ni modifica fixtures. Probar destino existente, store ausente, marcador ausente, login_clock ausente, texto alterado, symlink/hardlink/FIFO, permisos inválidos, sidecar y puerto ocupado. Verificar bytes y/o filas coherentes y ausencia de ready, no sólo exit2. Nunca usar bases ajenas; propietario malicioso con el mismo UID queda fuera del contrato.
5. Frontera HTTP y apagado. Host incorrecto y Origin presente (también vacío) deben negar; usar sockets crudos cuando una librería normalice cabeceras. Control positivo con Host esperado y sin Origin. Probar solicitud local incompleta con presupuesto explícito, que la conexión se cierre y que el proceso siga atendiendo después; medir SIGTERM en reposo y durante esa solicitud. El timeout2s no se debe vender como plazo total contra envío lento ni protección DoS productiva. Registrar tiempos y clasificar cualquier espera dentro del contrato real, sin umbrales inventados a posteriori.
6. Instrumento y CI. Revisar filtros, permisos, checkout fijado, propagación de errores y paso CLI del workflow. Ejecutar los bloques exactos una vez si hace falta cerrar regresión sobre el SHA congelado; no duplicar las12pruebas heredadas de login. Reconsultar checks como metadatos históricos, sin iniciar Actions/VM ajenos ni atribuir al log remoto los conteos locales. Separar suite del autor de banco nuevo y deuda de recursos de ambos.

## Falsadores obligatorios, sólo en copias

Positivo pertinente primero. MutaciónA: omitir consentimiento explícito; la aserción de no crear/no escuchar debe fallar por ese efecto. MutaciónB: borrar revoked_at al arrancar; el caso de reinicio debe observar200 donde exige403. MutaciónC: quitar guard Host/Origin; la prueba HTTP debe detectar la aceptación indebida con control positivo intacto. Guardar diff exacto, salida completa y aserción afectada. Un exit1 por import, timeout accidental o baseline ya rojo no prueba sensibilidad. No commitear producto mutado ni corregir el producto por iniciativa propia.

## Recursos, evidencia y criterios de cierre

Cerrar SQLite explícitamente con closing/finally; with connection confirma transacciones pero no cierra. Para hashes, detener escritores y fijar si se mide archivo principal, WAL, snapshot o filas. No interpretar checkpoint como pérdida. En finally detener hijos propios y comprobar PID ausente y puertos cerrados, también en mutantes/timeouts. No borrar árboles ajenos.

Por afirmación: input permitido -> esperado previo -> instrumento -> podía dar rojo por esa propiedad -> observado -> CONFIRMADO/REFUTADO/NO MEDIDO -> límite. Para cada defecto: introducido/heredado/instrumento, reproducción mínima, impacto, precondiciones y aceptación de arreglo. No emitir porcentaje de producto ni comparar modelos. Con defecto o anomalía no explicada, detener recomendación favorable y reportar; no revertir, corregir ni mergear automáticamente.

Entregar informe propio y captura íntegra (comandos, fuentes, fixtures, stdout/stderr, retornos, mutantes, recursos), excluyendo Authorization, tokens, passwords y datos reales. Publicar evidencia textual reversible e informe en git conforme a permisos vigentes, recuperar y comparar bytes, Doc público en Space validado y reporte propio en Nexus. No truncar ni marcar el trabajo terminado sólo por compilar. Reconsultar main al cierre y separar delta documental de producto.

Respuesta final: veredicto acotado sobre PR14 integrado; qué falló o qué intentos no hallaron fallos; qué no se midió que importaba; archivo commiteado y Doc. Esta auditoría NO concede un nuevo merge, no decide sobre PR16 ni certifica despliegue/piloto, validez jurídica, restauración, apagón, TLS, carga o adversario con mismo UID/root.

## Estado de ESTA preparación

CONFIRMADO documentalmente: PR14 integrado y sin delta de producto desde el merge hasta main observado; existencia del antecedente AstraPR16 y deuda de fixtures. NO MEDIDO en este turno: compilación, tests, arranque y seguridad del lanzador. No se emitió veredicto experimental ni se inició otra instancia de Astra.

Gate I: sujeto y comparación Git comprobados; oráculo/runtime/mutantes N/A para preparar instrucciones. Gate II: encargo delimitado con aceptación, límites y antecedentes; no aprobación del producto. Gate III al escribir: publicación/relectura/Doc/Nexus pendientes, a completar y registrar en el cierre de continuidad de este encargo. No reescribir el estado experimental por completar trámites.

Evidencia documental separada: docs/auditorias/2026-09-19-02-encargo-astra-pr14/evidencia.json. Captura acotada a cuatro comandos Git, stdout/stderr íntegros; no pretende ser captura de pruebas ni exportación de todo el contexto consultado. SHA256 original33111ea6c828ace4854f83f006b3c6a2d2e772dcd2e665ac55a45aed93be21f5.
