# 2026-09-23 20:50 · Peritaje integral del informe de Juan Pérez

## Pedido
Revisar íntegramente lo que dejó el abogado Juan Pérez, explorar los textos y determinar si los errores pudieron aparecer al copiar del Corpus original.

## Evidencia de entrada
- Cuenta piloto: `juanperez` / nombre mostrado: JUAN PEREZ.
- Informe recibido: categoría `extraction`.
- Documento: `dep-tar-compilado-de-sin-numero-2013-6b9dcffa`.
- Texto del informe: `hay errores " gue" por "que", palabra pario sn contexto, en vez de la aparece LL, TARJA EN VEZ DE TARIJA, TORIEÑOS, EN VEZ DE TARIJEÑOS. ENTRE OTRS. EXTRAÑO PORQUE , ANTERIORMENTE LA IA EXPLORA LOS ARCIVOS INTEGROS Y NO HABIA ERRORES DE ESTE TIPO`.

## Comparación original vs adaptado
Instrumento: Python + SQLite, ejecutado en la VM staging sobre:
- Original aislado: `/var/lib/corpus-django-staging/corpus-real-copy-20260923.db`.
- Adaptado servido: `/var/lib/corpus-django-staging/corpus-adapted-real-20260923.db`.

Para el UID informado:
- Original: 48 chunks, 78.384 caracteres concatenados.
- Adaptado: 48 chunks, 78.384 caracteres concatenados.
- Hash SHA-256 del cuerpo de cada chunk: coincidencia exacta 48/48; mismatches: 0.
- Los términos reportados aparecen con la misma frecuencia en ambos:
  - `gue`: 16.
  - `TARJA`: 16.
  - `TARIJA`: 178.
  - `TORIEÑOS`: 1.
  - `TARIJEÑOS`: 0.
  - `pario`: 5.
- Ejemplos leídos íntegramente: `Gue, habiendo sido...`, `Departamento de Tarja`, `Los torieños`, `pario PREAAMBLLO`.

## Veredicto
**No fue causado por la copia del Corpus original al adaptado.** El texto de Juan es idéntico por chunk entre ambas bases. Los errores pertenecen al OCR/extracción de la fuente original y la adaptación los preservó; no los inventó ni los corrigió.

Además, la extracción contiene contaminación típica de OCR: encabezados y sellos repetidos, fragmentos de página, caracteres aislados, HTML residual (`<u>`), y bloques repetidos entre páginas. Eso explica por qué una exploración semántica anterior podía parecer más limpia: probablemente estaba interpretando o corrigiendo el texto, no mostrando el OCR literal completo.

## Qué sí hay que corregir
No conviene sobrescribir el OCR original: es la evidencia de procedencia. La solución correcta es una capa separada de texto revisado/correcciones, vinculada al UID y a la versión exacta, con cada corrección trazable. Para este documento, priorizar revisión humana de `gue/que`, `Tarja/Tarija`, `torieños/tarijeños`, `pario PREAMBULO` y los duplicados de página.

## NO MEDIDO
- No se pudo cotejar contra el PDF/imagen fuente original porque no está montado en la VM staging; sí se cotejaron las dos bases SQLite que contienen la copia original y la versión servida.
- No se corrigió el texto todavía: el pedido fue peritaje de causa, no autorización para modificar el corpus jurídico.
