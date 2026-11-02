# 2026-11-02-02 · Planilla A con pase visual IA: 24 de 25 renglones coinciden con el escaneo y la referencia tiene un error en A16, «veintiéis» con tilde donde el impreso no la tiene

**Estado:** pase visual IA hecho, corrección propuesta en A16, falta la confirmación humana. Nada congelado.

## 1. Pedido

«Revisá primero A y respondé «A: sin cambios»», el 2-nov a las 10:36 ART, un minuto después de invitar a Abraham a revisar A. Se hizo un pase visual IA de la planilla A (Ley 524, página 2, `h01-p002`) contra el escaneo oficial. No se respondió «A: sin cambios» por dos motivos: el pase encontró una diferencia, y una revisión hecha por BRAIN no puede registrarse como revisión humana.

## 2. Herramientas y máquina

- **Sandbox de ClickUp, sin red.** Pillow 12.2.0 y numpy sobre el render oficial de la página (`pdftoppm` a 300 dpi en grises, 2526 × 3915, píxeles `b621ebff…`, idénticos a la imagen del banco). Solo recortes y ampliaciones; no se corrió ningún OCR.
- **Lectura:** BRAIN, modelo de lenguaje con visión, sobre los recortes.
- **Medición:** huecos entre columnas de píxeles oscuros (umbral < 140) en el título de A05.
- No se tocaron la VM, las planillas publicadas ni las páginas B, C y D.

## 3. Qué se midió

Los 25 renglones, franja por franja, en tiras de 1500 px de ancho (0,75 del original). Los puntos finos, ampliados de 1,35 a 4 veces:

| Renglón | Punto | Escaneo | Referencia | Veredicto |
|---|---|---|---|---|
| A05 | Separador decimal del monto de Bs. 17 millones | coma: «17.000.000,00» | igual | coincide |
| A05 | Espacio entre «TRANSITORIA» y «PRIMERA» | hueco de 14 px; entre letras, de 5 a 8 px; entre otras palabras, de 15 a 19 px | con espacio | coincide |
| A10 | Signo después de «SIGEP» | coma | coma | coincide |
| A14 | Tilde de «Remítase» | con tilde | con tilde | coincide |
| A15 | Inicial de «Departamento» | mayúscula | mayúscula | coincide |
| A16 | «Gobernación» | con b | con b | coincide |
| A16 | Tilde de la penúltima palabra | **sin tilde** | **«veintiéis», con tilde** | **no coincide** |
| A20 a A25 | Pie de página completo | «Telf. : 6113312», «Fax : 6113308», «www.aldt.gob», «Tarija - Bolivia», «Calle Sucre Esq. La Madrid», «(Plaza Luis de Fuentes y Vargas)» | igual | coincide |

Resultado: 24 de 25 renglones coinciden. Corrección propuesta, con la convención de respetar lo impreso aunque tenga errores propios: en A16, la penúltima palabra va sin tilde, tal como está impresa.

¿Podía dar rojo? Sí: dio rojo en A16. Las tildes se resuelven a esa escala: en el mismo párrafo se ven la de «días» y la de «Gobernación», y la virgulilla de «años».

## 4. Evidencia cruda

Renglones detectados por perfil horizontal (y en píxeles del original):

```
F3 [(982, 1026), (1045, 1090), (1111, 1155), (1175, 1212), (1251, 1274)]
F5 [(1621, 1658), (1685, 1729), (1749, 1794), (1812, 1846)]
F8 [(2576, 2623), (2704, 2752)]
F9 [(2830, 2870), (2903, 2927)]
F11 [(3742, 3777), (3785, 3818), (3856, 3915)]
```

Recortes (x0, y0, x1, y1 en el original) y escala:

```
A05 título:              (277, 974, 1400, 1034)    x1,35
A05 monto 17 millones:   (1400, 1103, 2265, 1163)  x1,7
A10 SIGEP:               (277, 1675, 1150, 1739)   x1,7
A14 Remítase:            (277, 2566, 560, 2633)    x4
A16 penúltima palabra:   (277, 2893, 820, 2937)    x2,6
A16 Gobernación y días:  (277, 2820, 1400, 2880)   x1,35
Pie izquierdo:           (277, 3700, 1100, 3915)   x1,6
Pie derecho:             (1650, 3700, 2526, 3915)  x1,6
```

Huecos del título de A05 (x de inicio y ancho en px, solo los de 5 px o más):

```
GAPS heading (x, width>=5px): [(277, 18), (324, 6), (341, 6), (368, 7), (460, 7), (476, 7), (505, 5), (523, 5), (558, 5), (595, 6), (627, 17), (672, 6), (708, 5), (742, 5), (775, 7), (804, 6), (820, 6), (927, 6), (943, 6), (980, 14), (1017, 6), (1052, 5), (1068, 7), (1114, 8), (1147, 6), (1217, 6), (1230, 19), (1269, 5), (1291, 15), (1325, 6), (1337, 6)]
```

El hueco de 14 px en x = 980 separa «TRANSITORIA» de «PRIMERA»; el de 17 px en x = 627 separa «DISPOSISICON» de «TRANSITORIA».

El recorte de A16 queda en el Doc espejo. Los recortes son derivados: se regeneran con estas coordenadas desde el render oficial.

## 5. Archivos generados

Este recibo. Sin evidencia binaria en git.

## 6. NO MEDIDO

- **La confirmación humana.** Hasta que Abraham mire el recorte y confirme, A16 es una corrección propuesta y la página A sigue sin gold.
- **La revisión humana de los otros 24 renglones.** Si solo se confirma A16, la página queda como pase visual IA con confirmación humana del cambio, no como gold humano completo.
- **Independencia.** El pase no es ciego: BRAIN conocía los puntos donde la salida OCR difiere de la referencia en esta página y los amplió a propósito. Tampoco es un instrumento con tasa de error conocida.
- Las planillas B, C y D no se tocaron; este recibo no dice nada de ellas.

--- METODO TITAN / PROMETEO ---
Accion delicada: NO
Modo aplicado:   PROMETEO LIGERO
Maquina:         sandbox ClickUp (Pillow/numpy, recortes del render oficial) + lectura visual de BRAIN
Rubrica:         N/A (modo ligero)
N/A declarados:  rubrica completa (recibo chico de revision)
Review externo:  pendiente: la confirmacion humana de A16 es el falsador
Instrumento:     lectura visual con zoom de 1,35x a 4x; perfil de columnas para el espacio de A05; dio rojo en A16
Artefactos:      este archivo + Doc espejo de las planillas (seccion nueva, linkeada desde el chat)
