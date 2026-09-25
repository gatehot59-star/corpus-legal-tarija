# Cierre de sesiones viejas y redespliegue

## Acción autorizada

El usuario pidió: "Forzá el cierre de sesiones viejas y redeployá".

## Acción ejecutada

1. **Cierre masivo de sesiones**: `Session.objects.all().delete()`, 38 sesiones eliminadas.
2. **Bump de época de política**: `PolicyState.session_epoch` 2 → 3, para que cualquier sesión recuperada igual quede inválida.
3. **Redespliegue**: checkout del commit `0e0b688` (con el recibo de verificación), `systemctl restart corpus-django-staging.service`.
4. **Salud**: `/corpus/live/` 200, `/corpus/ready/` 200.

## Verificación en vivo (login fresco)

- Login `luz` → `/empleados/` (rol correcto).
- `/corpus/` con sesión nueva: 200, `hero-search-main` presente, 7 selects (catálogo + búsqueda + reporte).
- Búsqueda `ley`: `?q=ley&source=&rubro=&tipo=`, `Cita interna` visible, 10 tarjetas.

## Efecto para el usuario

Toda sesión anterior quedó invalidada en el servidor: ya no hace falta borrar cookies manualmente. Entrá de nuevo con `luz`/`223344` al mismo link y vas a ver la versión nueva. Tu cuenta sigue entrando al portal de empleados por rol; el Corpus de abogados queda en `/corpus/`.

--- METODO TITAN ---
Accion delicada: SI (cierre masivo de sesiones + restart, autorizado explícitamente)
Modo aplicado:   TITAN FULL
Rubrica:         39/40 -> 97.5/100
N/A declarados:  1 (external review not issued)
Review externo:  no emitido (deuda declarada)
Instrumento:     PolicyState epoch 2->3, Session 38->0, systemctl restart, curl 200, Playwright fresh login
