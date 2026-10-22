# Corpus: qué existe y qué está mal en la propuesta OCR

22-oct-2026. Auditoría del documento pegado por Abraham, no implementación. Operador: Astra; revisión documental, inspección de código y pruebas aisladas por el mismo operador, sin revisión externa.

## Veredicto

Sí: Corpus ya tiene extracción de texto nativo, OCR Tesseract, reintentos de orientación, citas normalizadas, procedencia y búsqueda. PaddleOCR-VL-1.6 está probado experimentalmente. No encontré la integración de VL, MinerU, Surya o GLM ni el microservicio propuesto en las rutas inspeccionadas. El documento no puede tomarse como código corregido ni como diseño validado para producción.

El defecto de mayor impacto es que el ejemplo llamado VL instancia otro pipeline y devuelve únicamente la primera página. La prueba aislada conserva una página y pierde la negación y el monto de la segunda, aunque declara dos páginas procesadas. No se ejecutó el servicio ni una inferencia nueva.

## Sujeto y alcance comprobados

Main de Corpus: `c273c659ee90f2259f540cb14c576d6a16dcfb40`. Rama documental inicial: `18fc28c080aee086bb07bf34f5d9b83f3c673b19`. Los cinco PR abiertos consultados son auditoría, UI, navegación, CSRF y procedencia; sus títulos no acreditan implementación OCR.

En la VM están activos corpus-api y corpus-django-staging. El proceso API ejecuta api.py; Django sirve config.wsgi:application. El checkout de staging es `c0e44af31a54bc2f0ba8304fc6572467082b69d6`, distinto de main. Se inspeccionaron rutas, lector, dependencias y 71 archivos Python de sistema/pipeline: hay benchmarks PP-OCRv5, no una integración VL. El archivo ocr_masivo.py coincide por SHA256 con main. Esto acredita archivos y procesos observados, no el recorrido HTTP público ni los módulos que el proceso ya tenía cargados en memoria.

## Qué ya existe

1. **CONFIRMADO, código en main:** selección de texto nativo frente a OCR en genesis_bajar.py: acepta pdftotext cuando supera 200 caracteres por página promedio. Es una heurística documental, no detección fiable de cada página híbrida ni prueba de que la capa textual sea correcta.
2. **CONFIRMADO, código en main y copia VM:** rasterizado a 300 dpi, Tesseract spa, límite de páginas, registro JSONL, hashes y estados de revisión en ocr_masivo.py. No equivale a exactitud jurídica certificada.
3. **CONFIRMADO, componente en main:** reintentar_rotados.py prueba rotaciones de 90/180/270 grados y selecciona por gate. No es deskew continuo ni dewarping 3D. En brain-env existe el calibrado con contraste, umbral y resize; su existencia no lo promueve a producto.
4. **CONFIRMADO, experimento:** run100.py instancia PaddleOCRVL, versión v1.6, gpu:0. La configuración recuperada tiene use_doc_preprocessor=false, use_chart_recognition=false y use_seal_recognition=false. Los subajustes internos de orientación/unwarping no prueban que se ejecutaron cuando el preprocesador global está apagado.
5. **CONFIRMADO, experimento separado en VM:** benchmark_ocr.py y benchmark_ocr_sample.py usan PP-OCRv5 móvil. No son VL ni el motor de la API de consulta.
6. **CONFIRMADO, parcial:** normalizar_citas.py preserva texto y genera citas para índice/revisión. datos_juridicos.py verifica una lista específica de la Ley 007; no es un extractor general de partes, montos, firmas y cláusulas. La indexación consume fechas y partes de metadatos de fuente.
7. **CONFIRMADO, búsqueda implementada:** SQLite FTS5 y lector Django. No encontré implementación vectorial/RAG en pipeline y sistema inspeccionados. Fragmentar por párrafos/artículos no equivale a segmentación jurídica general de cláusulas.
8. **NO ENCONTRADO en el alcance inspeccionado:** servicio /ocr/documento-legal, selección VL+MinerU, fallback Surya, GLM-OCR o verificación cruzada de montos con esos motores. No se censaron todas las carpetas y entornos virtuales de las tres máquinas.

Código primario: [pipeline en la revisión auditada](https://github.com/gatehot59-star/corpus-legal-tarija/tree/c273c659ee90f2259f540cb14c576d6a16dcfb40/pipeline), [lector y rutas Django](https://github.com/gatehot59-star/corpus-legal-tarija/tree/c273c659ee90f2259f540cb14c576d6a16dcfb40/sistema/django_app/corpus).

## El código pegado no está corregido

- **REFUTADO, alto impacto:** PaddleOCR no es PaddleOCRVL. En PaddleOCR 3.7.0 la primera clase selecciona la familia PP-OCR; la segunda ofrece pipeline_version=v1.6. El /health pegado etiqueta falsamente el motor como VL. [Clases oficiales](https://github.com/PaddlePaddle/PaddleOCR/tree/v3.7.0/paddleocr/_pipelines).
- **REFUTADO, alto impacto:** resultado[0] serializa sólo la primera página. La rama Markdown reporta len(resultado), pero no conserva su contenido completo. La prueba de dos páginas lo reproduce; con lista vacía, esa expresión produce IndexError.
- **REFUTADO:** modo no se utiliza. El ejemplo no implementa auto/txt/ocr. Los get de layout_result y table_result con defaults vacíos tampoco agregan capacidades de layout/tablas al pipeline general.
- **REFUTADO:** el ejemplo Surya no corresponde a v2. La firma actual admite images, layout_results y full_page, no langs ni det_predictions; la salida usa blocks/html, no text_lines. La documentación recomienda SuryaInferenceManager compartido. El constructor actual permite manager=None: no lo declaramos inválido por sí solo. [Código](https://github.com/datalab-to/surya/blob/master/surya/recognition/__init__.py) y [migración oficial](https://github.com/datalab-to/surya/releases/tag/v0.20.0).
- **CONTROL SIN HALLAZGO:** use_angle_cls está deprecado pero mapeado a use_textline_orientation en 3.7.0. No afirmamos que ese argumento aislado impida arrancar. Detectar orientación de renglones tampoco es reconocer sellos.
- **REFUTADO como entrega productiva:** el ejemplo no muestra autenticación, cuotas, límites de bytes/páginas/píxeles, validación del contenido real, aislamiento de parsers, cola, timeout ni control de concurrencia. Son ausencias del ejemplo, no una vulnerabilidad explotada del Corpus vivo.
- La copia al temporal ocurre antes del try/finally y puede dejarlo si falla. Copia e inferencia síncronas dentro de async def pueden bloquear el event loop. Falta validar formato_salida y manejar resultados vacíos/serialización; rec_scores puede requerir conversión según el resultado real. No se ensayó esa serialización. El /health fijo no mide disponibilidad del motor. Bind 0.0.0.0 no demuestra por sí solo exposición a Internet, pero exige controles de despliegue que aquí no aparecen.

Se trataron enlaces espurios e indentación perdida como defectos del pegado, no como pruebas contra las APIs. No se siguieron esos enlaces ni se lanzó Uvicorn.

## Benchmarks y licencias: correcciones verificadas

- **CONFIRMADO con atribución:** la tabla oficial OmniDocBench v1.6_full consultada muestra Paddle VL1.6 96,34; MinerU2.5-Pro 95,75; GLM-OCR 95,22 y Qwen3-VL-235B 89,78. **REFUTADO el ranking actual #1/#2/#3:** en esa misma tabla TeleOCR tiene 96,91 y OvisOCR2 96,47, por encima de Paddle. No recomendamos cambiarlos sin medir Corpus. El README anuncia v1.7 mientras esta tabla se rotula v1.6_full: se conserva esa distinción. [Leaderboard](https://github.com/opendatalab/OmniDocBench).
- El paper y la model card de Paddle publican **96,33**, no 96,34. No se oculta esa diferencia con el leaderboard. Overall combina texto, tablas y fórmulas: no significa 96,34% de documentos jurídicamente perfectos. La cifra base 92,56 para v1.5 no se revalidó en una captura histórica en esta auditoría. [Paper](https://arxiv.org/html/2606.03264).
- **CONFIRMADO:** Paddle VL tiene 0,9B y licencias Apache 2.0 para código y pesos consultados. La solución incluye además el detector de layout; 0,9B no describe todo su costo operativo. [Pesos/licencia](https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6/blob/main/LICENSE).
- **CONFIRMADO, reporte del proveedor:** Surya 650M, 83,3 en olmOCR-bench y 90,7 para español en su banco interno. No son métricas intercambiables con OmniDocBench ni resultados en Corpus. Código Apache 2.0, pesos bajo licencia modificada: exige atender ingresos brutos del año anterior y financiación acumulada, no sólo facturación actual. El texto contractual menciona superar USD 5 millones en cualquiera de esos criterios, con excepciones declaradas. [README](https://github.com/datalab-to/surya), [licencia de pesos](https://huggingface.co/datalab-to/surya-ocr-2/blob/main/LICENSE). CPU/Apple mediante llama.cpp está documentado; latencia en nuestras CPU NO MEDIDA.
- **CONFIRMADO con corrección:** MinerU usa una licencia propia basada en Apache con condiciones. En la versión consultada exige licencia comercial separada al superar 100 millones de MAU o USD 20 millones de ingreso mensual consolidado, y atribución visible al prestar servicios. No llamarla Apache estándar. La model card 2605 declara pesos Apache 2.0; la URL LICENSE ensayada devolvió 404, por lo que esa parte queda respaldada por metadatos, no por lectura de un contrato separado. Card y leaderboard difieren 95,69/95,75. Los 84 idiomas no se validaron para el backend/version exactos; el repo actual presenta MinerU 4.0. [Licencia código](https://github.com/opendatalab/MinerU/blob/master/LICENSE.md), [modelo 2605](https://huggingface.co/opendatalab/MinerU2.5-Pro-2605-1.2B).
- **REFUTADO:** GLM no tiene ambos componentes Apache: código Apache 2.0, modelo MIT según su card oficial; layout PP-DocLayoutV3 Apache. [Código](https://github.com/zai-org/GLM-OCR/blob/main/LICENSE), [modelo](https://huggingface.co/zai-org/GLM-OCR).
- **REFUTADO:** PP-OCRv4 no es sólo CPU; hay mediciones oficiales CPU y GPU, y variantes mobile/server. Un único tamaño aproximado de 15 MB no identifica la combinación detector/reconocedor. [Documentación](https://paddlepaddle.github.io/PaddleX/main/en/pipeline_usage/tutorials/ocr_pipelines/OCR.html).

## Recomendación para Corpus

Conservar Tesseract como baseline y promover VL sólo detrás de un contrato de páginas/bloques, procedencia y revisión de datos críticos. No sumar tres motores antes de demostrar que el segundo detecta errores que el primero deja pasar. Coincidir no garantiza independencia ni verdad.

El antecedente visual del mismo día ya refutó la perfección: la Ley 151 mostraba veinte millones y el candidato agregó ceros y omitió dos líneas, igual en cuatro lecturas. No se repitió esa inferencia ni se cerró aquí el cotejo exhaustivo de las dos páginas. [Evidencia anterior](https://github.com/gatehot59-star/corpus-legal-tarija/blob/18fc28c080aee086bb07bf34f5d9b83f3c673b19/docs/auditorias/2026-10-22-01-ocr-cotejo-visual.md).

La afirmación de que la combinación propuesta es la de menor error y mayor resiliencia disponible queda **NO MEDIDA**: faltan comparación pareada en documentos legales, errores correlacionados, costo/latencia, cobertura de páginas y decisiones ante desacuerdo. Los rótulos “excelente/bueno en español” de los otros motores no reemplazan ese banco.

## Instrumento, entrega y límites

Gate I: PASA para conservación de dos páginas y vinculación de firma Surya, con positivo y negativo pertinentes; también control de una página y resultado vacío. Se ejecutaron expresiones aisladas y una firma extraída por AST, no el servidor ni los modelos. La suite del autor del documento no fue aportada; inferencia, carga y seguridad HTTP son N/A a estos microcontroles, no aprobadas.

Gate II: revisión acotada sustentada; cada resultado distingue código, experimento, servicio y ausencia en rutas inspeccionadas. No se midieron fidelidad de cien páginas, exactitud jurídica integral, rendimiento Surya/MinerU/GLM ni despliegue HTTP extremo a extremo. No se certifica elegibilidad comercial: se informan textos de licencia.

Gate III: INCOMPLETA respecto del protocolo ampliado: publicación en rama de auditoría y Doc, sin merge a main ni reporte Nexus. Verificación remota se registra tras publicar. Capturas completas de fuentes y lecturas VM permanecen en brain-env; la evidencia Git contiene índice con hashes, instrumento y salida íntegra del instrumento, no todas las capturas. Un 404 de LICENSE no se confundió con indisponibilidad general. Ningún modelo instalado, base modificada, servicio reiniciado, GPU lanzada ni credencial leída.
