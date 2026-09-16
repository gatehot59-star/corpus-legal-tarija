# La ventaja del corpus Tarija, reevaluada desde sus fuentes

16-sep-2026, America/Buenos_Aires. Lectura de código, no certificación de producción ni benchmark competitivo.

**Revisión de main examinada:** `9ac92c8b4ca2b853d4ce04276d89d32fa3e84290`.
**Trabajo adicional examinado parcialmente:** PR #1, abierto y no mergeado; head `2360f27d43fdc9a1e2a74a3f6465698918df2ad1`. El diff completo excedió el límite de lectura: no declaro auditoría íntegra del PR.

## Veredicto corregido

**El corpus tiene más valor propio del que reconocí al compararlo con chats jurídicos.** No es solamente una colección de PDFs ni la base interna de Custos: tiene procesamiento documental reproducible, tratamiento explícito de ambigüedades del OCR y una interfaz reutilizable por consumidores distintos.

La ventaja respaldada por los archivos es una especialización de datos y de integración. No está demostrada todavía una superioridad frente a competidores, exclusividad de cobertura tarijeña, fidelidad jurídica integral ni disposición a pagar. Retiro mi recomendación de centrar toda la oportunidad en operaciones del bufete como conclusión sobre el corpus: esa recomendación correspondía a Custos, que es otro producto.

## 1. La parte más valiosa: recuperar sin corregir la ley por intuición

En [normalizar_citas.py](https://github.com/gatehot59-star/corpus-legal-tarija/blob/9ac92c8b4ca2b853d4ce04276d89d32fa3e84290/pipeline/normalizar_citas.py), `extraer()` conserva el texto de entrada como prefijo del índice y añade aparte variantes de citas. Cada cita tiene `canonico_probable`, `ambigua`, línea y contexto. `Art. 17.1` puede producir una variante `Art. 17.I` para búsqueda sin sustituir esa cadena dentro del documento.

[test_citas.py](https://github.com/gatehot59-star/corpus-legal-tarija/blob/9ac92c8b4ca2b853d4ce04276d89d32fa3e84290/pipeline/test_citas.py) contiene casos de romanos, montos, referencias que no deben interpretarse como artículos y conservación del prefijo original. El [workflow OCR](https://github.com/gatehot59-star/corpus-legal-tarija/blob/9ac92c8b4ca2b853d4ce04276d89d32fa3e84290/.github/workflows/ocr-masivo.yml) invoca este test, el gate y los nombres de archivo antes de los shards. Leí ese cableado; no ejecuté una corrida nueva.

**Valor para el usuario:** encontrar una cita a pesar del OCR sin hacer pasar una corrección inferida por texto oficial. Esto sí tiene implementación específica, no solo una promesa comercial.

**Límite:** conservar el OCR no demuestra que el OCR copie fielmente el PDF. El campo de cita llamado `crudo` se obtiene sobre la línea sin diacríticos, mientras el contexto conserva la línea de entrada. La preservación del cuerpo no equivale a que cada campo sea byte a byte original.

## 2. El corpus puede servir a más de un producto

En [ingesta.py](https://github.com/gatehot59-star/corpus-legal-tarija/blob/9ac92c8b4ca2b853d4ce04276d89d32fa3e84290/sistema/api/ingesta.py), `Documento`, los adaptadores, el índice y la cola de revisión están separados. En [servidor.py](https://github.com/gatehot59-star/corpus-legal-tarija/blob/9ac92c8b4ca2b853d4ce04276d89d32fa3e84290/sistema/api/servidor.py), `cita_de()` entrega identidad, fuente y hash; la búsqueda devuelve confianza y vigencia, y la consulta para agentes permite limitar caracteres. Hay manifiesto y OpenAPI.

SQLite FTS5, BM25, filtros y biblioteca estándar reducen componentes de operación. Son tecnologías conocidas y copiables, no una barrera competitiva por sí mismas. El trabajo acumulado de adaptación de fuentes y tratamiento de errores puede ahorrar reconstrucción a un consumidor, pero no medí ese ahorro.

La [separación de productos](https://github.com/gatehot59-star/corpus-legal-tarija/blob/9ac92c8b4ca2b853d4ce04276d89d32fa3e84290/SUITE-Y-CONSUMIDORES.md) es explícita: el corpus mejora y existe aunque Custos se detenga. La forma del código es coherente con esa independencia. No hace falta convertirlo en gestor de expedientes para que tenga valor.

## 3. Tarija es especialización real; exclusividad sigue sin probar

Los adaptadores de Gaceta y TSJ están presentes. El material departamental se procesa como fuente propia, no como una mención incidental dentro de una base nacional. Sin embargo, no conté hoy el manifiesto completo ni consulté la base viva.

[COBERTURA.md](https://github.com/gatehot59-star/corpus-legal-tarija/blob/9ac92c8b4ca2b853d4ce04276d89d32fa3e84290/COBERTURA.md) conserva y corrige fotografías históricas; su snapshot del 9-sep informa 1.034 departamentales, 5.030 de GENESIS y 15 de LexiVox. Esos números no son un nuevo inventario mío. El manifiesto de Gaceta no representa todo el corpus, y documentos, leyes, resoluciones y pasajes no son unidades intercambiables.

[COMPETENCIA.md](https://github.com/gatehot59-star/corpus-legal-tarija/blob/9ac92c8b4ca2b853d4ce04276d89d32fa3e84290/COMPETENCIA.md) ya corrige «nadie lo tiene»: reporta material tarijeño en aBOgacion. Su comparación histórica de 36 leyes contra 784 leyes y resoluciones tampoco justifica un multiplicador entre categorías distintas. No volví a contar ese repo externo.

**Conclusión:** tiene sentido defender profundidad local y facilidad de verificación; no decir «somos los únicos» ni «tenemos más que todos». Los sitios comerciales leídos en la investigación anterior muestran ofertas anunciadas, no su cobertura exhaustiva.

## 4. La procedencia es una ventaja en construcción, no una garantía completa

En [ocr_masivo.py](https://github.com/gatehot59-star/corpus-legal-tarija/blob/9ac92c8b4ca2b853d4ce04276d89d32fa3e84290/pipeline/ocr_masivo.py), hay verificación del archivo descargado y estados de fallo, pero la condición exacta es:

```python
if esperado and not esperado.startswith(real[:12]) and real != esperado:
```

No exige igualdad completa del SHA-256 y no rechaza un hash esperado ausente. Evaluación aislada de esa condición con cadenas sintéticas, ejecutada en el sandbox auxiliar, no en producción:

```jsonl
{"caso_sintetico": "igual", "hashes_iguales": true, "rechazado_por_condicion_de_ocr_masivo": false}
{"caso_sintetico": "mismo_prefijo_distinto_resto", "hashes_iguales": false, "rechazado_por_condicion_de_ocr_masivo": false}
{"caso_sintetico": "ausente", "hashes_iguales": false, "rechazado_por_condicion_de_ocr_masivo": false}
{"caso_sintetico": "distinto_prefijo", "hashes_iguales": false, "rechazado_por_condicion_de_ocr_masivo": true}
```

Esto prueba el alcance del predicado, no una colisión real, un PDF manipulado ni una explotación.

En la ingesta de main, `Documento.hash()` usa el hash recibido o calcula uno sobre el texto. El consumidor no recibe en ese campo una distinción explícita entre hash del PDF y hash del texto. Los adaptadores permiten una URL general de la Gaceta o GENESIS como respaldo; además, el registro que construye `ocr_masivo.procesar()` no copia `fuente_url`, que el adaptador de Gaceta busca después. En ese recorrido sin enriquecimiento intermedio, el enlace exacto se pierde y se usa el general.

**Por qué cambia la valoración:** exponer un campo `sha256` y un enlace no garantiza que un tercero pueda obtener los mismos bytes oficiales y reproducir la cita.

## 5. Parte de la mejor implementación está fuera de main

El [PR #1](https://github.com/gatehot59-star/corpus-legal-tarija/pull/1) sigue abierto. Su diff incluye `alias.py`, registro de múltiples procedencias, adaptación de Gaceta por manifiesto, fuente nacional y una frontera HTTP. Es más amplio que la breve descripción inicial del PR. Leí sus metadatos y parte del diff, no todas sus 32 modificaciones.

En main, el adaptador de Gaceta todavía recorre `corpus/texto/*.txt`; esa selección puede omitir textos de otra ubicación. La variante del PR aborda justamente ese problema usando el manifiesto como censo. En main, reingerir el mismo UID reemplaza documento y revisión; no está la tabla de alias del PR. Por eso no adjudico a main la preservación de todas las apariciones que describe esa rama.

**No concluyo que esas funciones estén ausentes del despliegue:** no comparé el servidor vivo con ambas revisiones. Los contratos de rutas documentados tampoco coinciden por completo con `servidor.py` de main. Código versionado, rama de trabajo y servicio desplegado siguen siendo sujetos distintos.

## 6. Honestidad de los límites suma valor, pero no reemplaza calidad jurídica

[gate_v2.py](https://github.com/gatehot59-star/corpus-legal-tarija/blob/9ac92c8b4ca2b853d4ce04276d89d32fa3e84290/pipeline/gate_v2.py) evalúa caracteres, basura, palabras plausibles y un ancla legal. Permite `APTO` si al menos la mitad de las páginas pasa y existe un ancla. No contrasta artículos, negaciones, montos o fechas con el PDF. **APTO significa pasar ese filtro, no exactitud jurídica certificada.**

La ingesta envía `vigencia_no_medida` a revisión y la API no convierte NULL en vigente. Es útil que la incertidumbre viaje con los datos. El [experimento de vigencia](https://github.com/gatehot59-star/corpus-legal-tarija/blob/9ac92c8b4ca2b853d4ce04276d89d32fa3e84290/mediciones/EXP-VIG-001-el-techo-de-la-vigencia-esta-medido-86-por-ciento-no-nombra-su-objeto.md) describe cláusulas genéricas que requieren interpretación. Su 86% corresponde a secciones abrogatorias clasificadas en ese experimento, no al 86% de toda norma boliviana ni a una prueba de imposibilidad universal.

No atribuyo vigencia completa, precisión superior a competidores, búsqueda semántica ni recall local medido a los archivos inspeccionados.

## Qué sostendría comercialmente

**Propuesta defendible como hipótesis:** documentación jurídica de Tarija preparada para búsqueda y reutilización, con fuentes rastreables, ambigüedades explícitas y procesamiento inspeccionable. El valor es hacer utilizable y revisable la fuente, no prometer que una IA sabe toda la ley.

El activo más difícil de reemplazar sería una colección local mantenida, con cobertura reconciliada contra las fuentes, citas que se puedan reconstruir y correcciones jurídicas revisadas. Hoy el código aporta parte de ese camino; mantenimiento efectivo, cobertura actual y revisión profesional no quedaron re-medidos.

Probaría el corpus como producto propio: búsquedas locales seleccionadas por profesionales, comparando tiempo total hasta verificar el documento, resultados relevantes, enlaces exactos, fecha y ambigüedades frente a Gaceta y alternativas. No compraría ni contactaría a nadie sin autorización; tampoco fijaría el precio solo por las tarifas de chats nacionales.

## Método y límites de esta reevaluación

Lectura directa por GitHub de fuentes de main, test de citas y workflow OCR; lectura de contexto y mediciones históricas; comprobación del único PR abierto devuelto y revisión parcial de su diff; evaluación local de una condición lógica con datos sintéticos, con salida cruda arriba. No hubo descarga masiva, OCR nuevo, consulta a la base viva, benchmark competitivo, dictamen de licencias ni cambios de código.

La independencia es del instrumento: esta tabla lógica es una reproducción propia, no una certificación externa. No se mergeó el PR ni se trasladaron funciones de Custos al corpus. La única escritura es este informe y su copia documental en ClickUp.
