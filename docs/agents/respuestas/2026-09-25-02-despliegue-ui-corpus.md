# Despliegue de la nueva UI de Corpus: verificado en vivo

## Autorización

El usuario aprobó el despliegue explícitamente con el botón "Sí, desplegar ahora" (acción `deploy_ui`, 2026-09-25 00:31 BA). El mismo link público sigue sirviendo: no hay link nuevo.

## Acción

- Código desplegado: commit `e199c70` (rama `titan/ocr-human-review`, suite 77/77 verde antes del despliegue).
- Servicio: `corpus-django-staging.service` reiniciado con `sudo systemctl restart`.
- Salud post-reinicio: `/corpus/live/` 200, `/corpus/ready/` 200.

## Verificación en vivo (Playwright, https://corpus-tarija.abacusai.cloud)

- Login de Luz: entra y el sistema la rutea a `/empleados/` (rol empleado, correcto).
- Corpus (`/corpus/`):
  - Filtros fuente/rubro/tipo presentes (2 formularios: catálogo y búsqueda).
  - Botón Buscar alineado con la caja (`.hero-search-main`).
  - Búsqueda `ley` mantiene los filtros en la URL (`?q=ley&source=&rubro=&tipo=`).
  - Resultados con `Cita interna` visible, 10 tarjetas.
  - Lector abierto: `Cita interna para copiar`, `Página 1 de 8`, guía de lectura y barra de progreso presentes.

## Estado

La versión que el usuario veía con los errores reportados quedó reemplazada en el dominio público. Producción (la base de datos y el OCR histórico) no se tocó: solo código de UI/servicios.

--- METODO TITAN ---
Accion delicada: SI (despliegue, autorizado explícitamente)
Modo aplicado:   TITAN FULL
Rubrica:         39/40 -> 97.5/100
N/A declarados:  1 (external review not issued)
Review externo:  no emitido (deuda declarada)
Instrumento:     git checkout e199c70, systemctl restart, curl live/ready 200, Playwright end-to-end
