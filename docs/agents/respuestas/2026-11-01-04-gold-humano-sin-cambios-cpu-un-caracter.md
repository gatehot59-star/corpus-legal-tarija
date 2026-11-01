# Gold humano de la Ley 524 p. 1: revisión «SIN CAMBIOS»; la CPU erra 1 carácter y acierta los 23 números

## 1. Pedido y veredicto

Pedido literal: «SIN CAMBIOS», respuesta de Abraham a la planilla de revisión humana del recibo 2026-11-01-03 (Ley 524, página 1, h01-p001), recibida el 1-nov-2026 a las 14:25 ART.

**Gold humano congelado sin correcciones:** el texto queda idéntico a la referencia IA (2.854 caracteres, SHA-256 `12ded3ed113cf7dcd9c1c34335c7d0ec080175430a083a1c83a3f4b428de83fd`), ahora con human_review=true, revisor y fecha. Archivo: `docs/agents/evidencia/2026-11-01-04-gold-humano-ley524-p1/gold-human-v1-h01-p001.json`.

**Salida CPU contra ese gold, medida:**

- Con espacios y saltos de línea normalizados: 1 edición en 2.843 caracteres, CER 0,0352 %. Es «Presupuestó» donde la ley dice «Presupuesto», en el título del Artículo 6.
- Palabras: 1 de 401, WER 0,2494 %.
- Números: 23 de 23 iguales; ninguno falta ni sobra (montos, número de ley, fechas y teléfonos).
- Sin normalizar: 16 ediciones, CER 0,5606 %; 15 son espacios y saltos de línea, repartidos en 14 tramos.

**Conclusión, no medición:** en esta página la CPU reproduce el texto con un solo error tipográfico, una tilde de más, que no toca montos ni números. La salida GPU existente tiene el mismo texto byte a byte (recibo 2026-11-01-02), así que comparte estas cifras. Es una página y un revisor: no generaliza al resto del corpus.

Doc espejo: [Gold humano de la Ley 524 p. 1](https://app.clickup.com/90171457413/docs/2kza6fw5-26237), ruta Space > Doc.

## 2. Herramientas, máquina y escrituras

- brain-env, Python del gateway: leyó gold-ai-v1.json local con SHA-256 verificado, el manifiesto de la planilla desde GitHub (commit 2e1404303e90ad019b55c24366b546d0873a31c9, SHA-256 verificado) y la captura terminal seleccionada de la corrida CPU (SHA-256 `96ad28d81c5d240d91b74f9e9b5f1c191dd424ef389b4c70c56661a59cba35db`, la misma publicada en 672c94ddca58d27117dcd0e950c0faeb5bdcf745). Escribió sólo en `/workspace/ocr-gold-humano-ley524-p1-20261101/`.
- GitHub MCP: este commit, append-only en main. ClickUp: actualización del Doc espejo.
- No se corrió OCR, GPU ni API; no hubo conexión a la VM; no se tocó el producto, PR33, el gold IA sellado ni el schedule.

## 3. Qué se midió

- Instrumento: measure.py, SHA-256 `955cec7246abcb52089e2b0a9b47b4e76894fbf124e548ca7cbafba2c28b3e35`. Levenshtein exacto por carácter y por palabra, con y sin normalizar espacios; multiconjunto de números con la expresión de la planilla; tramos de diferencia con difflib. Ubica el texto CPU por su SHA-256, exige human_review=true y verifica el hash del texto del gold antes de medir.
- Controles para que pueda dar rojo: el gold contra sí mismo da 0 ediciones y 23 números; una mutación de un dígito (595.477.378 a 595.477.379) suma una edición y marca el número faltante y el sobrante.

## 4. Evidencia cruda

```text
CAPTURE_SHA 96ad28d81c5d240d91b74f9e9b5f1c191dd424ef389b4c70c56661a59cba35db
MEASURE_EXIT 0 STDERR ''
FILE gold-human-v1-h01-p001.json 5805 af09bf8873a7ca0356987a7c946dfe108c647c2be73a053e5efdfa0a9928c878
FILE measure.py 3804 955cec7246abcb52089e2b0a9b47b4e76894fbf124e548ca7cbafba2c28b3e35
FILE measure-output.json 1114 60b04efa3bf1d6e0096a869066405863c0495c883ff545a1e695b7713f0bbd8b
```

La salida completa del instrumento está verbatim en `measure-output.json`, en este mismo commit.

Para repetirlo: recuperar terminal-selected-capture.json del sobre publicado en 672c94ddca58d27117dcd0e950c0faeb5bdcf745 y correr `python3 measure.py gold-human-v1-h01-p001.json terminal-selected-capture.json`.

## 5. Archivos generados

- `docs/agents/evidencia/2026-11-01-04-gold-humano-ley524-p1/gold-human-v1-h01-p001.json`: 5.805 bytes, SHA-256 `af09bf8873a7ca0356987a7c946dfe108c647c2be73a053e5efdfa0a9928c878`.
- `docs/agents/evidencia/2026-11-01-04-gold-humano-ley524-p1/measure.py`: 3.804 bytes.
- `docs/agents/evidencia/2026-11-01-04-gold-humano-ley524-p1/measure-output.json`: 1.114 bytes, SHA-256 `60b04efa3bf1d6e0096a869066405863c0495c883ff545a1e695b7713f0bbd8b`.
- Este recibo. No hay binarios.

## 6. NO MEDIDO

- La exactitud de la CPU en otras páginas, otras leyes o escaneos más difíciles: esto es una página.
- La minuciosidad y la duración de la revisión: hay un único revisor y su respuesta fue «SIN CAMBIOS».
- La independencia plena: revisó una referencia IA, no transcribió desde cero, y ya conocía el único punto de desacuerdo, el título del Artículo 6.
- La reproducibilidad de la CPU: hubo una sola corrida y el estándar pide tres por página.
- La validez jurídica o una fidelidad certificada: no se declaran.
- Las otras cuatro páginas del banco siguen sin gold humano.

--- METODO TITAN / PROMETEO ---
Accion delicada: NO, evidencia append-only y un Doc actualizado
Modo aplicado: LIGERO
Maquina: brain-env, lectura y medicion local; GitHub MCP para el commit
Rubrica: N/A (modo ligero)
N/A declarados: rubrica completa, medicion chica de una pagina
Review externo: NO REALIZADO; la revision humana es del gold, no del instrumento
Instrumento: measure.py exit0, stderr vacio; gold contra si mismo 0 y mutacion de un digito detectada; salida cruda en measure-output.json
Artefactos: docs/agents/respuestas/2026-11-01-04-gold-humano-sin-cambios-cpu-un-caracter.md + https://app.clickup.com/90171457413/docs/2kza6fw5-26237
