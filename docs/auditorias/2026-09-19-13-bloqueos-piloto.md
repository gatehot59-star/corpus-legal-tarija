# Corpus: qué bloquea un piloto real

19-sep-2026 ART. Diagnóstico de dependencias y código, no ejecución de piloto ni nueva auditoría experimental. Main observado: `7b3d3ef7d7e238e4131eff2aeb04943cc20e6cf9`; PR18: `2231ca8edbe4c0b6eba88156d5abd087bbf9e51f`; PR19: `31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05`. Ambos PR siguen abiertos, sin merge.

## Veredicto

**El bloqueo no es conseguir más tests verdes: falta pasar del fixture a una colección real autorizada y conectar un servicio completo para personas reales.** El código actual rechaza deliberadamente documentos y cuentas reales. Aun integrando PR18/19 quedarían sin cerrar búsqueda protegida, feedback privado, recuperación operativa y aceptación del entorno que se abrirá.

Hay dos frentes que pueden avanzar en paralelo: definir quién revisa y qué documentos/tareas se autorizan; construir y verificar la integración técnica contra ese contrato, manteniendo datos sintéticos hasta la aprobación. No está justificado esperar a reparar toda la deuda de fixtures, comprar infraestructura o terminar membresías.

## 1. Primer corte: muestra autorizada y responsables

La [enmienda vigente, secciones 2, 3 y 7](https://github.com/gatehot59-star/corpus-legal-tarija/blob/7b3d3ef7d7e238e4131eff2aeb04943cc20e6cf9/docs/agents/respuestas/2026-09-17-03-enmienda-plan-corpus-v2.md) exige M01: revisión jurídica/privacidad con lista exacta de documentos y tareas permitidos, y M02: snapshot aislado de esa muestra con procedencia y retirada. Dice literalmente: «Las actas deben existir realmente, no inferirse de esta enmienda».

**NO ACREDITADO:** revisor jurídico boliviano y docente/editor confirmados, disponibilidad, acta aplicable de alcance/datos/licencias y muestra aceptada. En Nexus, las consultas de decisiones y estado con Corpus/piloto devolvieron cero filas; los mensajes pertinentes no aportaron un acuerdo de Corpus. Las búsquedas de Docs/chat localizaron planes y recibos técnicos, no un acta que cierre estos gates. Es ausencia de evidencia encontrada, no prueba de que nadie haya hablado con una universidad.

**Responsabilidad propuesta, no asignación:** Abraham decide alcance y recursos; J valida contenido/privacidad/licencias; D define tareas y participantes. Ser auditor de software no convierte a Brain, SOL o Astra en el revisor jurídico humano del plan.

**Qué cierra este corte:** nombres y disponibilidad confirmados, lista UID/versión/fuente con inclusiones y exclusiones, dictamen aplicable, política de datos, tareas de evaluación y aprobación de alcance. A03/A04/A06/A07/A08/I01/I02 y A09 corresponden a decisiones distintas; no se sustituyen por «seguí».

El [arranque autorizado](https://app.clickup.com/90171457413/docs/2kza6fw5-12557/2kza6fw5-14817) preservó expresamente esos gates: ejecutar técnica por etapas no aprobó gastos, contratación, contacto institucional ni despliegues. Las universidades identificadas como candidatas no son participantes confirmados.

## 2. Segundo corte: no existe todavía una entrada para usuarios y documentos reales

**CONFIRMADO por fuente, no un bug nuevo:** [demo_aislada.py de PR19](https://github.com/gatehot59-star/corpus-legal-tarija/blob/31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05/sistema/api/demo_aislada.py#L125-L148) valida el único fixture y las identidades fixture-ana/fixture-ben; emite `DEMO_CANDIDATE_NOT_SYNTHETIC` ante otro candidato. Sus grants usan `SYNTHETIC-NOT-APPROVAL`; escucha en loopback y declara que no existe modo de producción.

El [contrato de isolated_login.py](https://github.com/gatehot59-star/corpus-legal-tarija/blob/7b3d3ef7d7e238e4131eff2aeb04943cc20e6cf9/sistema/api/isolated_login.py#L1-L5) excluye alta real, reset, emisión de permisos y migración. PR19 agrega una referencia local, no cambia este contrato.

**Qué falta:** una frontera adoptada para identidades reales y permisos gratuitos por grupo/colección/fechas/revocación, aprovisionamiento y recuperación de cuentas, sin abrir rutas laterales. El plan propone Django; la demo casera de ensayo no acredita haber adoptado esa arquitectura. Mantener Django o cambiarlo requiere una decisión explícita, no renombrar `fixture-*`.

**Aceptación:** participante real autorizado accede; cuenta sin grant, grupo equivocado, permiso vencido/revocado y documento retirado no acceden. Todo sobre el snapshot aprobado y la revisión que se pretende servir. D09 es gratuito: pagar no forma parte de esta puerta.

## 3. Tercer corte: el recorrido buscar → verificar → guardar → reportar sigue partido

**CONFIRMADO:** [index.html, línea 293](https://github.com/gatehot59-star/corpus-legal-tarija/blob/7b3d3ef7d7e238e4131eff2aeb04943cc20e6cf9/sistema/web/index.html#L293) llama `/api/v1/buscar`. El [handler legacy](https://github.com/gatehot59-star/corpus-legal-tarija/blob/7b3d3ef7d7e238e4131eff2aeb04943cc20e6cf9/sistema/api/servidor.py#L318-L371) entrega búsqueda/documentos sin pasar por la frontera v2; `/api/v1/revision` solo lee una cola por GET, no recibe reportes.

**Impacto:** poner el buscador viejo delante del login nuevo no protege resultados ni snippets. Esto describe el código del repo: no demuestra exposición remota actual de la VM. No se confundieron sus rutas con las de la API desplegada histórica.

La [página de PR19](https://github.com/gatehot59-star/corpus-legal-tarija/blob/31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05/sistema/web/auth_spike.html) sí une lectura de un documento fijo y descarga de referencia. No hace búsqueda, colección privada, compartir revocable ni envío de errores. El plan todavía exige D04/D05/D07 y flujo observable D06/M04: la referencia local cubre parte de guardar, no todos esos contratos.

**Qué cierra este corte:** búsqueda autorizada desde la consulta hasta cada resultado/página, procedencia consistente, guardado/compartición con aislamiento y revocación según alcance acordado, reporte privado con recepción y trazabilidad. Probar el recorrido real, no solo sus módulos.

## 4. Cuarto corte: seguridad de staging y recuperación que permita volver a operar

**CONFIRMADO:** el [restore disponible](https://github.com/gatehot59-star/corpus-legal-tarija/blob/7b3d3ef7d7e238e4131eff2aeb04943cc20e6cf9/sistema/RECUPERACION-DEMO.md#L40-L92) devuelve `serve_authorized: false`, vacía sesiones/deshabilita colecciones y no tiene reapertura. Es una protección valiosa frente a backups viejos, no recuperación operativa terminada.

**NO MEDIDO para piloto:** TLS/proxy y cierre lateral del despliegue elegido, ciclo de cuentas/reset, protección CSRF conforme a la arquitectura adoptada, logs/privacidad, carga concurrente, accesibilidad manual y restauración consistente con reconciliación actual de permisos/retiradas. M03/E03-E07/F02-F05 exigen probarlo en staging y sobre la versión candidata. Cookies no son un checkbox si se adopta otra arquitectura; cualquier cambio del contrato del plan debe explicitarse.

**Aceptación:** recuperar el conjunto real de datos operativos sin resucitar accesos retirados, recuperar servicio con autorización y registrar tiempos/pérdidas tolerables; probar identidades y rutas desde el ingreso público previsto. Una copia en cuarentena y 37 controles Chromium no prueban eso.

No se hizo nueva conexión a la VM en este diagnóstico. El cotejo de [A01/A02 del 17-sep](https://app.clickup.com/90171457413/docs/2kza6fw5-12557/2kza6fw5-14817) identificó un servidor desplegado distinto de main y preservó su bind loopback. Es antecedente, no medición actual. El corte técnico exige reconciliar esa diferencia antes de desplegar, no sustituir main a ciegas.

## 5. Último corte: aceptación humana y apertura explícita

M04 observa tareas equivalentes en una demo cerrada; **no es el piloto institucional**. I08 calibra esfuerzo real e I09 decide el siguiente lote. El camino vigente a F08 exige colección aceptada C08, revisión final E08, soporte y acuerdo F07, capacidad/smoke F05 y D09. F08 es la decisión go/no-go y despliegue reversible, no una consecuencia automática del CI.

**NO ACREDITADO:** lista de participantes confirmados, consentimiento, responsables de soporte, acta F07/F08 y revisión del release que se abriría. El [plan base, unidades D-F e I](https://github.com/gatehot59-star/corpus-legal-tarija/blob/7b3d3ef7d7e238e4131eff2aeb04943cc20e6cf9/docs/agents/respuestas/2026-09-17-01-plan-integral-corpus-titan-full.md#L273-L320) define esas aceptaciones; la enmienda reemplaza sus precedencias.

El alcance propuesto es 84 unidades editoriales, no todo el corpus. El plan admite una enmienda de alcance aprobada: un piloto más estrecho puede reducir curación y funciones, **no borrar privacidad, permisos, recuperación ni consentimiento**. Esa reducción no quedó autorizada por este pedido de diagnóstico.

## Lo que NO pondría en el camino crítico sin una dependencia demostrada

- **169 omisiones de cierre SQLite en fixtures y PR17:** deuda real de tests, no requisito demostrado del piloto. Si afectan reproducibilidad, reparar el caso que bloquea la aceptación. La [corrección de prioridad](https://github.com/gatehot59-star/corpus-legal-tarija/blob/7b3d3ef7d7e238e4131eff2aeb04943cc20e6cf9/docs/agents/respuestas/2026-09-19-09-smallest-useful-feature.md) ya lo reconocía.
- **Membresía/pagos H02-H04:** la enmienda los sitúa después de G08; no son prerrequisito del piloto gratuito. Sí hacen falta recursos y límites de gasto del piloto. I10 regula oferta/comercialización posterior, no excusa para abrir sin presupuesto.
- **Más PDFs, todas las bibliotecas o los 6079 documentos:** se acepta la colección ofrecida, no un volumen arbitrario. Fuente/derechos/vigencia pendientes impiden ofrecer ese documento, no obligan a completar Bolivia entera.
- **Comprar GPU/VPS, cambiar todo el stack o deuda Android/Custos:** no se identificó una falta de cómputo como causa del bloqueo. La capacidad del entorno final se mide en su gate, no se presume ilimitada.
- **Subir QA de 88,89 a 90 o sumar checks:** el score de PR19 es autoevaluación, no gate jurídico u operativo. La revisión de código independiente y permiso de merge siguen pendientes para integrar esa pieza, pero no son la única distancia al piloto.

## Orden recomendado, no ejecución autorizada

1. Acordar una ficha de piloto: tarea jurídica, colección exacta, quién revisa/edita, participantes objetivo, datos permitidos y tope de recursos. Primera decisión humana necesaria; no hace falta inventar una fecha de lanzamiento.
2. Cerrar M01 y decisiones aplicables; preparar M02. En paralelo, revisar PR18/19 y diseñar integración de cuentas/búsqueda/feedback con contratos sintéticos. No aflojar el lanzador de pruebas para meter usuarios reales.
3. Verificar el recorrido y M03 en staging aprobado; observar M04, calibrar I08 y decidir alcance/lote I09. No presentar horas históricas del plan como horas restantes.
4. Completar aceptación de colección y release, recuperación/capacidad/soporte y acuerdos F07; recién entonces decisión F08 y apertura reversible.

**El próximo avance útil es fijar y aceptar una muestra real con sus responsables, mientras se cierra la integración. Otra ronda genérica de mantenimiento no sustituye esa decisión.** Las 323 horas históricas hasta F08 son una hipótesis de planificación sin recalibrar; no un saldo ni una fecha.

## Método, evidencia y límites

Lectura directa de refs/archivos por Git y PRs por GitHub, plan/enmienda y Docs A01/A02; Nexus reportes, decisiones, estado y mensajes; dos búsquedas ClickUp de piloto/aprobaciones/responsables. El índice devolvió muestras con más resultados: no se afirma búsqueda exhaustiva de toda comunicación ni ausencia universal de acuerdos. No se contactó a nadie.

Refs remotas medidas a 20-sep-2026 00:26:45 UTC: main `7b3d3ef`, PR18 `2231ca8`, PR19 `31dff1ed`. Manifiesto de diez fuentes conservado en el taller. SHA-256 de enmienda: `92f3bbc2d6b15a8896e43dffeef526813aff1ddf594d85f898562ee550a08d90`; demo de PR19: `b77a594a9779f526c87bed0dc29c075916e1ff5c62fe512c9b6b98bc3518ee49`; servidor main: `db7c1192b3cf4867aa7d0a31f2a8f56f1980ad16ccfda93c60c4234b941e0802`.

Fuentes completas recuperables en los commits citados; las líneas leídas son evidencia de contratos/rutas, no un ensayo de explotación. Los resultados anteriores de tests/CI no se reejecutaron ni se convirtieron en aval de piloto. Algunos resultados largos se truncaron al visualizar: los contratos decisivos de demo/restore se recuperaron en rangos explícitos antes de concluir.

El grafo tampoco equivale a un ejecutor de aprobaciones: [la auditoría de sus bypass](https://app.clickup.com/90171457413/docs/2kza6fw5-12537/2kza6fw5-14797) mostró que precedencia no valida alcance/saldo del acta. Este diagnóstico respeta la prosa de permisos, no firma autorizaciones por alcanzabilidad de una fila.

**Qué no se midió que importaba:** decisiones humanas fuera de las fuentes accesibles, estado actual de VM/TLS, disponibilidad de revisores/participantes, vigencia jurídica de la muestra, carga, recuperación operativa y utilidad observada. Ninguno se rellena con una inferencia.

Gate I: N/A a baseline/mutantes de producto porque no hay instrumento experimental nuevo; sujeto/ref/rutas identificados. Gate II: conclusiones separadas entre confirmado y no acreditado, con condiciones de cierre y sin atribuir defectos nuevos. Gate III: cierre documental, no release; publicación y lectura remota del informe, Doc público y Nexus se verifican antes del chat. Sin score de producto.

TITAN: revisión acotada de dependencias y fuentes; sin producto, merge, despliegue, cuentas, mensajes ni issues nuevos. La documentación no modifica las aprobaciones del plan.
