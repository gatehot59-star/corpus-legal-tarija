# Dos páginas lentas: texto idéntico y latencia repetida

Verificación realizada el 21-oct-2026. La inferencia terminó el 16-oct-2026 a las 15:24:45 ART; el observador descargó sus salidas a las 15:26:28 ART. No se relanzó OCR en este turno.

## Conclusión derivada

**PASS de igualdad exacta de texto:** las tres nuevas lecturas de cada página son idénticas entre sí y a su lectura en el lote original. Doce pares comprobados por igualdad directa de bytes UTF-8, sin normalizar espacios, saltos, tildes, mayúsculas ni forma Unicode. Cero pares distintos. Esto demuestra repetibilidad observada de estas dos páginas, no que su texto sea correcto.

**Latencia observada:** las dos páginas volvieron a tardar prácticamente lo mismo. No eran únicamente excepciones de tiempo irrepetibles del lote original. No se identificó la causa interna de la demora y no se definió retrospectivamente un umbral de aprobación temporal.

## Mediciones

<table><tr><th>Página</th><th>Original, s</th><th>Tres repeticiones, s</th><th>Media, s</th><th>Mediana, s</th><th>Desvío estándar muestral, s</th></tr><tr><td>PDF Resoluciones 216 a 250 de 2012/2013, página 1 (p037)</td><td>155.285756</td><td>154.547697; 155.706264; 155.797829</td><td>155.350597</td><td>155.706264</td><td>0.696837</td></tr><tr><td>Ley 151/2016, página 2 (p092)</td><td>168.662756</td><td>166.964220; 168.399527; 169.046028</td><td>168.136592</td><td>168.399527</td><td>1.065520</td></tr></table>

Cambio de media respecto de la lectura original: +0.041756 % para p037 y -0.311962 % para p092. Rangos nuevos: 1.250132 y 2.081808 segundos. Sólo tres repeticiones por página, una sesión GPU nueva; no tres sesiones independientes.

Las seis inferencias sumaron 970.461565331 s y el lote continuo tardó 970.526994552 s (16 min 10.527 s). Preparación y carga no están incluidas en ese lote. Inicio del lote: 16-oct 15:08:34.651573 ART; fin: 15:24:45.178599 ART. Inferencia: exit 0. GPU real verificada por parámetros Place(gpu:0), Tesla T4.

## Igualdad de texto

p037 conserva 1204 caracteres, 1217 bytes UTF-8 en las cuatro lecturas. SHA256 del texto: 95ea8c35df4c20c3561383ecc9328623c583d0824f1e84f8f5d03d4d5b6e7afb.

p092 conserva 2362 caracteres, 2413 bytes UTF-8 en las cuatro lecturas. SHA256 del texto: f99debd9b3280558d9a3a25070ce415d3045785787ad8b1e2e1cbc4872c89c22.

Los seis JSON crudos de layout también resultaron idénticos, byte por byte, a sus originales, no sólo su texto extraído. Hashes crudos: p037, 4ccd14493fe3ebf0ac5170fdd7c306de65aaf3e6439da71f10cce0794bb4ecce; p092, 32a8134152102d6ba876331d7f83a0ff2c33f9349ff1e5424f7e5a971c27392e. Los JSON crudos completos permanecen en Kaggle y brain-env; este commit contiene los ocho textos completos, los tiempos y recibos esenciales, no todos los logs ni las cajas.

## Qué se controló

Se leyó el código del ensayo y su recibo de arranque previamente publicado. Orden sellado A,B,B,A,A,B; cada iteración llama predict, sin caché de predicciones de la aplicación. Se conservó el calentamiento, la semilla 20261015, la configuración, el límite de 4096 tokens por bloque y las imágenes originales a 300 dpi. El manifiesto congelado conserva cien imágenes; únicamente se procesaron las dos seleccionadas, tres veces cada una. No se subieron textos originales a la inferencia.

Los 125 nombres y versiones de paquetes registrados coinciden con el lote original. También coinciden el manifiesto de modelos, sus revisiones y hashes, el pipeline y parámetros comparados, y la imagen Docker recuperada en el arranque. No se afirma identidad de host físico ni telemetría continua de temperatura o carga.

La verificación del 21-oct comprobó seis IDs en el orden esperado, dos entradas distintas con hashes originales, seis archivos crudos y sus SHA256, texto extraído contra bloques, longitudes, número de bloques, tiempos positivos, orden sin solapamientos, suma y reloj de pared compatibles, estado completed y exit 0. Se volvió a comprobar el pin del manifiesto y los archivos originales de tiempos y predicciones.

Instrumento de igualdad: a.encode('utf-8') == b.encode('utf-8'), no similarity score. Control positivo idéntico aceptado; cinco variantes distintas detectadas: carácter, espacio agregado, LF frente a CRLF, Unicode compuesto frente a descompuesto y negación eliminada. Estos controles son artificiales y no resultados OCR adicionales. Cualquier diferencia de texto real habría producido igualdad falsa.

Operador: BRAIN GPT-6 Astra, ejecución mediante build.python en brain-env, exit 0. No auditoría externa. Los avisos previos de wrapt ausente, ccache y deprecación de synchronize siguen en el log; la inferencia terminó con exit 0 y seis salidas. No se ocultaron ni se les atribuyó la latencia.

## Evidencia y reproducción

[Datos, ocho textos y recibos](../evidencia/2026-10-21-01-repeticion-ocr-cierre.json).

Para recomputar la igualdad desde ese JSON, agrupar los IDs de repeat_predictions por p037/p092, agregar el texto de original_predictions de cada grupo, codificar cada cadena como UTF-8 y comparar todos los pares sin strip ni normalización. Para los tiempos usar repeat_timings.seconds, agrupado por el mismo prefijo. original_timings contiene la referencia temporal. Cada texto incluye los saltos iniciales y el contenido OCR sin correcciones.

[Ensayo de seis inferencias, versión 1](https://www.kaggle.com/code/abrahammendieta/corpus-vl16-repeat-two-outliers-20261016).

[Corrida original de cien páginas](https://www.kaggle.com/code/abrahammendieta/corpus-vl16-100-pages-20261016).

[Protocolo y arranque sellados](https://github.com/gatehot59-star/corpus-legal-tarija/commit/c7b33ce4103f6ec95546bcb142b9c07374bf0537).

## Límites y estado del producto

NO MEDIDO: exactitud contra un gold humano para estas páginas, causa de los 155/168 segundos, costo por bloque o tokens, repetibilidad en otras máquinas o cargas, y generalización al corpus completo. Una lectura incorrecta también puede repetirse exactamente. La historia de las 36/91 páginas que precedían a estos casos en el lote original no se reprodujo.

No se corrigió ni integró un OCR en producción, no se hizo deploy ni merge, ni se modificaron pesos, imágenes, credenciales o permisos. El avance es una medición cerrada, no una optimización. El análisis previo de cien páginas sigue siendo 59 min 37.087 s continuos y no se sustituye por el tiempo de esta selección lenta.
