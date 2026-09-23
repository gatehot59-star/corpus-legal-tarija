# Link público CORPUS TARIJA: alias funcionando

## Pedido
El link debe quedar como CORPUS TARIJA, no el hash de Abacus.

## Qué se midió
- nginx de la VM ya declaraba `corpus-tarija.abacusai.cloud` como alias del sitio y el túnel lo sirve.
- GET por el alias: login 200 y live 200 sin tocar nada.
- POST login por el alias: 403, porque Django solo confiaba en el origen hash para CSRF.

## Cambio
- `settings.py`: nueva variable `CORPUS_EXTRA_ORIGINS` (orígenes HTTPS adicionales, explícitos, separados por coma, fail-closed). Commit `8b5c6a6`.
- VM: `/etc/corpus-django-staging.env` con `CORPUS_EXTRA_ORIGINS=https://corpus-tarija.abacusai.cloud` (una sola línea; se limpió un duplicado). Backup en `/tmp/env.bak`.
- Staging redesplegado a `8b5c6a6`, servicio `active`.

## Evidencia cruda (sesión pública de Abraham por el alias)

```text
suite: Ran 54 tests ... OK
alias GET login: 200, live: 200
login_theme=1
csrf_len=32
login_post=302 -> https://corpus-tarija.abacusai.cloud/corpus/
ws_theme=1 ws_hero=1
doc=200 doc_prov=1   (decreto 13214 con su versión propia)
```

## Link que queda
https://corpus-tarija.abacusai.cloud/corpus/login/

El link viejo con hash sigue respondiendo: mismo servicio, dos nombres. No se retiró.

## NO MEDIDO
- No se pidió un dominio propio fuera de abacusai.cloud (p. ej. corpus.icca-engine.com); eso requiere DNS/Cloudflare del dominio y es otra tarea.
- CI del PR corre en GitHub; revisar antes de mergear. No se mergeó a `main`.

--- METODO TITAN ---
Accion delicada: SI (config de seguridad y env del servicio)
Modo aplicado: TITAN FULL
Rubrica: pendiente en PR
N/A declarados: producción, cuentas reales, SMTP y carga
Review externo: pendiente en PR; silencio no es aprobación
Instrumento: VM real + curl público con sesión de Abraham por el alias; evidencia cruda arriba
