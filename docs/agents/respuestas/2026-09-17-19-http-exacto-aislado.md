# PR9: lector exacto conectado a HTTP aislado, sin cambiar Corpus vivo

17-sep-2026. Pedido: Connect the exact reader without changing live Corpus.

[PR9](https://github.com/gatehot59-star/corpus-legal-tarija/pull/9), rama titan/exact-http-isolated sobre PR8. Base cc8c33562a4adb9976db81478b8cac6f353152f8; codigo publicado y reejecutado 72a3563b13cda5f66104c6746e24c9e79ac4b615. Sin merge ni despliegue.

## En criollo y lugar en el plan

El texto exacto ya puede salir por una peticion HTTP real, en una copia aislada. No se conecta al buscador vivo ni se cambia su proceso. Avance reversible de B02/integracion de B04 e I05, no cierre de D09, M03, piloto ni publicacion B08. Se releyo la enmienda v2: permite prototipos aislados, no adopcion implicita.

La nueva ruta solo funciona cuando el host da una decision explicita de acceso por documento y version en cada pagina. Sin esa funcion, deniega todo. Las pruebas usan decisiones sinteticas; no hay cuentas, sesiones o permisos piloto reales inventados.

## Arquitectura y decisiones

Arbol significativo:
- sistema/api/version_text.py: adapter exacto de PR8, intacto.
- sistema/api/exact_http.py: WSGI opt-in, validacion, decision de acceso, conexion SQLite read-only y JSON.
- sistema/api/servidor.py: servidor legacy intacto, no se monta ninguna ruta nueva ahi.
- tests/test_exact_http.py: 15 pruebas con socket HTTP loopback real, SQLite sintetico y policy de fixture.
- .github/workflows/clean-snapshot.yml: conserva checkout pinneado, contents:read y pruebas previas; agrega compilacion y test HTTP bajo timeout60s.
- Este recibo: contratos, resultados y evidencia cruda comprimida. No dependencias nuevas, contenedor ni despliegue.

Se elige un modulo WSGI separado porque modificar el handler legacy mezclaria el ensayo con un contrato consumido y sus superficies publicas. No es otro framework ni otro producto. No crea listeners al importar ni tiene una base por defecto. El banco inicia wsgiref en 127.0.0.1:puerto efimero y lo apaga al terminar; wsgiref es servidor de prueba, no una recomendacion de produccion.

Se exige version explicita desde la primera pagina para que el authorizer decida sobre el mismo UID/hash que se lee. Se rechazan version desconocida y parametros legacy, no se cae a fusionar ni a la version actual. El descubrimiento autorizado de la version actual queda fuera de esta ruta.

## Contrato y flujo

ExactReaderApp(db_path: str|Path, authorize: Callable[[dict,str,str],bool]|None=None). El db_path debe ser un archivo existente explicito; se abre con mode=ro, PRAGMA query_only=ON y se cierra por peticion. El directorio y la base son administrados por el host confiable; no garantiza resistencia a sustituciones maliciosas por el mismo usuario del sistema.

GET /api/v2/documento/{uid}/texto?version={sha256}&start=0&limit=2600. UID ASCII alfanumerico/guion/guion bajo, max200; hash64hex minuscula; start entero no negativo; limit1..10000; consulta max2048 caracteres, solo tres claves unicas. Parametros desconocidos, duplicados y offsets ambiguos se rechazan.

Peticion -> locator validado -> authorize(environ,uid,version) -> solo True literal -> SQLite solo lectura -> read_version -> JSON con texto exacto, hash, version, next y procedencia. La funcion authorize pertenece al host: debe autenticar y comprobar grant vigente, grupo, coleccion, version y retirada. Un encabezado de usuario no se convierte automaticamente en identidad. No hay segundo sistema de permisos.

Respuesta: conserva contrato PR8, agrega offset_unit=unicode_code_points y source_url_scope=current_document. La URL se toma de la fila estable actual, NO se presenta como URL historica de esa version. authority=secondary, oficial=false, legal_validity=NOT_MEASURED. No implica fidelidad juridica revisada.

Errores:403 ACCESS_DENIED;503 ACCESS_POLICY_UNAVAILABLE o DATABASE_UNAVAILABLE;409 version ausente/integridad/procedencia;416 offset fuera del texto;400 locator invalido;404 ruta/documento inexistente;405 metodo distinto de GET;500 generico para fallo inesperado. Todas las respuestas pasan por no-store y nosniff, no exponen traceback ni tienen CORS abierto. Error de policy cierra acceso antes de tocar DB.

## Verificacion ejecutada

- 15 tests HTTP nuevos pasan. El caso de SOL conserva 150 frases y6906caracteres a traves de paginas de401caracteres; hash completo y DB sintetica antes/despues coinciden.
- Policy ausente, identidad ausente, truthy distinto de True, excepcion de policy, otro UID/version y retirada entre paginas se rechazan. La retirada es una mutacion del conjunto permitido del fixture, no revocacion en un sistema real de grants.
- Dos mutantes locales: omitir el guard de acceso y quitar un caracter de cada pagina. Ambos producen exit1 con assertion failure. No son resultados de CI remoto; prueban que el instrumento local podia dar rojo.
- unittest discover ejecuto133tests en12.840s, exit0. NO son133pruebas unicas: el banco SOL hereda diez pruebas del baseline. Se conservan todos los nombres y resultados crudos, sin sumar duplicados como nuevos.
- Tras publicar72a3563, el nuevo modulo, tests, servidor legacy y adapter PR8 coinciden byte a byte con los medidos. Se ejecuto py_compile y los comandos del workflow:21tests previos en7.626s y15HTTP en1.434s, exit0.
- CI GitHub stable_identity completed/success,21:57:59Z a21:58:04Z: https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35279540112/job/105398041954. El CI ejecuta los bancos sinteticos, no la base real. Review Copilot solicitada, get_reviews=[]; no se infiere aprobacion.

Lectura HTTP de tres versiones de la copia candidata ya existente, paginas10000, sin volver a descargar fuentes:
- Familia historico:195893caracteres,20paginas,0.133s, SHA256 db65fb4ef2f1ef388b7cdeb446b38f1f58eab3ebb3998f4e84b2535fd04ba1a4.
- Comercio:693914caracteres,70paginas,1.325s, SHA256 3e8b29e0d9ed3714aa7270b2297287df17a2067c344aa8578859567b6f1b7b60.
- CPE:263357caracteres,27paginas,0.344s, SHA256 9465ad7d8464032e2e4e5c59405db1a9e71ba65f5dc9cf782e81eb4beb1a2f42.

Las117paginas reconstruyen exactamente cada extraction_json.text y su hash. Es verificacion de transporte/lectura de versiones ya extraidas, NO nuevo cotejo juridico contra fuentes originales. Tiempo loopback de una corrida, no SLA ni benchmark10x. La allowlist de este ensayo admite solo esos pares UID/version y no representa permisos humanos.

Candidato SHA256 antes y despues:375bc549ddaac619bfdba89d0f4cc162c8c6c6575516287e9d553d9e8cf13ed9. Listener cerrado y thread terminado. No hubo SSH a la VM ni llamada de despliegue, no se modifico la base viva ni se certifico nuevamente su estado operativo. servidor.py permanece igual a la base de PR8.

## Coverage y errores propios

La primera llamada python -m trace descubrio CERO tests y mostro porcentajes de importacion. Se descarto: exit0 no era medicion de tests. Una segunda pasada no trazaba imports y subcontaba; la definitiva traza descubrimiento y threads. El reporte final dice84lineas ejecutables,100% en exact_http.py; NO cobertura de ramas, concurrencia o producto completo. version_text.py82% dentro de este banco nuevo; sus tests propios corrieron aparte. El generador inicial de archivos tambien introdujo signos +; se detecto con compile antes de transferir y se materializo codigo limpio, cuyos hashes publicados coinciden.

Comando de coverage definitivo, desde raiz del checkout:
```sh
python3 -c 'import trace,threading,unittest; t=trace.Trace(count=True,trace=False,ignoredirs=["/usr/local/lib/python3.12"]); suite=t.runfunc(unittest.defaultTestLoader.discover,"tests",pattern="test_exact_http.py"); assert suite.countTestCases()==15; threading.settrace(t.globaltrace); result=t.runfunc(unittest.TextTestRunner(verbosity=2).run,suite); threading.settrace(None); t.results().write_results(show_missing=True,summary=True,coverdir="/workspace/corpus-exact-http/coverage-final"); assert result.wasSuccessful()'
```

## Seguridad, limites y siguiente dependencia real

SQL parametrizado en el reader; no comandos, fetch externo, HTML ejecutado, secretos, cookies o nuevos paquetes en el modulo. Headers de no-cache/JSON, errores redactados y decision obligatoria revisados. Workflow conserva pin SHA, pull_request, contents:read y persist-credentials:false. No se hizo una auditoria nueva de secretos historicos, Python CVEs, host, TLS o ingress; no afirmar que esos controles estan certificados.

Antes de montar publicamente siguen siendo necesarios identidad/sesion reales, AccessGrant por grupo/coleccion/vigencia, retirada desde fuente autorizada, TLS, limites de carga, logging operacional y las aprobaciones del plan. El callback es un contrato ejecutable con guard, no esas implementaciones. No hay atomicidad distribuida entre revocacion y una respuesta ya autorizada; se reconsulta cada pagina, no se puede retirar texto ya entregado al cliente. Cache-Control no borra copias previas. La base/ledger son confiables administrativamente; no se impone un tope al JSON almacenado. Se relee y hashea la extraccion completa por pagina, rendimiento10x no medido.

No se cambian busqueda, citas, exportacion, UI ni enlaces legacy. No se reconstruye la primera version legacy que solo tiene chunks, ni se inventa una URL historica, vigencia o revision juridica. Estas dependencias del alcance B02/D09/M03 siguen abiertas en el plan y en el PR; no quedan cerradas por este ensayo. Proximo paso: implementar/adaptar el proveedor real de acceso en la integracion aislada y probar sus casos del plan, sin desplegar ni fabricar actas.

## QA aplicable al modulo aislado, no al producto

TITAN FULL por HTTP/CI. Criterios: completitud14/15 (exact_http.py completo; host real fuera de alcance), ejecutabilidad15/15 (compile y HTTP de commit publicado), seguridad13/15 (guard/mutante/errores y DB read-only; no auditoria de host), testing14/15 (15HTTP,mutantes,3reales,coverage de lineas; no carga/concurrencia), arquitectura9/10 (modulo desacoplado,sin cambios legacy;10x no medido), documentacion9/10 (contrato/comandos/limites aqui y docstrings; autenticacion real pendiente), mejoras4/5 (scope de URL, unidad de offset,no-store y errores estables), proceso4/5 (evidencia cruda y CI; review externa no emitida). Total82/90=91/100. DevOps despliegue10puntos N/A porque no se autoriza ni entrega despliegue; CI si esta implementado y medido. NO aprobacion de merge, piloto o produccion.

Roles ejercidos: Architect(definio modulo/contrato), Builder(implementacion), Security(frontera fail-closed), Tester(HTTP/mutantes/copy), QA(lectura publicada y limites). No ejecutores externos inventados ni ordenes enviadas a otro agente.

## Evidencia cruda de corridas validas, transporte sin perdida

JSON28706bytes, SHA25612b4d9b3f60086b0e6d502bd1731445d65a0d001059d76486249443ad4c6ab1b. Contiene stdout/stderr completos de regresion, mutantes y comandos del commit publicado, resultados de lectura real, hashes y log final de coverage. La salida de porcentajes de la primera corrida sin tests se descarta explicitamente; solo se conserva su stderr con NO TESTS RAN, no se la etiqueta evidencia valida. El objeto coverage_command es descripcion; el comando literal reproducible esta arriba. Logs no recortados dentro de cada corrida valida; unittest limita su propio diff de assertion y ese mensaje se conserva verbatim.

Decodificar el unico bloque base64 de este archivo con base64.b64decode y zlib.decompress, verificar longitud/hash y json.loads. El veredicto anterior es interpretacion separada.

```base64
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
```
