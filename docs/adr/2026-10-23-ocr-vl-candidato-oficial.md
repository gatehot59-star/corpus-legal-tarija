# Decisión: PaddleOCR-VL-1.6 es candidato oficial, no producción

Fecha de la decisión: 2026-10-23, 22:59 ART (UTC-3).
Estado: candidatura oficial aprobada; promoción a producción NO autorizada.
Proyecto: Corpus Legal Tarija.

## Mandato

Pedido explícito del usuario: «Guardá PaddleOCR-VL como candidato oficial, no producción».

PaddleOCR-VL-1.6 queda registrado como el candidato oficial de OCR de Corpus. Esta decisión se refiere al motor VL probado, no al PaddleOCR PP-OCRv5 de comparaciones antiguas.

## Alcance de la decisión

- Registrar la candidatura y conservar su evidencia.
- No reemplazar el OCR actual ni reindexar textos productivos.
- No mergear ni desplegar el PR #33 por esta decisión.
- El montaje paralelo existente no equivale a adopción productiva.
- Las evaluaciones posteriores deben conservar originales y salidas candidatas separadas. Una prueba autorizada no autoriza la promoción.
- Toda promoción a producción requiere una decisión explícita posterior, distinta de esta candidatura.

## Precedentes y límites que siguen vigentes

- [Comparación de cinco páginas jurídicas](https://github.com/gatehot59-star/corpus-legal-tarija/commit/4dd606c5688b37cf52d25409555a4ae579f12a23): menor error frente a una referencia anotada por IA, no un gold humano.
- [Repeticiones del parche](https://github.com/gatehot59-star/corpus-legal-tarija/commit/94b471ad980316410c1cb3efe955b52044f2f16f): seis lecturas nuevas, texto idéntico en doce pares; los JSON crudos difieren en la ruta temporal. Repetibilidad no demuestra exactitud jurídica general.
- La referencia humana ciega y la generalización jurídica permanecen NO MEDIDAS. No se presenta el resultado como infalibilidad ni certificación jurídica.
- [PR #33](https://github.com/gatehot59-star/corpus-legal-tarija/pull/33) consultado al registrar: abierto, no mergeado; head bb5578f798a5846fe1388c4e84dc2332ea537197. Su base sigue siendo la rama del sidecar, no main. No se modifica el PR.

## Alternativas no adoptadas

No se elige reemplazar ahora el OCR de Corpus, retirar Tesseract ni aceptar automáticamente las transcripciones de VL. Conservar Tesseract no implica que se haya implementado un selector o fallback nuevo.

## Trazabilidad

Registro documental en una rama creada desde main b722bda135943a125152f0031accd15b2ab7b238. No modifica código, servicios, permisos, credenciales, datos de producción ni estados de tareas.

La decisión se refleja también en el [Doc de resultados seleccionado](https://app.clickup.com/90171457413/docs/2kza6fw5-24397), conservando intacta la evidencia histórica de la tanda.

Método: TITAN LIGERO; acción delicada NO; rúbrica N/A por entrega documental. Sin nueva medición, merge ni despliegue en este registro.
