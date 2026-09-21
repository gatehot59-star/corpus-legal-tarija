# Corpus main: browser runtime fix and VM acceptance

## Estado

La rama nueva parte del `main` resuelto en vivo como `01a9756e5fa6cbcd6c80f3b52cc396fdf9a0ff9f`, aunque el pedido mencionaba `069d61f8ea6ccc3506a2e87fd8a7a173b3efde1c`. Esa diferencia queda registrada, no se tapa. El head de esta entrega es `4f1e617ec49dad877017baeadf9fd2583380834c`, publicado en [PR26](https://github.com/gatehot59-star/corpus-legal-tarija/pull/26).

## Cambio

El login real de Chromium devolvía 403 porque `no-referrer` impedía la interacción same-origin esperada. Se cambió únicamente a `same-origin`. CSRF sigue activo. La regresión demuestra que un Origin same-origin sin Referer pasa y que `Origin: null` sigue rechazado. No se aceptan orígenes externos.

El entorno browser quedó reproducible: Playwright 1.63.0 y dependencias Python fijadas, Fontconfig y fuentes provisionadas por el workflow, Xvfb para la corrida headed y canal Chromium completo explícito para evitar el headless shell que había terminado en SIGTRAP por Fontconfig.

## VM acceptance

En el build VM aislado, sobre el head exacto, `pip check` no encontró dependencias rotas; `manage.py check` pasó; migraciones no mostraron drift; pasaron 39 tests en 5.409 s; cobertura de aplicación 93% con umbral 85%; la jornada browser completa terminó con exit 0. El runner comprobó además `server.wait(timeout=20)` después de terminar Gunicorn, así que el servidor temporal se detuvo limpio.

La jornada fue sintética y cubrió login, búsqueda protegida, lectura exacta/procedencia, referencia privada, reporte privado con escape XSS, logout/replay vencido, aislamiento Ana/Ben, móvil 390x844, recuperación, rechazo del token de un uso y revocación que bloquea lectura y oculta referencias.

## Límites

Esto no es deploy ni un servicio persistente: es la aceptación completa en la VM aislada solicitada, con Gunicorn temporal y datos sintéticos. No se usaron cuentas, datos ni correo reales. El merge a `main` sigue pendiente de tu confirmación explícita; PR17-21 no se reabrieron y el hold de PR18 no se tocó.

--- METODO TITAN ---
Accion delicada: SI
Modo aplicado: TITAN FULL
Rubrica: 90/100 provisional, pendiente de CI hosted y decisión humana de merge
N/A declarados: 0
Review externo: PR26 abierto, review solicitado; silencio no es aprobación
Instrumento: brain-env build VM, `docs/agents/evidencia/2026-09-21-main-browser-runtime-fix.json`, head `4f1e617ec49dad877017baeadf9fd2583380834c`
