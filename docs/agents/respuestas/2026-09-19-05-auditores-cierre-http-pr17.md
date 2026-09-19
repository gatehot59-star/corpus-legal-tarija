# Auditores revisados y primer reparo corregido: conexiones del fixture HTTP

19-sep-2026 ART. Pedido: revisa que te dejaron los auditores y sigue. Revisor del handoff e implementador del arreglo puntual: Brain; no auditor independiente de su propia correccion.

## Estado real recuperado

Main9175f7bb12df5d0cd46c15b7c4e358e111d106c2. Leidos completos informe AstraPR14 docs/auditorias/2026-09-19-03-astra-pr14-integrado.md, cierre/indice AstraPR16 docs/auditorias/2026-09-19-01-astra-pr16-cuarentena.md, yhandoff docs/auditorias/2026-09-19-04-revision-astra-merge-pr16.md; Nexus49,50,51,52 consultados. No se confundio el cierre actual delindicePR16 con su estado historico abierto.

PR16 YA integrado por autorizacion en otro hilo:2e06380900eef97ec7290e5cd25e38d1ef96e17e,19sep11:33:51ART,contenido presenteenmain. No se hizo otro merge ni se uso esa firma paraPR17. PRs abiertos al comenzar:soloPR1cabeza2360f27d43fdc9a1e2a74a3f6465698918df2ad1. No solapamiento de un PR activo con test_exact_http.py.

Los auditores no demostraron nuevos defectos de producto en los contratos aislados PR14/16. Dejaron deuda de cierres explicitos SQLite en fixtures, advertencia sobre timeout de inactividad frente a plazo total ysolapamiento de suites pesadas, ydos unidades de continuacion: corregir instrumentos ymatriz delrecorrido de usuario. No se repitieron142aserciones sin un delta. El timeout2s no se presento como garantiaDoS; esta entrega no lo modifica.

## Incremento ejecutado: PR17, un archivo

https://github.com/gatehot59-star/corpus-legal-tarija/pull/17
Rama titan/tester-http-sqlite-close, base9175f7b, head3eedba5460495bb1c329e0cd87d8305fd0e9e00a. Solo tests/test_exact_http.py: import closing y3contextos with closing(sqlite3.connect(self.db)) as c,c. Nada de producto,workflow,assertions funcionales,basesreales oAPI.

El contexto interior de conexion confirma/revierte la transaccion; el exterior closing la cierra aun anteexcepcion. Preserva la semantica anterior decommit/rollback,sin depender deGC. Callers reales comprobados porstack:15aperturas ensetUp linea32base,1en test_historical_exact_version_survives_current_change linea130y1en test_tampered_text_never_returned linea159. No se atribuyeron todas las41aperturas aese fixture:24ya se cerraban.

Se eligio primer incremento minimo para aislar elreparo verificable,sin extender a5archivos adicionales ni declarar deuda global saldada. No se afirma que arreglar estos tests acerque por si solo laUI alusuario; reduce una fuente de ambiguedad experimental especifica pedida porlauditoria. Duracionobservada de este turno enminutos,no promesa de productividad global.

## Instrumento recuperado, no inventado desde el resumen

Se reconstruyo laevidencia AstraPR16 desde las3revisiones indicadasenelindice:bc3a4c51b78f1b4210cf9ef3d613bc005caf9398,05e450e4ab28353434fea66013d644cf2ce0cffe,90acb23b681a75beb5ad37961a8d8fa66483acb8,misma ruta docs/auditorias/2026-09-19-01-astra-pr16-cuarentena/evidence.xz.b64. JSON420667bytes,SHAe4e3c3f266c91d628fdcb2be55a319aebd80700c7b42a408d71273e128f5b273 verificado.

Extraccion exacta resource_followup.instrument a sitecustomize.py,sin editarlo. Observador retiene referencias yregistra argv,pid,abiertas,cerradas,pendientes ystacks. Mide cierre EXPLICITO,no supervivencia despues desalida deproceso. Lectura fallida inicial delnombre instruments.resource_observer no seconfundio conausencia:elcampo correcto estabaen resource_followup.instrument. Un intento de comparar texto dentro destr(dict) dioFalse porrepresentacion/escapes,no fueprueba decorrupcion;seuso elcampo literal reconstruido.

Supervisor propio captura cmd,cwd,exit,stdout,stderr yJSONdelobservador. Corridas seriales,enarchives base/fixed nuevos. No se elevaron timeouts ni se lanzaron suites pesadas simultaneas.

## Resultados propios

Controldelcontador:positivo1abierta/1cerrada/0pendientes;negativo deliberado1/0/1. Criterio uniforme enproceso aparte:assert unclosed==0;positivoexit0,negativoexit1.

ANTES sobremain9175f7b:15tests funcionalespasan en1.398s,41abiertas/24cerradas/17pendientes. DESPUES:15tests en1.611s,41/41/0. Inverso exacto(usandoarchivooriginal enotraejecucion):15tests en1.316s,41/24/17. Criterio uniforme daexit1/0/1respectivamente. Elarchivooriginal eselcontrolnegativo deesa propiedad,no undefecto productivofabricado.

Importante:la suite funcional salia0inclusocuando17conexiones no secerraban. No se presenta ese verde como detector declose;elobservador ylaassertion separada sonsuinstrumento. Lossesgos deseleccion propios no desaparecen porque elobservadorvenga deAstra.

Tresbloques run delworkflow existenteejecutados exactamente enserial:79regresion+18demo+14restore=111casos positivos,compilacionincluida. Sin contar otra vez12login heredados orepeticiones del15HTTP. Captura cruda permite vercada duracion;ultimo bloque14tests24.044s,demo18tests28.009s. No se atribuyen las111pruebas aunnuevo CI demain.

Controldeexcepciontransaccional aislado:insertseguido deAssertionError,rollback deja0filas yobservador registra0pendientes. Estemicrocontrol prueba elpatron closing+transaccion,nouna excepcion inyectada encada caller delproducto. SinfallbackGC niwarningsocultos.

Codigo recuperado deGit en3eedba5 comparado byteporbyteconelarchivoejecutado:True. Diff exacto1archivo4insertions3deletions. No cambiasuitesrestantes.

## CI yreview

PR17 job https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35449708876/job/105914625233 completed/success,14:45:36Z..14:46:15Z(11:45:36..11:46:15ART). Los7elementosdepasos delHTMLpublico muestran success, incluidoslos3bloques. No stdoutremotocompleto;conteo111provienedecapturaslocales. No cambios deworkflow nipermisos;test_exact_http.pyyafigurabaenpaths yencomando.

Elcontador declose se ejecuto local ysepreserva comoevidencia,no esta agregado como un nuevogate delCI. ElCI comprueba regresionfuncional;no se fingequeesecheckdetectaria unaretiradafuturadeclosing. Integrarunguard derecursos para todaslassuites esotraunidad,requiere primeroatribuirycorregirlasrestantes.

ReviewCopilot solicitadoPR17,no esaprobacion. EstePR queda abierto,sinmerge. No nuevo runtimeproductivo,servidorpermanente,cuentasreales,credenciales niNAT.

## Evidencia durable

Envoltorio docs/agents/evidencia/2026-09-19-05-cierre-http.json,xz+base64,reversible. Decodifica89251bytesJSON,SHA256d5ca21c389dc28afb44cf41dce4a045cc3d8c95747988c1214ac054bc69eb6c4. Contiene9corridas constdout/stderr completos ystacks,6evaluaciones delmismooraculo,sourcesexactos deobservador/supervisor y7pasosCI. No bases,contraseñas,tokens niheadersHTTPcapturados;elbearerlabel ficticio deltest permaneceencodigo,historico,no credencialreal.

```python
import base64,hashlib,json,lzma
from pathlib import Path
w=json.loads(Path('docs/agents/evidencia/2026-09-19-05-cierre-http.json').read_text())
raw=lzma.decompress(base64.b64decode(w['payload'],validate=True))
assert len(raw)==w['uncompressed_bytes']
assert hashlib.sha256(raw).hexdigest()==w['sha256']
evidence=json.loads(raw)
```

Comparacion remota debytes/campos se realiza antesdechat,Docpublico yNexus. Scratchpropio/workspace/corpus-sqlite-close-20260919,procesospythonpropios ausentes alfinal;listeners del15HTTPcerrados por stop/server_close/joinconassert. No se certifican recursos deprocesosajenos.

Error depreparacion propio:primercomando inline delcriterio final tenia backslash-nliteral,produjoSyntaxErrorantesdecorrerhijos;segundocomando concomprensionescapturo retornosvalidos. No se relanzaron lassuites poresefallo ni se atribuyo alproducto.

## Pendientes ycontrolfinal

CONFIRMADO: reparo heredado HTTP17sinclose ycorreccion0enramaconregresionconservada. REFUTADO: que15testsverdespor sisolos certifiquen cierreSQLite. NO MEDIDO: estadoactual porcallerdelasotrassuites señaladas;nostatsantiguoscomoresultadonuevo.

Pendientes:clean_snapshot_sol,access_policy,login_guardsconfixtureisolated_login,isolated_session. No saldados. Unidad2 matrizbuscar/verificar/guardar/reportar ylecturacompletadelconsumidorUI siguenpendientes,separadasdeestePR. No UIv1conectadaav2,nopublicacionjuridica,nopiloto,noquitarcuarentena,noreapertura,norecuperacionproductiva. M01-M04/F05no cierran.

ModoTITANLIGERO,unarchivodetests,noaccionesdelicadas,norubricadeproductoparaunreparo. GateI:PASA paraobservadorconpositivo/negativo yantes/despues/inverso,capturayatribuciondelcallsite. GateII:PASA acotado,sin extrapolaraotras suites oservicio vivo. GateIII al escribir:gitpendientedereadback,Doc/Nexus secompletanantesdechat;sinconcluirtemporalmentequeyaexisten. No hacefaltarepetirotraauditoriaglobalparaunimporty3contextos.
