# Comparación visual de páginas 1 y 3 de la Ley 522

15 de octubre de 2026. Pedido: «Compará visualmente las páginas 1 y 3». BRAIN / GPT-6 Astra, mismo operador del experimento, no auditoría independiente.

## Qué muestra la imagen

Ambas hojas tienen un cuerpo principal de **una sola columna**, encabezado centrado y grupos separados en el pie. La página 1 es más densa; la página 3 presenta más separación entre bloques. Las vistas generales son reducidas: sirven para inspeccionar estructura, no para transcribir el contenido.

En el margen izquierdo inferior de ambas hay un **trazo aislado e irregular**, separado del texto normativo. El recorte de página 1 lo sitúa a la izquierda del tramo con incisos e), f), g). El de página 3 lo sitúa a la izquierda de un título que empieza «ARTÍC…» y los apartados I y II. La identificación de ese título como artículo 12 proviene del OCR previo y sus coordenadas, no de una transcripción completa del recorte.

Los trazos no constituyen una segunda columna ni forman parte visual del encabezado. No puedo determinar sólo con estos recortes si son anotación manual, marca de reproducción u otro artefacto, ni validar que deban leerse como letras C y D: **C y D son las etiquetas que produjo PaddleOCR**, no una identificación visual segura.

## Antes y después

| Página | Situación en el escaneo | Salida original de Paddle | Salida geométrica |
|---|---|---|---|
| 1 | Trazo aislado en margen inferior, al lado de los incisos | Unidad 53, reconocida como C, próxima a esa zona de la secuencia | Primera unidad no vacía, antes de ASAMBLEA LEGISLATIVA |
| 3 | Trazo aislado en margen inferior, junto al bloque del artículo 12 según OCR | Unidad 43, reconocida como D, entre título y apartado I | Primera unidad no vacía, antes de las detecciones del encabezado |

La comparación visual respalda el hallazgo previo: **el salto al encabezado no representa la posición de las marcas en la página**. El reordenador conservó las cadenas, pero inventó una agrupación de lectura como columna izquierda. La imagen original no fue alterada; lo que cambió fue el orden del texto extraído.

No se demuestra empeoramiento neto de toda la página ni exactitud del cuerpo normativo. Ya había cambios favorables aparentes en incisos y pies. No se midió CER real ni se transcribió cada línea.

## Evidencia visual examinada

Se recuperaron desde la VM los dos PNG exactos del banco, sin volver a rasterizar el PDF:

- Página 1: 2514 × 3921 px, 5.195.082 bytes, SHA-256 `66a24dab854cefb406318e67536119858581c584d4bc53fdded8d446cd2ca4e9`.
- Página 3: 2511 × 3879 px, 4.194.962 bytes, SHA-256 `e011d9efda1a6d680e59d65f8df6b1c864fd99fb4b3c0d1d61794f2923757ebc`.

Los hashes coincidieron con los del banco original antes de preparar las vistas.

La inspección efectiva se hizo sobre vistas generales de 160 px de ancho y recortes a escala original de 400 × 300 px, rectángulo `(50,2920,450,3220)`. Derivados convertidos a gris y binarizados: umbral 210 en vista general y 165 en recortes. Esa transformación puede omitir trazos débiles: **no es una inspección exhaustiva del original en gris ni una referencia gold**. Las vistas mayores preparadas no se consiguieron abrir mediante el visor remoto.

Recortes efectivamente vistos:

- [Margen de página 1](https://u228265714.p.clickup-attachments.com/u228265714/eac0fae8-d33b-56b7-84cb-2ae0df01b5a3/pagina-1-margen.png?view=open).
- [Margen de página 3](https://u228265714.p.clickup-attachments.com/u228265714/9762e63f-b40d-5961-9ee7-152b822eb73c/pagina-3-margen.png?view=open).

Vistas generales efectivamente vistas:

- [Página 1, estructura general](https://u228265714.p.clickup-attachments.com/u228265714/6223e12c-c748-5be7-9fd4-9521d9704348/pagina-1-general.png?view=open).
- [Página 3, estructura general](https://u228265714.p.clickup-attachments.com/u228265714/d32d78e1-a707-5ec8-907a-757f8220a7ef/pagina-3-general.png?view=open).

Estos enlaces son adjuntos de ClickUp; pueden requerir acceso. No se commitearon binarios derivados.

## Recuperación del entorno y límites

El visor de archivos falló primero con conexión cerrada y luego sin conexión. El navegador alternativo no pudo conectar con su sesión. El Python del host no tenía Pillow; se generaron los derivados con Pillow ya disponible en brain-env y se transfirieron en base64 al sandbox para verlos. Un intento inicial de umbral falló por modo de imagen; se convirtió explícitamente a gris y se repitió. Las imágenes que sí fueron abiertas quedaron adjuntas. No se instalaron paquetes ni se inició infraestructura nueva.

Originales y derivados preparados quedan en `/workspace/ocr-visual-20261015` y copias del host en `/home/estudiante/ocr-visual-20261015`. No se modificaron baseline, algoritmo, modelos ni producción.

**CONFIRMADO visualmente:** trazos marginales aislados y cuerpo principal a una columna; no son un encabezado ni una columna textual del margen.

**CONFIRMADO por secuencias previas:** ambos trazos reconocidos como C/D fueron adelantados al primer texto no vacío.

**NO MEDIDO:** naturaleza exacta de los trazos, fidelidad de cada palabra, contraste completo en gris, conveniencia de suprimir marcas y calidad global antes/después.

Recomendación: conservar las marcas y su procedencia separadas del cuerpo; evitar que cajas vacías o marcas aisladas decidan columnas. Es recomendación, no corrección implementada ni validada.

METODO TITAN: LIGERO, diagnóstico propio acotado sin acción delicada. Instrumentos: hashes, Pillow, inspección visual de los cuatro derivados citados y comparación con secuencias originales. Sin auditor externo, rúbrica de producción, merge ni despliegue.

[Diagnóstico previo de las seis páginas](https://github.com/gatehot59-star/corpus-legal-tarija/blob/eb7957f8f9906d271e0b6656f23090f618a0211f/docs/agents/respuestas/2026-10-15-06-paginas-orden-regresiones.md).
