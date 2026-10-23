# PR33: tres repeticiones nuevas por página lanzadas, primera extracción en curso

Fecha: 2026-10-23. Zona del informe: ART, UTC-3. Corte de evidencia: 14:41:13 ART.

## Estado vivo

**EN CURSO.** La tanda fue lanzada a las 14:33:57 ART. A las 14:41, el primer trabajo estaba extrayendo la página 1 con el modelo real cargado. Había un trabajo admitido, dos todavía no admitidos y **0 de las 6 nuevas inferencias de página terminadas**. No existe todavía un veredicto de repetibilidad.

El pedido es tres lecturas nuevas de cada una de las dos páginas sintéticas del ensayo del PR #33. No es un replay del verificador. Se ejecutan tres trabajos nuevos del mismo PDF completo, en orden A,B / A,B / A,B, con un worker y una carga del modelo nuevos por trabajo. No se lanzó una segunda tanda durante la comprobación.

## Alcance y localización

- Repositorio: `gatehot59-star/corpus-legal-tarija`.
- PR bajo prueba: https://github.com/gatehot59-star/corpus-legal-tarija/pull/33.
- Candidato exacto: `bb5578f798a5846fe1388c4e84dc2332ea537197`.
- Base documental consultada: `b722bda135943a125152f0031accd15b2ab7b238`.
- Rama de este registro: `titan/tester-ocr-pr33-repeats-20261023`, creada desde esa base.
- Instrumento: `scripts/ocr/pr33_repeats_20261023.py`.
- Evidencia: `docs/agents/evidencia/2026-10-23-05-pr33-repeticiones-checkpoint.json`.
- Ruta del Doc: Space > PR33: tres repeticiones nuevas por página en curso (23-oct, 005).
- Ejecutor: GPT-6 Astra mediante el contenedor brain-env y SSH existente a la VM. Sandbox usado para preparar y comprobar el instrumento, no para inferir.

No se mergeó el PR, no se desplegó el parche y no se modificaron Corpus, nginx, bases, pesos ni runtime. No se abrió un puerto TCP, no se configuró una GPU paga y no se reinició ningún gateway.

## Evidencia del arranque real

Unidad: `corpus-ocr-pr33-repeats-28egapd3.service`.

Base en VM: `/home/ubuntu/ocr-pr33-repeats-20261023-28egapd3`.

Invocation ID: `1e94d46b519c4c3b809bc018714eaff6`.

El lanzamiento devolvió exit 0. Eso solo acredita admisión por systemd; la ejecución real se comprobó después con el estado de la unidad, los procesos, la admisión HTTP sobre socket Unix, el progreso y el log del modelo.

A las 14:39:38 ART se observaron el runner PID 11066, el servidor experimental PID 11072 y el worker PID 11076. El worker tenía `start_ticks=244390`, su argumento `--job` apuntaba al trabajo `42fc461e59e74003ace6642aa4f476b8` y su cgroup era el de esta unidad experimental. La admisión había devuelto HTTP 202 a las 14:33:59 ART. No se confunde ese proceso con el OCR productivo PID 739, observado como control positivo en su propio cgroup.

A las 14:41:11 ART, el checkpoint decía `repeat=1`, `phase=extraction`, `page=1`, `completed_pages=0`, `model_loaded=true`. El log conserva la carga de los pesos locales de PP-DocLayoutV3 y PaddleOCR-VL-1.6. `comparison.json` todavía no existía en la primera captura. El campo `Result=success` de una unidad aún running **no es el resultado final de la tanda**.

## Condiciones selladas antes de inferir

Instrumento final: 26086 bytes, SHA256 `47fb172602f5dc02db8d7130095a9c2b42a24e6fd3f366785c123c423b9d7648`.

Sello final: SHA256 `238608b526d9d41ad0535982ff82a179a52776938ef3f1c7353ef8dc06d3f245`, creado a las 14:33:57 ART antes del lanzamiento. Se conserva el sello anterior, sustituido antes de inferir para añadir la cesión de recursos a producción.

PDF: 61472 bytes, SHA256 `468c5115a7edf50febdf50a3a9fdb5b7189b789877e6210da6949c74e0e98eb6`.

Ambas imágenes son RGB de 5000 por 3750 píxeles. Sus hashes, iguales al ensayo original, son:

- Página A: `6719dbb333a38ea5444efd252c4391cb8eb693211d4782bfe2133dca99ec8090`.
- Página B: `d733b4f16ba038a5aba7db38c85178b98a99f1532b61c47a5ab370954d8b86f2`.

Fuente del servicio candidato: `90df955df6edec61cc2c27876997848ba25c014d8dc5661fc2f1e91c6cf69a97`. Se conservan PaddleOCR 3.7.0, PaddleX 3.7.2, PaddlePaddle 3.3.1, Pillow 13.0.0, CPU, un hilo y la configuración original. `use_ocr_for_image_block:false` y `CORPUS_OCR_LOW_MEMORY=0` no fueron alterados para buscar un PASS. Los hashes, revisiones de modelos, freeze y configuración completos están en el lanzamiento y el entorno archivados.

No se envían transcripciones previas al candidato. El comparador abre las salidas originales después de que terminen los tres workers. La preparación sí consultó metadatos y el resultado original para fijar la referencia; no se presenta eso como un ensayo ciego de exactitud.

## Qué medirá y qué no

El estándar es [Estándar de reproducibilidad OCR v1.0](https://app.clickup.com/90171457413/docs/2kza6fw5-24177). La implementación compara bytes UTF-8 exactos, sin strip, normalización Unicode ni correcciones. Para cada página compara las tres salidas nuevas entre sí y contra el original: seis pares por página, doce pares en total. El JSON crudo se compara aparte, sin quitar rutas ni metadatos; puede diferir aunque el texto coincida.

El instrumento exige IDs de trabajos y pares PID/start_ticks nuevos, ejecución secuencial, cobertura de dos páginas por trabajo, tiempos positivos, imágenes y procedencia iguales al sello, progreso terminal coherente, worker exit 0, ausencia de timeout/señal y acuerdo entre resultado del worker y de la API. Conservará preparación, carga, calentamiento, extracción por página y tiempo continuo por separado. No hay umbral temporal inventado después de medir.

**Límites declarados antes del lanzamiento:**

- El candidato original no fijaba ni registraba una semilla RNG. Se preservó ese comportamiento: `explicit_seed:null`. Reproducibilidad con semilla controlada: **NO MEDIDO**.
- Se selló el freeze completo actual; del original se acreditan pins principales, configuración y modelos, no una huella transitiva completa equivalente.
- Los tres trabajos nuevos pertenecen a un mismo arranque de la VM. El original fue anterior al reinicio de las 13:53 ART. No es un diseño controlado entre sesiones o reinicios.
- Repetibilidad no certifica exactitud jurídica, generalización, superioridad frente a Tesseract ni seguridad de producción.
- Coverage, CI de este instrumento y revisión externa de su selección experimental no están acreditados. No se cambiaron workflows para esta corrida.

## Controles del instrumento

El self-test final en VM devolvió exit 0. Registra dos controles positivos y trece negativos detectados: carácter, espacio final, LF/CRLF, Unicode, negación, ID duplicado, muestra faltante, página faltante, tiempo cero, imagen equivocada, texto agregado contradictorio, fuente equivocada y certificación falsa. Además verifica seis pares para cuatro muestras.

Esos controles son sintéticos. **No cuentan como inferencias OCR nuevas.** El instrumento puede dar rojo por una diferencia literal, una muestra ausente o una ejecución incompleta; todavía no puede respaldar un PASS de las seis lecturas porque no terminaron.

Comando local de controles, sin inferencia: `python3 scripts/ocr/pr33_repeats_20261023.py --self-test`.

El comando exacto de la corrida real está conservado en `launch.json` dentro de la evidencia. No se debe volver a ejecutar para consultar el estado.

## Recursos y protección del trabajo existente

La unidad tiene 6 GiB de RAM, 3 GiB de swap, CPUQuota 100%, Nice 10, red privada sin salida y solo el estado propio escribible. El runtime y el producto quedan de solo lectura. Tiene un presupuesto de 2400 segundos por trabajo y 8100 segundos para la unidad. No hay retries automáticos.

Si aparece un trabajo productivo queued/running, el instrumento aborta solo su tanda experimental. Consulta los `state.json` reales cada cinco segundos. No modifica ni cancela los trabajos productivos.

A las 14:39, OCR, API y Django estaban activos, con NRestarts 0. A las 14:41 no había trabajos OCR productivos queued/running y el hash del servicio productivo seguía siendo `ba6319aed537f601745e9d54c1156ce5ee2dd3da500581a94347fc4b64ce5e0f`.

En ese checkpoint, la unidad experimental había alcanzado un pico de RAM de 6442450944 bytes y un pico de swap de 3047464960 bytes. `memory.events` tenía `oom=0` y `oom_kill=0`. Son mediciones **intermedias**, no contadores finales ni una promesa de ausencia futura de OOM.

## Errores propios conservados

1. El primer preflight buscó trabajos por `status.json`, pero el producto usa `state.json`. Esa lista vacía no se tomó como prueba válida: se corrigió antes del lanzamiento y se encontraron doce trabajos históricos terminales, ninguno activo.
2. Un primer envío del preparador tuvo SyntaxError por escapes de salto de línea. Falló al parsear, antes de ejecutar el código remoto; no se lanzó inferencia. Se corrigió y se compiló el preparador antes del envío válido.
3. La primera lectura de checkpoint falló por PermissionError sobre el `runner.log` creado por systemd. Se repitió solo la lectura con privilegio existente; no se cambiaron permisos, procesos ni configuración.
4. La versión inicial del instrumento fue reforzada antes de inferir. El archivo que corre y el que se entrega tienen el hash final indicado; la versión inicial no se presenta como la ejecutada.

Los stderr y exit codes de los dos errores de ejecución se conservan literalmente en el paquete publicado. Las fuentes completas de transporte y la telemetría de cinco segundos continúan en las carpetas de evidencia de brain-env y la VM; su publicación completa queda fuera de este checkpoint. Las exclusiones y sus hashes están declarados, no ocultos.

## Evidencia y lectura independiente

El archivo de evidencia contiene un JSON UTF-8 comprimido con XZ y codificado en base64. Tras decodificar `payload_xz_base64` y descomprimir, se deben verificar 51092 bytes y SHA256 `f38b274ce93ae9fde6cd4518f9614d14d5f0003d019719373a764a483d8354e3`.

Incluye catorce archivos de texto de la VM con bytes y hashes, el comando completo de lanzamiento, sello, controles, preparación, entorno, admisión, worker log, progreso y veredicto aún running; además incluye las salidas de systemd, cgroup, procesos, servicios, estados productivos y errores propios. El instrumento se entrega aparte, byte por byte igual al observado en la VM. No se commitean PDF, PNG, pesos ni binarios. Tampoco se incluye la configuración sensible del diagnóstico anterior de gateways.

Para contradecir este checkpoint basta comprobar que el job/worker no corresponde al candidato sellado, que el modelo no llegó a cargar o que el checkpoint no estaba en extracción. Los doce pares textuales y el resultado final permanecen pendientes y no forman parte de esta afirmación.

## QA provisional y cierre pendiente

Tipo de entrega: instrumento diagnóstico y checkpoint, no producto desplegable. TITAN FULL. Roles aplicados: Tester, comprobación de aislamiento y evidencias, documentación y QA. No se invoca una revisión externa inexistente.

Rúbrica provisional: **37/45, 82,2/100**. No aprueba todavía el cierre de la medición.

- Completitud 12/15: instrumento y sello completos, pero las seis lecturas y la comparación final siguen pendientes. Evidencia: `state/run/checkpoint.json` y `verdict.json`.
- Ejecutabilidad 12/15: self-test exit 0 y primer worker real en extracción; el recorrido terminal de los tres trabajos no fue observado aún. Evidencia: `launch.json`, procesos y worker log.
- Documentación 9/10: comandos, entradas, límites, errores y lectura independiente documentados; falta el recibo final.
- Proceso QA 4/5: controles que pueden fallar y evidencia cruda preservada; selección experimental sin review externo y cierre aún no medido.

N/A: 55 puntos correspondientes a Seguridad general de producto (15), Testing formal/coverage (15), Arquitectura de producto (10), DevOps (10) e Innovación (5). No se usa N/A para esconder resultados de inferencia: esos están expresamente pendientes. El chequeo de aislamiento realizado no equivale a una auditoría OWASP o de dependencias transitivas.

Próxima lectura: consultar **la misma unidad**, `state/run/checkpoint.json`, `runs.json`, `verdict.json` y, cuando exista, `comparison.json`. No relanzar ni cambiar el instrumento en caliente. Si termina o falla, conservar resultados, estados y procesos antes de decidir cualquier nueva ejecución. No hay notificación automática configurada.

## Método TITAN

Acción delicada: NO para esta publicación experimental, sin merge ni despliegue. Modo aplicado: TITAN FULL. Rúbrica provisional 37/45, 82,2/100, no aprobatoria del resultado final. Review externo: sin hallazgos emitidos (deuda), no equivale a revisión aprobada. El instrumento y sus controles están ejecutados; el veredicto de repetibilidad sigue **EN CURSO**.
