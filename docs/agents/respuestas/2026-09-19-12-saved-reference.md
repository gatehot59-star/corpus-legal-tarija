# Corpus: referencia versionada sintética, PR19

Fecha de trabajo: 19-sep-2026, ART. Autor y operador: Brain. Esta es una entrega de implementación y medición propia, no una auditoría independiente ni autorización de integración.

## Permiso, base y alcance

Aprobación humana: `approve_corpus_saved_reference`, comentario `80170047133243`, valor `implement_synthetic_versioned_reference_download_five_files_new_branch_stacked_pr_public_doc_browser_tests_no_auth_changes_no_merge_no_deploy_no_real_data`.

PR: https://github.com/gatehot59-star/corpus-legal-tarija/pull/19

Rama: `titan/builder-saved-reference`, apilada sobre `titan/browser-auth-spike` (PR18), base medida `2231ca8edbe4c0b6eba88156d5abd087bbf9e51f`. Código publicado y medido: `5995a6a8b3d82676ee5187046facf3ca1d1ce204`. El commit documental posterior no cambia ese código.

Cinco archivos autorizados: `sistema/web/auth_spike.html`, `tests/browser_auth.cjs`, `sistema/DEMO-AISLADA.md`, este recibo y `docs/agents/evidencia/2026-09-19-12-saved-reference.json`. Los tres primeros fueron publicados juntos; este commit agrega los dos últimos. Sin cambios en autenticación, backend, esquema, dependencias o workflow respecto de PR18. Sin merge, despliegue, cuentas reales ni datos jurídicos reales.

## Resultado útil y contrato

La página local permite entrar como Ana ficticia, leer completo el documento fijo y guardar una referencia JSON de su versión. Guardar queda deshabilitado antes de completar la lectura y después de logout o recarga. La descarga vuelve a consultar la misma versión protegida y compara su procedencia con la lectura: si se pierde el permiso o cambia la procedencia, no descarga y borra el texto y la referencia pendiente de la pantalla.

El JSON contiene exactamente 16 campos: `schema`, `environment`, `uid`, `version`, `text_sha256`, `source_sha256`, `source_url`, `source_url_scope`, `hash_scope`, `authority`, `oficial`, `legal_validity`, `total_characters`, `retrieved_at`, `permission_checked_at`, `warnings`. No exporta cuerpo del documento, token, contraseña ni notas privadas.

Valores explícitos: `schema=corpus-reference-v1`, `environment=isolated_test`, `source_url_scope=current_document`, `hash_scope=text_utf8`, `authority=secondary`, `oficial=false`, `legal_validity=NOT_MEASURED`. Incluye cuatro advertencias. Nombre: `corpus-fixture-demo-<version>.reference.json`, con la versión real insertada en ejecución. La URL solo admite HTTP/HTTPS sin usuario ni contraseña; no se visita durante la descarga.

El hash del texto no se confunde con el hash de la fuente. La URL corresponde al documento actual: no acredita la fuente histórica. La versión permanece fijada aunque cambie la versión corriente en la tabla de documentos. La referencia no otorga acceso ni certifica vigencia jurídica. No hay importador, búsqueda protegida, selector de documentos ni envío de reportes.

## Custodia del código

SHA-256 de los bytes ejecutados y publicados, verificados por lectura remota:

- `sistema/web/auth_spike.html`: `c8ca15462dbe46151d60f2005aa30754151969a11d0898fd2de778130f61ac44`.
- `tests/browser_auth.cjs`: `3496953361b72bd9425b423e74f5579615da980d7bb10385b269845cd637b2ec`.
- `sistema/DEMO-AISLADA.md`: `834993af863f336930c439a9144ba949dab86496f8960ca9a5c6bbb2f69aa02e`.

## Evidencia cruda y reproducción

Archivo hermano: `docs/agents/evidencia/2026-09-19-12-saved-reference.json`. Es un envoltorio JSON de transporte `xz+base64`, no una selección de mensajes favorables. Decodificado: **85779 bytes**, SHA-256 **e0b8316179fdd67e605e3cd47c10914b5f3f8de8cabd38c5ae1d877302cbae81**.

Contiene comandos, directorios, códigos de salida, stdout/stderr íntegros de cada corrida, primer fallo real, fuentes de instrumentación y derivación de cobertura, hashes de archivos, mutaciones y atributos de los nueve pasos de CI. Verificación mínima desde el repositorio:

```python
import base64, hashlib, json, lzma
from pathlib import Path
wrapper = json.loads(Path('docs/agents/evidencia/2026-09-19-12-saved-reference.json').read_text())
raw = lzma.decompress(base64.b64decode(wrapper['payload'], validate=True))
assert len(raw) == wrapper['bytes']
assert hashlib.sha256(raw).hexdigest() == wrapper['sha256']
evidence = json.loads(raw)
for run in evidence['runs']:
    print(run['label'], run['cmd'], run['exit'])
```

Para repetir las pruebas del navegador se usa el procedimiento completo en `sistema/DEMO-AISLADA.md` y `node tests/browser_auth.cjs` con Playwright 1.63.0. La máquina medida fue brain-env, Chromium 153.0.8010.12. No se instaló software global ni se usó un despliegue vivo.

## Resultados medidos

1. `node --check tests/browser_auth.cjs`: exit 0.
2. Regresión Python en cuatro bloques seriales, exactamente los comandos conservados en `runs`: 79 casos núcleo + 18 CLI demo + 14 restore + 7 frontera HTTP del navegador = **118 casos**, todos aprobados. Compilación Python incluida. No se sumaron dos veces los tests de login heredados por GuardTests.
3. Banco final en Chromium real: **37 checkpoints, 37 aprobados**, exit 0. Repetición instrumentada también aprobada. Se descarga el archivo de verdad y se analiza con JSON.parse: no se infiere éxito del texto del botón.
4. Mutante `const checked = selected;` en lugar de la nueva consulta: exit 1 en **revoked_save_no_download**. El control positivo descarga; después de revocar permiso, el original no descarga y el mutante sí intenta hacerlo.
5. Mutante `source_sha256:r.text_sha256`: exit 1 en **source_hash_not_text_hash**. La respuesta controlada tiene hashes distintos; el original conserva ambos y el mutante los confunde.

Los mutantes solo existieron en copias de prueba y no forman parte del PR. Los checkpoints cubren JSON exacto sin texto/token, nombre de descarga, campos de procedencia, pérdida de permiso después de leer, versión histórica, procedencia inválida, hashes distintos, cambio de metadatos al guardar y entre páginas, esquemas URL no admitidos y credenciales en URL. Se mantienen pruebas previas de Origin, Unicode astral, retiro, logout y recarga.

Las respuestas interceptadas de hashes distintos y Unicode son pruebas del contrato del consumidor, no certificaciones de integridad de una fuente jurídica. La prueba de versión histórica sí cambia la versión corriente en la base de candidato manteniendo el historial anterior.

## CI real y revisión externa

CI del commit de código `5995a6a8b3d82676ee5187046facf3ca1d1ce204`: run https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35477751509, job `105989838853`, completed/success. Inicio 20-sep-2026 00:03:31 UTC, fin 00:04:32 UTC: 19-sep 21:03:31 a 21:04:32 ART.

Se recuperaron atributos reales de los nueve pasos: todos success. Paso 6 frontera HTTP 00:04:09 a 00:04:10 UTC; paso 7 Chromium 00:04:10 a 00:04:31 UTC. El workflow ya existía en PR18; PR19 no lo cambia. Los conteos 118 y 37 son de stdout local conservado, no de un log remoto que no se descargó. El estado del commit documental se comprueba aparte al cerrar; no se transfiere automáticamente el verde de otro SHA.

Se solicitó review automático. Consulta posterior `get_reviews`: `[]`. Sin aprobación externa emitida; sigue siendo deuda de PR19. No confundir ausencia de objeciones con revisión positiva.

## Cobertura y límites del instrumento

V8 antes de recargar: **5443/5844 caracteres no blancos en rangos ejecutados, 93.1383%**. NO es cobertura de líneas, sentencias ni ramas, ni de todo el proyecto. La captura inicial al detener después de recargar retornó 18.9596% de rangos; se conserva con su limitación y no se presenta como aceptación. Una nueva copia instrumental detiene la cobertura antes de navegar, pero termina igualmente el banco completo con recarga y aserciones. Fuente y datos crudos de ambas derivaciones están en evidencia.

No se hizo inspección visual humana de la captura móvil. Una captura y una comprobación de overflow no equivalen a revisión de accesibilidad o usabilidad. Rendimiento bajo carga y compatibilidad fuera del Chromium medido: NO MEDIDO. Sin barrido CVE actualizado en esta unidad; no se agregaron dependencias, pero eso no certifica la cadena heredada.

La comprobación de permiso no puede retirar un archivo ya descargado ni impedir una revocación que ocurra después de responder la consulta. Token y referencia pendiente se olvidan al salir/recargar; recargar no revoca la sesión persistente. La fuente actual puede no representar la procedencia histórica. No hay TLS público, usuarios reales, validación legal ni piloto observado.

## Errores conservados

- Un error de comillas en la preparación se detectó al compilar el script antes de ejecutarlo.
- Primera descarga: terminaba con caracteres literales de barra invertida y n; JSON.parse falló en posición 963. Se corrigió el producto usando String.fromCharCode(10), no se debilitó el test. Corrida fallida conservada en `first_failure`.
- El primer parser de cobertura esperaba otra forma de respuesta Playwright; la salida vacía no se contó como cobertura cero. Se leyó `source/functions` y se recalculó desde rangos crudos.
- Medir después de reload perdió visibilidad de rangos; se conservó esa captura y se midió antes de navegar, sin ocultar la limitación de la métrica.

## QA aplicable y decisión

Autoevaluación de una función sintética local sin despliegue propio. No es revisión externa ni declaración de producción lista. Roles de trabajo: contrato/arquitectura, Builder, Security acotado a exportación, Tester, documentación y QA propio. No se añadieron funcionalidades fuera de la aprobación para inflar Innovación.

| Criterio | Puntos | Evidencia y descuento |
|---|---:|---|
| Completitud | 15/15 | Tres archivos completos publicados, contrato de 16 campos y cinco archivos de entrega. |
| Ejecutabilidad | 15/15 | runs: syntax, cuatro regression, final-browser-positive, todos exit 0. |
| Seguridad | 12/15 | metadata/readPage/downloadReference, lista cerrada, no cuerpo/token, mutante de permiso detectado; sin auditoría externa ni CVEs actualizados. |
| Testing | 12/15 | 118 Python, 37 Chromium, dos rojos causales; rangos V8 no equivalen a cobertura de ramas/líneas, sin carga. |
| Arquitectura | 9/10 | Reutiliza endpoint protegido sin backend nuevo, versión fijada; alcance deliberadamente un documento ficticio. |
| DevOps | N/A, 10 | Módulo local sin despliegue propio autorizado; se verifica CI heredado, no se declara producción desplegable. |
| Documentación | 10/10 | Runbook y recibo con comandos, hashes, errores y límites concretos. |
| Innovación | 4/5 | Salvaguardas implementadas: hash fuente separado, detección de deriva, URL sin credenciales, revalidación antes de guardar; no se amplía producto. |
| Proceso QA | 3/5 | Evidencia íntegra, controles rojos y aprobación preservada; selección de pruebas y score del propio autor, revisión independiente pendiente. |
| Total | **80/90 = 88.89/100** | **Por debajo de 90. Entrega en PR con deuda explícita, no firma de merge ni producción.** |

Deudas localizadas en PR19: revisión externa de selección de pruebas; cobertura de líneas/ramas no medida; auditoría visual/accesibilidad y cadena heredada no certificadas. No se crean nuevos issues fuera del lote aprobado. Legal/privacy, búsqueda, reportar, cuentas reales y piloto siguen fuera de esta entrega; no son fallos que un test sintético pueda cerrar.

Nota de proceso heredado: el recibo 11 clasificó como LIGERO un cambio de workflow. TITAN exige FULL para workflows: esa clasificación fue incorrecta. El CI efectivamente ejecutado no borra la discrepancia metodológica. Este recibo no reescribe aquel historial ni presenta una aprobación retrospectiva.

## TITAN SCORECARD

| Rol | Score aplicable | Loops | Observaciones |
|---|---|---:|---|
| Contrato/arquitectura | 9/10 | 1 | Referencia secundaria sin body y versión fija. |
| Builder | 30/30 | 2 | JSON.parse detectó el delimitador inválido; corregido sin aflojar el banco. |
| Security | 12/15 | 1 | Frontera nueva de metadatos medida; sin certificación global. |
| Tester | 12/15 | 2 | 37 checkpoints finales y dos mutantes; límites V8 conservados. |
| Documentación | 10/10 | 1 | Evidencia cruda reproducible y runbook. |
| Salvaguardas dentro del alcance | 4/5 | 1 | Sin funcionalidades ajenas al permiso. |
| QA propio | 3/5 | 1 | No sustituye revisión independiente. |
| Total | 80/90, 88.89/100 | | DevOps 10 puntos N/A. Deuda, sin merge. |

--- METODO TITAN ---
Accion delicada: SI (validacion de metadatos de exportacion)
Modo aplicado: TITAN FULL
Rubrica: 80/90 -> 88.89/100
N/A declarados: 10 (DevOps: modulo local sin despliegue propio)
Review externo: pedido; sin aprobacion emitida, deuda de PR19
Instrumento: brain-env; Python y Chromium con stdout/stderr crudos en el archivo de evidencia; dos mutantes exit 1
