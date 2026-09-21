# Corpus Django: aplicación privada, validada con datos sintéticos

Arquitectura: `docs/adr/2026-09-21-corpus-django.md`. Contratos: `contracts/corpus_django.py`. Lote32 aprobado en comentario80170047177490. PR22, rama `titan/builder-corpus-django`. No merge ni despliegue.

## Arranque reproducible

Desde raíz del repo, Bash/Python3.12. Solo fixtures. No envía emails ni usa bases reales.

```bash
set -euo pipefail
python3 -m venv /tmp/corpus-django-venv
/tmp/corpus-django-venv/bin/pip install -r sistema/django_app/requirements.txt
export CORPUS_TEST_PROFILE=synthetic
export CORPUS_DB="$(mktemp -d)/application.sqlite3"
cd sistema/django_app
/tmp/corpus-django-venv/bin/python manage.py migrate --noinput
/tmp/corpus-django-venv/bin/python manage.py provision_fixture --snapshot "$(dirname "$CORPUS_DB")/snapshot.sqlite3"
/tmp/corpus-django-venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 1 --timeout 30
```

Abrí `http://127.0.0.1:8000/corpus/login/`. Usuario ficticio `fixture-ana`, contraseña pública de prueba `Synthetic-Corpus-Only-2026!`. `fixture-ben` comparte la contraseña ficticia pero NO tiene grant. Buscar `Artículo`, abrir, verificar SHA/procedencia, guardar referencia, reportar privadamente y salir. Ctrl+C detiene este servidor. Nunca usar perfil synthetic con personas/datos reales.

## Pruebas

Con el mismo entorno y desde sistema/django_app, sin iniciar servidor:

```bash
set -euo pipefail
/tmp/corpus-django-venv/bin/python manage.py check
/tmp/corpus-django-venv/bin/python manage.py makemigrations --check --dry-run
/tmp/corpus-django-venv/bin/python -m coverage run --source=corpus manage.py test corpus.tests --verbosity=2
/tmp/corpus-django-venv/bin/python -m coverage report --omit='*/tests/*,*/migrations/*' --fail-under=85
```

Última ejecución local:38tests (19acceso,11flujo,8recuperación),93% de líneas de aplicación excluyendo tests/migraciones. Recuperación83% individual. Tres mutantes de auth/CSRF/logout rechazados antes de ampliar recuperación. Gunicorn real recorrió login/búsqueda/lectura/guardado/reporte/logout en loopback. Inspección visual/E2E con navegador NO MEDIDA.

CI del código2cd4ca7ebe23422d617d3e5c741e084a4cdfeedf: https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35594375708/job/106315738125, success, siete pasos, incluyendo construir y probar contenedor no-root sin red. Este README y el reporte son posteriores y documentales; no atribuir automáticamente el resultado anterior a un SHA nuevo.

## Funciones y política

UI HTML `/corpus/`, sesiones y CSRF Django, logoutPOST, recuperación de contraseña por token Django, búsqueda autorizada, lector exacto existente, referencias propias sin texto y feedback privado. No autorregistro, admin público, JWT/localStorage ni sesión fixture reutilizada. Operadores autorizados administran modelosORM, no existe todavía consola de alta real.

Autorización por petición: usuario activo, epoch actual, policy no cuarentena, membership habilitada, grant vigente/no revocado para usuario/grupo/colección, colección habilitada con evidencia, locator no retirado. Staff/superuser no salta controles. Identidad y dueño nunca vienen de X-User/X-Collection. Lectura/snippets ocurren después del filtro, y guardar/reportar reautorizan. Cambios de política deben actualizar revision en la misma transacción; subir session_epoch para invalidación global. No se pueden retirar bytes ya enviados al cliente.

`sistema/api/version_text.py` se importa sin editar. Solo versiones HTML LexiVox secundarias; no se certifica vigencia jurídica ni carácter oficial. El adaptador abre O_RDONLY/O_NOFOLLOW/O_NONBLOCK, verificaSHA y deserializa esos mismos bytes en SQLite query_only/trusted_schemaOFF. Así no reabre una ruta sustituible tras el hash. Este reemplazo del mode=ro propuesto es deliberado y documentado.

Límites: q1..128caracteres/256bytes, página1..20, offset0..10000; lectura1..10000caracteres y SHA completo; feedback1..2000caracteres, categorías extraction/metadata/access/other, sin adjuntos. Búsqueda máximo200locators,2millones de caracteres,5segundos,snapshot64MiB. Exceso503 sin truncamiento silencioso. Escaneo lineal: capacidadnacional/carga10x no medida. Referencias sin paginación y20reportes recientes son límites actuales, no capacidad ilimitada.

## Entorno y seguridad

CORPUS_DB: ruta absoluta obligatoria de SQLite operativo, distinta del snapshot. CORPUS_SECRET_KEY: mínimo40caracteres desde gestor de secretos, obligatoria fuera de test, nunca enGit. CORPUS_HOSTS: hosts explícitos separados por coma sin wildcard. CORPUS_ORIGIN: origenHTTPS fijo sin barra final para reset. CORPUS_TEST_PROFILE=synthetic: opt-in local, fixture y correo en memoria; ausencia usa perfil restrictivo. CORPUS_TRUST_PROXY=yes: solo para proxy controlado que elimine/sobrescriba X-Forwarded-Proto; por defecto no se confía en él.

DEBUGFalse, cookiesSecure fuera de test/HttpOnly/SameSite, HTTPS/HSTS, CSRF, no-store, CSP sin scripts/conexiones externas, errores genéricos. Correo real deliberadamente deshabilitado: backenddummy; reset solo probado con correo en memoria. Configurar proveedor requiere autorización. El contenido de respuesta de reset es uniforme, NO se certifica igualdad temporal por el envío síncrono.

Login/reset/feedback:10intentos por IP/purpose/minuto persistidos con digestHMAC, sin confiar en X-Forwarded-For. Proxy compartido requiere política de rate-limit de staging. No se registran URLs/query/texto/password en Django ni access-logGunicorn. Métricas operativas y auditoría de cambios de política siguen pendientes antes de producción.

## Recuperación y rollback

`python manage.py recover_snapshot --help` enumera parámetros. FuenteSQLite consistente y digest completo; destino nuevo absoluto nunca sobrescrito. `--backup`, `--sha256`, `--target`, `--current-policy-revision` exige revisión independiente superior a backup y produce cuarentena: purga sesiones, revoca grants, deshabilita memberships/colecciones y sube epoch. No modifica fuente ni inicia listener. FIFO/symlink rechazados sin bloqueo.

Reconciliación explícita añade `--reconcile-from` y `--authority-sha256`: autoridad ACTUAL independiente, revisión exacta, epoch no retrocedido, no cuarentena. Resultado parte de autoridad actual; no recupera usuarios/passwords/grants/retiradas viejos. Solo incorpora referencias/reportes con identidad(id/username/date_joined) y locator(id/colección/UID/versión) idénticos, purga sesiones e incrementaepoch. SHA no prueba actualidad: custodio debe acreditarla por otro canal. serve_authorized expresa estado técnico del resultado, no aprobación humana de despliegue. No apuntar servicio real a ese resultado sin gate de reapertura.

`corpus.services.OfflineRecovery` implementa restore_quarantined(backupUUID,revision) con registro inyectado por operador: UUID->(ruta,digest,destino). No hay rutaHTTP ni descubrimiento arbitrario. Este adaptador CI-probado cierra la carencia publicada en la primera evidencia histórica.

Backups: SQLite backupAPI o escritores detenidos; nunca copiar archivo vivo ignorandoWAL. Mantener política/revisión por canal independiente, SHA, permisos0600 y comprobacionesdeintegridad. No guardar backups/snapshots enGit. Incidente: cerrarservicio, subir epoch/cuarentena en autoridad actual, conservar archivo problemático y recuperar a destino nuevo. Nunca hacer rollback a sesiones/grants viejos.

## Contenedor y operación

Desde raíz limpia: `docker build -f sistema/django_app/Dockerfile -t corpus-django:local .`. Multi-stage, Python por digest, usuario10001, HEALTHCHECK. Usar checkout limpio: no hay .dockerignore en el lote y no deben existir bases/secretos en el directorioapp. Solo copia app, contrato y lector. CIcorre en todos losPRs, contents:read, checkoutSHA/persist-credentials:false; construye y prueba sin red, NO despliega ni cambia workflowPR21.

`/corpus/live/` mide proceso, `/corpus/ready/` y `/corpus/health/` policyDB no cuarentena; no certifican todos los snapshots ni correo. TLS/proxy, cuentas reales, muestra autorizada, carga, backupcustodiado y ensayo institucional conservan sus gates. No se alteraron legacy niPR1/17/18/19/20/21, no se reanudó laboratorio, no se levantó revisiónindependientePR18/logout.

## Evidencia y deuda

`docs/agents/evidencia/2026-09-21-django-delivery.json`:69.136bytes crudos base64+lzma, SHA verificado desdeGit. `docs/agents/respuestas/2026-09-21-django-delivery.md`: actualización38tests,CI y score84/100,0N/A, no firma deproducción. Los límites anteriores son explícitos; reviewCopilot pedido y reviews vacías no equivalen a aprobación.
