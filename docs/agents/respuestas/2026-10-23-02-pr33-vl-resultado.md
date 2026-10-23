# PR33: PASS en la prueba sintética con VL real; sin despliegue

## Pedido y sujeto

Pedido: «Check the VM result now», 23-oct-2026 06:55 ART. Se inspeccionó la ejecución existente, sin relanzar inferencia ni editar el producto.

Sujeto exacto: [PR #33](https://github.com/gatehot59-star/corpus-legal-tarija/pull/33), revisión probada `bb5578f798a5846fe1388c4e84dc2332ea537197`, archivo de servicio SHA256 `90df955df6edec61cc2c27876997848ba25c014d8dc5661fc2f1e91c6cf69a97`. Unidad propia `corpus-ocr-pr33-smoke-w30qwx_f.service`. Instrumento ejecutado `run_vm.py`, SHA256 `154df42ab9a317201650adf00b04e4e93f93e92557432aeedc031c2a0a9cd31e`.

## Resultado medido

Captura final leída a las **06:56:06 ART**. El proceso terminó a las **06:50:36 ART**, exit 0, `SubState=exited`, `Result=success`. `ExecMainCode=1` significa CLD_EXITED, no exit code 1; el exit code está en `ExecMainStatus=0`. La unidad conserva ActiveState=active por RemainAfterExit, no porque siga corriendo.

**PASS acotado:** las dos páginas sintéticas terminaron con PaddleOCR-VL-1.6 real en CPU, worker exit 0, sin timeout, progreso final completed 2/2. Resultado `requires_review`, `fidelity_certified:false`.

La página mixta se derivó a VL y conservó su capa nativa por separado. La salida incluye exactamente `NO PAGAR Bs20.000.000`; la segunda página incluye `NO AUTORIZADO Bs30.000.000`. Al releer la salida se comprobó igualdad literal de ambos textos con los esperados del fixture, las ocho repeticiones de la cláusula nativa, agregados de texto/Markdown, bloques y hashes. Esta igualdad es del fixture artificial conocido, no una medición de fidelidad jurídica general.

Los dos controles negativos también dieron el rechazo esperado: txt sobre página mixta, `native_text_not_usable`, exit 1; cinco páginas, `page_limit`, exit 1. No son fallos inesperados del ensayo.

## Instrumento que puede fallar

El verificador fijado antes de la inferencia exige las páginas, las negaciones, fronteras de montos, motor, hash del código, capa nativa y estado final. Aceptó el resultado real. En la relectura rechazó nuevamente los cinco mutantes de negación, monto aumentado, página omitida, motor incorrecto y código distinto. No se cambió el instrumento, pipeline ni configuración para aprobar.

El resultado obtenido por la API se comparó con el resultado escrito por el worker: objetos completos idénticos. El replay del verificador no es una nueva inferencia ni una réplica independiente del modelo.

Afirmación → instrumento → podía dar rojo → veredicto:

- La prueba sintética con VL real pasó → salida completa, verificador sellado y mutantes → sí → PASS.
- Los procesos propios terminaron → estado estructurado de systemd y escaneo exacto de argv/cgroup en /proc → sí → PASS al momento de la captura.
- El parche tiene fidelidad jurídica general o está listo para producción → este único fixture no cubre eso → no → NO MEDIDO.

## Tiempos y recursos

Trabajo VL observado por supervisor: **1180.8406815780327 s, 19 min 41 s redondeados**. Ensayo completo con controles y cierre: 1196.4473076410359 s, 19 min 56 s. Son tiempos distintos.

Worker: 1175.5217180510517 s. Preparación: 1.8673325839918107 s; carga: 155.6252172869863 s; calentamiento: 57.794664020999335 s. Extracción página 1: 786.6884224090027 s; página 2: 168.90150418994017 s. No se definió umbral de latencia ni se hizo A/B pareado con el montaje anterior: no atribuir causalmente el tiempo a las correcciones.

Pico final de RAM retenido por systemd: 6442450944 bytes, 6 GiB. El pico de swap observado durante la corrida fue 3190124544 bytes, pero el pico final de swap y los contadores OOM finales son NO MEDIDOS porque el cgroup ya había desaparecido al capturar. No se presentan los contadores intermedios como finales.

## Cierre y continuidad de Corpus

A las 06:56:54 ART, el escaneo de /proc recorrió 100 procesos sin errores de acceso: cero coincidencias del candidato por argv exacto o cgroup; los tres PID anteriores ya no existían. El control positivo sí encontró el servidor OCR montado. No se confundió una herramienta ausente con cero procesos.

El servidor de prueba salió con -15 por SIGTERM del cierre planificado, después de terminar el worker. No representa un fallo de inferencia.

OCR montado, Corpus API y Django staging siguen activos y con NRestarts 0. Esto mide sus estados de servicio, no un nuevo recorrido web de usuario. Código montado SHA256 `ba6319aed537f601745e9d54c1156ce5ee2dd3da500581a94347fc4b64ce5e0f`, distinto del parche. No hubo merge, despliegue, sustitución, cambio de tareas ni mensajes en este turno.

## Evidencia y límites

[Doc de continuidad](https://app.clickup.com/90171457413/docs/2kza6fw5-24317), [página del registro](https://app.clickup.com/90171457413/docs/2kza6fw5-24317/2kza6fw5-27117). El checkpoint previo permanece inalterado en el commit `4532dbd6a9fff696afb66c5c68552e50d19132fd`.

Paquete final: `docs/agents/evidencia/2026-10-23-02-pr33-vl-resultado.json`, 19439 bytes, SHA256 `b73ce2e34eb96b1ce571e74bf419ef3ed07644a66ddf7a71b34e8b289ff2fa55`. JSON base64+XZ+UTF8-JSON: 138191 bytes descomprimidos, SHA256 `050acfaa3e92b5a8656ead0b10f2f9672b9e6045e6941da8bc932414c131165e`.

Incluye 39 registros de archivos, 32 de ellos con contenido textual completo, resultados, logs, polling JSONL, metadatos, programas de captura y escaneo, verificaciones y referencia al instrumento exacto ya publicado. Los siete binarios derivados se identifican por hash, sin commitearlos. Sin pesos, bases, entradas privadas ni configuración SSH. Cada texto fue verificado por longitud y hash antes de empaquetar; la lectura remota del commit se registra en el Doc después de publicarlo.

FAIL inesperado en este ensayo: ninguno observado. NO MEDIDO: calidad jurídica general, tres repeticiones nuevas por página, variedad documental, rendimiento pareado y revisión externa. Este PASS no cierra integralmente las cinco tareas ni aprueba merge/despliegue.

--- METODO PROMETEO ---
Accion: lectura de resultado y publicación documental; sin intervención productiva
Modo: LIGERO, sin puntuación global del parche
Maquinas: brain-env como transporte/custodia/replay; VM para lectura final y proceso; inferencia previa ya terminada
Instrumento: run_vm.py fijado, positivos y mutantes, salida real, systemd y /proc con positivo conocido
Veredicto: PASS sólo de integración sintética; fidelidad general y preparación productiva NO MEDIDAS
Review externo: no acreditado por esta comprobación; no se solicitó ni envió mensaje
Artefactos: docs/agents/respuestas/2026-10-23-02-pr33-vl-resultado.md + https://app.clickup.com/90171457413/docs/2kza6fw5-24317
