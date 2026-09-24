# OCR humano: PaddleOCR gana el muestreo, pero todavía no se promociona

## 1. Pedido

Comparar como humano Tesseract fast, Tesseract best y PaddleOCR sobre las mismas 10 páginas del PDF oficial de Juan Pérez, atendiendo especialmente a identificadores de resolución, artículos, fechas, nombres propios, cantidades, citas legales, orden de párrafos y ruido de sellos o firmas.

## 2. Herramientas y máquina

- `MUDH Gateway -> build.run` en el entorno aislado de BRAIN y `vm-corpus.sh` para leer `/tmp/ocr-goldset` en la VM de Corpus.
- `MUDH Gateway -> playwright` para abrir la URL oficial de la fuente y confirmar que el servidor entrega `RPA_161_200_2013_2014.pdf`.
- No se modificó producción ni el OCR original. No se gastó runtime ajeno.

## 3. Qué se midió

Misma entrada renderizada a 300 dpi, páginas 1, 2, 5, 10, 15, 20, 25, 30, 40 y 44.

- Tesseract fast: 18.926 caracteres, 91,33 s, gate 10/10.
- Tesseract best: 19.095 caracteres, 98,26 s, gate 10/10.
- PaddleOCR PP-OCRv5 mobile Latin CPU: 18.892 caracteres, 407,82 s, gate 10/10.
- Comparación humana de contenido sustantivo: PaddleOCR fue el texto preferible en 10/10 páginas. Tesseract no fue preferible en ninguna página.

PaddleOCR preservó mejor los identificadores `R.A.`, artículos, nombres y frases legales. Tesseract repitió errores que sí cambian el significado: `94/74`, `39/32`, `30/20`, `GOTO 65/SOTO 5`, `tarijeños/torieños`, además de corrupción de vocabulario jurídico.

## 4. Evidencia cruda

Fuente oficial descargada por la corrida previa:

```text
URL: https://www.tarija.gob.bo/gaceta-oficial/resoluciones-del-pleno-de-la-asamblea?download=832:resoluciones-del-pleno-de-la-asamblea-161-al-200-del-2013-2014&start=500
Archivo: RPA_161_200_2013_2014.pdf
Páginas: 44
Bytes: 2875681
SHA-256: 6b9dcffaffdfb997dc4227dea2d89d0a01b4474d6c00abfa4bb4152ca4750784
```

Benchmark:

```text
pdf=/tmp/juan-source.pdf
pages=[1,2,5,10,15,20,25,30,40,44]
dpi=300
engines=tesseract_fast_psm3,tesseract_best_psm3,paddleocr_ppocrv5_mobile_latin_cpu
all existing structural gates: true
```

Los textos completos por motor están en la VM, bajo `/tmp/ocr-goldset/{tesseract_fast_psm3,tesseract_best_psm3,paddleocr}`. La anotación reproducible de cada página y cada campo crítico quedó en `docs/agents/evidencia/2026-09-24-02-ocr-human-review.json`.

## 5. Hallazgos por página

- **1:** Paddle conserva el cuerpo del preámbulo; Tesseract produce `pario`, `torieños` y múltiples sustituciones.
- **2:** Paddle conserva el cuerpo histórico y la cita final; los tres motores necesitan limpiar sellos y firmas. La fecha requiere confirmación visual antes de publicación porque los motores discrepan.
- **5:** Paddle recupera `Arts. 94 y 105` y `Resolución 102/2013-2014`; Tesseract confunde artículos y número de resolución.
- **10:** Paddle conserva `DECLARAR DESIERTA`, `SETAR` y las comisiones; Tesseract rompe nombres jurídicos y la convocatoria.
- **15:** Paddle conserva `Acta de la Sesión Ordinaria N° 38/2013-2014`; Tesseract pierde el encabezado y corrompe la oración principal.
- **20:** Paddle recupera `R.A. N° 179/2013-2014` y `R.A. N° 109/2013-2014`; Tesseract fast confunde los identificadores.
- **25:** Paddle conserva el proyecto del `Estadio Olímpico`, los artículos 94, 105 y 117 y la fecha; Tesseract daña el título y el Art. 118.
- **30:** Paddle conserva `Convenio Interinstitucional N° 39/2011`, `65 butacas` y el plazo de 30 días; Tesseract altera números y nombres. La lectura humana corrige `COTO GS` a `GOTO 65`.
- **40:** Paddle conserva `Acta de la Sesión Ordinaria N° 45/2013-2014`; Tesseract best lee `44` donde corresponde `64`.
- **44:** Paddle conserva `Artículos 88, 94 y 105`, `APROCA` y `aplazar el tratamiento`; Tesseract best altera 88/94 y la frase decisoria.

## 6. Veredicto

PaddleOCR es el candidato técnicamente superior para el texto jurídico sustantivo de este documento, aun con un costo de CPU aproximadamente 4,5 veces mayor. No autorizo reemplazar el OCR histórico todavía: falta una gold completa y realmente independiente, y la página 2 demuestra que una fecha aislada puede seguir siendo un riesgo aunque el cuerpo parezca mejor.

Siguiente paso correcto: ampliar la revisión a 120-200 páginas representativas, transcribir los campos críticos de forma independiente, calcular CER/WER reales y medir costo por página. El OCR original queda preservado; Paddle pasa a candidato, no a producción.

## 7. NO MEDIDO

- CER y WER verdaderos contra una transcripción gold carácter por carácter de las 10 páginas.
- Verificación visual independiente de cada fecha, numeral y firma.
- Calidad sobre las otras 2.614 páginas escaneadas.
- Seguridad de una promoción nacional de PaddleOCR.

## 8. Archivos generados

- `docs/agents/evidencia/2026-09-24-02-ocr-human-review.json`
- `docs/agents/respuestas/2026-09-24-02-ocr-human-review.md`

--- METODO TITAN ---
Accion delicada: NO
Modo aplicado:   TITAN FULL
Rubrica:         38/40 -> 95/100
N/A declarados:  2 (DevOps and deployment do not apply to an OCR evidence report)
Review externo:  no emitido (deuda declarada)
Instrumento:     BRAIN via MUDH Gateway build.run, exit=0; raw benchmark retained at `/tmp/ocr-goldset`
