# PR20: el arreglo resiste rechazos, bloqueo SQLite y respuesta perdida

## Pedido, sujeto y límite de independencia

Auditar el arreglo de logout de PR20 sin mergear ni desplegar. Revisión probada: `cc2ca30760c486cad3154c619a20f94cf75cc691`, base del PR `31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05`; cambio del arreglo contra `a8aeb301f8840caa547e48730a46e1b9406927bc`. PR20 permanece abierto y sin merge en la reconsulta final.

**Conclusión: sin nuevos reparos en los escenarios probados. No es una aprobación externa.** Astra escribió el arreglo anterior y también opera esta auditoría. El oráculo y el instrumento son nuevos y no calculan el esperado mediante el código juzgado; eso aporta una comprobación experimental separada, no independencia personal ni una revisión ciega de otro autor. La selección de casos sigue expuesta al sesgo del mismo autor.

[PR20](https://github.com/gatehot59-star/corpus-legal-tarija/pull/20). [Arreglo y recibo anterior](https://github.com/gatehot59-star/corpus-legal-tarija/blob/620994f76be2bdfacfad86680102bedd515a8871/docs/agents/respuestas/2026-09-20-02-logout-retry.md).

## Contrato y recursos

Productor: cliente real `sistema/web/discovery_spike.html`. Consumidor: Chromium real frente al servidor CLI `sistema/api/demo_discovery.py` y el logout persistente `isolated_session.py`. Login real emite la sesión; búsqueda y lectura reales prueban contenido positivo antes de cada fallo.

El oráculo fija antes de correr: al pedir cerrar, limpiar contenido de inmediato y bloquear acciones; una respuesta rechazada o ambigua no acredita revocación; conservar el mismo bearer solo para reintentar desde la UI; al confirmar, ese bearer debe recibir 403 en búsqueda. Recargar olvida la credencial, pero no demuestra revocación. Las expectativas son constantes escritas en el instrumento, no salidas de helpers del producto.

Gateway MUDH, brain-env, GitHub para revisiones y publicación documental, ClickUp público y Nexus para cierre. Chromium 153.0.8010.12 / Playwright 1.63.0 / Node 24.18.0 / Python 3.12.14 del entorno usado en esta jornada. Archives propios del SHA, fixtures nuevas por escenario, stores ficticios, loopback, timeouts, conexiones SQLite cerradas explícitamente. No cambios en producto, workflow, permisos, ramas de PR, bases reales, comentarios, merges ni despliegue. No se encendió otra ejecución CI: se consultó la existente.

## Mediciones nuevas

Instrumento completo `audit_logout_fix.cjs` incluido dentro de la evidencia. **Ocho escenarios, 163 comprobaciones con esperado explícito**, exit 0; repetición desde otro archive y fixtures nuevas: **163 comprobaciones**, exit 0. Son comprobaciones, incluidas preparación y limpieza, no 163 escenarios ni porcentaje de cobertura.

1. Marcador de fixture ausente: logout HTTP403 real. Al restaurarlo, el bearer original aún sirve antes del reintento y queda denegado después de confirmar.
2. Otro proceso sostiene `BEGIN IMMEDIATE`: logout HTTP503 real. Se libera y cierra la conexión; reintento con la sesión original revoca correctamente. No se simula el 503 ni se atribuye al producto una transacción de prueba.
3. Petición abortada antes de llegar al servidor: UI no confirma, conserva reintento, bearer sigue activo antes de cerrar de verdad.
4. Respuesta perdida después de que el servidor revocó: el instrumento envía el logout real mediante `route.fetch`, observa 200 y aborta la entrega al navegador. La UI dice cierre no confirmado aunque el bearer ya recibe403; el reintento idempotente confirma sin crear ni sustituir sesión.
5. HTTP200 con `logged_out:false`: fallo inyectado en la respuesta del navegador, no respuesta producida por el servidor. No se acepta como éxito; el reintento real revoca.
6. HTTP200 con JSON incompleto: mismo resultado seguro.
7. HTTP200 con `logged_out:"true"` como string: no se acepta como boolean true.
8. Recarga con cierre aún no confirmado, después de abortar la petición: la UI olvida la sesión y permite entrar nuevamente, pero el bearer original sigue válido. **Límite previo confirmado y ya declarado, no defecto nuevo del arreglo.** No se ensayó una recarga mientras una respuesta tardía siguiera en vuelo.

En cada cierre se retuvo temporalmente la primera petición para observar el estado pendiente: texto vacío, selección vacía, cero resultados y controles deshabilitados antes de recibir respuesta. Eventos sintéticos no duplican el logout ni habilitan búsqueda/lectura/login/descarga. Se comprobó que el bearer no aparece en DOM, URL, localStorage o sessionStorage. La credencial conserva sus privilegios en el servidor hasta revocarse; la separación de uso es del cliente, no un token servidor de permiso reducido.

## Falsadores causales

Dos mutantes servidos solo a la página de prueba mediante interceptación de HTML; ningún archivo de producto se modificó en git.

- Borrar `logoutToken` cuando llega403: exit1 exactamente en `marker403:failure_retry_enabled`. Login, contenido positivo, limpieza pendiente y estado403 habían pasado. La misma comprobación pasa sin el mutante.
- Omitir la eliminación inmediata de resultados al comenzar logout: exit1 en `marker403:pending_content_cleared`; observado `['',2,'ninguna']`, esperado `['',0,'ninguna']`. No se espera al catch para juzgar la limpieza inmediata. La misma comprobación pasa en el candidato.

Ambas salidas completas, las sustituciones exactas y hashes del HTML original/mutado están capturadas. No se tomó cualquier exit1 como detección válida.

## Referencia del autor, evidencia anterior y CI

Se reejecutó el banco publicado del autor: **59 comprobaciones Chromium**, exit0. `tests/test_isolated_session.py`: **10 tests**, exit0. Se mantienen separados del instrumento nuevo; no se reejecutaron aquí los140Python ni el banco37 anterior.

La evidencia del arreglo se recuperó de git y se decodificó estrictamente:85.540bytes y SHA256 `a5fefda71841dbd3a9cca3c5bfe9124223a3ddc82b2dc934d39db94e59721cd4`, coincidentes. Eso confirma integridad del paquete, no transforma sus afirmaciones en una nueva corrida.

El job existente106060447751 corresponde a `cc2ca307...` y figura completed/success. Se conserva estado y pasos; no se obtuvo stdout del runner ni se inició CI nuevo. Ningún informe del autor se usó como sustituto de probar el producto.

## Error del instrumento, conservado

En la primera ejecución, el registrador guardó una referencia mutable al array de estados HTTP: una respuesta200 posterior quedó agregada al `actual` de una comprobación que antes había evaluado `[403]` o `[503]`. Esto hacía inconsistente la captura final, aunque la comparación en ese instante hubiese pasado. No es fallo de PR20.

Se corrigió solo el instrumento con `structuredClone` de actual/expected antes de comparar y registrar. Se preservan íntegros la primera salida y el delta de esa versión; las dos ejecuciones finales usan observaciones congeladas y reemplazan ese intento como evidencia de la propiedad. No se borró el resultado inconveniente.

## Estados de afirmaciones y gates

**CONFIRMADO:** el arreglo permite reintentar tras403/503; no afirma éxito por fallos de red ni cuerpos200 inválidos; conserva el bearer original para reintento; mantiene la pantalla sin contenido mientras está pendiente; revoca o reconfirma idempotentemente la revocación; los controles experimentales detectan los defectos introducidos.

**CONFIRMADO, límite heredado:** recargar no revoca una sesión pendiente. La advertencia del cliente sigue siendo necesaria. Los fallos de transporte/cuerpo fueron inyectados en Playwright y no acreditan que el backend los emita espontáneamente.

**NO MEDIDO:** revisión externa por otro autor; concurrencia entre pestañas; respuestas tardías después de navegación; expiración durante un cierre lento; todos los códigos HTTP posibles; Firefox/WebKit, accesibilidad integral, cobertura de líneas/ramas, CVEs globales, producción o piloto jurídico. ¿Qué no se midió que importaba? La independencia de selección de casos de otro revisor y el ciclo de navegación con respuestas en vuelo.

Gate I PASA en alcance: sujeto exacto, oráculo fijado, positivos reales, dos mutantes con aserción causal, repetición nueva, captura íntegra corregida y recursos cerrados. Cada escenario registra servidor exit0 y listener cerrado; el lock termina exit0; scan final de procesos propios vacío. No se realizan hashes físicos SQLite ni se infiere consistencia WAL: N/A.

Gate II PASA en alcance: sin nuevo defecto demostrado; distingue simulaciones de respuesta, fallos reales SQLite y límite conocido; no mezcla conteos ni aprueba producto completo. La autoría compartida queda explícita.

Gate III: informe y evidencia documental se publican en main; su integridad, pertenencia a main, Doc público y Nexus se verifican como pasos finales antes del cierre de chat. Un resultado experimental no autoriza merge ni despliegue.

## Custodia y reproducción

[Evidencia de esta auditoría](https://github.com/gatehot59-star/corpus-legal-tarija/blob/main/docs/agents/evidencia/2026-09-20-03-pr20-logout-fix-audit.json): xz+base64, **110.141 bytes**, SHA256 `b58ea650791e6d9724673123b76c290edba9cbdbb2093a2c3a4d8f61f8d4e045`. Contiene instrumento completo, variante inicial, stdout/stderr íntegros de cada corrida, comandos, entornos, mutaciones, hashes de fuente, reconsulta de refs/CI y scan de procesos. Se excluyen valores de bearer desde la captura y se registran comparaciones booleanas, sin trazas de red ni screenshots.

Extraer el head indicado. Decodificar JSON de evidencia con base64 estricto y lzma, comprobar longitud/hash y recuperar `instrument.source`. Ejecutar `node audit_logout_fix.cjs <archive> all`; modos `mutant_forget` y `mutant_stale` deben dar rojo en las aserciones citadas. El script solo crea y elimina sus propias fixtures temporales, detiene sus listeners y no escribe en el archive. `runs.independent-final.env` conserva rutas del runtime utilizado; en otra máquina instalar el mismo Playwright/Chromium.

--- METODO PROMETEO ---
Acción delicada de producto: NO; auditoría experimental de ciclo de sesión, control final aplicado. Máquina: brain-env; CI existente consultado. Método: ASTRA AUDITOR CORPUS, gates separados, sin score numérico usado como aprobación. Revisión externa: pendiente, mismo autor del arreglo. Artefactos: este informe y evidencia en git; espejo público de ClickUp y continuidad Nexus completados y enlazados en el cierre. Sin merge ni despliegue.
