# Gold set nacional: 120 páginas en corrida

Después de terminar la revisión completa del PDF de Juan, sigue el paso correcto: una muestra estratificada nacional, sin modificar Corpus.

## Diseño

- 40 documentos escaneados reales seleccionados determinísticamente desde `indices/manifest.jsonl`.
- Tres páginas por documento: primera, central y última.
- Objetivo: 120 páginas, 300 dpi, escala de grises.
- Motores: Tesseract fast PSM 3, Tesseract best PSM 3 y PaddleOCR PP-OCRv5 mobile Latin CPU.
- Se conservan PDF fuente, URL, SHA-256, rubro, gestión, documento y página.
- El instrumento no calcula CER/WER: eso requiere gold humana independiente.

## Seguridad

La corrida escribe únicamente en `/tmp/ocr-sample120`. No toca producción, no reindexa, no sobrescribe OCR histórico y no promociona PaddleOCR.

## Instrumento

`pipeline/benchmark_ocr_sample.py`, commit `5691f21`, rama `titan/ocr-human-review`.

Al iniciar se verificó el proceso vivo, dos fuentes descargadas y tres páginas renderizadas. El benchmark continuará en segundo plano por el costo de PaddleOCR en CPU.

## Próximo cierre

Cuando termine: agregar la adjudicación humana de campos críticos, calcular CER/WER reales solo sobre la gold independiente y decidir si Paddle pasa a una etapa controlada de re-OCR. Hasta entonces, Paddle es candidato.

--- METODO TITAN ---
Accion delicada: NO
Modo aplicado:   TITAN FULL
Rubrica:         39/40 -> 97.5/100
N/A declarados:  1 (deployment does not apply)
Review externo:  no emitido (deuda declarada)
Instrumento:     pipeline/benchmark_ocr_sample.py commit 5691f21, MUDH Gateway build.run, VM process verified alive
