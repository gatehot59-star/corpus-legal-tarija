# Latencia de PaddleOCR-VL-1.6 por documento y características

16 de octubre de 2026. Lectura posterior a la corrida, sin detener ni relanzar OCR.

## Resultado y alcance

PASS de cobertura y consistencia temporal: 100/100 páginas distintas de 34 PDFs públicos, una pasada secuencial en Tesla T4 (parámetros Place(gpu:0)), a 300 dpi. No es PASS de exactitud.

Lote continuo: **3577.087365249 s, 59 min 37.087 s**. Suma de inferencias: 3575.853638565 s. Diferencia de escritura/intervalos: 1.233727 s. Media de inferencia: 35.758536 s/página; mediana: 32.086812 s; extremos: 6.323810 a 168.662756 s. Rendimiento continuo: 1.677342 páginas/minuto.

El lote comenzó 10:38:49.520909 ART y terminó 11:38:26.608312 ART. Preparación más ejecución del notebook: 10:31:14.384671 a 11:38:31.359786 ART, 4036.975115 s. Carga del modelo: 4.270517 s; calentamiento: 3.615933 s, incluidos en preparación, no en lote continuo.

Se recogieron y procesaron 100 registros; faltantes y fallidos: cero. 33 documentos aportan tres páginas y uno aporta una. Las páginas seleccionadas de un PDF no necesariamente son contiguas ni representan todo el documento. Los totales por documento de abajo son exclusivamente los de la muestra.

## Características de página

Las etiquetas son las producidas por el modelo, no una clasificación humana ni inspección visual de las cien imágenes. Los caracteres son texto emitido, no cantidad verdadera de texto presente. Los umbrales son descriptivos post hoc.

| Característica | Páginas | Media s | Mediana s |
|---|---:|---:|---:|
| Tabla detectada | 23 | 53.054 | 52.717 |
| Sin tabla detectada | 77 | 30.592 | 24.842 |
| Menos de 1000 caracteres emitidos | 23 | 15.635 | 15.834 |
| 1000 a 2499 caracteres emitidos | 53 | 35.786 | 31.756 |
| 2500 o más caracteres emitidos | 24 | 54.983 | 48.254 |
| Menos de 15 bloques | 47 | 36.521 | 22.384 |
| 15 a 24 bloques | 49 | 34.547 | 33.168 |
| 25 o más bloques | 4 | 41.642 | 42.360 |

Las tablas se asociaron con una media 1.73 veces mayor, pero también con más texto: 2428 frente a 1628 caracteres por página. No es una estimación causal del costo de una tabla. Entre las páginas con al menos 2500 caracteres: 12 con tablas promediaron 66.000 s y 12 sin tablas 43.967 s; sigue sin ser un ensayo pareado ni ajuste suficiente por contenido.

Correlación Spearman entre duración y caracteres emitidos: 0.922241; con caracteres de contenido crudo (incluye HTML de tablas): 0.948578. Pearson correspondiente: 0.627777 y 0.647946, sensible a las dos excepciones lentas. Son asociaciones posteriores al OCR, no un predictor validado para archivos nuevos.

Cantidad de bloques: Spearman 0.050026, sin asociación monotónica apreciable en esta muestra. Megapíxeles: Pearson -0.027776 y Spearman -0.259007. Rango 8.5272 a 20.625405 MP, todos a 299.9994 dpi. Esto no demuestra que bajar resolución no ayude: resolución, contenido y formato no se variaron en forma controlada.

## Comparación de los 34 documentos

Títulos abreviados desde el manifiesto, sin el parámetro residual &start. Media, mediana y total en segundos. El CSV acompaña las cien páginas y sus posiciones originales. Los identificadores pNNN se vinculan al manifiesto congelado, que conserva SHA256 completo y URL de imagen.

| Documento | IDs de muestra | Páginas originales | Media s | Mediana s | Total s |
|---|---|---|---:|---:|---:|
| Ley 151/2016 | p091,p092,p093 | 1,2,3 | 76.493 | 36.161 | 229.478 |
| Resoluciones 216 a 250, 2012/2013 | p037,p038,p039 | 1,20,39 | 64.770 | 20.754 | 194.309 |
| Ley 351/2018 | p046,p047,p048 | 1,3,5 | 63.083 | 59.522 | 189.249 |
| Ley 365/2018 | p025,p026,p027 | 1,2,4 | 59.552 | 54.783 | 178.657 |
| Ley 238/2017 | p067,p068,p069 | 1,2,3 | 58.543 | 57.659 | 175.630 |
| Ley 474, modificación presupuestaria 2023 | p082,p083,p084 | 1,2,3 | 54.693 | 55.217 | 164.079 |
| Ley 318/2018 | p028,p029,p030 | 1,2,3 | 53.924 | 47.614 | 161.772 |
| Ley 522, bomberos voluntarios | p031,p032,p033 | 1,3,5 | 41.311 | 42.188 | 123.933 |
| Ley 239/2017 | p013,p014,p015 | 1,2,4 | 40.324 | 39.555 | 120.972 |
| Ley 139/2016 | p076,p077,p078 | 1,4,8 | 39.774 | 35.385 | 119.323 |
| Ley 396/2019 | p043,p044,p045 | 1,2,4 | 39.247 | 39.399 | 117.741 |
| Ley 471, presupuesto 2024 | p097,p098,p099 | 1,2,3 | 39.091 | 46.043 | 117.272 |
| RPA 047/2021-2022, POA | p040,p041,p042 | 1,2,3 | 38.871 | 39.473 | 116.613 |
| Ley 230/2017 | p061,p062,p063 | 1,3,6 | 38.429 | 34.360 | 115.288 |
| RPA 040-1/2021-2022, agenda estratégica | p010,p011,p012 | 1,2,4 | 36.407 | 34.648 | 109.222 |
| Ley 005/2010 | p004,p005,p006 | 1,2,3 | 34.003 | 38.160 | 102.008 |
| Ley 109/2014 | p052,p053,p054 | 1,7,14 | 31.085 | 34.462 | 93.255 |
| Ley 009/2010 | p100 | 1 | 30.857 | 30.857 | 30.857 |
| RPA 001 ad hoc/2022-2023 | p085,p086,p087 | 1,2,3 | 30.561 | 33.168 | 91.682 |
| RPA 008/2022-2023, sesión ordinaria | p049,p050,p051 | 1,2,4 | 26.903 | 33.748 | 80.708 |
| Ley 155/2016 | p088,p089,p090 | 1,2,3 | 26.830 | 22.384 | 80.490 |
| Resoluciones 311 a 347, 2013/2014 | p022,p023,p024 | 1,20,40 | 26.646 | 26.607 | 79.938 |
| Resoluciones 237 a 275, 2013/2014 | p058,p059,p060 | 1,21,41 | 25.661 | 26.018 | 76.982 |
| Resoluciones 21 a 50, 2011/2012 | p055,p056,p057 | 1,16,31 | 24.919 | 14.379 | 74.756 |
| Resoluciones 71 a 109, 2013/2014 | p001,p002,p003 | 1,21,41 | 24.422 | 18.970 | 73.267 |
| Resoluciones 71 a 105, 2014/2015 | p007,p008,p009 | 1,18,35 | 23.681 | 17.808 | 71.042 |
| Ley 066/2012 | p064,p065,p066 | 1,2,3 | 23.494 | 18.814 | 70.483 |
| Resoluciones 1 a 59, 2015/2016 | p094,p095,p096 | 1,29,58 | 22.352 | 21.717 | 67.056 |
| Resoluciones 36 a 70, 2014/2015 | p079,p080,p081 | 1,18,36 | 21.031 | 18.514 | 63.094 |
| Resoluciones 161 a 190, 2011/2012 | p034,p035,p036 | 1,16,31 | 20.563 | 16.372 | 61.688 |
| Ley 371/2019 | p073,p074,p075 | 1,3,5 | 19.929 | 14.647 | 59.787 |
| Resoluciones 1 a 35, 2012/2013 | p070,p071,p072 | 1,18,36 | 19.132 | 18.984 | 57.396 |
| Resoluciones 86 a 103, 2010/2011 | p019,p020,p021 | 1,9,18 | 18.301 | 16.696 | 54.904 |
| Resoluciones 266 a 305, 2011/2012 | p016,p017,p018 | 1,20,39 | 17.641 | 19.080 | 52.922 |

## Excepciones que importan

p092, Ley 151/2016 página 2: 168.662756 s, 2362 caracteres, 13 bloques y ninguna tabla detectada. Las otras dos páginas del mismo documento tardaron 36.160741 y 24.654783 s. Su media de 76.493 s está dominada por una única página.

p037, primera página del PDF de resoluciones 216 a 250 de 2012/2013: 155.285756 s, 1204 caracteres, 15 bloques y ninguna tabla detectada. Las otras páginas muestreadas tardaron 18.268538 y 20.754212 s. Las dos excepciones juntas consumieron 9.06 % del tiempo de inferencia de todo el lote. No se midieron tiempos por bloque, tokens descartados, temperatura o utilización continua; no atribuirlas a firmas, mala imagen, throttling ni límite de tokens.

Las siguientes lentas sí tienen tablas detectadas: Ley 318/2018 página 2, 100.112 s; Ley 351/2018 página 3, 97.310 s; Ley 365/2018 página 2, 81.452 s.

La más rápida, p074 (Ley 371/2019 página 3), tardó 6.324 s y emitió 262 caracteres. Incluye tres bloques clasificados como image, cuyo contenido no se transcribe con use_ocr_for_image_block=false. Rapidez no demuestra lectura completa ni calidad; no llamarla simplemente una página fácil.

Las primeras diez páginas promediaron 28.810 s y las últimas diez 44.466 s, pero su contenido es distinto y p092 está en el último grupo. Orden de ejecución frente a latencia: Spearman 0.053957. No hay base para afirmar degradación progresiva por esa comparación.

## Método, evidencia y límites

Se cruzaron manifest.json, timings.json, predictions.json y los cien pNNN-raw.json por ID. Se verificó SHA256 de cada salida cruda, número de bloques y longitud del texto contra tiempos. verify100.py se volvió a ejecutar: salida completa, exit 0; control positivo y ocho mutaciones rechazadas (missing, duplicate_input, wrong_hash, zero_time, aggregate, overlap, not_completed, reload). El instrumento puede rechazar incoherencias, pero no mide exactitud. Mismo operador, no auditoría externa.

El log conserva un aviso de sitecustomize por wrapt ausente, avisos de ccache y deprecaciones. La inferencia terminó exit 0 y cien PAGE_DONE; no se borraron los avisos ni se usaron para inventar una causa de los outliers.

CSV derivado: ../evidencia/2026-10-16-04-latencia-paginas.csv. Duraciones redondeadas a seis decimales; las métricas se calcularon con valores completos. Fuente completa de la corrida: [Kaggle, versión 1](https://www.kaggle.com/code/abrahammendieta/corpus-vl16-100-pages-20261016). Los JSON crudos, textos y logs permanecen allí y en brain-env; este commit no pretende contenerlos íntegros.

Hashes SHA256 de los insumos:

- manifest.json: f20a4fff96ec400b0e877ec800034ae86bfbf7d397c4b0b70c72ff92426f9aad
- timings.json: 131c36cb21c6741197cbf8c22762c6e855e7be58767bcc65d86115bfeaae1887
- predictions.json: 272b79a4c8ff823ee4c22a85ad647cbe5574c67d264d65c9da88a46b6ff157b7
- status.json: 43cbb2c356b58de0fc1383618c07c2ef9c443b20d098d50003b82a6351c522db

Recomendación: estimar el trabajo por volumen de texto y tablas, no sólo por número de páginas; instrumentar bloques y repetir p037/p092 antes de intentar optimizar sus demoras. Es una recomendación, no una ejecución nueva. NO MEDIDO: CER/WER de estas cien páginas, causalidad de las diferencias, efecto de bajar resolución, repetibilidad y rendimiento de producción. Sin cambios de producto, main, PR ni deploy.
