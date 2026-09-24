# 2026-09-23 22:35 · Comparación OCR medida

## Pedido
Comparar el OCR actual contra una alternativa mejor antes de decidir el reprocesamiento integral.

## Control identificado
El repositorio usa Tesseract con `spa`, `--psm 3`, rasterizado a 300 dpi en gris. La VM tiene Tesseract 5.3.4. La corrida histórica del corpus mide 784 documentos y 2.624 páginas; este benchmark se ejecutó sobre el PDF oficial de Juan Pérez, páginas 1 y 10, como muestra corta.

## Medición ejecutada
PDF oficial: 44 páginas, 2.875.681 bytes, SHA-256 `6b9dcffaffdfb997dc4227dea2d89d0a01b4474d6c00abfa4bb4152ca4750784`.

Tesseract `spa`, 300 dpi, mismas imágenes:

| Variante | Páginas | Caracteres | Tiempo | Observación |
|---|---:|---:|---:|---|
| `tessdata_fast`, PSM 3 | 1 y 10 | 4.860 | 19 s | control actual aproximado |
| `tessdata_best`, PSM 3 | 1 y 10 | 4.889 | 23 s | +29 caracteres, +0,6%; no prueba mayor exactitud |

La VM no tenía instalados `paddleocr`, `paddlepaddle`, `docTR`, `easyocr`, `opencv` ni `torch`. Por tanto, **PaddleOCR todavía no fue medido**. La búsqueda externa sí confirma que PaddleOCR/PP-OCRv5 en español y PP-StructureV3 son candidatos razonables, pero sus benchmarks públicos no son evidencia sobre este corpus.

## Veredicto
`tessdata_best` no justifica por sí solo reprocesar los 784 documentos: agrega costo y cambia muy poco el volumen, sin gold set no permite afirmar que corrige `gue`, `Tarja`, `torieños` o números legales. El ganador de motores sigue **NO MEDIDO**.

## Próximo benchmark válido
Instalar PaddleOCR en un entorno aislado, fijar versión y modelos, ejecutar PP-OCRv5 español sobre las mismas páginas y comparar CER/WER, números de artículos, fechas, citas, recall de búsqueda, orden de lectura, RAM y tiempo. Después repetir sobre 120-200 páginas estratificadas antes de tocar los 784 documentos.

## Evidencia cruda
- `ENGINE_BINARIES`: `/usr/bin/tesseract`, `tesseract 5.3.4`, `/usr/bin/pdftoppm`, `/usr/bin/pdfinfo`.
- Módulos Python: `paddleocr=NO paddlepaddle=NO easyocr=NO doctr=NO pytesseract=NO cv2=NO torch=NO`.
- `spa.traineddata` fast y best fueron descargados para la comparación; ambos corrieron con exit 0 sobre las dos páginas.
- Documento PDF conservado por hash; ningún Corpus ni producción fue modificado.
