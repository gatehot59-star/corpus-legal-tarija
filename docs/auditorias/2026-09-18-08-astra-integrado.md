# Astra: sesiones persistentes verificadas; falta componer el consumidor aislado

18-sep-2026 ART (UTC-3). Encargo aceptado por Abraham mediante elección explícita de GitHub del workspace. Auditoría acotada del incremento integrado, no implementación. Revisión, verificación experimental y control final son funciones del mismo operador, no tres testigos independientes.

## Dictamen y prioridad

**No encontré un nuevo defecto del producto en las propiedades ensayadas.** El logout revoca únicamente el bearer presentado, conserva las otras sesiones y sigue revocado después de terminar el proceso servidor y abrir otro proceso del sistema operativo sobre el mismo store. Se repitió en un store nuevo. No es crash recovery ni reinicio de máquina.

**El menor bloqueo demostrado hacia un recorrido usable es la composición explícita.** El handler de `sistema/api/servidor.py`, seleccionado por el arranque documentado en `sistema/README.md`, sirve salud pero no monta el wrapper nuevo. En scratch: GET salud200, POST login501, POST logout501 y GET texto v2 404. En cambio, elegir `IsolatedSessionApp` expresamente permite el recorrido probado. No es una regresión imprevista: el incremento declara que no reemplaza el servicio existente.

Recomendación acotada, NO implementada: un lanzador reproducible y explícito de la demo aislada que seleccione el wrapper, un candidato versionado y un store ficticio separado, con inicialización verificable. No empezar por otra ronda de79tests ni asumir que mergear expone las rutas. Una interfaz, recuperación/restore, provisión real y permisos jurídicos/humanos de piloto requieren alcance y autorización separados.

**El entrypoint del host productivo NO MEDIDO.** Solo se identificó y ejecutó el handler del entrypoint documentado; no se consultó ni tocó VM, configuración viva, servicios o bases productivas.

## Sujeto congelado y contexto

Repo `gatehot59-star/corpus-legal-tarija`. Main al inicio `526a29a92144f24853f56595d2eea4bdb836967c`; producto integrado `30189275ea996e23aa7804e2334f0b9ba93dd8d1`. El delta desde el main1178057 del encargo solo agrega documentos. Plan original y enmienda v2 no cambiaron respecto del contexto leído. Nexus43/44 y las revisiones06/07 se recuperaron antes de medir.

Productor/consumidor ensayado: `IsolatedSessionApp` hereda los guards de `IsolatedLoginApp`, delega lectura a `SQLiteAccessPolicy` y `ExactReaderApp`, que usa `read_version`. Fixtures SQL propios, texto esperado de1.793 puntos de código fijado fuera del productor, Unicode, CRLF y37 repeticiones. Se identifica explícitamente el hash del texto UTF8; no se atribuye semántica textual a hashes PDF de otros registros.

Entorno: brain-env mediante Gateway MUDH build, Python3.12.14, SQLite3.46.1,2CPU. HTTP real en127.0.0.1. No Actions/GPU/VM iniciados. Conexión de publicación autorizada: workspace. No se extrajeron credenciales del taller.

## Integración comprobada

Se ejecutó `git merge-tree --write-tree eef9bf2e20c93c582145a776df180b104037ec12 21ab505ef2f9dd0245971c265fafbb018a8fa7cb` sin cambiar ramas. Returncode0, stderr vacío, tree `110dccfa2da21ff08fbac7b875d705f6cf496ade`: idéntico a `30189275^{tree}`.

Diff de sistema/pipeline/tests/workflows desde ese merge al main ensayado: vacío. Consulta específica autenticada PR7: closed/merged:true. Consulta específica PR1: open/merged:false, head `2360f27d43fdc9a1e2a74a3f6465698918df2ad1`; `merge-base --is-ancestor` de ese head a main devuelve1, sin errores. PR1 sigue excluido. Su conflicto no hace falta para resolver este incremento, por lo que no se reauditaron sus32archivos ni se intentó reconciliarlos.

El workflow leído dispara en pull_request/manual, no push a main. No se certificó un nuevo CI de main ni se disparó manualmente. Las79pruebas de autor siguen siendo antecedentes: no se repitieron ni sumaron como medición nueva.

## Recorrido nuevo y repetición

Instrumento propio `integrated_probe.py`, no hereda fixtures del autor. Credenciales ficticias con verificador scrypt construido directamente, dos identidades y dos sesiones reales emitidas para una misma identidad. Grants introducidos por SQL explícito, no por login.

Baseline:69 comprobaciones satisfechas, salida0. Repetición íntegra en otro temporal:69, salida0. No son138tests independientes: incluyen páginas y controles repetidos del mismo recorrido.

- Login200, cuenta sin grant403, grant explícito y texto paginado íntegro con páginas de113 puntos de código.
- Quitar marca bloquea lectura, logout y login403 sin revocar la sesión; restaurarla reanuda200. Retirada documental o revocación del grant entre páginas rechaza403; otro usuario conserva su acceso cuando solo se revoca el grant de la primera identidad.
- Un lock escritor sintético BEGIN IMMEDIATE impide logout:503, sin logged_out:true. Tras liberar el lock, consulta directa devuelve revoked_atNULL y lectura200. Reintentar logout200 persiste revoked_at1000, y la página siguiente403.
- La segunda sesión del mismo usuario y la de otra identidad siguen200. Repetir logout conserva la primera fecha.
- Se terminó ordenadamente el proceso31665, retorno0, puerto cerrado; se inició31666 sobre el mismo store. La sesión revocada sigue403 y las otras dos200. Repetición independiente con procesos31729/31730 confirma lo mismo. No se reutilizó simplemente un objeto.
- Reloj igual1000.25 admite login. Password erróneo1010.8 devuelve401 y persiste high-water1010.8;1010.7 devuelve503. El presupuesto llega a cinco mediante requests reales, sin forzarlo con SQL; intento1011.9 devuelve429 y persiste1011.9. En proceso nuevo,1011.8 devuelve503 y1062 recupera login200.
- Store sintético sin tabla login_clock: login503, lectura previamente autorizada200, logout de una sesión ficticia200 y ninguna automigración. Reponer explícitamente el esquema de fixture restablece login200. Esto no autoriza una migración real ni ofrece monotonicidad global de lecturas.

El archivo candidato conservó su hash. Objeto de esa comparación: SQLite principal del candidato cerrado tras preparar el fixture; no se compara como inmutable el store de sesiones, que debe cambiar. No se certifican sidecars productivos.

## Qué no se repitió por ceremonia

Mientras se recuperaba contexto ya existía la auditoría07 de locks: cuatro situaciones, incluido UPDATE seguido de COMMIT ocupado y ROLLBACK, con falsador de falso éxito. Se verificó su bundle publicado de190.533bytes y SHA256 declarado. Se reutiliza como antecedente, no como ejecución propia ni hallazgo nuevo. Aquí se ejecutó un ancla writer-lock acotada y se priorizó lo pendiente: persistencia en proceso nuevo y sesiones de dos identidades.

También se decodificó y verificó el bundle06 de55.496bytes. Ambos hashes, revisiones y distinción histórica están en context.json. No se certifica por eso todo el trabajo histórico.

## Falsadores del banco

Copias separadas del código; baseline positivo y la misma aserción objetivo negativa. Cuatro mutantes, cada uno detectado sin depender únicamente de exit1:

| Mutante | Aserción objetivo |
| --- | --- |
| No persistir revocación | revoked_next_page |
| Revocar todas las sesiones | same_identity_other_session |
| Ignorar high-water | rollback_after_wrong_password |
| Ignorar marca en despacho | pause_read |

Se preservaron modificaciones exactas, resultados originales/mutados, comandos, stdout/stderr completos y respuestas HTTP. Los fallos derivados no se cuentan como defectos independientes. El sondeo del handler documentado tuvo un positivo salud200: sus501/404 no se explican por servidor inaccesible.

## Recursos, seguridad y exclusiones de captura

Todas las conexiones propias de preparación/consulta usan cierre explícito; lock cerrado y rollback en finally; HTTPConnection cerradas. Los workers instrumentaron las conexiones del producto: baseline109/109 y21/21 cerradas; repetición igual. Cero abiertas en los doce workers de baseline, repetición y cuatro variantes; todos retornaron0, cerraron listeners y ya no figuraban en/proc. Supervisores terminados en estadoZ, sin ejecución activa. No se infiere cierre por el mero timeout.

Captura: cuerpos y headers completos de respuestas, excluyendo valores access_token sintéticos al capturar. Requests password/Authorization no se registran. Logs de worker/supervisor completos. No bases, credenciales reales ni textos de causas publicados. Fuentes completas de instrumentos incluidas; producto reproducible desde SHA fijado, con hashes individuales en context.json.

## Estados y control final v2

CONFIRMADO: composición aislada explícita, exactitud del fixture, permisos ensayados, revocación selectiva, rechazo correcto bajo lock escritor, high-water de login y persistencia después de terminar/reabrir un proceso. Integración simulada coincide y PR1 queda excluido.

REFUTADO dentro del alcance: que arrancar el handler documentado ya ofrezca las rutas v2; que el lock ensayado signifique logout confirmado; que se necesite revocar otras sesiones para cerrar una.

NO MEDIDO: configuración del host vivo, caída durante COMMIT, crash recovery, restore real, reinicio de máquina, carga o concurrencia arbitraria, proxy/TLS, usuarios/provisión real, vigencia/privacidad jurídicas,6079documentos, búsqueda/citas/export y utilidad comercial. No evaluación entre modelos ni A/B de skills. Despliegue N/A: no autorizado ni requerido para esta auditoría.

Gate I PASA acotado: sujeto pinneado, golden externo, baseline limpio, falsación dirigida, cierre explícito, repetición nueva y capturas recomputables. Gate II PASA acotado: causalidad, límites, prioridades y reproducción separados. Ninguna nota numérica levanta pendientes. Gate III: evidencia remota ya verificada; informe, Doc público y Nexus se verifican como pasos de entrega, no como propiedades del producto.

## Evidencia, custodia y reproducción

Carpeta `docs/auditorias/2026-09-18-08-astra-integrado/`. Concatenar `evidence.xz.b64.part0`, `part1`, `part2` en ese orden, sin separadores:8.000+8.000+7.916caracteres. Base64 estricto, luego lzma.decompress. JSON íntegro:550.961bytes, SHA256 `2db93dea9e58bab24545763c2fb7b12349fcf7cf2b2cd0c0f14dd69fbbb0aa08`.

Los tres tramos se recuperaron desde commit `d60ac0498a2993b900f67f79d6918c8f9cc8c890`: comparación byte por byte con original=True; commit antecesor de main=True; delta de producto desde el SHA probado vacío. Sin recortes de captura ni binarios commiteados.

Para reproducir: extraer las fuentes de files del JSON, recuperar main526a29a en repo, ejecutar `python3 integrated_probe.py repo baseline.json`, luego `python3 integrated_mutate.py <raiz>`, y `python3 documented_host_probe.py <raiz>`. El probe crea sus propios temporales, inicia y termina workers y no necesita tokens o bases previos. La repetición vuelve a invocar el probe hacia repeat.json. Variantes y errores se conservan en sus archivos, no se mezclan con baseline.

No se publican retrospectivamente como completados los informes locales01/03 ni la entrega ajena pendiente de4,7MB. Esta entrega corresponde únicamente al encargo integrado aceptado ahora.
