# 2026-11-02-03 · Página A congelada como gold asistido: Abraham confirmó que A16 dice «veintiseis» sin tilde; los otros 24 renglones quedan solo con el pase IA

**Estado:** `h01-p002` (Ley 524, página 2) congelada como `gold-asistido-v1`, con `human_review=parcial`. B, C y D siguen pendientes.

## 1. Pedido

«esta sin tilde», el 2-nov a las 11:29 ART, en respuesta al pedido de confirmar A16 mirando el recorte ampliado del escaneo oficial (en el chat y en el Doc espejo). Se congela la página A con esa corrección, como gold asistido: pase visual IA sobre los 25 renglones más confirmación humana de A16.

## 2. Herramientas y máquina

- **brain-env (taller).** `freeze_a.py` lee `gold-ai-v1.json` (verificado por SHA-256 `36097a8d…`), aplica la corrección y escribe el gold en `/workspace/ocr-gold-humano-4p-20261102/`. No lee ninguna salida OCR.
- **GitHub MCP** para este commit. **ClickUp** para actualizar el Doc espejo.
- No se tocaron la VM, las planillas ni las páginas B, C y D. No hubo OCR, GPU, API externa ni Kaggle.

## 3. Qué se midió

- La corrección cambia **exactamente 1 carácter** de la referencia: offset 2076, «é» por «e», en A16 (renglón 25 del texto). El largo se mantiene en 2.277 caracteres.
- Guardas de `freeze_a.py`, que abortan si fallan: hash de la referencia, 25 renglones con texto y A16 en el renglón 25, ancla «veintiséis» única en el renglón y en la página, y un solo carácter distinto. Pasaron todas (exit 0).
- Texto de la referencia: SHA-256 `4406088a5d26bb6238ee5617aba1ed4a563c1ebea55a138024f964231ba5e3e5`. Texto congelado: SHA-256 `3a9b68b06d1725e15e93ecdb977f9cb099f4351ec2f4be2288b4781a8c168212`.

¿Podía dar rojo? Las guardas son condiciones que abortan; no se ejercitaron con un control negativo (ver NO MEDIDO). La corrección en sí sí tuvo un falsador: la confirmación humana sobre el escaneo, que podía decir «tiene tilde» y dijo «esta sin tilde».

## 4. Evidencia cruda

`python3 freeze_a.py`, exit 0, stderr vacío:

```
FROZEN h01-p002 chars 2277 changed_offset 2076 'é' -> 'e'
TEXT_SHA256 3a9b68b06d1725e15e93ecdb977f9cb099f4351ec2f4be2288b4781a8c168212
REF_TEXT_SHA256 4406088a5d26bb6238ee5617aba1ed4a563c1ebea55a138024f964231ba5e3e5
```

Respuesta de Abraham, textual: «esta sin tilde».

## 5. Archivos generados

Bajo `docs/agents/evidencia/2026-11-02-03-gold-asistido-h01-p002/`:

| Archivo | Bytes | SHA-256 |
|---|---|---|
| `freeze_a.py` | 3.671 | `b4df782eee11bce6ad6dfc0f7f04f33fcccd4f20a03df05b2b55988d19687f84` |
| `gold-asistido-v1-h01-p002.json` | 4.530 | `0b45752be7db8b20f41b483148edc2d7d6968fb775590a46c1c85d9e374e5d59` |

## 6. NO MEDIDO

- **Revisión humana de A01 a A15 y A17 a A25.** Solo tienen el pase visual IA; por eso `human_review=parcial`. Si Abraham los revisa, la página puede subir a gold humano completo.
- **El OCR contra este gold.** Se mide cuando estén cerradas las cuatro páginas, como dice el plan publicado, para no sesgar la revisión de B, C y D.
- **Control negativo de las guardas** de `freeze_a.py`.
- Reproducibilidad, otros documentos y certificación legal.

## Cómo sigue

Faltan B, C y D. Mismo formato: «B: sin cambios» o «B05: dice «…», debe decir «…»». D es la corta.

--- METODO TITAN / PROMETEO ---
Accion delicada: NO
Modo aplicado:   PROMETEO LIGERO
Maquina:         brain-env (freeze_a.py, solo lee gold-ai-v1.json; no lee OCR)
Rubrica:         N/A (modo ligero)
N/A declarados:  rubrica completa (congelado de una pagina)
Review externo:  la confirmacion humana de A16 es el falsador y dio verde; los otros 24 renglones no tienen review humano
Instrumento:     freeze_a.py exit 0: ancla unica, mapa de renglones, exactamente 1 caracter cambiado
Artefactos:      este archivo + Doc espejo de las planillas (seccion actualizada, linkeada desde el chat)
