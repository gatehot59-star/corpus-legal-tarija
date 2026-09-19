# Revisión de Astra, PR16 integrado y siguientes instrucciones para Brain

19-sep-2026 ART. Autorización confirm_merge_pr16_after_astra, comentario80170047115753: integrar únicamente PR16 cabeza67d0251, verificar main y publicar revisión e instrucciones. No despliegue, PR1, datos reales ni reapertura.

## Resultado

Astra cumplió el encargo de PR14 dentro del contrato de demo local. Se recuperó su evidencia publicada de308634bytes y se verificó SHA2564764df2c1a270414709f7d07628271ce93dc4c5f36df7bb0eb0f117bc401f521; se leyó el banco corregido antes de ejecutarlo. Sus expectativas de texto son constantes externas al lector, emplea CLI y sockets reales, SQL directo y procesos distintos. El error original de nombre http sombreado está preservado y correctamente atribuido al instrumento.

Reejecución propia del mismo instrumento, no nuevo oráculo:142aserciones sin fallos. Repetición serial con retorno capturado:142/0,exit0,26.318s. Tres falsadores reproducidos con el mismo banco: opt-in10aserciones/4fallos pertinentes, revocación38/3 y Host/Origin14/3; todos exit1 por las aserciones objetivo. No se suman repeticiones como pruebas independientes ni se llama revisión externa a las funciones del mismo operador.

Una repetición intermedia concurrente con nuestra regresión falló126aserciones/3fallos: el banco mató init después de5s, luego intentó servir ese fixture incompleto. Resultado inicial init=-15/timeout, seguido de server_exit2 y error de lectura JSON. No es evidencia de un bypass. La misma prueba, sin modificar fuente ni timeout y ya sin otra suite propia paralela, pasó142/0. Contención del scheduler es hipótesis compatible, NO causalidad demostrada. La corrida adversa permanece íntegra; no se certifica latencia de inicialización bajo carga. Brain debe evitar lanzar sus suites pesadas a la vez y separar setup del veredicto del producto.

El timeout de2s es de inactividad, no plazo total: el banco conserva observaciones de cliente lento e incompletos. No convertirlo en garantía DoS/productiva ni en defecto nuevo sin cambiar el contrato. Los tracebacks locales de inactividad se preservan; no se demostró exposición al cliente o caída. La deuda de cierre explícito SQLite de fixtures heredados no se convirtió en fuga productiva.

## Merge ejecutado y comprobación posterior

[PR16](https://github.com/gatehot59-star/corpus-legal-tarija/pull/16) integrado a las11:33:51ART como2e06380900eef97ec7290e5cd25e38d1ef96e17e. Consulta posterior closed/merged:true, cabeza autorizada67d0251ac2d768065cf75b976cd5a72580d34bdd. Cuatro archivos,495líneas agregadas: demo_restore.py, test_demo_restore.py, RECUPERACION-DEMO.md y workflow.

Preflight git merge-tree sobre maina188771b produjo árbol9bff74c7df3790ae6e4b2b574a7eeb58112269f6 sin conflictos. Tres bloques run exactos del workflow ejecutados allí:79regresión+18demo+14restore=111casos, todos exit0; compilación incluida. Duraciones72.755s,32.903s y28.484s. Se leyó el restaurador y su contrato; auditoría AstraPR16 previa es antecedente, no fingimos reejecutar sus89aserciones en esta revisión. Su banco del autor sí se ejecutó en la combinación.

El árbol del merge remoto coincide exactamente con el probado. Extraído ese commit de main, el banco de Astra volvió a completar142aserciones sin fallos, con procesos reales, lectura y logout persistente. No se repitieron innecesariamente las111porque los árboles son idénticos. Esa corrida posterior conserva result.json/stdout/stderr; no se guardó aparte el exit del padre y no se inventa. La repetición serial anterior sí registra exit0. Las tres ejecuciones142/0 son del mismo banco.

CI histórico consultado: check105821331184 completed/success en PR16, job https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35414843978/job/105821331184 . No se lanzó ni se afirma CI nuevo sobre main: el workflow no tiene push. No se recuperó log remoto completo, el conteo111 es local.

[PR1](https://github.com/gatehot59-star/corpus-legal-tarija/pull/1) reconsultado: abierto, cabeza2360f27d43fdc9a1e2a74a3f6465698918df2ad1 sin cambiar. Tiene32archivos y39commits; no se integra por su título antiguo ni por arrastre. PR14/15 ya estaban integrados. No se borraron ramas.

## Instrucciones siguientes para Brain, listas para otra conversación

Partí del main integrado2e063809, recuperá el main vigente y este informe. Leé las auditorías Astra03(PR14) y01(PR16), sus cierres, el plan/enmienda v2 y Nexus. Estas instrucciones no ejecutan cambios ni conceden otro merge/despliegue. Antes de editar, comprobar PRs superpuestos. Cada unidad técnica acotada a4h; si no cabe, separar y reestimar, no ampliar silenciosamente.

### Unidad1: corregir deuda del instrumento, sin reescribir producto

En una rama titan/ propia, identificar los callers que abren SQLite sin cierre explícito en fixtures de tests/test_clean_snapshot_sol.py, tests/test_exact_http.py, tests/test_access_policy.py, tests/test_login_guards.py y tests/test_isolated_session.py, incluyendo el fixture heredado de tests/test_isolated_login.py si el stack apunta allí. No modificar módulos productivos para que el contador pase. Preservar semántica de commit/rollback con closing/finally y cleanup incluso cuando falle una aserción; with sqlite3.connect no cierra.

Antes de cambiar, ejecutar el observador de Astra sobre positivo cerrado y negativo deliberadamente abierto. Repetir cada suite afectada con argv/callsite y asignar origen real a cada apertura, no asumir que todas pertenecen al fixture. Aceptación:111casos funcionales conservados, compilación y mismo contador sin conexiones propias pendientes en las suites corregidas; el negativo deliberado sigue detectado. No ocultar warnings, forzar GC como sustituto del cierre ni descontar conexiones sin explicación. Incorporar captura de retorno, stdout/stderr y cleanup; serializar suites pesadas y separar un timeout de preparación de fallo productivo. No subir el timeout sin medición que lo justifique.

Cinco suites no implican cinco bugs nuevos del producto. No usar los contadores históricos2/17/63/69/35 como resultado de una corrida futura. Si requiere más de4h, cerrar primero el fixture exact_http con su reproducción y dejar el resto explícito, sin proclamar deuda completa cerrada. Abrir PR separado para revisión; NO merge automático con esta firma.

### Unidad2: determinar el mínimo faltante para un recorrido útil, sin otra arquitectura nueva

Objetivo: buscar -> verificar fuente/versión -> guardar referencia -> reportar un error, dentro de una demo sintética y aislada. Antes de implementar, leer completos sistema/web/index.html, sistema/api/servidor.py, README y los adaptadores de sesión/lectura. Hay interfaz y búsqueda históricas /api/v1/buscar, documento, alcance, catálogos y revisión; nuestra inspección para planificar fue sólo un extracto, NO auditoría funcional completa. La demo nueva sirve v2 y no hay evidencia aquí de integración de aquella web con permisos v2. No conectar la UI v1 a datos reales ni reutilizar su lector sin verificar autorización y texto exacto.

Entregar primero una matriz concreta de las cuatro acciones: consumidor actual, ruta/almacenamiento, identidad/permiso exigido, procedencia y versión, prueba positiva/negativa, y falta comprobada. Guardar referencia no equivale a exportar texto; cola de revisión GET no demuestra un endpoint para enviar reportes. No afirmar que guardar/reportar existen o faltan sólo por no ver sus nombres en el extracto. Identificar la menor composición reutilizable y proponer UN incremento vertical sintético <=4h, con archivos exactos y aceptación, antes de ampliar a UI completa o nuevas dependencias.

La propuesta debe preservar versiones y retirada entre acciones, no restaurar concesiones con login, no mostrar material real como jurídicamente validado y no abrir a red externa. Si el siguiente incremento necesita datos revisados, aprobación jurídica o cambios de acceso, explicitar qué registro humano falta; no inventarlo ni sustituirlo con más tests. No marcar M04 realizado por una simulación sin usuarios ni cerrar M01/M02/M03/F05 por integrar PR16.

### No hacer ahora

No agregar reapertura automática a la cuarentena, borrar manifiestos, resetear reloj/presupuesto, refrescar grants desde un backup viejo, elevar límites de tamaño para usar datos reales, incorporar PR1 ni convertir el servidor monohilo en producción. Restauración fría en cuarentena no resuelve reconciliación vigente, backup caliente, crash, RPO/RTO, TLS ni validez jurídica. No priorizar nuevas rondas de los mismos142controles sin delta o hipótesis concreta.

Cierre de Brain: cambios y pruebas por archivo/revisión, positivos y falsadores pertinentes, datos crudos completos sin secretos, git recuperado/verificado, Doc público y Nexus. Distinguir código entregado, integrado, desplegado y piloto. La siguiente autorización de implementación/revisión se resuelve sobre alcance real y reglas de confirmación; este texto no notifica ni asigna a otro agente.

## Custodia de la revisión propia

Captura propia434828bytes, SHA25682ab223da77ba85bd39d1b94078dc16775ae9067816001e1ca84082d9882eae6. Incluye instrumento Astra reutilizado, supervisor propio, seis resultados premerge (incluida corrida adversa), comandos con salidas completas, tres bloques YAML, preflight, merge real y resultado posterior. Tokens/passwords/Authorization/digests individuales e imágenes SQLite quedan excluidos según el instrumento; no hubo datos reales.

Transporte reversible xz+base64 en TRES REVISIONES del mismo archivo docs/auditorias/2026-09-19-04-revision-astra-merge-pr16/evidence.xz.b64. HEAD contiene únicamente el último tramo; no es un archivo decodificable por sí solo. Recuperar por orden17af4cda3e98d6ed762c73fd8505cd75b02f17db,7f21aa2a4bc8978f587bcabd83c1bd133c9139b8,419aa801a440e7c380ff9e9b569e65b8fdbc75a6; longitudes7500,7500,8180ASCII. Los tres commits son ancestros de main. Reconstrucción desde fetch y comparación contra el original: BYTE-IDÉNTICA, no sólo igualdad de resumen.

```python
import subprocess,base64,lzma,hashlib,json
path='docs/auditorias/2026-09-19-04-revision-astra-merge-pr16/evidence.xz.b64'
revs=['17af4cda3e98d6ed762c73fd8505cd75b02f17db','7f21aa2a4bc8978f587bcabd83c1bd133c9139b8','419aa801a440e7c380ff9e9b569e65b8fdbc75a6']
parts=[subprocess.check_output(['git','show',s+':'+path]) for s in revs]
assert list(map(len,parts))==[7500,7500,8180]
raw=lzma.decompress(base64.b64decode(b''.join(parts),validate=True))
assert len(raw)==434828
assert hashlib.sha256(raw).hexdigest()=='82ab223da77ba85bd39d1b94078dc16775ae9067816001e1ca84082d9882eae6'
evidence=json.loads(raw)
```

No se reejecutó el observador de cierre SQLite; se comprobaron hijos ausentes/puertos cerrados en los resultados propios:82hijos y20puertos premerge;25hijos posteriores ausentes, con comprobación de cierre de listeners en el banco. No significa medir supervivencia de cada conexión heredada. Errores propios preservados/declarados: polling SyntaxError antes de operar; primer intento de empaquetar antes de existir result.json; dry-run git sin credencial local, recuperado mediante conector autorizado sin extraer secretos. No truncamiento de evidencia para solucionar transporte.

Gate I: reproducción del instrumento corregido y falsadores PASA en alcance; repetición adversa clasificada, causa exacta del tiempo de init NO MEDIDA. Gate II: conclusión de Astra sostenida sin nuevos defectos probados ni aprobación productiva. Gate antes del merge: compilación y111tests en árbol idéntico, runtime CLI y bloqueo de recuperación ejercitados; podían detectar esos fallos. Gate III al escribir: evidencia publicada y reconstruida; readback de este informe, Doc público y Nexus se completan como cierre administrativo antes del chat, sin cambiar los resultados experimentales.
