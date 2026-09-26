# Auditoría del sistema funcional Corpus contra el plan v2

Fecha: 2026-09-26 ART  
Sujeto exacto: repo `gatehot59-star/corpus-legal-tarija`, rama `main`, commit `c273c659ee90f2259f540cb14c576d6a16dcfb40`.  
Referencia de producto: [plan integral Corpus v2](https://app.clickup.com/90171457413/docs/2kza6fw5-12477/2kza6fw5-14737), cuya enmienda vigente exige 80 tipos, 110 ocurrencias, calibración antes de ampliar, permiso gratuito separado del pago y demo cerrada antes del piloto.  
Referencia de estado posterior: [relevamiento del 25-sep](https://app.clickup.com/90171457413/docs/2kza6fw5-15417/2kza6fw5-17677) y [checklist de entrega del 26-sep](https://app.clickup.com/90171457413/docs/2kza6fw5-15457/2kza6fw5-17717).

## Veredicto

El sistema funcional **existe y ya permite una demo técnica cerrada**: login, autorización por petición, búsqueda, lectura exacta, guardado de referencias, reporte privado, logout, recuperación y cuarentena tienen implementación y pruebas sintéticas. **No cumple todavía el hito de apertura del piloto F08 del plan v2**, porque el repo principal no contiene un circuito operativo para altas/grants reales, la evidencia es sintética, la gold OCR humana no está cerrada, la vigencia está medida solo parcialmente, la revisión jurídica/privacidad M01 no está acreditada y el flujo de compartir investigación no está implementado.

Encontré además un defecto funcional concreto: `Application.search()` pasa solo `rows[0]` a `search_snapshot()`. Con dos colecciones autorizadas y snapshots distintos, la búsqueda FTS consulta el snapshot de la primera colección, aunque el conjunto de permisos incluya ambas. La checklist reciente declara dos colecciones, pero este caso no aparece en la aceptación de navegador, que usa una sola colección sintética.

No firmo “listo para piloto universitario” ni “producto comercial”. Firmo **demo técnica condicionada**, con bloqueadores claros y un camino corto para llegar a F08.

## Evidencia de que el núcleo está construido

- El commit analizado es `c273c659ee90f2259f540cb14c576d6a16dcfb40`, cuyo mensaje declara integración del Corpus real completo en Django staging.
- El árbol contiene `sistema/django_app`, contratos, lector exacto, políticas, tests Django y workflow de CI.
- `sistema/django_app/corpus/models.py` define `PolicyState`, `Collection`, `Membership`, `AccessGrant`, `Locator`, `SavedReference`, `PrivateFeedback` y `AttemptBudget`.
- `sistema/django_app/corpus/access.py` reautoriza por usuario, epoch, membresía, grant vigente/no revocado, colección habilitada y locator no retirado. El código no usa staff como bypass.
- `sistema/django_app/corpus/services.py` implementa `search`, `read`, `save_reference`, `list_references`, `report_error` y `OfflineRecovery`.
- `sistema/django_app/corpus/views.py` expone login con CSRF, logout POST, recuperación, búsqueda, lectura, guardado, feedback privado y health checks.
- `tests/browser_acceptance.py` recorre en fixture sintético: acceso denegado sin sesión, login, búsqueda, lectura con SHA y procedencia, guardado, reporte con payload XSS, logout, replay de cookie vieja, aislamiento entre usuarios, móvil, recuperación, expiración del token y retirada del locator.
- `.github/workflows/corpus-django.yml` ejecuta tests Django, cobertura mínima 85%, contenedor no-root sin red y aceptación Chromium sintética bajo Xvfb. El checkout está fijado a SHA.
- El README de Django registra 38 tests, 93% de líneas de aplicación y CI verde del commit `2cd4ca7ebe23422d617d3e5c741e084a4cdfeedf`; también aclara que la inspección visual/E2E con navegador no estaba medida en ese momento. El workflow actual sí contiene el job browser, pero la evidencia de producto real sigue siendo distinta de la fixture.

Esto confirma una base técnica real. No confirma cobertura jurídica, piloto con usuarios ni producción.

## Cruce contra los gates del plan v2

### 1. Calibración antes de ampliar: PARCIAL

El plan exige B05 antes de C01.1, C03.1 y C05.1, I08 para calibrar y I09 antes de ampliar. En el sistema actual hay código y datos de prueba, pero no encontré en main una compuerta operativa que impida ampliar una colección real sin acta de calibración, tope, recursos y decisión I09. El contrato de aplicación protege lectura y escritura de referencias, no la ingesta ni la aprobación del plan de datos.

Estado: **NO MEDIDO como gate del producto**. Las pruebas de contratos del plan prueban el verificador del grafo, no que el servicio de Corpus lo obedezca.

### 2. Procedencia, identidad y lectura exacta: PARCIALMENTE CONFIRMADO

La procedencia v2 y el lector nacional tienen contratos y mutantes. El lector Django abre con `O_RDONLY | O_NOFOLLOW | O_NONBLOCK`, verifica SHA sobre el descriptor abierto y lee esos mismos bytes mediante `/proc/self/fd`. La respuesta marca fuente secundaria y `NOT_MEASURED`, lo que evita vender vigencia o autoridad que no fueron probadas.

Pero la integración real se hizo con un adaptador de snapshot; el README del lote dice explícitamente que no certifica todos los snapshots, correo, carga ni ensayo institucional. El hash prueba integridad del archivo respecto del digest registrado, no autenticidad estatal, fidelidad jurídica, vigencia o permiso de redistribución.

Estado: **CONFIRMADO para integridad técnica del snapshot aislado; NO MEDIDO para calidad jurídica, vigencia y autorización de publicación**.

### 3. AccessGrant gratuito separado del pago: IMPLEMENTADO COMO MODELO, NO COMO OPERACIÓN

El modelo tiene `origin`, `valid_from`, `valid_until`, `revoked_at`, usuario, grupo, colección, emisor y evidencia. `access.py` exige grant vigente, grupo/membresía habilitados y colección habilitada. Esto encaja con el contrato conceptual del plan.

El defecto es que `origin` es un `CharField(max_length=30)` sin `CheckConstraint` ni enum para distinguir `free` y `paid`. La separación queda en convención, no en el esquema. Además, el README de Django dice: “no existe todavía consola de alta real”. El repo principal no contiene el portal de empleados que permitiría crear, revocar y observar cuentas piloto; los PRs 30 y 31 siguen abiertos.

Estado: **PARCIAL**. La política funciona en fixture; la operación real de altas, grants, revocaciones y telemetría de piloto no está en main.

### 4. Demo cerrada M01-M04: TÉCNICAMENTE SINTÉTICA, NO PILOTO

La aceptación browser demuestra el recorrido equivalente con `fixture-ana` y `fixture-ben`, una base sintética, una colección sintética, contraseña pública de prueba y correo en memoria. Es buena evidencia de que el flujo puede fallar y que el aislamiento básico existe.

No demuestra M01: revisión jurídica y privacidad de una muestra real, incluida la relación temporal familiar. No demuestra M02: snapshot mínimo con procedencia y retirada usado por usuarios reales. No demuestra M03: seguridad, restore y cierre de rutas alternativas en la configuración de entrega institucional. No demuestra M04: observación por docentes/editor y tareas equivalentes con usuarios universitarios.

Estado: **CONFIRMADO como demo técnica sintética; NO MEDIDO como demo cerrada del plan**.

### 5. Datos y OCR: BLOQUEADOR DE CALIDAD, NO DE CÓDIGO

El estado documentado más reciente informa 6.079 documentos, 818 OCR y gold set de 120 páginas completa en los tres motores, pero la transcripción gold humana sigue pendiente. Sin gold humana no hay CER/WER independiente para decidir Paddle/Tesseract ni autorización para presentar el OCR como confiable.

La vigencia también sigue parcial: el relevamiento informa 13/527 leyes medidas. La interfaz muestra “Vigencia no medida”, que es correcto, pero F08 no debe comunicarse como biblioteca jurídica vigente completa.

La composición actual incluye 5.030 Autos Supremos, 1.034 documentos de Gaceta de Tarija y 15 de LexiVox. La auditoría histórica de privacidad ya midió nombres de partes en jurisprudencia. Por eso M01 no es decorativa: la parte mayoritaria del corpus no debe abrirse como si fuera normativa anónima.

Estado: **NO MEDIDO para OCR humano y vigencia amplia; privacidad de la muestra real pendiente de cierre formal**.

### 6. Flujo buscar → leer → guardar → reportar: PARCIALMENTE CONFIRMADO

El flujo existe de punta a punta en fixture y el sistema guarda un locator, no texto copiado. El reporte es privado y la lectura/reporte vuelven a autorizar.

Hallazgo funcional: en `sistema/django_app/corpus/services.py`:

```python
rows = list(access.eligible(principal).select_related("collection").order_by(
    "collection_id", "uid", "version_sha256"))
...
snippets = search_snapshot(rows[0], query.strip(), allowed)
```

`reader.search_snapshot()` abre el snapshot recibido y busca allí. Por tanto, con dos colecciones habilitadas, la búsqueda no itera los snapshots: usa solo el primero. La aceptación browser crea y prueba una única colección sintética, así que no puede dar rojo por este caso.

Estado: **REFUTADO como búsqueda multi-colección completa**. La lectura exacta por locator sí queda aislada por colección/UID/versión.

### 7. Compartir investigación: FALTA

El plan define culminar para encontrar, verificar, guardar y compartir investigación jurídica. El modelo actual solo tiene `SavedReference` con dueño y lista privada. No hay modelo de investigación compartida, destinatario/grupo, permiso de compartir, revocación del enlace ni exportación controlada de una colección de referencias.

Estado: **REFUTADO como cobertura del objetivo funcional completo**. Guardar una referencia propia no equivale a compartir investigación.

### 8. Restore y continuidad: PARCIAL

`OfflineRecovery` y los tests de recuperación implementan cuarentena, destino nuevo, digest y epoch, y el README prohíbe restaurar a una fuente vieja sin autoridad actual. Es un diseño prudente.

La evidencia es de SQLite sintético y no acredita restore del snapshot real, integridad del backup real, operación con WAL detenido, recuperación de la instancia desplegada ni procedimiento ejecutado por un operador independiente. El propio README deja pendientes métricas operativas y auditoría de cambios de política.

Estado: **CONFIRMADO en fixture; NO MEDIDO en servicio y datos reales**.

### 9. I10 y cobro: NO HABILITADO

El plan v2 exige inversión máxima de aprendizaje, horas mensuales, contribución neta, mínimos de pagadores y renovadores, denominadores, fecha de evaluación y periodicidad/moneda de US$10 antes de ofertar. No hay evidencia de esos valores ni de un embudo real. El relevamiento de mercado sirve como hipótesis, no como validación comercial.

Estado: **NO MEDIDO**. No corresponde vender “validado” ni abrir membresía por el estado técnico.

## Hallazgos priorizados

### H-01 ALTO: búsqueda incompleta con dos colecciones

Archivo: `sistema/django_app/corpus/services.py`, método `Application.search`; causa: se pasa `rows[0]` a `search_snapshot`. Impacto: un usuario autorizado puede no encontrar documentos de la segunda colección aunque pueda leerlos directamente. El caso positivo de dos colecciones falta en browser acceptance.

Corrección mínima: agrupar locators por snapshot, consultar cada snapshot con sus UIDs permitidos, combinar hits de forma determinista y paginar después de la unión; agregar fixture con dos colecciones, resultados exclusivos de cada una y un control de no autorización.

### H-02 ALTO: main no tiene operación de piloto real

El README Django dice que solo hay fixtures y que no existe consola de alta real. Los PRs 30 y 31, que agregan navegación/UI profesional, siguen abiertos según el listado vivo de GitHub. La checklist del 26-sep describe un staging externo con ocho accesos, pero no es evidencia de que ese estado corresponda al commit main auditado ni de que esté fuera de `CORPUS_TEST_PROFILE=synthetic`.

Corrección mínima: fijar SHA desplegado, perfil efectivo, digest de base y lista de cuentas/grants; cerrar una ruta de alta/revocación operable; hacer smoke con una cuenta nueva; mantener fixtures separadas y desactivarlas antes de entregar.

### H-03 MEDIO: contrato free/paid no está reforzado por esquema

`AccessGrant.origin` acepta cualquier cadena. La política v2 necesita distinguir gratuito y pago sin ambigüedad. Agregar enum/check constraint, migración y tests de valores inválidos, además de impedir que un grant pagado sea necesario para el control positivo gratuito.

### H-04 ALTO: calidad jurídica y privacidad no tienen cierre de gate

Gold humana OCR pendiente, vigencia 13/527 y revisión M01 no acreditada. El corpus contiene jurisprudencia con nombres de partes y el plan exige privacidad antes del piloto. No es un fallo del login: es un fallo de readiness del producto.

Corrección mínima: cerrar gold humana con evidencia cruda, publicar estado de vigencia por documento, seleccionar muestra jurídica/privacidad, documentar decisiones de anonimización y repetir búsqueda/lectura/exportación sobre esa muestra.

### H-05 MEDIO: README y estado de main están desincronizados

`README.md` raíz mantiene inventario de 2026-09-03 y `COBERTURA.md` se autodeclara viejo. El README Django afirma “No merge ni despliegue” aunque `main` contiene el squash de integración real del 23-sep. Fechar datos viejos es correcto; dejarlos como puerta de entrada sin un puntero inequívoco al estado actual hace que un operador arranque desde el mapa equivocado.

Corrección mínima: un `CONTEXTO-CORPUS.md` canónico en main con SHA actual, composición, perfil desplegado, gates F08, bloqueadores y enlaces a evidencia; marcar los documentos históricos como históricos desde el índice, no solo dentro del archivo.

## Qué queda confirmado y qué no

**CONFIRMADO:** núcleo Django ejecutable en fixture; autorización por petición; lectura exacta con hash; guardado de locator; feedback privado; logout y recuperación; pruebas de mutantes y browser sintético; workflow PR con cobertura y contenedor no-root.

**REFUTADO:** búsqueda completa sobre múltiples colecciones; cumplimiento del objetivo “guardar y compartir”; afirmación de que el repo principal ya contiene una operación de alta real para el piloto.

**NO MEDIDO:** calidad jurídica de muestra; gold OCR humana; vigencia completa; restore real; despliegue fuera del perfil synthetic; cuentas universitarias reales; M01-M04; D09/E03/E04/F08 ejecutados; I08/I09/I10; conversión, pago y renovación.

## Recomendación de secuencia

1. Corregir H-01 y probarlo con dos snapshots.
2. Congelar un SHA de staging y retirar la ambigüedad synthetic/producción.
3. Cerrar gold OCR humana y la muestra M01 de privacidad/vigencia.
4. Operar D09 con altas, grants y revocación, luego ejecutar M04 con dos usuarios docentes/abogados y tareas equivalentes.
5. Solo si M01-M04 y F08 quedan verdes, medir I10. No meter pagos antes.

La prioridad no es otra ronda general de arquitectura: es **una versión reproducible, con dos colecciones, muestra revisada y piloto real**.

## Instrumentos y límites

- Lectura viva del repositorio GitHub: árbol de `main`, commit, archivos Django, contratos, tests y workflow.
- Lectura de los Docs públicos: plan v2, relevamiento de estado y checklist de entrega.
- Comparación estructural entre el código del repo y los gates del plan.
- No se inició el servidor real ni se tocó la VM, staging, base viva, cuentas, credenciales, despliegue o PRs abiertos.
- No se ejecutó el browser CI desde esta auditoría; se inspeccionó su código y el check declarado por el commit.
- No se auditaron las ramas abiertas 30/31 como si fueran main.

## Scorecard de auditoría

| Criterio aplicable | Score | Evidencia |
|---|---:|---|
| Completitud | 9/10 | Este informe cubre plan, repo, sistema, pruebas y límites; no incluye runtime live no autorizado. |
| Calidad del razonamiento | 9/10 | El hallazgo H-01 sale del llamador real y del lector real, no de una primitiva aislada. |
| Documentación | 9/10 | Hallazgos con archivos, SHAs, estados y correcciones; links al plan y evidencia. |
| Proceso QA | 8/10 | Se inspeccionaron checks, fixtures y falsadores; no se ejecutó una nueva corrida runtime. |
| **Total normalizado** | **35/40 = 87,5/100** | Auditoría aprobada como informe, no como aprobación del producto. |

--- METODO TITAN ---
Accion delicada: NO; solo lectura y documentación en rama de auditoría.
Modo aplicado: TITAN FULL.
Rubrica: 35/40 -> 87,5/100; no es score del producto.
N/A declarados: deployment productivo y ejecución sobre cuentas reales, porque no fueron autorizados ni necesarios para localizar H-01.
Review externo: no pedido; esta nota es auditoría, no PR de producto.
Instrumento: GitHub live sobre main `c273c659ee90f2259f540cb14c576d6a16dcfb40`, lectura de código/tests/workflow y contraste con Docs públicos; sin runtime nuevo.
Maquina: ClickUp/GitHub MCP para lectura y escritura documental.
Artefactos: este archivo + Doc público de ClickUp enlazado en el cierre.
