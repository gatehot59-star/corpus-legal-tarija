# PaddleOCR-VL-1.6: corrida incompleta por límite de tiempo

Revisión: 16-oct-2026 08:09 ART. Operador BRAIN / GPT-6 Astra.

## Veredicto acotado

**FAIL de completitud bajo el presupuesto sellado:** se terminaron tres de cinco páginas; la cuarta superó 1800 segundos y el runner abortó. La quinta no se ejecutó. **NO MEDIDO:** CER/WER del banco completo, exactitud jurídica y superioridad sobre Tesseract/PaddleOCR anteriores.

El fallo se registró el **15-oct a las 22:09:10 ART**, equivalente a `2026-10-16T01:09:10.375644+00:00`. La comprobación actual de `/proc/291224` no encontró ese proceso. No quedó corriendo toda la noche. No se relanzó, no se amplió el timeout ni se modificó la configuración.

Para esta VM y configuración CPU, el tiempo observado no es práctico para una lectura interactiva: las tres páginas completas tardaron aproximadamente 25,51, 19,91 y 23,35 minutos. Esto no prueba que la precisión sea mala ni que otro hardware no lo ejecute mejor. Tampoco se diagnosticó la causa raíz de lentitud como fallo del modelo.

## Evidencia de tiempos, sin redondear

Contenido de `timings.json` recuperado de la VM:

```json
[
  {
    "id": "h01-p001",
    "seconds": 1530.631917962004,
    "characters": 2845,
    "blocks": 16,
    "raw_sha256": "725e64df2443e6a12d8f7a06b5ea7a97b8a3ae02db7b9b3cc41d143eb136d2cf",
    "rss_peak_kib": 7702720
  },
  {
    "id": "h01-p002",
    "seconds": 1194.4102359520039,
    "characters": 2254,
    "blocks": 20,
    "raw_sha256": "7e5a0c1cab1afb0065f72d03ea6db368f0de843dc953c6f78a147d4ee39a379e",
    "rss_peak_kib": 7702720
  },
  {
    "id": "h02-p001",
    "seconds": 1400.8209659550048,
    "characters": 2597,
    "blocks": 16,
    "raw_sha256": "ea0999ff6fc78475e93933405bda655f67659d46744e2055963186201a5862fa",
    "rss_peak_kib": 7725104
  }
]
```

Corresponden a Ley 524 páginas 1 y 2, y Ley 523 página 1. La página detenida es Ley 523 página 2; la no ejecutada es Ley 523 página 3.

El archivo `status.json` quedó atrasado al abortar; no debe interpretarse como proceso activo:

```json
{
  "phase": "inference",
  "page": "h02-p002",
  "started_utc": "2026-10-16T00:39:10.263488+00:00",
  "completed_pages": 3
}
```

El traceback en `failure.json` muestra la excepción durante generación nativa, dentro de `paddle.nn.functional.common.linear`, al entregarse la señal del runner. Última línea literal:

```text
TimeoutError: page or warmup exceeded 1800 seconds
```

No se capturó el exit del proceso con un supervisor externo: el código publicado sale con 1 al capturar la excepción, pero ese 1 no se presenta como exit observado. Sí se observaron el archivo de fallo, el traceback y la ausencia del proceso.

## El evaluador rechazó la corrida incompleta

Se ejecutó sin alterar el manifiesto, las predicciones ni la referencia:

```text
python3 /workspace/ocr-heldout-20261015/heldout.py score /workspace/ocr-heldout-20261015/manifest.json --gold /workspace/ocr-heldout-20261015/gold-ai-v1.json --gold-sha256 36097a8dcb63e601cf3a3108d63fb9178a3d57067019c5b9c9e4d4c3331806d7 --predictions /workspace/paddle-vl16-heldout-20261015/predictions.json
```

Exit observado: **2**. Stdout: vacío. Stderr completo:

```json
{"error": "cobertura incompleta o páginas extra", "metrics_emitted": false}
```

**PASS del bloqueo de cobertura:** el instrumento podía emitir error ante un banco incompleto y lo hizo. No se rellenaron páginas faltantes con texto vacío ni se publicó un promedio de tres como resultado de cinco.

## Preservación y límites de publicación

Se recuperaron desde la VM los registros y las predicciones a `/workspace/paddle-vl16-heldout-20261015`. Los originales permanecen en `/tmp/paddle-vl16-heldout-20261015` de la VM. Hashes SHA-256 de los archivos leídos:

- failure.json, 5673 bytes: `0a0418a55b022713c648ea9d968e2972114eb84430f5425223b9060aa61a94d0`.
- timings.json, 668 bytes: `efcaba724361870fbc8511914593f787726fe7989ad28ba9c917577765803aa5`.
- predictions.json, 8395 bytes: `0499325eb96a9f725d6594cd20b601c1c65e5882c67bfa926b21cfad541018b6`.
- run.log, 8433 bytes: `0f6f712d0b632722d6f84b6adde18f984f2c57496f2242d41a2d6c3b4a7ca3b4`.

Este informe publica tiempos y estado completos, el recibo del evaluador completo y sólo la última línea del traceback. Los logs íntegros y las tres predicciones no están contenidos en este commit: se declara explícitamente ese límite, sin presentar hashes como sustituto del contenido. No se inspeccionaron ni puntuaron los textos parciales para ajustar el modelo.

[Runner y sello previos](https://github.com/gatehot59-star/corpus-legal-tarija/commit/35d23b2c3186e8545b27ee2e4bc141d0ff9eabcd).

## Próxima decisión

Una continuación requiere una corrida nueva o continuación versionada con un presupuesto distinto, preservando este FAIL. No se debe modificar retrospectivamente el límite sellado ni prometer superioridad sin completar y evaluar el banco. No se ejecutó esa continuación en esta revisión.

La referencia sigue siendo IA adjudicada, no gold humano. No se tocó producción, no se publicaron pesos, no hubo merge, deploy, gasto ni nueva inferencia.
