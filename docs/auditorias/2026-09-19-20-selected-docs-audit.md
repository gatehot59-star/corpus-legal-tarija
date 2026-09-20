# Auditoría de los dos informes seleccionados: Astra integrado y OPUS PR8 a PR11

19-sep-2026, 22:24 ART. Sujeto elegido por el contexto del pedido «audita»: los Docs Astra integrado y OPUS PR8 a PR11, no el contrato de búsqueda recién publicado ni un PR distinto. Revisión de custodia, instrumentos y conclusiones históricas; control ejecutado en brain-env, sin nueva corrida del producto.

## Dictamen

**Astra integrado: conclusiones históricas sustentadas en la evidencia recuperada. OPUS: resultados técnicos no descartados, pero su agregador automático admite un falso positivo y su entrega original no acredita el cierre exigido. Ambos Docs contienen estado histórico que no debe usarse como diagnóstico actual.**

Los reparos de OPUS no son descubrimientos nuevos: la revisión 2026-09-17-23 ya los documentaba. Esta auditoría comprueba el instrumento original y reproduce el defecto de su criterio. No se inventa una falla nueva del producto ni se compara superioridad de modelos.

## Sujetos y fuentes

- [Doc Astra seleccionado](https://app.clickup.com/90171457413/docs/2kza6fw5-13137), página leída completa: https://app.clickup.com/90171457413/docs/2kza6fw5-13137/2kza6fw5-15397 . Informe `docs/auditorias/2026-09-18-08-astra-integrado.md`, commit c7b6ed79640c37547607332e9a49276543696907. Producto ensayado entonces: 30189275ea996e23aa7804e2334f0b9ba93dd8d1; main entonces: 526a29a92144f24853f56595d2eea4bdb836967c.
- [Doc OPUS seleccionado](https://app.clickup.com/90171457413/docs/2kza6fw5-12977), página leída completa: https://app.clickup.com/90171457413/docs/2kza6fw5-12977/2kza6fw5-15237 . Informe `docs/auditorias/2026-09-18-opus-pr8-pr11-independent.md`, commit 982b82cb1b5925ba45175a3dd185ffeca6eb6b72. Sujeto histórico: PR11 3a60627101859ca92c9b0a4fdd436205b99bb504 y cadena PR8 a PR11.
- Correcciones contrastadas: `docs/auditorias/2026-09-17-23-revision-opus.md` y `docs/auditorias/2026-09-18-09-revision-astra-integrado.md`.
- Main congelado para la inspección actual: acef5ae6cadebf9efd9acc76cfea4c76f97ff290. Nexus consultado, incluyendo reporte 41 de revisión OPUS y avances 52 a 65. Las últimas propuestas no sustituyen los objetos seleccionados.

## A1. Astra: custodia y criterio semántico CONFIRMADOS

Recuperé desde git las tres partes 8000/8000/7916 del commit d60ac0498a2993b900f67f79d6918c8f9cc8c890. Base64 estricto y xz: 550961 bytes, SHA256 `2db93dea9e58bab24545763c2fb7b12349fcf7cf2b2cd0c0f14dd69fbbb0aa08`, igual al declarado.

Recalculé cada `passed` comparando observed contra expected, sin confiar solo en el total del recibo. Baseline 69/0 y repetición 69/0 coinciden. Los cuatro mutantes tienen positivo pertinente y negativo objetivo: no_revoke 65/4; revoke_every_session 64/5; ignore_clock 67/2; ignore_dispatch_marker 68/1. El código del agregador exige baseline limpio y la aserción objetivo, no cualquier salida 1.

También recuperé la contraprueba posterior: 570136 bytes, SHA256 `3533901e95f4b6c0fe2635ebe4b7c6cc8768060bbe3a3eff27e12323ea898fec`. Recalculé su sabotaje de reinicio: 68/1, único fallo new_process_revoked, observado 200 frente a 403. Es evidencia histórica de sensibilidad causal, no otra ejecución de sesiones en este turno.

## O1. OPUS: criterio de detección FALLA

Extraje por AST la expresión original de `opus_mut.py` publicada dentro de la revisión posterior: `sum(1 for o in out if o['returncode'] != 0)`. Verifiqué que ese código coincide con el instrumento del bundle original local cuyo hash declara OPUS.

Ejecuté ESA expresión, sin ejecutar su script que borra directorios fijos. Entrada: el returncode 1 de la contraprueba publicada del baseline SIN mutación, cuyo único FAIL es B6c, espacio final normalizado por el transporte. Resultado: **1 mutante detectado**, aunque no se introdujo ningún mutante. Control con returncode 0: 0 detectados. Control semántico independiente: candidato sin cambio no detectado; observado 200 frente a esperado 403 sí detectado.

Impacto: el contador no discrimina el fallo previo del instrumento de la violación buscada. No implica que sus cuatro falsadores reales fueran falsos positivos: la revisión posterior conserva y demuestra fallos adicionales pertinentes. Aceptación de reparación: baseline válido para cada propiedad, detección por aserción objetivo y control de copia sin cambio. No modifiqué el banco ajeno.

## O2. OPUS: custodia original INCOMPLETA, no evidencia inventada

El bundle local existe: 51615 bytes, SHA256 `6983abd5aa2c0556b6947625b224b16c928092e4b26f75e5096b2195d71177ba`, coincidente. Su informe original tiene un solo commit en la historia de main consultada. El árbol con nombres OPUS contiene el informe y la revisión posterior con sus dos bloques, no una publicación identificada del bundle original. Nexus devuelve el reporte 41 de revisión, no un cierre posterior de OPUS en la consulta por ese nombre. Eso no prueba inexistencia en cualquier otra rama o sistema.

Sí está publicada la contraprueba posterior: 52819 bytes, SHA256 `15ecde1fa1501111b023833fa95b5c6db77e9a1ac72ba41bbe8bcaa70a98993c`, reconstruida y verificada ahora. No debe confundirse con el bundle original.

Además el instrumento original conserva `fails[:8]` y `r.stderr[-300:]`, confirmados estructuralmente por AST. Una publicación posterior de esos bytes no recuperaría lo descartado. Aceptación: corregir captura, preservar salidas completas de una ejecución acotada y verificarlas remotamente. No publiqué evidencia original ajena en su nombre ni cerré su trabajo por asociación.

## H1. Lectores y temporalidad: dos extrapolaciones que no corresponden

El script `opus_legacy.py` inspeccionado hace SELECT y concatena chunks; no invoca HTTP. La equivalencia con documento() del árbol PR11 y la diferencia frente al lector 84358cc que usa fusionar están demostradas por la contraprueba histórica, no reejecutadas aquí. La inflación 15,03% a 15,42% no se extrapola a ambos lectores ni a producción. El 3/6079 mide esa copia candidata y adapter, no porcentaje de producto terminado.

«Falta conectar el consumidor» en Astra describe el estado de aquella revisión. El main actual contiene demo_aislada.py y los módulos exact_http/version_text; PR14 y su auditoría posterior ya cubrieron la composición aislada. El Handler histórico no se convirtió por eso en el launcher nuevo. No propongo rehacer una conexión ya implementada.

«isolated_test no corta lecturas existentes» en OPUS describe PR11. Inspeccioné estructuralmente el __call__ actual: consulta la marca antes de despachar al lector. Astra integrado contiene el positivo pause_read 403 y mutante 200. No mantengo el comportamiento antiguo como vulnerabilidad actual. Esta inspección de fuente no certifica una petición concurrente ya pasada del guard.

## Método, evidencia y límites

Brain-env: Python 3.12.14, SQLite 3.46.1, dos CPU; inventario y método releídos. Verificador propio `selected_review.py` ejecutado, exit 0, stderr vacío. Instrumento, resultados, stdout/stderr completos de esa ejecución y referencias inmutables están en el archivo hermano `2026-09-19-20-selected-docs-audit/evidence.xz.b64`: un archivo base64+xz, JSON 19336 bytes, SHA256 `85a306cb13101d6ec49e818451b0cad902e7998a5a4e320ab838abb8da0d0e14`.

El recibo incluye longitud/hash de los cuerpos Git, no vuelve a copiarlos íntegros: se recuperan por revisión y ruta. Es una captura declarada de verificación, no un volcado de toda la conversación. Sin tokens, SQLite ni datos reales nuevos. Para reproducir: decodificar base64 estricto y lzma; extraer verification.instrument_source; revisar rutas de solo lectura y ejecutarlo sobre el repo con los commits disponibles y scratch propio. La comparación con el bundle OPUS local requiere ese antecedente; el resto usa evidencia remota. No correr opus_mut.py a ciegas.

NO MEDIDO en este turno: nuevas sesiones HTTP, suites 63/69, runtime actual de los servicios, producción, TLS, carga, crash, vigencia jurídica o piloto. Los resultados anteriores no se suman como pruebas nuevas. No se creó ningún listener ni proceso de servicio; los subprocess Git son síncronos y terminaron. Revisor/verificador/control final son el mismo operador; la independencia del control reside en su criterio, no en el nombre Astra.

Gate I de esta revisión: PASA para custodia, recálculo y control causal del agregador; runtime de producto N/A. Gate II: PASA en el alcance seleccionado, con hallazgos heredados y límites separados. Gate III al escribir: pendiente de publicación, readback, Doc público y Nexus; el cierre verificará esos pasos antes del chat.

Prioridad: no repetir auditorías de producto ya cubiertas. Lo útil aquí es corregir el criterio/captura de OPUS y añadir contexto histórico a esos Docs si se encarga; no son prerrequisitos demostrados para el siguiente incremento de Corpus. No modifiqué los dos Docs originales, producto, PRs, despliegues ni permisos.
