# 2026-09-23 23:55 · PaddleOCR móvil vs Tesseract sobre el PDF de Juan

## Pedido
Instalar PaddleOCR aislado y compararlo contra Tesseract.

## Entorno aislado
- `/tmp/paddle-ocr-venv` en la VM build; no toca Corpus ni el servicio.
- `paddlepaddle 3.3.1`.
- `paddleocr 3.7.0`.
- Modelos usados: `PP-OCRv5_mobile_det` + `latin_PP-OCRv5_mobile_rec`.
- CPU, `enable_mkldnn=False` después de que el modelo medium por defecto fallara con `ConvertPirAttribute2RuntimeAttribute` en oneDNN.
- El modelo PP-OCRv6 medium por defecto fue descartado para CPU: quedó más de 3 minutos en una inferencia y no es una comparación operable en esta VM.

## Muestra controlada
PDF oficial de Juan Pérez, mismas imágenes renderizadas a 300 dpi en gris, páginas 1 y 10.

### Tesseract, `spa`, PSM 3
- `tessdata_fast`: página 1 **3.034 caracteres**, página 10 **1.826**, total **4.860**, **19 s**.
- `tessdata_best`: página 1 **3.044**, página 10 **1.845**, total **4.889**, **23 s**.

### PaddleOCR PP-OCRv5 mobile
- Página 1: **3.017 caracteres**, **56,92 s**.
- Página 10: **1.823 caracteres**, **37,45 s**.
- Total: **4.840 caracteres**, aproximadamente **94 s**.

## Calidad observable en la muestra
PaddleOCR devuelve una salida más estructurada y legible en la página 1: conserva encabezados como `ASAMBLEA LEGISLATIVA DEPARTAMENTAL DE TARIJA`, `R.A. N° 161/2013-2014`, `RESOLUCIÓN`, `Constitución Política del Estado`, y `TARIJEÑOS`. El Tesseract crudo conserva más basura de encabezado/sello y reporta errores como `Gue`, `Tarja`, `pario` y `torieños` en esa página.

PaddleOCR detectó en página 1: `gue=1`, `que=10`, `pario=0`, `tarja=1`, `tarija=5`, `torieños=0`, `tarijeños=1`; en página 10: `gue=0`, `que=2`, `pario=0`, `tarja=0`, `tarija=3`, `torieños=0`, `tarijeños=0`.

La comparación de conteos no es todavía una métrica de exactitud legal: falta transcripción dorada cotejada contra la imagen. No se declara PaddleOCR ganador definitivo solo por apariencia.

## Veredicto
**PaddleOCR móvil es un candidato real mejor que Tesseract para calidad estructural en esta muestra corta, pero cuesta aproximadamente 4-5x el tiempo del control en CPU.** No se reprocesan todavía los 784 documentos. El siguiente paso es un gold set de 120-200 páginas con CER/WER, números de artículos, fechas, citas, recall de búsqueda, layout y RAM.

## No medido
- CER/WER formal de PaddleOCR.
- Exactitud de campos jurídicos sobre transcripción dorada.
- Rendimiento PaddleOCR en las 2.624 páginas.
- PP-StructureV3 separado para tablas/orden de lectura.
- Comparación GPU o Actions x64.

## Evidencia de proceso
- Primera ejecución del modelo medium falló con oneDNN; se corrigió desactivando oneDNN y se eligió el modelo móvil.
- El smoke test inicial falló por asumir que `predict()` era iterador; se corrigió y la corrida final produjo ambos textos.
