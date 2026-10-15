# Banco OCR held-out v1: cinco páginas nuevas reservadas; gold pendiente

15 de octubre de 2026. **Se crearon las entradas, el protocolo de anotación y el evaluador; NO se completó una referencia transcrita ni una comparación de precisión.** Estado: `HELD_OUT_RESERVED_GOLD_PENDING`.

## Qué quedó creado

Cinco páginas reales de dos documentos completos, descargados nuevamente desde la fuente oficial, rasterizados y sellados por SHA-256. No son cuatro deformaciones de un mismo texto ni páginas adicionales de las leyes usadas para ajustar el OCR.

- Ley Departamental 524: páginas 1 y 2, presupuesto institucional y POA 2027.
- Ley Departamental 523: páginas 1, 2 y 3, estructura de cargos y escala salarial.

Se eligieron las primeras dos leyes del listado oficial consultado, antes de cualquier resultado de candidato, y se incluyeron todas sus páginas. No se promete una muestra aleatoria ni representativa de Bolivia. La unidad independiente son **dos documentos**, no cinco leyes.

Fuente: [listado oficial de leyes de Tarija](https://www.tarija.gob.bo/gaceta-oficial/leyes-departamentales). Las dos URL completas, respuestas HTTP 200, hashes PDF, tamaños, metadatos y páginas figuran en `benchmarks/ocr-heldout-20261015/manifest.json`.

La selección quedó registrada a las 14:26:43 ART. La primera rasterización terminó a las 14:27:21 ART. **Cero llamadas a Tesseract, Paddle, calibrado o ABBYY sobre estas páginas.** No se cambió ningún motor ni se consumió el test para seleccionar un ganador.

## Separación comprobada y sus límites

Se contrastaron los dos SHA-256 de PDF y sus URL con `gold_index.jsonl` de la muestra anterior de 120 páginas, y con los nombres hash de los 40 PDF cacheados. Ninguno de los dos documentos apareció. Se publican los cuarenta hashes excluidos, el hash del índice consultado y los seis hashes de imágenes reales del banco de la mañana. Tampoco coinciden las nuevas imágenes con esas seis.

Esto es separación por documento respecto de **los bancos comprobados**, no prueba de ausencia en el entrenamiento de los motores, en cada trabajo histórico o en otra copia visualmente equivalente con bytes diferentes. No se hizo búsqueda exhaustiva de duplicados perceptuales en todo Corpus.

El banco anterior queda para desarrollo/regresión. Estas cinco páginas quedan reservadas para la primera evaluación de una versión congelada. Si se inspeccionan resultados para ajustar un motor, el conjunto pasa a ser desarrollo y debe reservarse otro conjunto documental para el siguiente claim held-out.

## La referencia que falta

`pdftotext` devolvió 5.821 caracteres de la Ley 524, pero el PDF declara `Scanner System Image Conversion` y contiene imágenes escaneadas. **Una capa de texto incrustada no demuestra que sea una transcripción correcta ni independiente.** Se leyó una muestra durante descubrimiento; se descartó como gold. No se conoce qué generó esa capa.

La Ley 523 no produjo texto extraíble. Por eso las cinco referencias permanecen `null`, no cadenas vacías disfrazadas de transcripciones ni resultados de otro OCR usados como verdad.

Falta realizar dos transcripciones visuales independientes y resolver discrepancias antes de puntuar. No se asignó trabajo a terceros ni se fingió un revisor externo. El benchmark de precisión no está listo para evaluar hasta completar esta etapa.

### Contrato de anotación

1. Transcribir sólo desde las imágenes. No mostrar la capa de texto del PDF ni las salidas de candidatos a los transcriptores.
2. Mantener todo texto impreso legible, encabezados y pies; no corregir ortografía, cifras, tildes o fechas según otra norma.
3. Orden visual: columna izquierda antes que derecha, de arriba hacia abajo; tablas por filas con notas de regiones explícitas. No se afirma que estas páginas tengan tablas sin revisar su contenido visual.
4. Firmas manuscritas y marcas no textuales sólo se excluyen con regiones documentadas. Toda ilegibilidad pendiente bloquea puntuación, no se convierte silenciosamente en blanco.
5. Verificar especialmente montos, fechas, números, artículos y negaciones. Guardar las dos transcripciones originales y la resolución de discrepancias fuera del alcance del motor candidato.
6. Congelar la referencia adjudicada y su hash, junto con código/configuración de cada motor, antes de inspeccionar resultados.

Los nombres declarados de transcriptores y adjudicador son metadatos: el script puede exigirlos y detectar coincidencias evidentes, pero **no certifica identidad ni independencia humana**. La separación por permisos y el registro temporal de los revisores son controles operativos pendientes; no hay ACL nueva ni custodia secreta implementada por este script.

## Preparación reproducible

Poppler `pdftoppm 24.02.0`, 300 dpi, opción `-gray`, PNG sin texto incrustado proveniente del PDF. Los cinco PNG son RGB con sus tres canales iguales, comprobado por diferencias de canales; son grises pese al contenedor RGB. Se registran hashes tanto del archivo PNG como de píxeles decodificados.

El materializador volvió a descargar ambos PDF desde la fuente y regeneró las cinco imágenes en un directorio nuevo: **los cinco hashes PNG coincidieron exactamente**. Si la fuente cambia o el renderer no coincide, se detiene; no reemplaza la muestra silenciosamente. Los PDF y PNG no se commitean.

Archivos locales de trabajo: brain-env `/workspace/ocr-heldout-20261015` para fuentes, manifiesto, programa y evidencia; VM `/tmp/ocr-heldout-20261015` para PDF y cinco PNG, y `/tmp/ocr-heldout-20261015-reproduced` para la reproducción nueva comprobada. Las imágenes no fueron publicadas como endpoint ni se modificó producción.

Desde la raíz del repo, en un entorno con Python 3 y Poppler 24.02.0:

```sh
python3 benchmarks/ocr-heldout-20261015/heldout.py selftest benchmarks/ocr-heldout-20261015/manifest.json
python3 benchmarks/ocr-heldout-20261015/heldout.py status benchmarks/ocr-heldout-20261015/manifest.json
python3 benchmarks/ocr-heldout-20261015/heldout.py materialize benchmarks/ocr-heldout-20261015/manifest.json --root /tmp/corpus-heldout-from-git
python3 benchmarks/ocr-heldout-20261015/heldout.py verify benchmarks/ocr-heldout-20261015/manifest.json --root /tmp/corpus-heldout-from-git
```

El destino de `materialize` debe ser nuevo: no sobrescribe un directorio existente. `status` devuelve 2 mientras esta reserva carece de gold; eso es el resultado esperado, no un fallo de rasterización.

### Interfaz de puntuación futura, no ejecutada contra páginas reales

Acción `score`, mismo manifiesto, argumentos `--gold`, `--gold-sha256` y `--predictions`. Se exigen cobertura exacta de las cinco páginas, hashes de imagen, referencia no vacía, estado adjudicado y ausencia de regiones sin resolver. Una salida OCR vacía sí se admite y se penaliza como borrado total.

Gold JSON: `benchmark_id`, `status=adjudicated`, `origin=independent_visual_transcription`, `transcribers` con dos identificadores distintos, `adjudicator`, y `pages` indexadas por los cinco IDs. Cada página lleva `image_sha256`, `status=adjudicated`, `unresolved_regions=[]`, `scope_notes` y `text`.

Predicciones JSON: `benchmark_id`, `engine_author` y `pages`; cada página contiene `image_sha256` y `text`. El autor declarado no debe coincidir con los dos transcriptores. El scorer normaliza únicamente NFC y blancos, calcula CER/WER por página, micro agregado y macro por documento. Los dos documentos son demasiado pocos para proclamar representatividad o superioridad general. No se generan métricas de exactitud jurídica.

El módulo `score` valida los archivos suministrados, no vuelve a correr OCR ni demuestra que el contenido declarado provenga efectivamente del motor. Antes de usarlo se debe ejecutar `verify` contra las imágenes y conservar comandos/exits/salidas reales del candidato. El hash de gold debe haberse registrado antes de la corrida, no calcularse después para justificarla.

## Evidencia cruda de verificación

Comandos ejecutados en VM desde `/tmp/ocr-heldout-20261015`. El programa tiene SHA-256 `7e6dd89820d6e7a9d2fdefaed0127d34e6157976f61c890ab94c17c1978caf3e`; manifiesto `d423c44f29e57724eaec692f6457dbb432ccd645af6b21380bd437d1e197f750`.

`python3 heldout.py selftest manifest.json`, exit 0, stderr vacío:

```json
{
  "checks": [
    "identical_zero",
    "number_and_negation_detected",
    "empty_output_full_deletion",
    "duplication_can_exceed_100pct",
    "pending_gold_rejected",
    "same_transcriber_rejected",
    "ocr_reference_rejected",
    "missing_page_rejected",
    "changed_image_rejected",
    "unresolved_region_rejected",
    "engine_author_transcriber_rejected",
    "prior_document_rejected"
  ],
  "passed": 12,
  "real_ocr_runs": 0,
  "real_gold_created": 0,
  "test_data": "artificial only, not benchmark annotations"
}
```

`python3 heldout.py status manifest.json`, exit 2, stderr vacío:

```json
{"state": "HELD_OUT_RESERVED_GOLD_PENDING", "pages": 5, "gold_status": "PENDING_DOUBLE_VISUAL_TRANSCRIPTION_AND_ADJUDICATION", "ready_for_accuracy_scoring": false}
```

`python3 heldout.py score manifest.json`, exit 2, stdout vacío, stderr:

```json
{"error": "falta gold sellado o predicciones", "metrics_emitted": false}
```

`python3 heldout.py verify manifest.json --root /tmp/ocr-heldout-20261015`, exit 0, stderr vacío:

```json
{
  "verified_documents": 2,
  "verified_pages": 5,
  "gold_status": "PENDING_DOUBLE_VISUAL_TRANSCRIPTION_AND_ADJUDICATION",
  "candidate_ocr_runs_in_this_tool": 0
}
```

`python3 heldout.py materialize manifest.json --root /tmp/ocr-heldout-20261015-reproduced`, exit 0, stderr vacío:

```json
{
  "verified_documents": 2,
  "verified_pages": 5,
  "gold_status": "PENDING_DOUBLE_VISUAL_TRANSCRIPTION_AND_ADJUDICATION",
  "candidate_ocr_runs_in_this_tool": 0
}
```

Las doce pruebas usan frases artificiales, incluyendo omisión de negación, cambio de número, duplicación y borrado total. **No son cinco páginas transcritas ni resultados de candidatos.** Los comandos y stderr/stdout completos de la primera rasterización están en `manifest.json`.

## Veredicto por afirmación

- Reserva de cinco entradas reproducibles: PASS, hashes de PDF/PNG y nueva materialización exacta.
- No coincidencia documental en la muestra anterior inspeccionada: PASS, intersección vacía contra cuarenta hashes publicados.
- Scorer detecta los defectos modelados por doce controles: PASS sobre fixtures artificiales.
- Referencias de las cinco páginas: PENDIENTES, cero transcripciones creadas.
- Precisión y ranking held-out: NO MEDIDOS; ningún candidato corrió.
- Independencia universal, custodia secreta o representatividad jurídica: NO MEDIDAS.

TITAN LIGERO, instrumento acotado sin modificar gates de producto, main, permisos ni contratos consumidos. No hay auditor externo. Se publican tres archivos, sin merge ni despliegue. El siguiente paso necesario es la anotación visual independiente, no otra corrida sin gold.
