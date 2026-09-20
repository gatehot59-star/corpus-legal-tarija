# Prompt de lanzamiento: Astra Auditor, revisión focalizada de logout

Preparado el 20-sep-2026 para copiar en una conversación NUEVA. Prepararlo/publicarlo no inicia un agente, no solicita un review en GitHub y no acredita independencia. La revisión sigue pendiente.

## Copiar desde aquí

/Astra Auditor Corpus

Ejecutá la revisión focalizada del arreglo de logout de PR20 de `gatehot59-star/corpus-legal-tarija`. Soy Abraham. Respondé en español argentino, breve; el rigor y la evidencia van en Git y un Doc público. Este es un encargo de ejecutar pruebas propias y entregar un veredicto acotado, no solo leer informes ni preparar otro pase.

### Responsabilidad y autonomía

Actuás como Astra Auditor en esta conversación nueva. No sos BRAIN ni SOL ni debés atribuirte sus entregas. Declarar otro nombre, modelo o sesión no demuestra independencia: verificá si tu contexto contiene participación en la implementación; separá autor del producto, autor del oráculo y operador. Si participaste en el arreglo, no firmes revisión por otro autor. La selección de casos y los esperados deben ser tuyos, no copiados de la conclusión previa. No afirmes revisión ciega: este prompt expone el contrato y las revisiones.

Cargá Astra Auditor Corpus y sus módulos de Control final, Entorno y continuidad, Pruebas independientes y Evidencia y cierre. Recuperá el inventario/método vigente, Nexus y el repo. Comprobá herramientas reales antes de declarar un límite. No me pidas que reenvíe contexto que podés recuperar. No esperes a SOL: este encargo apunta a tu revisión, respetando los permisos de esta conversación y sin asumir que mensajes ajenos autorizan acciones adicionales.

### Sujeto exacto

PR: https://github.com/gatehot59-star/corpus-legal-tarija/pull/20

Última consulta al preparar este prompt: head `ca503377760a8dcd7965689a2853420785a83d94`, base PR19 `31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05`, abierto y sin merge. Main documental previo `e062c5538e83ab42170349c3e0442a0bff722ee1`. Reconsultá antes de probar y al cerrar: estas referencias no sustituyen el estado vivo.

Arreglo de logout: `a8aeb301f8840caa547e48730a46e1b9406927bc` -> `cc2ca30760c486cad3154c619a20f94cf75cc691`. Hasta el head citado, el delta posterior es solo la regresión de selección del banco; corroboralo. Archivos principales: `sistema/web/discovery_spike.html`, `sistema/api/isolated_session.py`, `sistema/api/demo_discovery.py`; banco existente `tests/browser_discovery.cjs`, workflow `.github/workflows/clean-snapshot.yml`.

No sustituir por Custos, MUDH-Mobile, el lector legado ni otra rama. Revisar este componente no aprueba PR18/19/20 completos ni autoriza integrarlos.

### Pregunta y contrato a desafiar

¿El cliente conserva un camino explícito para revocar la sesión original cuando el cierre no está confirmado, sin mostrar contenido protegido ni habilitar acciones ajenas al cierre?

Al iniciar logout debe vaciar contenido, selección, resultados y referencia; bloquear acciones ajenas; conservar el bearer original únicamente para reintentos explícitos desde la UI. Confirmar solo con `logged_out === true`, booleano. Un rechazo o fallo de transporte no prueba revocación ni autoriza sustituir el bearer con un login nuevo. Después de confirmar, comprobar denegación del bearer original por HTTP independiente y que otra sesión no sufrió revocación colateral.

`logoutToken` no tiene privilegios reducidos en el backend. Recargar/navegar olvida el handle, pero no equivale a revocar. Son límites declarados, no bugs nuevos por sí mismos.

### Orden de trabajo

1. Leé contrato y código actuales. Antes de abrir los instrumentos y resultados históricos, escribí tu propia matriz: propiedad, input, esperado, positivo, violación causal, criterio de parada y limpieza. No prometas independencia de casos si primero copiaste la matriz anterior.
2. Usá un archive propio del SHA, fixtures sintéticas nuevas, CLI/HTTP real en loopback y navegador real cuando la propiedad sea de UI. No uses SQL emulado como sustituto del consumidor HTTP. Verificá acceso/credencial según las reglas de la nueva sesión; no extraigas secretos de remotos ni imprimas tokens.
3. Priorizá estados pendientes, reintento con el bearer original y criterio de confirmación. Separá fallos antes de llegar al servidor de respuesta perdida después de revocar; contrastá UI y estado servidor. Elegí al menos un borde material según tu criterio y justificá por qué. No repitas todo Corpus ni reabras la regresión de selección ya incorporada sin nueva evidencia.
4. Ejecutá positivos y falsadores causales: la misma aserción debe pasar con el candidato y fallar por la violación introducida, no por fixture roto ni un exit1 genérico. Conservá corridas inválidas y errores propios. Repetí el caso decisivo en entorno nuevo si depende de estado/timing.
5. Después contrastá tus resultados con el pase y los antecedentes. BFCache solo permite juzgar callbacks restaurados si demostraste mismo documento/UUID y pageshow.persisted; no fuerces la conclusión quitando protecciones del producto. Precondición ausente = NO MEDIDO.
6. Entregá resultado y límites, con comandos y stdout/stderr completos, fuentes exactas del instrumento, fixtures reproducibles sin secretos, controles, revisión probada y recursos propios cerrados. No cambies producto por iniciativa propia para resolver un hallazgo.

### Fuentes canónicas para la segunda fase

Pase: https://github.com/gatehot59-star/corpus-legal-tarija/blob/92c833d13fe24e7bdb756e4cfc451678c6034e09/docs/agents/respuestas/2026-09-20-10-logout-review-handoff.md

Doc del pase: https://app.clickup.com/90171457413/docs/2kza6fw5-13877

Verificación de todos sus enlaces: https://github.com/gatehot59-star/corpus-legal-tarija/blob/e062c5538e83ab42170349c3e0442a0bff722ee1/docs/auditorias/2026-09-20-13-handoff-links.md

El pase enlaza informes02-05 y evidencia reversible con fuentes completas. La selección fue incorporada en09 y contrastada en11; los reparos documentales de11 fueron corregidos después. Distinguí historial de pendiente actual. Nexus214 es un encargo enviado originalmente a SOL, no recepción ni inicio de esta instancia. Consultá reportes posteriores antes de duplicar trabajo.

### Permisos y cierre

Permitido por este encargo: lectura, pruebas propias aisladas con datos ficticios y publicación de tu informe/evidencia en Git, Doc público en Space validado y continuidad Nexus, conforme al método. No autorizado: cambios de producto/workflow/permisos/credenciales, bases reales, merge, despliegue, envío de mensajes/review requests o asignaciones. No consumir runtime ajeno sin la confirmación que corresponda.

Veredicto por afirmación: CONFIRMADO / REFUTADO / NO MEDIDO, con impacto, precondiciones y reproducción. Separá defecto nuevo, heredado, límite declarado e instrumento defectuoso. Identificá qué no se midió que importaba. Un resultado sin reparos no autoriza merge.

Para considerar completa la entrega: informe y evidencia propios publicados, recuperados y comparados byte por byte, informe perteneciente a main; Doc público leído; continuidad Nexus. Reportá Gate I/II/III por separado. Si falta algo, declaralo INCOMPLETO o BLOQUEADO, no terminado. G2 solo puede cambiar cuando exista esta revisión ejecutada con selección propia y límites de independencia explícitos; abrir una conversación o recibir el pase no lo cierra.

Empezá ahora por recuperar el contexto vivo, fijar el sujeto y diseñar tu matriz. No vuelvas a responder únicamente que hace falta buscar un revisor.

## Fin del prompt

Nota de preparación: esto es un artefacto documental, sin ejecución de auditoría, sin revisión externa ni nuevos tests. TITAN LIGERO, rúbrica numérica N/A. El operador que lo preparó conserva contexto de la implementación y no se presenta como el revisor externo que se busca.
