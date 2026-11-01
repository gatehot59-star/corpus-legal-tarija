# Planilla para el gold humano de la Ley 524 p. 1: 9 franjas del escaneo, 24 renglones de la referencia y ningún OCR a la vista

## 1. Pedido y veredicto

Pedido literal: «DAME EL ARCHIVO Q DEBO REVISAR». Viene de la respuesta anterior: la página que procesó la CPU (Ley 524, p. 1, h01-p001) no tiene gold humano; la única referencia es la transcripción IA congelada, con human_review=false.

**Entregado:** una planilla PDF de 8 hojas para que Abraham valide esa referencia contra el escaneo oficial. Hoja 1: instrucciones y formato de respuesta. Hoja 2: página completa con los cortes F1 a F9. Hojas 3 a 7: cada franja del escaneo con sus renglones debajo, R01 a R24. Hoja 8: respuesta y datos de control. No muestra ninguna salida OCR.

- PDF: [revision-humana-ley-524-p1.pdf](https://t90171457413.p.clickup-attachments.com/t90171457413/8b6e2ac0-9a6e-514e-95f2-0d2a661be494/revision-humana-ley-524-p1.pdf?view=open), adjunto de ClickUp, 4.320.414 bytes, SHA-256 `d3fd0d76d4830b9f48a60e724345786748ca1c542e4c511590107723f46c1e98`.
- Doc espejo: [1-nov-2026 · Tu planilla para el gold humano de la Ley 524 p. 1](https://app.clickup.com/90171457413/docs/2kza6fw5-26237), ruta Space > Doc.
- Manifiesto con la numeración congelada de renglones y franjas: `docs/agents/evidencia/2026-11-01-03-planilla-revision-ley524-p1/manifest.json`.

**Conclusión, no medición:** la planilla está lista. La exactitud de la referencia y la de la CPU contra gold humano siguen NO MEDIDAS hasta que vuelva la revisión.

## 2. Herramientas, máquina y escrituras

- Sandbox de ClickUp Brain, sin red: poppler 22.12.0 (pdftoppm, pdfinfo, pdfimages, pdftotext), Pillow 12.2.0, WeasyPrint 69.0 y las fuentes DejaVu de matplotlib. Entradas: el adjunto de ClickUp del PDF oficial (attachment:1a7e60a8-3b63-4c22-acff-e4ff06a754c1.pdf) y el de la referencia (attachment:27b27a68-fadd-42ec-96d4-536b2926d61a.json), verificados por SHA-256.
- brain-env, sólo lectura: estructura de la referencia y cajas de diseño de raw-0001.json de la corrida CPU 4eb6c147c31d45b3b57c8a95669e8ac5; búsqueda de gold humano en el taller; lectura por SSH de la VM Corpus (nombres de archivo y tablas de bases, sin escribir).
- Escrituras: el adjunto PDF, tres previsualizaciones de control no compartidas, este commit y el Doc espejo. No se corrió OCR, GPU ni API; no se tocó la VM, el producto, PR33 ni el schedule.

## 3. Qué se midió

Antes de la planilla, en el turno anterior y sin publicar entonces:

- Búsqueda de gold humano para h01-p001: la referencia declara human_review=false; el gold set de 120 páginas declara gold_text=False y su índice no contiene la Ley 524 (overlap-check sin coincidencias); en el taller y en la VM sólo aparecieron una guía de revisión de Tesseract del 2-sep, una cola de revisión del 3-sep y scripts del gold set de 120 páginas. Ninguno tiene una transcripción humana de esta ley. Instrumento: búsqueda por nombre de archivo y por tablas de bases, que podía dar rojo si el archivo existía con esos nombres; no prueba ausencia bajo cualquier nombre.
- Salida CPU contra la referencia IA, no contra gold humano: 16 ediciones de carácter en crudo (0,5606 %) y 1 con espacios normalizados sobre 2.843 caracteres (0,0352 %): «Presupuestó» donde la referencia dice «Presupuesto», en el título del Artículo 6. 1 de 401 palabras (0,2494 %). 23 de 23 números iguales.

En este turno:

- Entradas: PDF y referencia coinciden con lo sellado; texto de h01-p001 de 2.854 caracteres, SHA-256 `12ded3ed113cf7dcd9c1c34335c7d0ec080175430a083a1c83a3f4b428de83fd`; 35 renglones, 24 con texto.
- Render de la página 1 a 300 dpi en grises: 2520 × 3888 y píxeles idénticos a la imagen del banco que procesó el OCR (SHA-256 RGB `7e71fb47a5464b0ad49ecd5d6f6f2b867e36492b8524b2a37887216e00d5a870`).
- Cortes en el punto medio del blanco entre bloques: 0, 995, 1503, 1758, 2075, 2455, 2710, 3216, 3571 y 3888. Las 9 franjas cubren la hoja sin huecos, con 20 píxeles de solapamiento. Asignación verificada por código: cada renglón con texto y cada caja, una sola vez y en orden.
- QA sobre el PDF final con pdftotext: 24/24 renglones presentes junto a su ID; 24/24 mutantes de un carácter rechazados; 24/24 IDs cruzados rechazados; la variante «Presupuestó», que sólo tiene el OCR, ausente. 8 hojas.
- Inspección visual: en la primera construcción, las 8 hojas a 40 dpi y la hoja 3 a 100 dpi; en la final, que sólo cambió la vista general a JPEG, la hoja 2 a 60 dpi. Las franjas muestran el texto que corresponde a sus renglones.

## 4. Evidencia cruda

Primera construcción (vista general en PNG, PDF de 7.604.344 bytes; descartada sólo por peso):

```text
== inputs
29085b9662453ccd51daea02c10bde124b8e0c91adc712d9d6f3f88c8c92b946  ley524.pdf
36097a8dcb63e601cf3a3108d63fb9178a3d57067019c5b9c9e4d4c3331806d7  ref.json
-rw-r--r-- 1 user user 1642786 Nov  1 17:02 ley524.pdf
-rw-r--r-- 1 user user   17008 Nov  1 17:02 ref.json
pdftoppm version 22.12.0
Creator:         Scanner System
Producer:        Scanner System Image Conversion
Pages:           2
Page size:       604.8 x 933.12 pts
page   num  type   width height color comp bpc  enc interp  object ID x-ppi y-ppi size ratio
--------------------------------------------------------------------------------------------
   1     0 image    2521  3889  rgb     3   8  jpeg   no         4  0   300   300  909K 3.2%
   2     1 image    2527  3915  rgb     3   8  jpeg   no         7  0   300   300  682K 2.4%
weasyprint 69.0 pillow 12.2.0
BUILD_OK pdf revision-humana-ley-524-p1.pdf pixel_identical True cuts [0, 995, 1503, 1758, 2075, 2455, 2710, 3216, 3571, 3888] build_sha 451dfca7798f2f094021b38fd2bf1a662c78129f1263f8e7529c38f7b1ef1256
QA {"instrument": "pdftotext (poppler) sobre el PDF final; cada renglón buscado como «Rnn + texto» con espacios normalizados", "pdf_pages": 8, "lines_present_with_id": 24, "lines_total": 24, "mutant_controls_rejected": 24, "wrong_id_controls_rejected": 24, "ocr_only_variant_absent": true}
QA_BAD_ROWS []
```

Construcción final, la entregada (vista general en JPEG calidad 90 y hash de píxeles por franja):

```text
BUILD_OK pdf revision-humana-ley-524-p1.pdf pixel_identical True cuts [0, 995, 1503, 1758, 2075, 2455, 2710, 3216, 3571, 3888] build_sha 452db24c7c805e6bdab7e5a0b8567470909cc65eb7177711b182a8c159f3844a
QA {"instrument": "pdftotext (poppler) sobre el PDF final; cada renglón buscado como «Rnn + texto» con espacios normalizados", "pdf_pages": 8, "lines_present_with_id": 24, "lines_total": 24, "mutant_controls_rejected": 24, "wrong_id_controls_rejected": 24, "ocr_only_variant_absent": true, "failing_rows": []}
452db24c7c805e6bdab7e5a0b8567470909cc65eb7177711b182a8c159f3844a  build.py
d01bb5955e6818554ed7ebc377e9b7834bdf3b9aa287ec1b0891ad6395037677  qa.py
139a7d5ba18d5db92997f827f3af933791f71e6893928f9f9eabd7fe4399ec53  manifest.json
d3fd0d76d4830b9f48a60e724345786748ca1c542e4c511590107723f46c1e98  revision-humana-ley-524-p1.pdf
  13467 build.py
   2180 qa.py
  11341 manifest.json
4320414 revision-humana-ley-524-p1.pdf
```

Ambas construcciones salieron con exit 0. build.py corta con error si cambia algún hash de entrada, la marca human_review, el largo del texto, la estructura de renglones, el tamaño del render o la cobertura de los cortes; qa.py corta con error si falta un renglón o aparece la variante del OCR.

Medición previa contra la referencia IA, salida del instrumento en brain-env (el texto CPU se ubicó por su SHA-256 `fc072bac865c7951fb687e77a9340696e7c0c2a3575705c79f6534e57b4e0451` dentro de la captura terminal seleccionada):

```text
CPU_TEXT_PATHS ['/stdout#json/files/state/4eb6c147c31d45b3b57c8a95669e8ac5/result.json/content#json/pages[0]/text', '/stdout#json/files/state/4eb6c147c31d45b3b57c8a95669e8ac5/result.json/content#json/text']
GOLD_FILE_SHA_OK True
human_review False REF_LEN 2854 CPU_LEN 2845
NFC ref True cpu True
CHAR_EDITS raw 16 CER_raw_pct 0.5606
CHAR_EDITS ws 1 len_ref_ws 2843 CER_ws_pct 0.0352
WORD_EDITS 1 ref_words 401 WER_pct 0.2494
DIFF 1 replace | ref= 'o' | cpu= 'ó' | ctx= '. Artículo 6. (Presupuesto de la Asamblea Legislati'
DIFF_SPANS 1
NUM_ONLY_REF {}
NUM_ONLY_CPU {}
NUM_TOKENS ref 23 cpu 23
```

## 5. Archivos generados

En este commit:

- `docs/agents/evidencia/2026-11-01-03-planilla-revision-ley524-p1/manifest.json`: renglones R01 a R24 con su índice y texto exacto, franjas, cortes, hashes de entradas, de píxeles por franja y del PDF, convenciones de revisión, contaminación declarada y resultado de QA.
- `docs/agents/evidencia/2026-11-01-03-planilla-revision-ley524-p1/build.py`: generador ejecutado.
- `docs/agents/evidencia/2026-11-01-03-planilla-revision-ley524-p1/qa.py`: instrumento de QA ejecutado.
- Este recibo.

Fuera de Git por ser derivados binarios: el PDF, adjunto de ClickUp identificado arriba por SHA-256 y tamaño, y los recortes, identificados por el hash de sus píxeles en el manifiesto.

## 6. NO MEDIDO

- La revisión humana en sí: pendiente de Abraham.
- La exactitud de la referencia IA y la de la salida CPU contra gold humano.
- La legibilidad en su teléfono.
- La reproducibilidad byte a byte del PDF: WeasyPrint puede variar metadatos; lo verificable es el texto del PDF (qa.py) y los píxeles de cada franja.
- El efecto de lo que el revisor ya sabe: en el chat se le dijo que la única diferencia CPU frente a la referencia IA está en el título del Artículo 6. Queda declarado en el manifiesto.

Cuando vuelva la revisión: aplicar cada corrección a su renglón Rnn, congelar el gold humano de h01-p001 con human_review=true, revisor y fecha, y recién ahí medir CER, WER y números de la salida CPU.

--- METODO TITAN / PROMETEO ---
Accion delicada: NO, bitacora y evidencia append-only, un adjunto
Modo aplicado: LIGERO
Maquina: sandbox de ClickUp Brain sin red para el PDF; brain-env y VM Corpus solo lectura
Rubrica: N/A (modo ligero)
N/A declarados: rubrica completa, entrega chica de un archivo para revision humana
Review externo: NO REALIZADO
Instrumento: build.py exit0; qa.py exit0 sobre el PDF final con pdftotext: 24/24 renglones, 24/24 mutantes y 24/24 IDs cruzados rechazados; salida cruda en este archivo
Artefactos: docs/agents/respuestas/2026-11-01-03-planilla-gold-humano-ley524-p1-sin-ocr.md + https://app.clickup.com/90171457413/docs/2kza6fw5-26237
