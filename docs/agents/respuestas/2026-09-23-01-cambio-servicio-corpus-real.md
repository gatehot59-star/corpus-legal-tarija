# Cambio del servicio Django al Corpus real adaptado

## Pedido
Cambiar el servicio Django staging para usar la copia adaptada del Corpus real completo.

## Herramientas declaradas
Se usó el túnel verificado `scripts/acceso/vm-corpus.sh` para ejecutar mediciones y cambios en la VM. Se usaron GitHub Contents para publicar el adapter, el lector FTS y esta evidencia. Se reinició únicamente `corpus-django-staging.service`; no se tocó `corpus-api` ni la base original `/home/ubuntu/rag-abogacia-v7.db`.

## Qué se midió

- Snapshot adaptado: `341172224` bytes, propietario `ubuntu:ubuntu`, modo `0400`.
- SHA-256 del snapshot: `d6b5c2f381a1276cf537264a86906093c727b4ce4cf0149b737bf41ad3490a52`.
- Integridad SQLite: `ok`.
- Registros: `6079` documentos y `6079` versiones exactas adaptadas.
- Catálogo Django activo: una colección real, `6079` locators.
- Servicio: `active`.
- Health loopback: `live_http=200`.
- Health público: `public_live=200`.
- Smoke real interno: Ana obtuvo lectura HTTP `200` sobre `dep-tar-ley-departam-472-2023-94831274`; búsqueda `ley` obtuvo HTTP `200` después de sustituir el límite sintético de 200 locators por el índice FTS verificado.

## Evidencia cruda

```text
snapshot: ubuntu ubuntu 400 341172224 /var/lib/corpus-django-staging/corpus-adapted-real-20260923.db
d6b5c2f381a1276cf537264a86906093c727b4ce4cf0149b737bf41ad3490a52  /var/lib/corpus-django-staging/corpus-adapted-real-20260923.db
ok
6079 6079
89701639ffaf41be9c945d291d1e3c6f d6b5c2f381a1276cf537264a86906093c727b4ce4cf0149b737bf41ad3490a52 6079
active
live_http=200
read 200 ... uid dep-tar-ley-departam-472-2023-94831274
search 200 ...
public_live=200
```

## Archivos generados

- `sistema/django_app/corpus/management/commands/adapt_real_corpus.py`, commit `0dcb422bfa9a886bf825a6675aafbcc5f44cf287`.
- `sistema/api/version_text.py`, commit `f2bedb3fe0d2ba73790ac2dca864e460023c5246`.
- `sistema/django_app/corpus/reader.py`, commit `fbcb307177d4a71f687b79140a5f052cbdf41c95`.
- `sistema/django_app/corpus/services.py`, commit `6425788735612404e6aa6575226478a05a2a44dc`.
- Este recibo, commit posterior en `titan/adapt-real-corpus`.

## NO MEDIDO

No se ejecutó todavía una jornada Chromium pública completa sobre datos reales, ni prueba de carga/concurrencia. El acceso operativo conserva las cuentas sintéticas `fixture-ana` y `fixture-ben`; no se habilitaron cuentas reales, correo real ni despliegue productivo.
