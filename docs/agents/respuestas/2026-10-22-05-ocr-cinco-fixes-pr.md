# Cinco defectos OCR corregidos en rama; PR33 abierto, sin merge ni despliegue

## Pedido

«Corregí los cinco defectos y abrí un PR». Implementación de los cinco defectos de la auditoría003, no de sus dos límites de cobertura. El operador pasó explícitamente de auditor a implementador. No se modificaron estados de tareas.

[PR33](https://github.com/gatehot59-star/corpus-legal-tarija/pull/33). [Doc espejo](https://app.clickup.com/90171457413/docs/2kza6fw5-24297).

## Sujeto, herramientas y máquina

Repo gatehot59-star/corpus-legal-tarija. Rama titan/ocr-five-fixes-20261022; código bb5578f798a5846fe1388c4e84dc2332ea537197. PR apilado hacia titan/ocr-vl-sidecar-20261022, base5a108c028792b409974b00ebe04be5e1215f9029. Main no contiene aún el sidecar; este PR no introduce toda su historia ni habilita un despliegue por implicación.

Se leyeron las ramas y archivos de los PR abiertos32,31,30,27,1 antes de editar: ninguno tocaba sistema/ocr_sidecar. Edición y pruebas en sandbox aislado; GitHub conectado para rama/commit/PR y solicitud de revisión Copilot. Brain-env para Git y SSH sólo lectura. Sin GPU, sin runtime ajeno de inferencia, sin cambios de servicios, credenciales o bases.

## Cinco correcciones

1. pdfimages inspecciona raster por página. Auto deriva página mixta a OCR y conserva native_text; txt rechaza el caso mixto en lugar de omitirlo. Inventario inesperado falla cerrado. Logo también dispara OCR: costo conservador declarado.
2. complete_document rechaza páginas no blancas con texto vacío o sólo espacios, aunque tengan bloques. Blancos explícitos siguen válidos.
3. Progreso terminal actualizado por worker y supervisor. Fallos parciales conservan conteos de páginas validadas, sin éxito global falso.
4. timed_out indica vencimiento real del plazo; SIGKILL externo produce worker_signal y signal9. No se deduce OOM de una señal.
5. validate_result coteja esquema, texto, Markdown, conteos, estado y fidelity_certified con las páginas. Lo usa supervisor y GET result; rechaza contradicciones, no las reescribe.

## Medición

Primero13 grupos nuevos sobre el código original: exit1,15 fallos de subpruebas y2 errores por campos nuevos ausentes. Los cinco defectos se refutaron con aserciones pertinentes; los dos errores adicionales no se usan como prueba causal. Después60/60. Tras agregar3 grupos de inventario/API:63/63,exit0. py_compile exit0. La segunda corrida completa no es una medición independiente del modelo.

Comando: desde sistema/ocr_sidecar, `python -m unittest -v`. Linux con /usr/bin/pdfinfo,pdftotext,pdftoppm,pdfimages. Entorno de test: Python3.12, Pillow12.2.0 y pypdf6.14.2 preinstalados, no runtime productivo. El pin del servicio Pillow13.0.0 no cambió. Los fixtures PDF usan pypdf sólo en tests. Parsers, procesos y API Unix reales; instalación/YAML/modelo doblados en pruebas que lo declaran. No inferencia VL nueva, OOM real ni exactitud jurídica.

## Evidencia cruda

Archivo `docs/agents/evidencia/2026-10-22-05-ocr-cinco-fixes.json`: JSON con payload XZ/base64,38188 bytes descomprimidos, SHA25642620a97aa36263184bd977c4ab1f6d6e1a928f1277fcb5136e1f0b384894e87. Incluye stdout/stderr íntegro antes/después/final, exitcodes y diff completo. Decodificar data con base64, descomprimir XZ, verificar bytes/hash y parsear JSON. No secretos ni originales privados.

Fuentes recuperadas desde Git y comparadas con los archivos probados:
- sistema/ocr_sidecar/ocr_service.py:90df955df6edec61cc2c27876997848ba25c014d8dc5661fc2f1e91c6cf69a97,36878bytes.
- sistema/ocr_sidecar/test_adversarial_fixes.py:7d834f0e7d7522b856619e1f1bb80a9fc2982840cff668e684c9ddd0b7db0cfe,12111bytes.
- sistema/ocr_sidecar/test_worker_contract.py:d4bd8d075e63b6ccb79955294e7f49a5e7c7978cc2e3667b6f76c0a3fb9ab0dc,4543bytes.

## Continuidad

VM consultada read-only: pdfimages24.02.0 presente; OCR,CorpusAPI,Djangostaging activos. Archivo montado sigue con SHAba6319aed537f601745e9d54c1156ce5ee2dd3da500581a94347fc4b64ce5e0f. No tiene estos arreglos todavía. Revisión Copilot solicitada, status requested; no equivale a aprobación.

## QA y NO MEDIDO

Preparación productiva78/100, inferior a90, sin aprobación de merge/despliegue. N/A0. Completitud15/15 por cinco regresiones corregidas; ejecutabilidad14/15 por63 tests/compilación sin VL nuevo; seguridad11/15 por negativos y HTTP sin auditoría transitiva nueva; testing12/15 por rojo/verde sin cobertura/estrés nuevos; arquitectura8/10 por diff acotado con latencia extra no medida; DevOps3/10 sin humo ni despliegue; documentación9/10 por comandos/límites con review pendiente; innovación2/5 por revalidación de lectura/progreso sin scope adicional; proceso4/5 por evidencia/hash sin revisión externa cerrada. Las evidencias de cada criterio son el código y banco de este commit, los logs del paquete y la consulta read-only arriba; no se afirma evidencia de lo que se descontó.

Incumplimiento declarado: rúbrica cargada antes de editar, puntuación emitida después del commit y no antes de esa escritura. No se oculta ni compensa por tests verdes.

NO MEDIDO: nuevo clasificador con VL real, exactitud jurídica, costo por logos/páginas mixtas, memoria, compatibilidad en runtime completo, auditoría de dependencias, revisión externa cerrada. Los límites de multiplicidad y calidad semántica siguen abiertos. No se crearon issues ni se enviaron mensajes adicionales sin autorización.

## Veredicto

Cinco fallos corregidos en código y protegidos por regresiones, PR abierto para revisión. No afirmar que el OCR montado quedó corregido, que las cinco tareas están cerradas ni que el PR está aprobado para merge.

--- METODO PROMETEO ---
Accion delicada: SI
Modo aplicado: FULL
Maquina: sandbox; brain-env y VM sólo lectura
Rubrica:78/100,N/A0, deuda declarada
Review externo: Copilot solicitado, aún no aprobación
Instrumento: unittest/py_compile, rojo antes/verde después, logs completos en evidencia hermana
Artefactos: docs/agents/respuestas/2026-10-22-05-ocr-cinco-fixes-pr.md + https://app.clickup.com/90171457413/docs/2kza6fw5-24297
