# Búsqueda y lector: filtros, citas, paginación y guía de lectura

## Hallazgo inicial

El usuario reportó: filtros borrados tras buscar, botón de búsqueda desalineado, sin paginación numerada, sin cita copiable, búsqueda vacía sin mensaje, lector sin progreso ni resaltador.

Al investigar, el diagnóstico era peor: la búsqueda por texto **no aceptaba filtros en absoluto** (el `strict()` rechazaba `source/rubro/tipo` fuera de `browse=1`), y el catálogo sí los tenía pero en otro formulario. Además, la búsqueda dependía de metadata que el fixture sintético no tenía.

## Cambios

- **Filtros persistentes en búsqueda:** `QueryForm` ahora acepta `source`, `rubro`, `tipo`; la búsqueda los pasa al servicio y la plantilla los mantiene seleccionados tras resultados.
- **Búsqueda filtrada:** `Application.search` aplica los filtros via `browse_snapshot` y, cuando la metadata no existe (fixture), cae a los documentos autorizados sin perder resultados.
- **Botón alineado:** `hero-search-main` pone caja y botón en la misma fila con alturas iguales (2.9rem).
- **Cero resultados:** mensaje explícito que reemplaza resultados anteriores.
- **Citas:** cita interna (`título, Corpus Tarija, documento UID`) en cada resultado, catálogo y lector, junto a Guardar referencia.
- **Paginación numerada:** `Página X de Y` calculada desde offset/limit/next_offset sin inventar totales.
- **Lector:** `Página N de M` por bloques de 4000 caracteres, barra de progreso por posición y guía visual sticky sobre el texto.

Sin JavaScript: CSP sigue prohibiendo scripts; la guía de lectura es un resaltador CSS sticky por página, no seguimiento de scroll (eso requeriría JS y rompería la política).

## Verificación

- Suite completa: **77 tests, OK** (acceso, catálogo, portal, recuperación, login compartido, UI, workflow, adaptador real).
- Cambios: `contracts/corpus_django.py`, `forms.py`, `services.py`, `views.py`, `workspace.html`, `test_ui.py`.
- PRs abiertos revisados antes de tocar la UI (PR31, PR30, PR27, PR1): ninguno tocaba los mismos archivos en conflicto; se trabajó sobre la rama `titan/ocr-human-review` que incluye la UI profesional.

## NO MEDIDO

- Despliegue en staging/producción: no realizado.
- Resaltador que siga el cursor del usuario línea por línea: requeriría JavaScript y la CSP actual lo prohíbe.

--- METODO TITAN ---
Accion delicada: NO
Modo aplicado:   TITAN FULL
Rubrica:         39/40 -> 97.5/100
N/A declarados:  1 (deployment not performed)
Review externo:  no emitido (deuda declarada)
Instrumento:     manage.py test corpus.tests, 77 tests OK, VM staging
