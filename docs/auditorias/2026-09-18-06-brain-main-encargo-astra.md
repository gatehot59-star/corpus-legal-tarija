# BRAIN: revisión del main integrado y encargo acotado para Astra Auditor

18-sep-2026 ART. Pedido de Abraham: auditar lo nuevo de BRAIN y preparar instrucciones para Astra. No se envía una orden a otro agente ni se modifica el skill; este archivo es el encargo listo para una instancia nueva.

## Dictamen en criollo

El avance se sostiene en el alcance probado: PR12 corrige la pausa por marca y el reloj de login; PR13 agrega logout persistente; la cadena PR7 a PR13 quedó integrada en main. Repetí los 79 tests del autor, sus tres falsadores de logout y 22 comprobaciones propias. No apareció un fallo nuevo de producto en esas corridas. Eso NO acredita Corpus vivo, integración productiva, piloto ni utilidad jurídica.

Mi prueba propia también fue falsada: ignorar el high-water rompe exactamente dos controles de rollback; no persistir logout rompe tres controles de revocación. No se usa el mero exit1 como prueba de sensibilidad.

## Sujeto exacto, revisiones y permisos

Repositorio: gatehot59-star/corpus-legal-tarija.

- Main leído y probado: `1178057e2a7744d1494554d1c45de651855ceee1`.
- Merge de producto: `30189275ea996e23aa7804e2334f0b9ba93dd8d1`; entre este y 1178057 solo cambian tres archivos documentales, no sistema/pipeline/tests/workflows.
- PR12 código: `314c6d7e9286a0bcca9ce0cacbfa0312c301f93f`.
- PR13 código: `de4551825704a036d979b5245cd5bdebbe993e37`; cabeza con recibo `21ab505ef2f9dd0245971c265fafbb018a8fa7cb`.
- Base anterior: `eef9bf2e20c93c582145a776df180b104037ec12`; PR11 anterior: `3a60627101859ca92c9b0a4fdd436205b99bb504`.
- PR1 permanece abierto, cabeza `2360f27d43fdc9a1e2a74a3f6465698918df2ad1`; no lo integro ni lo corrijo.

La conversación de las 20:42 ART muestra el botón del lote PR13→PR7 como autorizado, excluyendo PR1 y despliegue. El cierre de las 20:56 y git coinciden en el alcance. No se interpreta esa autorización de merge como permiso de intervenir producción.

Se verificó el inventario disponible del taller y el método ya leído; medición actual: Python/SQLite y CPU en la evidencia. Se usó brain-env mediante gateway; no VM, Actions ni GPU disparados para esta revisión.

### Integración contrastada, no solo recibo

Se regeneró sin mover ramas:

`git merge-tree --write-tree eef9bf2e20c93c582145a776df180b104037ec12 21ab505ef2f9dd0245971c265fafbb018a8fa7cb`

Salida completa: `110dccfa2da21ff08fbac7b875d705f6cf496ade\n`; stderr vacío; returncode0. Es exactamente el tree del merge30189275 y el preflight guardado por BRAIN. El tree completo de PR13 solo NO es ese tree porque main contiene documentos de auditoría adicionales; no confundir comparación de producto con igualdad de todos los archivos.

El listado autenticado de PRs devolvió state closed y merged_at para7..13, pero también merged:false. No lo tomé como prueba de no-merge: consulta específica get de PR7 devolvió merged:true y la historia git contiene la cadena. Este conflicto del listado queda declarado; no se presenta una reconsulta específica de los siete que no se hizo. PR1 sigue open en el listado. La API anónima alcanzó rate limit403; se cambió al conector autenticado sin tocar credenciales.

## Qué se ejecutó y qué demuestra

Archivo nuevo de ejecución: `probe.py`, incluido íntegro en evidencia. Oráculo propio: texto fijo Unicode repetitivo, SHA calculado fuera del lector, SQL sintético, scrypt directo, reloj fijado y login real por HTTP loopback. No se importaron helpers de tests de BRAIN. Todas las conexiones propias usan cierre explícito; HTTPConnection y listener se cierran en finally.

22 comprobaciones, todas satisfechas:

1. Dos logins reales emiten sesiones ficticias; sin grant la lectura da403; grant SQL explícito permite200 y texto íntegro.
2. Quitar marca bloquea lectura y logout con403; restaurarla reanuda lectura. La pausa NO equivale a revocación permanente.
3. Logout devuelve200, próxima lectura403 y otra sesión del mismo usuario sigue200. Repetición conserva la primera fecha. Recrear la app sobre el mismo store no revive la sesión.
4. Retroceso fraccional de1000.8 a1000.7 produce503. Se fuerza de forma declarada presupuesto agotado por SQL propio: login1010.8 da429 y persiste1010.8 como high-water; recrear app y probar1010.7 da503. Se ensaya la rama throttled, no se simulan seis intentos naturales.
5. Logout con reloj hacia atrás999 sigue revocando; luego1100 no revive acceso. Archivo candidato conserva sus bytes y listener termina.

Los resultados guardan estados y valores de las propiedades comprobadas, incluido texto completo comparado. No se afirma captura de todo tráfico HTTP: tokens, passwords y headers de Authorization no se registraron. Los stdout/stderr de los procesos sí están completos. No confundir este alcance de captura declarado con los recortes históricos de otros instrumentos.

Falsadores propios en copias nuevas:

- Suprimir guard high-water: baseline positivo, luego fallan `fractional_rollback_login` y `rollback_after_throttle_and_recreate`;22checks,exit1.
- Hacer que UPDATE conserve revoked_at NULL: fallan `revoked_next_read`, `revocation_recreated_app`, `backward_logout_still_revoked`;22checks,exit1.

Además se reejecutó el instrumento de BRAIN leído antes: cinco suites10+18+15+15+21=79tests,compile exit0; sus tres mutantes exit1 por assertions de revocación, otras sesiones e idempotencia. Son suite e instrumento del autor, no79 oráculos independientes. No se suman repeticiones ni herencia para inflar el total.

El workflow leído solo dispara por pull_request/manual, no por push a main. BRAIN declara check_runs0 del merge y no promete CI nuevo en main. Ese conteo remoto no fue remedido por esta instancia al fallar la API anónima; las corridas posteriores de taller sí fueron nuevas.

## Límites y reparos de proceso

No encontré un nuevo defecto de producto en las propiedades anteriores. No se probaron concurrencia, contención del store, caída de proceso durante COMMIT, recuperación real, proxy/TLS, VM, corpus vivo ni cuentas humanas. Recrear objeto no es reiniciar proceso o máquina.

Los bancos heredados del autor todavía tienen contextos `with sqlite3.connect(...)` que por sí solos no cierran conexiones. No produjo fallo en esta corrida; tampoco certifico cierre exhaustivo de sus recursos. Astra debe separar esa deuda del instrumento de corrupción de producto. Mi banco no reutiliza esos fixtures y cierra explícitamente.

El contrato de logout con bearer desconocido/repetido o identidad fuera de fixture NO es autenticación productiva. El wrapper exige opt-in, loopback y marca administrativa; un proxy que aparenta loopback no queda mágicamente autenticado. No se convierte un límite documentado en bypass remoto sin un caso dentro del contrato.

Nexus seguía en reporte42 al abrir: el último merge de BRAIN no estaba allí. Git y el Doc sí contienen su cierre. Ausencia en Nexus no refuta código ni tests, pero deja continuidad incompleta.

## INSTRUCCIONES PARA ASTRA AUDITOR: copiar este bloque en una instancia nueva

Sos Astra Auditor Corpus. Usá tu skill y núcleo común v2. Abraham pide auditar el incremento de BRAIN ya integrado, NO implementar nuevas funciones. Este encargo no autoriza despliegue, merge, modificar producto, intervenir VM, tocar bases vivas/credenciales, crear issues o enviar comentarios. Leé antes de ejecutar.

### 1. Recuperá y congelá el sujeto

Consultá main/PRs al arrancar. Base de este encargo: main1178057, producto30189275. Si hubo cambios posteriores, separá su delta; no atribuyas a un SHA nuevo resultados del viejo. Leé estos archivos en git:

- `docs/agents/respuestas/2026-09-18-03-guards-auditoria.md`.
- `docs/agents/respuestas/2026-09-18-04-logout-aislado.md`.
- `docs/agents/respuestas/2026-09-18-05-cadena-integrada-main.md` y sus JSON de evidencia.
- Este informe y su evidencia hermana.
- Plan `2026-09-17-01-plan-integral-corpus-titan-full.md` y enmienda `2026-09-17-03-enmienda-plan-corpus-v2.md`; no ejecutar unidades del plan como permisos.

Leé el diff PR11→main, en particular `isolated_login.py`, `isolated_session.py`, `access_policy.py`, `exact_http.py`, los tests y `clean-snapshot.yml`. No uses solamente los recibos. Inventario y método están en mudh-mobile; Corpus no es Custos.

### 2. Prioridad uno: composición real y permisos, no volver a contar79

Identificá el entrypoint realmente usado por el host y el consumidor que se invoca. Diferenciá: código en main, wrapper elegible, proceso iniciado, servicio desplegado. Demostrá en scratch el recorrido login real→sin grant403→grant explícito→lectura paginada íntegra→logout→siguiente página403. Usá dos identidades y dos sesiones de una identidad: sólo debe revocarse el bearer presentado; lo demás mantiene su política. Esperado fijo fuera del código auditado, SQL propio y conexiones cerradas. En SHA sin delta, una repetición de esta revisión sirve como ancla, no hace falta repetir todas las suites por ceremonia.

Probá ausencia de marca, restauración, retirada de documento/grant entre páginas y reapertura del store. No exijas revocar texto ya entregado ni una lectura autorizada antes del COMMIT. Separá prueba secuencial de garantía concurrente.

### 3. Prioridad dos: bordes aún no medidos que pueden mentir sobre logout

En store sintético exclusivamente, retené un lock con otra conexión cerrable, pedí logout y verificá respuesta de error, ausencia de falso logged_out y estado real de la sesión; liberá lock y verificá logout exitoso y siguiente lectura denegada. Usá timeout y finally. Si el cliente recibe503, no inventes que la sesión necesariamente fue revocada: leé la fila.

Ensayá persistencia con un PROCESO nuevo que reabra el mismo store, no sólo un objeto nuevo. Distinguilo de crash recovery o reinicio de host, que no vas a certificar. Si encontrás una carrera, registrá orden de transacciones y precondiciones; no atribuyas riesgo remoto a un operador que controla el store por contrato.

Reloj: igualdad/fracciones, password erróneo y throttle seguido de rollback, tabla login_clock ausente y retorno a tiempo válido. Este informe ya comprobó throttle1010.8→recreación→1010.7; reusalo como antecedente a refutar, no lo vendas como hallazgo nuevo. El high-water cubre LOGIN; no asumas garantía global de las lecturas. Un store antiguo sin tabla no se migra solo: registrá qué operación falla y qué sigue permitido.

### 4. Prioridad tres: integración y continuidad antes de proponer otra función

Cotejá árbol final con integración simulada, no sólo cabezas de ramas. Validá PR1 abierto/excluido y el conflicto del adaptador nacional si lo necesitás para proponer el siguiente lote; NO lo resuelvas ni audites automáticamente sus31archivos ajenos al delta. Si un listado contradice merged_at, consultá el PR específico y git; no firmes con el booleano contradictorio.

Marcá qué falta para un consumidor usable: composición/provisionamiento explícitos, vista aislada si se decide, recuperación/restore, revisión jurídica y permiso humano de piloto. No conviertas esta lista en orden de implementación ni certifiques producto por79tests. Priorizá el menor bloqueo demostrado hacia el recorrido usable, no generar más documentos o bancos sobre el mismo caso ya resuelto.

### 5. Tu instrumento también se audita

Baseline limpio en la propiedad; mutante local debe fallar ESA aserción y no un import. Mutantes mínimos: no revocar, revocar otras sesiones, ignorar reloj/marca. No sumar defectos derivados como hallazgos distintos. Cierre SQLite explícito y estados de WAL comparables; hash de archivo principal no demuestra por sí solo igualdad lógica durante checkpoint.

No repetir el error OPUS: `documentos.sha256` puede referirse al PDF/origen, no al texto. Antes de alegar pérdida identificá productor, bytes hasheados, ledger y lector. Diferenciá concatenador main de fusionar84358cc. Tres versiones en una copia no son porcentaje de producto ni prueba jurídica.

### 6. Parada y entrega

Terminá al resolver las tres prioridades dentro del delta: cada afirmación CONFIRMADO/REFUTADO/NO MEDIDO; cada anomalía producto/instrumento/entorno. Si un borde no se ejecuta, dejalo NO MEDIDO, sin ampliar a auditoría universal. Guardá fuentes, inputs, comandos y salidas completas desde captura, sin primeras/últimas líneas; excluí secretos expresamente. No hay obligación de inventar hallazgos.

Informe y evidencia documental en git autorizado, readback byte a byte y pertenencia a main, Doc público en Space y cierre Nexus. Si hay bloqueo de credencial, pedir sólo esa decisión y declarar entrega incompleta; git local sin credenciales NO significa que el conector GitHub falle. Usá la conexión autorizada en esa nueva conversación según sus reglas, no extraigas tokens del taller. No publiques el trabajo pendiente de otros auditores en sus nombres.

Chat final en criollo: qué cambió realmente, qué reparo demostraste y qué falta para uso real. Links a archivo e informe público. Sin puntaje que compense gates fallidos; no ranking de modelos ni A/B con/sin skill.

## Evidencia y control final de ESTA revisión

Evidencia: `docs/auditorias/2026-09-18-06-brain-main-encargo-astra/evidencia.json`, commit `67d308433200ebf0a7e9d818e2cae5f07defc3b9`. xz+base64 reversible,55.496bytes originales,SHA256 `80c6baa75278c0d5ea027ef1d88806911033f7605ffe54a79da066d47f9ba8f6`. Recuperada desde git y comparada con la captura local: byte_identical true. Incluye instrumentos completos ejecutados, resultados propios y del autor, falsadores, fuente-hashes, entorno y contraste de árboles. La regeneración merge-tree posterior está transcripta completa más arriba.

Gate I: pasa para propiedades ejercitadas con positivos y mutantes dirigidos; concurrencia/crash/host NO MEDIDO. Gate II: afirmaciones y límites separados; no se inventa defecto. Gate III: evidencia remota ya verificada; informe, Doc público y registro propio se completan en el cierre de este turno, sin afirmar retrospectivamente publicaciones ajenas pendientes.

Roles: revisión, verificación y control final del mismo operador, no tres revisores independientes. No producto ni bases vivas modificados. Los scripts sólo alteran copias temporales; los listeners propios terminaron. Esta revisión no completa por arte de magia la publicación pendiente del informe anterior de ambos auditores y sus4.700.035bytes.
