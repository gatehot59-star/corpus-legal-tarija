# OCR a toda máquina + sistema de agentes: análisis y plan

Fecha: 2026-09-25. Pedido de Abraham: revisar OCR en GitHub, evaluar ingeniería
inversa/motor propio, revisar el sistema de agentes de Corpus y el rol del
corpus como base para agentes externos.

## 1. Decisión OCR (relevamiento GitHub completo)

**No construir un OCR desde cero.** La vía ordenada:

1. **Producción: PaddleOCR PP-OCRv5 Latin mobile** (Apache-2.0). Ya ganó
   44/44 adjudicaciones humanas. Optimizar inferencia: DPI, deskew,
   multiproceso por página, backend ONNX/OpenVINO, perfilar det/rec por
   separado. El 4,86x vs Tesseract se ataca aquí, no con otro motor.
2. **Fine-tuning del reconocedor (rec) con las 120 páginas gold.** Una página
   jurídica densa da 30-100 líneas/crops: 3.600-12.000 muestras de
   reconocimiento, suficiente según la guía de Paddle (~5.000 muestras rec).
   Split POR DOCUMENTO (70/15/15), nunca por línea. Atacar los errores
   medidos: que→gue, Tarija→TARJA, tarijeños→torieños, ñ/acentos, numerales.
   Detector intacto salvo evidencia de líneas perdidas/fusionadas.
3. **Destilación server→mobile si la latencia sigue crítica.** PaddleOCR
   tiene knowledge distillation nativo (teacher logits → student CTC).
   Teacher: PP-OCRv5_server Latin; student: mobile exportado a ONNX/OpenVINO.
   Un VLM (olmOCR, Surya 2) solo como teacher de casos difíciles (sellos,
   degradados), nunca como motor único: riesgo de normalizar/inventar texto,
   inaceptable en leyes.
4. **Challengers medidos, no adoptados:** Surya 2 (83,3 olmOCR-bench, español
   90,7% interno; pesos Open Rail-M con restricción comercial: revisar antes
   de cualquier uso pago), PP-OCRv6 (documentado, benchmark local pendiente).
5. **Descartados por licencia o foco:** Calamari (GPL-3.0), Nougat y
   GOT-OCR2.0 (pesos CC-BY-NC / research-only), dots.ocr (acuerdo adicional +
   PyMuPDF/AGPL), MinerU (historial AGPL, licencia custom por versión),
   olmOCR como motor principal (7B, GPU, inglés).

**"Ingeniería inversa" realista para 1-2 personas:** no replicar el motor;
sí destilarlo. Teacher grande etiqueta nuestros 818 escaneados, student chico
aprende, y encima datos sintéticos con plantillas jurídicas tarijeñas (ruido
de escaneo, sellos, membretes). Eso ES el OCR propio: un modelo destilado y
fine-tuneado sobre nuestro dominio, con licencia Apache-2.0 limpia.

**KPIs antes de reprocesar:** CER global, CER en topónimos/nombres, WER,
exactitud de artículos/números/fechas, recall de líneas, tasa de páginas a
revisión humana, páginas/minuto. La gold de 120 páginas sigue siendo la
puerta: sin CER/WER no hay decisión.

## 2. Sistema de agentes: lo que existe y lo que falta

Lo que YA está decidido y construido (SUITE-Y-CONSUMIDORES.md):

- Corpus es producto independiente; Custos Legis lo consume, no al revés.
- Contrato HTTP para consumidores: `/buscar`, `/texto`, `/estado`,
  `/openapi.json`, `/agente/manifiesto`, `/api/v1/procedencias/{uid}`.
- Límites declarados: búsqueda literal (sin expansión semántica), facetas
  sobre muestra de 400 pasajes, offset corta en 10.000.
- NO entra: multi-tenancy, expedientes privados, casos/plazos/facturación.

Lo que falta para que agentes EXTERNOS lo usen de verdad:

1. **Autenticación de agentes**: hoy el contrato asume consumidor interno o
   sesión de usuario. Un agente externo necesita API key con scope (leer,
   buscar), rate limit propio y revocación auditable, separada de las
   sesiones de abogados.
2. **El flanco de privacidad sigue abierto**: el backend escucha en
   0.0.0.0:8080. Antes de exponer el contrato a agentes externos hay que
   bindearlo a loopback o ponerlo detrás del gateway con auth.
3. **Respuestas para máquinas, no solo para humanos**: citas con UID+hash en
   JSON estable, `vigencia` como campo (medida/no medida/derogada), y errores
   acotados que un agente pueda razonar (no solo 403 plano).
4. **El manifiesto de agente existe pero declarado viejo**: hay que
   regenerarlo cuando se cierre OCR/vigencia, porque un agente que confía en
   metadatos defectuosos amplifica el defecto.
5. **El sistema de agentes que estás creando (MUDH/gateway) puede ser el
   primer consumidor externo real**: el gateway ya habla con la VM; el paso
   natural es que un agente MUDH consuma `/buscar` con su propia key y quede
   registrado en el panel de uso como consumidor tipo "agente".

## 3. Orden de ejecución propuesto (a toda máquina)

1. Terminar la transcripción gold de 120 páginas (canal de visión abierto) →
   CER/WER por motor.
2. Si Paddle confirma: fine-tuning rec con los crops de la gold; reprocesar
   los 818 escaneados como VERSIÓN NUEVA (original intacto).
3. En paralelo: bind del backend a loopback + API keys con scope para
   agentes.
4. Vigencia visible (medida/no medida/derogada) en API y UI.
5. Regenerar `/agente/manifiesto` con los metadatos ya purgados.
6. Piloto universitario; agente MUDH como primer consumidor externo.

Nada de esto cambia la regla de SUITE-Y-CONSUMIDORES: el corpus sirve datos
públicos verificables; todo lo que solo sirva a un bufete va a Custos Legis.
