# Modernización profesional de la interfaz Corpus

## Pedido
Revisar el corpus anterior y agregar al nuevo sistema lo que tenía de útil, con ventanas más profesionales, más intuitivas, adaptables a distintos dispositivos y con opción de modo noche. También se pidió explorar corpus profesionales o proyectos en GitHub.

## Qué se midió
- Repositorio vivo leído en `feat/catalog-navigation` y rama nueva `feat/ui-professional-polish`.
- Plantillas actuales revisadas: `workspace.html`, `login.html`.
- Vistas y servicios revisados para no romper autorización ni catálogo.
- PR30 quedó verde en checks `application`, `browser` y `stable_identity`.
- Se creó una rama separada para no mezclar esta mejora con PR30.

## Qué se construyó
- Nuevo shell visual profesional para `workspace.html`.
- Nuevo login con el mismo sistema visual y recuperación clara.
- Modo noche con `prefers-color-scheme` y toggle manual persistente.
- Diseño responsive para escritorio, tablet y móvil.
- Tarjetas de documentos con badges por fuente, rubro y tipo.
- Lateral de filtros más claro y acciones privadas mejor ordenadas en lectura.
- Se agregaron atajos y secciones más legibles para referencias y reportes.

## Referencias exploradas
- CourtListener / freelawproject: filtros avanzados responsive, tarjetas legales, acciones por resultado.
- trybunalkonstytucyjny: persistencia de estado en URL, filtros por secciones y tipos, foco en lectura experta.
- Circuitus: tipografía legal, panel de lectura, biblioteca, organización de trabajo.
- CaseLens / LexMind / LegalLookup: dashboards legales modernos, tarjetas, modo oscuro, enfoque producto.

## Archivos generados
- `sistema/django_app/corpus/templates/corpus/workspace.html`
- `sistema/django_app/corpus/templates/corpus/login.html`
- `sistema/django_app/corpus/tests/test_ui.py`

## NO MEDIDO
- No ejecuté la suite Django ni Chromium desde esta sesión.
- No hice merge a `main`.
- No hice inventario pixel a pixel de la interfaz vieja en la VM; esta ronda mejora el nuevo sistema con la metadata y patrones ya verificados.

--- METODO TITAN ---
Accion delicada: SI (toca frontera de interfaz privada)
Modo aplicado: TITAN FULL
Rubrica: pendiente en PR
N/A declarados: producción, cuentas reales, SMTP y carga no son objeto de esta feature
Review externo: pendiente en PR; silencio no es aprobación
Instrumento: GitHub real + sandbox para preparar plantillas; evidencia cruda en PR
