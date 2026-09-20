# Brain: revisión de auditores y avance documental de PR20

20-sep-2026 ART. Pedido: «Revisa que dejaron los auditores y avanza». Yo soy Brain; no me atribuyo las corridas de Astra ni suplanto a SOL. No se pidió ni ejecutó merge/despliegue.

## Resultado y acción ejecutada

Leí las entregas nuevas en Nexus83-86, las páginas públicas15/16 y el diff real. Astra agregó un ensayo útil de expiración durante logout con dos sesiones del mismo usuario, y luego incorporó su regresión al banco existente. No encontré un defecto nuevo que justificara tocar producto en este alcance.

Actualicé la descripción de [PR20](https://github.com/gatehot59-star/corpus-legal-tarija/pull/20), que seguía declarando ca503377/88checks y pase no enviado. Ahora declara c1e54ad/109checks, CI vigente y el envío ya autorizado a SOL. Conserva referencias e historia como antecedentes, no como estado actual.

Readback por API: head c1e54ad0035f23d8ab549e9b16e3a6751bc1b2d2, base31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05, open, merged=false,13commits,10archivos. No cambié rama, base, título, código, tests, workflow, permisos ni despliegue. No envié mensajes nuevos al revisor.

## Contraste directo, no solo recibos

Último delta ca503377→c1e54ad: tests/browser_discovery.cjs,101inserciones, único archivo cambiado. Test22340bytes SHA256 1d661c0fea21a20d669a52e848e7337b6fb9854999a7da5d939fd0e29f32c571. Leí las101líneas: retención de logout, intervención de validez SOLO en A, comprobación A403/B200, confirmación real, restauración EXACTA de ventana original, revocación persistente de A y uso/cierre independiente de B. La limpieza forzada viene después de las aserciones.

[CI actual](https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35523532354/job/106111629018): API consultada en este turno, head_sha c1e54ad0035f23d8ab549e9b16e3a6751bc1b2d2, completed/success. Diez pasos completed/success, ninguno skipped;16:42:03..16:43:26UTC=13:42:03..13:43:26ART. No nuevo Actions ni descarga de stdout.109 es conteo local publicado, no inferido de CI.

## Evidencias recuperadas y recomputadas

[Auditoría15](https://github.com/gatehot59-star/corpus-legal-tarija/blob/9d986a6f66326e139d860d65f0fec1e04c0796b8/docs/auditorias/2026-09-20-15-astra-logout-executed.md) y [evidencia15](https://github.com/gatehot59-star/corpus-legal-tarija/blob/9d986a6f66326e139d860d65f0fec1e04c0796b8/docs/auditorias/2026-09-20-15-astra-logout-executed/evidence.xz.b64): decodificación base64 estricta+xz,138159bytes SHA256 f701085562ebe44a0ec4216033a5a3617dd34fefeb984345bde5b4ab252da022, coincide con el declarado.

[Entrega16 y bloque de evidencia](https://github.com/gatehot59-star/corpus-legal-tarija/blob/48ada7899214eb1fdc3761603e2ff6376952c8c9/docs/agents/respuestas/2026-09-20-16-expiry-ci.md): bloque base64 extraído por delimitador, decodificación estricta+xz,96353bytes SHA256 190c9faeadc6b7a3eccd23d99a8e44e07f73ebe45376bbe2e9596f7d09d6c5c0, coincide.

Las aserciones con actual/expected se recomputaron mediante comparación de serializaciones JSON con claves ordenadas: distingue true de1. Se leyó stdout o, para mutantes16, stderr; no se supuso que exit1 fuera detección pertinente. Resultados impresos por Python (extracto de campos de resumen; los registros originales completos siguen en los paquetes enlazados):

| Paquete/corrida | Exit | Registros con pass | Comparaciones tipadas | Fallos de propiedad |
|---|---:|---:|---:|---|
|15 positive-run|0|183|183|ninguno|
|15 repeat-run|0|183|183|ninguno|
|15 lose_handle-run|1|16|15|marker403:retry_available, false frente a true|
|15 trust_string-run|1|15|14|string_true:failure_not_confirmed, false frente a true|
|16 positive|0|109|50|ninguno|
|16 repeat|0|109|50|ninguno|
|16 mutant-expired|1|102|44|expiry_restored_window_does_not_resurrect_A,200 frente a403|
|16 mutant-collateral|1|104|46|expiry_same_user_B_not_revoked,[[0]] frente a[[1]]|

Cero discrepancias entre comparación tipada y flag pass en esas ocho capturas. Los59checks heredados del banco16 no incluyen actual/expected: no inventé su recomputación. En los mutantes15 el registro scenario_error es una consecuencia de la aserción, no otro defecto.183 o109 son comprobaciones por corrida, no escenarios ni porcentaje de cobertura; no sumo repeticiones.

Reproducción del cálculo sobre los paquetes decodificados: leer files[nombre], convertirlo de texto JSON si corresponde, leer stdout o stderr, extraer records/checks, filtrar presencia simultánea de actual/expected/pass, comparar json.dumps(actual,sort_keys=True) contra json.dumps(expected,sort_keys=True), listar desacuerdos y discrepancias con pass. Para los nombres exactos usar la tabla y añadir .json; los15 llevan sufijo -run. El instrumento inline terminó exit0, stderr vacío. No se publicó ni ejecutó un nuevo script de producto. Esta tabla es una derivación reproducible, no se llama captura íntegra de todas las llamadas de este turno.

## Lo que significa y lo que no

CONFIRMADO: el nuevo banco apunta a una propiedad relevante y detecta dos violaciones dirigidas. Restaurar validez evita confundir expiración con revocación. B sobrevive: hay control de aislamiento entre sesiones del mismo usuario.

NO MEDIDO en este turno: nuevas ejecuciones propias de Chromium/HTTP, expiración natural15min, todas las carreras, BFCache del documento restaurado, otros navegadores y producción/piloto. Las corridas son de Astra; yo inspeccioné código, custodia, registros y estado vivo. No infiero reparación universal ni aprobación independiente.

## Qué sigue abierto y quién lo tiene

Consulté mensajes Nexus id>=214: solo apareció el encargo214 de Brain a auditor-sol, enviado15:12:55.717UTC, leido=0. Envío autorizado por Abraham en comentario80170047145910. No hay respuesta posterior en esa consulta. No pruebo ausencia universal de actividad ni cierro G2. El encargo ya está enviado, no corresponde pedir otra autorización para el mismo envío ni mandar duplicados.

[Pase existente](https://github.com/gatehot59-star/corpus-legal-tarija/blob/92c833d13fe24e7bdb756e4cfc451678c6034e09/docs/agents/respuestas/2026-09-20-10-logout-review-handoff.md): fija ca503377. Requiere reconsultar la revisión al comenzar; desde allí solo cambió el test de expiración, no HTML/backend. Astra15 declara continuidad con su implementación y no cierra revisión por otro autor. Brain no transforma esa autoverificación en firma externa.

Siguiente paso que cambia la decisión: veredicto de revisión focalizada por quien no escribió el fix, atender sus reparos y después decidir integración con autorización explícita. No hace falta otra ronda idéntica de BFCache, otro pase ni más tests sin hipótesis nueva. Los gates jurídicos y operativos del piloto son independientes; este pedido no autoriza personas, datos o despliegue reales.

## Método y custodia

Revisión acotada por Brain, máquina brain-env mediante build/run; Git público y API de Actions, Nexus y Docs como contexto. LIGERO: solo lectura, recomputación y documentación. No cambié frontera de confianza ni workflow. Rúbrica numérica N/A: no nueva implementación ni certificación del producto. Calidad: fuentes versionadas y límites explícitos; proceso: positivos y fallos pertinentes contrastados; completitud limitada a15/16 y continuidad. No se declara revisión exhaustiva de todo Corpus.

Este archivo deja el cierre en Git; espejo público ClickUp y continuidad Nexus se verifican antes del chat final. Snapshot de main antes de publicar:48ada7899214eb1fdc3761603e2ff6376952c8c9. La publicación documental no mueve el head del PR20.
