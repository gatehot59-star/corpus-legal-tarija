# Astra: PR16 bloquea la copia vieja; no equivale a restablecer el servicio

19-sep-2026 ART. Encargo de Abraham: buscar el trabajo nuevo dejado para auditar y ejecutarlo. Auditoría de producto e instrumento, no implementación. Revisor, verificador y control final son funciones de un mismo operador, no tres revisores externos.

## Sujeto y descubrimiento

Repositorio gatehot59-star/corpus-legal-tarija. Último cierre propio: informe08, commit c7b6ed79640c37547607332e9a49276543696907. Recuperé Nexus46 a48, git y el Doc del PR16; Nexus todavía no reflejaba los cambios posteriores de recuperación, por lo que no lo tomé como inventario completo.

Main inicial: `9aebfac99998d27c4f76c470813dedebea8924f4`. PR14 y PR15 figuran merged:true en consultas específicas autenticadas; integración de demo `9913d8dd5074d6aedd0d261c42caea6480e794fe`. Hasta el main inicial, el delta posterior a esa integración fuera de docs está vacío. El bloqueo de composición del informe08 ya no es el siguiente trabajo: existe un lanzador explícito y su CI.

Sujeto nuevo: [PR16](https://github.com/gatehot59-star/corpus-legal-tarija/pull/16), abierto, no mergeado, head `67d0251ac2d768065cf75b976cd5a72580d34bdd`, base `3d45e774ce1c0c126a4e63aef31c256d448f74b8`. Leí completos sus cuatro archivos: demo_restore.py, test_demo_restore.py, RECUPERACION-DEMO.md y workflow. Productor: restore() y su CLI; consumidor: demo_aislada.py serve que monta IsolatedSessionApp. No se sustituye por servidor.py histórico ni por el servicio vivo.

Contexto vigente leído: enmienda operativa v2, recibo09 sobre rollback de autorizaciones y recibo10 de implementación. La revisión previa de Astra08 es antecedente, no evidencia nueva de este PR. PR1 queda fuera.

## Veredicto acotado

**CONFIRMADO:** para un fixture sintético frío válido, PR16 copia a un destino nuevo, conserva candidato/origen/estado actual y deja la salida no servible. La barrera de archivo y la ausencia del marcador SQL impiden arrancar por separado. Purga sesiones y apaga colecciones. Conserva el estado histórico declarado sin presentarlo como vigente.

**CONFIRMADO:** un backup viejo copiado sin cuarentena vuelve a permitir el mismo token revocado y un login nuevo. El positivo previo observa logout200, sesión revocada403 y otra identidad200; la retirada posterior devuelve403. La copia vieja permite200. Se replica el riesgo operativo que motivó el PR, no un acceso remoto no autorizado ni pérdida del texto almacenado.

**Sin defecto nuevo del restaurador en lo probado.** Hay un reparo heredado en la higiene de conexiones de una suite antigua, detallado abajo; no se lo atribuye a PR16. No se modificó producto para acomodar los tests.

**NO MEDIDO:** reconciliación y reapertura segura, backup caliente, caída abrupta/corte de energía, atomicidad duradera del par, carreras exhaustivas o adversario con el mismo UID/root, offsite/RPO/RTO, servicio real/TLS, vigencia jurídica y piloto. El flag source-stopped declara la condición: no la mide ni adquiere un lock. M03/F05 permanecen abiertos en esos alcances.

## Instrumento propio y resultados

Se archivó el head exacto en scratch nuevo de brain-env, alcanzado por Gateway build. Medición actual: Python3.12.14, SQLite3.46.1,2CPU, FTS5 funcional y125767004160bytes libres al inicio. No se lanzó Actions, GPU ni VM para esta auditoría. Se usaron temporales propios y HTTP literal127.0.0.1.

`probe.py` no importa helpers del banco del autor: maneja sus subprocesses, HTTP y SQL. El texto esperado se escribe aparte de las constantes del launcher: Unicode, carácter combinante y CRLF; páginas de7caracteres. El init real produce el fixture, pero no produce el esperado del verificador. Para la fidelidad del restore, el oráculo son los bytes previos de las bases frías y filas SQL observadas antes de la función auditada. Los valores históricos de presupuesto se alteran mediante SQL propio.

Baseline:89aserciones,0fallos, exit0. Repetición completa en scratch nuevo:89,0,exit0. No son178tests independientes: se repitió el mismo banco para controlar estado y limpieza.

Casos principales:

1. CLI init, login de dos identidades, paginación exacta, cierre del primer proceso y nuevo proceso con distinto PID. Logout persiste; la otra identidad sobrevive. Retirada posterior rechaza.
2. Backup frío anterior: control ingenuo permite el token viejo y un login nuevo. El CLI de PR16 restaura el mismo backup a otro directorio con exit0 y status quarantined, nunca serve_authorized.
3. SQL independiente: cero sesiones, cero marcador, colecciones0. Filas de grants, retiradas, password verifiers, reloj, presupuesto, usuarios y memberships conservadas; los valores de credenciales se comparan sólo en memoria, no se publican.
4. Candidato byte-idéntico; dos archivos del origen y estado actual preservados. Manifiesto en disco igual a stdout; hashes recalculados, directorio0700 y archivos0600. Conexiones escritoras cerradas antes de las comparaciones de bytes; no checkpoint sobre datos ajenos.
5. Servir con ambas barreras: exit2 sin ready. En copias exclusivas del auditor, quitar sólo manifiesto sigue dando2; reponer sólo store viejo conservando manifiesto también da2. No son instrucciones de reapertura.
6. Fallo de escritura durante copia de sessions.db: manifiesto incomplete ya presente y salida rechazada. Fallo SQL real inyectado por trigger antes de apagar colecciones, después de borrar marcador/sesiones: transacción revierte ambos borrados; el manifiesto mantiene bloqueado el destino completo. Fuente intacta.
7. Flags ausentes/parciales, opción reopen inexistente y destino existente se rechazan. El centinela del destino anterior permanece exacto.

El trigger es un instrumento de fallo en fixture propio, no una propiedad prometida contra bases hostiles. Las inspecciones SQL posteriores conservan filas históricas no sensibles; las imágenes privadas no se publican.

## El banco también pudo dar rojo

Dos mutaciones de una línea, en copias del producto fuera de ramas de trabajo, ejecutadas con exactamente el mismo probe:

- Omitir DELETE de access_sessions: baseline satisface sessions_purged; mutante observa2en lugar de0 y falla esa asercción. La postcondición del propio restaurador también rechaza la operación, por lo que exit0 no se afirma. Se conservan las seis aserciones fallidas, incluyendo consecuencias del rollback.
- Omitir escritura inicial del manifiesto: baseline satisface partial_first_barrier; mutante no tiene el archivo ante fallo de copia y falla ese criterio. También falla file_only: con store viejo y sin esa barrera el launcher produce ready. Se guardan las ocho aserciones fallidas y las capturas completas.

Ambos probes mutantes salen1. No se usan solamente sus exit codes para declarar detección. En los intentos negativos que arrancaron indebidamente, el límite del supervisor terminó los procesos propios; sus ready y timeouts quedan registrados, no ocultos como rechazo exitoso. No se lanzaron corridas rojas en GitHub.

## Suite del autor y CI

Ejecuté textualmente los tres bloques run del YAML congelado, incluyendo py_compile y timeouts:21SOL+15HTTP+15permisos+18guards+10sesiones+18demo+14restore=111tests, todos exit0. Los12login heredados no se cuentan otra vez. Capturas completas en commands; los tres pasos tardaron51.642,32.308y28.624s. El follow-up HTTP de15tests es repetición diagnóstica, no amplía el conteo.

El diff del workflow agrega sólo tres paths y el paso de restore: no cambia bloques anteriores, pin de checkout, contents:read, persist-credentials:false ni timeout5min. API autenticada check_runs: job105821331184, completed/success, [corrida previa](https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35414843978/job/105821331184). No hice una nueva corrida remota ni obtuve stdout remoto; el111es conteo local. get_reviews devolvió[]: silencio no es aprobación.

El archivo de evidencia del autor en9aebfac se decodificó:40613bytes, SHA25605520c6fd2f6cbede8688acff7837e606e352c544f05079f19817455d99d1e35. Eso comprueba integridad de ese archivo, no convierte su relato en mi medición. No recalculé su porcentaje de cobertura de líneas ni lo usé como veredicto de seguridad.

## Reparo de instrumento heredado: close no es commit

El observador de recursos retiene referencias y registra llamadas explícitas a close(). Control positivo:1conexión abierta/1cerrada; control negativo deliberado:1/0, detectado. Por diseño, esto mide cierre explícito sin depender del recolector; no demuestra una fuga productiva después de terminar el proceso.

Los cuatro probes propios cierran sus29conexiones de proceso principal; todos sus subprocesos observados tienen0sin cerrar. Baseline y repetición usan15hijos cada uno. Escaneo final de los60hijos de las cuatro corridas:ninguno presente;19puertos observados:ninguno abierto.

En la regresión antigua aparecieron registros de conexiones sin close explícito. Para atribuir sin adivinar, reejecuté sólo test_exact_http.py en scratch instrumentado con argv y stack por conexión:15tests pasan,41conexiones,24cierres,17sin cierre explícito. El stack apunta a fixtures, incluyendo setUp línea32; código idéntico entre la base y PR16 (diff vacío). Otros cuatro procesos de la regresión antigua también señalaron2,63,69y35; no se les atribuye un caller específico sin el mismo diagnóstico.

Clasificación: deuda heredada de higiene/reproducibilidad del banco, prioridad baja frente a reabrir accesos; no defecto introducido por restaurador, ni evidencia de pérdida de datos o fuga de producción. Corrección propuesta, no realizada: closing/finally en esos fixtures y repetir misma suite con contador0. Dueño propuesto: mantenimiento del banco, sin asignación ni issue creado. No invalida las observaciones propias del restore, hechas con cierre explícito y repetición fresca. Tampoco autoriza describir toda la suite heredada como libre de recursos abiertos.

## Custodia y reproducción exacta

Evidencia íntegra de esta captura: JSON420667bytes, SHA256 `e4e3c3f266c91d628fdcb2be55a319aebd80700c7b42a408d71273e128f5b273`. Contiene fuentes de instrumentos ejecutados, fuentes congeladas relevantes, comandos, stdout/stderr sin recortes, respuestas HTTP, mutaciones exactas, oráculos/aserciones, snapshots lógicos no sensibles, recursos, contexto y diagnóstico heredado.

Exclusiones declaradas: Authorization, valores de tokens sintéticos, cuerpos con contraseñas, digests individuales de credenciales e imágenes SQLite. Tokens son redactados al capturar. No hay cuentas ni secretos reales. Las contraseñas públicas constantes del fixture en el código siguen siendo datos ficticios explícitos.

Transporte xz+base64 en TRES VERSIONES INMUTABLES del MISMO archivo `docs/auditorias/2026-09-19-01-astra-pr16-cuarentena/evidence.xz.b64`. Es transporte por historial, no tres archivos ni tres evidencias distintas. **El archivo en HEAD solo contiene el bloque final: NO alcanza para decodificar.** Recuperar en este orden:

1. `bc3a4c51b78f1b4210cf9ef3d613bc005caf9398`:11000bytes, SHA256e529b2f961c65d6ee463f0389888d88908a67ecd8b39b3f4c811f2b8910009eb.
2. `05e450e4ab28353434fea66013d644cf2ce0cffe`:11000bytes, SHA25654253b561a8880b15386236aa2ba08d30997bbdce133154df1febc4ae077c86d.
3. `90acb23b681a75beb5ad37961a8d8fa66483acb8`:11296bytes, SHA2569aa483610c91f5f2d6f47116766bff27deb3d7f9dc546b60d3fdfc9ce3cb9896.

```python
import subprocess, base64, lzma, hashlib, json
path = 'docs/auditorias/2026-09-19-01-astra-pr16-cuarentena/evidence.xz.b64'
revisions = ['bc3a4c51b78f1b4210cf9ef3d613bc005caf9398', '05e450e4ab28353434fea66013d644cf2ce0cffe', '90acb23b681a75beb5ad37961a8d8fa66483acb8']
parts = [subprocess.check_output(['git','show',s+':'+path]) for s in revisions]
assert list(map(len, parts)) == [11000,11000,11296]
raw = lzma.decompress(base64.b64decode(b''.join(parts), validate=True))
assert len(raw) == 420667
assert hashlib.sha256(raw).hexdigest() == 'e4e3c3f266c91d628fdcb2be55a319aebd80700c7b42a408d71273e128f5b273'
evidence = json.loads(raw)
```

Esta reconstrucción ya se ejecutó tras fetch remoto:payload idéntico, JSON byte por byte idéntico al original, tres commits ancestros de main. Fuentes probe.py, supervisor.py y postlude.py están dentro del JSON. Para repetir: extraer instruments['probe.py'], ejecutar `python3 probe.py REPO_CONGELADO DIRECTORIO_NUEVO`; el directorio no debe existir. El supervisor contiene la ejecución exacta y los falsadores. No ejecutar el supervisor sin adaptar su puntero local: documenta esta corrida, no es instalador de producto.

Preparación propia: un comando de observación de metadata tuvo SyntaxError por paréntesis y no ejecutó pruebas; no se relanzó el supervisor. La representación del editor con signos+ se normalizó y compiló antes de transferir; longitud/SHA verificados al recibir. Ninguna anomalía de transporte se imputó a Corpus.

## Gates antes de firmar

Gate I PASA para el banco nuevo: sujeto exacto, oráculos externos al restore, baseline positivo, dos falsadores de propiedades, cierre explícito, repetición fresca y captura completa declarada. La higiene de todas las suites heredadas NO pasa como afirmación global; se acota y reporta arriba. Cobertura jurídica, producción y crash: NO MEDIDO, no N/A usado para vender seguridad.

Gate II PASA en este alcance: cada afirmación seleccionada tiene resultado/límite; separación candidato/instrumento/entorno; controles negativos preservados; reproducción y prioridad; permisos respetados. No nota numérica ni ranking entre modelos.

Gate III EN FINALIZACION al publicar este informe: evidencia remota reconstruida y verificada; faltan readback de este informe, Doc público y registro propio en Nexus. El cierre se agrega debajo después de comprobarlos. No presentar este estado intermedio como entrega completa.

Siguiente decisión útil: revisión/integración autorizada del PR16, no implementación adicional asumida. Después, si se encarga reapertura, exige fuente confiable del estado actual de permisos/retiradas; una copia vieja no puede inventar los eventos posteriores. Ningún merge, despliegue, modificación de bases vivas, cuenta real, issue o mensaje fue realizado por esta auditoría.
