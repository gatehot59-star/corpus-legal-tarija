# PR33: primera repetición completa, segunda iniciada; tanda en curso

Fecha: 2026-10-23. Zona: ART, UTC-3. Último corte: **14:54:56 ART**.

## Estado vivo

**EN CURSO: 2 de 6 nuevas inferencias de página terminadas.** La primera repetición del PDF de dos páginas terminó a las 14:54:02 ART, con worker exit 0, sin timeout y sin señal. Duró 1202,405893938 segundos, aproximadamente 20 minutos y 2 segundos. La segunda fue admitida a las 14:54:03 ART y estaba cargando el modelo en el corte de las 14:54:56. La tercera todavía no había sido admitida.

No hay veredicto de repetibilidad: el comparador está programado para contrastar las tres salidas nuevas de cada página y el original después de que terminen los tres workers. No se repitió el verificador para contar lecturas nuevas, no se relanzó la tanda y no se modificó el instrumento durante la corrida.

## Pedido, ejecución y localización

Se ejecutan tres trabajos nuevos, secuenciales, del mismo PDF de dos páginas: A,B / A,B / A,B. Cada trabajo vuelve a cargar PaddleOCR-VL-1.6 en un worker nuevo. Las seis lecturas son inferencias de página; no son seis documentos diferentes.

- Repositorio: `gatehot59-star/corpus-legal-tarija`.
- PR bajo prueba: https://github.com/gatehot59-star/corpus-legal-tarija/pull/33.
- Candidato exacto: `bb5578f798a5846fe1388c4e84dc2332ea537197`.
- Rama del registro: `titan/tester-ocr-pr33-repeats-20261023`, desde `b722bda135943a125152f0031accd15b2ab7b238`.
- Instrumento: `scripts/ocr/pr33_repeats_20261023.py`.
- Evidencia inicial: `docs/agents/evidencia/2026-10-23-05-pr33-repeticiones-checkpoint.json`.
- Unidad: `corpus-ocr-pr33-repeats-28egapd3.service`.
- Carpeta VM: `/home/ubuntu/ocr-pr33-repeats-20261023-28egapd3`.
- Invocation ID: `1e94d46b519c4c3b809bc018714eaff6`.
- Ruta del Doc: Space > PR33: tres repeticiones nuevas por página en curso (23-oct, 005).

Ejecutor: GPT-6 Astra, mediante brain-env y el SSH existente a la VM. El sandbox preparó y comprobó el instrumento; las inferencias corren en la VM. Lanzamiento único: 14:33:57 ART, systemd-run exit 0. Después se comprobó la ejecución real con procesos, admisión HTTP sobre socket Unix, progreso y log del modelo, no solo con el éxito del lanzamiento.

No se mergeó el PR, no se desplegó el parche ni se cambiaron Corpus, nginx, bases, pesos, runtime o workflows. No se abrió un puerto TCP ni se reinició un gateway. No se usa GPU paga.

## Sello y diseño

Instrumento ejecutado: 26086 bytes, SHA256 `47fb172602f5dc02db8d7130095a9c2b42a24e6fd3f366785c123c423b9d7648`. El archivo recuperado del commit inicial es idéntico byte por byte a la copia ejecutada en la VM.

Sello final: `238608b526d9d41ad0535982ff82a179a52776938ef3f1c7353ef8dc06d3f245`, fijado antes de inferir. Se conserva el sello previo, sustituido antes del lanzamiento para añadir la cesión de recursos a producción.

PDF: 61472 bytes, SHA256 `468c5115a7edf50febdf50a3a9fdb5b7189b789877e6210da6949c74e0e98eb6`.

Imágenes RGB de 5000 por 3750 píxeles, idénticas por hash al original:

- Página A: `6719dbb333a38ea5444efd252c4391cb8eb693211d4782bfe2133dca99ec8090`.
- Página B: `d733b4f16ba038a5aba7db38c85178b98a99f1532b61c47a5ab370954d8b86f2`.

Fuente candidata: `90df955df6edec61cc2c27876997848ba25c014d8dc5661fc2f1e91c6cf69a97`. Runtime conservado: PaddleOCR 3.7.0, PaddleX 3.7.2, PaddlePaddle 3.3.1 y Pillow 13.0.0, CPU y un hilo. No se alteraron `use_ocr_for_image_block:false` ni `CORPUS_OCR_LOW_MEMORY=0` para buscar un PASS. Modelos, revisiones, hashes, freeze y configuración completos están en el paquete inicial.

El estándar es [Estándar de reproducibilidad OCR v1.0](https://app.clickup.com/90171457413/docs/2kza6fw5-24177). Se compararán bytes UTF-8 exactos, sin strip ni normalización: seis pares por página, doce en total, incluyendo el original. El JSON crudo se comparará aparte, con sus rutas y metadatos intactos. Se conservan preparación, carga, calentamiento, extracción por página y tiempo continuo por separado. No se inventó un umbral de latencia.

El candidato solo recibe el PDF. El comparador abre las transcripciones originales al finalizar los tres workers. La preparación sí consultó el resultado original para fijar su referencia; no es una prueba ciega de exactitud.

## Límites que siguen abiertos

- Semilla RNG original no fijada ni registrada. Se preservó `explicit_seed:null`: reproducibilidad con semilla controlada **NO MEDIDA**.
- Freeze transitivo completo actual sellado; del original se acreditan pins principales, configuración y pesos, no una huella transitiva completa equivalente.
- Los tres trabajos nuevos comparten un arranque de VM. El original fue anterior al reinicio de las 13:53 ART: no es un diseño controlado entre reinicios.
- Repetibilidad, exactitud jurídica, generalización y superioridad frente a otro OCR son preguntas distintas.
- La comparación final, los contadores finales y la terminación de los tres workers siguen pendientes. No se interpreta `Result=success` de una unidad running como éxito terminal.
- Coverage, CI de este instrumento y review externo de la selección experimental no están acreditados. No se cambiaron workflows para esta corrida.

## Controles y protección de producción

El self-test final en VM devolvió exit 0: dos controles positivos y trece negativos detectados, más la comprobación de seis pares para cuatro muestras. Incluye mutaciones de carácter, espacio, LF/CRLF, Unicode y negación, muestras duplicadas o ausentes, página faltante, tiempo cero, imagen/fuente equivocadas, agregado contradictorio y falsa certificación. Son controles sintéticos, no lecturas OCR.

El instrumento exige trabajos y pares PID/start_ticks distintos, ejecución secuencial, cobertura y procedencia coherentes, tiempos positivos, worker exit 0, ausencia de timeout/señal y acuerdo entre resultados de worker y API. El comando local que solo prueba controles es `python3 scripts/ocr/pr33_repeats_20261023.py --self-test`.

La unidad tiene 6 GiB RAM, 3 GiB swap, CPUQuota 100%, Nice 10, red privada sin salida y solo su estado escribible. Runtime y producto quedan de solo lectura. Presupuesto: 2400 segundos por trabajo y 8100 para la unidad, sin retries automáticos. Si aparece OCR productivo queued/running, aborta solo el experimento; comprueba `state.json` cada cinco segundos.

A las 14:39, OCR, API y Django estaban activos con NRestarts 0. A las 14:41 no había trabajos productivos activos y el servicio montado conservaba su hash original `ba6319aed537f601745e9d54c1156ce5ee2dd3da500581a94347fc4b64ce5e0f`. Pico experimental observado entonces: RAM 6442450944 bytes, swap 3047464960 bytes, `oom=0`, `oom_kill=0`. Son contadores intermedios, no finales.

## Errores propios y alcance del archivo

El primer preflight consultó `status.json` en vez de `state.json`. Se corrigió antes de lanzar: doce trabajos históricos terminales, ninguno activo. Un primer preparador falló al parsear por escapes de salto de línea; no ejecutó inferencia. La primera captura de checkpoint no pudo leer el runner.log de systemd; se corrigió con lectura privilegiada, sin cambiar permisos ni procesos. La versión inicial del instrumento se reforzó antes de inferir; se archiva la versión final realmente ejecutada.

Los stderr y exits de los dos errores de ejecución están en el paquete inicial. Las fuentes completas de transporte y los sondeos de cinco segundos permanecen en las carpetas locales de evidencia; sus exclusiones están declaradas. No se incluyen PDF, PNG, pesos, binarios ni la configuración sensible de gateways del diagnóstico anterior.

## Publicación inicial verificada

El [commit inicial del lanzamiento](https://github.com/gatehot59-star/corpus-legal-tarija/commit/0c5478979f4392ed6ca29772fa7a7af935c881f2) conserva el recibo detallado con corte de 14:41, el instrumento y el paquete inicial. Este recibo lo actualiza con el avance de las 14:54 sin borrar aquel corte histórico.

Lectura de vuelta a las 14:54:52 ART:

- Instrumento: 26086 bytes, SHA256 `47fb172602f5dc02db8d7130095a9c2b42a24e6fd3f366785c123c423b9d7648`, idéntico al ejecutado.
- Paquete: 14578 bytes, SHA256 `d2b5bdebc88acfb3fdb44959cabb2b9df6cb432522805908df9e62192a3387f6`, idéntico al generado.
- Descomprimido: 51092 bytes, SHA256 `f38b274ce93ae9fde6cd4518f9614d14d5f0003d019719373a764a483d8354e3`. Los catorce archivos de texto internos pasaron su comprobación de bytes y SHA.

El paquete es JSON UTF-8 comprimido con XZ y codificado como `payload_xz_base64`. Conserva el comando completo, sello, controles, preparación, entorno, admisión, log del modelo, progreso, procesos y errores. Su corte sigue siendo 14:41; el avance posterior está a continuación, separado de las conclusiones.

## Evidencia estructurada del avance de 14:54

Lectura por SSH, exit 0. Estas son observaciones estructuradas del lector sobre los archivos y la unidad existentes, no texto generado por el modelo OCR ni un nuevo lanzamiento. Se conserva el stdout de systemd; los objetos JSON se presentan con formato legible, no como una comparación de bytes de esos archivos.

```json
{
  "captured_utc": "2026-10-23T17:54:56.636726+00:00",
  "checkpoint": {
    "utc": "2026-10-23T17:54:54.242695+00:00",
    "repeat": 2,
    "job": "e329585db5804defb472a66c25e92fad",
    "state": {
      "status": "running",
      "updated_utc": "2026-10-23T17:54:03.896850+00:00",
      "progress": {"phase": "loading", "expected_pages": 2, "completed_pages": 0}
    },
    "completed_repeats": 1,
    "new_pages_completed": 2
  },
  "first_repeat": {
    "job": "42fc461e59e74003ace6642aa4f476b8",
    "admission_status": 202,
    "submitted_utc": "2026-10-23T17:33:59.796818+00:00",
    "submitted_monotonic": 2443.890046043,
    "worker_pid": 11076,
    "worker_start_ticks": 244390,
    "state": {
      "status": "requires_review",
      "error": null,
      "worker_exit": 0,
      "timed_out": false,
      "signal": null,
      "job_wall_seconds": 1202.4058939380002,
      "updated_utc": "2026-10-23T17:54:02.213718+00:00",
      "progress": {
        "phase": "completed",
        "expected_pages": 2,
        "completed_pages": 2,
        "error": null,
        "updated_utc": "2026-10-23T17:54:02.206984+00:00"
      }
    },
    "finished_utc": "2026-10-23T17:54:03.844333+00:00",
    "finished_monotonic": 3647.937572288
  },
  "second_repeat": {
    "job": "e329585db5804defb472a66c25e92fad",
    "admission_status": 202,
    "submitted_utc": "2026-10-23T17:54:03.871111+00:00",
    "submitted_monotonic": 3647.964339687,
    "worker_pid": 16118,
    "worker_start_ticks": 364800,
    "worker_argv": [
      "/opt/corpus-ocr-vl/runtime/venv/bin/python",
      "/home/ubuntu/ocr-pr33-repeats-20261023-28egapd3/subject/ocr_service.py",
      "worker",
      "--job",
      "/home/ubuntu/ocr-pr33-repeats-20261023-28egapd3/state/run/jobs/e329585db5804defb472a66c25e92fad",
      "--runtime",
      "/opt/corpus-ocr-vl/runtime"
    ],
    "worker_cgroup": "0::/system.slice/corpus-ocr-pr33-repeats-28egapd3.service\n"
  },
  "verdict_observation": {
    "status": "running",
    "text_repeatability": "EN CURSO",
    "new_inferences_completed": 2,
    "seal_sha256": "238608b526d9d41ad0535982ff82a179a52776938ef3f1c7353ef8dc06d3f245",
    "instrument_sha256": "47fb172602f5dc02db8d7130095a9c2b42a24e6fd3f366785c123c423b9d7648"
  },
  "systemd": {
    "exit_code": 0,
    "stdout": "MainPID=11066\nResult=success\nExecMainCode=0\nExecMainStatus=0\nActiveState=active\nSubState=running\n",
    "stderr": ""
  }
}
```

## QA provisional y continuación

Rúbrica del checkpoint inicial: **37/45, 82,2/100**, no aprobatoria del cierre. Completitud 12/15 (seis lecturas y comparación pendientes en aquel corte); ejecutabilidad 12/15 (controles y worker real, sin recorrido terminal completo); documentación 9/10 (comandos, límites y errores, sin recibo final); proceso QA 4/5 (falsadores y evidencia, sin review externo). La primera vuelta terminada no convierte esa evaluación provisional en aprobación del experimento completo.

N/A: 55 puntos de Seguridad general de producto, Testing formal/coverage, Arquitectura de producto, DevOps e Innovación, por ser un instrumento diagnóstico. No se esconde la inferencia faltante bajo N/A. El aislamiento comprobado tampoco equivale a auditoría OWASP o transitiva.

Próxima consulta: **la misma unidad**, checkpoint.json, runs.json, verdict.json y comparison.json cuando exista. No relanzar, no modificar las condiciones en caliente y no contar un replay como nueva lectura. Al finalizar, verificar las seis inferencias, los doce pares textuales, JSON crudo, tiempos, exits y cierre de procesos. No hay notificación automática configurada.

## Método TITAN

Acción delicada: NO para esta publicación experimental propia, sin merge ni despliegue. Modo: TITAN FULL. Rúbrica provisional 37/45, 82,2/100. Review externo: sin hallazgos emitidos (deuda), no equivale a revisión aprobada. Los controles y dos lecturas nuevas están ejecutados; la repetibilidad sigue **EN CURSO**.
