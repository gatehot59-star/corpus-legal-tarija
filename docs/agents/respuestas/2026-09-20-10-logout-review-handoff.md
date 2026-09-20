# PR20: pase focalizado para revisión de logout

## Encargo y estado

Preparar una revisión por alguien distinto de quien implementó el arreglo. Este paquete no envía una solicitud, no asigna un revisor y no cierra G2. No autoriza merge, despliegue ni cambios de producto. Rol de esta entrega: documentación y comprobación de fuentes, no nueva auditoría experimental.

Consulta GitHub del 20-09-2026 a las 14:39:21 UTC: [PR20](https://github.com/gatehot59-star/corpus-legal-tarija/pull/20) abierto, sin merge; head `ca503377760a8dcd7965689a2853420785a83d94`, base PR19 `31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05`. Main documental `4a30db151e5f367850b2b7627c4d5b487c29eb78`. La API de reviews devolvió `[]`; eso no descarta revisiones privadas ni demuestra una regla de aprobación obligatoria.

El arreglo está en `cc2ca30760c486cad3154c619a20f94cf75cc691`, contra `a8aeb301f8840caa547e48730a46e1b9406927bc`. Desde ese arreglo hasta el head actual solo cambió `tests/browser_discovery.cjs`: 56 líneas añadidas para selección. El HTML de logout no cambió. Astra implementó el arreglo y operó sus pruebas posteriores: no presentarlas como revisión externa.

## Pregunta de decisión

¿El cliente conserva un camino explícito para revocar la sesión original cuando el cierre no está confirmado, sin seguir mostrando contenido protegido ni habilitar acciones ajenas al cierre?

El defecto anterior era concreto: un logout rechazado con 403 eliminaba el único bearer del cliente y deshabilitaba el reintento, aunque la sesión seguía activa en el servidor. No se demostró un bypass remoto ni una confirmación falsa de cierre.

El arreglo mueve el bearer original a `logoutToken`, vacía `token`, limpia contenido/selección/resultados y bloquea las demás acciones. Solo una respuesta cuyo `logged_out` sea el booleano `true` descarta el handle y confirma. Ante rechazo, transporte fallido o cuerpo inválido, permite reintentar con el mismo bearer. Este conserva privilegios en el servidor hasta la revocación real: no es una credencial de permisos reducidos.

## Entrada al código, en este orden

1. [Diff del arreglo](https://github.com/gatehot59-star/corpus-legal-tarija/compare/a8aeb301f8840caa547e48730a46e1b9406927bc...cc2ca30760c486cad3154c619a20f94cf75cc691). Separar el cambio de HTML de su banco de pruebas.
2. [Cliente actual](https://github.com/gatehot59-star/corpus-legal-tarija/blob/ca503377760a8dcd7965689a2853420785a83d94/sistema/web/discovery_spike.html): estado y controles líneas 13-14; guard y limpieza 58-70; petición, validación y catch 130-140; descarte al navegar 143-148. Leer también `request`, que borra `token` ante 403.
3. [Logout persistente](https://github.com/gatehot59-star/corpus-legal-tarija/blob/ca503377760a8dcd7965689a2853420785a83d94/sistema/api/isolated_session.py), especialmente `logout_request`, y su composición en [demo_discovery.py](https://github.com/gatehot59-star/corpus-legal-tarija/blob/ca503377760a8dcd7965689a2853420785a83d94/sistema/api/demo_discovery.py). No juzgar la UI sin el consumidor HTTP real.
4. [Banco actual](https://github.com/gatehot59-star/corpus-legal-tarija/blob/ca503377760a8dcd7965689a2853420785a83d94/tests/browser_discovery.cjs), bloque de rechazos y recuperación aproximadamente 120-205. [CI existente](https://github.com/gatehot59-star/corpus-legal-tarija/blob/ca503377760a8dcd7965689a2853420785a83d94/.github/workflows/clean-snapshot.yml) ejecuta ese banco; no confundirlo con provenance-v2.yml.

## Evidencia reutilizable, no corridas nuevas

Los cuatro paquetes siguientes se recuperaron de main y decodificaron con base64 estricto y xz en este turno. Sus tamaños y SHA coinciden con los informes. Son evidencia histórica contra cc2ca307; esta preparación no volvió a ejecutar Chromium.

| Fuente | Qué aporta y qué no |
| --- | --- |
| [02: arreglo](2026-09-20-02-logout-retry.md) | 59 comprobaciones Chromium repetidas; HTML viejo con banco nuevo falla en `logout_403_attempt_1_retry_enabled`; mutante de pérdida del handle falla en la misma propiedad. |
| [03: prueba focalizada](../../auditorias/2026-09-20-03-pr20-logout-fix-audit.md) | Ocho escenarios, 163 comprobaciones repetidas: 403 real, bloqueo SQLite/503 real, petición abortada antes del servidor, respuesta perdida después de revocar, cuerpos 200 inválidos y recarga. Mutantes detectados en `marker403:failure_retry_enabled` y `marker403:pending_content_cleared`. |
| [04: navegación](../../auditorias/2026-09-20-04-delayed-logout-navigation.md) | 110 comprobaciones repetidas; documentos nuevos, respuesta antigua 200/403 y sesión nueva sin contaminación observada durante 300 ms. El control rojo altera el detector, no el producto. No prueba BFCache. |
| [05: BFCache](../../auditorias/2026-09-20-05-bfcache-pending-logout.md) | Control cacheable restaurado realmente; PR20 volvió como documento nuevo. Callback en el mismo documento restaurado: NO MEDIDO, no bug demostrado. |

Paquetes canónicos bajo `docs/agents/evidencia/`, en el main fijado arriba:

| Archivo | Bytes decodificados | SHA-256 |
| --- | ---: | --- |
| 2026-09-20-02-logout-retry.json | 85540 | a5fefda71841dbd3a9cca3c5bfe9124223a3ddc82b2dc934d39db94e59721cd4 |
| 2026-09-20-03-pr20-logout-fix-audit.json | 110141 | b58ea650791e6d9724673123b76c290edba9cbdbb2093a2c3a4d8f61f8d4e045 |
| 2026-09-20-04-delayed-logout-navigation.json | 126702 | 30814e05e02e7ac6af5ea4b2432d6e14d87a7776636588d7d39f09429bfc43ef |
| 2026-09-20-05-bfcache-pending-logout.json | 178839 | d175c44c881fc010ee67a6bf01d18ff54d72b82af311a66c34c152605bdd4fc5 |

Todos usan un campo `data` base64 de xz. En 03, `instrument.source` contiene `audit_logout_fix.cjs`, y `runs` conserva comandos y salidas. En 04 también existe `instrument.source`; en 05 las fuentes/capturas están en `files`. Revisar primero argumentos y captura del instrumento antes de lanzarlo en un archive propio.

Entorno histórico: Python 3.12.14, Node 24.18.0, Playwright 1.63.0 y Chromium 153.0.8010.12. En brain-env, NODE_PATH `/workspace/corpus-browser-spike-u6wwk669/.browser-tools/node_modules` y LD_LIBRARY_PATH `/workspace/corpus-browser-spike-u6wwk669/.browser-tools/sysroot/usr/lib/x86_64-linux-gnu`; son punteros de entorno, no garantía para otra máquina. El comando existente de CI es `timeout 120s node tests/browser_discovery.cjs`, después de preparar sus dependencias como indica el workflow.

La [entrega 09](2026-09-20-09-selection-ci.md) añadió la regresión de selección: 88/88 locales dos veces y dos mutantes detectados. [CI del head actual](https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35515778571/job/106091355198) tuvo success; los conteos son locales, no stdout recuperado de Actions. Esto aborda G1, no sustituye la revisión de logout G2.

## Trabajo focalizado propuesto al revisor

Elegí tus casos antes de reutilizar los instrumentos del autor. Priorizá propiedades que podrían cambiar la decisión sobre este arreglo, no una nueva auditoría de todo Corpus.

1. Partí de login, búsqueda y lectura positivos. Retené la respuesta de cierre y comprobá limpieza inmediata y bloqueo tanto por controles como por eventos disparados programáticamente.
2. Provocá rechazo antes de revocar: 403 y 503 reales en fixture propia. Comprobá que todos los intentos usan el bearer original, no crean otra sesión y no se reintentan solos.
3. Separá fallo antes de llegar al servidor de respuesta perdida después de revocar. Contrastá estado de UI con petición HTTP independiente usando el bearer original. Un fallo de transporte no demuestra ninguno de esos estados por sí solo.
4. Desafiá la confirmación: falso, ausente, string y booleano true. Después de confirmar, exigí denegación del bearer original; mantené una segunda sesión como control de que no se revocan sesiones ajenas.
5. Elegí al menos un borde no cubierto que juzgues material. Candidatos declarados: expiración durante un cierre lento o interacción entre pestañas. BFCache solo permite afirmar algo del callback si se demuestra mismo documento restaurado, no con un evento sintético ni quitando protecciones del producto.
6. Falsá tu criterio: positivo de la propiedad pasa y mutante causal falla en esa misma aserción. Guardá el delta y la salida completa, no cualquier exit 1 como detección.

Usá exclusivamente fixtures ficticias, archives separados y listeners loopback. No cambies producto para facilitar la prueba. Cerrá conexiones, bloqueos, procesos y puertos propios; no registres bearers, contraseñas ni cabeceras Authorization.

## Criterio de salida

**Sin reparos en el alcance:** expectativas independientes satisfechas, falsadores causales detectados, evidencia reproducible y límites explícitos. No equivale a autorización de merge.

**Con reparos:** reproducción sobre head identificado que pierda el reintento, conserve contenido mientras cierra, permita acciones ajenas, acepte confirmación inválida, deje utilizable el bearer tras confirmación real o revoque una sesión ajena. Distinguir instrumento/transporte/producto antes de atribuir causa.

**NO MEDIDO:** precondición no alcanzada o evidencia insuficiente. No contarlo como aprobado ni convertirlo automáticamente en bloqueo. Recargar/navegar olvida el handle y no revoca: límite previo, no defecto nuevo salvo contradicción concreta del contrato.

Entregar revisión, archivos/líneas, casos elegidos y por qué, esperado/observado, positivos/falsadores, comandos/salidas completas, revisión final del head y recomendación acotada. G2 cambia de estado cuando exista esa revisión de otro autor, no cuando se publique este pase.

## Método y cierre documental

TITAN LIGERO, documentación focalizada; no orden enviada ni ejecución delegada. Rúbrica numérica N/A. Gate I: N/A para nuevo experimento; comprobación documental de refs, diff y decodificación real. Gate II: alcance, criterios y límites declarados. Gate III se completa únicamente con readback byte a byte, pertenencia a main, Doc público leído y Nexus; el cierre verificable se registra allí.

Error propio de preparación: el repositorio de objetos no tenía remote origin; `fetch origin` falló y se recuperó usando la URL pública explícita. Sin impacto sobre producto ni evidencia histórica. No se ejecutaron pruebas, merges, despliegues, comentarios, solicitudes de review ni asignaciones.
