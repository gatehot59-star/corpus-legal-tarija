# Gold set nacional: 120 páginas completas

La corrida corregida terminó exactamente las 120 páginas esperadas.

## Medición

- 40 documentos escaneados, 3 páginas por documento.
- 120 imágenes fuente a 300 dpi.
- Tesseract fast: 120/120, 850,11 s, gate 120/120.
- Tesseract best: 120/120, 955,27 s, gate 120/120.
- PaddleOCR PP-OCRv5 mobile: 120/120, 5.097,53 s, gate 120/120.

`gold_text=False` sigue siendo el valor correcto: esto es una comparación de candidatos, no una gold humana. La transcripción independiente de las 120 páginas sigue pendiente.

## Estado

El benchmark ya está listo para adjudicación y ranking de riesgo legal. No se tocó producción, no se reindexó el Corpus y no se sobrescribió el OCR histórico.

## Evidencia

- `/tmp/ocr-sample120/report.json`
- `pipeline/benchmark_ocr_sample.py`, commit `11818a9`

--- METODO TITAN ---
Accion delicada: NO
Modo aplicado:   TITAN FULL
Rubrica:         39/40 -> 97.5/100
N/A declarados:  1 (deployment does not apply)
Review externo:  no emitido (deuda declarada)
Instrumento:     benchmark_ocr_sample.py commit 11818a9, report.json verified at /tmp/ocr-sample120
