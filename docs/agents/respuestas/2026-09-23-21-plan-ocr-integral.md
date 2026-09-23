# 2026-09-23 21:30 · Plan integral para OCR de los escaneados

## Corrección de alcance
El peritaje anterior fue puntual sobre el documento de Juan Pérez. No resolvió ni auditó los 784 documentos escaneados. Este recibo corrige explícitamente ese alcance: la deuda es general y debe medirse sobre todo el conjunto.

## Qué está medido
- Población: 784 documentos escaneados, 2.624 páginas.
- Pipeline histórico: `pipeline/ocr_masivo.py`.
- Motor declarado: Tesseract con idioma `spa`, `--psm 3`, rasterizado `pdftoppm -r 300 -gray -png`.
- Gate: volumen, basura de caracteres, plausibilidad léxica y ancla legal a nivel documento.
- README: Ley 007 medida con CER 6,2%, WER 9,3%, F1 de bolsa 0,947 y 38/40 datos jurídicos.
- Segunda pasada existente: solo documentos rechazados por orientación, no una segunda OCR integral.
- La VM staging tiene Tesseract 5.3.4 pero no `spa.traineddata`; PaddleOCR, PaddlePaddle, docTR, EasyOCR, OpenCV y Torch no están instalados allí. No se debe confundir esta ausencia local con la corrida histórica en Actions.
- PDF oficial de Juan: 44 páginas, SHA-256 `6b9dcffaffdfb997dc4227dea2d89d0a01b4474d6c00abfa4bb4152ca4750784`.

## Qué no está medido todavía
- CER/WER y campos jurídicos de PaddleOCR, PP-StructureV3, docTR o cualquier alternativa sobre Tarija.
- Comparación controlada con `tessdata_best`, `--oem 1`, deskew, Sauvola y PSM alternativos.
- PDF/imagen fuente cotejado página por página para los 784 documentos.
- Ganancia de búsqueda, lectura de columnas/tablas, consumo de CPU/RAM y tasa de fallos de un motor alternativo.

## Decisión técnica provisional
No se reemplaza Tesseract sin benchmark. El candidato principal es PaddleOCR PP-OCRv5 en español, con PP-StructureV3 como salida separada de layout/tablas. Tesseract mejorado queda como control y fallback. docTR queda secundario por la incertidumbre del checkpoint español; Surya requiere revisión de licencia GPL y hardware.

## Corrida que corresponde
1. Congelar el control actual, incluyendo versión de Tesseract, `spa.traineddata`, renderer, DPI, PSM y hashes.
2. Crear gold set de 120-200 páginas: Ley 007, Juan Pérez, páginas limpias/degradadas, rotadas, columnas, tablas, sellos y años distintos.
3. Medir control actual, Tesseract mejorado y PaddleOCR español sobre las mismas imágenes.
4. Aceptar un reemplazo solo si mejora CER/WER y campos legales, no reduce recall de búsqueda, conserva páginas y es reproducible offline.
5. Ejecutar los 784 documentos en una copia candidata; preservar el OCR bruto y publicar aparte el texto ganador, layout y cola de revisión humana.

## Regla de seguridad del corpus
No se corregirá silenciosamente el OCR crudo. Cada corrección o texto alternativo debe quedar vinculado a UID, versión, página, motor, modelo y confianza; la promoción a lo que ve el abogado ocurre solo después del benchmark.

## Fuentes externas verificadas
- PaddleOCR oficial: https://github.com/PaddlePaddle/PaddleOCR
- PP-OCRv5 multilingüe: https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/algorithm/PP-OCRv5/PP-OCRv5_multi_languages.en.md
- PP-StructureV3: https://www.paddleocr.ai/latest/en/version3.x/pipeline_usage/PP-StructureV3.html
- Tesseract quality guide: https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html
- docTR: https://github.com/mindee/doctr

## Veredicto
El problema no es solo Juan. El pipeline completo merece una auditoría OCR nueva. Todavía no hay base para afirmar que PaddleOCR gana en este corpus: eso es precisamente lo que debe medir el benchmark.
