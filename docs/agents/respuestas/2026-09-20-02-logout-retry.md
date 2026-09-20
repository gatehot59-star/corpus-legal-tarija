# PR20: reintento de cierre corregido, sin merge ni despliegue

## Pedido y autorización

Corregir el reintento de logout de PR20. Lote aprobado mediante el botón del 20-09-2026: cliente, banco Chromium, recibo, evidencia, Doc público y continuidad. No autoriza merge, despliegue, mensajes a terceros ni cambios en otros PRs. Ruta: Space > este Doc público.

## Conclusión

El arreglo está en [PR20](https://github.com/gatehot59-star/corpus-legal-tarija/pull/20), commit `cc2ca30760c486cad3154c619a20f94cf75cc691`, sobre `a8aeb301f8840caa547e48730a46e1b9406927bc`. El cliente conserva la credencial original en memoria exclusivamente para reintentar el cierre. No vuelve a habilitar búsqueda, lectura, descarga ni login mientras falta confirmar la revocación. Un 403 ordinario de lectura mantiene el comportamiento anterior: limpiar contenido y exigir un login nuevo.

La credencial no se transforma en un token de privilegios reducidos en el servidor: sigue siendo el bearer original. La restricción de uso es del cliente. La autorización y revocación del backend no se modificaron.

## Herramientas, máquina y alcance

GitHub y Gateway MUDH para leer refs, código, PRs abiertos, ejecutar Python y Chromium, publicar los dos archivos de producto en `titan/protected-discovery` y releer sus bytes. ClickUp para este Doc público. Ejecución local en brain-env; CI existente en Actions ubuntu-24.04, sin editar workflow. Python 3.12.14, Node 24.18.0, Playwright 1.63.0 y Chromium 153.0.8010.12 medidos. Sin dependencias nuevas, secretos, datos reales ni servicios expuestos fuera de loopback.

Cambio de rol explícito: Astra implementa este arreglo; no se presenta como su auditor independiente. Roles aplicados: lectura del repositorio, contrato de estados, implementación, revisión de seguridad acotada, pruebas y documentación; evaluación final del autor, no aprobación externa.

## Código y comportamiento

Solo dos archivos de producto, 105 inserciones y 8 eliminaciones:

- `sistema/web/discovery_spike.html`: estado `logoutToken` separado del token de lectura; traslado al iniciar el cierre; limpieza inmediata de texto, selección y resultados; bloqueo de acciones ajenas al cierre; conservación ante respuesta rechazada; descarte al confirmar o abandonar la página.
- `tests/browser_discovery.cjs`: fallos reales previos a revocación mediante intervención controlada del marcador de la fixture; dos rechazos consecutivos por cada estado 403 y 503; mismo bearer en todos los intentos; contenido limpio, acciones bloqueadas, ausencia en DOM/URL/storage, recuperación y revocación del bearer original. Fixtures separadas para respetar, no debilitar, el límite persistente de cinco logins por minuto.

No se modifican autorización, búsqueda, lector, servidor, rate limiter, workflow ni otras ramas. No se agregan mejoras ajenas al alcance.

## Mediciones

El banco nuevo sobre el HTML anterior falla con exit 1 exactamente en `logout_403_attempt_1_retry_enabled`, después de login, contenido positivo y logout 403 real. Sobre el arreglo: **59/59 comprobaciones Chromium**, exit 0, repetidas en otra ejecución con fixtures nuevas: **59/59**, exit 0. Al sabotear únicamente la conservación de `logoutToken` ante 403, vuelve a fallar con exit 1 en la misma comprobación.

Regresión Python: **140 tests**, las diez suites del workflow, todos exit 0. Banco Chromium anterior de autenticación y referencias: **37 comprobaciones**, exit 0 y sin errores del navegador. Validación sintáctica del banco nuevo y compileall de API/tests: exit 0.

Instrumentos de la auditoría previa, ejecutados sin cambios contra el arreglo: **38 aserciones HTTP** pasan; las observaciones de navegador para 403 y 503 muestran login 200, búsqueda 200, cierre rechazado con reintento habilitado, sesión original aún activa antes del reintento y 403 con ese mismo bearer después del cierre confirmado. El script de observación no convierte su exit 0 en una aprobación: la conclusión se deriva de esos estados registrados.

CI del commit exacto `cc2ca307...`: job `106060447751`, completado con success y **10 pasos exitosos**, incluidos Python y ambos bancos Chromium. Se conserva la respuesta completa de metadatos; no se afirma haber obtenido stdout del runner. Los conteos anteriores proceden de las ejecuciones locales.

## Evidencia cruda y reproducción

[Evidencia](https://github.com/gatehot59-star/corpus-legal-tarija/blob/main/docs/agents/evidencia/2026-09-20-02-logout-retry.json): envoltorio `xz+base64`, **85.540 bytes decodificados**, SHA-256 `a5fefda71841dbd3a9cca3c5bfe9124223a3ddc82b2dc934d39db94e59721cd4`. Contiene comandos, códigos de salida, stdout/stderr completos, variantes reproducibles, instrumentos anteriores, runtimes, readback, cierre de procesos y metadatos de CI. El veredicto está separado de esas salidas.

Para repetir: extraer el commit del arreglo, disponer de Playwright/Chromium indicados y ejecutar `node tests/browser_discovery.cjs`. Para el rojo inicial: extraer la base y usar únicamente el banco nuevo. Para el mutante: aplicar al arreglo el delta `source_variants.mutant_diff_from_head` de la evidencia y ejecutar el mismo banco. No aplicar ese mutante al PR.

Se preservan también dos intentos inválidos: primero hubo prefijos `+` en la transferencia de archivos, que produjeron un error de sintaxis; después el banco ampliado agotó el presupuesto de logins de una sola fixture. Ninguno cuenta como control rojo válido. Se corrigió el transporte y se separaron las fixtures sin tocar el backend. Una llamada larga al Gateway venció, pero la ejecución continuó y se recuperaron todas sus salidas guardadas.

Readback del producto, byte por byte igual a lo probado: HTML 13.870 bytes, SHA-256 `69eba91fcf88b5c0547e263276cfc1a9f0da2703b91a1601397e8fffb0b5efdb`; banco 12.632 bytes, SHA-256 `3db3319d302149a7a06d24046fa995eb668e9e92ee366ef534378f72329fff09`.

## Archivos documentales y límites

[Recibo en git](https://github.com/gatehot59-star/corpus-legal-tarija/blob/main/docs/agents/respuestas/2026-09-20-02-logout-retry.md) y evidencia en `docs/agents/evidencia/2026-09-20-02-logout-retry.json`, append-only en main. El código permanece en PR20, abierto y sin merge. No se despliega ni se envían comentarios de PR o instrucciones a otros ejecutores.

NO MEDIDO: revisión independiente del arreglo, cobertura de líneas/ramas JavaScript, auditoría general de CVEs, otros navegadores, accesibilidad integral, concurrencia, producción y uso jurídico. Recargar o cerrar la pestaña todavía pierde la credencial en memoria y no equivale a revocarla; ese límite preexistente no se amplía a persistencia automática.

## Evaluación acotada del autor

77/85 = **90,59/100**, no aprobación independiente. Completitud 15/15: dos archivos íntegros y readback; ejecutabilidad 15/15: bancos y CI; seguridad 12/15: aislamiento del estado pendiente y no exposición en DOM/URL/storage, sin auditoría general de CVEs; testing 12/15: baseline y mutante rojos, repetición verde y regresión, sin cobertura JS medida; arquitectura 9/10: estado separado, backend intacto, límite de recarga declarado; documentación 10/10: recibo, evidencia reproducible y espejo público; proceso 4/5: salidas crudas, falta revisión externa. N/A 15 puntos: DevOps 10 por prohibición expresa de despliegue y ausencia de cambios de infraestructura; innovación 5 porque mejoras adicionales quedan fuera del arreglo autorizado.

--- METODO PROMETEO ---
Acción delicada: SI. Modo: FULL. Máquina: brain-env y Actions ubuntu-24.04. Rúbrica del autor: 77/85, 90,59/100; 15 puntos N/A justificados. Review externo del arreglo: pendiente, no solicitado mediante mensajes en este turno. Instrumentos: Chromium real, Python y CI del commit exacto; evidencia cruda enlazada. Artefactos: recibo y evidencia en git, más este [Doc público](https://app.clickup.com/90171457413/docs/2kza6fw5-13717).
