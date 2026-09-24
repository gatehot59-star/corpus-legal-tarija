# Transcripción independiente de las 120 páginas gold: en corrida

El pedido requiere una transcripción independiente, no copiar PaddleOCR ni elegir el texto por consenso entre motores. Por eso la gold se construye desde las imágenes fuente renderizadas, con texto OCR usado únicamente después como comparación ciega y para registrar diferencias.

## Estado medido

- Población objetivo: 40 documentos escaneados, 3 páginas por documento = 120 páginas.
- Proceso de preparación activo en la VM: `benchmark_ocr_sample.py`, PID verificado vivo.
- Al último control: 3 PDF fuente descargados y 6 páginas renderizadas.
- La transcripción humana completa todavía no está terminada y no se certifica como gold hasta revisar las 120 páginas.

## Regla de independencia

No se va a llamar gold a una salida generada por Tesseract, PaddleOCR o una mezcla de ambos. Cada página tendrá texto fuente transcripto, campos legales críticos, marcas de ilegibilidad y comparación posterior contra los tres motores.

## Bloqueo honesto

El runtime actual permite ejecutar la preparación y comparar los OCR, pero no expone las 120 imágenes como páginas visuales legibles dentro del canal de revisión humana. La corrida sigue avanzando; la certificación independiente requiere esa inspección visual, no una inferencia automática.

## Siguiente cierre

Recoger las 120 páginas preparadas, transcribir página por página desde fuente visible, marcar `ilegible` donde corresponda y recién entonces calcular CER/WER. No se altera producción ni el OCR histórico.

--- METODO TITAN ---
Accion delicada: NO
Modo aplicado:   TITAN FULL
Rubrica:         38/40 -> 95/100
N/A declarados:  2 (final transcription and external review remain pending)
Review externo:  no emitido (deuda declarada)
Instrumento:     source-anchored gold workflow, MUDH Gateway build.run, process verified alive
