# Integración full del Corpus real en Django staging

## Pedido
Continuar hasta dejar integrado el Corpus real completo en el servicio Django staging y verificar el sistema de punta a punta.

## Herramientas declaradas
Se usaron GitHub Contents, el túnel VM `scripts/acceso/vm-corpus.sh` y Chromium público mediante Playwright. Se desplegaron cambios en `/opt/corpus-django-staging` y se reinició solo `corpus-django-staging.service`. No se modificó la base original del Corpus.

## Correcciones realizadas

La primera suite del branch nuevo dio `Found 39 test(s)` pero terminó con 1 failure y 3 errors: el adapter había endurecido campos que el fixture sintético no contiene, había eliminado el módulo `time` que el test parchea y había intentado FTS sobre un snapshot sintético sin tabla `chunks`. Se corrigió el adapter para aceptar la procedencia sintética existente, el lector para señalar snapshot sin FTS y el servicio para conservar el fallback acotado de exact reads y su presupuesto temporal.

## Qué se midió después

- Suite Django: `Ran 39 tests in 1.011s`, `OK`.
- Servicio: `active`.
- Health loopback: HTTP 200.
- Chromium público posterior al fix: Ana login HTTP correcto, búsqueda real `ley`, resultados paginados, lectura exacta HTTP 200 y procedencia visible.
- Documento leído: `dep-tar-compilado-de-sin-numero-2010-0cc4b4a2`.
- Versión exacta: `6d34496cfcfba071ede1193ccbaa4506ea3a400ef45d19a2acb469507b8e19ae`.
- SHA de fuente: `0cc4b4a2f21be21002a741ceebdbc27f3e65799daca8177ac3e695bee755d053`.
- Extensión: `18.323` caracteres.
- Reset de cuenta público: solicitud uniforme, token sintético de un uso, cambio de contraseña, login nuevo correcto y replay del token HTTP 403.
- Expiración server-side: 10 sesiones expiradas; navegación protegida posterior HTTP 403.
- Logout/replay y aislamiento Ana/Ben ya verificados en la misma jornada real.

## Evidencia cruda

```text
Found 39 test(s).
System check identified no issues (0 silenced).
.......................................
Ran 39 tests in 1.011s
OK
active
live=200
read 200 ... uid dep-tar-compilado-de-sin-numero-2010-0cc4b4a2
search 200 ...
reset form accepted token
reset password -> /corpus/login/
reused reset token -> HTTP 403
expired_sessions 10
protected after expiry -> HTTP 403
```

## Archivos generados

- `sistema/api/version_text.py`, commit `6bbd9069b06cd5c0a07298b9ca65e59b8c12aeef`.
- `sistema/django_app/corpus/reader.py`, commit `91d9ccf9fb3758da6065d0aa503095a38c5dc666`.
- `sistema/django_app/corpus/services.py`, commit `c7c1630ce8ed3689fba47212f60b050206b93157`.
- Este recibo, commit posterior en `titan/adapt-real-corpus`.
- PR de integración: https://github.com/gatehot59-star/corpus-legal-tarija/pull/28.

## Estado

Integración full de staging: VERDE dentro del alcance medido. La base original permanece intacta y la colección activa usa el snapshot adaptado de 6.079 documentos.

## NO MEDIDO

Carga/concurrencia formal, accesibilidad visual formal, SMTP real, cuentas reales, rollback ejercido y despliegue productivo. El merge a `main` sigue siendo decisión humana después de revisión del PR.

--- METODO TITAN ---
Accion delicada: SI (frontera de confianza y servicio público)
Modo aplicado: TITAN FULL
Rubrica: 92/100 provisional, pendiente de revisión independiente
N/A declarados: SMTP real, cuentas reales, producción, carga formal y rollback ejercido no son parte del staging autorizado
Review externo: PR28 abierto; review automático pendiente, silencio no es aprobación
Instrumento: suite Django + Chromium público Playwright + VM tunnel; salida cruda transcrita arriba y enlaces a commits/PR
