# PaddleOCR-VL-1.6 contra el banco reservado: EN CURSO

15 de octubre de 2026. Operador BRAIN / GPT-6 Astra. Este es un punto de control, no un benchmark finalizado.

## Qué está corriendo

Primera corrida de PaddleOCR-VL-1.6 sobre las cinco páginas originales de las leyes 524 y 523, en la VM Ubuntu de Corpus, CPU de dos núcleos y sin GPU NVIDIA localizada. Se configura un hilo, batch 1, nice 10, backend nativo Paddle, sin MKL-DNN, sin orientación/unwarping y sin colas. Se observaron tres hilos del proceso durante la primera página.

Se descargaron los pesos públicos y el detector de layout fijando revisiones exactas. La VM conserva los otros entornos: el nuevo venv reutiliza sus paquetes mediante un .pth sin actualizarlos y añade 27 dependencias en su propio directorio. No se cambió el producto ni se publicó ningún peso.

## Medido hasta este punto

La carga terminó en 107,166697 segundos y el calentamiento en 36,201833 segundos. La imagen sintética de calentamiento no pertenece al banco y fue leída exactamente como `Prueba de lectura. No pagar 123 pesos.`. Ese resultado sólo demuestra inferencia básica, no precisión jurídica.

El sello se escribió a las 23:28:00 UTC (20:28 ART). La primera página empezó a las 23:30:24 UTC (20:30 ART). Todavía no se publican métricas del banco.

## Contrato congelado

Se verificaron los cinco hashes PNG y el hash de gold IA antes de ejecutar. La inferencia no consulta el texto de referencia; sólo su hash se comprueba antes de correr. La evaluación carga la referencia únicamente al terminar las cinco páginas.

Se conserva el orden nativo de parsing_res_list y todos los block_content, incluidos encabezados y pies. Sólo en bloques table se elimina markup HTML y se extrae texto en orden DOM sin expandir rowspan/colspan. No hay corrección ortográfica, máscaras manuales ni reconstrucción guiada por gold.

Máximo de generación: 4096 tokens por bloque. Timeout nominal: 1800 segundos por página, con SIGALRM; una operación nativa prolongada puede demorar la entrega de la señal a Python. No se convierte un timeout en texto vacío ni se publican métricas parciales como si cubrieran cinco páginas.

La referencia es doble transcripción visual y adjudicación por IA, no gold humano. Sólo hay dos documentos: no permite afirmar superioridad universal ni representatividad jurídica. No se corrieron otros motores sobre este banco en esta solicitud.

## Controles ejecutados

El adaptador de texto pasó cinco fixtures: texto literal, inclusión de encabezado/pie, tabla con celda combinada, signos literales fuera de tabla y entidades HTML. El evaluador previo pasó sus doce falsadores. Un segundo cálculo de distancia, Myers bit-parallel, coincidió con el DP del evaluador en 200 pares aleatorios sintéticos y cinco casos conocidos; aún no se aplicó a resultados reales de este banco.

## Evidencia y continuación

[Runner ejecutado y congelado](../evidencia/2026-10-15-13-paddle-vl16-run.py).

[Resumen del sello, hashes y configuración](../evidencia/2026-10-15-13-paddle-vl16-seal-summary.json).

Registro completo local en `/tmp/paddle-vl16-heldout-20261015` de la VM; copia de preparación en `/workspace/paddle-vl16-heldout-20261015` de brain-env. Leer `status.json`, `run.log`, `failure.json` si aparece y `scores.json` sólo al completar. No relanzar si hay proceso en curso. El runner guarda predicciones y tiempos por página y puntúa automáticamente al completar cinco.

El manifiesto histórico permanece `GOLD_PENDING`; no se lo interpreta como estado actual. El gold IA publicado después es el identificado por su hash en el sello. Este punto de control todavía no contiene toda la evidencia cruda en Git: no es una entrega de resultados finales.

TITAN LIGERO, diagnóstico aislado sin cambios de producto, credenciales, red pública nueva, merge o deploy. Revisión externa no realizada. PASS sólo para descarga, integridad, carga y calentamiento; precisión del banco NO MEDIDA todavía.
