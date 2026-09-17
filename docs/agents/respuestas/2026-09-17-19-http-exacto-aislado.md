# PR9: lector exacto conectado a HTTP aislado

17-sep-2026. [PR9](https://github.com/gatehot59-star/corpus-legal-tarija/pull/9), rama titan/exact-http-isolated sobre PR8. Codigo publicado y reejecutado:72a3563b13cda5f66104c6746e24c9e79ac4b615; base:cc8c33562a4adb9976db81478b8cac6f353152f8. Sin merge ni despliegue.

## Que cambia y donde estamos

El lector exacto de PR8 ya responde a peticiones HTTP reales en un ensayo aislado. Avance reversible de B02/integracion de B04 e I05; no cierra D09,M03 ni publicacion B08. No se cambio el buscador vivo, sus servicios, su base, credenciales o proxy. No hubo SSH a la VM ni se certifico de nuevo su estado operativo. Los listeners temporales terminaron.

## Arquitectura y contrato

- sistema/api/exact_http.py: WSGI opt-in, sin listener ni DB por defecto. Valida locator, llama a authorizer y abre SQLite mode=ro/query_only.
- sistema/api/version_text.py: adapter exacto de PR8 intacto.
- sistema/api/servidor.py: servidor legacy intacto, no se montan rutas nuevas en el.
- tests/test_exact_http.py:15tests con socket loopback real, SQLite y policy sinteticos.
- .github/workflows/clean-snapshot.yml: conserva checkout pinneado, contents:read, persist-credentials:false y tests previos; suma modulo/tests nuevos y timeout60s.

Sin paquetes externos nuevos. Python3.12.14 medido en brain-env. No se hizo nueva auditoria de CVEs de Python, secretos historicos, host o ingress.

Contrato: ExactReaderApp(db_path, authorize=None). authorize(environ,uid,version) es codigo confiable del host; solo True literal permite acceso. Debe autenticar y comprobar grant vigente, grupo, coleccion, version y retirada en CADA peticion. No se convierte un header X-User en identidad. Sin policy:403; policy rota:503. El fixture no implementa ni demuestra cuentas/grants piloto reales.

GET /api/v2/documento/{uid}/texto?version={sha256}&start=0&limit=2600. Version explicita desde primera pagina, UID ASCII alfanumerico/guion/guion bajo max200, hash64hex minuscula, start entero no negativo, limit1..10000. Query max2048 y tres claves unicas; duplicados, campos desconocidos y locators legacy rechazados. Descubrimiento autorizado de version actual queda fuera.

Flujo: HTTP -> locator validado -> policy para UID/version -> DB solo lectura -> read_version -> JSON con texto exacto, version, hash, next y procedencia. No fusiona chunks ni cae silenciosamente a otra version. La decision previa evita leer el documento para un acceso denegado.

Se elige modulo WSGI separado para no alterar el contrato consumido del handler legacy. El banco usa wsgiref en127.0.0.1:puerto efimero; no es un servidor recomendado para produccion. Sin montaje automatico. La base/directorio son administrados por host confiable; no resistencia universal a reemplazos maliciosos por el mismo usuario local.

Respuesta conserva contrato PR8 y agrega offset_unit=unicode_code_points y source_url_scope=current_document. La URL procede de la fila estable actual, NO es historica por version. authority=secondary, oficial=false y legal_validity=NOT_MEASURED. Todas las respuestas no-store/nosniff, sin CORS abierto ni traceback.

Errores:400 locator;403 acceso;404 ruta/documento;405 metodo;409 version ausente/integridad/procedencia;416 offset;503 policy/DB;500 inesperado redactado. SQL parametrizado en read_version; sin shell, fetch externo, HTML ejecutado, cookies o secretos nuevos.

## Mediciones y limites del instrumento

En codigo publicado: py_compile y comandos del workflow,21tests previos en7.626s y15HTTP en1.434s, exit0. SHA de modulo/tests coincide byte por byte con lo ensayado; servidor.py y version_text.py tambien coinciden con la base. Logs completos en payload final.

El caso SOL atraviesa HTTP en paginas de401caracteres:150frases/6906caracteres exactos, hash y DB sintetica antes/despues iguales. Negativos:identidad ausente, headers falsos, policy ausente/rota/truthy, otro UID/version, retirada entre paginas, version desconocida, entradas malformadas y ledger alterado.

Dos mutantes locales dan exit1:omitir guard de acceso y quitar un caracter de cada pagina. Las assertion failures completas estan preservadas. El instrumento podia dar rojo por las dos afirmaciones principales. No se afirma haber ejecutado esos mutantes en GitHub CI.

Tres versiones reales de la copia candidata existente recorrieron117paginas HTTP de10000caracteres:Familia195893/20paginas/0.133s;Comercio693914/70/1.325s;CPE263357/27/0.344s. Texto completo igual al ledger y a sus hashes de version. Los hashes exactos y resultados estan en payload. NO es nuevo cotejo juridico contra fuentes originales ni benchmark10x/SLA. La allowlist del ensayo solo admite esos tres pares UID/version y no representa aprobacion humana.

Candidato SHA256 antes/despues:375bc549ddaac619bfdba89d0f4cc162c8c6c6575516287e9d553d9e8cf13ed9. listener_stopped=true. No DB viva leida/escrita en este turno.

[CI stable_identity](https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35279540112/job/105398041954):completed/success,21:57:59Z a21:58:04Z. CI corre bancos sinteticos, no DB real. Copilot solicitado; get_reviews=[] al consultar, no aprobacion.

Coverage final stdlib trace:84lineas ejecutables,100% exact_http.py. Es cobertura de lineas, no ramas/carga/concurrencia; version_text.py82% en este banco nuevo, tests propios aparte. Se trazo el descubrimiento y los threads. La primera medicion descubrio cero tests y se descarto, no se uso su aparente100%. La segunda omitio imports y subconto. Comando final desde raiz:

```sh
python3 -c 'import trace,threading,unittest; t=trace.Trace(count=True,trace=False,ignoredirs=["/usr/local/lib/python3.12"]); suite=t.runfunc(unittest.defaultTestLoader.discover,"tests",pattern="test_exact_http.py"); assert suite.countTestCases()==15; threading.settrace(t.globaltrace); result=t.runfunc(unittest.TextTestRunner(verbosity=2).run,suite); threading.settrace(None); t.results().write_results(show_missing=True,summary=True,coverdir="/workspace/corpus-exact-http/coverage-final"); assert result.wasSuccessful()'
```

## Lo que falta, sin disfrazarlo de implementado

Antes de montar publicamente:identidad/sesion, AccessGrant real por grupo/coleccion/vigencia, retirada desde fuente autorizada,TLS,limites de carga,logging operativo y aprobaciones del plan. El callback es un contrato con guard ejecutado, no esas implementaciones. No atomicidad distribuida entre revocacion y respuesta ya autorizada:se reconsulta por pagina, no se borra lo ya entregado. no-store no retira copias previas.

Relee/hashea JSON completo por pagina; tope al ledger y rendimiento10x no medidos. No cambia busqueda,citas,exportacion,UI o enlaces legacy. No reconstruye la primera version legacy almacenada solo en chunks ni inventa URL historica/vigencia/revision juridica. Estas dependencias B02/D09/M03 siguen abiertas en el plan y en PR9. Siguiente paso real:proveedor de acceso de la integracion aislada y pruebas de grants del plan, sin despliegue ni actas inventadas.

## TITAN QA del modulo aislado

82/90=91/100;NO aprobacion de merge,piloto o produccion. DevOps despliegue10puntos N/A,no autorizado;CI si implementado y medido. Completitud14/15 (modulo completo,host fuera de alcance);ejecutabilidad15/15 (compile/HTTP publicado);seguridad13/15 (guard/mutante/errores/readonly,no auditoria host);testing14/15 (15HTTP,mutantes,3reales,coverage lineas,no carga);arquitectura9/10 (desacoplado,legacy intacto,10x no medido);documentacion9/10 (contrato/comandos/limites,auth real pendiente);mejoras4/5 (scope URL,unidad offset,no-store,errores estables);proceso4/5 (crudos/CI,review no emitida).

Roles:Architect,Builder,Security,Tester,QA. No ejecutores externos ni ordenes inventados. Errores propios:signos+ del generador detectados por compile antes de pruebas;coverage inicial sin tests descartado;primer transporte de evidencia danado y sustituido por este payload pequeno, sin modificar codigo. Este recibo final acota las afirmaciones a las corridas crudas incluidas;no presenta logs resumidos como completos.

## Evidencia cruda, separada del veredicto

JSON10909bytes, SHA256a17b20c4ed50fd92c6a3cf9e7230d3ac0c1e3d24726a16ea419eb874341d3910. zlib+base64, sin perdida. Incluye comando publicado/stdout/stderr completos de21+15tests, logs completos de2mutantes, coverage final, resultados reales, hashes y runtime. Los diffs que unittest limita por defecto se conservan tal como los emitio. Decodificar el unico bloque base64 con base64.b64decode y zlib.decompress; comprobar hash, longitud y json.loads.

```base64
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
```
