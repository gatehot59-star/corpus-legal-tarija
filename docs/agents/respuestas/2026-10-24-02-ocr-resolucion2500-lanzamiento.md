# Prueba de resolución: 5000 a 2500 píxeles, mismo corte de dos horas

## Estado y alcance

Pedido24-oct02:43 ART: medir si bajar la resolución evita el timeout. Se inició un único trabajo nuevo a las02:46:56 ART. Captura02:48:31 ART: worker real PID164885, start_ticks4642058; estado running, fase loading,0/4 páginas terminadas. Resultado final sobre evitar timeout: EN CURSO. Calidad del texto: NO MEDIDO.

No se relanzó la tanda125. Esta prueba usa sólo las mismas páginas1 a4 del primer trabajo que falló: Resoluciones161 a200,2013/2014. El PDF del trabajo es idéntico byte a byte,354295bytes,SHA2566d243b8fba9b238e421280c343cd6336228de8e2a9795f68c09d0a97d47b7cd0. Fuente original SHA2566b9dcffaffdfb997dc4227dea2d89d0a01b4474d6c00abfa4bb4152ca4750784.

## Variable modificada y controles

Único cambio de código en la copia experimental del candidato PR33: argumento Poppler scale-to5000 pasa a2500. El argumento -r300 permanece igual; por eso no se presenta como una medición de DPI150. Se miden dimensiones reales:1621x2500,1616x2500,1618x2500 y1616x2500. Corresponden aproximadamente a un cuarto de los píxeles anteriores. No implica por sí solo un cuarto del tiempo.

Las cuatro imágenes que preparó el worker vivo se leyeron antes de inferir y sus hashes coincidieron4/4 con los renders sellados. Los renders del PDF original y del subconjunto también coincidieron4/4. Los hashes altos y bajos son diferentes; no son dos brazos con la misma entrada.

Sin cambios: cuatro páginas por trabajo, JOB_TIMEOUT7200s, CPUQuota100%, un hilo, memoria6GiB, swap3GiB, Nice10, modelo, pesos, paquetes, layout, configuración del pipeline,4096 tokens máximos por página y warmup128. Modo ocr forzado. Semilla no fijada, como en el control histórico.

Se mantienen aislamiento por systemd, red bloqueada durante OCR, AF_UNIX, capacidades vacías, usuario ubuntu y escritura sólo en el estado experimental. Ante demanda OCR productiva se aborta únicamente esta prueba. Sin GPU paga, retries automáticos, merge, despliegue ni cambios al OCR actual de Corpus.

## Qué cuenta como resultado

PASS para este trabajo: cuatro páginas no blancas, salida real y JSON crudo de todas, hashes de imágenes correctos, exit0, sin timeout/señal y tiempo de trabajo menor que7200s. No alcanza con procesar dos páginas, devolver texto vacío o ampliar el reloj.

FAIL_TIMEOUT: el supervisor vuelve a agotar7200s. Si hay otro error o interrupción, el efecto sobre timeout queda NO MEDIDO con el motivo guardado. El observador tiene7260s para recoger el estado y la unidad7800s de resguardo; ninguno amplía el deadline7200s del worker ni el criterio de éxito.

Referencia histórica: mismo PDF a5000px terminó con timeout a7200,811s, dos salidas parciales; página1 tardó2934,824s y página2,3457,900s. Es un diagnóstico de una corrida nueva contra una histórica, no A/B contemporáneo aleatorizado ni prueba de repetibilidad. No permite reclamar un efecto causal general o cero errores. El cotejo visual de calidad sigue pendiente.

## Instrumentos y evidencia

Archivos scripts/ocr/resolution_probe_20261024.py y resolution_prepare_20261024.py. Se ejecutaron y se leyeron de vuelta desde el commit ea6696521b44ea400fb5eae9b3d76427b6292cb8, idénticos byte a byte. SHA256 del ejecutor1727b3b3e26a5ab27d18df5c67d1b003f1ce8fbd790e75e6ba589765399dc421; preparador4d3cb1a14545767ef919b38daea285e2476f6d20c04d0c921f274f3c187ee02d. Helper anterior sellado a2ee42bcc8df2fa1afa2bce1b0c6cd1180fcaa1238627a20662ab95aa38a7c53.

Self-test: un positivo y ocho mutantes rechazados (timeout, tiempo excedido, página faltante, imagen incorrecta, certificación falsa, bypass nativo, discrepancia de crudo y crudo faltante). Exit0 local y en VM; no son inferencias. Render real y nueve comandos de preparación/chequeo/lanzamiento exit0. Verificación del runtime y freeze sin cambios. No hay certificación global ni cobertura formal declarada.

La evidencia adjunta docs/agents/evidencia/2026-10-24-02-res2500-evidence.json contiene el JSON íntegro seleccionado de preparación, comandos exactos con stdout/stderr, sello, checkpoint y procesos, hashes de imágenes reales del worker y consulta systemd. Está codificado como XZ/base64 para evitar duplicación extensa de texto; no contiene PDFs, PNGs ni pesos. Al decodificar:28622bytes,SHA2562a7e62598e18573608d7216b56c87847b0e10c1e72e97a5719719d3bd3a376bf. Las capturas tienen contenido textual verbatim y hashes propios para recomputar las afirmaciones.

Máquinas: brain-env como acceso y pruebas ligeras; VM como instrumento OCR. Sandbox sin uso para inferir. PR33 leído en vivo, sigue abierto con head bb5578f798a5846fe1388c4e84dc2332ea537197. Producto OCR hash ba6319aed537f601745e9d54c1156ce5ee2dd3da500581a94347fc4b64ce5e0f intacto. API/Django/OCR productivo activos con PIDs726/727/739, NRestarts0 en captura02:48 ART.

## Continuación verificable

VM: /home/ubuntu/ocr-res2500-20261024-qadg81o2. Unidad corpus-ocr-res2500-qadg81o2.service. Job88f65c3a787a45c0bda63cdcf5df23f0. Estado actual en state/run/measurement.json y checkpoint.json; resultado y archivos se preservarán allí. Sello22ea2f8f88f099eac2eeb0eabe0718dd90832191917d5bfabbde8f29fa50a2dd. Copia experimental del servicio SHA256c3e7bce637f948d05936acb402647f86da1fccd5d6093cc98086980260263c83; no es el código productivo.

brain-env: /workspace/corpus-ocr-resolution-20261024; live-capture.json y collect_live.py permiten retomar lectura sin relanzar. Fecha esperable del corte, si agota el plazo: alrededor de04:46:56 ART del24-oct; no es una estimación de finalización ni una promesa de aviso automático.

Modo TITAN LIGERO, diagnóstico acotado. Instrumento propio con evidencia cruda, no auditor externo. No se modifican CI, tareas, reportes ni credenciales.
