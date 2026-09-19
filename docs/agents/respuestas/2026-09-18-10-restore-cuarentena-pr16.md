# PR16: recuperar una copia sintetica sin reabrir accesos

18-sep-2026 ART. Autorizacion ClickKit approve_corpus_quarantined_restore: implementar en rama, pruebas, CI y PR; sin merge, despliegue, datos reales ni reapertura automatica.

## Resultado

PR16 https://github.com/gatehot59-star/corpus-legal-tarija/pull/16, rama titan/builder-quarantined-restore. Base3d45e774ce1c0c126a4e63aef31c256d448f74b8; codigo67d0251ac2d768065cf75b976cd5a72580d34bdd. Cuatro archivos,495lineas agregadas,0eliminadas: sistema/api/demo_restore.py(152),tests/test_demo_restore.py(226),sistema/RECUPERACION-DEMO.md(108),workflow9lineas nuevas. Producto sigue SOLO en PR; main recibe este recibo y evidencia, no el restaurador.

Ya corrio en GitHub: https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35414843978/job/105821331184, stable_identity completed/success, 2026-09-19T02:09:52Z..02:10:30Z (18-sep23:09:52..23:10:30ART). Paso5 Compile and test quarantined synthetic restore success02:10:19Z..02:10:28Z, separado de los pasos anteriores. Se recuperaron los atributos completos de los7elementos de pasos del HTML publico, no stdout completo remoto. El111proviene de las salidas locales, no de contar logs GitHub inaccesibles.

## Contrato implementado

CLI demo_restore.py --source ORIGEN --destination NUEVO --isolated-demo --source-stopped. Funcion restore(source,destination,isolated_demo,source_stopped)->dict. Sin listener, red externa, secretos nuevos ni parametros de reapertura. Solo fixture de demo validado, dos SQLite privados/regulares/propios, sin symlinks/hardlinks/FIFO/sidecars.8MiB por base,16MiB de imagenes; no dimensionado para Corpus real. Destino separado nuevo, padre existente sin symlinks; nada de overwrite/retry automatico sobre parciales.

--source-stopped es DECLARACION DEL OPERADOR, no un lock ni prueba de que el proceso esta detenido. Se exige operacion fria. Compara bytes del origen antes/despues de validarlo y copiarlo para detectar cambios observables; no ofrece atomicidad de dos bases en caliente, ni protege de ABA/operador malicioso con mismo UID/root. Este limite aparece en codigo,manifiesto,runbook y PR.

La primera escritura del destino0700 es RESTORE-QUARANTINE.json0600 con status incomplete. El lanzador existente rechaza ese tercer archivo antes de escuchar: protege incluso si el proceso falla durante copia/sanitizacion. Despues copia ambas bases y verifica igualdad. En una transaccion sobre sessions.db de DESTINO elimina login_environment, purga access_sessions y apaga todas las colecciones; exige postcondiciones antes de declarar exito.

Mantiene grants,retiradas,verificadores de password,presupuesto yreloj para inspeccion, sin declararlos vigentes. Candidato byte-identico; store cambia intencionalmente y el manifiesto distingue hashes de origen/salida e inventarios. SHA es integridad,no firma ni autenticidad. No tokens o hashes individuales de credenciales en manifiesto/log. El store privado si conserva verificadores: no compartirlo como archivo publico.

Al final status quarantined,serve_authorized false. No --reopen. La salida parcial se conserva para inspeccion,nunca se borra sola. Ni retirar solo el manifiesto ni conservar solo el manifiesto con store antiguo debe habilitar arranque: ambas barreras se probaron por separado. Un operador con permisos para desactivar ambas queda fuera del modelo; no se vende como sandbox contra su propietario.

## Pruebas que efectivamente corrieron

Verificador extrae y ejecuta textualmente los3bloques run del workflow; preserva comando,cwd,exit,stdout,stderr. Pasos previos comparados estructuralmente iguales a base. Checkout SHA11d5960a326750d5838078e36cf38b85af677262,contents:read,persist-credentials:false,ubuntu24.04,tope5min sin cambios. Nuevo paso py_compile+timeout120s banco restauracion, sin if ni continue-on-error; tres paths nuevos. No installs/dependencias nuevas ni cambios de permisos.

111positivas:21SOL5.998s+15HTTP1.428s+15permisos5.205s+18guards21.971s+10sesiones13.811s+18demo31.957s+14restore28.945s. Los12login heredados no se cuentan dos veces. Primera pasada del nuevo banco tenia12tests22.542s; se agregaron2fallos inyectados y se ejecutaron los14completos antes de publicar. No se cuentan las repeticiones como tests distintos.

El caso extremo usa el CLI real: inicia demo/login/lectura200,apaga,copia,revoca sesion en estado actual y observa403,revoca permiso/retira documento,restaura BACKUPANTIGUO a destino nuevo. Comprueba store saneado,manifiesto/hashes/permisos0700/0600,preservacion de fuente,candidato ycampos historicos; intento de servir rechaza. Tambien prueba faltanflags,reopeninexistente,destinoexistente/anidado,symlink/hardlink/FIFO,sidecars/permisosamplios,corrupcion/candidatoajeno,tamanoacotado,origen cambiado antes/despues,copia parcial yfallo de sanitizacion.

Falsadores locales sobre copias, ejecutando el mismo bloque nuevo completo:
- no-marker-removal: omite DELETElogin_environment. El guard de postcondicion rechaza; bancoexit1,1fallo+1error(QUARANTINE_NOT_ESTABLISHED y2!=0). No se afirma que haya servido inseguro: se detecto la implementacion rota.
- no-first-barrier: omite primera escritura del manifiesto. Bancoexit1,3fallos+2errores, incluidos manifesto ausente al fallo de copia yassertions de cuarentena. Se guardan TODOS los errores, no solo el primero.
No fueron corridas rojas GitHub; CI real fue positiva. Mutantes no commiteados.

Trace stdlib en proceso de tests ysubprocesos via sitecustomize:113/118lineas ejecutables=95.76271186440678%,faltan35,87,101,103,106 en demo_restore.py. Otra corrida de los14tests, no14tests nuevos. Es cobertura de LINEAS,no ramas/carreras/crash. Codigo ycaptura del medidor se incluyen. No se infiere seguridad general de ese porcentaje.

## Evidencia cruda y reproduccion

Archivo docs/agents/evidencia/2026-09-18-10-restore-evidence.json es envoltorio textual xz+base64, NO binario ni resumen. Decodifica JSON40613bytes,SHA25605520c6fd2f6cbede8688acff7837e606e352c544f05079f19817455d99d1e35. Contiene full_tests con5procesos completos,coverage con salida/lineas,ci_steps con7elementos completos,fuenteexacta de ambos instrumentos yresultado final. No se recorta stdout/stderr. Es compresion reversible para no repetir enormes salidas; el readback debe comparar bytes ycampos contra originales antes del chat.

Decodificar con Python estandar:
```python
import base64, hashlib, json, lzma
from pathlib import Path
p = Path('docs/agents/evidencia/2026-09-18-10-restore-evidence.json')
w = json.loads(p.read_text())
raw = lzma.decompress(base64.b64decode(w['payload'], validate=True))
assert len(raw) == w['uncompressed_bytes']
assert hashlib.sha256(raw).hexdigest() == w['sha256']
evidence = json.loads(raw)
```

Los4archivos del commit67d0251 se recuperaron ycompararon byte por byte con los probados:todosTrue. Scratch /workspace/corpus-quarantine-20260918;solo fixtures temporales del banco, no bases reales. El script verificador se ejecuto una sola vez con nohup,observado hasta complete.json;no se relanzo por consultas tempranas. Medidor de cobertura es corrida separada identificada.

## Seguridad y QA

Se reviso superficie nueva:sinendpoint/red/SSRF/deserializacionejecutable,SQL de identificadores fijos,noentradaSQL,validacionprevia de paths,tamanos/permisos,erroresredactados,destinoexclusivo,barreraprimera,postcondicionestransaccionales ymanifest sin secretos. No nueva dependencia externa: no se pinnea un paquete de memoria ni se afirma barridoCVE global del runtime. TLS/CSRF/cookies/rate-limit de produccion no aplican al CLI yno se certifican por arrastre.

TITAN FULL: Architect contrato/runbook,Builder modulo,Security frontera de copia,Tester banco/CI/falsadores,QA interno yDocs. Roles no equivalen a revisores independientes. Rubrica80/85=94.12/100: completitud15/15(4archivos completos/diff),ejecutabilidad15/15(compiler/111tests/CI),seguridad14/15(barreras ylimites;dueño confiable),testing14/15(14nuevas,95.76%lineas,2falsadores;no crash/concurrencia),arquitectura9/10(moduloaislado/reusa validador;noexpansionproductiva),documentacion9/10(runbookcontrato/errores/limites),QA4/5(evidenciacruda,seleccion propia). N/A15:DevOpsproductivo10,innovacionfueraalcance5. Puntaje no mide avance del proyecto.

Copilot solicitado paraPR16;get_reviews devolvio[] al consultar,noaprobacion. No se inventan hallazgos ni review externo. La aprobacion de este turno no autoriza merge. PR1 fuera del alcance;main solo recibe evidenciadocumental.

## Gate y siguiente

Copia fiel -> bytes/hash yfixturevalidado -> podia fallar -> confirmado acotado.
Queda bloqueado -> CLI real,SQLpostconditions ybarrerasporseparado -> podia fallar -> confirmado en fixtures.
Banco detecta rotura -> dosmutantes mismo step -> podia fallar -> exit1 ambos.
Origen esta detenido -> flagoperador -> NO podia medirlo -> NO MEDIDO por software.
Recuperacionproductiva/piloto -> ninguno -> NO MEDIDO.

Este incremento resuelve la PREPARACION EN CUARENTENA, no reconciliacion ni reapertura. M03/F05 siguen abiertos pararecuperacionreal,offsite,RPO/RTO,controloperativo yautorizaciones. No despliegue,no datosreales,no reemplazo de bases,no credencialesreales,no merge. Proximo gate es review/integracion delPR bajoautorizacion propia;no se activa automaticamente.
