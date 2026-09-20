# SOL y Astra revisados: reparar el contrato, después implementar búsqueda protegida

19-sep-2026 ART, pedido «revisa las auditoria de sol y de astra auditor y trabaja con el resto». Rol: revisión y corrección documental propia. No atribuyo independencia personal a mi trabajo ni tomo el pedido como permiso de merge/despliegue. Main inicial06bcfe22d8c1b8ea39cb8ffb60384887cc8f3f62. PR19 fuente31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05.

## Qué tomé de cada auditor y qué no repetí

[SOL PR8-11](https://github.com/gatehot59-star/corpus-legal-tarija/blob/06bcfe22d8c1b8ea39cb8ffb60384887cc8f3f62/docs/auditorias/2026-09-17-22-sol-pr8-pr11.md): lectura exacta, permisos y reparos del escritor probados entonces; marca isolated_test no cortaba lecturas emitidas en PR11. Leí el __call__ actual de isolated_login.py líneas93-114: consulta la marca antes de despachar. Ese reparo histórico no se vuelve a presentar como fallo actual. No reejecuté sus63tests ni su instrumento histórico.

[Astra14](https://github.com/gatehot59-star/corpus-legal-tarija/blob/06bcfe22d8c1b8ea39cb8ffb60384887cc8f3f62/docs/auditorias/2026-09-19-14-astra-brain-pr18-pr19.md): no nuevos reparos en lo probado de PR18/19; confirma el control Unicode y las denegaciones del guardado. Decodifiqué su evidencia estrictamente:29465bytes SHA2564b7d0d05dfa4637c61344aa18cbcd0e477b331d4ac322bd15b4eb62269c9c871. Custodia confirmada; resultados experimentales históricos, no corrida propia nueva. El autor declara haber construido el spike original: no lo llamo auditoría independiente total de autenticación.

[Astra20](https://github.com/gatehot59-star/corpus-legal-tarija/blob/06bcfe22d8c1b8ea39cb8ffb60384887cc8f3f62/docs/auditorias/2026-09-19-20-selected-docs-audit.md): revisa informes históricos de Astra y OPUS, no el endpoint nuevo. Su reparo del contador OPUS y recortes es deuda del instrumento, no bloqueo demostrado de búsqueda. No corregí ni publiqué el banco ajeno en su nombre. No llamo SOL a OPUS ni atribuyo a SOL la revisión19: esta se declara autocrítica del autor del contrato.

[Revisión19](https://github.com/gatehot59-star/corpus-legal-tarija/blob/06bcfe22d8c1b8ea39cb8ffb60384887cc8f3f62/docs/auditorias/2026-09-19-19-search-contract-review.md): un conflicto HEAD/JSON, dos riesgos de reutilizar respuestas y una aclaración de frontera. Evidencia remota zlib+base644955bytes SHA2569240e241d0bb94189248b1e6477cbf81b46b35877eab34e795322f79beb72ece, recuperada/decodificada ahora. No endpoint nuevo implementado aún.

## Trabajo aplicado

Enmendé EN EL MISMO ARCHIVO `docs/agents/respuestas/2026-09-19-18-protected-search-contract.md`, sin tocar código ni abrir otra especificación paralela:

1. HEAD no lleva cuerpo, aun si el rechazo llega de un guard anterior; conserva precedencia de status y omite Content-Length/Transfer-Encoding. Prueba futura sobre bytes de red, no el accessor HEAD del cliente.
2. Elegí serialización/envoltura exclusiva de la ruta de búsqueda en los dos archivos nuevos ya previstos. Cubre errores de aislamiento y transporte antes de dispatch; normaliza headers elegidos sin editar helpers core ni rutas antiguas.
3.405 de búsqueda anuncia Allow:GET; login/logout mantienen POST. No convertir un rechazo403/503 previo en405.
4. Aclaré815bytes como máximo testigo de gramática válido;2048 inválido produce400 y2049 produce414, bajo guards/método/body válidos. El límite grueso2048 no promete una entrada válida de ese tamaño.
5. Agregué aceptación negativa de HEAD y cabeceras. Si cubrir las rutas tempranas exige tocar core, se revisa el alcance antes de hacerlo.

Decisión de diseño, no certificado de implementación. Semántica de permisos, límites de q/documentos/respuesta, sesión/grant y versión fijada permanecen. La demo fija, autenticación, política, lectores y workflow no cambiaron.

## Medición propia acotada y salida completa

Archive nuevo PR19, import de IsolatedLoginApp desde sistema/api. Llamadas directas `reply(start_response,status,{error:code})`, capturando status,headers y todos los bytes del iterable. Sin socket/DB/listener/token. Esperado: reproducir las salidas del helper histórico, no demostrar todavía un defecto en un buscador inexistente. Python supervisor exit0, stderr vacío.

```json
{"requested":403,"status":"403 Forbidden","headers":[["Content-Type","application/json"],["Cache-Control","no-store"],["X-Content-Type-Options","nosniff"],["Content-Length","36"]],"body":"{\"error\": \"ISOLATED_LOGIN_DISABLED\"}"}
{"requested":503,"status":"503 Service Unavailable","headers":[["Content-Type","application/json"],["Cache-Control","no-store"],["X-Content-Type-Options","nosniff"],["Content-Length","34"]],"body":"{\"error\": \"ISOLATION_UNAVAILABLE\"}"}
{"requested":405,"status":"405 Method Not Allowed","headers":[["Content-Type","application/json"],["Cache-Control","no-store"],["X-Content-Type-Options","nosniff"],["Content-Length","31"],["Allow","POST"]],"body":"{\"error\": \"METHOD_NOT_ALLOWED\"}"}
```

La salida confirma G1/G2. No exigí al helper de login comportarse como búsqueda: la corrección está en la composición propuesta, no en acusar una vulnerabilidad del helper. Para repetir, recuperar el archive31dff1ed, importar esa clase y capturar sus tres llamadas estáticas; no necesita fixtures ni credenciales. RFC9110§9.3.2 y el extracto completo conservado en evidencia19 son el oráculo HEAD. No se reconsultó RFC en red ni se midió HEAD HTTP en este turno.

## Siguiente incremento, requiere confirmar el lote

Se conserva el [alcance16](https://github.com/gatehot59-star/corpus-legal-tarija/blob/06bcfe22d8c1b8ea39cb8ffb60384887cc8f3f62/docs/agents/respuestas/2026-09-19-16-protected-integration-file-scope.md):9archivos nuevos y1workflow modificado, rama separada desde PR19, PR apilado y Doc público. Flujo sintético entrar → buscar solo lo autorizado → leer versión explícita → guardar referencia → salir. Dos identidades y dos colecciones, sin exposición de documentos denegados en conteos/orden/snippets/páginas. Conservar todas las suites anteriores y mutantes causales; no cuentas/datos reales, merge o despliegue.

La corrección de este contrato y este recibo NO son parte de los diez archivos de implementación ni significan que ese lote se ejecutó. El pedido general de avanzar no sustituye la confirmación de un lote de10archivos. No creo código antes de esa confirmación.

## Cierre y límites

Git: contrato18 enmendado y recibo21, solo2archivos documentales. Doc18 se actualiza para que no siga ordenando el comportamiento rechazado; Doc público del recibo y Nexus conservan continuidad. Readback y hashes se verifican antes de informar terminado el cierre documental.

GateI: fuente actual y helper real identificados; las tres llamadas coinciden. Endpoint/baseline/mutantes nuevos N/A a esta enmienda. GateII: histórico vs actual, SOL vs OPUS vs Astra y método directo vs HTTP separados. GateIII: cierre documental Git/Doc/Nexus, no producto ni permiso de integración. NO MEDIDO: implementación nueva, HEAD en red, búsqueda/privacidad extremo a extremo, concurrencia, piloto humano, TLS/carga/validez legal. No puntuación para compensar faltantes.

--- METODO TITAN ---
Modo: revisión documental con comprobación directa de helper y enmienda de contrato. Máquina:brain-env. No cambios delicados de producto/workflow, ni PR merge/despliegue. Implementación futura FULL con lote explícito. Auditoría no exhaustiva y revisión externa de la enmienda pendiente; no autoaprobación de producto.
