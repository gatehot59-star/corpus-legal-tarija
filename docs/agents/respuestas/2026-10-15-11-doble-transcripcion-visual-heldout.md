# Doble transcripción visual IA del held-out: cinco páginas adjudicadas

15 de octubre de 2026. Se completaron dos lecturas separadas de las cinco páginas y una adjudicación visual posterior. **Es referencia visual anotada por IA, no una transcripción humana certificada ni garantía de cero errores.** No se ejecutó Tesseract, PaddleOCR, calibrado ni ABBYY sobre estas cinco páginas.

## Entregables

- Referencia final: `benchmarks/ocr-heldout-20261015/gold-ai-v1.json`.
- SHA-256 final: `36097a8dcb63e601cf3a3108d63fb9178a3d57067019c5b9c9e4d4c3331806d7`.
- [Archivo descargable con A original, A literal, B, adjudicación v1 descartada, adjudicación v2, gold y validación](https://u228265714.p.clickup-attachments.com/u228265714/ef5335c9-c43c-5fb9-9471-508c9fe4e5fd/corpus-heldout-transcripciones-y-referencia.zip?view=open).
- [Referencia final JSON descargable](https://u228265714.p.clickup-attachments.com/u228265714/c9c9c9ec-4a3f-5a63-a72d-5b101ef65c79/corpus-heldout-referencia-IA.json?view=open).
- [PDF original Ley 524 adjunto al Doc del banco](https://t90171457413.p.clickup-attachments.com/t90171457413/1a7e60a8-3b63-4c22-acff-e4ff06a754c1/heldout-ley-524.pdf?view=open).
- [PDF original Ley 523 adjunto al Doc del banco](https://t90171457413.p.clickup-attachments.com/t90171457413/870ae1d2-23c9-41ab-afdd-ab32d723c39c/heldout-ley-523.pdf?view=open).

Los archivos A/B y revisiones completos están preservados en el ZIP de ClickUp; en Git están la referencia final y este informe, no todas las transcripciones intermedias. Es archivo repartido entre Git y ClickUp, no evidencia íntegramente contenida en Git.

## Fuentes, separación y alcance

Se verificaron los PDF adjuntos contra los hashes del manifiesto congelado:

- Ley 524: `29085b9662453ccd51daea02c10bde124b8e0c91adc712d9d6f3f88c8c92b946`, 1.642.786 bytes.
- Ley 523: `dd85855e5e0d3134e29998776d7c3eb347d3e1ebde24ef890b37fc0c7c4d7d04`, 2.696.319 bytes.

Se generaron vistas PNG de los mismos PDF a 150 dpi y ampliaciones a 300 dpi. Son derivados de los mismos originales, no se afirma que sean los mismos bytes que los PNG grises del banco. Los hashes de imagen en la referencia final identifican las entradas selladas del benchmark. No se leyó capa textual de los PDF para transcribir; tampoco se consultaron resultados de candidatos. La muestra de capa textual que el coordinador había leído durante el descubrimiento anterior no fue entregada a los transcriptores.

AI-A y AI-B recibieron instrucciones separadas de leer las cinco imágenes sin consultar al otro. AI-B inicialmente no consiguió ver píxeles y reportó bloqueo; después se abrieron las imágenes adjuntas y completó las cinco. No se contó el intento bloqueado como una lectura.

AI-C recibió A/B después de su entrega y adjudicó mirando imágenes. El coordinador revisó además páginas y recortes ampliados y señaló errores de la primera adjudicación. AI-C volvió a revisar las cinco imágenes a 300 dpi. Son contextos de agentes separados, no familias de modelos independientes; existe riesgo de sesgos compartidos. El coordinador es autor del instrumento del benchmark y no se presenta como auditor externo.

## Correcciones y decisiones reales

A había agregado etiquetas editoriales de tabla y expandido categorías combinadas en cada fila. Se conservó A original, y A-literal eliminó esas adiciones. La referencia final usa tabulaciones, categorías una sola vez al inicio de cada grupo y celdas siguientes vacías. No se insertan pipes ni la palabra TABLA en el texto puntuable.

B omitió el pie de Ley 523 p. 1. Se comprobó que estaba impreso y se incluyó.

La primera adjudicación introdujo errores nuevos: leyó `Tarija. así como`, quitó tildes a `ítems` y `Única`, quitó el punto final de `T.G.N.` y leyó coma tras `Artículo 5`. Los recortes ampliados contradijeron esas decisiones; se corrigieron a coma tras Tarija, `ítems`, `Única`, `T.G.N.` y punto tras Artículo 5. La v1 no se borró ni se presenta como válida.

Se conservaron las formas visibles de la fuente, no se corrigió por gramática o aritmética:

- Ley 524 p. 2: `DISPOSISICON` en ambos encabezados, verificado letra por letra como D-I-S-P-O-S-I-S-I-C-O-N.
- Ley 523 p. 1: monto anual en números `38.976.276` y en letras terminación `doscientos sesenta y seis`, aunque no coinciden.
- Ley 523 p. 3: `veintiseis` sin tilde en la fecha final; `ítems` y `Única` sí llevan tilde.
- Ley 524 p. 1: `Bs. 595.477.378.` sin guion después del punto, y `Proyectos de Inversión` con mayúscula.

Firmas manuscritas y emblemas decorativos están fuera del alcance puntuable. Se incluyen los nombres/cargos impresos bajo las firmas, encabezados, pies, teléfonos y dirección. El trazo manuscrito marginal de Ley 524 p. 1 está excluido. Estas exclusiones están declaradas por página. No se alteraron las imágenes del banco ni se aplicaron máscaras: una futura salida OCR debe evaluarse con el mismo alcance documentado, sin quitar errores a posteriori guiándose por la referencia.

El coordinador corrigió también notas de alcance de AI-C v2 que decían dos tablas en 523 p. 1 e incluían firma; hay una tabla en esa página y se excluyen firmas manuscritas. Esa rectificación de metadatos no cambió el texto final de AI-C v2.

## Estado del banco

La referencia contiene cinco páginas no vacías, 12.615 caracteres crudos y cero regiones declaradas sin resolver tras adjudicación. Esos conteos y los hashes se comprobaron por código; no certifican exactitud de lectura.

`gold-ai-v1.json` usa `status=adjudicated`, `origin=independent_visual_transcription` para la interfaz del evaluador, y declara explícitamente método IA, `human_review=false` y límites de independencia. El origen significa lectura visual separada, no independencia estadística ni revisión humana.

El manifiesto original conserva su estado histórico `GOLD_PENDING`: no se sobrescribió el sello de selección. La referencia se entrega como archivo nuevo asociado a su SHA-256. El comando `status` de la versión original sólo informa el manifiesto y por eso seguirá mostrando el estado histórico; no interpreta automáticamente este archivo nuevo. No se cambió el evaluador para convertir una revisión IA en certificación humana.

No se corrieron motores candidatos ni se emitió ranking o CER/WER real. La referencia se puede usar como referencia IA versionada en la próxima evaluación, declarando este origen. Una comparación que requiera gold humano independiente sigue pendiente de esa revisión.

## Evidencia de estructura e integridad

Validación final local, 2026-10-15T18:09:14.901970+00:00:

```json
{"benchmark_id":"corpus-heldout-20261015-v1","gold_sha256":"36097a8dcb63e601cf3a3108d63fb9178a3d57067019c5b9c9e4d4c3331806d7","human_review":false,"candidate_ocr_runs":0,"source_pdf_hashes_verified":true,"page_ids":["h01-p001","h01-p002","h02-p001","h02-p002","h02-p003"],"pages_with_nonempty_text":5,"unresolved_regions":0,"reference_chars":12615}
```

La revisión de contenido es visual y sus decisiones están en el ZIP; no se usó una igualdad de hashes como si probara que una palabra es correcta. Los hashes fijan la versión que se anotó y la que se entrega.

## Método y límites

TITAN LIGERO, anotación acotada sin cambiar código de producción, permisos, secretos, CI ni main. PASS de cobertura y entrega de dos lecturas IA más adjudicación; NO MEDIDO de exactitud perfecta y validación humana. No merge, deploy ni mensajes a terceros. No hay promesa de superioridad OCR derivada de esta entrega.
