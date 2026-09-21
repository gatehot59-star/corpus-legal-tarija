# Búsqueda protegida: implementación probada y evidencia íntegra publicada

19-sep-2026 ART, cierre de custodia solicitado a las23:09. Implementación del lote aprobado en comment80170047135186, no permiso de merge ni despliegue. Rama `titan/protected-discovery`, [PR20](https://github.com/gatehot59-star/corpus-legal-tarija/pull/20), apilada sobre PR19 `titan/builder-saved-reference`, base31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05. Contrato18 enmendado ef0e5b271ccd1b3eca09e89b71feb01581a9a860.

## Actualización de cierre: reemplaza el pendiente anterior

La evidencia completa YA ESTÁ EN GIT, en `docs/agents/evidencia/2026-09-19-17-protected-discovery.json`, commit c5830a08d52bf0584e67c9044f36a9ac6e450ff7. Se recuperó mediante git fetch/git show, se decodificó base64 con validate=True y xz, se verificó longitud68208 y SHA256 ab06e374c2a8d4303e98e7b20bde4f8d278ed45b126d686dd53861c844841112, y se comparó BYTE A BYTE con la captura original: igualdad exacta, exit0. El archivo ya no es el manifiesto de custodia incompleta. La publicación modificó solo ese archivo, sin alterar producto ni evidencia.

El CI del head anterior828302ced932d1f93b84ecd2de7be55b0cba85c4 terminó exitosamente, diez pasos sin omisiones: job106004327938, run35483096506,02:06:09..02:07:25UTC del20-sep,23:06:09..23:07:25ART del19-sep. Se consultaron check runs Y el detalle de pasos de la API, no solo estado combinado. [Ejecución observada](https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35483096506/job/106004327938).

**El CI del head que contiene este recibo se verifica DESPUÉS de este commit.** Su SHA, job, pasos y resultado final quedan en la descripción de PR20 y en el [Doc público de cierre](https://app.clickup.com/90171457413/docs/2kza6fw5-13677). No se etiqueta el CI del padre como el del hijo ni se crea un bucle infinito de commits de estado. Esta nota acredita custodia ya observada, no anticipa el resultado de una ejecución futura.

Revisión automática solicitada: al cierre de la consulta,0reviews y0threads; silencio NO es aprobación. Sigue sin mergear y sin desplegar.

## Resultado e impacto

CONFIRMADO: el fixture permite entrar, buscar solo versiones autorizadas, seleccionar una, leerla completa y descargar una referencia sin texto ni credenciales. Dos identidades ficticias, dos colecciones configuradas por el servidor, cuatro documentos. Permisos completos antes de tocar contenido; excepción de política descarta todo. El lector y el guardado vuelven a autorizar la versión exacta. La página pública no lleva títulos ni catálogo protegido.

CONFIRMADO: HEAD de búsqueda no emite cuerpo, Content-Length ni Transfer-Encoding, incluso en403/503 tempranos. Se verificaron bytes crudos de red, no un accessor HEAD que oculta contenido. Normalización JSON/header exclusiva de búsqueda; los405 de login/logout conservan Allow:POST.

NO MEDIDO: producción, piloto, revisión independiente, accesibilidad visual completa, carga, otros navegadores, cobertura de ramas y CVEs actualizados. No hay aprobación legal por haber pasado estos tests.

## Archivos y conservación del core

Ocho archivos de código, tests y manual publicados y recuperados byte a byte a57b5a28bbf37b7d35123b23d24ac522cd0b3af96. Delta autorizado final: nueve adiciones y un workflow modificado, diez archivos. No se tocaron access_policy.py, isolated_login.py, isolated_session.py, exact_http.py, version_text.py, demo_aislada.py, demo_restore.py, servidor.py, index.html, auth_spike.html ni tests heredados.

- sistema/api/protected_search.py:226 líneas, SHA256 bbad1d7599cfc743981837ceb74f581ff4f36939be7c7730090620b6c4701c17.
- sistema/api/demo_discovery.py:256 líneas, d571b4995d1df41dd52a0f57af762b06394b7eadc7481d07d1bc015e75ab73d3.
- sistema/web/discovery_spike.html:144 líneas, d8fd920aed755de18cbbc29c8ad791547fb82004f8e1c1d729e5cfad834de7c4.
- tests/test_protected_search.py:227 líneas, f8cb7d51c62f3522eb75968b692720e651909f9e68e11fa13852f9d9e5d750ef.
- tests/test_demo_discovery.py:185 líneas, b140547aacee16df434285a60d38adae73cebce0f963d65f2a36a90d3e33ae17.
- tests/browser_discovery.cjs:118 líneas,71e24f043573915079e9e7238841d42ee7e5b50169497b775495d14402d37b78.
- .github/workflows/clean-snapshot.yml:97 líneas,6127646251cf6d51606951531555394055289aad2f41efea0be0397d5a4d6182.
- sistema/DEMO-DISCOVERY.md:141 líneas,6a6e2a7b78a82f6a17e5910165f8a7041bfee307b37d8c1c39a5a37f394e986e.

## Pruebas ejecutadas y alcance de sus conteos

140 Python positivos LOCALES:21 clean_snapshot_sol,15 exact_http,15 access_policy,18 login_guards,10 isolated_session,18 demo_aislada,14 demo_restore,7 browser_auth,15 protected_search y7 demo_discovery. No se vuelven a contar los12 login heredados incluidos en GuardTests. Los pasos exitosos de CI no sustituyen sus stdout: los conteos citados proceden de las capturas locales publicadas.

Chromium153.0.8010.12 con Playwright1.63.0:37 checkpoints del banco heredado y18 del nuevo. El nuevo repitió positivo en fixture fresco. Comprueba ambas identidades, texto Unicode/CRLF/astral exacto, snippet hostil inerte, descarga JSON real con16campos, hashes distintos, revocación después de resultados/entre páginas/antes de guardar, limpieza al cambiar identidad, logout y recarga. No hubo errores de página; ancho390 sin overflow horizontal. Esto no reemplaza inspección visual/accesibilidad.

Cuatro mutantes scratch: permitir todos los candidatos produce AssertionError2!=1; usar versión actual en lugar de la explícita falla la aserción de200 al cambiar fila actual; devolver contenido en HEAD falla `HEAD wire content must be absent`; omitir Referrer-Policy falla `required search header Referrer-Policy`. Los positivos de esas mismas propiedades pasaron. Los mutantes no se publicaron como producto. Sus reemplazos exactos, comandos, stdout/stderr y returncode están en el bundle.

Los tests de consulta cubren128/129puntos,256/257bytes,815bytes codificados válidos,2048inválidos frente a2049demasiado largos, claves duplicadas decodificadas, UTF-8/escapes inválidos, controles, espacios y NFC/casefold. Fixtures denegados válidos perturbados no cambian el resultado visible. Catálogo vacío verifica sesión. Fallo posterior de política no permite leer ni devolver resultados parciales. Paginación del endpoint comprobada; UI muestra primeras cinco y pide acotar, fixture actual4.

## Errores propios e instrumento

El primer test de colección movía un grant a la otra colección existente: esperaba403 pero el permiso nuevo autorizaba legítimamente su documento. Corregido el fixture a scope no configurado, no el producto. La captura fallida se conserva.

Se ajustó la gramática para permitir `=` literal dentro del valor de q, sin segunda decodificación. Los primeros mutantes de versión/headers producían KeyError al observar la respuesta incorrecta: se reforzaron las aserciones de estado/header y repitieron, ahora fallan por la propiedad nombrada.

El primer `python -m trace` ejecutó CERO tests y mostró100% de líneas importadas. Ese número queda REFUTADO como cobertura. El instrumento corregido carga el módulo explícitamente, exige15casos y ejecuta la suite:175de185líneas según `_find_executable_linenos`,94.59%; ese denominador incluye la línea sintética0. Excluyéndola son175/184=95.11%. Solo protected_search.py, no ramas, harness, navegador ni proyecto entero. Fuente del instrumento, conteos y salidas completas están en el bundle.

La entrega previa se interrumpió con evidencia solo local pese a estar autorizada su publicación: cierre incompleto real. Este turno subsana custodia y comprueba CI sin reabrir el lote ni presentar las pruebas anteriores como nuevas.

## Seguridad y límites revisados

Consultas SQL parametrizadas para sesión y reutilización literal de SQLiteAccessPolicy, no copia del SQL de grants. Nada de HTML desde snippets: textContent. Sin URLs de búsqueda hacia fuera, archivos importados, shell desde inputs, CORS o persistencia de tokens. CSP con hashes exactos, loopback/Host/Origin/FetchMetadata y duplicados sensibles. Archivos privados/exclusivos/manifiesto antes de bind. Checkout pinneado y contents:read heredados; no nueva dependencia ni workflow.

No se ensayaron CVEs recientes ni capacidad bajo carga. Socket2s es inactividad y SQLite1s espera de lock, no plazo total. No es servidor productivo ni sandbox contra el operador. Una respuesta ya autorizada o un archivo descargado no se puede retirar.

## Custodia reproducible

El JSON de evidencia tiene cuatro campos:codec,bytes,sha256,payload. Para verificar sin ejecutar el contenido:

```python
import base64, hashlib, json, lzma
from pathlib import Path
w = json.loads(Path('docs/agents/evidencia/2026-09-19-17-protected-discovery.json').read_text())
raw = lzma.decompress(base64.b64decode(w['payload'], validate=True))
assert w['codec'] == 'xz+base64'
assert len(raw) == w['bytes'] == 68208
assert hashlib.sha256(raw).hexdigest() == w['sha256'] == 'ab06e374c2a8d4303e98e7b20bde4f8d278ed45b126d686dd53861c844841112'
evidence = json.loads(raw)
```

La misma secuencia de decode/len/hash fue ejecutada sobre bytes recuperados de Git; además se comparó con el original local. El bundle contiene `discovery-first-capture.json`, `discovery-capture-v2.json`, `discovery-final-checks.json`, `discovery-trace-corrected.json`, `discovery-trace-capture.json`, `discovery-source-manifest.json`, `remote_byte_equal`, `verified_head`, `scope_delta`, `trace_instrument_source`. No bases de datos, binarios, tokens de sesión ni credenciales reales. Base64 transporta JSON comprimido reversible, no un ejecutable.

## Observación cruda de CI previo

API GET https://api.github.com/repos/gatehot59-star/corpus-legal-tarija/actions/jobs/106004327938. Atributos seleccionados de respuesta, no logs stdout remotos:

```json
{"id":106004327938,"head_sha":"828302ced932d1f93b84ecd2de7be55b0cba85c4","status":"completed","conclusion":"success","started_at":"2026-09-20T02:06:09Z","completed_at":"2026-09-20T02:07:25Z","steps":[{"name":"Set up job","status":"completed","conclusion":"success","number":1},{"name":"Run actions/checkout@11d5960a326750d5838078e36cf38b85af677262","status":"completed","conclusion":"success","number":2},{"name":"Compile and test copy, exact reading and isolated session lifecycle","status":"completed","conclusion":"success","number":3},{"name":"Compile and test synthetic demo CLI (real subprocess lifecycle)","status":"completed","conclusion":"success","number":4},{"name":"Compile and test quarantined synthetic restore","status":"completed","conclusion":"success","number":5},{"name":"Test opt-in browser HTTP boundary","status":"completed","conclusion":"success","number":6},{"name":"Test protected synthetic discovery and raw HTTP","status":"completed","conclusion":"success","number":7},{"name":"Test real Chromium login, exact reading and logout","status":"completed","conclusion":"success","number":8},{"name":"Post Run actions/checkout@11d5960a326750d5838078e36cf38b85af677262","status":"completed","conclusion":"success","number":16},{"name":"Complete job","status":"completed","conclusion":"success","number":17}]}
```

## TITAN SCORECARD y gates

Autoevaluación73/85=85.88/100 conservada, debajo90. No se aumenta por trasladar evidencia. Completitud13/15; ejecutabilidad15/15; seguridad12/15; testing11/15; arquitectura8/10; documentación9/10; proceso5/5. Fundamentos: fuentes/manifiesto y bancos arriba; deducciones por cobertura no global, revisión externa/CVEs/carga/visual pendientes. N/A15:deployment10 prohibido, ampliaciones5 fuera de scope. La cifra previa era provisional; publicar no elimina estas deudas.

Gate I: positivos y cuatro falsadores en alcance acotado. Gate II: evidencia íntegra ahora pública y decodificable, relato separado. Gate III:custodia Git cerrada, CI posterior al commit y estado final consignados en PR/Doc. No se certifica main ni se autoriza merge/piloto. La ausencia de review no es hallazgo ni aprobación.

--- METODO TITAN ---
Accion delicada de implementación:SI, frontera y workflow; este cierre solo documentación/evidencia autorizadas. Modo:TITAN FULL. Roles de implementación:Builder,Security,Tester,Docs/control propio, no revisor externo. Máquina:brain-env. Sin merge/deploy/datos reales. Revisión independiente pendiente. Git conserva producto, pruebas y evidencia íntegra; PR/Doc reflejan verificación del head final sin otro cambio de código.
