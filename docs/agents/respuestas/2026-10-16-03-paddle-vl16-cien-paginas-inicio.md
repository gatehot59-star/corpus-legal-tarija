# Cien páginas seguidas con PaddleOCR-VL-1.6: medición lanzada, tiempo pendiente

16-oct-2026. Pedido: «Medí cuánto tarda procesar cien páginas seguidas».

## Estado del checkpoint

**EN CURSO.** Kaggle aceptó la versión 1 el 16-oct a las **10:31:01 ART**. A las **10:31:18 ART** su estado era `KernelWorkerStatus.RUNNING`. No es un resultado de cien páginas completadas, ni confirma todavía la fase interna de inferencia. **Tiempo total de cien páginas: NO MEDIDO en este checkpoint.** No se multiplicó por veinte la corrida previa.

Notebook privado: https://www.kaggle.com/code/abrahammendieta/corpus-vl16-100-pages-20261016

Dataset privado: https://www.kaggle.com/datasets/abrahammendieta/corpus-throughput100-20261016

La lectura de vuelta del notebook confirmó `is_private: true`, `enable_gpu: true`, `machine_shape: NvidiaTeslaT4` y el código exacto por SHA256. La selección de GPU no sustituye la comprobación de hardware y parámetros que hará el runner antes de inferir.

## Qué se procesa

**Cien páginas distintas de 34 documentos jurídicos públicos de Corpus**, una detrás de otra. No son cien páginas contiguas de un único PDF ni veinte repeticiones de las cinco páginas anteriores.

Se seleccionaron las primeras cien imágenes de hashes distintos del índice histórico de 120 páginas, ordenando por SHA256 del PDF y número de página. No se eligieron según las salidas del OCR. Todas las imágenes conservan sus bytes y resolución original: el metadato PNG fue comprobado a 299,9994 dpi, equivalente a 300 dpi. No se aplica reducción externa de resolución.

El manifiesto enumera las cien páginas, su orden, hash PNG, hash PDF, página fuente, título, dimensiones y URL de imagen. El índice fuente tiene SHA256 `01594b2af1fddeeb9ce741d8940fef2bbaae8a45c91b8e5201d0a86a19efee39`. La selección contiene 100 hashes de imagen distintos; no se saltaron duplicados antes de completar los cien. El ZIP privado sólo lleva 100 PNG y manifiesto, sin gold, credenciales ni expedientes privados.

No se reclama muestra representativa de todo Corpus ni precisión OCR sobre estas cien páginas: **no tienen gold humano y no se puntúa exactitud**. Se mide rendimiento de procesamiento sostenido.

## Contrato de medición

Se reutilizan el motor, pesos, versiones y configuración efectivos de la corrida GPU anterior: PaddleOCR-VL-1.6, PaddleOCR 3.7.0, PaddleX 3.7.2, PaddlePaddle GPU 3.3.1 cu126, batch 1 y máximo 4.096 tokens por bloque. Una T4 (`gpu:0`) para reconocimiento, aunque Kaggle pueda asignar dos. El runner prohíbe fallback silencioso a CPU y comprueba que los parámetros estén en GPU.

El modelo se construye una sola vez, se hace un calentamiento sintético y luego se llaman cien inferencias reales consecutivas, sin caché de predicciones ni recarga entre páginas. Se guardan todos los bloques y textos, sin editar salidas.

Se registran por separado:

1. Preparación fría: instalación, descarga de pesos y preparación del entorno.
2. Carga del modelo y calentamiento sintético.
3. Suma de tiempos de las cien inferencias, con sincronización CUDA.
4. Tiempo continuo del lote, incluido guardado de resultados y sobrecarga entre páginas.
5. Tiempo de cada página, mediana, extremos y comparación descriptiva de las primeras diez con las últimas diez; pico de memoria residente por página.

El timeout por página sigue siendo 1.800 segundos. El presupuesto del proceso de inferencia es de 21.600 segundos y el notebook tiene un límite solicitado de 25.200 segundos. Son límites de seguridad, no estimaciones de duración. Un fallo o un timeout conserva las salidas parciales y no se publica como tiempo de cien páginas completas.

## Instrumentos de control

El adaptador pasó sus cinco fixtures, exit 0. La preparación leyó y verificó exactamente 101 archivos del ZIP, y rechazó un PNG deliberadamente alterado. El verificador temporal pasó una corrida artificial positiva y rechazó ocho manipulaciones: página faltante, entrada duplicada, hash incorrecto, tiempo cero, agregado incorrecto, solapamiento temporal, estado no final y más de una carga declarada.

**Esas pruebas son artificiales: no son cien páginas OCR procesadas.** Sólo verifican el instrumento. El verificador final también exige los cien IDs en orden, hashes de entrada, longitud de cada salida, consistencia del reloj UTC con el monotónico, suma y duración total, hashes de los JSON crudos y exit 0 del proceso.

La declaración `model_loads: 1` se sustenta además en la lectura del runner, que construye el pipeline una vez antes del bucle. Ese campo por sí solo no es un sensor independiente de recargas internas. No se afirma independencia de operador ni auditoría externa.

## Seguimiento real

Un proceso en brain-env quedó consultando el estado cada 60 segundos. Cuando termine la versión 1, descargará sus outputs y ejecutará el verificador sobre los resultados completos. Si hay error, guardará el fallo en vez de inventar una duración. **No relanza jobs, no cambia parámetros, no envía mensajes y no hay notificación automática al usuario.**

Raíz de trabajo en brain-env: `/workspace/paddle-vl16-100-20261016`. Archivos de seguimiento: `watch.log`, `watch-history.jsonl`, `completion.json` o `watch-failure.json`. Resultados previstos al finalizar: `output-v1/corpus-vl16-results`, recibo de descarga y recibo de verificación. Se comprueba la existencia de cada uno al retomar, no se supone que ya esté creado.

## Huellas del experimento

- Manifiesto: `f20a4fff96ec400b0e877ec800034ae86bfbf7d397c4b0b70c72ff92426f9aad`.
- ZIP de 196.202.786 bytes: `1902df14f23e1016228db9d1db2684806a0b35ed6bedc2c43fcb5b96ea41fbc3`.
- Runner: `f4a3ca42cf694fc185ec1e0fc6d56cf8913b4d92d26fde260eb485948bbd182c`.
- Kernel: `b1ad69ed971d6d95f8e6c76cf1300b89ed69705cfdf738a6e4775b523c84f403`, idéntico al recuperado de Kaggle.
- Verificador: `17ee3aa70155273017566a6fb94031fb136ba0e73726ca52d552468b151fe934`.
- Observador: `773ce68bf94b80f0071f3d433b4d6ef456f16e25f098dc87e40d53b43384bddd`.

Los scripts y el manifiesto completo están en brain-env y el kernel en Kaggle. Este commit es **un checkpoint documental con recibos de arranque**, no un paquete completo de resultados ni una declaración de éxito del benchmark.

## Antes de firmar

«La ejecución fue aceptada y estaba activa» → push y campo de estado Kaggle → podían fallar → PASS de arranque.

«El código privado coincide con el preparado» → pull de metadata y hash de fuente → podía diferir → PASS.

«Procesó cien páginas en X minutos» → todavía no existe recibo final leído → NO MEDIDO.

«Precisión jurídica de cien páginas» → sin referencia adjudicada → NO MEDIDO y fuera de alcance.

## Errores propios y alcance

La primera inspección de PNG intentó usar PIL con el Python base de la VM, que no lo tenía; se usó el venv de Paddle ya instalado. Una llamada de preparación del observador agotó la espera del transporte; se comprobó que el archivo no existía antes de reintentar. La consulta del dataset durante la subida devolvió 403; después de la creación efectiva devolvió `ready`. Ninguno se confundió con fallo del OCR ni con duplicación de la corrida.

No se modificaron producción, main, credenciales, permisos, workflows ni el notebook del banco de cinco páginas. Se creó un experimento privado separado. TITAN LIGERO: instrumento diagnóstico acotado, rúbrica formal N/A. No hay PR ni revisión externa emitida.
