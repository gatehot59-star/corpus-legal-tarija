# Fix de versiones del catálogo + despliegue de la UI nueva en staging

## Pedido
El usuario reportó que seguía viendo la interfaz vieja y que varios documentos daban error, con esta URL real:
`/corpus/read/?collection=89701639-ffaf-41be-9c94-5d291d1e3c6f&uid=nac-decreto-ley-13214-1975-faf9d1e5&version=6d34496c...`

## Causa raíz medida
1. La UI nueva estaba solo en PR31, nunca desplegada en staging. Por eso se veía lo mismo.
2. `browse_snapshot` estampaba en TODOS los documentos del catálogo la `version_sha256` del primer locator. La colección real tiene 6.079 versiones exactas (una por documento), así que solo abría el primero; el resto fallaba autorización (403). El smoke anterior pasó porque probó justo el primer documento.

## Cambios
- `reader.py`: `browse_snapshot` recibe mapa uid→versión y estampa la versión propia de cada documento. Commit `035272d5`.
- `services.py`: construye `{uid: version}` desde los locators elegibles. Commit `c960e9ad`.
- `test_catalog.py`: actualizado al mapa uid→versión. Commit `bdc04663`.
- Staging actualizado a `bdc0466` (rama `feat/ui-professional-polish`) y servicio reiniciado con sudo.

## Evidencia cruda (VM real, sesión pública de Abraham)

```text
servicio: active, live=200, public=200
login_theme=2            (login nuevo servido)
login_post=302 -> /corpus/
ws_theme=2 ws_hero=1     (workspace nuevo servido)
doc_nac13214=403         (link VIEJO con versión ajena: rechazo correcto)
cat_versiones_distintas=21  cat_items=20   (cada documento con su versión)
doc_segundo=200 doc2_prov=1                 (otro documento del catálogo abre)
row=('nac-decreto-ley-13214-1975-faf9d1e5', 'cd4d3b446189336248463464f88708d29c925388a3558dbc0bdee3c30d1caeb7')
doc_13214_real=200 doc4_prov=1 doc4_texto=Seguridad Social   (con su versión propia abre)
```

## Lo que debe saber el usuario
Los links generados antes del fix (como el que pegó) llevan versión ajena y van a seguir dando 403. Hay que entrar de nuevo desde el catálogo o la búsqueda: los links nuevos ya llevan la versión correcta de cada documento.

## NO MEDIDO
- Suite Django y Chromium completos no se re-ejecutaron en esta sesión; CI del PR corre en GitHub.
- No se mergeó a `main`. PR31 ahora contiene la navegación (PR30) + UI + este fix.
- Los títulos en resultados de búsqueda muestran el UID (el locator guarda uid como título en la colección real); el catálogo sí muestra el título humano.

--- METODO TITAN ---
Accion delicada: SI (servicio staging reiniciado)
Modo aplicado: TITAN FULL
Rubrica: pendiente en PR
N/A declarados: producción, cuentas reales, SMTP y carga no son objeto de esta feature
Review externo: pendiente en PR; silencio no es aprobación
Instrumento: VM real via vm-corpus.sh + curl público con sesión de Abraham; evidencia cruda arriba
