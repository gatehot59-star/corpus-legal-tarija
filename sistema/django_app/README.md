# Corpus Django: aplicación privada, ejecución sintética

Decisión: `docs/adr/2026-09-21-corpus-django.md`. Contratos: `contracts/corpus_django.py`. Implementación aprobada en comentario80170047177490. Rama `titan/builder-corpus-django`, sin merge ni despliegue autorizado.

## Qué existe

Mesa HTML bajo `/corpus/`: login con sesión Django y CSRF, búsqueda autorizada, lectura de versión exacta y procedencia, referencias privadas sin copia de texto, reportes privados, logout servidor y restablecimiento de contraseña mediante token Django. Un operador prepara cuentas/grupos/colecciones/grants; no hay autorregistro ni admin público. Nunca se usa el login fixture del sistema anterior.

El lector integrado `sistema/api/version_text.py` se importa sin modificarlo. Soporta versiones HTML LexiVox secundarias, no fuentes arbitrarias ni una declaración de vigencia legal. La adaptación abre el archivo con O_RDONLY/O_NOFOLLOW, verifica SHA y deserializa los mismos bytes en SQLite query_only; evita la carrera entre verificar una ruta y abrir otra vez esa ruta. Esta es una desviación deliberada del `mode=ro` propuesto, no una modificación del lector.

## Arranque local sintético

Desde raíz del repositorio, Bash y Python3.12. No usa datos reales ni envía emails. El directorio temporal debe ser nuevo.

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

Abrir `http://127.0.0.1:8000/corpus/login/`. Cuenta ficticia `fixture-ana`, contraseña pública exclusivamente sintética `Synthetic-Corpus-Only-2026!`. `fixture-ben` tiene la misma contraseña ficticia pero NO grant: sirve para comprobar la denegación. Buscar `Artículo`, abrir el resultado, comprobar versión/procedencia, guardar, reportar y salir. Nunca habilitar el perfil synthetic para usuarios reales. Ctrl+C detiene solo este servidor.

## Aceptación reproducible

Con el entorno anterior, sin necesidad de iniciar servidor:

```bash
set -euo pipefail
/tmp/corpus-django-venv/bin/python manage.py check
/tmp/corpus-django-venv/bin/python manage.py makemigrations --check --dry-run
/tmp/corpus-django-venv/bin/python -m coverage run --source=corpus manage.py test corpus.tests --verbosity=2
/tmp/corpus-django-venv/bin/python -m coverage report --omit='*/tests/*,*/migrations/*' --fail-under=85
```

Medición local inicial: 35 tests (19 de acceso, 11 de flujo, 5 de recuperación), cobertura total de aplicación92%, excluyendo tests/migraciones. Recuperación80% individual: no se oculta con el agregado. Tres mutaciones de auth/CSRF/logout hicieron fallar sus tests. Gunicorn real atendió el recorrido HTTP completo en loopback; eso NO equivale a inspección visual o E2E con navegador.

## Configuración

`CORPUS_DB`: ruta absoluta al SQLite operativo, obligatoria; no el snapshot legal. `CORPUS_SECRET_KEY`: al menos40 caracteres, obligatoria fuera del test, provista por gestor de secretos; nunca enGit. `CORPUS_HOSTS`: hosts concretos separados por coma, sin wildcard; obligatoria fuera del test. `CORPUS_ORIGIN`: origen HTTPS fijo sin barra final para reset, obligatorio fuera del test. `CORPUS_TRUST_PROXY=yes`: solo si un proxy controlado elimina/sobrescribe X-Forwarded-Proto; por defecto no se confía en ese encabezado. `CORPUS_TEST_PROFILE=synthetic`: opt-in explícito para fixtures, HTTP local y correo en memoria; ausencia usa configuración restrictiva.

Sin perfil test: DEBUGFalse, cookies Secure/HttpOnly/SameSite, redirecciónHTTPS excepto liveness, HSTS, CSRF, CSP sin scripts ni conexiones externas, no-store y errores genéricos. El backend de correo real está deshabilitado deliberadamente: configurar proveedor requiere autorización separada. El reset se prueba con correo en memoria, NO se promete entrega real. No hay logging de URL/query/texto/password en Django o access-logGunicorn; métricas operativas y auditoría de cambios de política siguen pendientes de integración antes de producción.

## Política y límites

Usuario activo + epoch actual + policy no quarantined + membership habilitada + grant usuario/grupo/colección vigente y no revocado + colección habilitada con evidencia + versión no retirada. Staff/superuser no es bypass. La autorización precede lectura/snippets y se repite al leer/guardar/reportar. No se confía en X-User, X-Collection ni IDs de dueño enviados por el navegador.

Cambios administrativos de política se hacen mediante un operador autorizado y una transacción que actualice revision; para invalidación global también incrementar session_epoch. El lote no expone una consola administrativa ni autoriza alta de personas reales. Los modelos ORM están disponibles para la futura administración aprobada. El contenido ya entregado en una respuesta no puede retirarse retroactivamente del cliente.

Consulta1..128caracteres/256bytes; página1..20; offset0..10000. Lectura1..10000caracteres con SHA completo. Feedback1..2000caracteres, categorías extraction/metadata/access/other, sin adjuntos. Catálogo de búsqueda máximo200 locators autorizados, presupuesto2millones de caracteres/5segundos, snapshot64MiB. Exceso produce503, nunca resultados truncados fingiendo completitud. Escaneo lineal: no es un buscador nacional escalado ni un benchmark10x. Lista de referencias no paginada y reportes muestran20recientes; ampliar eso requiere prueba de carga y UX, no inventar capacidad.

Login/reset/reportes:10intentos por IP/purpose/minuto persistidos; no se usa X-Forwarded-For. Detrás de un proxy compartido puede convertirse en un límite común y necesita política de rate-limit de staging, no activar confianza implícita. Existe potencial temporal de enumeración en recuperación propio del envío síncrono; respuesta y contenido son uniformes, tiempo no certificado.

## Recuperación: dos operaciones distintas

Comando `python manage.py recover_snapshot --help` describe todos los parámetros. Requiere backupSQLite consistente, digest completo, destino nuevo absoluto y revisión de política independiente superior al backup. `--backup`, `--sha256`, `--target`, `--current-policy-revision` sin reconciliación genera destino en cuarentena: purga sesiones, invalida grants y memberships, deshabilita colecciones e incrementa epoch. No toca la fuente ni inicia listener.

Reapertura offline requiere además `--reconcile-from` y `--authority-sha256`: snapshot independiente de la autoridad ACTUAL, con revisión exacta y epoch no retrocedido. El resultado parte de esa autoridad actual, NO restaura usuarios, passwords, grants ni retiradas del backup viejo. Solo importa referencias/reportes cuando usuario(id/username/date_joined) y locator(id/colección/UID/versión) son idénticos. Purga sesiones y sube epoch otra vez. Una fuente archivada no se vuelve actual por tenerSHA: el operador debe demostrar procedencia/actualidad por fuera del backup. Se prueban revocación y retirada preservadas.

El CLI es un adaptador explícito por rutas; aún no implementa el lookupUUID del Protocol RecoveryService. Tampoco crea un servicio programado de backup ni una autorización institucional. No ejecutar reconciliación real ni apuntar el servicio a su resultado sin aprobación de reapertura. El campo serve_authorized expresa el estado técnico de política de ese resultado, no concede permiso humano de despliegue.

Backups consistentes: detener escritores o usar SQLite backup API; copiar un archivo vivo con WAL no es un backup válido. Guardar evidencia actual/revisión por canal independiente, SHA, permisos0600 y verificar foreign_key_check/integrity_check. No colocar snapshot ni backup dentro del repo. No rollback a grants/sesiones viejos: ante incidente cerrar servicio, subir epoch/cuarentena en autoridad actual, investigar y recuperar a destino nuevo; nunca sobrescribir el archivo problemático.

## Contenedor y CI

Desde raíz: `docker build -f sistema/django_app/Dockerfile -t corpus-django:local .`. Multi-stage, imagenPython por digest verificado, usuario10001, no secretos copiados explícitamente. El build debe hacerse desde checkout limpio: el lote no incluye .dockerignore, por lo que no usar un árbol con bases/secretos locales. El Dockerfile copia solo app, contrato y lector, no toda la raíz. CI construye y ejecuta tests sin red en el contenedor, y no despliega. El workflow separado corre en todos los PRs, solo contents:read, checkout porSHA y persist-credentials:false; no cambia el workflow retenido enPR21.

`/corpus/live/`: proceso responde sin depender deDB. `/corpus/ready/` y `/corpus/health/`: policyDB presente y no cuarentena; no certifican cada snapshot ni envío de correo. TLS/reverse-proxy, alta de usuarios, muestra autorizada, backup custodiado, carga y ensayo institucional siguen siendo gates de staging/operación, no permisos inferidos delCI.

## Custodia y no interferencia

Evidencia cruda: `docs/agents/evidencia/2026-09-21-django-delivery.json`. Reporte: `docs/agents/respuestas/2026-09-21-django-delivery.md`. No se modifica ningún módulo legacy, ni PR1/17/18/19/20/21. No se retoma el laboratorioCI ni se levantan sus holds. Las revisiones independientes existentes siguen pendientes; las pruebas nuevas no las sustituyen.
