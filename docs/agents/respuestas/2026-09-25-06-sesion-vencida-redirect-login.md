# Sesión vencida: redirect al login + sesión rodante de 8 horas

Fecha: 2026-09-25 (noche, America/Argentina). Rama `titan/ocr-human-review`.

## Síntoma reportado por varios usuarios

Tras unos minutos sin usar Corpus, con la ventana abierta, al volver aparecía
una página pelada con el texto "Solicitud no disponible." y nada más.

## Causa raíz (dos conjuntas)

1. `SESSION_COOKIE_AGE = 1800` con `SESSION_SAVE_EVERY_REQUEST = False`:
   la sesión moría 30 minutos después del login, sin importar la actividad.
2. `guarded` traducía la falta de sesión (`AUTHENTICATION_REQUIRED`) y el
   epoch viejo (`ACCESS_DENIED` desde `state_for`) a un 403 de texto plano
   en vez de redirigir al login.

## Arreglo

- `corpus/views.py`: `guarded` ahora redirige al login cuando el error es
  `AUTHENTICATION_REQUIRED`, o `ACCESS_DENIED` con sesión que necesita
  re-login (nuevo `needs_fresh_login`: sin identidad, epoch viejo, cuenta
  inactiva o política ausente/en cuarentena). Hace `logout()` antes.
- `config/settings.py`: `SESSION_COOKIE_AGE = 28800` (8 horas) y
  `SESSION_SAVE_EVERY_REQUEST = True`: la sesión se renueva con la
  actividad; expira solo tras 8 horas de inactividad.
  `SESSION_EXPIRE_AT_BROWSER_CLOSE = True` se mantiene (decisión de
  seguridad deliberada: cerrar el navegador cierra la sesión).

## Lo que NO cambió (verificado por tests)

- 403 acotado se mantiene para denegaciones con sesión sana: documento sin
  grant, versión retirada, abogado entrando a /empleados/.
- CSRF 403, throttle 429, integridad 503, errores de validación 400.
- El interruptor de época (`session_epoch`) sigue cerrando todas las
  sesiones cuando se decide.
- Link de reset usado y sesión vieja ahora redirigen al login (antes 403).

## Commits

- `04ca264` views.py: redirect al login en sesión vencida/epoch viejo
- `3ef4d5e` settings.py: sesión de 8 horas, renovación por actividad
- `65406af` test_access.py: asserts actualizados + 2 tests nuevos
  (epoch viejo → login; pin de sesión rodante de 8h)
- `c0e44af` test_workflow.py: sesión invalidada y link usado → login

## Verificación

- Suite completa en la VM: **78/78 OK** (76 anteriores + 2 nuevos).
- Despliegue: `systemctl restart corpus-django-staging.service`
  (sin bump de época: las sesiones vigentes se conservan).
- En vivo con navegador real: `GET /corpus/` sin sesión → pantalla de
  acceso (antes: "Solicitud no disponible."); login de `luz` funciona y
  llega a su panel.
