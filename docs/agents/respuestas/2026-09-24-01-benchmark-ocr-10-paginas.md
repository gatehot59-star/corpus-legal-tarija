# 2026-09-24 02:00 · Benchmark OCR ampliado a 10 páginas

## Instrumento
`sistema/pipeline/benchmark_ocr.py`, commit `2d5c018`, ejecutado en la VM build sobre el PDF oficial de Juan Pérez con páginas 1, 2, 5, 10, 15, 20, 25, 30, 40 y 44. Todas las variantes recibieron los mismos PNG a 300 dpi en gris.

## Resultado crudo
- Tesseract fast, `spa`, PSM 3: 10 páginas, 18.926 caracteres, 91,33 s, gate 10/10.
- Tesseract best, `spa`, PSM 3: 10 páginas, 19.095 caracteres, 98,26 s, gate 10/10.
- PaddleOCR PP-OCRv5 mobile Latin CPU: 10 páginas, 18.892 caracteres, 407,82 s, gate 10/10.

Conteos de términos disputados en las 10 páginas:
- Tesseract fast: `gue=5`, `que=54`, `pario=3`, `tarja=4`, `tarija=35`, `torieños=1`, `tarijeños=0`.
- Tesseract best: `gue=4`, `que=50`, `pario=0`, `tarja=9`, `tarija=24`, `torieños=0`, `tarijeños=0`.
- PaddleOCR mobile: `gue=1`, `que=56`, `pario=0`, `tarja=2`, `tarija=53`, `torieños=0`, `tarijeños=1`.

## Veredicto
PaddleOCR muestra una señal favorable en errores léxicos observables: menos `gue`, `pario` y `tarja`, y aparece `tarijeños` en una página donde Tesseract no lo recuperó. Pero cuesta aproximadamente **4,5x** Tesseract fast en CPU. Los tres pasan el gate estructural 10/10.

**No es todavía una exactitud legal probada.** Los conteos no son una gold transcription: no permiten afirmar CER/WER ni que toda sustitución sea correcta. Falta transcripción humana de las 10 páginas o una muestra dorada de 120-200 páginas.

## Estado
El instrumento y los textos crudos de los tres motores quedaron aislados en `/tmp/ocr-goldset` de la VM; no se modificó el corpus ni staging. La decisión correcta es preparar el gold set y evaluar campos jurídicos antes de reprocesar los 784 escaneados.
