# ADR: ensayo aislado de disparo por PR exclusivamente documental

20-sep-2026 ART. Estado: DISEÑADO, NO EJECUTADO. Pedido: Design an isolated test for documentation-only PR triggering. Diseña Brain, implementará Brain; SOL y Astra Auditor auditan. Este pedido no autoriza crear repositorios de ensayo, abrir PRs experimentales, gastar runtime ni cambiar protecciones. Publicar este ADR y su Doc no ejecuta el ensayo.

## Supuestos y pregunta exacta

Se quiere cerrar el NO MEDIDO de PR21: ¿GitHub dispara .github/workflows/clean-snapshot.yml ante opened y synchronize cuando TODO el diff del PR es documentación y el workflow sin filtros ya existe en su base?

No es la pregunta de si un commit Markdown dentro de un PR mixto dispara CI. GitHub usa diff de tres puntos acumulado; la ejecución final de PR21 no distingue esos casos. No confundir iniciar un run con aprobar sus tests, ni ausencia temporal con prueba de que nunca correrá.

Estado vivo consultado: main645d1732bec136bcc518070db42ff93437f95fd6; PR21 rama titan/deploy-docs-ci head3b92dc432f285c00d5a45e717883c5c6e3fe46f9. Antecedente leído: docs/agents/respuestas/2026-09-20-22-brain-docs-ci.md. El workflow del head tiene SHA256 c69a9f1a21a348bd400fff15165fc55e7e8e7c94fdee1a4a6b7e604d47d0ce72; original005b9214aa1695edb4fdfb1675cbba813fbe6ce921d3d4f06ae0b0c83687e4df. Nuevas mediciones de triggers: siete YAML completos parseados con BaseLoader. Nexus no tenía entradas posteriores a92 en esta consulta.

## 1. Árbol y aislamiento

Elegido: repositorio público de laboratorio NUEVO, sin fork ni historial importado, con nombre a resolver y aprobar antes de crearlo. No se crea ahora. Mismo proveedor GitHub Actions y mismo propietario si su política lo permite, pero sin secretos de repositorio/organización accesibles, environments, runners self-hosted, webhooks de despliegue ni Apps agregadas para el experimento. La identidad de control opera por integración autorizada desde fuera de Actions; sus credenciales nunca entran en jobs.

Árbol inicial del laboratorio: snapshot de archivos rastreados de main645d1732, conservando contenido, modos y rutas del código, tests y fixtures. Única exclusión estructural de preparación: los seis workflows distintos de clean-snapshot.yml NO se materializan en el laboratorio. No se borra nada en Corpus. El manifiesto de preparación enumera todos los archivos y hashes, exclusiones y base original; se conserva FUERA de los PRs de prueba. Revisar el snapshot por secretos y material no autorizado antes de publicarlo, aunque el origen sea público. No generar ni importar credenciales, bases de datos o binarios nuevos.

Rutas significativas heredadas: .github/workflows/clean-snapshot.yml (único workflow), pipeline/ (copia/lectura), sistema/api/ (lector, política, sesión y CLI sintéticos), tests/ (siete bancos heredados), y restantes archivos fuente/fixtures del snapshot. No nuevo contenedor, manifest de dependencias ni paquete: las suites y checkout existentes son el sujeto, no una reimplementación.

Ramas de laboratorio propuestas, seis en total:
- lab/docs-trigger-old-base: raíz del snapshot, workflow original con paths; default branch del laboratorio durante el ensayo.
- lab/docs-trigger-new-base: hija de old-base con SOLO las24líneas eliminadas del workflow, bytes iguales al candidatoPR21; sin informe22.
- lab/docs-trigger-old-docs: desde old-base, solo docs/ci-trigger-probe.md.
- lab/docs-trigger-new-docs: desde new-base, el MISMO archivo y bytes de Markdown.
- lab/docs-trigger-old-code: desde old-base, solo pipeline/clean_snapshot.py, comentario inerte al final.
- lab/docs-trigger-new-code: desde new-base, el MISMO comentario inerte al final.

Las dos bases se congelan antes de abrir PRs. Ningún PR apunta a main de Corpus ni se retargetea. El cambio de workflow es preparación de base y JAMÁS forma parte del diff de un PR documental. No instalar un workflow observador que produzca el resultado esperado por sí mismo.

## 2. Decisiones y matriz

Cuatro PRs independientes, todos no draft y del mismo repositorio de laboratorio:
- OLD-DOCS: old-docs hacia old-base. Solo MD. Predicción: no run de clean-snapshot observado por filtro.
- NEW-DOCS: new-docs hacia new-base. Solo MD. Predicción: run pull_request creado y siete pasos exitosos.
- OLD-CODE: old-code hacia old-base. Solo pipeline/clean_snapshot.py, ruta incluida en paths original. Predicción: run y suites exitosas.
- NEW-CODE: new-code hacia new-base. Misma ruta/cambio. Predicción: run y suites exitosas.

En ambos PRs documentales se prueba opened, se termina su ventana de observación y luego se agrega una segunda línea al MISMO MD para synchronize. Antes y después, diff acumulado exactamente un MD y ningún workflow/código. No introducir el control positivo de código dentro de esos PRs: los contaminaría.

Contenido MD inicial exacto: encabezado '# Documentation-only trigger probe', línea vacía y 'Synthetic CI experiment. No application input.' con LF final. Para synchronize se agrega 'Second documentation-only revision.' con LF. Sin HTML activo, enlaces, instrucciones ejecutables ni datos reales.

Control positivo: añadir al final de pipeline/clean_snapshot.py una línea en blanco y '# Isolated CI path positive control; no runtime change.' con LF. Antes verificar sintaxis de base/candidato y equivalencia AST ignorando atributos de posición; si no es un comentario inerte, detener sin abrir PR. No tocar legal_html.py porque activaría otro workflow en el proyecto original y complicaría la atribución.

Alternativas rechazadas: PR21 mixto (no discrimina); workflow_dispatch o rerun manual (no prueba el evento); job reducido a echo (no prueba el workflow entregado); merge provisional en Corpus (innecesario y no autorizado); ramas de ensayo en Corpus (menor aislamiento frente a workflows push heredados y permisos existentes). Un fork agrega condiciones de aprobación/token distintas y se evita.

La lectura completa mostró censo-gaceta-tcp con push.paths disparadores/censo-gaceta.txt y contents:write; GENESIS y OCR con ramas de push especiales. No basta prometer no ejecutarlos: en el laboratorio no existen sus archivos. legal-html/provenance también se excluyen para aislar un único workflow. Snapshot sin historial evita que un push inicial importe disparadores anteriores.

Escala: cuatroPRs, no diez repeticiones automáticas. A10x no multiplicar repos/jobs: reutilizar el protocolo solo ante revisión nueva del workflow, mantener evidencia y una réplica autorizada si aparece ambigüedad. Máximo seis oportunidades de evento: dos opened de controles de código y dos eventos en cada PR documental. Se esperan cuatro runs; si OLD-DOCS dispara, hasta seis. Timeout heredado5min por job: hasta30job-min de configuración, no promesa de costo cero ni ETA de pared. Sin reintentos automáticos.

## 3. Contrato del instrumento y del veredicto

Implementación del recolector aún NO escrita. Registros propuestos, UTF-8 JSON, sin código descargado de evidencia ejecutado:

Experiment: schema='corpus-docs-trigger-v1', repository_url, source_sha, old_base_sha, new_base_sha, workflow_path, old_workflow_sha256, new_workflow_sha256, snapshot_manifest, excluded_paths, authorization_reference, started_at_utc, completed_at_utc.

Observation: case enum OLD-DOCS/NEW-DOCS/OLD-CODE/NEW-CODE; activity enum opened/synchronize; pr_number, base_ref/base_sha/head_ref/head_sha, merge_base_sha, merge_ref_sha si existe; exact_changed_files con status/modos/hashes; workflow_blob_at_base/head/merge; event_time_utc, deadline_utc; poll_responses con URL, hora, estadoHTTP, encabezados de paginación/rate-limit, cuerpo completo; matched_runs, check_suites/check_runs, jobs_and_steps, logs_reference; trigger_state enum CREATED/NO_RUN_OBSERVED/NOT_MEASURED; execution_state enum SUCCESS/FAILURE/INCOMPLETE/NOT_APPLICABLE; reason.

Identidad causal: correlacionar repositorio, workflow_path/id, event=pull_request, asociación al PR, SHAs de head/base y merge ref del episodio. Guardar todos los SHA recibidos: no asumir que check-run.head_sha siempre es el SHA de la rama head; GitHub puede usar el merge sintético. Un run antiguo, de otro PR, de dispatch o de código-control no acredita NEW-DOCS. Run_attempt también se registra. No reutilizar SHA entre controles.

Readiness: acciones habilitadas, permisos de lectura suficientes, checkout permitido, ningún bloqueo de aprobación ni conflicto, sin cambios de bases, no directivas de omisión en commits/PR head. Crear PR/push desde la integración autorizada, no mediante GITHUB_TOKEN de un workflow que podría suprimir eventos recursivos. Verificar manifiesto/base contra candidato; jobs/permisos idempotentes e idénticos aPR21, sin fragmentos instrumentados.

Precondiciones se validan ANTES de cada evento: git diff base...head y endpoint files del PR coinciden exactamente; se pagina completo. Workflow idéntico base/head del PR, y solo la diferencia24líneas entre bases. Delta inesperado, permiso insuficiente, API truncada/rate-limit no resuelto o workflow no identificable invalidan ese episodio, no lo convierten en negativo.

Lecturas de runs/checks/jobs cada15seg durante hasta5min desde evento confirmado, y lectura final al cerrar la ventana. Consultas totalmente paginadas por workflow/evento/ventana más asociación y SHA; no concluir por un único check ausente. Si un run aparece antes del límite, seguirlo hasta su estado terminal con ventana operativa adicional10min; no declararlo fallido solo por tardar en cola.

NEW-DOCS: CREATED solo con run correlacionado al opened o synchronize exacto. SUCCESS solo con jobstable_identity y los tres bloques de tests realmente exitosos, no skipped/neutral/cancelled. Se espera el mismo total de siete pasos observado enPR21, pero validar nombres/estado y workflow, no contar siete sin contenido. Logs se descargan si están disponibles y se conservan completos; no atribuir111tests a CI sin su stdout.

OLD-DOCS: NO_RUN_OBSERVED solo con lectura completa durante ventana y controles positivos creados en condiciones equivalentes. Significa ausencia acotada, no 'jamás correrá'. Ambos controles de código confirman que GitHub y el workflow filtrado podían arrancar. Si no corren, o existe una espera global, comparación INCONCLUSA. Si OLD-DOCS crea run, REFUTADA la predicción del negativo: investigar, no reclasificarlo como éxito.

Separar conclusiones: disparo documental del candidato CONFIRMADO si NEW-DOCS opened y synchronize crean sus runs con diffs puros; ejecución de suites CONFIRMADA solo con success completo; efecto comparativo del filtro RESPALDADO en la ventana si controles pasan y OLD-DOCS no tiene run; equivalencia con configuración/ramas/protección productiva de Corpus NO MEDIDA. Esta limitación del repositorio de laboratorio se mantiene incluso si todo coincide.

## 4. Flujo de datos y ejecución futura

Autorización separada -> crear laboratorio vacío sin auto-inicialización -> comprobar aislamiento y Actions desactivadas durante preparación -> publicar snapshot saneado y ambas bases -> recuperar bytes/manifiestos -> habilitar Actions solo para el ensayo -> crear heads/abrir cuatroPRs -> inspeccionar diffs y recoger episodiosopened -> cerrar ventanas -> agregar SOLO segundoMD a los dos PRs documentales -> recoger synchronize -> conservar evidencia fuera de los cuatroPRs -> informeGit+Doc+Nexus.

Frontera de control: integración autenticada crea recursos/eventos; GitHub decide el disparo; runner hosted ejecuta únicamente fuente sintética del snapshot con contents:read; recolector externo observa API/logs y deriva veredicto. El runner no decide su propio resultado de disparo ni publica aprobación. Fuente del colector y comandos se incluyen en el recibo final, nunca solo una tabla autodeclarada.

La evidencia va a una rama documental separada de Corpus o almacenamiento acordado, NO a los PRs experimentales: evitar nuevos synchronize o contaminar diff. Primero guardar respuesta cruda, después calcular el veredicto. Releer evidencia remota porSHA y comparar bytes antes del cierre.

## 5. Riesgos, parada y autoridad

Bases equivocadas/cambio deworkflow enPR: preflight diff y hash; episodio inválido. API inconsistente: preservar cada respuesta y clasificar NO MEDIDO, no asumir cero. Negativo por Actions desactivadas o identidad que no dispara: readiness más controles positivos. Mezcla head/mergeSHA: conservar ambos y asociaciónPR. Eventos fuera de orden: no hacer segundo push hasta cerrar primero; no cancel-in-progress añadido. Código de docs consumido: archivo nuevo exclusivamente de laboratorio, contenido fijo inerte; no se ejecuta ni importa.

Repos público puede heredar Apps/políticas/secrets de organización: inspeccionar antes de habilitar Actions. Si no se puede garantizar el aislamiento, no publicar datos ni correr. No leer ni volcar valores de secretos para inspeccionar disponibilidad. No cambiar políticas del propietario para forzar un verde.

No emitir run esperado no equivale a fallo del producto: distinguir trigger, ejecución, preparación y observabilidad. No crear aprobaciones, no tocar reglas, main ni PR1/17/18/19/20/21. No merge de ninguna rama del ensayo. No cierre/borrado automático de PRs, ramas ni repositorio al final: limpieza destructiva y cancelaciones requieren alcance aprobado. Ante run ajeno al único workflow autorizado, parar nuevos eventos y pedir autorización puntual para contención si no estuviera ya contemplada.

Para ejecutar se requiere nueva aprobación del repositorio exacto/visibilidad, dos bases+cuatroheads, cuatroPRs, cambios de archivos sintéticos, habilitación de Actions en laboratorio, hasta seis runs y captura/publicación de evidencia. Este ADR no es esa autorización. No se pide token nuevo si la integración ya puede hacerlo; verificar catálogo/capacidad antes de afirmar un límite.

## Fuentes verificadas y estado de entrega

[Informe22 y límite original](https://github.com/gatehot59-star/corpus-legal-tarija/blob/3b92dc432f285c00d5a45e717883c5c6e3fe46f9/docs/agents/respuestas/2026-09-20-22-brain-docs-ci.md).
[GitHub: filtros y diff de tres puntos](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).
[GitHub: eventos predeterminados de PR](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).
[GitHub: directivas de omisión](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs).
[GitHub: checks y eventos elegibles](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks).

Lecturas en vivo de esta entrega: refsGit, archivo22, siete workflows parseados estructuralmente y documentación oficial. No se hizo un experimento nuevo ni se escribió un colector. Especificación, no test aprobado. Rama documental titan/architect-docs-trigger-test; este ADR más Doc público, sin PR adicional de diseño ni solicitudes de revisión.

--- METODO TITAN ---
Accion delicada: NO en esta entrega, solo diseño documental; el experimento futuro sí requiere autorización. Modo aplicado:TITAN LIGERO, diseño acotado. Rubrica:N/A. Instrumento:lecturas reales y parseoYAML, no runtimeexperimental. Review externo:pendiente, no solicitado de nuevo. Estado:DISEÑADO, NO EJECUTADO, NO INTEGRADO.
