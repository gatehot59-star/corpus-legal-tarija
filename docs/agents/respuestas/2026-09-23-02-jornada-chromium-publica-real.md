# Jornada Chromium pública sobre datos reales

## Pedido
Ejecutar la jornada Chromium pública completa sobre el servicio Django staging usando el Corpus real adaptado.

## Herramientas declaradas
Se usó Chromium real mediante el servicio Playwright conectado al gateway y el túnel VM mediante `scripts/acceso/vm-corpus.sh`. Se corrigió y desplegó la configuración CSRF de origen HTTPS antes de repetir la jornada. El servicio reiniciado fue únicamente `corpus-django-staging.service`.

## Qué se midió

- Primer POST público de login: HTTP 403 CSRF, con `Origin` y `Referer` same-origin; causa: el servicio activo no tenía `CSRF_TRUSTED_ORIGINS`.
- Fix publicado en `sistema/django_app/config/settings.py`, commit `6c346a5454c1a38a10b7bc8e43c399a2adbf4387`, desplegado en VM.
- Servicio posterior: `active`; `/corpus/live/` loopback HTTP 200; `/corpus/live/` público HTTP 200.
- Ana inició sesión públicamente con Chromium.
- Búsqueda real `ley`: resultados visibles, paginación disponible y locators reales.
- Lectura exacta: HTTP 200; documento `dep-tar-compilado-de-sin-numero-2010-0cc4b4a2`; versión `6d34496cfcfba071ede1193ccbaa4506ea3a400ef45d19a2acb469507b8e19ae`; SHA de fuente `0cc4b4a2f21be21002a741ceebdbc27f3e65799daca8177ac3e695bee755d053`; 18.323 caracteres.
- Procedencia visible: fuente secundaria y vigencia jurídica no medida.
- Referencia privada guardada y visible para Ana.
- Reporte privado enviado y visible: `Jornada Chromium real: OCR visible con artefactos en el encabezado; registrar para revisión.`
- Logout ejecutado; replay de la URL protegida devolvió HTTP 403.
- Ben inició sesión públicamente; búsqueda `ley` devolvió `Sin resultados autorizados para esta consulta` y no mostró referencias ni reportes de Ana.

## Evidencia cruda

```text
POST /corpus/login/ => 403 (antes del fix)
CSRF_TRUSTED_ORIGINS = [CORPUS_ORIGIN] if CORPUS_ORIGIN.startswith("https://") else []
deployed commit: 6c346a5454c1a38a10b7bc8e43c399a2adbf4387
active
live=200
public_live=200
Ana login -> /corpus/
search ley -> /corpus/?q=ley
read -> HTTP 200
reference -> visible in Tus referencias
private feedback -> 23 de septiembre de 2026 a las 10:09 · extraction · received
logout -> /corpus/login/
replay protected URL -> HTTP 403
Ben search ley -> Sin resultados autorizados para esta consulta
Ben references -> Todavía no hay referencias disponibles.
Ben reports -> No enviaste reportes.
```

## Archivos generados

- `sistema/django_app/config/settings.py`, commit `6c346a5454c1a38a10b7bc8e43c399a2adbf4387`.
- Este recibo, commit posterior en `titan/adapt-real-corpus`.

## NO MEDIDO

No se probaron carga/concurrencia, accesibilidad visual formal, recuperación de cuenta ni expiración de sesión en esta jornada. Sigue siendo staging con cuentas sintéticas; no hay correo real ni despliegue productivo.

--- METODO TITAN ---
Accion delicada: NO
Modo aplicado: TITAN FULL
Rubrica: N/A (jornada de aceptación operativa, sin cambio de contrato)
N/A declarados: código de producción, CI/CD, arquitectura e innovación no son objeto de esta jornada
Review externo: no aplica a la corrida; el fix CSRF queda pendiente de revisión/merge humano
Instrumento: Chromium público Playwright + VM tunnel, evidencia cruda en este archivo
