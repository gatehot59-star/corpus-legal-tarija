# Corpus: cierre retomado, todavía bloqueado por browser CI

## Estado vivo

BRAIN retomó el cierre sobre los heads vivos. Abraham todavía no dejó observaciones nuevas en PR24: comentarios y reviews consultados devolvieron vacío. No esperé tareas operativas suyas para medir y corregir; sí queda pendiente su decisión humana de merge.

PR22 sigue abierto sobre `main`, head `ba9646bf89fecb2a2431e9708f876dd0966afe81`. PR23 sigue abierto, apilado sobre PR22, head `777ca6374989ac042ddf7cb8275a7e3c7bdf7da2`. PR24 sigue abierto, apilado sobre PR23, head final de esta vuelta `2c09af55e8448bb385a2211a7506631161dce603`.

## Qué hice

Mantuve el fix de login aprobado: `SECURE_REFERRER_POLICY=same-origin`, CSRF intacto, `Origin: null` rechazado y regresión causal. La suite del fix pasó39tests, check, drift de migraciones y93% de cobertura de aplicación.

Incorporé al entorno browser las cuatro piezas que pedía el cierre: pins exactos de Playwright; `fontconfig`, `fonts-dejavu` y `libfontconfig1`; `fc-cache` y `fc-match`; dependencias completas de Chromium con `playwright install --with-deps`; y un control Xvfb para no confundir un cierre headless con un fallo de aplicación. El runner ejecuta login, búsqueda, lectura/procedencia, referencia, feedback privado/XSS, logout/replay, aislamiento Ana/Ben, móvil, reset y retirada.

## Qué medí

La aceptación conectada real sigue siendo PASS para ese recorrido: Chromium153.0.8010.12 completó los checkpoints en servicio Gunicorn sintético temporal, incluida recuperación, password nuevo/viejo, token de un uso y retirada. Esa evidencia está en `docs/agents/evidencia/2026-09-21-browser-fix.json`.

La automatización hosted sigue RED. Hubo tres intentos con browser job:

- `106431822487`, head `dca10b7`: fontconfig instalado, browser failure.
- `106432577525`, head `4d71f0b`: fontconfig/Xvfb instalados, browser failure.
- `106433891305`, head `2c09af5`: fontconfig/Xvfb instalados, browser failure.

En paralelo, application job `106433079271` pasó compile, migraciones, 39 tests, cobertura y contenedor. No tengo lectura del log de pasos del browser por las restricciones actuales de la conexión; por eso no invento la causa. El TargetClosed local sigue registrado, pero no lo atribuyo automáticamente a los jobs hosted.

## Qué mergeé

**Nada.** PR22, PR23 y PR24 siguen abiertos. No salteé el hold de PR18 ni las revisiones independientes. No hubo despliegue, datos reales, credenciales, email saliente ni eventos del laboratorio.

## Qué queda bloqueado para Abraham

El merge de PR24 y su pila queda bloqueado por dos cosas concretas: el check browser hosted está rojo, y la decisión de merge requiere confirmación humana cuando las condiciones estén verdes. PR22 no se puede tratar como producto aceptado por separado porque el recorrido browser que lo consume fue corregido después en PR24. PR23 es evidencia, no una base para fingir verde.

## Siguiente acción concreta

Conseguir el log crudo del browser hosted o reproducir el mismo runner con la misma imagen, identificar el primer fallo real, corregir solo eso y rerunear el head exacto. Después: revisar checks de PR24, actualizar la base viva de la pila si corresponde, y recién ahí presentar a Abraham el lote exacto para confirmación de merge. No cerrar PR23 ni reordenar PR18/19/20 por arrastre.

--- METODO TITAN ---
Accion delicada: SI
Modo aplicado: TITAN FULL
Rubrica:84/100 provisional, no firma de integración
N/A declarados:0
Review externo: PR24 sin observaciones nuevas; no aprobación
Instrumento: brain-env local39tests/93%; Chromium conectado PASS; GitHub Actions API cruda preservada en `docs/agents/evidencia/2026-09-21-corpus-close.json`; hosted browser FAIL