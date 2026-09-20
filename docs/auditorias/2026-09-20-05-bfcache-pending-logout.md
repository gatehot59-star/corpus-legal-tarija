# PR20: BFCache real en control, no restaurado con logout pendiente

## 1. Pedido y conclusión

Pedido: Test actual BFCache restoration during a pending logout.

CONFIRMADO: Chromium restauró realmente el control cacheable, mismo UUID de JavaScript y pageshow.persisted=true, dos veces. REFUTADO en esta configuración: PR20 volvió como documento nuevo con logout pendiente, tanto 200 como 403 reales retenidos, dos corridas por caso. NO MEDIDO: callback tardío dentro del mismo documento de PR20 restaurado. La precondición no se alcanzó; no se declara aprobado ese comportamiento ni se inventa un bug.

Sin modificaciones de producto, merge, despliegue, cuentas reales ni mensajes a ejecutores. No se quitaron cabeceras para forzar el resultado.

## 2. Sujeto, herramientas y máquina

Repo gatehot59-star/corpus-legal-tarija, PR20 head cc2ca30760c486cad3154c619a20f94cf75cc691, base 31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05. Consulta final: abierto, merged=false, mismo head. Main previo ee97fa4a9b9a2f73af6815ad0babd28c049ad2ff.

Verificador experimental y control final, mismo operador que escribió el fix: no revisión externa. brain-env, Python3.12.14, Node24.18.0, Playwright1.63.0, Chromium completo153.0.8010.12. Bibliotecas Debian verificadas por SHA extraídas privadamente, sin instalación global; no Actions ni GPU.

Playwright desactiva BFCache por defecto. Se omitió solo --disable-back-forward-cache; el control negativo lo conserva. Headless-shell reportó BackForwardCacheDisabledForDelegate: no era positivo válido. Se pasó al ejecutable Chromium completo.

## 3. Instrumento, mediciones y reproducción

bfcache_test.cjs SHA256 f159897fea1e4e29fe0cb0e7cfe8892c05867e690d664da79d31fd49a2330640; bfcache_proxy.py SHA256 2a92d516fb77e621c75c5dcfc8cd3109bca98f25b800ba367c6ccb322d36b7f4. Fuentes completas dentro de evidencia.

Proxy loopback inicia CLI/fixture reales, conserva HTML y cabeceras de caché/seguridad, remapea Host/Origin al backend. Retiene primera respuesta logout DESPUÉS de procesarla upstream. 403 por quitar marca isolated_test en base ficticia, restaurada antes de volver; 200 del logout real. Sin Playwright routes ni eventos sintéticos ni edición de Corpus. addInitScript observa UUID/pageshow/pagehide en sessionStorage sin bearer: instrumentación declarada. Navegación /away, history.back, espera URL/commit/pageshow, no load.

Resultados definitivos:
- control-history-back.json y control-repeat.json: exit0, mismo UUID, pageshow.persisted=true.
- disabled_control-history-back.json: exit1 exactamente same_document_restored; razón nativa BackForwardCacheDisabledByCommandLine. Falsador de la misma aserción del positivo, no mutación del producto.
- nostore_control-history-back.json: exit1 same_document_restored, documento nuevo.
- pending200-history-back.json y pending200-repeat.json: contenido previo positivo, respuesta real200 retenida, UI esperando, navegación real; exit1 same_document_restored.
- pending403-history-back.json y pending403-repeat.json: iguales precondiciones con respuesta real403; exit1 same_document_restored.

Cada ensayo definitivo de PR20 sirvió HTML dos veces con SHA256 69eba91fcf88b5c0547e263276cfc1a9f0da2703b91a1601397e8fffb0b5efdb, idéntico al archivo fuente del head. Segundo servicio y UUID nuevo confirman documento nuevo. Repetición en archive nuevo y fixtures nuevos.

Razones nativas: MainResourceHasCacheControlNoStore, JsNetworkRequestReceivedCacheControlNoStoreResource, BrowsingInstanceNotSwapped. No se atribuye causalidad universal a una única cabecera. Chrome documenta restricciones de no-store con fetch/XHR también no-store: https://developer.chrome.com/docs/web-platform/bfcache-ccns. No-store no garantiza exclusión universal de BFCache.

La sección del instrumento que comprobaría sesión B y callback tardío tras restauración NO se ejecutó: la aserción de identidad detuvo PR20 antes. No contar esos checks como pasados. La suite previa del autor/CI no se reejecutó en este ensayo.

Reproducción: decodificar data con base64 estricto y lzma, verificar bytes/hash; extraer instrumentos de files en scratch propio. Cada corrida conserva command/env/exit/stdout/stderr/duración completos. Usar archive del head indicado, Chromium completo y bibliotecas; ejecutar control, disabled_control, nostore_control, pending200 y pending403. Exit1 de los casos no restaurados significa que la demanda explícita de restauración no se cumple, no fallo de autenticación.

## 4. Errores, recursos y evidencia cruda

Se preservan todas las corridas de navegador capturadas: fallos iniciales por bibliotecas ausentes; headless-shell sin BFCache; timeout de goBack esperando load. El último se corrigió SOLO en el instrumento con history.back/commit/pageshow; el control entonces restauró. No son defectos del producto.

La comprobación auxiliar de recursos falló por asumir JSON objeto cuando había lista, después por ausencia de ps. Se corrigió validando tipo y leyendo /proc. Errores declarados en captura, sin reconstruir tracebacks terminales completos.

Cierres registrados: proxy exit0, backend exit0, hilo servidor cerrado; compuertas liberadas, marcas restauradas y revocaciones explícitas de sesiones ficticias. Comprobación final: 18 puertos proxy rechazan conexión; barrido acotado sin procesos de instrumentos. No se sondeó individualmente cada puerto backend: evidencia de cierre de proceso, no medición de todos sus sockets. No inspección universal del host.

Evidencia reversible xz+base64: 178839 bytes, SHA256 d175c44c881fc010ee67a6bf01d18ff54d72b82af311a66c34c152605bdd4fc5. Incluye salidas completas de todas las corridas de navegador capturadas, también fallidas, cuatro versiones del instrumento, proxy y comprobación final de recursos. Bearers nunca registrados; sin video ni browser trace.

Alcance publicado excluye metadatos completos del PR, ldd, descargas Debian y texto de Chrome. Conservados en paquete completo local de230363bytes SHA256 37e08681969e8b49a5d40186e7af58561826962573a0f1a4b4b480c83b3b97b1. No se llama al paquete publicado archivo íntegro de todo el turno. Binarios Debian y archive del repo no se commitean.

## 5. Archivos y Doc

- docs/auditorias/2026-09-20-05-bfcache-pending-logout.md
- docs/agents/evidencia/2026-09-20-05-bfcache-pending-logout.json

Doc público, Space > Doc (sin Folder): https://app.clickup.com/90171457413/docs/2kza6fw5-13777

## 6. Gates y límites

Gate I PASA para distinguir restauración real/documento nuevo: sujeto y bytes, positivo/falsador, repetición y captura. NO MEDIDO para callback dentro de PR20 restaurado. Gate II: causalidad y exclusiones explícitas, no aprobación de producto. Gate III: cierre de chat condicionado a recuperación remota, comparación byte por byte, pertenencia a main, Doc público leído y Nexus. Registro de comprobación posterior en Nexus, no asumirlo por este texto.

NO MEDIDO que importa: BFCache de PR20 en otros navegadores/configuraciones, origen productivo, pestañas, cookies, callback dentro del documento restaurado y causalidad universal de no-store. Esta prueba no borra la deuda de revisión externa.

--- METODO PROMETEO ---
Accion delicada: NO, diagnóstico aislado/documentación; ninguna frontera de confianza modificada.
Modo aplicado: LIGERO, verificador experimental y control final.
Maquina: brain-env.
Rubrica: N/A, diagnóstico acotado; Gates separados arriba.
Review externo: pendiente; mismo autor del fix.
Instrumento: Chromium real/proxy de demora; comandos y salidas completos en evidencia reversible.
Artefactos: docs/auditorias/2026-09-20-05-bfcache-pending-logout.md + docs/agents/evidencia/2026-09-20-05-bfcache-pending-logout.json + https://app.clickup.com/90171457413/docs/2kza6fw5-13777
