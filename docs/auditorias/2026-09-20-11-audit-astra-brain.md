# Contraauditoría de Astra Auditor y Brain

20-sep-2026, ART. Pedido: «Audita la auditoria de astra auditor y el trabajo de brain».

## Veredicto

**Astra encontró un hueco real y el banco actual ya lo cubre.** Reproduje el falso verde del banco viejo y los rojos dirigidos del nuevo. Brain recomputó correctamente la evidencia histórica, pero su informe06 llama `revoked` al campo de confirmación que realmente se llama `logged_out`. La descripción viva de PR20 volvió a quedar atrasada tras incorporar los tests.

Sin defecto nuevo de producto demostrado en los casos ejecutados. No es aprobación de merge: **la revisión de logout por otro autor sigue pendiente**. El pase10 está preparado, no enviado ni asignado. Publicarlo no cerró G2. No corresponde repetir BFCache ni mantener G1 como deuda abierta.

## Sujeto y autoría

Alcance: revisión Brain06; auditorías Astra07 (HTTP/paginación) y08 (huecos de merge); implementación09 de tests y pase10. Antecedentes03-05 solo se recomputan. No auditoría exhaustiva de todo Corpus.

Main inicial `fea377f66b806543b91bf76bd2db84a6ccfd6d81`. PR20 actual `ca503377760a8dcd7965689a2853420785a83d94`, base PR19 `31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05`. HTML idéntico a `cc2ca30760c486cad3154c619a20f94cf75cc691`; delta desde ese arreglo: exactamente56 líneas añadidas a `tests/browser_discovery.cjs`.

BRAIN escribió la implementación original y revisión06; Astra Auditor publicó07/08; implementación09 y pase10 se registraron como Astra. No atribuyo estos últimos a Brain. Esta instancia escribió el arreglo histórico de logout: **no puede ser su revisor externo cambiándose el nombre**.

Ocho reproducciones nuevas en archives propios usando instrumentos y mutantes publicados por los autores, más un comparador nuevo. Verifican reproducibilidad y poder de detección, no una nueva selección externa de casos de logout. W-01 no se resuelve solo cambiando de operador.

## 1. Astra07: integridad por HTTP real, CONFIRMADO

Reejecuté `probe-v2.py`, recuperado y leído, contra el head actual. Positivo33 comprobaciones, cero fallos, exit0. El mutante que deja continuar después de una excepción del lector produjo33 comprobaciones, tres fallos, exit1.

Rojos exactos: `authorized_corruption_no_partial`, `offpage_authorized_corruption_no_partial`, `empty_page_still_validates_authorized_content`. Los otros30 pasan. El comparador recalcula actual/expected mediante JSON tipado: ninguna inconsistencia de passed. No rojo por arranque, import ni timeout.

Se sostienen integridad aun fuera de página, aislamiento de la corrupción de otra colección y offset vivo. Expirar una sesión antes del request no prueba una carrera durante logout. Revocación simultánea dentro del mismo request: NO MEDIDO.

[Informe07](https://github.com/gatehot59-star/corpus-legal-tarija/blob/fea377f66b806543b91bf76bd2db84a6ccfd6d81/docs/auditorias/2026-09-20-07-search-pagination.md)

## 2. Astra08: hueco histórico CONFIRMADO; mantenerlo abierto hoy, REFUTADO

Copié a un archive propio únicamente el HTML mutante publicado, inspeccionando el diff: cambia la asignación UID/version para elegir siempre el primer resultado. El banco histórico pasó59/59 sobre esa UI rota, exit0. Es reproducción del falso verde, no lectura del recibo.

El oráculo08 pasó31/31 en producto correcto. En el mutante acumuló10 fallos de31: versión, texto, locator, filename y procedencia para a2 y b2. Los otros21 pasan.

El banco actual pasó88/88. Contra el mutante general se detuvo en `selection_fixture-a2_pins_clicked_version`, con70 aserciones alcanzadas. Contra el mutante solo de Ben llegó a80 y falló en `selection_fixture-b2_pins_clicked_version`. No ejecutó88 comprobaciones en las ramas rojas. Las29 nuevas del positivo conservan actual/expected y fueron recomputadas; las59 heredadas solo registran booleanos, no se finge recomputación independiente de valores ausentes.

**G1 está atendido en el alcance demostrado.** Conservar el diagnóstico08 con su fecha, sin arrastrar su recomendación de pausa por G1 como deuda vigente.

[Auditoría08](https://github.com/gatehot59-star/corpus-legal-tarija/blob/fea377f66b806543b91bf76bd2db84a6ccfd6d81/docs/auditorias/2026-09-20-08-merge-gaps.md) · [Implementación09](https://github.com/gatehot59-star/corpus-legal-tarija/blob/fea377f66b806543b91bf76bd2db84a6ccfd6d81/docs/agents/respuestas/2026-09-20-09-selection-ci.md)

## 3. CI y exactitud del cambio09, CONFIRMADO

Banco remoto actual16114bytes, SHA256 `0c1f34694b9e8de2a28985b3078222292406c30027ae50200aaaaa6f47d43984`, igual al ejecutado y a evidencia09. Su primer error de publicación no persiste.

Workflow leído: incluye el path del banco y ejecuta `timeout 120s node tests/browser_discovery.cjs` bajo `set -euo pipefail`. Los asserts propagan exit1. API nueva del job106091355198/run35515778571: head exacto ca503377, completed/success, diez pasos completed/success incluido Chromium. No recuperé stdout Actions:88 es conteo local.

Merge virtual main+head: exit0, árbol `d82b32720ffae9bc35a00ad58baff39b216b35cb`; diff contra head en sistema/tests/.github vacío. Equivalencia de producto en este snapshot, no merge ejecutado ni permiso de saltar PR18/19.

[CI exacto](https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35515778571/job/106091355198)

## 4. Brain06: recomputación válida, campo de contrato incorrecto

Paquete32816bytes, SHA256 `a27d028cb3101c252c2ec702efb060a867ff18cd54ecb803d3ec199147b6ed28`, recuperado junto a inputs02-05. Su comando se reejecutó cambiando solo directorio de entrada: exit0, stdout idéntico. Se sostienen163/0 de03,110/0 de04 y precondición BFCache no alcanzada de05. Recomposición de observaciones históricas, no nuevas corridas de esos escenarios.

**REFUTADO documental, gravedad baja:** «Confirmar revoked===true borra ambos handles.» El cliente real usa `if (r.logged_out !== true) throw new Error("Respuesta inválida");`; no lee `r.revoked`. Body del PR y pase10 sí nombran `logged_out` correctamente. Corregir la frase del informe06, no el producto: evita enviar a un revisor a probar el campo equivocado. E-01: describir el contrato concreto que se midió.

La imprecisión no invalida los experimentos ni prueba un logout defectuoso.

[Brain06, sección2](https://github.com/gatehot59-star/corpus-legal-tarija/blob/fea377f66b806543b91bf76bd2db84a6ccfd6d81/docs/auditorias/2026-09-20-06-revision-sol-astra.md) · [Cliente](https://github.com/gatehot59-star/corpus-legal-tarija/blob/ca503377760a8dcd7965689a2853420785a83d94/sistema/web/discovery_spike.html)

## 5. Body del PR: REFUTADO como estado vivo

El body dice `Head actual: cc2ca307...` y presenta59 como banco ampliado; API actual ca503377 y banco88. Su corrección anterior fue válida para su momento: quedó vieja después de09. No acusar falsedad retrospectiva a Brain por un cambio posterior.

Deuda documental de prioridad baja, no bug ni bloqueo técnico nuevo. Actualizar juntos head, banco y enlace CI, preservando antecedentes. No edité el PR bajo este pedido.

[PR20](https://github.com/gatehot59-star/corpus-legal-tarija/pull/20)

## 6. G2 y pase10: NO CERRADO

API reviews de PR20 `[]`. Pase10 declara expresamente que no envía ni asigna: lo preparado corresponde a esa afirmación. No hay nombre de revisor comprometido en el pase. No convertirlo en revisión ya hecha.

**Qué no se midió que importaba:** nueva selección de casos del arreglo de logout por alguien que no lo escribió. Esta reproducción no la sustituye. Ausencia de conversaciones privadas y reglas de branch protection: NO MEDIDO, no inferidas de reviews[]. No envié mensajes ni asignaciones.

[Pase10](https://github.com/gatehot59-star/corpus-legal-tarija/blob/fea377f66b806543b91bf76bd2db84a6ccfd6d81/docs/agents/respuestas/2026-09-20-10-logout-review-handoff.md)

## Qué cacé sin encontrar defecto nuevo

Conteos inflados, falsadores que fallasen por otra causa, banco verde incapaz de detectar el cambio, fuente remota distinta, CI de otro head, confusión main/rama, integridad fuera de página y falsa aprobación BFCache. Los resultados acotados se sostienen; los dos rojos documentales están separados. Ni score, ni hash ni ausencia de reviews autorizan merge.

Prioridad: G1 tiene regresión versionada; G2 tiene paquete pero no revisión. No otro ciclo idéntico BFCache. BFCache de PR20 restaurado, producción, piloto, validez jurídica, concurrencia y otros navegadores siguen NO MEDIDOS en este turno.

## Evidencia, entorno y límites

Ocho corridas nuevas CLI/HTTP/Chromium en brain-env: Python3.12.14, Node24.18.0, Playwright1.63.0, Chromium153.0.8010.12. CPU2, disco libre124586663936bytes medidos. Inventario de máquinas y método de permisos leídos como contexto histórico, no reetiquetados como medición actual de Actions/Kaggle. No se necesitó ni declaró inaccesible otra máquina.

Evidencias07/08/09 decodificadas estrictamente:112353/69062/87207bytes y hashes iguales a informes. Mutantes recuperados de scratch previo, copiados a archives propios después de cotejar diferencias. No asumir que scratch persistente es nuevo. Ninguna edición de producto remoto.

Dos ensayos HTTP y dos de selección cerraron servidor; sus cuatro puertos rechazaron conexión111. Barrido acotado sin procesos propios. Bancos versionados conservan limpieza heredada; no agregué telemetría de cada puerto ni certifico ausencia global de Chromium.

Errores propios: buscó inicialmente data en wrapper06 que usa payload; el comparador inicial esperaba stdout de mutantes cuyo JSON está en stderr. Correcciones solo de lectura/comparador; ocho corridas sin alterar. Se conserva comparador inicial y su salida fallida; del primer KeyError hay descripción, no reconstrucción terminal completa. Publicación por git local falló en dry-run128 por falta de credencial de transporte; se recuperó con el conector GitHub autorizado, sin extraer tokens.

**Evidencia publicada**: [2026-09-20-11-audit-astra-brain/evidence.xz.b64](2026-09-20-11-audit-astra-brain/evidence.xz.b64), base64 estricto+xz, JSON226207bytes, SHA256 `a30631c7dacbde7490daaef167732d131980bd589fe47d8dee12d8177464d189`. Todas las salidas de las ocho corridas nuevas, cuatro result.json completos HTTP/selección/descargas, runner, ambas versiones del comparador y su error, diferencias de mutantes, manifiesto y verificación seleccionada de PR/job.

Fuentes reutilizadas probe-v2.py/selection.cjs no duplicadas: viven en evidencias07/08 fijadas por manifiesto y SHA. Stdout recomputado06 idéntico al ya publicado06, no duplicado; resultado de igualdad sí incluido. Metadatos API seleccionados, no objetos completos ni stdout Actions. Sin tokens, SQLite, video, trace ni archivo de toda la conversación. Paquete local ampliado267138bytes SHA256 `1c5e1f4731002469cc880a32a8c7e86da8f9da40ec0a8375cc5d5dbe585c29c4`, no presentado como publicado.

Reproducción: decodificar y verificar longitud/hash; files conserva comandos/stdout/stderr. Recuperar instrumentos referidos desde evidencia07/08; recrear archives ca503377 y cc2ca307 y outputs propios según runner.py; no ejecutar paths persistentes sin verificar. Los diffs fijan mutantes y entorno Playwright está en las corridas.

## Gates y método

Gate I: reproducibilidad CONFIRMADA acotada, positivos/falsadores dirigidos, falso verde viejo y rojos actuales. Gate II: cronología, límites y autoría separados. Gate III: chat condicionado a lectura remota de main, comparación de evidencia, Doc público leído y Nexus.

QA autoevaluada del informe: completitud14/15, razonamiento9/10, documentación9/10, aporte4/5, proceso5/5 =41/45,91,11%. N/A55 de nueva implementación. Descuentos por alcance no exhaustivo, selección de casos reutilizada y captura parcial del primer error. No score del producto ni cierre de G2.

--- METODO TITAN ---
Accion delicada: NO; auditoría/documentación, sin merge/despliegue ni cambio de confianza.
Rol: contraauditor de afirmaciones; operador de reproducciones, no revisor externo de su arreglo.
Maquina: brain-env; GitHub API para head/CI/reviews.
Rubrica:41/45,91,11% del informe;55 N/A de producto.
Review externo: G2 pendiente, no sustituido.
Instrumento: ocho corridas, comparador tipado, falsadores y git/API.
Artefactos: este informe, evidencia reversible, Doc público y Nexus; lectura remota antes del chat.
