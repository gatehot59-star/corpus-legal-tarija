# Tres repeticiones de cada página atípica: EN CURSO

16-oct-2026, lanzamiento 15:01 ART. Pedido: repetir las dos páginas extremas para probar reproducibilidad. Se interpreta como las dos más lentas señaladas en el informe previo, no como mínimo y máximo.

A = p037: primera página del PDF Resoluciones 216 a 250 de 2012/2013, 155.28575577499987 s en el lote original. PNG SHA256 6c7da29c3fc8057035eab6c2c4e5f3b0e8a5fe1727e3c79e95a06853e2512685.

B = p092: Ley 151/2016 página 2, 168.66275608699925 s originales. PNG SHA256 88d9fdddf68205f68d69ab1324bfd00dd406e7ac07b42abf91894950432ba539.

## Diseño sellado antes de ejecutar

Seis inferencias: A,B,B,A,A,B, tres por página, una única carga del modelo y el mismo calentamiento sintético. IDs de ensayo: p037-r1, p092-r2, p092-r3, p037-r4, p037-r5, p092-r6. El sufijo indica posición global, no repetición dentro de página.

Reutiliza el dataset privado de cien imágenes y verifica su manifiesto y los cien hashes; sólo llama predict para las dos páginas seleccionadas. Imágenes originales a 300 dpi, sin máscaras ni reducción. Mismo PaddleOCR-VL-1.6, pesos fijados por revisión y SHA256, Paddle GPU 3.3.1, PaddleOCR 3.7.0, PaddleX 3.7.2, semilla 20261015, batch 1, gpu:0, un hilo CPU, MKLDNN desactivado, 4096 tokens máximos por bloque, sin colas, sin OCR de bloques image. Se conserva el código de inferencia y su temporización sincronizada CUDA. Timeout 1800 s por página. No se agregó instrumentación por bloque que pudiera alterar la comparación.

La nueva sesión tiene T4 solicitada e imagen Docker idéntica recuperada desde Kaggle. El uso real de GPU se comprueba dentro de la ejecución; RUNNING no certifica carga ni inferencias completadas. Las dependencias transitivas se resuelven como en la corrida original y se registran: comparar el seal y pip-freeze al cerrar, no afirmar identidad completa de paquetes antes de leerlos.

Comparar al cierre cada tiempo, mediana, rango, dispersión y razón contra el original; además comparar el texto exacto entre repeticiones y con la salida original. No fijar después un umbral conveniente para declarar reproducibilidad. Por ahora NO MEDIDO.

Limitación: tres repeticiones en una sesión nueva, no tres sesiones independientes. No se reproduce la historia de 36/91 páginas anteriores del lote original. Las páginas se eligieron por ser extremas: cambios pueden reflejar regresión a la media. No es exactitud OCR ni prueba causal del origen de la demora.

## Ejecución observada

Adaptador: cinco fixtures, exit 0. Push: versión 1 aceptada, exit 0, 18:01:13.671834 UTC. Kaggle generó el slug desde el título y no usó el ID solicitado. La primera consulta al ID solicitado falló; se consultó el enlace devuelto y dio RUNNING. Se terminó únicamente el observador local que consultaba el enlace incorrecto y se inició otro con el enlace real. No se canceló la GPU, no hubo segundo push.

Pull del código y metadatos: exit 0. SHA256 idéntico al kernel local: a872889090e75e77ecfddfed610fe5d54dbc9d3375d2b21be81d360cc80668b3. Notebook privado, dataset correcto, NvidiaTeslaT4. El observador recoge outputs al estado terminal y los marca DOWNLOADED_NOT_VERIFIED; no emite veredicto ni avisos de chat.

[Corrida privada](https://www.kaggle.com/code/abrahammendieta/corpus-vl16-repeat-two-outliers-20261016).

Directorio de trabajo brain-env: /workspace/paddle-vl16-repeat2-20261016. Fuente original: /workspace/paddle-vl16-100-20261016/run100.py. Nuevo runner run-repeat.py; kernel/kernel.py; observador watch-actual.py; recibos preflight.json, push-receipt.json, slug-correction.json y pull-readback.json. Outputs finales esperados en output-v1/corpus-vl16-results. El código completo está en Kaggle y brain-env; este commit registra el protocolo y recibo, no afirma que los scripts ya hayan completado inferencia.

Sin cambios al producto, main, PR, despliegue, credenciales o corrida original. Modo TITAN LIGERO, rúbrica formal N/A. Evidencia de arranque separada del veredicto aún pendiente.
