# PR10: permisos persistentes conectados al lector aislado

17-sep-2026. Pedido:CONTINUA, sobre la conexion HTTP exacta sin cambiar Corpus vivo.

[PR10](https://github.com/gatehot59-star/corpus-legal-tarija/pull/10). Rama titan/persistent-access-policy sobre PR9. Base39d4f806860c4fb04749aedd4d12c9bc28440850. Codigo publicado y reejecutado17de5b16cca0378ad822535d82338b5238df3238. Sin merge, despliegue, cambios a la VM, base viva, credenciales o servicios. PR1 y ramas PR7/PR8/PR9 no se modificaron.

## Resultado y lugar en el plan

El callback de PR9 ya tiene un proveedor persistente real:consulta una base SQLite separada para resolver sesion, usuario, membresia y AccessGrant antes de leer una version. Sus pruebas usan identidades y actas ficticias explicitamente marcadas. Se implementa la decision de acceso, NO la emision real de permisos, altas de cuentas, login, pago ni piloto.

Es avance tecnico aislado de D09/B02 y parte de los controles M03; no cierra esas unidades ni sustituye A08/I02 o autorizaciones juridicas. Se releyeron la enmienda v2 y el estado actual:main9bc270d,PR9sin cambios y sin review threads al inicio. No aparecio proveedor de acceso existente en sistema/contracts/tests de la base.

## Arquitectura decidida antes de implementar

Arbol del cambio:
- sistema/api/access_policy.py: esquema SQL, proveedor de acceso y composicion make_app.
- tests/test_access_policy.py:15tests de integracion HTTP con SQLite y fixtures ficticios.
- .github/workflows/clean-snapshot.yml: agrega triggers, compilacion y test; conserva permisos y los tests anteriores.
- Este archivo:ADR, contrato, limites, QA y evidencia cruda.

Decisiones:store de permisos separado del candidato, para no meter datos de identidad en el corpus legal; coleccion fija del lado servidor, no de un header; un SELECT con joins para observar todos los permisos en una instantanea SQLite; nueva consulta por pagina para no cachear revocaciones. Se reutilizan PR9 y PR8, sin cambiar rutas legacy ni abrir otro servidor. No se incorpora framework ni paquete externo. SQLite3.46.1 y Python3.12.14 medidos en brain-env; STRICT se ejecuto efectivamente.

No se elige JWT autocontenido porque el requisito inmediato exige revocacion persistente por pagina y todavia no hay un emisor autentico. Se acepta una sesion bearer opaca ya emitida por el host:solo su SHA256 se guarda. El emisor futuro debe usar al menos256bits de entropia criptografica; validar longitud/formato NO demuestra esa entropia. En este turno no se genero ni emitio una credencial real.

A10x:indices por digest,grants(user_id,collection_id) y claves compuestas; no se afirma benchmark10x ni capacidad productiva. El lector de PR8 sigue releyendo/hashando texto completo por pagina.

## Contratos y flujo

SQLiteAccessPolicy(store,collection,clock=time.time), callable(environ,uid,version)->bool. make_app(candidate,policy_store,collection,clock) devuelve ExactReaderApp con este proveedor; exige archivos distintos. Importar o construir no inicia listener ni escribe schema. El store debe existir. SCHEMA es declaracion ejecutable, no una migracion aplicada automaticamente.

Tablas:access_users(id,enabled);access_sessions(token_sha256,user_id,valid_from,valid_until,revoked_at);access_collections(id,enabled,approval_evidence);access_memberships(user_id,group_id,enabled);access_grants(id,user_id,group_id,collection_id,origin,valid_from,valid_until,revoked_at,issued_by,evidence_id);access_documents(collection_id,uid,version,withdrawn_at). Fechas:segundos Unix UTC. Intervalo[inicio,fin), cualquier revoked_at/withdrawn_at no nulo bloquea. origin solo pilot/paid; ambos usan la MISMA decision.

HTTP Authorization -> valida Bearer opaco -> SHA256 -> SELECT de sesion/usuario/grant/membresia/coleccion/documento/version -> True literal -> PR9 abre candidato readonly -> PR8 entrega texto exacto. Sin sesion valida,usuario habilitado,membresia coincidente,coleccion habilitada,grant vigente no revocado y version no retirada:no hay lectura. Sesion y grant deben haber comenzado y no haber vencido. Otro UID o version no hereda acceso.

La coleccion esta enlazada en configuracion del host, no puede elegirse con X-Collection/X-User/X-Group. Los valores de SQL son parametros. Store read-only/query_only y conexion cerrada por peticion. Una consulta valida sin permiso retornaFalse y PR9responde403. Fallo de store o reloj invalido levanta error y PR9responde503redactado. Se mantienen no-store y la validacion de locators de PR9.

La referencia approval_evidence/evidence_id exige presencia estructural; NO comprueba que el acta exista, sea autentica o juridicamente suficiente. Ese control pertenece al flujo administrativo de emision, pendiente. Es un error vender estas cadenas como aprobacion humana.

## Pruebas ejecutadas desde el commit publicado

Comandos y stdout/stderr completos en el payload al final.

- Compilacion py_compile:exit0.
- tests/test_access_policy.py:15tests,5.161s,exit0.
- tests/test_exact_http.py:15tests,1.449s,exit0.
- tests/test_clean_snapshot_sol.py:21tests,5.891s,exit0.

Son51tests entre estos tres bancos; no se suman las reejecuciones de coverage como tests nuevos. Un test incluye19subcasos independientes:sin sesion/usuario/grant/membresia/documento,usuario/membresia/coleccion deshabilitados,sesion/grant futuros o vencidos/revocados,otro usuario/grupo/coleccion,documento retirado y otra version. Cada subcaso comprueba primero200 y despues403,restaurando su fixture aislado. No son19usuarios reales ni19gates humanos aprobados.

Ademas se prueban limites temporales inclusivo/exclusivo,revocacion de sesion/grant y retirada entre paginas,headers falsos,credencial ausente/forjada/digest usado como credencial,fallo de store,reloj NaN/infinito/negativo/bool/texto,constructores,esquema invalido y origen pilot/paid sin conciliar ningun pago.

El control positivo pagina completamente un texto sintetico de150clausulas y exige igualdad exacta y hashes sin cambios de AMBAS bases. El test teardown apaga el servidor y exige thread terminado. Todas las escrituras/revocaciones/borrados del banco son sobre archivos temporales ficticios. Algunos negativos crean relaciones huerfanas con foreign_keys desactivado en la conexion de test para comprobar que incluso esas filas no autorizan.

Controles negativos sobre copias del codigo publicado:
1. Eliminar g.revoked_at IS NULL:la prueba de revocacion entre paginas falla200!=403,exit1.
2. Sustituir ?<g.valid_until por ?>=0:subcaso grant-expired falla,exit1.
3. Sustituir d.version=? por ? IS NOT NULL:subcaso different-version falla,exit1.

Las sustituciones exactas y logs completos estan en payload. No se publicaron esos mutantes ni se afirma que GitHub los corrio.

Coverage stdlib trace con descubrimiento y threads trazados:access_policy52lineas ejecutables,100%lineas. NO coverage de ramas,carga,concurrencia o sistema completo. exact_http73% y version_text70% dentro del banco NUEVO; sus suites propias corrieron por separado. No se presenta esto como100%de Corpus.

Antes de reejecutar se compararon archivos con el ensayo local:access_policy tenia una linea en blanco adicional en la version publicada,ASTigual;por eso todas las pruebas y mutantes se volvieron a ejecutar desde el commit publicado, no se afirmo byte-identidad falsa. Los tests,exact_http,servidor y version_text si eran byte-identicos.

[CI stable_identity](https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35288402474/job/105425726034):completed/success,23:47:44Z a23:47:51Z. Workflow conserva checkout11d5960a326750d5838078e36cf38b85af677262,contents:read,persist-credentials:false,pull_request y timeout60s por banco. Review Copilot solicitada,get_reviews=[]antes de cierre:no aprobacion.

## Seguridad y lo que aun NO se entrega

El store y su escritor administrativo son confiables; no se protegen contra un administrador malicioso o sustitucion de archivos por el mismo usuario del sistema. La decision usa una instantanea de permisos, pero NO hay transaccion atomica entre el store y la posterior lectura de texto. Una revocacion confirmada despues de autorizar una peticion no retira esa respuesta en vuelo ni texto ya entregado;si bloquea la siguiente pagina. Reloj del host debe ser confiable.

No login,reset,emision/rotacion de sesiones,UI de cuentas,administracion autorizada/auditada de grants ni validacion de actas humanas. No TLS,rate limiting,prueba de carga,ingress o auditoria nueva de CVEs/historial de secretos. No publicacion de coleccion ni pruebas con personas. Origin paid es solo un fixture del mismo gate,no integracion de pagos. No endpoints de escritura ni cookies nuevos.

Pendiente conectar el ciclo de vida de cuentas/sesiones y emision administrativa respaldada por actas reales,siempre primero aislado. D09 no se cierra con un SELECT,ni M03 con tres bancos. Los demas bloqueos y gates del plan siguen vigentes. No se amplio el alcance juridico ni se corrigio OCR.

## QA TITAN aplicable

TITAN FULL por acceso/CI.82/90=91/100 como MODULO AISLADO,no aprobacion de despliegue/merge/piloto. DevOps de despliegue10N/A porque no se autoriza/entrega;CI si medido.

Completitud14/15:archivo completo,make_app y schema ejecutados;emision fuera de alcance. Ejecutabilidad15/15:compile y51tests sobre17de5b16. Seguridad13/15:SQL parametrizado,readonly,checks y3mutantes;host/emisor pendientes. Testing14/15:15nuevos,19subcasos,3mutantes,52lineas100%;no carga/concurrencia. Arquitectura9/10:separacion e interfaces,indices;sin medicion10x. Documentacion9/10:contrato,comandos,limites y crudos;sin runbook productivo. Mejoras4/5:coleccion fijada,readonly,fallo de reloj cerrado y restricciones de esquema. Proceso4/5:relectura publicada,CI y crudos;review ajena aun no emitida.

Roles:Architect(contrato/store),Builder(implementacion),Security(frontera),Tester(HTTP/SQL/mutantes),QA(relectura/evidencia). No delegacion u orden externa inventada. Criterio de avance:reemplazar la policy fija por una decision persistente probada,sin fingir que existe un sistema de cuentas terminado.

## Evidencia cruda y veredicto separado

PayloadJSON14634bytes,SHA256de12ad3301abd59a345b98d016c01c049cdd9cd48a947608d6eb65f25601c8b0. Incluye comandos,stdout/stderr completos,exit codes,mutaciones,runtime,hashes y commit. Decodificar el unico bloque base64 con base64.b64decode,zlib.decompress;validar longitud/hash y json.loads. El texto anterior es conclusion,los logs siguientes son salida del instrumento. Se comprobara contra los bytes originales despues de publicar.

```base64
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
```
