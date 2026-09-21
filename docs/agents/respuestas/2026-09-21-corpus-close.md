# Corpus: browser CI cerrado, integración todavía no ejecutada

## Estado vivo

La corrección quedó en PR24, rama `titan/fix-corpus-browser-login`, head `440fa6534bbb27edf7cf51b477332e65a258df46`. PR24 sigue abierto y su base viva es PR23. PR22, PR23 y PR24 siguen abiertos; no ejecuté merges.

## Qué faltaba y qué corregí

Reproduje en el runtime de build el fallo real, con el head exacto: el headless shell de Playwright murió con `SkFontMgr_FontConfigInterface.cpp:163`, `SIGTRAP`, al cargar la página. Probé el canal Chromium completo con la configuración de Fontconfig medida y el navegador dejó de cerrarse. En la misma corrida apareció el segundo fallo, independiente y concreto: la prueba armaba una URL absoluta dos veces para el replay de sesión vencida. Cambié el runner para usar el canal completo y reutilizar `read_url` sin concatenar el origen.

No toqué CSRF, permisos, datos reales ni el flujo del producto. La corrección conserva el rechazo de `Origin: null` y la regresión de login same-origin.

## Verificación

La jornada local sintética completa pasó con exit 0 en brain-env desde `440fa6534bbb27edf7cf51b477332e65a258df46`. El nuevo CI de PR24 también pasó: application job `106448220581` y browser job `106448220758`, ambos sobre ese head, ambos `success`. El browser hosted terminó en `51s`; application en `33s`.

El recorrido que queda verde cubre login, búsqueda, lectura versionada y procedencia secundaria, referencia privada, feedback privado con escape XSS, logout y replay vencido, aislamiento Ana/Ben, viewport móvil, recuperación de contraseña, token de un uso y retiro que bloquea lectura y oculta referencias.

## Integración

**Qué mergeé:** nada. El usuario autorizó construir y probar, pero mergear sigue siendo una acción destructiva que requiere confirmación humana explícita en el momento. Tampoco salteé el hold G2 de PR18 ni convertí reviews vacíos en aprobaciones.

**Qué queda bloqueado para Abraham:** solo la decisión de integración, más la revisión independiente pendiente de PR18. PR24 ya no está bloqueado por CI. Antes de mergear hay que revisar la pila viva y elegir explícitamente qué PRs integrar, sin arrastrar PR17/PR21 históricos ni saltear PR18.

## Siguiente acción concreta

Presentarte el lote exacto de merges candidatos con sus heads, bases, checks y dependencias, y pedir una confirmación única. No voy a ejecutar el merge por inferencia.

--- METODO TITAN ---
Accion delicada: SI
Modo aplicado: TITAN FULL
Rubrica: 90/100 provisional, pendiente de decisión de integración
N/A declarados: 0
Review externo: CI externo verde; reviews humanas/independientes pendientes, silencio no es aprobación
Instrumento: GitHub Actions check runs 106448220581/106448220758 y brain-env Chromium; evidencia cruda en `docs/agents/evidencia/2026-09-21-corpus-close.json`
