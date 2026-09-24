# Revisión íntegra de la interfaz: fallas medidas y corregidas

## Pedido
El usuario reportó en staging: textos que se sobreponen, caracteres y botones muy grandes, modo noche que no funciona. Pidió revisar el sistema íntegro y resolver.

## Auditoría medida (Playwright contra el staging público, sesión de Abraham)

Antes:
- Consola: `Refused to execute inline script ... Content Security Policy directive: "default-src 'none'"`. El modo noche era un script inline y el CSP lo bloqueaba: nunca pudo funcionar.
- Lectura en móvil 390px: ancho de página 654px, 33 elementos desbordados (hashes de 64 chars y URL de fuente sin quiebre en la tarjeta de procedencia).
- Botón `Buscar` estirado a 87x130px por la grilla del hero.
- Lectura con el UID crudo como título (`nac-ley-1178-1990-a01f769a` a 49.6px).
- Hero a 64px en desktop.

Después (mismo instrumento, mismo usuario):
- Consola sin errores.
- Tema: `data-theme=auto` → clic en Modo noche → `data-theme=dark`, fondo pintado `rgb(15,18,23)`, etiqueta cambia a `Modo claro`. Sin JavaScript: el tema es cookie de servidor (`corpus_theme`) + `prefers-color-scheme`; el CSP sigue sin permitir scripts.
- Lectura desktop 1280: 0 desbordes. Lectura móvil 390: 0 desbordes. Catálogo móvil: 0 desbordes.
- Botón `Buscar`: 89x42px.
- Título de lectura: título humano real (`Bolivia: Ley de Administración y Control Gubernamentales (SAFCO), 20 de julio de 1990`).

## Causa raíz del modo noche roto
El `BoundaryMiddleware` publica CSP `default-src 'none'` sin `script-src`, por diseño. La primera versión de la UI metió un `<script>` inline para el tema: el navegador lo rechazó siempre. Se reemplazó por un POST `/corpus/theme/` que fija cookie `corpus_theme` (HttpOnly, SameSite=Lax, Secure fuera de test) y las plantillas leen la cookie vía `request.COOKIES`. `prefers-color-scheme` cubre el modo automático.

## Falla de seguridad que introduje y corregí en la misma sesión
El formulario del tema llevaba un token CSRF por render y rompió la uniformidad byte a byte de la respuesta de recuperación de contraseña (anti-enumeración). El test `test_password_reset_uniform_and_old_session_invalidated` lo agarró: 51 tests, 1 falla. Corregido omitiendo el toggle en la pantalla de confirmación (`mode == "sent"`). Suite final: `Ran 51 tests ... OK`.

## Cambios
- `workspace.html`, `login.html`: reescritos sin scripts, wrap de hashes/URLs, `min-width:0` en grillas, tamaños acotados, título humano.
- `views.py`: nueva ruta `theme` (POST, valores light/dark/auto, `next` solo local) y `doc_title` en lectura.
- `urls.py`: ruta `theme/`.
- `test_ui.py`: tema por cookie, rechazo de valores inválidos y redirect externo, ausencia de `<script>` en todas las páginas, título humano.
- Staging redesplegado a `c1f799d`, servicio `active`, público 200.

## NO MEDIDO
- Contraste WCAG formal (ratios) no medido; los pares de color se eligieron conservadores.
- CI del PR corre en GitHub al momento del commit; revisar checks antes de mergear.
- No se mergeó a `main`.

--- METODO TITAN ---
Accion delicada: SI (servicio staging reiniciado, nueva ruta POST)
Modo aplicado: TITAN FULL
Rubrica: pendiente en PR
N/A declarados: producción, cuentas reales, SMTP y carga
Review externo: pendiente en PR; silencio no es aprobación
Instrumento: Playwright real contra staging público + suite Django 51 tests en VM; evidencia cruda arriba
