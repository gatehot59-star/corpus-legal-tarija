# ABBYY: credencial aceptada, consulta de saldo denegada

15 de octubre de 2026, 18:47 a 18:48 ART. Operador: BRAIN / GPT-6 Astra.

## Resultado y alcance

Se usó la contraseña indicada por el usuario, con autorización explícita, para solicitudes HTTPS de sólo lectura desde brain-env al endpoint estadounidense de ABBYY Cloud OCR SDK. El identificador de autenticación fue el Application ID, no el correo de la cuenta.

**PASS: la credencial fue aceptada en listTasks.** La misma ruta devolvió HTTP 200 con autenticación y HTTP 401 sin ella. Esto comprueba acceso autenticado en el endpoint US; no es una prueba de reconocimiento OCR.

**BLOQUEADO: getApplicationInfo devolvió HTTP 403 y el cuerpo `403 Prohibited`.** No se recuperaron saldo, tipo de aplicación ni vencimiento. ABBYY documenta que esta consulta está deshabilitada por defecto y debe habilitarse en Settings de la aplicación. La causa concreta del 403 no se inspeccionó en la consola; no se afirma que falte crédito.

**NO MEDIDO: procesamiento OCR, costo por página, exactitud y comparación con Tesseract/PaddleOCR.** No se subieron archivos, no se crearon trabajos OCR, no se compró crédito y no se cambió configuración de la cuenta ni del producto.

## Instrumento y resultados

Ejecutor: servicio Python existente de brain-env. Instrumento: urllib.request con verificación TLS mediante ssl.create_default_context(), encabezado Basic únicamente en las dos consultas autenticadas al host cloud-westus.ocrsdk.com, redirecciones deshabilitadas y tiempos máximos de 20/15 segundos. Ambos scripts terminaron con exit 0 y stderr vacío. El exit del script sólo indica que registró los resultados; el veredicto se apoya en los códigos HTTP.

1. GET /v2/getApplicationInfo sin autenticación: 401, cuerpo vacío, 1,287251 s.
2. GET /v2/getApplicationInfo con autenticación: 403, cuerpo `403 Prohibited`, 1,257991 s.
3. GET /v2/listTasks con autenticación: 200, JSON de tipo objeto, 1,195380 s.
4. GET /v2/listTasks sin autenticación: 401, cuerpo vacío.

El cuerpo de listTasks se excluyó intencionalmente del registro para evitar publicar información de trabajos; se conserva su SHA-256. No se infiere un conteo de trabajos a partir del tipo JSON. Las demás respuestas y los metadatos obtenidos se publican sin cambios en los dos registros enlazados.

- [Registro de solicitudes](../evidencia/2026-10-15-12-abbyy-auth.json), SHA-256 `fca07d46e5aed33949089d8e6a9e2f9b842a6fc6458d925bc82f594ed6be9bf4`.
- [Control negativo sobre listTasks](../evidencia/2026-10-15-12-abbyy-negative.json), SHA-256 `647c6d3f0aebf252041f9a519d7403a7f4613bb1a27c41e24004df822ced2628`.

No se publica el payload de ejecución porque contenía la credencial. Los registros no incluyen contraseña, encabezado Authorization ni su valor Base64. No se configuró almacenamiento permanente del secreto. No se auditó la retención interna del transporte de ejecución ni se puede retirar la contraseña ya compartida en la conversación con esta prueba; se recomendó rotarla para uso permanente, sin hacerlo sin autorización.

## Antes de firmar

Autenticación aceptada en listTasks -> respuesta HTTP del mismo endpoint con/sin encabezado -> podía dar rojo y devolvió 200/401 -> PASS acotado.

Saldo conocido -> getApplicationInfo -> podía fallar y devolvió 403 -> NO MEDIDO, consulta bloqueada.

ABBYY reconoce correctamente -> ningún trabajo OCR enviado -> instrumento ausente -> NO MEDIDO.

## Próximo paso necesario

En la consola de ABBYY Cloud OCR SDK, abrir Settings bajo `corpus legal` y habilitar getApplicationInfo. Luego repetir sólo esa consulta para conocer el crédito y vencimiento antes de procesar páginas. No usar la contraseña de aplicación como contraseña del correo ni de la consola de usuario. No iniciar otro reset.

## QA y límites

TITAN FULL por tratamiento de una credencial sensible. Se revisaron autorización explícita, destino HTTPS fijo, validación TLS, rechazo de redirecciones y ausencia del secreto en los registros que se publican. No es una auditoría OWASP del servicio ABBYY ni de Corpus.

La rúbrica formal se registró después de las solicitudes, no antes: incumplimiento de orden documentado. No se presenta esta autoevaluación como revisión externa.

Rúbrica del diagnóstico: Completitud 14/15 (faltan los datos de saldo, explícitamente bloqueados); Ejecutabilidad 15/15 (ambos scripts exit 0 y cuatro respuestas en los registros); Seguridad 10/15 (la clave ya estaba expuesta en la conversación, no hay auditoría de retención del transporte ni rotación); Documentación 10/10 (alcance, respuestas, hashes y próximo paso explícitos); Proceso QA 3/5 (control negativo real, rúbrica posterior y sin revisión externa). Total 52/60, 86,7/100. Los 40 puntos N/A corresponden a Testing de producto, Arquitectura, DevOps e Innovación: no se entrega código ni infraestructura. No alcanza el umbral para aprobar configuración permanente; sí queda registrada la medición de acceso, con sus límites.

No se corrigió ni desplegó producto y no se abrió PR. La rama documental se leyó en vivo en `05ecc45c4beca50cd28ca45f2d4bfc371b0c6049`; se consultaron los PR abiertos sin modificarlos. Se añaden únicamente este informe y dos registros sin secretos.

## Fuentes oficiales consultadas en vivo

- [Autenticación: Application ID y Application Password](https://support.abbyy.com/hc/en-us/articles/360017326739-Authentication).
- [getApplicationInfo: habilitación en Settings y datos de saldo](https://support.abbyy.com/hc/en-us/articles/360017326699-getApplicationInfo-Method).
