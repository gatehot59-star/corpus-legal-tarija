# OCR: pruebas adversariales de las cinco tareas en curso

Fecha: 22-oct-2026, ART. Operador: BRAIN, modelo GPT-6 Astra. Encargo: ejecutar pruebas adversariales, no corregir producto, desplegar ni cambiar estados.

## Resultado

La suite del autor pasa 47/47. El instrumento nuevo ejecuta 45 comprobaciones: 38 PASS y 7 FAIL. Una segunda corrida en temporales nuevos produce exactamente los mismos registros. Son 45 comprobaciones únicas, no 90 pruebas independientes.

Los siete rojos representan cinco defectos de contrato/operación y dos límites de cobertura. No equivalen a siete vulnerabilidades remotas. Ninguna de las cinco tareas queda aprobada integralmente por este banco.

## Sujeto y entorno

Repo gatehot59-star/corpus-legal-tarija, rama titan/ocr-vl-sidecar-20261022, revisión 5a108c028792b409974b00ebe04be5e1215f9029. Archivo sistema/ocr_sidecar/ocr_service.py, SHA256 ba6319aed537f601745e9d54c1156ce5ee2dd3da500581a94347fc4b64ce5e0f, coincidente entre Git, copia de pruebas y archivo montado.

Pruebas en sandbox aislado con Python, Pillow, pypdf y Poppler real. No se ejecutó inferencia nueva de Paddle ni se modificó la VM. Brain-env se usó para lectura de Git y SSH de sólo lectura. Consulta final: corpus-ocr-vl, corpus-api y corpus-django-staging activos; NRestarts del OCR 0.

Main antes de publicar: c273c659ee90f2259f540cb14c576d6a16dcfb40. La rama de producto no cambió durante la medición. PRs abiertos revisados por identidad: 32, 31, 30, 27 y 1; ninguno es una corrección posterior de esta rama OCR. El recibo del montaje ya declaraba las deudas de SIGKILL y progreso: no son descubrimientos nuevos.

## Cinco defectos reproducidos

1. **Alta, contenido híbrido dentro de una misma página.** Un PDF sintético tiene más de 200 caracteres nativos y una imagen incrustada con la cláusula `NO PAGAR Bs20.000.000`. `prepare_pages(auto)` elige sólo texto nativo y no renderiza esa página; el texto nativo no incluye la cláusula. El control digital elige nativo; el escaneado elige OCR; `ocr` forzado sí renderiza el PDF mixto. Esto no contradice la prueba anterior de páginas digitales y escaneadas separadas: es otro caso. Cierre: conservar la región raster o señalar la omisión potencial y evitar presentar esa ruta como conservación completa.

2. **Alta, vacío que el contrato acepta.** Una página declarada no blanca con un bloque cuyo texto es vacío pasa `complete_document`. El positivo con `NO PAGAR` pasa y el mutante sólo vacía el texto del bloque y de la página. Se acepta como `requires_review` en vez de rechazarse como salida vacía. No demuestra que Paddle haya generado ese vacío en una corrida real. Cierre: el mismo caso debe producir `empty_nonblank_output`, manteniendo el blanco explícito válido.

3. **Media, progreso final obsoleto.** El worker real de una página digital termina con `result.completed_pages=1` y deja `progress.completed_pages=0`. No hay modelo doble en el parser; sólo se sustituyen la verificación de instalación y lectura YAML para aislar el flujo nativo. Cierre: progreso terminal coherente con el resultado, tanto en éxito como en fallo parcial.

4. **Media, SIGKILL se etiqueta timeout sin vencer el plazo.** Un hijo real se envía SIGKILL antes del plazo de un segundo. El supervisor conserva exit -9 pero informa timeout. Control: un hijo que duerme 30 segundos sí agota el plazo de 0,15 segundos y es terminado por el supervisor. Esto reproduce la confusión de señales; no provoca ni mide OOM. Cierre: informar timeout sólo si venció el plazo y separar señal de causa desconocida.

5. **Media, salida agregada contradictoria aceptada.** Con páginas válidas `NO PAGAR`, un worker de prueba entrega texto agregado `PAGAR` y `fidelity_certified=true`; el supervisor acepta `requires_review`. El positivo consistente también pasa. Se inyectó un resultado del worker, no una carga HTTP de un atacante. Es defensa adicional ante bugs o corrupción del worker confiable, no bypass remoto demostrado. Cierre: validar el esquema final, coherencia del texto agregado y prohibición de certificación.

## Dos límites de cobertura, no nuevos exploits

- `check_reference` verifica presencia, no multiplicidad: dos referencias idénticas `NO AUTORIZADO` pasan aunque la salida conserve una sola. El control con ambas ocurrencias pasa. La prueba demuestra que este banco no detecta toda omisión, no que su docstring prometiera conteo.
- `eligible_native` acepta `XYZQWERTY` repetido como capa útil. Rechaza el carácter de reemplazo corrupto. Es el límite conocido de la heurística de longitud/alfabéticos, no una prueba de fidelidad semántica.

## Resultado por tarea

- [Integración VL](https://app.clickup.com/t/86e3v02ya): PASS acotado para rechazo de revisión y pesos alterados, y para no etiquetar VL una extracción nativa. Paquetes y pesos sintéticos en pruebas de manifiesto. Motor real nuevo, baseline seleccionable y reversión integral: NO MEDIDO.
- [Regresiones jurídicas](https://app.clickup.com/t/86e3v02y7): el positivo pasa y mutantes de monto, negación, fecha, artículo, nombre y omisión son rechazados. FAIL de cobertura para multiplicidad. Son referencias sintéticas, no gold humano ni revalidación visual completa de Ley 151.
- [Protección](https://app.clickup.com/t/86e3v02ye): PASS para copia interrumpida, truncamiento, firma falsa, tamaño, modo inválido, limpieza de admisiones fallidas, cola llena y PDF malformado; FAIL para bloque vacío y clasificación de SIGKILL.
- [PDF híbrido](https://app.clickup.com/t/86e3v02y6): PASS en clasificación de PDF digital, escaneado y blanco, ruta forzada y detección de carácter corrupto; FAIL en mixto dentro de página y límite alfabético.
- [Procedencia y disponibilidad](https://app.clickup.com/t/86e3v02y8): PASS para cambio de configuración tras admisión y resultado nativo; FAIL para progreso terminal y agregado contradictorio. Disponibilidad frente a todos los fallos reales de importación/modelo: NO MEDIDO.

## Instrumento, reproducción y custodia

La evidencia hermana `evidencia/2026-10-22-03-ocr-adversarial.json` contiene un paquete de texto JSON comprimido XZ y codificado base64. Decodificar `data`, descomprimir XZ, verificar longitud y SHA256 y leer el JSON. Incluye el script exacto adversarial.py, stdout/stderr completo de la suite del autor y ambos registros/logs nuevos. Cada archivo tiene su hash.

Recuperar ocr_service.py y las pruebas del autor desde la revisión congelada en una carpeta subject. Ejecutar `python -m unittest -v` allí. Ejecutar luego `python adversarial.py --subject subject --out run.json`. Código de salida esperado del instrumento nuevo: 1 por los hallazgos, no por error de ejecución. No usar ese exit como único oráculo: cada caso conserva esperado/observado.

Los fixtures propios se generan desde el script, sin originales privados. Los temporales se eliminan; los procesos se esperan y los hilos se unen explícitamente. No se guardan credenciales, variables de entorno, argumentos SSH ni datos privados. No se alteró código productivo para hacer pasar el banco.

La independencia aquí reside en entradas y expectativas fijadas fuera del productor. El mismo operador hizo la revisión y ejecución; no es revisión externa ni una instancia independiente por nombre.

Errores del instrumento/entorno conservados: una consulta inicial de metadatos del gateway tuvo un paréntesis faltante y no ejecutó; se corrigió. El transporte de la suite del autor emitió una advertencia RPC, pero el log completo en disco registra 47 tests OK. Las dos corridas adversariales finalizaron y devolvieron 1 por los mismos siete hallazgos.

## Qué no se midió que importaba

Inferencia nueva con VL real; exactitud jurídica o CER/WER; gold humano; comportamiento visual de toda capa corrupta; autenticación con otro UID real; aislamiento systemd bajo ataque; concurrencia de modelos y memoria; auditoría transitiva de dependencias; presión sostenida; reversión final a Tesseract. No se reejecutaron auditorías históricas de PR7 a PR11, fuera de este consumidor.

## Gates y cierre

- Gate I, instrumento: PASA en el alcance declarado. Positivos, mutantes pertinentes, repetición en scratch nuevo, resultados adversos y recursos cerrados. Pruebas de modelo real: NO MEDIDO.
- Gate II, informe: PASA acotado. Cinco defectos y dos límites separados; causa, precondiciones, controles y aceptación explicitados. Sin aprobación global ni nota inventada.
- Gate III, entrega: verificar publicación y bytes de vuelta en el cierre del Doc. El envío de un reporte a Nexus requiere aprobación separada y no se ejecutó. Por esa omisión declarada, el protocolo de cierre completo permanece INCOMPLETO aunque Git y Doc se publiquen.

No se cambiaron los cinco estados en curso, no se reparó producto, no se hizo merge de código ni despliegue. Siguiente trabajo recomendado: primero preservar imágenes de páginas mixtas y rechazar bloques vacíos; después arreglar progreso, señales y coherencia del resultado final.
