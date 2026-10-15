# Corpus: comparación de ambos OCR sobre el banco completo

15 de octubre de 2026. Corrida: 14:00:22 a 14:06:02 ART (17:00:22 a 17:06:02 UTC).

## Conclusión

**Conservar el OCR estándar como referencia. No promover el calibrado actual.** Los dos usan Tesseract; el calibrado no es un motor entrenado aparte. Su consenso conserva variantes incompatibles como líneas adicionales, acumula contenido y empeora los cuatro controles con referencia.

Se ejecutaron las diez imágenes originales con cada brazo: 20 salidas y 170 llamadas OCR medidas (10 estándar, 160 calibrado), más un calentamiento separado. Todos los procesos finalizaron con código 0, lo cual NO significa que el texto sea correcto.

En los cuatro controles, el estándar produjo **22 ediciones de caracteres sobre 3.648 caracteres de referencia: CER 0,6031 %**. El calibrado produjo **5.649 ediciones: CER 154,8520 %**. CER puede superar 100 % porque las inserciones adicionales también cuentan. No significa una precisión negativa.

Banco completo: **17,117 s estándar contra 319,506 s calibrado**, 18,666 veces más tiempo. Son sumas de tiempos observados por imagen, no latencia de servicio ni benchmark repetido.

## Sujetos exactos y entorno

- Estándar: comando de reconocimiento de `pipeline/ocr_masivo.py` en main `c273c659ee90f2259f540cb14c576d6a16dcfb40`: Tesseract, español, PSM 3. Se midió la etapa PNG a texto, no el pipeline completo de descarga, PDF, gate documental y publicación.
- Calibrado: `/workspace/ocr_calibrado.py`, SHA-256 `ca03ca138d3cca94f98b5c3f73ded64f51e5a06e465b111fe519feb6edc797ab`. Se invocaron sus funciones originales `preprocesa`, `tesseract` y `consenso`, sin corregirlas. Cuatro preparaciones (gray, contrast, threshold, resize) por PSM 3, 4, 6 y 11. Dieciséis candidatos por imagen, en ese orden.
- Ambos usaron el binario Tesseract 5.5.3, sus bibliotecas y `spa.traineddata` copiados desde brain-env y verificados por hash. No se sustituyeron por el Tesseract 5.3.4 de la VM.
- Se ejecutó en la VM Corpus Ubuntu 24.04, kernel 6.16.9+, glibc 2.39, dos CPU, Pillow 12.3.0. Brain-env tenía otro proceso activo consumiendo CPU. Estos tiempos son de la VM, NO de brain-env; tampoco prueban paridad bit a bit entre ambas CPU.
- `OMP_THREAD_LIMIT=1`, `OMP_NUM_THREADS=1`, prioridad nice 10. Ejecución secuencial, estándar seguido de calibrado por imagen. Un warmup estándar sobre el control limpio, fuera del tiempo medido.
- No se rerasterizaron los PNG. Se preservaron los hashes del banco de la mañana: seis escaneos públicos y cuatro variantes sintéticas de un único fragmento de Ley 439. Los controles ya se habían visto: no son held-out ni cuatro textos independientes.
- No se modificó el script original, main, despliegue ni documentos del Corpus. No se envió nada a ABBYY.

## Cuatro controles: precisión medible

| Control | Estándar: ediciones caracteres / palabras | Calibrado: ediciones caracteres / palabras | CER estándar | CER calibrado |
|---|---:|---:|---:|---:|
| Limpio | 3 / 3 | 151 / 30 | 0,3289 % | 16,5570 % |
| Giro 2 grados, blur y ruido | 7 / 7 | 3.559 / 619 | 0,7675 % | 390,2412 % |
| 150 dpi | 8 / 7 | 732 / 127 | 0,8772 % | 80,2632 % |
| Dos columnas | 4 / 4 | 1.207 / 220 | 0,4386 % | 132,3465 % |
| Total | 22 / 21 | 5.649 / 996 | 0,6031 % | 154,8520 % |

WER agregado: estándar 3,5714 %, calibrado 169,3878 %. Normalización: NFC y colapso de blancos únicamente; se mantienen acentos, mayúsculas y puntuación.

Ambos conservaron las 32/32 presencias de cadenas que se buscaban. **Ese chequeo no detecta el contenido agregado incorrectamente.** Tampoco lo detectó `gate_v2.evaluar([texto])`: devolvió APTO en las veinte salidas. Esta fue una aplicación diagnóstica por página, no el gate documental completo de producción. No debe leerse APTO como exactitud jurídica.

## Seis páginas reales: tiempos y volumen, sin precisión inventada

| Página | Estándar s | Calibrado s | Caracteres estándar | Caracteres calibrado |
|---|---:|---:|---:|---:|
| Ley 522 p. 1 (d01-p001) | 3,613012 | 56,798190 | 3.452 | 30.011 |
| Ley 522 p. 3 (d01-p003) | 2,577071 | 45,375892 | 2.952 | 6.728 |
| d02-p001 | 4,181846 | 72,392962 | 2.895 | 3.805 |
| d02-p002 | 2,194942 | 43,471844 | 1.471 | 2.456 |
| d03-p001 | 1,022465 | 21,390842 | 903 | 4.997 |
| d03-p020 | 1,307983 | 25,727213 | 1.318 | 5.510 |
| Total real | 14,897318 | 265,156943 | 12.991 | 53.507 |

La diferencia de longitud no es por sí sola una tasa de error. **No hay transcripción independiente de esas seis páginas: CER/WER reales siguen NO MEDIDOS.** Los cuatro controles sí demuestran una regresión del calibrado; no hace falta fingir un gold real para descartarlo en su estado actual.

## Por qué falla el consenso

Se inspeccionó y ejecutó la función original. Agrupa cada línea por una clave que elimina tildes, puntuación y mayúsculas, pero no alinea líneas equivalentes por posición o significado. Si cambia una letra, un número o un salto de línea, aparece una clave nueva. La función termina uniendo una línea ganadora de CADA clave, incluidas claves incompatibles.

Prueba directa contra el código original:

- Entrada: `Ley 439` y `Ley 438`.
- Salida exacta: `Ley 439\nLey 438`.
- Alertas: `[]`.

No elige entre los dos números: conserva ambos sin alerta. En cambio `no podrán intervenir` frente a `no podran intervenir` sí comparte clave y genera alerta. El fallo es más concreto que decir que Tesseract lee mal: el ensamblado añade candidatos distintos como contenido adicional.

El control limpio ilustra la regresión: el estándar tiene 918 caracteres y el calibrado 1.060, con variantes adicionales de la cabecera y del inciso. El control inclinado llega a 4.466 caracteres contra 918 del estándar. Los textos íntegros de los ocho controles están en la evidencia JSON publicada.

## Frente a las pruebas anteriores

En el mismo banco, el Tesseract 5.3.4 anterior dio 24 ediciones de caracteres; el estándar 5.5.3 actual dio 22. **No atribuir los dos caracteres de diferencia exclusivamente a la versión:** también hay configuración y recursos de runtime a controlar. Sólo una de las diez salidas nuevas fue byte a byte idéntica a su salida anterior.

PaddleOCR simple había dado 690 ediciones, casi todas por el orden de dos columnas. PP-Structure había corregido columnas y dañado el inclinado. Paddle más geometría había dado 1 edición total en los cuatro controles, pero después se detectaron falsas columnas en dos páginas reales. Por eso este resultado respalda conservar el estándar frente al calibrado actual, **no declarar un ganador universal ni desplegar geometría sin arreglar y volver a validar su orden real**.

## Verificación, evidencia y límites de publicación

El verificador separado `verify.py` recalculó los ocho CER/WER con matriz completa, comprobó 20 salidas, 170 llamadas, hashes de entradas y reconstrucción del consenso sin importar el módulo OCR. Rechazó cinco alteraciones deliberadas: caso ausente, texto, exit code, hash de entrada y score. Exit 0. La selección e interpretación fueron del mismo operador: **no es auditoría externa**.

El verificador publicable `2026-10-15-09-verificar-ocr-corpus.py` también se ejecutó: 20 registros, 170 exits, ocho scores recalculados y un score alterado rechazado, exit 0. Ejecución desde la raíz del repositorio:

```sh
python3 docs/agents/evidencia/2026-10-15-09-verificar-ocr-corpus.py docs/agents/evidencia/2026-10-15-09-ocr-corpus.json
```

**Alcance explícito de la publicación:** Git incluye el reporte, los ocho textos completos con referencia, tiempos y hashes de las veinte salidas, los 170 códigos de salida, stderr íntegro deduplicado con índices que permiten reconstruirlo, resultados de verificación y el verificador publicable. No incluye las salidas reales completas, las 170 salidas candidatas ni el ejecutor completo de esta corrida. No se presenta este extracto como un archivo integral de reproducción.

El registro completo de 927.750 bytes se conserva en `/workspace/ocr-corpus-comparacion-20261015/record.json` en brain-env y `/tmp/ocr-corpus-comparacion-20261015/record.json` en la VM. SHA-256 `3e07cc61b084e1acf8f73f5f3c131159df282374e5b03315c8de58dcb312185a`. En ambos lugares están las fuentes ejecutadas; las imágenes intermedias permanecen en la VM. Esta publicación parcial de la evidencia es deuda respecto del estándar de guardar todo en Git, no un PASS de archivo completo.

Advertencia real conservada: dos lecturas de imágenes ampliadas informaron `Image too small to scale!! (2x36 vs min width of 3)` y `Line cannot be recognized!!`, aun con exit 0. Ningún mensaje se ocultó como si exit 0 implicara lectura íntegra.

Incidentes del operador: la conexión de lanzamiento venció a los 20 segundos; se comprobó que la corrida seguía y NO se relanzó. La lectura y verificación posteriores recuperaron cierre completo con exit 0. La publicación Git usa la integración; las vías Git nativas no autenticaron. No se instalaron paquetes ni se tocaron credenciales para resolverlo.

## Estado y decisión

- PASS: cobertura completa de los diez PNG por ambos brazos y validación de los ocho scores con referencia.
- FAIL: calibrado como mejora de calidad en este banco; empeora los cuatro controles y cuesta 18,666 veces más tiempo total.
- FAIL como detector de este problema: presencia de cadenas y gate por página no rechazan las duplicaciones medidas.
- NO MEDIDO: precisión de escaneos reales, calidad universal, latencia de producción, paridad entre máquinas, OCR ABBYY y auditoría externa.
- Sin cambios de producto: se comparó, no se corrigió ni desplegó.

Recomendación derivada: mantener estándar como referencia, no conectar la salida de este consenso a indexación/RAG, y corregir la alineación/selección del consenso antes de volver a medirlo. No se implementó esa corrección en este pedido.

## Método

TITAN LIGERO, diagnóstico acotado, acción delicada NO, rúbrica N/A. Instrumentos reales más evidencia verificable; interpretación propia y publicación parcial declaradas. Main quedó en `c273c659ee90f2259f540cb14c576d6a16dcfb40`.
