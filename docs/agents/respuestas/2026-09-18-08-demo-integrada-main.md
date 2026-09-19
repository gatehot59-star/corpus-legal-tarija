# PR15 y PR14 integrados: demo sintetica y CI en main

18-sep-2026 ART. Autorizacion exacta: confirm_corpus_merge_15_14, merge_pr15_into_pr14_then_pr14_into_main_verify_each_no_deploy_no_real_data_exclude_pr1. Este recibo cierra ese lote de dos merges, no autoriza el siguiente.

## Resultado comprobado

PR15 se integro en PR14 como e7e06e9cc94a917160e522fa409bc66f6829b2ee a las 22:42:04 ART. Su arbol completo coincide con el commit probado 84cae9a793715355a29fd692fe097003349aa316: git diff exit0. GitHub ejecuto un nuevo CI sobre esa cabeza combinada y termino success antes del segundo merge.

PR14 se integro en main como 9913d8dd5074d6aedd0d261c42caea6480e794fe a las 22:43:01 ART. Su arbol 3147006444f7bf6f8f629f8d05a8373dcf4c3dd5 coincide exactamente con el preflight git merge-tree contra main1707ba7070f039bdfcfc52ecdc3be3799152f088. Ambos PR fueron leidos de nuevo: closed y merged:true. Se preservaron las ramas.

Diff frente al main anterior: cuatro archivos, 633 lineas agregadas, cero eliminadas. Nuevos sistema/api/demo_aislada.py, tests/test_demo_aislada.py y sistema/DEMO-AISLADA.md; nueve lineas agregadas a .github/workflows/clean-snapshot.yml. No se modificaron servidor.py, bases reales, cuentas reales ni infraestructura de produccion. PR1 sigue abierto con cabeza2360f27d43fdc9a1e2a74a3f6465698918df2ad1, sin tocar.

## CI de la cabeza combinada, no del commit de main

Job https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35413461264/job/105817429355: stable_identity completed/success, 2026-09-19T01:42:12Z..01:42:43Z. El paso3 de regresion termino success 01:42:15Z..01:42:30Z; el paso4 de demo CLI termino success 01:42:30Z..01:42:41Z. Se capturaron todos los atributos de los seis elementos de pasos del HTML publico. No se recupero stdout completo de GitHub y no se adjudica alli el conteo individual97.

El workflow tiene pull_request y workflow_dispatch, no push. No se afirma una corrida nueva de CI sobre9913d8d. Lo que se ejecuto sobre el main real fue la verificacion local siguiente.

## Pruebas posteriores al merge, sobre main real

Se hizo git archive9913d8d en un directorio nuevo. Se reutilizo, sin cambiarlo, el instrumento docs/agents/evidencia/2026-09-18-07-demo-ci-verifier.py.txt. Lee YAML con BaseLoader, valida permisos/path filters/ausencia de if y continue-on-error, ejecuta los bloques run exactos y conserva command, cwd, exit, stdout y stderr completos.

Comando: python3 /workspace/corpus-demo-merge-20260918/verify.py /workspace/corpus-demo-merge-20260918/main /workspace/corpus-demo-merge-20260918/main-tests.json. Una sola corrida, lanzada con nohup y observada hasta producir los tres registros y structure.json final.

Regresion exit0: 21 SOL en5.985s, 15 HTTP en1.385s, 15 permisos en5.123s, 18 guards en22.411s y10 sesiones en14.089s. Demo CLI exit0:18 pruebas en32.435s. Total97 pruebas positivas; no se suman otra vez las12 login heredadas.

El banco CLI ejecuta procesos reales, observa evento ready con PID y loopback, recorre paginacion exacta, cierra sesion, comprueba403 posterior y200 de las otras sesiones, apaga el proceso, levanta otro PID y verifica persistencia. Al salir exige terminacion y puerto cerrado. No es solo una importacion ni unit tests simulando el servidor. No demuestra arranque de Corpus vivo, UI real, TLS ni piloto.

Control negativo en copia aparte: if not args.isolated_demo: se cambia por if False:. Mismo bloque del workflow, exit1; test_init_requires_opt_in_without_writes falla AssertionError:0!=2. Ademas test_serve_requires_opt_in_without_mutation produce TimeoutExpired15s porque el servidor indebidamente arranca. Se guardan ambos:18 pruebas48.410s, failures1/errors1. No se vende como un unico fallo limpio ni como rojo intencional de GitHub. El mutante no se commitea ni se integra.

## Evidencia y limites

- docs/agents/evidencia/2026-09-18-08-demo-main-tests.json: tres registros completos del instrumento, sin recortar stderr.
- docs/agents/evidencia/2026-09-18-08-demo-merges-ci.json: respuestas de merge, check estructurado y atributos completos de pasos. Las selecciones de estado se identifican como tales, no como respuestas completas.
- Instrumento reutilizado: docs/agents/evidencia/2026-09-18-07-demo-ci-verifier.py.txt.

Se compararan los JSON recuperados de Git contra las capturas antes del chat; esta frase describe el control pendiente de publicacion y no lo da anticipadamente por hecho. Los cuerpos historicos de PR14/15 describen su estado al abrirse, incluyendo CI entonces pendiente; este recibo y los campos estructurados son el estado posterior. No se modificaron retrospectivamente esos cuerpos para borrar la historia.

## Gate antes de firmar

Compila -> py_compile dentro de ambos bloques, exit0 -> podia dar rojo -> medido bien.
Regresion y demo arrancan en aislamiento -> suites + CLI en subprocess real -> podian dar rojo ->97 positivas.
Opt-in roto es detectado -> mismo step sobre mutante -> podia dar rojo ->exit1 con assertion objetivo y timeout adicional.
Merge correcto -> respuestas API, relectura closed/merged y comparacion completa de arboles -> podia dar rojo ->medido bien.
Corpus listo para piloto/comercial -> ningun instrumento de esta entrega ->NO MEDIDO.

## QA y alcance

Modo TITAN FULL. Roles aplicados: integracion GitHub, verificacion y documentacion; QA interno, no nuevo auditor independiente. Rubrica de integracion/configuracion56/60=93.33/100: completitud15/15(diff de cuatro archivos y arbol exacto), ejecutabilidad15/15(compilador,97tests y procesos reales), seguridad13/15(contents:read,scope sintetico y sin despliegue; no certificacion productiva), documentacion9/10(runbook y evidencia, cuerpos PR historicos), proceso QA4/5(crudo y falsador, review externo no emitido). N/A40: nuevo testing/cobertura como feature15, arquitectura10, DevOps de produccion10 e innovacion5. Los tests existentes se ejecutan y se exponen, no se afirma haber creado nueva cobertura. El puntaje no mide completitud del producto.

Review de PR14 leido: lista vacia; hilos de PR14/15 vacios en preflight. Ausencia de objeciones no es aprobacion externa. No hubo nuevo defecto de producto en esta corrida; la falta de review ya era deuda explicitada y conocida al autorizar. No se abre otra tarea de implementacion ni se activa otro runtime ajeno.

Correccion de preparacion: el clon no tenia origin/main pese a fetch con ramas explicitas. El comando fallo128 antes de medir; se hizo fetch de main solo y se fijo su SHA, sin sustituir FETCH_HEAD despues de otro fetch. No se uso ese error como limite del entorno.

## Lo siguiente en el plan

La composicion sintetica ya esta integrada, no pendiente de merge. Sigue convertirla en un recorrido util de usuario y probar restauracion/seguridad, respetando muestra legal revisada y autorizaciones humanas antes del piloto. Esta entrega no cierra M01-M04 ni habilita cobros. No hay despliegue ni nuevas cuentas reales.

Enlaces: https://github.com/gatehot59-star/corpus-legal-tarija/pull/15 y https://github.com/gatehot59-star/corpus-legal-tarija/pull/14.
