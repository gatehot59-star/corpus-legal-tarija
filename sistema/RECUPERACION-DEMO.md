# Recuperar una demo: copiar no autoriza a servir

Este comando prepara una **copia sintética en cuarentena**. No restaura Corpus
vivo, no reabre accesos y no modifica el origen. No usar sobre datos reales.
Antecedente medido: `docs/agents/respuestas/2026-09-18-09-restore-reabre-accesos.md`.

## Contrato y arquitectura

`demo_restore.restore(source, destination, isolated_demo=True,
source_stopped=True) -> dict` retorna el manifiesto, o falla con `ValueError`,
`OSError` o `sqlite3.Error`. El CLI traduce esos errores a exit2 sin datos SQL
ni credenciales. Exit0 significa **copia en cuarentena**, no permiso de acceso.

Flujo: origen frío -> imágenes de bytes acotadas -> validación de fixture
existente -> destino exclusivo0700 -> barrera primero -> dos copias0600 ->
quitar marcador, purgar sesiones y deshabilitar colecciones -> manifiesto.

Archivos: `sistema/api/demo_restore.py` (comando), `tests/test_demo_restore.py`
(banco con CLI real), este runbook y `.github/workflows/clean-snapshot.yml`
(paso dedicado). Sin dependencias nuevas; Python/SQLite/POSIX de la demo.
No cambios en el servidor existente, la autenticación o el formato del candidato.

## Uso

1. Detené el proceso que usa el origen. Usá únicamente un directorio generado
   por `demo_aislada.py init`, con sus dos archivos SQLite, completo y marcado.
   Conservá el backup original privado; incluye verificadores de contraseña y
   hashes de sesiones aunque sus cuentas sean ficticias.
2. Elegí un destino que no exista y cuyo padre exista, sin symlinks, separado
   del origen (tampoco dentro). No se permite sobreescribir ni reanudar parciales.
3. Ejecutá desde la raíz del repo:

```sh
python3 sistema/api/demo_restore.py \
  --source ./corpus-demo-local \
  --destination ./corpus-demo-recuperada \
  --isolated-demo --source-stopped
```

El manifiesto JSON devuelve `status: quarantined`, `serve_authorized: false`,
hashes SHA256 de origen y salida, inventario de tablas y acciones realizadas.
No incluye contraseñas, hashes de credenciales ni tokens. Los hashes son
integridad de bytes, **no firma ni autenticación del backup**.

`--source-stopped` es una declaración del operador, NO una medición ni un lock
compartido con el servidor. Si no podés asegurar que está detenido, NO lo uses.
Se compara el origen antes/después de validar y copiar para detectar cambios;
eso no hace transaccional una copia concurrente de dos bases. Rechaza sidecars.

## Dos barreras y un resultado que no se reabre solo

`RESTORE-QUARANTINE.json` se crea ANTES de copiar las bases. El lanzador actual
rechaza ese tercer archivo antes de escuchar, incluso si la copia queda parcial.
Además se vacía `login_environment`, se purgan sesiones y se deshabilitan todas
las colecciones en una transacción sobre la copia. Se verifican las tres
postcondiciones antes de emitir éxito.

Los permisos, retiradas, verificadores de contraseña, presupuesto y reloj del
backup se preservan para inspección, **no se declaran vigentes**. Restaurar una
sesión o reiniciar el presupuesto/clock no recupera eventos posteriores perdidos.
El candidato debe conservar exactamente sus bytes; sessions.db cambia
intencionalmente para bloquearlo. El manifiesto distingue ambos hashes.

El intento siguiente debe devolver exit2 sin evento `ready`:

```sh
python3 sistema/api/demo_aislada.py serve \
  --directory ./corpus-demo-recuperada --isolated-demo
```

**No borres el manifiesto ni reinsertes el marcador para “arreglar” ese error.**
Es el resultado esperado. No existe `--reopen`, migración ni activación
automática. Reabrir requiere un procedimiento distinto con reconciliación
confiable del estado actual y autorización explícita, fuera de esta entrega.

## Fallos y límites

No se borra una salida parcial. Queda para inspección en cuarentena; para repetir
elegí otro destino nuevo. No se elimina ni reemplaza automáticamente trabajo.
El destino requiere0700; cada archivo0600. Origen regular, propio, sin links,
sin sidecars, máximo8MiB por base (16MiB de imágenes). No escalar el límite
para convertir esto en restaurador productivo. A diez veces los datos sigue
siendo un instrumento de fixture acotado, no un sistema de backups.

Operador/UID/root confiables: no protege contra alguien que reemplace archivos
o quite ambas barreras con esos permisos. Las comparaciones detectan cambios
observables, no todas las carreras ni ABA. Los fsync de archivos no certifican
corte de energía, atomicidad del par, RPO/RTO ni almacenamiento externo.

No servidor, credenciales reales, red externa, permisos nuevos o SQL dinámico
con entrada del usuario. No backup en caliente ni certificación jurídica,
TLS, recuperación productiva o cierre de M03/F05.

## Verificación

```sh
python3 -m py_compile sistema/api/demo_restore.py tests/test_demo_restore.py
python3 tests/test_demo_restore.py
```

El CI ejecuta este bloque con timeout120s como paso separado, además de las
97 pruebas previas. El banco comprueba el CLI y la negativa del lanzador real;
también fallos parciales, origen cambiante, corrupción y rutas peligrosas.
El caso de backup viejo conserva la fuente y comprueba sesiones vacías,
colecciones apagadas y rechazo aun quitando solamente el manifiesto en el
fixture de prueba. Otro caso repone el store viejo sólo en el fixture y verifica
que el manifiesto solo mantiene el bloqueo. No confundas esas inyecciones del
banco con instrucciones para reabrir.
