# Geometría pura: columnas ordenadas sin volver a reconocer texto

15 de octubre de 2026. Operador: BRAIN / GPT-6 Astra. Pedido: «Run geometría only. Pero imprime en español lo estas haciendo en inglés». TITAN LIGERO, diagnóstico acotado, sin acción delicada, PR, merge ni despliegue.

## Resultado y decisión

Se procesaron las diez salidas originales de PaddleOCR simple. El control de dos columnas pasó de **689 a 0 ediciones de caracteres**, sin cambiar ninguna cadena reconocida. El control inclinado y desenfocado conservó **0 errores**, a diferencia del brazo PP-StructureV3 que había introducido 266. El control de 150 dpi conserva una coma ausente: un reordenador no puede recuperarla.

**La alternativa geométrica resolvió este caso de columnas sin repetir la regresión anterior. No está validada para producción.** Se conservaron exactamente las 326 unidades de texto, una vez cada una. Las seis páginas reales también cambiaron de orden, pero no existe transcripción independiente para establecer si ese cambio fue correcto. Preservar palabras no garantiza preservar su relación jurídica.

Es una regresión post hoc sobre cuatro controles ya vistos de un único texto, no una prueba ciega ni held-out. Los siete fixtures geométricos nuevos son pruebas unitarias construidas, no páginas nuevas reconocidas por OCR.

## Qué se ejecutó

La función `order(polys)` recibe exclusivamente los polígonos originales `rec_polys`. No recibe textos, referencia, identificador del caso ni puntuaciones. Devuelve una permutación de índices; después se aplica esa permutación a `rec_texts` y se unen las unidades con saltos de línea. No hubo recortes, reconocimiento adicional, diccionarios, corrección ortográfica, descarte de cajas ni consulta lingüística para decidir el orden.

Heurística fijada antes de la corrida:

1. Estimar el ángulo mediano del borde superior de los polígonos y desinclinar coordenadas. Si supera 15 grados absolutos, no corregirlo y registrarlo.
2. Buscar cortes verticales vacíos de al menos 1,5 alturas medianas de línea, con al menos dos elementos a cada lado; leer izquierda antes que derecha.
3. Si no hay corte vertical válido, buscar cortes horizontales vacíos de al menos 0,5 alturas; leer arriba antes que abajo.
4. Si no hay corte, agrupar por altura con tolerancia 0,5 y ordenar por posición horizontal.

La regla es geométrica, no infalible. Tablas, notas marginales, títulos que atraviesan columnas, cajas solapadas, bloques de una sola línea, escritura no horizontal o diseños sin un canal blanco suficiente pueden inducir un orden incorrecto. No existe un detector validado de ambigüedad ni una abstención automática de calidad. El caso unitario de título ancho no demuestra cobertura de todos los títulos.

Python 3.12.14 y biblioteca estándar en brain-env. No se instaló nada. No se usó la VM para nueva inferencia: se leyeron sus resultados previos ya preservados en brain-env. No se tocó Corpus, su base, servicios, modelos ni configuración.

## Resultados de los controles

Referencia por variante: 912 caracteres normalizados y 147 palabras. Normalización: NFC y colapso de blancos; se preservan puntuación, tildes y mayúsculas. Fuente original del texto: https://www.lexivox.org/norms/BO-L-N439.xhtml .

| Control | Paddle simple: ediciones de caracteres | PP-Structure anterior | Geometría: ediciones de caracteres | CER geométrico | Ediciones de palabras geométricas |
|---|---:|---:|---:|---:|---:|
| Limpio | 0 | 2 | 0 | 0 % | 0 |
| Inclinado, blur y ruido | 0 | 266 | 0 | 0 % | 0 |
| 150 dpi | 1 | 2 | 1 | 0,109649 % | 1 |
| Dos columnas | 689 | 3 | 0 | 0 % | 0 |

En dos columnas, WER pasó de 112/147 a 0/147. En 150 dpi permanece 1/147, 0,680272 %. Los otros dos controles permanecen exactos bajo la normalización declarada. El control inclinado conserva «no podrán» y «por sí mismos»: no se sustituyó su texto por el del brazo layout.

Agregado descriptivo de estos cuatro controles: 1/3648 caracteres y 1/588 palabras. No representa exactitud del corpus jurídico ni generalización. No se ajustó el algoritmo después de consultar los resultados de esta corrida.

## Tiempo de posprocesado, no de OCR

| Caso | Unidades | Segundos de geometría | Cambió orden |
|---|---:|---:|---|
| d01-p001 | 73 | 0,002802841 | Sí |
| d01-p003 | 55 | 0,003337682 | Sí |
| d02-p001 | 42 | 0,001234904 | Sí |
| d02-p002 | 29 | 0,000915027 | Sí |
| d03-p001 | 30 | 0,001035819 | Sí |
| d03-p020 | 40 | 0,002532896 | Sí |
| c01-clean | 12 | 0,000541937 | No |
| c02-skew-blur | 12 | 0,000367418 | No |
| c03-150dpi | 12 | 0,000488643 | No |
| c04-two-columns | 21 | 0,000736274 | Sí |

Total diez casos: **0,013993441 s**, unos 14 ms. Seis reales: 0,011859169 s. Se cronometró únicamente `order(polys)`, no lectura, escritura, puntuación ni OCR. Una pasada en brain-env, sin aislamiento ni repetición estadística. No sumar estos tiempos a los 125,9 s anteriores como si se hubiera medido un pipeline integrado en la misma máquina.

## Instrumentos y falsadores

Sello: 2026-10-15 13:07:04,525771 UTC. Fin: 13:07:10,614335 UTC. Comando ejecutado, exit 0:

```sh
python3 /workspace/ocr-geometry-20261015/geometry.py /workspace/ocr-ab-20261015-0foi89wk/results-v2 /workspace/ocr-geometry-20261015/run1
```

Siete fixtures pasaron: una columna, dos columnas, título ancho, tres columnas, entrada vacía y rotaciones de -7 y +7 grados. Tres mutaciones fueron rechazadas por el validador de permutación: duplicar índice, omitirlo y cambiar una cadena.

Un verificador separado, `verify.py`, corrió con exit 0 a las 13:08:11 UTC. Leyó los JSON originales, verificó igualdad de todos los textos y polígonos, comprobó las diez permutaciones, reconstruyó cada archivo de salida y verificó sus hashes. Recalculó 16 distancias mediante matriz completa, distinta de las dos filas usadas por el instrumento. Exigió métricas nulas para los seis escaneos reales.

Además, cinco copias manipuladas del registro fueron rechazadas: índice duplicado, índice omitido, texto alterado, score falseado y caso eliminado. Los originales no fueron modificados. El mismo operador ejecutó ambos instrumentos: **no es una auditoría externa**, ni una selección independiente de la muestra.

## Evidencia y reproducibilidad

[Script ejecutado](../evidencia/2026-10-15-05-ocr-geometria.py) y [evidencia seleccionada](../evidencia/2026-10-15-05-ocr-geometria.json).

El JSON publicado contiene texto y polígonos originales de los cuatro controles, referencia, permutaciones, puntuaciones, hashes y tiempos de los diez casos, además de stdout/stderr completos de ejecución y verificación. Permite recomputar el orden y CER/WER de los controles. Los textos y geometrías completos de las seis páginas reales, trazas recursivas y fuente del verificador se conservan en brain-env, no se incluyen todos en Git.

Para recomputar un control con los archivos publicados: cargar el módulo mediante `importlib.util`, leer el JSON, llamar a `order(caso['polys'])`, comparar con `caso['permutation']`, unir `caso['texts'][i]` y calcular distancia contra `reference`. La ejecución completa de `run` requiere el banco y los raw preservados; no se presenta como paquete autónomo con PDFs y modelos incluidos.

Custodia: `/workspace/ocr-geometry-20261015`. Baseline: `/workspace/ocr-ab-20261015-0foi89wk/results-v2`. Banco y diez raw originales permanecieron idénticos por SHA-256.

| Artefacto | SHA-256 |
|---|---|
| Script ejecutado | `b65a0089322af8bb1d9ca0fbaab798fb3dd4c4a8f1b4a4b03160de26ad64f4ad` |
| Banco original | `cc8abf3c3f26674fe3547fa3687ec4f9e7796ce4051bf8f406a5f6aad49e31ab` |
| Registro completo | `2326681202afe24a41cb3db241c6a3662d5ece0502a8e9b123d2b5c574358797` |
| Verificador separado | `e23cbf3329cede7d663a756601c108e3159c68503196764c12ac3e35426ec8c4` |
| JSON publicado | `71535272d186a6d1785424271a0fd5afc6c5484795ef21075b4541831cf63aae` |

Error propio de preparación: se intentó escribir el script antes de crear la carpeta. La escritura falló; se creó una carpeta nueva y se repitió, sin afectar originales ni resultados.

## Veredicto acotado

**PASS:** ejecución diez casos, conservación exacta de las 326 unidades, controles recalculados y rechazo de manipulaciones; columnas sintéticas corregidas sin regresión en los otros tres controles.

**FAIL residual:** falta una coma en el OCR de 150 dpi, que la geometría no pretende reparar.

**NO MEDIDO:** exactitud y orden correcto de escaneos reales, generalización a páginas no vistas, tablas, casos ambiguos, beneficio integrado y preparación para producción.

La decisión es conservar este candidato para evaluación con referencias reales y nuevas páginas, no promoverlo automáticamente. ABBYY y los diez casos jurídicos Corpus/RuleX no se ejecutaron en este pedido.

Antecedentes: [Paddle simple/Tesseract](https://github.com/gatehot59-star/corpus-legal-tarija/blob/141a9103fc4442413ed6ec16eab592ecd9804fd2/docs/agents/respuestas/2026-10-15-03-tesseract-paddleocr-medidos.md) y [PP-StructureV3](https://github.com/gatehot59-star/corpus-legal-tarija/blob/c544655d70107d81e1b661940aabbda88a278e86/docs/agents/respuestas/2026-10-15-04-paddleocr-layout.md). Se leyó el informe vivo antes de actuar; entrega en rama documental existente, no en `main`.
