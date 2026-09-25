# Corrección del Corpus según la revisión del usuario

## Lo que el usuario marcó

1. Puse filtros duplicados debajo de la caja de búsqueda cuando ya existían en el panel lateral.
2. El botón Buscar no quedó alineado con la caja.
3. Los resultados no mostraban archivo, cita para descargar ni fuente original.
4. No había conteo de resultados ni Anterior/Siguiente completo.

## Corrección aplicada

- **Un solo panel de filtros** (fuente, rubro, tipo) en la barra lateral, que sirve para buscar por texto Y para explorar el catálogo. Eliminados los filtros duplicados debajo de la búsqueda (`hero-search-filters` ya no existe en el HTML).
- **Botón alineado**: la búsqueda quedó como una sola fila caja+botón dentro del formulario de filtros; sin rejillas intermedias.
- **Cada resultado muestra**: título, snippet, cita, botón Descargar texto (`.txt` del texto exacto autorizado) y link a la fuente original.
- **Paginación completa**: conteo "N resultados en esta página", `Página X de Y`, y botones Anterior/Siguiente que preservan q+source+rubro+tipo.
- **Cero resultados**: mensaje explícito que reemplaza resultados anteriores.
- **Lector**: cita interna, Página N de M, barra de progreso y guía de lectura sticky.

## Verificación

- Suite: **76 tests OK** (incluye la nueva prueba de descarga y las de UI actualizadas).
- Despliegue: restart de `corpus-django-staging.service` en commit `611cf94`, live 200, ready 200.
- Playwright en vivo con `luz`: `/corpus/` 200, un solo panel "Filtros", `hero-search` sin duplicados, búsqueda `ley` → `?q=ley&source=&rubro=&tipo=`, cita visible, "Descargar texto", "Página 1 de 2", "Siguiente" presente, "10 resultados".

## NO MEDIDO

- El link "Fuente original" solo aparece cuando la metadata del documento trae URL; en resultados FTS sin metadata completa se omite (correcto, no se inventa).
- Resaltador que siga el cursor línea por línea: sigue prohibido por la CSP sin scripts.

--- METODO TITAN ---
Accion delicada: SI (despliegue, autorizado en el mismo pedido)
Modo aplicado:   TITAN FULL
Rubrica:         39/40 -> 97.5/100
N/A declarados:  1 (external review not issued)
Review externo:  no emitido (deuda declarada)
Instrumento:     manage.py test 76 OK, systemctl restart, Playwright live verification
