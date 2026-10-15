# Evidencia de la prueba viva de Corpus, 15 de octubre de 2026

Sujeto: https://corpus-tarija.abacusai.cloud/corpus/ . Cuenta sintética existente. Sin interacción con RuleX.

Este archivo publica resultados y extractos seleccionados, no los cuerpos HTML íntegros. Las respuestas completas fueron capturadas antes de resumir y quedan bajo permisos restringidos en brain-env porque incluyen formularios con tokens CSRF. No se publican contraseñas, cookies, tokens ni HTML privado de las cuentas de prueba.

## Custodia

Directorio de ejecución: `/workspace/corpus-live-20261015-3l_idyw4`.
Puntero de continuidad: `/workspace/corpus-live-20261015-current.txt`.
23 cuerpos de respuesta conservados. Todos los hashes registrados se recomputaron sobre los archivos guardados y coincidieron.

| Registro | Bytes | SHA-256 |
|---|---:|---|
| record.json, inicial e intacto | 60237 | 4081601e9c65c6d9deb42857c9be16e4e6095fc796a917c2b4fbca24b1468374 |
| correction.json, corrección separada | 9995 | af333d10db4bef1c65f8a65c6a0ff79cb241c2f0547c2c3de067e8124177797a |
| manifest.json | Ver archivo local | 43d605b7aa757475c69b1cd69b1aab27cefed2b4928365fd5020f5b8ad850f76 |

## Extractos del registro inicial

Ventana UTC: `2026-10-15T04:36:09.007493+00:00` a `2026-10-15T04:36:20.395353+00:00`.

```json
{
  "existing_synthetic_login": {"status": "PASS", "http": 200, "path": "/corpus/"},
  "codigo_procesal_civil": {"http": 200, "visible_result_cards": 3, "pagination": "Página 1 de 1", "known_target_present": true},
  "asistencia_familiar": {"http": 200, "visible_result_cards": 7, "pagination": "Página 1 de 1"},
  "source_filters_first_page": {
    "tsj_genesis": {"visible_cards": 10, "all_visible_labels_match": true},
    "tarija_gaceta": {"visible_cards": 10, "all_visible_labels_match": true},
    "lexivox_nacional": {"visible_cards": 10, "all_visible_labels_match": true}
  },
  "reading": {
    "page_label": "Página 1 de 100",
    "declared_range": "Caracteres 0 a 10000 de 396295",
    "body_characters": 10000,
    "body_sha256": "c05071daa7a24a6c693a67bf90d692104a9b9f76484a67ef8b56ffd59d92c9ae",
    "secondary_source_warning": true,
    "duplicate_visible_phrase_count": 2
  },
  "download": {
    "http": 200,
    "download_characters": 10000,
    "first_slice_matches": true,
    "full_text_hash_equals_version": false
  },
  "linked_source": {"http": 200, "contains_ley_439": true, "gratuidad_phrase_count": 1},
  "anonymous_read": {"final_http": 200, "final_path": "/corpus/login/", "reader_text_present": false},
  "search_snippets": {"literal_markup_in_visible_text": true, "rendered_mark_tags": 0}
}
```

La descarga observada es un tramo. Su hash no se presenta como verificación del documento entero ni la diferencia con el identificador de versión se etiqueta automáticamente como corrupción.

### Documento identificado

UID: `nac-codigo-439-2013-ad34a6a4`.
Versión: `90b0801b897b36a7d8a65fd3d901c31336d8dc6ad2a45e9cb4a132a2ed0b974c`.
SHA de fuente mostrado: `ad34a6a4a5193b2d64a1a4a4653ecc884df57292d26e0598af2154ea9a317bb9`.
Fuente enlazada: https://www.lexivox.org/norms/BO-L-N439.xhtml .

Lectura probada:
https://corpus-tarija.abacusai.cloud/corpus/read/?collection=89701639-ffaf-41be-9c94-5d291d1e3c6f&uid=nac-codigo-439-2013-ad34a6a4&version=90b0801b897b36a7d8a65fd3d901c31336d8dc6ad2a45e9cb4a132a2ed0b974c

## F01: contraste textual, extractos literales

Lector de Corpus:

```text
 causa, siempre que no afecten los principios del debido proceso y de la seguridad jurídica, de manera que se concluya la tramitación de la causa con la debida celeridad procesal.
Gratuidad. El pde la causa, siempre que no afecten los principios del debido proceso y de la seguridad jurídica, de manera que se concluya la tramitación de la causa con la debida celeridad procesal.
Gratuidad. El proceso civil es gratuito, siendo ésta la condición para hacer realidad el acceso a la justicia en condiciones de igualdad.
```

Página actual de LexiVox, texto extraído con espacios entre nodos:

```text
 causa, siempre que no afecten los principios del debido proceso y de la seguridad jurídica, de manera que se concluya la tramitación de la causa con la debida celeridad procesal. Gratuidad. El proceso civil es gratuito, siendo ésta la condición para hacer realidad el acceso a la justicia en condiciones de igualdad.
```

`Gratuidad.`: 2 apariciones en el primer tramo de Corpus; 1 en el texto de la respuesta completa de LexiVox. Causa no determinada. No se contrasta aquí el hash del HTML actual contra el original histórico ni se certifica vigencia legal.

## F02: recorrido real y numeración

Chromium autenticado siguió el enlace del documento, no una URL reconstruida contra la raíz.

Salida del navegador, `2026-10-15T04:36:49.557Z`:

```json
{
  "page_labels": ["Página 3 de 100"],
  "character_range": ["Caracteres 10000 a 20000 de 396295"],
  "reader_characters": 10000,
  "next_link_text": "Seguir leyendo página 4",
  "version_preserved": true
}
```

El enlace pulsado decía `Seguir leyendo página 2`. El cuerpo avanzó correctamente, pero la etiqueta no. `ceil(396295 / 10000) = 40` tramos de ese tamaño.

## Correcciones del instrumento, sin borrar la primera corrida

El primer comprobador devolvió FAIL en consulta vacía por esperar una frase antigua y FAIL en siguiente página por usar `urljoin(dominio, href)` ante un `href` que empieza con `?`. **Ambos se retiran como fallos del producto.** El archivo `08_read_codigo_page2.body` es el 401 de la URL mal construida; no es evidencia contra el enlace real.

Texto real del control negativo:

```text
Resultados de búsqueda 0 resultados en esta página Sin resultados para esta consulta. No hay documentos que coincidan con el texto y los filtros elegidos. Página 1 de 1
```

La URL de continuación se volvió a resolver con `urljoin(url_del_documento, href)`. Se mantuvo la sesión autorizada y se obtuvo HTTP 200. Corrección ejecutada entre `2026-10-15T04:37:50.113904+00:00` y `2026-10-15T04:37:54.095902+00:00`.

```json
{
  "negative_query_corrected": "PASS",
  "empty_guard_can_reject_result_and_error": {
    "status": "PASS",
    "injected_result_rejected": true,
    "http500_rejected": true
  },
  "reader_next_page_corrected": {
    "status": "PASS",
    "http": 200,
    "characters": 10000,
    "page_label": "Página 3 de 100",
    "character_range": "Caracteres 10000 a 20000 de 396295"
  },
  "reader_page_number_tracks_navigation": {
    "status": "FAIL",
    "clicked_link_label": "Seguir leyendo página 2",
    "actual_page_label": "Página 3 de 100"
  },
  "unavailable_version_rejected": {"status": "PASS", "http": 403, "reader_text_present": false},
  "logout_denies_replay": {"status": "PASS", "final_http": 200, "final_path": "/corpus/login/", "reader_text_present": false}
}
```

Control de versión: se usó una única versión deliberadamente inexistente, 64 ceros, conservando el mismo documento. No se enumeraron documentos ni cuentas. El control negativo del evaluador vacío se aplicó a una copia local del HTML, no a la aplicación.

## Hashes de capturas seleccionadas

| Archivo | Bytes | SHA-256 |
|---|---:|---|
| 03_search_codigo.body | 25167 | 5264a6147e09e1ec835e8627f75344645a0e3be54f581b9ab66db0bd583c7cd7 |
| 04_search_familia.body | 31560 | 509f0e61746b10310c5b22e71c453625d5a531dc0b28e17d937649d7ace28008 |
| 05_search_absent.body | 20781 | 2f79f812410bb0f180e23d391a707ee2a3067e783a6045cd0cb4c248eb6f1422 |
| 07_read_codigo.body | 26375 | f1b49a61e4d4df408c1929fe73073b4ae1b7d89f2537ad1e2a8cb69774bd1437 |
| 08_read_codigo_page2.body, error del instrumento | 172 | 9371176869a945e2958e43b349397210a1b72b83f11c67e02e0be1f950254ef2 |
| 09_download_codigo.body | 10253 | c05071daa7a24a6c693a67bf90d692104a9b9f76484a67ef8b56ffd59d92c9ae |
| 10_original_lexivox.body | 432318 | c7fa65f7ce6d02e093ac3a7cda43e9533b96221d0ce964f3564c2f7c83b657c4 |
| 22_read_page2_corrected.body | 26307 | e6fbb37a6f76463eaa3b16008b8b4de852d4cd50d8109841e6e8cd953a595c51 |
| 23_invalid_version_control.body | 24 | db486d096b3556687a79a33feb9b92aedc13e38ae6fa34ca0abfc4079563b9b8 |
| 26_post_logout_replay.body | 7309 | 7de1dd8ba2d8016b028e96916155bd3564cfdb07e731a5f77e945672ea535727 |

La presencia de hashes permite comprobar la custodia local, no convierte un extracto publicado en la totalidad del cuerpo ni en una evaluación independiente.

## Reproducción y límites

Con una sesión de prueba autorizada, buscar `Código Procesal Civil`, abrir el resultado de Ley 439, revisar el primer tramo, seguir su enlace de continuación y abrir la fuente LexiVox. Para filtros, buscar `ley` seleccionando una fuente cada vez. Para ausencia, usar `zzcorpuscontrol20261015sincoincidencias`. Los resultados pueden cambiar con el despliegue y los datos.

No se publica una contraseña ni se ejecuta el provisionador. No se modificó Corpus. La revisión desplegada sigue NO MEDIDA y el contraste con RuleX sigue pendiente.
