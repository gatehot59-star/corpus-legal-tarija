# PR33: seis lecturas nuevas completas y texto repetible

Fecha del recibo: 2026-10-23, ART (UTC-3). Pedido: comprobar el estado de la tanda, sin volver a ejecutar OCR.

## Veredicto acotado

- PASS de ejecución: tres trabajos nuevos, seis inferencias de página, tres workers distintos, todos con exit 0, sin timeout ni señal.
- PASS de repetibilidad textual: 12/12 pares de bytes UTF-8 idénticos, sin normalizar, recortar ni agregar un salto final. Son cuatro muestras por página (original más tres nuevas), seis pares por página.
- FAIL de igualdad literal del JSON crudo: 12/12 pares distintos. La comparación estructural directa encontró una única ruta diferente en todos los pares: `/res/input_path`, el archivo temporal de cada trabajo. No se quitó esa clave para convertir el FAIL en PASS.
- NO MEDIDO por este ensayo: exactitud jurídica general, generalización documental, determinismo con semilla controlada, reproducibilidad controlada entre sesiones y mejora de rendimiento frente al servicio anterior.
- Sin merge, despliegue, cambio del OCR productivo ni nueva inferencia durante esta consulta.

La tanda terminó el 23-oct a las 15:33:42 ART. Se verificó el estado a las 22:12:31 ART y se recompararon las capturas a las 22:13:37 ART. El tiempo continuo fue 3584.937319534 s, aproximadamente 59 min 45 s.

## Qué se ejecutó

Tres trabajos secuenciales del mismo PDF sintético de dos páginas, orden A,B / A,B / A,B. Un worker, carga del modelo y calentamiento nuevos por trabajo. Las salidas originales se abrieron después, solo en el comparador; nunca se enviaron al OCR.

El candidato corresponde al head `bb5578f798a5846fe1388c4e84dc2332ea537197` del [PR #33](https://github.com/gatehot59-star/corpus-legal-tarija/pull/33). El instrumento publicado está en `scripts/ocr/pr33_repeats_20261023.py`, commit `0c5478979f4392ed6ca29772fa7a7af935c881f2`. El checkpoint posterior está en el commit `95212267f5e67d1bae07f2ea5bab520b3fc9a85b` y en el [Doc histórico de lanzamiento](https://app.clickup.com/90171457413/docs/2kza6fw5-24377). Este recibo reemplaza EN CURSO como estado actual, sin borrar ese corte histórico.

Inicio del runner: `2026-10-23T17:33:57.345639+00:00` (14:33:57 ART).
Fin del runner: `2026-10-23T18:33:42.282943+00:00` (15:33:42 ART).
Unidad: `corpus-ocr-pr33-repeats-28egapd3.service`.
Carpeta VM: `/home/ubuntu/ocr-pr33-repeats-20261023-28egapd3`.

### Trabajos y tiempos

Todos los tiempos siguientes están en segundos. La extracción se informa por página, separada de preparación, carga y calentamiento; no son tiempos de inferencia pura de tokens.

- R1, job `42fc461e59e74003ace6642aa4f476b8`, PID 11076, start_ticks 244390: admitido 14:33:59.796818 ART, terminal 14:54:02.213718 ART. Preparación 1.727474419; carga 149.530797844; calentamiento 54.444095980; página A 818.699652747; página B 167.478801039; worker 1197.044611025; trabajo 1202.405893938.
- R2, job `e329585db5804defb472a66c25e92fad`, PID 16118, start_ticks 364800: admitido 14:54:03.871111 ART, terminal 15:13:42.290856 ART. Preparación 1.728645617; carga 142.886032632; calentamiento 53.685617588; página A 800.992650605; página B 167.479618997; worker 1172.204429952; trabajo 1178.391449134.
- R3, job `94f55de93e484ee0905239c0ea7413ac`, PID 21041, start_ticks 482690: admitido 15:13:42.782439 ART, terminal 15:33:37.746591 ART. Preparación 1.830010063; carga 142.218016064; calentamiento 54.516463906; página A 815.335212750; página B 169.323972614; worker 1188.836422715; trabajo 1194.936592443.

Los tres conservan `requires_review`, `fidelity_certified:false`, progreso 2/2 completed, error null, worker_exit 0, timed_out false y signal null. Los resultados completos de API y worker coinciden. No hubo superposición de trabajos. Los 717 sondeos (241, 236 y 240) registran carga, extracción A, extracción B y finalización; no son inferencias adicionales.

Estadísticas descriptivas de las tres lecturas nuevas:

- Página A: media 811.675838701; mediana 815.335212750; mínimo 800.992650605; máximo 818.699652747; desvío muestral 9.403602769. Original: 786.688422409.
- Página B: media 168.094130883; mediana 167.479618997; mínimo 167.478801039; máximo 169.323972614; desvío muestral 1.065074260. Original: 168.901504190.

No hubo umbral temporal preregistrado ni comparación pareada contra el producto anterior. No se emite PASS de rendimiento.

## Instrumento y falsadores

El veredicto no se acepta solo porque el runner diga PASS. `verify_captured_repeats.py`, ejecutado en brain-env con exit 0, relee las capturas y no importa validadores del candidato ni del runner. Compara bytes directamente, recorre diferencias JSON, verifica sellos y recomputa tiempos y estadísticas.

Pasaron 57 comprobaciones de integridad y coherencia. No son 57 inferencias ni una auditoría externa: es otro instrumento del mismo operador. Su fuente ejecutada y salida completa están dentro del paquete de evidencia. SHA256 de la fuente: `77cc7bd08e73aace0fae1bd9c2f7ee5bab137f11e04c80fb901017cbf8ad022d`.

Controles de este comparador: un positivo y cinco negativos (carácter, espacio, LF/CRLF, Unicode y negación). El instrumento de lanzamiento ya tenía dos positivos, trece negativos y control de conteo de pares. Ninguno se cuenta como OCR nuevo.

Afirmación / instrumento / posibilidad de dar rojo / veredicto:

- Texto idéntico: bytes de ocho textos reales y controles mutados / sí / PASS, 12 pares.
- JSON idéntico: bytes crudos y recorrido estructural / sí / FAIL literal; solo cambia `/res/input_path`.
- Seis lecturas nuevas terminadas: tres jobs, PIDs y start_ticks distintos, logs y estados terminales, tiempos, entradas selladas y resultados / sí / PASS acotado a esta tanda.
- Sin procesos experimentales residuales: recorrido de `/proc` con control positivo del servicio productivo / sí / PASS al corte de las 22:12.
- Exactitud jurídica general: este banco sintético y su repetición / no / NO MEDIDO.
- Producto web disponible a las 22:12: no se hizo HTTP público en esta consulta / no / NO MEDIDO; no se reutiliza el 200 de las 13:54 como medición nueva.

## Cierre de procesos y recursos

Systemd: MainPID 0, Result success, ExecMainStatus 0, ExecMainCode 1 (CLD_EXITED, no exit 1). ActiveState active y SubState exited se deben a RemainAfterExit; no significan que el OCR siga corriendo. El servidor experimental terminó con SIGTERM previsto, exit -15; remaining_workers está vacío.

El scan posterior recorrió 101 procesos sin errores de lectura, encontró el OCR productivo como control positivo y ningún proceso experimental. OCR, API y Django estaban active/running con NRestarts 0 y ExecMainStatus 0.

Antes del teardown: RAM pico 6442450944 bytes (6 GiB), swap pico 3216707584 bytes, muy cerca del límite de 3 GiB. `memory.events`: max 234349, oom 0, oom_kill 0, oom_group_kill 0. Son contadores capturados antes de desaparecer el cgroup, no una lectura final de un cgroup aún vivo. La CPU consumida registrada por systemd fue 2977771320000 ns.

La tanda terminó sin OOM registrado, pero agotó el margen de RAM y casi todo el de swap. Esto no valida capacidad, concurrencia ni operación sostenida del producto.

El servicio productivo conserva SHA256 `ba6319aed537f601745e9d54c1156ce5ee2dd3da500581a94347fc4b64ce5e0f`. No se modificaron sus archivos, unidad, nginx, bases ni configuración.

## Sellos principales y límites

- PDF: 61472 bytes, SHA256 `468c5115a7edf50febdf50a3a9fdb5b7189b789877e6210da6949c74e0e98eb6`.
- Imágenes de cada trabajo: 5000 x 3750, RGB, iguales a las originales. Página A SHA256 `6719dbb333a38ea5444efd252c4391cb8eb693211d4782bfe2133dca99ec8090`; B `d733b4f16ba038a5aba7db38c85178b98a99f1532b61c47a5ab370954d8b86f2`.
- Texto A: 394 bytes, SHA256 `13e8f37954418d7049c68074ed5440b36e3c5f94256fd746a053395c228fb425`.
- Texto B: 41 bytes, SHA256 `cee48538e8ed9165d0ba7b54752c08a240653e1acc737b34785becda10b1318c`.
- Instrumento: 26086 bytes, SHA256 `47fb172602f5dc02db8d7130095a9c2b42a24e6fd3f366785c123c423b9d7648`.
- Sello final previo a inferir: SHA256 `238608b526d9d41ad0535982ff82a179a52776938ef3f1c7353ef8dc06d3f245`.
- Candidato: SHA256 `90df955df6edec61cc2c27876997848ba25c014d8dc5661fc2f1e91c6cf69a97`.

Se verificaron pesos, revisiones, configuración y runtime actual. PaddleOCR 3.7.0, PaddleX 3.7.2, PaddlePaddle 3.3.1, Pillow 13.0.0, CPU de un hilo, batch 1, MKLDNN false. `use_ocr_for_image_block:false` permanece sin cambio.

`explicit_seed:null`: el original no fijaba ni registraba semilla, y no se alteró el candidato para este ensayo. Del original se acreditan los pins principales, pesos y configuración, pero falta una huella transitiva completa equivalente al freeze de esta tanda. Tres workers corrieron dentro de un boot; el original fue anterior al reinicio de la VM. No se presenta esto como diseño controlado entre sesiones. CI, cobertura medida y review externo de este instrumento no están acreditados por esta consulta. No se consultó nuevamente Copilot.

## Evidencia conservada

Paquete: `docs/agents/evidencia/2026-10-23-06-pr33-repeticiones-resultado.json`.

- Esquema `corpus-evidence-xz-base64/1`, solo texto comprimido, sin PDF, PNG, pesos ni otros binarios derivados.
- 24589 bytes; SHA256 `c1b789966b43624f11a2b459e86475c99eb672f8615dbad0e1803c7d3c5d223f`.
- 51 archivos de texto completos; contenido JSON descomprimido 203284 bytes; SHA256 `a444e14fab5ef660d2e228d7ecaaa489fc9efdec98719e7d2a6ee833fe849fd2`.
- Incluye transcripciones, resultados, JSON crudos, estados, logs, entorno, sellos, comparación, verificador ejecutado y su salida, procesos y servicios.
- Los historiales completos de sondeo y archivos ya publicados se excluyen con hashes y tamaños. Los 717 sondeos siguen en VM y en la captura local completa. Inputs binarios solo por manifiesto de hashes.
- Directorio local de esta entrega: `/workspace/corpus-ocr-pr33-repeats-status-20261023-2211`.

## Método de esta entrega documental

Acción delicada: NO. TITAN LIGERO para lectura de estado y publicación de evidencia en la rama existente, sin alterar producto ni instrumento. Rúbrica N/A para esta entrega documental; no se recicla el score provisional del lanzamiento como aprobación final. Review externo: sin hallazgos emitidos (deuda), no aprobación. Compilador: ninguno; se ejecutó Python con exit 0. Esta entrega no autoriza merge ni despliegue.
