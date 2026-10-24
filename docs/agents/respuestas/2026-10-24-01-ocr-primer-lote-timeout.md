# Primer trabajo OCR: falló por timeout, dos páginas parciales conservadas

Consulta del 24-oct-2026 a las 02:37 ART sobre el lote autorizado de cuatro PDF/125 páginas. Es una verificación de estado, no un relanzamiento ni un cotejo de exactitud.

## Respuesta

No hay primer trabajo completo. El trabajo1 de32, páginas1 a4 del compilado Resoluciones161 a200,2013/2014, llegó al timeout real de7200s. El supervisor terminó el worker el24-oct a la01:22:44 ART; el ejecutor finalizó01:22:47 ART con stopped_incomplete y exit1. Había iniciado23-oct23:22:40 ART.

- Página1: salida parcial guardada,2934,823720114s de extracción (48m55s),2969bytes UTF-8,19bloques.
- Página2: salida parcial guardada,3457,8997809939974s (57m38s),3424bytes UTF-8,19bloques.
- Página3: extracción observada a la01:12:56 ART, interrumpida por timeout, sin raw final guardado.
- Página4: no se observó inicio y no hay salida guardada.
- Trabajos2 a32: no admitidos. No quedan procesos del experimento.

Son dos salidas nuevas parciales, no dos páginas aprobadas ni un documento completo. El contador global completed_pages/vl_inferences quedó0 porque sólo se incrementa después de validar un job entero; partial.json y dos raw prueban que sí hubo extracción parcial. No afirmar cero inferencias a partir de ese contador.

## Causa medida y límites

state.json: failed, error timeout, timed_out true, worker_exit -9, signal9, job_wall_seconds7200,8110510339975. El SIGKILL fue el mecanismo de timeout; no basta por sí solo para llamarlo OOM. En los eventos del cgroup: oom0, oom_kill0, oom_group_kill0. Pico memoria6442450944bytes (6GiB, el límite), swap2999431168bytes (aprox.2,79GiB). Hubo presión de memoria, pero no se aisló su contribución causal a la latencia.

Conclusión acotada: este trabajo de cuatro páginas no entró en el presupuesto de dos horas con esta configuración de CPU. No extrapolar un ETA para125 páginas ni convertir la parada en un veredicto sobre la calidad de todo PaddleOCR-VL.

## Integridad de los parciales: PASS, no fidelidad

Lectura de los archivos reales y comparación directa entre jobs y archive/batch-01:8/8 archivos idénticos byte a byte, incluido el input. Source SHA256 y subset SHA256 siguen coincidiendo con el manifiesto. Las imágenes de páginas1 y2 coinciden con las imágenes originales previamente selladas.

Un verificador separado, sin importar el validador del candidato ni del ejecutor, contrastó bytes/hash de cada captura, páginas1/2, método VL forzado, textos agregados, bloques del JSON crudo, tiempos positivos, procedencia, estado timeout y copia archivada. Exit0. Cinco mutantes fueron rechazados: falta una página, texto crudo alterado, timeout false, archivo cambiado y certificación de fidelidad falsa. Mismo operador; no auditor externo.

Instrumento: scripts/ocr/verify_reported125_first_batch_20261024.py, SHA256098364ec149c58be69d2ef1a6d94e23724a85e58d548d101fceca6c387898acd. Ejecución real en brain-env: python3 verify_first_batch.py first-batch-evidence.json, exit0. La captura de entrada completa está en /workspace/corpus-ocr-reported125-check-20261024-0236/first-batch-evidence.json,140649bytes,SHA25656c06ae7b70e17268b0f5e4ac526e308883148db0887f25895fe545f7e590645. Incluye parcial y raw completos. El JSON publicado junto a este recibo contiene estados, métricas y hashes, no la captura completa; se declara esa limitación explícitamente.

Los textos siguen requires_review y fidelity_certified false. No se hizo cotejo visual contra el PDF, no se calculó CER/WER ni se obtuvo gold humano. No se afirma superioridad contra el texto actual de Corpus. Las cadenas extrañas del OCR necesitan cotejo, no corrección por intuición.

## Estado de Corpus

Consulta viva02:37 ART: API PID726, Django PID727 y OCR productivo PID739 activos/running, NRestarts0. Hash del código OCR productivo ba6319aed537f601745e9d54c1156ce5ee2dd3da500581a94347fc4b64ce5e0f, igual al previo. Sin procesos experimentales residuales; scan de procesos sin errores. Esto acredita continuidad de esos servicios y del código observado, no una auditoría funcional completa.

No se reinició la tanda, no se cambiaron límites ni scripts ejecutados, no se reemplazó texto ni se reindexó Corpus. No merge, deploy, GPU paga, cierres de reportes ni modificación de tareas. Sólo lectura y publicación de este estado.

## Gate de afirmaciones

- El primer trabajo terminó completo -> estado terminal y partial.json podían contradecirlo -> FAIL.
- El motivo registrado es timeout -> timed_out, supervisor y7200s podían contradecirlo -> PASS.
- Dos salidas están preservadas e internamente consistentes -> bytes, hashes y raw podían contradecirlo, cinco mutantes rechazados -> PASS.
- El texto es una copia fiel del PDF -> no hubo instrumento visual en esta consulta -> NO MEDIDO.
- Los servicios productivos siguen activos -> systemctl estructurado y PIDs podían contradecirlo -> PASS acotado.

No se otorgó score global ni aprobación de producción. Para continuar habrá que decidir una estrategia distinta; este chequeo no autoriza relanzar o alterar el presupuesto sellado.
