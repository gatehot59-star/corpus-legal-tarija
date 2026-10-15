# Tesseract y PaddleOCR ejecutados: velocidad real y un fallo de orden de columnas

Fecha: 15 de octubre de 2026. Operador: BRAIN / GPT-6 Astra. Pedido vigente: «Reintentá brain-env y corré ambos motores».

## Conclusión

Ambos motores terminaron los diez insumos. Sobre seis páginas escaneadas reales, Tesseract tardó **14,942383 segundos** y PaddleOCR **125,893766 segundos**: Paddle consumió **8,42528 veces** el tiempo de Tesseract en esta configuración y esta única pasada. Esto mide tiempo, no exactitud del texto real.

En cuatro controles sintéticos de un mismo texto, Paddle reconoció mejor las tres variantes de una columna, pero su salida concatenada intercaló las dos columnas del cuarto control. Tesseract conservó ese orden, aunque confundió signos ordinales y algunos numerales romanos. **No hay un ganador global para Corpus.** No se cambió ni desplegó Corpus.

ABBYY no ejecutó OCR. El producto descargado anteriormente es FineReader PDF 16 para Windows, no un motor Linux ya activado. No se instaló Wine, inició una máquina Windows, activó una prueba, aceptó una licencia ni eludió una protección. Esta entrega cierra la ejecución autorizada de Tesseract/PaddleOCR, no completa la comparación original de tres motores.

## PASS, FAIL y NO MEDIDO

| Estado | Resultado y alcance |
|---|---|
| PASS | Dos motores, diez entradas cada uno, veinte salidas con exit 0. |
| PASS | Ocho puntuaciones sintéticas recalculadas con otra implementación; veinte pares de salida textual y registro crudo verificados. |
| PASS | El verificador rechazó una salida alterada y un puntaje falsificado, en copias separadas. |
| PASS | Al cierre, diez imágenes y siete archivos seleccionados de modelos/configuración conservaban su hash; no quedaban procesos del benchmark. |
| FAIL | La concatenación de `rec_texts` de PaddleOCR no conserva el orden izquierda-después-derecha en el control de dos columnas. |
| FAIL | La transcripción de Tesseract no es exacta en ninguno de los cuatro controles: hay errores ordinales y, según variante, romanos. |
| NO MEDIDO | CER/WER de las seis páginas escaneadas reales, por falta de transcripción de referencia independiente. |
| NO MEDIDO | OCR de ABBYY, superioridad global, calidad jurídica, generalización a todo Corpus, carga de producción o integración. |

No confundir estos diez insumos OCR con los diez casos ciegos pendientes de Corpus contra RuleX.

## Banco y referencia

La selección se fijó antes de leer las salidas actuales: primeros tres `sample_index` de una muestra pública de Corpus ya existente; para cada uno, las primeras dos páginas muestreadas al ordenarlas por número. Es un piloto de conveniencia acotado, no una muestra aleatoria representativa de todo Corpus.

Se comprobaron los hashes de los PDF cacheados contra su registro existente. No se afirmó que se hubieran vuelto a descargar de la web oficial en esta corrida. Se rasterizó una sola vez cada página con Poppler `pdftoppm 24.02.0`, a 300 dpi y en escala de grises; ambos motores recibieron los mismos PNG. El PDF de resoluciones produjo avisos sintácticos de Poppler, conservados en la evidencia original, pero la rasterización terminó con exit 0.

| Casos | Documento público | Páginas |
|---|---|---|
| d01-p001, d01-p003 | [Ley Departamental N 522, Bomberos Voluntarios](https://www.tarija.gob.bo/gaceta-oficial/leyes-departamentales?download=3512:ley-departamental-n-522-bomberos-voluntarios) | 1 y 3 |
| d02-p001, d02-p002 | [Ley Departamental 005/2010](https://www.tarija.gob.bo/gaceta-oficial/leyes-departamentales?download=818:ley-departamental-005-2010&start=460) | 1 y 2 |
| d03-p001, d03-p020 | [Resoluciones del pleno 266 al 305, 2011/2012](https://www.tarija.gob.bo/gaceta-oficial/resoluciones-del-pleno-de-la-asamblea?download=846:resoluciones-del-pleno-de-la-asamblea-266-al-305-del-2011-2012&start=500) | 1 y 20 |

Para exactitud se usó otro banco, explícitamente sintético: encabezado, fecha y artículos 3 y 29 de [Ley 439, texto HTML de LexiVox](https://www.lexivox.org/norms/BO-L-N439.xhtml). La referencia se fijó antes de inferencia y no proviene de ninguno de los dos OCR. Se normalizó el espacio tipográfico de los encabezados antes de dibujar. No es una transcripción de los escaneos ni una validación jurídica independiente.

Se dibujó el mismo texto con DejaVuSerif de 32 px y avance de línea de 46 px: limpio, giro de 2 grados con desenfoque/ruido, reducción a 150 dpi y dos columnas. Semilla de ruido: 20261015. Son **cuatro variantes de un único texto**, de 912 caracteres normalizados y 147 palabras cada una, no cuatro textos independientes.

Normalización de puntuación: Unicode NFC y colapso de blancos, manteniendo mayúsculas, tildes y puntuación. CER y WER son distancias de Levenshtein divididas por la longitud de referencia. La bolsa de palabras es sólo diagnóstico de reordenamiento. Ocho búsquedas de presencia de cadenas, con límites de palabra, no validan relaciones jurídicas ni estructura de incisos.

## Entorno y configuraciones

Se ejecutó en la VM de Corpus ya existente, a través de brain-env. Linux 6.16.9+, glibc 2.39, Python 3.12.3, dos CPU y aproximadamente 8 GB de RAM. Antes del trabajo se midieron 7.311.184 kB disponibles y carga baja. No se instaló ningún paquete para esta corrida.

**Tesseract 5.3.4**: `tesseract <imagen> stdout --tessdata-dir /tmp/tessdata -l spa --oem 1 --psm 3`. El modelo español fue identificado por SHA-256, no supuesto a partir del nombre del directorio: `6f2e04d02774a18f01bed44b1111f2cd7f3ba7ac9dc4373cd3f898a40ea6b464`.

**PaddleOCR 3.7.0, PaddlePaddle 3.3.1 y PaddleX 3.7.2**: detector `PP-OCRv5_mobile_det`, reconocedor `latin_PP-OCRv5_mobile_rec`, CPU, `enable_mkldnn=False`, `cpu_threads=1`, lado máximo del detector 960. Clasificador de orientación, corrección geométrica y orientación de líneas desactivados. No se usó PP-Structure ni reconstrucción posterior del diseño. Se concatenaron los `rec_texts` en el orden devuelto. Había modelos de otra versión en caché, pero no se usaron.

Se configuraron `OMP_NUM_THREADS`, `OMP_THREAD_LIMIT`, `MKL_NUM_THREADS` y `OPENBLAS_NUM_THREADS` en 1. Esto **no demuestra aislamiento estricto a un hilo**: una observación del proceso Paddle mostró cuatro hilos del sistema operativo. No hubo afinidad ni cuota de CPU por cgroup. Los motores corrieron secuencialmente con `nice 10`, primero Tesseract, después Paddle, con una entrada de calentamiento y una sola pasada medida. No se ajustaron parámetros después de ver puntajes.

Los tiempos de Tesseract incluyen un proceso CLI por imagen; Paddle reutiliza un objeto inicializado. La inicialización de Paddle quedó registrada aparte en 2,039976 s. Los calentamientos fueron 0,113427 s y 0,435753 s, respectivamente. Los totales de etapa, incluyendo los cuatro controles y otros gastos, fueron 17,596086 s y 178,092771 s. No se incluyen rasterización, instalación ni descarga de modelos en la tabla de OCR real.

## Tiempos sobre las seis páginas reales

| Caso | Tesseract (s) | PaddleOCR (s) | Caracteres Tesseract | Caracteres Paddle |
|---|---:|---:|---:|---:|
| d01-p001 | 3,365826 | 32,106789 | 3444 | 3551 |
| d01-p003 | 2,586339 | 29,576016 | 2952 | 2923 |
| d02-p001 | 3,930681 | 25,645153 | 2893 | 2871 |
| d02-p002 | 2,432936 | 15,094473 | 1488 | 1616 |
| d03-p001 | 1,145982 | 9,891716 | 919 | 977 |
| d03-p020 | 1,480620 | 13,579619 | 1335 | 1321 |
| Total | **14,942383** | **125,893766** | 13031 | 13259 |

Más caracteres no significa más aciertos. `accuracy_on_real_scans` permanece `null` para ambos. Sin referencia independiente no corresponde convertir diferencias entre candidatos en errores de uno u otro.

Memoria registrada con `getrusage`: Tesseract, máximo del padre 31.500 KiB y máximo de hijos 256.324 KiB; Paddle, 772.932 KiB y 346.532 KiB. Son máximos de procesos, no memoria total simultánea: no deben sumarse ni interpretarse como una medición completa de consumo del sistema.

## Exactitud de los cuatro controles, desagregada

| Control | Ediciones de caracteres Tesseract | CER Tesseract | Ediciones Paddle | CER Paddle | Ediciones de palabras T/P |
|---|---:|---:|---:|---:|---:|
| Limpio | 4 | 0,4386 % | 0 | 0 % | 3 / 0 |
| Giro, desenfoque y ruido | 7 | 0,7675 % | 0 | 0 % | 7 / 0 |
| 150 dpi | 8 | 0,8772 % | 1 | 0,1096 % | 7 / 1 |
| Dos columnas | 5 | 0,5482 % | 689 | 75,5482 % | 4 / 112 |

Paddle devuelve exactamente el texto normalizado en los dos primeros controles. En 150 dpi pierde una coma después de «colusión». En dos columnas conserva todas las palabras: F1 de bolsa de palabras = 1,0, pero entremezcla las columnas. Empieza con `Ley Nº 439`, luego el encabezado de `Artículo 29`, luego la fecha de la columna izquierda. El fallo es del orden de lectura de esta salida sin reconstrucción de diseño, no prueba que se hayan perdido esas palabras.

En Tesseract aparecen `Ley N?2 439`, comillas u otros caracteres en lugar del ordinal y, en variantes degradadas, `1.`, `TI.` o `IL.` en lugar de `I.`/`II.`. Preservar el orden no equivale a preservar todos los incisos.

Para completar el registro, el agregado de las cuatro variantes es: Tesseract, 24/3648 ediciones de caracteres (CER 0,657895 %) y 21/588 de palabras (WER 3,571429 %); Paddle, 690/3648 (CER 18,914474 %) y 113/588 (WER 19,217687 %). **No usar ese agregado como ranking general de reconocimiento:** casi todo el error agregado de Paddle proviene del orden de columnas, y se repite un mismo texto en las cuatro variantes.

Ambos obtuvieron 32/32 presencias de cadenas. Ese chequeo limitado no detecta el desorden de columnas, relaciones entre disposiciones ni todos los numerales romanos. No son 32 hechos jurídicos validados.

## Instrumento, incidentes y controles que podían fallar

El primer lanzamiento, a las 11:19:51 UTC, falló antes de inferencia al buscar `spa.traineddata` en el directorio predeterminado. No fue un fallo de reconocimiento. Se conservaron el programa, sello y registros de ese intento. La v2 apunta explícitamente al modelo existente en `/tmp/tessdata`; se usó otro directorio, sin sobreescribir el intento fallido. Las cuatro imágenes sintéticas regeneradas conservaron sus hashes. No se cambió banco, referencia ni métrica por observar resultados.

Sello v2: 11:21:33,856034 UTC. Inicio: 11:21:33,952813 UTC. Fin: 11:24:50,975973 UTC, equivalentes a aproximadamente 08:21 a 08:24 ART.

El instrumento incluye pruebas de identidad, sustitución, salida vacía, pérdida de negación, límites de números, orden de lectura, espacios, tildes y mayúsculas, más 200 pares cruzados contra una matriz completa. Además se ejecutó `verify_results.py`, una implementación separada de Levenshtein con matriz completa `uint32`, sin llamar a la función de puntuación del benchmark. Recalculó las ocho puntuaciones y verificó veinte pares de archivos de salida. Para Paddle reconstruyó el texto desde los `rec_texts` del JSON crudo.

A las 11:26:23 UTC se ejecutaron dos pruebas negativas reales en copias: agregar `ALTERADO` a un texto produjo exit 1 por hash; falsificar a cero las cuatro ediciones de Tesseract limpio produjo exit 1 por discrepancia con el cálculo. No se alteraron los originales. La mera desigualdad de dos hashes en un auto-chequeo no es el único respaldo: existen esos dos rechazos ejecutados.

La implementación separada y sus falsadores son del mismo operador. **No se presentan como auditoría externa independiente.** SHA-256 del verificador conservado: `5095dd85ffe8cb215dd7adef808ae08734b72c8d4247eaa01e074d6c0b3e1e4c`.

A las 11:27:09,927028 UTC, `closure.json` registró las diez entradas sin cambios, siete archivos de modelos/configuración sin cambios y cero procesos activos del benchmark. No se reinició ningún servicio ni se modificaron código de aplicación, base de datos, cuentas o documentos de Corpus. Los avisos de Paddle sobre `lang` ignorado ante modelos explícitos y ausencia de `ccache` quedaron retenidos, sin fallo de inferencia.

## Evidencia publicada y límites de reproducción

Esta entrega añade tres archivos en una rama documental, sin PR ni merge:

- Este informe.
- [Instrumento v2 realmente ejecutado](../evidencia/2026-10-15-03-ocr-benchmark.py).
- [Paquete de evidencia seleccionada](../evidencia/2026-10-15-03-ocr-resultados.json): procedencia, hashes de las diez entradas, modelos seleccionados, configuración, veinte tiempos y hashes de salidas, ocho textos sintéticos completos, puntuaciones, validación, rechazos y cierre.

El JSON publicado **no es** el archivo original `evidence.json` completo. Los textos completos de las seis páginas reales por motor, los veinte registros crudos, el banco original, los avisos completos y el verificador están preservados en brain-env; imágenes y modelos también permanecen en la VM. No se publican PDF, PNG, pesos de modelos, binarios propietarios ni credenciales.

Identidades de los originales:

| Artefacto | SHA-256 |
|---|---|
| Banco v2 original | `cc8abf3c3f26674fe3547fa3687ec4f9e7796ce4051bf8f406a5f6aad49e31ab` |
| Instrumento ejecutado, 18.892 bytes | `becb1312ce876e7de2101178f8b51fd8eb0de87d45ec465a41d2279647db422a` |
| Evidencia original, 108.135 bytes | `4cafd94af84e3e79638bf5da2ede2286fd90d85c76162004ed8573ccb104bc4c` |
| Paquete JSON publicado, 29.490 bytes | `e95c7e01c9bef5dbc03cc2d9e2574b9982a8d154552168679e408b2db0de0db2` |

Custodia: brain-env `/workspace/ocr-ab-20261015-0foi89wk/results-v2`; VM `/tmp/ocr-ab-v2-20261015-bkeba6f_`. Las imágenes reales siguen referenciadas en `/tmp/ocr-ab-20261015-_jcbdno7/inputs`, por lo que ese directorio no debe descartarse como si sólo contuviera el intento fallido.

El script conserva las rutas del entorno ejecutado; no se afirma que sea una instalación portable lista con un comando. `selftest` sólo valida la aritmética y sus falsadores, no ejecuta OCR. Una repetición requiere los insumos, modelos y dependencias identificados y un directorio nuevo. No se repitió la inferencia para preparar esta publicación.

## Decisión recomendada, no implementada

No sustituir todavía el OCR de Corpus basándose en este piloto. Mantener Tesseract como referencia rápida y evaluar Paddle como candidato con reconstrucción de orden, sin dar por demostrado que esa mejora ya exista. Antes de elegir hace falta transcripción independiente de los escaneos reales y puntuar números, fechas, negaciones, incisos y asociaciones en su contexto, además de CER/WER. El brazo ABBYY queda pendiente de un runtime autorizado y utilizable para el producto concreto.
