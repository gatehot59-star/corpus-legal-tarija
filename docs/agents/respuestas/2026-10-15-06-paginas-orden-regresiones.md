# Revisión de las seis páginas reales: salto espurio del margen en dos páginas

15 de octubre de 2026. Pedido: «Detectá qué páginas reales quedaron peor ordenadas». Operador: BRAIN / GPT-6 Astra, el mismo que implementó y ejecutó el experimento. Esto es un diagnóstico propio, **no una auditoría independiente**.

## Respuesta precisa

**Las páginas 1 y 3 de la Ley Departamental 522 presentan una nueva anomalía:** un carácter aislado del margen inferior izquierdo, reconocido como `C` o `D`, pasó a ser el primer texto no vacío de la página, por delante del encabezado. Casos `d01-p001` y `d01-p003`.

Esto identifica un defecto local del ordenamiento, no demuestra que toda la página haya empeorado en términos netos. En esas mismas páginas se agruparon mejor algunos incisos y bloques del pie. Sin referencia independiente no asigno una puntuación global de calidad ni un CER real.

**No encontré evidencia de nuevo desorden del cuerpo normativo en las otras cuatro páginas.** No equivale a aprobar su exactitud: el OCR original ya contiene errores, sellos y firmas ilegibles. En la página 20 de resoluciones, el área de firmas sigue siendo ambigua.

## Qué se revisó y qué no

Se leyeron las 269 unidades OCR de las seis páginas reales, incluidas las vacías, sus polígonos originales, la permutación aplicada y la traza de cortes. Se comprobó SHA-256 de los seis JSON contra el registro original y la igualdad de sus textos. Se leyó el script desde el commit `ac9abcdfac760d8a8d0d5d0292d4d9096cf7c9a6` y se comprobó igualdad byte a byte con el examinado en brain-env.

La revisión se basa en coordenadas, cadenas y secuencias antes/después. **No se hizo una nueva inspección visual de los PNG ni una transcripción independiente.** La interpretación semántica de los cambios es del mismo operador, no un ground truth externo. Los hashes validan identidad de insumos, no su fidelidad al papel.

No se cambió el algoritmo ni se sobreescribieron resultados. Se ejecutó una ablación de diagnóstico en memoria para aislar el desencadenante de la anomalía; no se publicó como solución ni se aplicó a Corpus.

## Hallazgo principal: una caja vacía activa una falsa columna

### Ley 522, página 1: d01-p001

Unidades originales relevantes, índices desde cero:

```text
0   texto=""   caja=[161,49,182,69]
1   texto="ASAMBLEA LEGISLATIVA"   caja=[1054,462,1447,515]
52  texto="emergencias."   caja=[467,3035,744,3076]
53  texto="C"   caja=[136,3055,223,3141]
54  texto="f)"   caja=[393,3080,463,3125]
55  texto="Solidaridad. Acción voluntaria y desinteresada orientada al auxilio, apoyo y protección de la"
```

Antes: el encabezado precedía al cuerpo; `C` aparecía entre la continuación del inciso e) y el inciso f). Después: la secuencia arranca `[0,53,1,2,3,...]`, por lo que el primer texto no vacío es `C`, luego `ASAMBLEA LEGISLATIVA`. La marca situada a y=3055 fue promovida al comienzo.

Traza medida: primer corte vertical en x=266,5, canal vacío de 87 px. Su lado izquierdo contiene sólo la caja vacía 0 y el carácter marginal 53. Como el algoritmo exige al menos dos cajas a cada lado y cuenta también las vacías, acepta ese par como columna.

Ablación: se llamó al mismo `order` con todos los polígonos menos el 0, sin alterar el código ni los archivos. Tras mapear los índices al original, `C` dejó de encabezar: volvió entre 52 y 54. Su posición pasó de 1 a 52, con un elemento menos en la entrada. El primer corte pasó a ser horizontal, y=3649,5. Esto identifica el papel causal de la caja vacía en este caso concreto.

También hay cambios favorables aparentes: 1. y 2. pasan antes de sus frases; c) antes de Ética; teléfono/fax, web/localidad y dirección quedan agrupados por bloques. Por eso no se declara empeoramiento neto de toda la página.

### Ley 522, página 3: d01-p003

```text
0   texto=""   caja=[145,53,165,73]
3   texto="ASAMBLEA LEGISLATIVA"   caja=[1045,461,1437,513]
42  texto="ARTÍCULO 12. (RESPETO COMPETENCIAL). -"   caja=[330,2974,1247,3031]
43  texto="D"   caja=[91,3004,190,3086]
44  texto="I. La presente Ley no crea una estructura pública bomberil departamental."
```

Antes: `D` estaba entre el título del artículo 12 y su apartado I. Después: secuencia `[0,43,1,2,3,...]`; `D` se convierte en el primer texto no vacío de la página, por delante de la detección `I` del encabezado y del nombre de la Asamblea.

Traza: corte vertical inicial x=254, canal de 128 px; lado izquierdo formado por las cajas 0 y 43. Al retirar sólo la caja vacía 0 en memoria, `D` vuelve entre 42 y 44; pasa de posición 1 a 42 en una entrada de tamaño reducido. Primer corte de la ablación: horizontal y=327,5.

En ambos casos se demuestra un salto espurio del margen a la cabecera. No se ha determinado visualmente qué representan C y D en el escaneo, ni si deben suprimirse. **No borrar caracteres automáticamente a partir de este diagnóstico.**

## Cobertura de las seis páginas

| Página | Diferencia relevante | Evaluación acotada |
|---|---|---|
| Ley 522, p. 1 (`d01-p001`) | C del margen inferior pasa al principio; incisos y pie también se reagrupan | Nueva anomalía de cabecera confirmada; balance global NO MEDIDO |
| Ley 522, p. 3 (`d01-p003`) | D del margen inferior pasa al principio; pie agrupado por bloques | Nueva anomalía de cabecera confirmada; balance global NO MEDIDO |
| Ley 005/2010, p. 1 (`d02-p001`) | e) pasa delante de «El Órgano Ejecutivo deberá presentar…»; una caja vacía cambia de lugar | Cambio coherente con inciso y coordenadas; sin regresión nueva identificada |
| Ley 005/2010, p. 2 (`d02-p002`) | Firma izquierda [23,25,27] seguida por derecha [24,26,28], en vez de entrelazar ambas | Agrupación coherente de nombre/cargo/institución; cuerpo normativo idéntico |
| Resoluciones, p. 1 (`d03-p001`, R.A. 266) | Sólo se intercambia una caja vacía con un fragmento de firma | Secuencia de textos no vacíos exactamente igual; no empeoramiento textual por orden |
| Resoluciones, p. 20 (`d03-p020`, R.A. 284) | Cambia sólo bloque de firmas [28..37], incluyendo «Justino» antes de «Zambrand Cachari» | Cuerpo normativo idéntico; calidad global de firmas NO MEDIDA por OCR roto |

En d02-p002, los textos OCR, no nombres validados, son «Justino Zambrana Cachari / Vicepresidente / Asamblea Legislativa Departamental Tarija» y «José AmásVeliz / Secretario / Asamblea Legislativa Departamental Tarija». El reordenamiento reúne cada bloque espacial, no los mezcla.

En d03-p020, el nombre y otros fragmentos ya estaban corruptos. El cambio agrupa izquierda/derecha y coloca «Justino» antes de «Zambrand Cachari», pero no permite validar la identidad ni el cargo de las firmas ilegibles. No atribuir a la geometría corrupción textual que ya estaba en el OCR.

## No confundir movimiento con error

Pares de unidades no vacías que invirtieron su orden respecto del original: 58, 44, 1, 3, 0 y 9 respectivamente, en el orden de la tabla. **No son errores ni una métrica de calidad.** Incluyen arreglos de incisos y agrupaciones de firmas. En particular, decir que las seis páginas cambiaron era cierto para los índices, pero no para la secuencia de texto no vacío: d03-p001 sólo movió un vacío.

## Qué no midió el ensayo anterior y sí importaba

El verificador anterior garantizaba permutación exacta, conservación de cadenas y métricas sintéticas. **No podía rechazar una falsa columna formada por una caja vacía y una marca marginal**, porque ambas se conservaban correctamente. La integridad era real, pero insuficiente para establecer buen orden de lectura en páginas reales. Es el hueco concreto del instrumento; no contradice el cero medido en el control sintético.

## Recomendación, no implementación

Antes de integrar: separar la elegibilidad de una caja para decidir cortes de su conservación en la salida, exigir evidencia espacial suficiente de columna y evaluar casos de margen/sellos contra referencia independiente. La ablación demuestra el desencadenante, pero quitar vacíos no es una solución validada ni cubre otros diseños. Conservar salidas originales y rastreo por índice.

**PASS:** reproducción de la promoción marginal y desaparición al retirar el ancla vacía en dos ablaciones; cobertura de seis secuencias. **FAIL:** detección de columna confunde un par disperso, uno vacío, con una columna de lectura. **NO MEDIDO:** balance de calidad global, exactitud real, naturaleza visual de marcas, oro independiente de firmas y generalización de una solución.

## Custodia y método

Resultados completos y pares invertidos: `/workspace/ocr-order-review-20261015/measured.json`; selección: `published.json`, SHA-256 `e985640eccd650b34a10838ea5d49315339f19bd88feff5441f83867064e5088`. Se preservan en brain-env. Este informe publica coordenadas, índices, cortes y resultados de ablación necesarios para localizar ambos hallazgos; no todos los raw ni PNG.

METODO TITAN: LIGERO; diagnóstico propio acotado, no auditoría independiente. Herramientas: Python y Git en brain-env. Comandos de comparación/ablación terminaron con exit 0; no se añadió script de producto. Sin modificación de main, PR, despliegue, modelos, baseline ni algoritmo. No se otorga puntuación de rúbrica de producción ni aprobación externa.

[Experimento examinado y enlaces a script/evidencia](https://github.com/gatehot59-star/corpus-legal-tarija/blob/ac9abcdfac760d8a8d0d5d0292d4d9096cf7c9a6/docs/agents/respuestas/2026-10-15-05-ocr-geometria.md).
