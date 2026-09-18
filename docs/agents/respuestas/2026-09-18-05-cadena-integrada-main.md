# Siete PR integrados en main, sin despliegue

18-sep-2026 ART. Abraham aprobo explicitamente el lote PR13->PR12->PR11->PR10->PR9->PR8->PR7 mediante ClickKit, excluyendo PR1 y cualquier despliegue. Se ejecuto ese lote completo, no se pidio una segunda autorizacion ni se amplio el alcance.

## Resultado verificable

Main de producto:30189275ea996e23aa7804e2334f0b9ba93dd8d1. Tree:110dccfa2da21ff08fbac7b875d705f6cf496ade, EXACTAMENTE el tree de la integracion simulada antes de pedir confirmacion. API GitHub confirma merged:true/state:closed en los siete PR. El unico PR abierto al cierre de la comprobacion es PR1, con cabeza2360f27d43fdc9a1e2a74a3f6465698918df2ad1 sin modificar. Esta entrega agrega despues solo recibo/evidencia a main.

Orden y commits de merge:

1. [PR13](https://github.com/gatehot59-star/corpus-legal-tarija/pull/13),logout hacia PR12:149b1ed260d76ffe73eee7b31e450b8a0a1cf609,23:50:30Z.
2. [PR12](https://github.com/gatehot59-star/corpus-legal-tarija/pull/12),guards hacia PR11:ceab40f1cc3e6a238921e3353bf7dd813ec9aa87,23:50:57Z.
3. [PR11](https://github.com/gatehot59-star/corpus-legal-tarija/pull/11),login hacia PR10:0158aa56793aefb52dd4d9091f945e8c5bfda2ba,23:51:17Z.
4. [PR10](https://github.com/gatehot59-star/corpus-legal-tarija/pull/10),permisos hacia PR9:993db008464166f80044f8dc24701d01680eb9c1,23:51:33Z.
5. [PR9](https://github.com/gatehot59-star/corpus-legal-tarija/pull/9),HTTP hacia PR8:47ae2e6d40c26646c5c7bd6606eb579321965b93,23:51:48Z.
6. [PR8](https://github.com/gatehot59-star/corpus-legal-tarija/pull/8),lector exacto hacia PR7:90856997d084656b4bf92b4d3d8714153466a231,23:52:04Z.
7. [PR7](https://github.com/gatehot59-star/corpus-legal-tarija/pull/7),copia limpia y cadena completa hacia main:30189275ea996e23aa7804e2334f0b9ba93dd8d1,23:52:22Z (20:52:22 ART).

Cada llamada uso expectedHeadSha de la cabeza comprobada inmediatamente antes. Se preservo historia con merge commits, sin squash/rebase ni borrado de ramas. Entre cada paso se comprobaron merged:true,la nueva cabeza del siguiente PR y tree identico al stack21ab505. Antes del ultimo paso,main seguia en eef9bf2. Ningun cambio de codigo manual durante la cadena.

## Por que PR1 queda afuera

[PR1](https://github.com/gatehot59-star/corpus-legal-tarija/pull/1) tiene conflicto add/add en sistema/api/fuente_nacional.py con las protecciones actuales. El diff antiguo acepta manifiestos ausentes como lista vacia,ignora JSON invalido y no verifica el hash al resolver texto;main ya tiene validaciones fail-closed. No se elige una version por encima de la otra a ciegas. Tambien toca otros31archivos; no es solamente un cambio de alias.

Primera simulacion local de PR1 dijo historias no relacionadas,pero el clon era shallow. Se completo el historial y se repitio:el conflicto add/add es el hallazgo real. La falta de historia del clon NO se atribuye al repositorio. PR1 queda pendiente de reconciliacion y pruebas separadas,no descartado ni cerrado.

## Preflight y comprobacion posterior

Se enumeraron ocho PR abiertos,main/auditorias sin cambios desde eef9bf2. Los checks estructurados de las siete cabezas previas decian completed/success;no habia reviews emitidas. No se convierte silencio de Copilot en aprobacion. Se comprobo cadena de ancestros7->8->9->10->11->12->13 y merge-tree sin conflictos para main+PR13. El resultado simulado agrega28archivos, no sustituye los entrypoints productivos existentes.

Antes de la aprobacion corrieron los mismos cinco bancos sobre el tree combinado:10+18+15+15+21=79tests exit0,py_compile exit0,3mutantes exit1 por assertions. Despues del merge se hizo git archive del main30189275 en otro directorio y se reejecuto el instrumento:

- tests/test_isolated_session.py:10tests,13.143s,exit0.
- tests/test_login_guards.py:18tests,22.158s,exit0.
- tests/test_access_policy.py:15tests,5.197s,exit0.
- tests/test_exact_http.py:15tests,1.560s,exit0.
- tests/test_clean_snapshot_sol.py:21tests,6.258s,exit0.
- py_compile isolated_session y su banco:exit0.

79tests del alcance integrado;las12login heredadas estan dentro de18,no duplicadas. Son HTTPloopback+SQLite real temporal y bancos de lector/copia,no una ejecucion del producto desplegado. Mutantes copiados del main:sin revocacion produce None!=1000;revocar todas produce403!=200 en otra sesion;reescribir fecha produce1010!=1000. Los tres fallan con AssertionError, no por imports ni timeout. No se suman mutantes ni repeticiones al total79.

Crudos completos:docs/agents/evidencia/2026-09-18-05-main-tests.json. Estados API:docs/agents/evidencia/2026-09-18-05-merges.json. Scripts y capturas originales quedaron en /workspace/corpus-merge-20260918;instrumento reutilizado /workspace/corpus-logout/verify.py. El banco detiene listeners ficticios y limpia temporales. No se imprimen tokens.

## CI no es lo mismo que esta prueba

Los siete PR tenian CI success antes de la cadena. El commit final30189275 devolvio check_runs total_count0:el workflow clean-snapshot se dispara por pull_request o workflow_dispatch,no por push a main. Por eso NO se afirma un nuevo CI verde de main;la evidencia posterior es la ejecucion real en brain-env desde su commit. No se lanzo manualmente CI ni se genero un despliegue.

Se inspeccionaron triggers de los workflows del tree:OCR/genesis/historico estan acotados a sus ramas,el censo a disparadores/censo-gaceta.txt que no cambia,y los bancos de integridad a PR/manual. No se cambio configuracion de despliegue,secretos,servidores o base viva.

## Gate antes de firmar

- Los siete se mergearon -> respuestas de merge y relectura API merged/state/merge_commit_sha -> podia decir false o distinto -> medido,bien.
- Main contiene el tree aprobado -> git rev-parse commit^{tree} contra tree preflight -> podia diferir -> medido,bien.
- Los79tests pasan desde main -> subprocess con command/cwd/exit/stdout/stderr crudos -> podia dar rojo -> medido,bien.
- El instrumento detecta tres defectos de logout -> mutaciones y assertions objetivo -> dio rojo en los tres -> sensibilidad medida para esos tres defectos.
- Producto en produccion arranca -> no hubo ejecucion ni despliegue -> NO MEDIDO. Esto se expuso ANTES de confirmar.

Una consulta anonima de PR12 devolvio merged:false inmediatamente despues de merge exitoso,mientras la cabeza destino ya era correcta. Se detuvo el siguiente merge,se consulto via MCP y confirmo closed/merged:true;las comprobaciones siguientes y el barrido final evitaron cache de URL. No se ignoraron los datos contradictorios.

## Alcance y siguiente trabajo

Integrado en Git NO equivale a activado en Corpus vivo. Lector exacto,permisos,login/guards/logout siguen requiriendo composicion/provisionamiento explicitos y datos ficticios para su entorno aislado. Sin cuentas reales,credenciales reales,conexiones a VM,migraciones,despliegue ni borrado de ramas. No se afirma haber re-auditado seguridad del host,OCR,derecho,cobertura6079documentos o crash recovery.

D09/M03 y piloto siguen abiertos. PR1 requiere reconciliar el adaptador antiguo sin perder las validaciones nuevas;la UI aislada del recorrido y la restauracion demostrada tambien siguen pendientes. Ninguna aprobacion legal,humana o comercial se sustituye por el merge.

QA del procedimiento de integracion:autorizacion acotada,preflight reproducible,head pinneada por merge,verificacion intermedia y final,79tests posteriores,3mutantes y evidencia cruda. No se fabrica un puntaje nuevo de producto:se conserva el alcance limitado de las evaluaciones anteriores. El arranque productivo permanece NO MEDIDO.
