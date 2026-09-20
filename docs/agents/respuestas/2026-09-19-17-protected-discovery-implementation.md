# Búsqueda protegida implementada y probada; cierre de evidencia todavía incompleto

19-sep-2026 ART. Implementación del lote aprobado en comment80170047135186, no permiso de merge ni despliegue. Rama `titan/protected-discovery`, apilada sobre PR19 `titan/builder-saved-reference`, base31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05. Contrato18 enmendado ef0e5b271ccd1b3eca09e89b71feb01581a9a860.

## Resultado e impacto

CONFIRMADO: el fixture ahora permite entrar, buscar solo versiones autorizadas, seleccionar una, leerla completa y descargar una referencia sin texto ni credenciales. Dos identidades ficticias, dos colecciones configuradas por el servidor, cuatro documentos. Permisos completos antes de tocar contenido; excepción de política descarta todo. El lector y el guardado vuelven a autorizar la versión exacta. La página pública no lleva títulos ni catálogo protegido.

CONFIRMADO: HEAD de búsqueda no emite cuerpo, Content-Length ni Transfer-Encoding, incluso en403/503 tempranos. Se verificaron bytes crudos de red, no un accessor HEAD que oculta contenido. Normalización JSON/header exclusiva de búsqueda; los405 de login/logout conservan Allow:POST.

NO MEDIDO: producción, piloto, revisión independiente, accesibilidad visual completa, carga, otros navegadores, cobertura de ramas y CVEs actualizados. No hay aprobación legal por haber pasado estos tests.

## Archivos y conservación del core

Ocho archivos de código, tests y manual publicados y recuperados byte a byte a57b5a28bbf37b7d35123b23d24ac522cd0b3af96. Delta exactamente siete adiciones y un workflow modificado, más este recibo y el manifiesto de evidencia del lote10. No se tocaron access_policy.py, isolated_login.py, isolated_session.py, exact_http.py, version_text.py, demo_aislada.py, demo_restore.py, servidor.py, index.html, auth_spike.html ni tests heredados.

- sistema/api/protected_search.py:226 líneas, SHA256 bbad1d7599cfc743981837ceb74f581ff4f36939be7c7730090620b6c4701c17.
- sistema/api/demo_discovery.py:256 líneas, d571b4995d1df41dd52a0f57af762b06394b7eadc7481d07d1bc015e75ab73d3.
- sistema/web/discovery_spike.html:144 líneas, d8fd920aed755de18cbbc29c8ad791547fb82004f8e1c1d729e5cfad834de7c4.
- tests/test_protected_search.py:227 líneas, f8cb7d51c62f3522eb75968b692720e651909f9e68e11fa13852f9d9e5d750ef.
- tests/test_demo_discovery.py:185 líneas, b140547aacee16df434285a60d38adae73cebce0f963d65f2a36a90d3e33ae17.
- tests/browser_discovery.cjs:118 líneas,71e24f043573915079e9e7238841d42ee7e5b50169497b775495d14402d37b78.
- .github/workflows/clean-snapshot.yml:97 líneas,6127646251cf6d51606951531555394055289aad2f41efea0be0397d5a4d6182.
- sistema/DEMO-DISCOVERY.md:141 líneas,6a6e2a7b78a82f6a17e5910165f8a7041bfee307b37d8c1c39a5a37f394e986e.

## Pruebas ejecutadas

140 Python positivos:21 clean_snapshot_sol,15 exact_http,15 access_policy,18 login_guards,10 isolated_session,18 demo_aislada,14 demo_restore,7 browser_auth,15 protected_search y7 demo_discovery. No se vuelven a contar los12 login heredados incluidos en GuardTests.

Chromium153.0.8010.12 con Playwright1.63.0:37 checkpoints del banco heredado y18 del nuevo. El nuevo repitió positivo en fixture fresco. Comprueba ambas identidades, texto Unicode/CRLF/astral exacto, snippet hostil inerte, descarga JSON real con16campos, hashes distintos, revocación después de resultados/entre páginas/antes de guardar, limpieza al cambiar identidad, logout y recarga. No hubo errores de página; ancho390 sin overflow horizontal. Esto no reemplaza inspección visual/accesibilidad.

Cuatro mutantes scratch: permitir todos los candidatos produce AssertionError2!=1; usar versión actual en lugar de la explícita falla la aserción de200 al cambiar fila actual; devolver contenido en HEAD falla `HEAD wire content must be absent`; omitir Referrer-Policy falla `required search header Referrer-Policy`. Los positivos de esas mismas propiedades pasaron. Los mutantes no se publicaron como producto.

Los tests de consulta cubren128/129puntos,256/257bytes,815bytes codificados válidos,2048inválidos frente a2049demasiado largos, claves duplicadas decodificadas, UTF-8/escapes inválidos, controles, espacios y NFC/casefold. Fixtures denegados válidos perturbados no cambian el resultado visible. Catálogo vacío verifica sesión. Fallo posterior de política no permite leer ni devolver resultados parciales. Paginación del endpoint comprobada; UI deliberadamente muestra primeras cinco y pide acotar, fixture actual4.

## Errores propios e instrumento

El primer test de colección movía un grant a la otra colección existente: esperaba403 pero el permiso nuevo autorizaba legítimamente su documento. Corregido el fixture a scope no configurado, no el producto. La captura fallida se conserva.

Se ajustó la gramática para permitir `=` literal dentro del valor de q, sin segunda decodificación. Los primeros mutantes de versión/headers producían KeyError al observar la respuesta incorrecta: se reforzaron las aserciones de estado/header y repitieron, ahora fallan por la propiedad nombrada.

El primer `python -m trace` ejecutó CERO tests y mostró100% de líneas importadas. Ese número queda REFUTADO como cobertura. El instrumento corregido carga el módulo explícitamente, exige15casos y ejecuta la suite:175de185líneas según `_find_executable_linenos`,94.59%; ese denominador incluye la línea sintética0. Excluyéndola son175/184=95.11%. Solo protected_search.py, no ramas, harness, navegador ni proyecto entero. Se guardaron fuente del instrumento, conteos y salidas completas.

## Seguridad y límites revisados

Consultas SQL parametrizadas para sesión y reutilización literal de SQLiteAccessPolicy, no copia del SQL de grants. Nada de HTML desde snippets: textContent. Sin URLs de búsqueda hacia fuera, archivos importados, shell desde inputs, CORS o persistencia de tokens. CSP con hashes exactos, loopback/Host/Origin/FetchMetadata y duplicados sensibles. Archivos privados/exclusivos/manifiesto antes de bind. Checkout pinneado y contents:read heredados; no nueva dependencia ni workflow.

No se ensayaron CVEs recientes ni capacidad bajo carga. Socket2s es inactividad y SQLite1s espera de lock, no plazo total. No es servidor productivo ni sandbox contra el operador. Una respuesta ya autorizada o un archivo descargado no se puede retirar.

## Custodia y gates

Bundle íntegro local:68208bytes, SHA256 ab06e374c2a8d4303e98e7b20bde4f8d278ed45b126d686dd53861c844841112, codec xz+base64,payload13560caracteres. Incluye capturas originales/adversas, repetición final, medición corregida, instrumento trace, manifiesto de fuentes y comparación remota.

**La evidencia íntegra aún NO está publicada en Git.** El JSON hermano es un manifiesto de custodia, no un reemplazo ni un recibo crudo. Hay que publicar el payload completo en ese mismo archivo autorizado, recuperarlo, decodificar estrictamente y comparar byte a byte antes de declarar entrega completa. No requiere ampliar scope ni nueva aprobación.

Gate I: positivos y falsadores ejecutados, alcance acotado; datos crudos pendientes de publicación. Gate II: resultados separados de límites; PASA como recibo de avance. Gate III: INCOMPLETO, falta custodia remota íntegra, CI final y cierre de revisión/Doc/Nexus. No se certifica main: la autorización fue rama/PR, no merge.

## TITAN SCORECARD

Autoevaluación provisional73/85=85.88/100, por debajo90. Completitud13/15 (producto ejecutable, entrega incompleta); ejecutabilidad15/15 (Python y Chromium); seguridad12/15 (frontera probada, no CVE/revisión externa); testing11/15 (falsadores y cobertura adaptador, no ramas/carga); arquitectura8/10 (scope y política única, fixture deliberadamente acotado); documentación9/10 (manual real, custodia pendiente); proceso5/5 (permisos y errores explícitos). N/A15:deployment10 prohibido, ampliaciones5 fuera de scope. Esta nota no concede merge ni piloteo y no debe citarse como aprobación.

--- METODO TITAN ---
Accion delicada:SI, frontera y workflow. Modo:TITAN FULL. Roles:Builder,Security,Tester,Docs y control propio, no revisor externo. Máquina:brain-env. Sin merge/deploy/datos reales. Revisión independiente pendiente. Código y bancos reales publicados; evidencia íntegra todavía local, cierre no completo.
