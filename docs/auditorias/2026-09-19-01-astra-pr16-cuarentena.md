# Astra PR16: cierre e índice de la auditoría de cuarentena

19-sep-2026 ART. **Gate III COMPLETA:** evidencia publicada y reconstruida byte por byte; informe experimental recuperado de git y presente en main; Doc público creado y leído en Space validado; reporte49 propio en Nexus insertado y consultado de vuelta a05:50:56UTC. Esta revisión agrega el cierre administrativo mediante un índice, sin sustituir ni recortar la captura experimental.

## Informe experimental íntegro, preservado

[2026-09-19-01-astra-pr16-cuarentena.md, versión experimental completa](https://github.com/gatehot59-star/corpus-legal-tarija/blob/7e89be2a0b03ef429dd32917ecb5189744ffc0e4/docs/auditorias/2026-09-19-01-astra-pr16-cuarentena.md).

Commit `7e89be2a0b03ef429dd32917ecb5189744ffc0e4`,14302bytes, SHA256 `4b1b190298cea0bdd862d1f8cf6dee5470547de5cb9efb42f678d1cde0e7ab81`. Readback por raw remoto y objeto git: iguales; commit ancestro de main. Su última sección describía la fase administrativa todavía pendiente al escribirlo; ese estado intermedio queda superado por este cierre, no por una nueva corrida del producto. Sus procedimientos, resultados adversos y límites permanecen íntegros en el enlace permanente.

[Doc público: Astra PR16, la recuperación queda bloqueada; reparo heredado en el banco de pruebas](https://app.clickup.com/90171457413/docs/2kza6fw5-13277), página verificada https://app.clickup.com/90171457413/docs/2kza6fw5-13277/2kza6fw5-15537, parent Space público validado90176846840. Continuidad: Nexus reportes49, agente astra-auditor, turno2026-09-19-01-pr16-cuarentena. No se marcaron trabajos ajenos terminados ni mensajes leídos.

## Sujeto y estado

Encargo: buscar qué trabajo nuevo quedó para auditar. Recuperados Nexus46-48, git y Docs; main inicial `9aebfac99998d27c4f76c470813dedebea8924f4`. PR14 y PR15 ya estaban integrados, confirmado por merged:true en consultas específicas. El hueco de composición del cierre anterior está resuelto en la demo; no se repite como bloqueo actual.

Auditoría de [PR16](https://github.com/gatehot59-star/corpus-legal-tarija/pull/16), head `67d0251ac2d768065cf75b976cd5a72580d34bdd`, base `3d45e774ce1c0c126a4e63aef31c256d448f74b8`. Cuatro archivos leídos completos. Productor real: demo_restore.py; consumidor real: demo_aislada.py serve e IsolatedSessionApp. PR16 seguía abierto/sin merge; su rama no cambió al reconsultarla. La publicación propia modifica sólo documentación/evidencia. No se infiere nada del servidor vivo.

Funciones: revisor, verificador y control final del mismo operador; no tres revisores independientes ni ranking de modelos. Brain-env real vía Gateway build: Python3.12.14,SQLite3.46.1,2CPU,FTS5 funcional; recursos aislados propios. No runtime nuevo de Actions/GPU/VM.

## Veredicto y pruebas

**CONFIRMADO:** un backup viejo copiado ingenuamente reabre el token revocado y permite un login nuevo. **CONFIRMADO:** PR16 preserva origen, candidato y estado actual, copia a destino nuevo y deja la salida bloqueada, con marcador ausente, sesiones purgadas, colecciones apagadas y manifiesto no autorizado. Los valores históricos se conservan sin declararlos vigentes.

Banco propio sin helpers del autor, texto Unicode/CRLF fijado aparte, bytes fríos y SQL como oráculos:89aserciones/0fallos, repetidas en scratch nuevo89/0. No son178tests independientes. CLI y HTTP reales con procesos distintos; retirada, logout, otra identidad, control ingenuo, hashes, permisos0700/0600, dos barreras separadas, escritura parcial y aborto de transacción por trigger. El fallo SQL ocurre después de los borrados y comprueba rollback mientras el manifiesto bloquea el destino. Los intentos inválidos no sobrescriben fuente ni destino existente.

Falsadores propios sobre copias: omitir purga rompe sessions_purged (2contra0); omitir primera barrera rompe partial_first_barrier y permite ready en el contracaso file_only. Mismo banco y positivo pertinente. Se conservan todos los fallos:6y8respectivamente, junto con los timeouts y terminaciones controladas de los servidores mutantes. No bastó con mirar exit1.

Suite del autor: tres bloques YAML exactos,111tests exit0, sin duplicar12login heredados. CI previo consultado mediante API: job105821331184 completed/success; no se lanzó CI nuevo ni se obtuvo stdout remoto. No se recalculó el porcentaje de cobertura del autor ni se usa como certificado de seguridad.

**Sin defecto nuevo del restaurador en lo probado.** Reparo heredado del instrumento: test_exact_http.py pasa15tests pero el observador de cierre explícito registra41conexiones/24close/17sinclose, con stacks en fixtures, incluido setUp32. Archivo idéntico base/head; no introducido porPR16. Otros avisos de la regresión se preservan sin atribuirles un caller no diagnosticado. Observador retiene referencias: mide cierre explícito, no prueba fuga productiva después de finalizar el proceso. Propuesta no ejecutada: closing/finally y repetición con contador0.

El contador tiene positivo1/1y negativo deliberado1/0. Los cuatro probes nuevos cierran29/29conexiones de proceso principal y sus hijos observados no dejan conexiones sinclose. Escaneo propio:60hijos ausentes y19puertos cerrados. Deuda heredada no se oculta ni invalida por arrastre las mediciones nuevas con cierre y repetición.

## Evidencia íntegra y recuperación

JSON420667bytes, SHA256 `e4e3c3f266c91d628fdcb2be55a319aebd80700c7b42a408d71273e128f5b273`. Fuentes ejecutadas, comandos, stdout/stderr completos, HTTP, oráculos, mutaciones, snapshots lógicos no sensibles, recursos y contexto. Excluidos al capturar: Authorization, tokens sintéticos, cuerpos con contraseñas, digests individuales de credenciales e imágenes SQLite. No hubo datos/cuentas reales.

Transporte xz+base64 mediante tres versiones inmutables del MISMO archivo. HEAD contiene sólo el bloque final; hay que recuperar los tres, en este orden:

1. [Bloque1](https://github.com/gatehot59-star/corpus-legal-tarija/blob/bc3a4c51b78f1b4210cf9ef3d613bc005caf9398/docs/auditorias/2026-09-19-01-astra-pr16-cuarentena/evidence.xz.b64):11000bytes, SHA256e529b2f961c65d6ee463f0389888d88908a67ecd8b39b3f4c811f2b8910009eb.
2. [Bloque2](https://github.com/gatehot59-star/corpus-legal-tarija/blob/05e450e4ab28353434fea66013d644cf2ce0cffe/docs/auditorias/2026-09-19-01-astra-pr16-cuarentena/evidence.xz.b64):11000bytes, SHA25654253b561a8880b15386236aa2ba08d30997bbdce133154df1febc4ae077c86d.
3. [Bloque3](https://github.com/gatehot59-star/corpus-legal-tarija/blob/90acb23b681a75beb5ad37961a8d8fa66483acb8/docs/auditorias/2026-09-19-01-astra-pr16-cuarentena/evidence.xz.b64):11296bytes, SHA2569aa483610c91f5f2d6f47116766bff27deb3d7f9dc546b60d3fdfc9ce3cb9896.

```python
import subprocess,base64,lzma,hashlib,json
path='docs/auditorias/2026-09-19-01-astra-pr16-cuarentena/evidence.xz.b64'
revs=['bc3a4c51b78f1b4210cf9ef3d613bc005caf9398','05e450e4ab28353434fea66013d644cf2ce0cffe','90acb23b681a75beb5ad37961a8d8fa66483acb8']
parts=[subprocess.check_output(['git','show',s+':'+path]) for s in revs]
assert list(map(len,parts))==[11000,11000,11296]
raw=lzma.decompress(base64.b64decode(b''.join(parts),validate=True))
assert len(raw)==420667
assert hashlib.sha256(raw).hexdigest()=='e4e3c3f266c91d628fdcb2be55a319aebd80700c7b42a408d71273e128f5b273'
evidence=json.loads(raw)
```

Reconstrucción desde fetch remoto realizada:payload idéntico y JSON idéntico byte por byte al original; tres commits ancestros de main. El informe experimental contiene instrucciones para extraer probe.py y ejecutar contra revisión congelada en destino nuevo. No ejecutar ciegamente los supervisores que documentan punteros locales de esta corrida. Error propio declarado: un comando de observación tuvo SyntaxError de paréntesis, sin ejecutar pruebas ni relanzar el supervisor; transporte normalizado, compilado y verificado por longitud/SHA antes de ejecutar.

## Gates y lo que no se midió que importaba

Gate I PASA para el banco nuevo: sujeto/oráculo/baseline/falsadores/recursos/repetición/captura. La afirmación global de higiene de todas las suites heredadas NO PASA y queda separada. Gate II PASA: completitud acotada, causalidad, documentación, prioridad y permisos. Gate III COMPLETA: git recuperado, informe en main, Doc público leído y Nexus49 verificado. Sin promedio ni nota que tape un gate.

NO MEDIDO: reconciliación/reapertura segura, backup caliente, crash/apagón, atomicidad duradera del par, concurrencia exhaustiva, adversario mismo UID/root, offsite/RPO/RTO, TLS/servicio real, validez jurídica y piloto. source-stopped es declaración, no lock. M03/F05 siguen abiertos en esos alcances.

Siguiente decisión: revisión/integración autorizada dePR16; no merge implícito. Reabrir después requerirá estado vigente confiable de permisos/retiradas: un backup viejo no contiene los eventos posteriores. No hubo producto corregido, merge, despliegue, bases vivas, cuentas reales, issues, asignaciones ni mensajes. Los antecedentes01/03 locales, publicación ajena4.7MB y A/Bskills no quedan cerrados por esta entrega.
