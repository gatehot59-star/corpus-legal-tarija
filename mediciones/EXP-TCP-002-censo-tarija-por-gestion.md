# EXP-TCP-002 · Censo TCP distrito Tarija por gestión (PARCIAL)

Medido: 2026-09-03 · navegador real headless, formulario público, sin credencial
Instrumento: `POST /api/buscador-jurisprudencia/buscarResolucionJurisprudencia`

## Contrato medido (verbatim del payload capturado)

```json
{"texto":"amparo","tipoBusqueda":"1","seccionId":0,"fechaInicial":"2015-01-01",
 "fechaFinal":"2015-12-31","distrito":"7","institucion":0,"magistrado":0,"recurso":0}
```

Respuesta `201` con array. Cada item: `resolucionId`, `expedienteId`, `numeroExpediente`,
`referencia` (snippet resaltado), `tipoResolucion`, `resolucion`, `fecha`, `baseId`.
**No hay campo de total ni paginación: el array viene completo.**

## Descubrimiento estructural: todo Tarija vive en distrito 7

`getListarDistrito` devuelve 174 distritos. Los de Tarija: 7 (Tarija), 16 (Tarija Capital),
135 (Bermejo), 137 (Entre Rios), 138 (Padcaya), 139 (San Lorenzo Concepcion), 140 (Villamontes),
141 (Yacuiba).

Medidos con rango completo 1999-2026: **16 = 0, 137 = 0, 140 = 0, 141 = 0**.
O sea: los sub-distritos no se usan en resoluciones. **NO MEDIDO: 135, 138, 139.**

## Censo por gestión, distrito 7

| Gestión | Resoluciones | Instrumento |
|---|---|---|
| 1999 | 1 | A |
| 2000 | 0 | A |
| 2001 | 0 | A |
| 2002 | 37 | A |
| 2003 | 91 | A |
| 2004 | 88 | A |
| 2005 | 71 | A |
| 2006 | 83 | A |
| 2007 | 48 | A |
| 2008 | 4 | A |
| 2009 | 1 | A |
| 2010 | 126 | A |
| 2011 | 96 | A |
| 2012 | 163 | A |
| 2013 | 236 | A |
| 2014 | 281 | A |
| 2015 | 349 | A |
| 2016 | 380 | B |
| 2017 | 293 | B |
| 2018 | 301 | B |
| 2019 | 290 | B |
| **1999-2019** | **2.939** | mixto |
| 2020-2026 | **NO MEDIDO** | - |

- **Instrumento A**: `tipoBusqueda=2` (cualquier término), texto
  `notifíquese regístrese archívese comuníquese constitucional`.
- **Instrumento B**: `tipoBusqueda=1`, texto `notifíquese`. Se usó en 2016+ porque A daba
  timeout de backend a los 15 s en los años de mayor volumen.
- **Los dos instrumentos NO son equivalentes**: en 2015, A = 349 y B = 344. B subcuenta 5 (1,4 %).
  Las filas B son por lo tanto **cota inferior**, no censo exacto.

## Sesgo declarado del método

El buscador **exige un término de texto**: no existe consulta sin criterio. Por lo tanto esto no es
un censo del universo, es el conteo de **resoluciones de Tarija recuperables por full-text con un
término de cierre procesal**. Una resolución que no contenga ninguno de esos términos no aparece.
No hay forma medida de acotar ese faltante todavía.

## Ausencia de tope, verificada

Mismo año y distrito con dos términos distintos: `amparo` = 227, `notifíquese` = 344.
Ninguno es un número redondo y difieren, así que **no hay límite fijo de resultados**.

## Errores propios cazados en esta corrida

1. Atribuí **293 a 2018** en una corrida donde no verifiqué el payload. Al re-medir capturando
   `fechaInicial`/`fechaFinal` enviados, **2018 = 301** y 2017 = 293. El 293 duplicado era mío,
   no del servidor. Desde entonces toda fila lleva el rango pedido verbatim.
2. Un `400` del backend **no significa payload inválido**: el cuerpo decía
   `{"message":"Error: Timeout: Request failed to complete in 15000ms"}`. El nombre del código
   mentía sobre la causa.
3. `robots.txt` responde 200 con el HTML de la SPA: **no es consultable** por esa vía.

## NO MEDIDO

- Gestiones **2020 a 2026** (7 gestiones). El límite fue de mi presupuesto de ejecución, no del sitio.
- Distritos 135, 138, 139.
- El faltante real del método full-text.
- **Licencia y política de redistribución.** Sigue bloqueando la ingesta: público no es redistribuible.
- Descarga y hash de los textos: nada se incorporó al corpus todavía.
