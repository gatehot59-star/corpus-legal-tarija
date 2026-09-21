# Corpus Django: lote32 construido, aceptación sintética y CI medidos

## Autoridad, sujeto y resultado

BRAIN implementó la aprobación humana80170047177490, approve_corpus_django_32_files. Basearquitectura47a499945d5594bae4a409216d2621a6e07a5585; rama titan/builder-corpus-django; PR https://github.com/gatehot59-star/corpus-legal-tarija/pull/22.32rutas respecto de arquitectura:31nuevas y READMEactualizado, ninguna eliminación. Contra main se agregan además ADR/contrato ya aprobados. No merge, despliegue, datos/cuentas/correo reales ni eventos del laboratorio. HoldsPR18/logout intactos; otrosPRs sin cambios.

El recorrido usable existe: entrar, buscar, leer versión/procedencia, guardar referencia privada, reportar privadamente y salir. Recuperación de cuenta probada con tokenDjango/backend enmemoria. Restauraciónoffline en cuarentena y reconciliación desde autoridadindependiente; no resucita sesiones,grants ni retiradas viejas. Administración de cuentas/grants vía modelosORM, no consola pública. El README contiene comandos y límites.

Código final probado:2cd4ca7ebe23422d617d3e5c741e084a4cdfeedf.38tests locales pasan, cobertura aplicación93% (575sentencias,43sin cubrir; sin tests/migraciones), recuperación83% individual. Tres mutantesauth/CSRF/logout del sujeto inicial fueron rechazados. Gunicornreal atendió el recorridoHTTPloopback, no una mera importación. CI del código final completó siete pasos, compilación/migraciones/suite/cobertura/construcciónDocker/testscontenedor:success. No confundir este verde con el nuevo SHA documental que crea el reporte.

## Evidencia y custodia

`docs/agents/evidencia/2026-09-21-django-delivery.json` en6e254423a7e8cb87dbf0092a3ec377f6a0d8a4c4 contiene69.136bytes crudos lossless, SHA25655efb56fba64ac95bffe4080ccadf890fd093a418fdb16b1d140afc6f995af9f. Se descargódesdeGit, base64estricto+lzma y longitud/SHA coincidieron. Archivos interiores:attempt1.json,attempt2.json,runtime-evidence.json,runtime_instrument.py,readback.json,osv.json,python-image.json. Los stdout/stderr de corridas y mutaciones y las respuestasHTTP están enteros. El instrumento fue ejecutado, no propuesto. Datos/tokens visibles pertenecen exclusivamente a fixtureslocales; no hay sessioncookies reales ni email enviado.

Decodificación:
```python
import json,base64,lzma,hashlib
from pathlib import Path
w=json.loads(Path('docs/agents/evidencia/2026-09-21-django-delivery.json').read_text())
raw=lzma.decompress(base64.b64decode(''.join(w['chunks']),validate=True))
assert len(raw)==w['decoded_bytes'] and hashlib.sha256(raw).hexdigest()==w['sha256']
evidence=json.loads(raw)
```

La primera evidencia es histórica:35tests/92%,Dockerpendiente y faltaadapterUUID. Este anexo la actualiza, no la reescribe: OfflineRecovery implementado, FIFO rechazado sin bloqueo,38tests/93%,Docker medido enCI.29fuentes iniciales eran byteidénticas al repositorioef71dfce. Los4archivos modificados fueron comparados otra vez contra2cd4ca7e: todosiguales; hashes abajo.

```json
[{"path":"sistema/django_app/corpus/reader.py","sha256":"8b153e27f5cd7d5a081ff912e4f92ae19544ef4ab8df7de8dcbdd8506ec42f95","equal":true},{"path":"sistema/django_app/corpus/services.py","sha256":"54d5e9c1f78ca57bd22a7110f42611957914a8a0f79cbef22bacd0d794f5035b","equal":true},{"path":"sistema/django_app/corpus/management/commands/recover_snapshot.py","sha256":"5cdf39dda0a51eb3380844b6a2883fd82c98dd9bc0cce86649613a54c4011513","equal":true},{"path":"sistema/django_app/corpus/tests/test_recovery.py","sha256":"0d14c06f178177c3d63815475cdd58168fa440cbc85e302c9c42e4799ec588a6","equal":true}]
```

## Última suite: salida cruda

Comando `/workspace/corpus-django-build/venv/bin/python -m coverage run --source=corpus manage.py test corpus.tests --verbosity=2`,cwd sistema/django_app, CORPUS_TEST_PROFILE=synthetic,CORPUS_DB absoluto temporal,exit0. stdout:
```text
Found 38 test(s).
Operations to perform:
  Apply all migrations: auth, contenttypes, corpus, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0001_initial... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying corpus.0001_initial... OK
  Applying sessions.0001_initial... OK
System check identified no issues (0 silenced).
```

stderr:
```text
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
test_authorization_precedes_reader (corpus.tests.test_access.AccessTests.test_authorization_precedes_reader) ... ok
test_disabled_collection_denied (corpus.tests.test_access.AccessTests.test_disabled_collection_denied) ... ok
test_disabled_membership_denied (corpus.tests.test_access.AccessTests.test_disabled_membership_denied) ... ok
test_empty_catalog_still_requires_valid_identity (corpus.tests.test_access.AccessTests.test_empty_catalog_still_requires_valid_identity) ... ok
test_epoch_and_quarantine_deny (corpus.tests.test_access.AccessTests.test_epoch_and_quarantine_deny) ... ok
test_expired_grant_denied (corpus.tests.test_access.AccessTests.test_expired_grant_denied) ... ok
test_future_grant_denied (corpus.tests.test_access.AccessTests.test_future_grant_denied) ... ok
test_inactive_user_denied (corpus.tests.test_access.AccessTests.test_inactive_user_denied) ... ok
test_login_csrf_required_and_no_header_identity (corpus.tests.test_access.AccessTests.test_login_csrf_required_and_no_header_identity) ... ok
test_logout_invalidates_old_cookie (corpus.tests.test_access.AccessTests.test_logout_invalidates_old_cookie) ... ok
test_no_grant_and_staff_never_bypass (corpus.tests.test_access.AccessTests.test_no_grant_and_staff_never_bypass) ... ok
test_positive_reader_and_contract (corpus.tests.test_access.AccessTests.test_positive_reader_and_contract) ... ok
test_revoked_grant_denied (corpus.tests.test_access.AccessTests.test_revoked_grant_denied) ... ok
test_throttle_is_persistent_across_clients (corpus.tests.test_access.AccessTests.test_throttle_is_persistent_across_clients) ... ok
test_unapproved_collection_denied (corpus.tests.test_access.AccessTests.test_unapproved_collection_denied) ... ok
test_withdrawn_version_denied (corpus.tests.test_access.AccessTests.test_withdrawn_version_denied) ... ok
test_write_csrf_required_even_when_authenticated (corpus.tests.test_access.AccessTests.test_write_csrf_required_even_when_authenticated) ... ok
test_wrong_collection_and_invalid_locator (corpus.tests.test_access.AccessTests.test_wrong_collection_and_invalid_locator) ... ok
test_wrong_group_denied (corpus.tests.test_access.AccessTests.test_wrong_group_denied) ... ok
test_authority_revision_quarantine_and_identity_mismatch (corpus.tests.test_recovery.RecoveryTests.test_authority_revision_quarantine_and_identity_mismatch) ... ok
test_bad_hash_and_existing_target_rejected (corpus.tests.test_recovery.RecoveryTests.test_bad_hash_and_existing_target_rejected) ... ok
test_current_policy_reconciliation_preserves_withdrawal_and_revocation (corpus.tests.test_recovery.RecoveryTests.test_current_policy_reconciliation_preserves_withdrawal_and_revocation) ... ok
test_missing_stale_or_self_authority_never_reopens (corpus.tests.test_recovery.RecoveryTests.test_missing_stale_or_self_authority_never_reopens) ... ok
test_nonregular_sources_rejected_without_blocking (corpus.tests.test_recovery.RecoveryTests.test_nonregular_sources_rejected_without_blocking) ... ok
test_protocol_adapter_resolves_only_registered_backup (corpus.tests.test_recovery.RecoveryTests.test_protocol_adapter_resolves_only_registered_backup) ... ok
test_quarantine_purges_sessions_and_disables_stale_authority (corpus.tests.test_recovery.RecoveryTests.test_quarantine_purges_sessions_and_disables_stale_authority) ... ok
test_symlink_and_foreign_schema_rejected (corpus.tests.test_recovery.RecoveryTests.test_symlink_and_foreign_schema_rejected) ... ok
test_hash_failure_never_returns_text (corpus.tests.test_workflow.WorkflowTests.test_hash_failure_never_returns_text) ... ok
test_health_distinguishes_process_from_policy (corpus.tests.test_workflow.WorkflowTests.test_health_distinguishes_process_from_policy) ... ok
test_password_reset_uniform_and_old_session_invalidated (corpus.tests.test_workflow.WorkflowTests.test_password_reset_uniform_and_old_session_invalidated) ... ok
test_real_http_journey_and_private_ownership (corpus.tests.test_workflow.WorkflowTests.test_real_http_journey_and_private_ownership) ... ok
test_reference_deduplication_and_no_content_columns (corpus.tests.test_workflow.WorkflowTests.test_reference_deduplication_and_no_content_columns) ... ok
test_search_budget_failure_not_partial_success (corpus.tests.test_workflow.WorkflowTests.test_search_budget_failure_not_partial_success) ... ok
test_service_range_and_feedback_validation (corpus.tests.test_workflow.WorkflowTests.test_service_range_and_feedback_validation) ... ok
test_snapshot_symlink_rejected (corpus.tests.test_workflow.WorkflowTests.test_snapshot_symlink_rejected) ... ok
test_strict_query_duplicate_unknown_and_invalid_ranges (corpus.tests.test_workflow.WorkflowTests.test_strict_query_duplicate_unknown_and_invalid_ranges) ... ok
test_synthetic_search_latency_and_pagination (corpus.tests.test_workflow.WorkflowTests.test_synthetic_search_latency_and_pagination) ... ok
test_withdrawal_after_page_blocks_read_save_report_and_reference (corpus.tests.test_workflow.WorkflowTests.test_withdrawal_after_page_blocks_read_save_report_and_reference) ... ok

----------------------------------------------------------------------
Ran 38 tests in 5.463s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
```

Comando coverage report --omit='*/tests/*,*/migrations/*' --fail-under=85,exit0,stderrvacío. stdout:
```text
Name                                              Stmts   Miss  Cover
---------------------------------------------------------------------
corpus/__init__.py                                    0      0   100%
corpus/access.py                                     37      3    92%
corpus/apps.py                                        3      0   100%
corpus/forms.py                                      22      0   100%
corpus/management/__init__.py                         0      0   100%
corpus/management/commands/__init__.py                0      0   100%
corpus/management/commands/provision_fixture.py      48      4    92%
corpus/management/commands/recover_snapshot.py      107     18    83%
corpus/models.py                                     67      0   100%
corpus/reader.py                                     35      3    91%
corpus/services.py                                   82      3    96%
corpus/urls.py                                        3      0   100%
corpus/views.py                                     171     12    93%
---------------------------------------------------------------------
TOTAL                                               575     43    93%
```

## API de CI: respuesta cruda final

GET https://api.github.com/repos/gatehot59-star/corpus-legal-tarija/actions/jobs/106315738125. No se afirma conteo de tests desde Actionsstdout:38 corresponde a la corrida local. El campo estructurado y pasos prueban éxito delworkflow sobre2cd4ca7e.

```json
{"id":106315738125,"run_id":35594375708,"workflow_name":"Corpus Django acceptance","head_branch":"titan/builder-corpus-django","run_url":"https://api.github.com/repos/gatehot59-star/corpus-legal-tarija/actions/runs/35594375708","run_attempt":1,"node_id":"CR_kwDOUMrZ-s8AAAAYwOlsDQ","head_sha":"2cd4ca7ebe23422d617d3e5c741e084a4cdfeedf","url":"https://api.github.com/repos/gatehot59-star/corpus-legal-tarija/actions/jobs/106315738125","html_url":"https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35594375708/job/106315738125","status":"completed","conclusion":"success","created_at":"2026-09-21T11:30:06Z","started_at":"2026-09-21T11:30:08Z","completed_at":"2026-09-21T11:30:42Z","name":"application","steps":[{"name":"Set up job","status":"completed","conclusion":"success","number":1,"started_at":"2026-09-21T11:30:09Z","completed_at":"2026-09-21T11:30:10Z"},{"name":"Run actions/checkout@11d5960a326750d5838078e36cf38b85af677262","status":"completed","conclusion":"success","number":2,"started_at":"2026-09-21T11:30:10Z","completed_at":"2026-09-21T11:30:11Z"},{"name":"Install exact dependencies and compile","status":"completed","conclusion":"success","number":3,"started_at":"2026-09-21T11:30:11Z","completed_at":"2026-09-21T11:30:18Z"},{"name":"Migrations, policy, CSRF, private workflow and recovery","status":"completed","conclusion":"success","number":4,"started_at":"2026-09-21T11:30:18Z","completed_at":"2026-09-21T11:30:21Z"},{"name":"Build and test non-root container without network","status":"completed","conclusion":"success","number":5,"started_at":"2026-09-21T11:30:21Z","completed_at":"2026-09-21T11:30:39Z"},{"name":"Post Run actions/checkout@11d5960a326750d5838078e36cf38b85af677262","status":"completed","conclusion":"success","number":10,"started_at":"2026-09-21T11:30:39Z","completed_at":"2026-09-21T11:30:39Z"},{"name":"Complete job","status":"completed","conclusion":"success","number":11,"started_at":"2026-09-21T11:30:39Z","completed_at":"2026-09-21T11:30:39Z"}],"check_run_url":"https://api.github.com/repos/gatehot59-star/corpus-legal-tarija/check-runs/106315738125","labels":["ubuntu-24.04"],"runner_id":1000003175,"runner_name":"GitHub Actions 1000003175","runner_group_id":0,"runner_group_name":"GitHub Actions"}
```

## Seguridad, desviaciones y NO MEDIDO

OWASP: acceso fresco/owner/withdrawal/CSRF probados; parámetrosORM/SQL ligados, plantillasescapadas y CSP; secretosreales ausentes de la entrega, sesión Django; erroresgenéricos, Securefuera de test; pins exactos yOSVquerybatch devolvió cincoresultadosvacíos paraDjango5.2.17/asgiref3.12.1/sqlparse0.6.0/gunicorn26.2.0/coverage7.16.1. Eso no es ausencia universal deCVE. CIcontents:read, checkoutSHA, sinpersistenciacredenciales. Sin fetchsaliente por fuenteslegales desdeHTTP. No se certifica OWASPcompleto.

Correcciones de revisión propia: evitarFIFO bloqueante conO_NONBLOCK; agregar adapterUUIDdelProtocol y negativos de autoridad/identidad. Snapshotdeserializado verifiedbytes en lugar de reabrir mode=ro: evita carrera de ruta. Tokens sintéticos/fixtures no son credencialesreales. MD5solo en tests; runtime usa DjangoPBKDF2.

Pendiente antes de producción: navegadorvisual/accesibilidadreal, carga10x/memoria/concurrencia, métricas/auditoría operativa, paginaciónreferencias, SMTP/TLS/proxy, altaoperativa de cuentas/grants y muestra legal autorizada. Recovery83% individual necesita ampliar cobertura. La actualidad de política debe acreditarla un custodio independiente; SHAno bastapara eso. Reset tiene respuestauniforme, no se prueba uniformidad temporal. No se asignórevisión humana nueva ni se inventóqueSOLempezó.

Errores propios conservados: herramienta patchretuvo prefijos+, primera compilaciónfalló antes de publicación; normalización de un prefijo en empaquetado, luego compileyhashremotoigual. Inspección de entorno tuvo un paréntesis de más y se corrigió. Primeroscommits consignaron rúbrica parcial en vez de score formalpreacción: incumplimientoM03, no maquillarlo. Publicación fraccionada en unidades relacionadas, no un únicopush. RevisiónCopilot pedida, listado de reviews devolvió[], no aprobación.

## TITAN SCORECARD

Autoevaluación del implementador, NO revisiónindependiente. Roles efectivamente usados: arquitectura heredada,Builder,Security,Tester,Deploy,QA; no afirmar sombreros noejecutados. Completitud15/15 (32rutas); ejecutabilidad15/15 (suite/HTTP/CI); seguridad12/15 (fronterasprobadas, operaciónnoacreditada); testing12/15 (38tests/93%,sinbrowser/carga); arquitectura8/10 (contratos/reutilización,sin10x); DevOps7/10 (contenedorCI,sinoperación/rollbackinstitucional); documentación8/10 (READMEyrecibos,no manual de alta real); innovación3/5 (snapshotsverificados,epoch y restauraciónsinpolíticavieja); procesoQA4/5 (evidenciacompleta,incumplimientoformalpreacción). Total84/100,0N/A: bajo elumbral90 parafirmaproducción. Entrega del lote sintético comprobada; no convertirla en sistema institucional terminado. Deudas identificadas enPR22/README; no se abrieronissuesadicionales fuera del lote autorizado.

Gate antesdefirmar: compila -> Python/CI -> sí podía fallar -> medido bien. FlujoHTTP arranca -> Gunicornproceso+HTTP -> sí -> medido bien. Permisos/CSRF/logout -> testsymutantes -> sí -> medido bien enalcance. Dockerconstruyeyprueba -> jobAPIpaso5success -> sí -> medido bien. Producción/usuariosreales/carga10x -> instrumento inexistenteenestelote -> NO MEDIDO, sin autorización.
