# PR12: reparos de aislamiento y reloj, reproducidos antes de corregir

18-sep-2026 ART. Pedido:CONTINUA sobre Corpus. [PR12](https://github.com/gatehot59-star/corpus-legal-tarija/pull/12),titan/login-audit-guards sobre PR11. Base3a60627101859ca92c9b0a4fdd436205b99bb504;codigo publicado y reejecutado314c6d7e9286a0bcca9ce0cacbfa0312c301f93f. Sin merge,despliegue,credenciales reales,cuentas humanas o cambios a Corpus vivo/VM. PR1 y PR7..PR11 intactos.

## Por que este paso

Antes de agregar otra funcion, se leyeron los reparos nuevos en main eef9bf2 y las ramas abiertas. [SOL](https://github.com/gatehot59-star/corpus-legal-tarija/blob/eef9bf2/docs/auditorias/2026-09-17-22-sol-pr8-pr11.md) confirma avances pero reproduce la marca de aislamiento solo en emision. [Revision Astra](https://github.com/gatehot59-star/corpus-legal-tarija/blob/eef9bf2/docs/auditorias/2026-09-18-02-revision-astra.md) confirma retrocesos de reloj dentro de ventana,ademas de distinguir un falso rojo WAL del instrumento. No se atribuye aquel falso rojo a corrupcion de Corpus. [OPUS](https://github.com/gatehot59-star/corpus-legal-tarija/blob/eef9bf2/docs/auditorias/2026-09-18-opus-pr8-pr11-independent.md) es contexto leido,no una nueva ejecucion en este turno.

Se priorizan los dos guards del modulo activo antes de sumar logout/reset:son dependencias reales de su contrato de aislamiento, no mantenimiento ajeno al objetivo. No se afirma que el corpus completo este cubierto:el lector exacto sigue limitado a extracciones versionadas disponibles. No se reaudito cobertura juridica ni la base real.

## Reproduccion sin cambios

El nuevo banco sobre git archive del PR11 original produjo exit1:quitar login_environment dejo lectura200en vez403. Secuencia de tiempos2000,2050,2049,1999:el tercer login produjo200en vez503 y dejo3sesiones en vez2. Dos tests,tres assertions rojas;la tercera es consecuencia de la sesion adicional,no tercer defecto independiente. Datos ficticios,HTTPloopback,temporales eliminados y listeners apagados. El banco no imprime tokens.

## Contrato elegido e implementado

1.Marca como corte de despacho:se consulta read-only antes de TODAS las rutas del wrapper IsolatedLoginApp. Fila ausente403ISOLATED_LOGIN_DISABLED;tabla/store inaccesibles503ISOLATION_UNAVAILABLE. Se conserva la comprobacion dentro de la transaccion de emision. Restaurar la marca permite otra vez usar sesiones y grants vigentes:esto es pausa del wrapper,NO revocacion permanente de sesiones. No retira solicitudes que ya pasaron el control ni texto entregado. Usar directamente PR9/PR10 sin el wrapper no obtiene esta semantica.

2.Reloj de LOGIN:tabla nueva login_clock(singleton,last_seen REAL)guarda ultima observacion confirmada en su transaccion. Se compara el timestamp original,antes de truncar a segundos de sesion,para detectar1000.8->1000.7. Rechaza valores menores con503y sin crear sesion;igualdad permitida. Observaciones confirmadas de password incorrecto y limites de intentos se conservan por el flujo transaccional. El banco prueba password incorrecto;no se agrega aqui una medicion separada de throttling+rollback. El guard anterior de inicio de ventana sigue existiendo.

No prometer monotonia global:lecturas PR10siguen comparando validez contra el reloj del host,no esta tabla. Tampoco protege contra rollback de la base,operador malicioso ni transacciones que abortaron antes de confirmar la observacion. La prueba recrea el objeto sobre el mismo store,no reinicia la maquina ni certifica crash recovery.

## Archivos y arquitectura

sistema/api/isolated_login.py:dos guards y declaracion login_clock. tests/test_login_guards.py:6regresiones nuevas con12heredadas del banco login. .github/workflows/clean-snapshot.yml:agrega path/compilacion y reemplaza ejecucion del banco de12por el de18,evitando contarlas dos veces. Mantiene21SOL,15HTTP,15access,pincheckout,contents:read,persist-credentials:false y timeouts.

Sin dependencias nuevas ni migracion automatica. El esquema se aplica solo en fixtures nuevos. Store antiguo sin login_clock:login503;lectura conserva su control de permisos y marca. No se migro ningun store real. Nueva consulta adicional de marca por solicitud;10x,carga y concurrencia no medidos. Store/clock/WSGI/admin confiables,advertencia de proxy publico y limites de cuerpo/socket de PR11siguen vigentes.

## Ejecucion del codigo publicado

Los dos archivos publicados coinciden byte por byte con los ensayados. Desde314c6d7:py_compile exit0;18tests login/guards en21.580s;15access en5.365s;15HTTPen1.455s;21SOLen5.575s. Total69tests de estos cuatro procesos,exit0. Las12login heredadas se ejecutaron una vez, no se cuentan como18nuevas.

Seis nuevas:marca retirada con sesion ya emitida y recuperacion al restaurarla;tabla de marca ausente;secuencia temporal auditada sin nueva sesion;fracciones y recreacion del objeto;password incorrecto actualiza observacion;tabla de reloj ausente falla cerrado sin automigrar. Los tests previos conservan login!=grant,expiracion,revocacion,malformados,limites y cleanup.

[CI stable_identity](https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35396710060/job/105767088891):completed/success,18-sep21:25:43Z..21:25:59Z. Copilot solicitado;no se infiere aprobacion de su silencio. Auditorias previas no certifican estos cambios nuevos.

Instrumento podia dar rojo:los mismos tests objetivo fallan contra PR11y pasan con el fix. Logs completos de antes/despues y regresiones en archivos JSON hermanos, no base64. No se ejecutan nuevos mutantes ni se afirma nueva cobertura de lineas en este turno.

## Alcance y siguiente dependencia

Correccion acotada de guards del login aislado. No logout/reset/UI/provisionamiento real/grants respaldados por actas humanas/TLS/carga. No merge ni piloto. No cambia lector legacy,OCR,busqueda,citas o exportaciones. D09/M03no se cierran aqui. Siguiente incremento de ciclo de sesion puede ser logout HTTP y su revocacion verificada,siempre aislado;no iniciado en esta entrega.

## QA TITAN FULL

81/90=90/100 para modulo aislado,no aprobacion de merge o produccion. Despliegue10N/A,no autorizado;CI si medido. Completitud14(guards/schema/tests completos,solo alcance declarado);ejecutabilidad15(compile69tests publicado);seguridad13(fallo cerrado con limites de carrera y reloj explicitados);testing12(rojo real antes,6nuevas+regresion,sin nueva coverage/carga);arquitectura9(cambio quirurgico,reuso,consulta extra no benchmark);documentacion10(contratos antes/despues,migracion no automatica,crudos y reproduccion);mejoras4(fracciones,persistencia,marca rota,restauracion);proceso4(git/CI/crudos,review nueva pendiente). No aumentar score por una auditoria historica.

Roles:Architect(semantica de pausa y reloj observado),Builder,Security,Tester,QA. Solo instrumentos de brain-env/GitHub,no ejecutores externos inventados. No nuevo testigo independiente de seleccion:los casos vienen de SOL/Astra,la regresion la escribio Brain.

## Evidencia

2026-09-18-03-guards.json:before sujetoPR11,after sujeto314c6d7,command/exit/stdout/stderr literales. 2026-09-18-03-regression.json:los tres bancos previos reejecutados contra314c6d7. CWD antes=/workspace/corpus-login-guards/base;despues=/workspace/corpus-login-guards/published. Guardar JSON plano evita repetir corrupciones previas de transporte codificado. Comparar todos los campos contra capturas locales antes de entregar.
