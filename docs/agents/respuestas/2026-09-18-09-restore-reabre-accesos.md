# Recuperacion: un backup anterior puede reabrir accesos revocados

18-sep-2026 ART. Pedido: SIGUE. Se avanzo con un ensayo de recuperacion frio, sintetico y reversible sobre el main c264ff94e07a46fa5f8b9a5f0d5b7115efd2fd54. No se escribio un restaurador de producto ni se modificaron las bases reales. La seguridad de restauracion queda RECHAZADA para el procedimiento ingenuo probado, no para toda estrategia posible de recuperacion.

## Por que este paso

Enmienda operativa v2, unidades M03/F05: recuperar no significa solo que SQLite abra o que los bytes coincidan. La identidad/politica tambien debe conservar las restricciones. Se leyeron el plan, el runbook de demo, esquemas access_policy/isolated_login, arbol y coincidencias backup/restore en sistema,infra,tests,instrumentos. Solo PR1 seguia abierto; no habia un PR de recuperacion para duplicar. Esta lectura no afirma ausencia de backups en todas las maquinas.

La prioridad es reducir un riesgo de perdida/reapertura antes de presentar el sistema como apto para piloto. M03 entero sigue pendiente: TLS, reset, controles operativos y muestra aprobada no se sustituyen con este experimento.

## Sujeto exacto y metodo

Repositorio archivado por git archive del SHA c264ff9. Instrumento docs/agents/evidencia/2026-09-18-09-restore-probe.py.txt. Importa solamente los helpers de transporte y ciclo de vida de tests/test_demo_aislada.py; no ejecuta su discovery ni duplica sus 18 tests. El lanzador real sirve por HTTP loopback en subprocesses con PIDs distintos. No se parchea el producto.

Crea su propio TemporaryDirectory, init genera dos SQLite ficticios con permisos privados. Cada backup es copytree a una carpeta nueva solo despues de apagar el servidor; no copia SQLite en caliente ni sobreescribe siquiera la fuente sintetica. No se usa un backup de Corpus vivo. Tokens viven solo en memoria; el recibo no los contiene.

Secuencia medida:
1. Login y lectura200; servidor apagado; copia fria de candidate.db y sessions.db identica a la fuente.
2. En el estado actual: logout200 y siguiente lectura403. Con servidor apagado se revoca el permiso de ana, se retira el documento y se adelanta deliberadamente el high-water del reloj una hora. Nuevo proceso: token viejo403 y login503 frente a ese reloj persistido.
3. Se restaura el backup anterior en otra carpeta nueva, sin modificar la fuente actual. Nuevo proceso: el MISMO token vuelve a200; login nuevo200 y lectura200. El reloj restaurado queda por debajo del high-water posterior perdido. El texto coincide con el prefijo ficticio esperado y el candidato conserva su SHA.
4. Se repite en otra copia restaurada, eliminando SOLO access_sessions: token viejo403 pero login nuevo200 y lectura200. Por eso purgar sesiones no resuelve el rollback de permisos y retiradas.
5. Otra copia restaurada queda en cuarentena quitando login_environment. El CLI real rechaza arranque exit2, stdout vacio, stderr DEMO_STARTUP_FAILED: ValueError. Las dos bases quedan identicas antes/despues del intento. Esto es bloqueo, NO reparacion ni permiso para reabrir.

La copia actual original queda byte-identica antes/despues de las restauraciones. Al terminar se cerraron los servidores y se limpiaron los directorios temporales del instrumento. Scan final de procesos de este ensayo: ninguno activo.

## Resultado y control

El oraculo de aceptacion exige403 para una sesion revocada antes de recuperar. Observo200: FAIL. El exit0 del instrumento solo significa observaciones completas, no restore seguro. El positivo de403 antes de copiar y el200 despues, obtenidos del mismo CLI y token, distinguen reinicio normal de rollback de almacenamiento.

La purga de sesiones es un contracontrol: muestra que una correccion estrecha que cierre el primer ejemplo igual habilita el documento retirado mediante login nuevo. La cuarentena demuestra una barrera existente que rechaza este fixture, no que pueda reconciliar estado perdido.

Se realizaron dos corridas independientes en directorios temporales nuevos. Primera con PIDs760..764; segunda con775..779 capturada con subprocess.run, timeout120s, stdout/stderr completos y exit0. La segunda es la captura canonica publicada. No se presenta como auditoria independiente de otra persona. Se reutilizan helpers propios, con assertions sobre HTTP y PID, sin inventar independencia del operador.

## Alcance del hallazgo

Esto NO refuta los tests previos de logout/reinicio: aquellos reinician con el store ACTUAL, este ensayo retrocede todo el store. Tampoco prueba una vulnerabilidad accesible remotamente: requiere que un operador restaure un backup anterior. Confirma un riesgo operativo que los limites anteriores declaraban NO MEDIDO.

Se perdieron simultaneamente revocacion de sesion, permiso, retirada y high-water. El experimento no atribuye la reapertura a uno solo por separado, ni mide restauracion incremental, offsite, corte de energia, consistencia en caliente, RPO o RTO. El high-water futuro es un control sintetico, no un incidente real de reloj.

Candidato ficticio SHA256 c3185812fc53daa82870eea16e778f04d3a1b3ee7dfef92a3e083bad7ea3926a. Es hash de fidelidad de bytes, NO evidencia de seguridad ni de validez juridica.

## Siguiente cambio propuesto, NO ejecutado

Crear un comando de recuperacion SOLO para la demo sintetica, restaurando exclusivamente a destino nuevo y manteniendo por defecto el resultado en cuarentena, con manifiesto/hash e inventario claro del estado de autorizacion antiguo. Ninguna opcion automatica de reabrir, ningun marcador reinsertado automaticamente y ningun permiso emitido.

Para reapertura real se necesita un estado de permisos/retiradas vigente y confiable, o aprobacion nueva que reconstruya el alcance desde fuentes actuales. El backup viejo no contiene eventos posteriores: no se pueden adivinar. El tratamiento de sesiones, credenciales, presupuesto de intentos y reloj debe ser explicito; no basta con borrar una tabla.

El cambio toca una frontera de autorizacion y requeriria modificar CI para verificarla. Se pide autorizacion concreta para implementarlo en PR, sin merge ni despliegue, en vez de aprovechar SIGUE como permiso general. No se restaura nada real.

## Evidencia y errores de preparacion

Captura canonica: docs/agents/evidencia/2026-09-18-09-restore-capture.json. Instrumento exacto ejecutado: docs/agents/evidencia/2026-09-18-09-restore-probe.py.txt, SHA2568810b85b48db24cb8efee08ba79ab2c5dafb7b93d50d17419061dedecec57f46. El JSON contiene comando, exit, stdout completo con diez eventos, stderr vacio. Se verificara igualdad con las capturas recuperando el commit antes de responder.

Preparacion: la primera escritura del auxiliar incorporo signos+ literales, detectados antes de compilar/ejecutar; se materializo el archivo limpio. El nombre de la columna de login_clock se corrigio a singleton tras leer el esquema real, antes de la primera corrida. Ningun script no ejecutado se entrega. El wrapper de la primera llamada acababa en cat y no exponia directamente el exit del instrumento; la segunda captura usa subprocess.run y conserva ese returncode real.

## QA

TITAN FULL, instrumento de diagnostico, no implementacion productiva. Completitud15/15: instrumento completo y10eventos; ejecutabilidad15/15: py_compile ydos corridas reales, oraculoFAIL explicito; documentacion9/10: sujeto/comando/control ylimites, no runbook productivo; proceso QA4/5: HTTP real, fuente preservada, captura recuperable, seleccion de casos propia sin review externo nuevo. Total43/45=95.56/100; N/A55 puntos del protocolo (seguridad productiva, testing/cobertura nueva, arquitectura, DevOps, innovacion). El puntaje califica el instrumento, NO la recuperacion, que dioFAIL.

No se modifica el workflow para un experimento puntual guardado como evidencia .py.txt. No es una nueva suite de regresion prometida como activa en CI. La futura implementacion debe llevar banco y paso CI propios bajo aprobacion.
