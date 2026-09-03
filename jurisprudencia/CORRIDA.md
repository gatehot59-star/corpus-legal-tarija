# Historico de jurisprudencia de Tarija, 2015-2026 (segunda corrida)

Disparada el 2026-09-03. **48 jobs**: 12 gestiones x 4 shards, con los 3 tipos de resolucion y
las 15 salas.

## Por que se relanzo

La primera corrida (12 jobs, uno por gestion) dejo **11 gestiones verdes con 2.664 resoluciones
y 64.682.493 caracteres**, y **2025 colgada**. Reproducido en brain-env, el culpable estaba en
el documento 48 de 198: un PDF de 1.977.159 bytes, **22 paginas y cero texto nativo**,
OCReandose pagina por pagina, con el resto de la gestion esperando en serie.

Dos correcciones: **timeout de 900 s por documento** y **4 shards por gestion**, asi el caso
peor baja de 198 documentos en serie a 50.

## El error de razonamiento que hubo en el medio, y vale mas que el fix

Una hora antes yo habia declarado esta misma hipotesis **REFUTADA**, porque el documento con
mas paginas de las 2.664 procesadas tenia 62 paginas y 0,0 s de OCR. El razonamiento estaba
mal: mire la muestra de los que **YA HABIAN TERMINADO** para concluir sobre el que estaba
colgado, y el que cuelga no esta en esa muestra por definicion. **Sesgo de supervivencia.**
Para explicar una falla, los sobrevivientes no sirven como muestra.

## Referencia de lo ya medido

| | |
|---|---|
| resoluciones (11 gestiones) | 2.664, todas OK |
| caracteres | 64.682.493 |
| via HTML oficial | 2.539 |
| via texto nativo del PDF | 120 |
| via OCR | 5 |
| segundos de OCR en total | 312,8 |

El resultado de esta corrida lo escribe el propio job en `RESUMEN.md` y `COBERTURA.txt`.
