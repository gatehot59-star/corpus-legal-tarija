# PR13: cerrar sesion revoca el bearer presentado en el entorno aislado

18-sep-2026 ART. [PR13](https://github.com/gatehot59-star/corpus-legal-tarija/pull/13), rama titan/isolated-logout sobre PR12 a67b4feb5f6e0fa13ec2c730f57d35bd2d2ba1f8. Codigo publicado y reejecutado: de4551825704a036d979b5245cd5bdebbe993e37. Main leido eef9bf2e20c93c582145a776df180b104037ec12, sin cambios nuevos desde la revision previa; PR12 sin hilos de review al iniciar. Ninguna rama ajena sobrescrita.

## En criollo y posicion en el plan

Agregue la salida del ciclo entrar-leer-salir. Antes habia login aislado y controles de lectura, pero no una ruta HTTP para cerrar esa sesion. Ahora salir marca esa sesion como revocada en SQLite y las consultas siguientes la rechazan; otra sesion del mismo usuario y la de otro usuario conservan sus permisos. Seguimos en implementacion aislada de acceso/ciclo de sesion, no en piloto ni producto desplegado. D09/M03 NO se cierran por esto.

No merge, despliegue, cuentas humanas, credenciales reales ni cambios a Corpus vivo, VM, PR1 o las ramas PR7..PR12. Los tokens emitidos durante pruebas pertenecen a fixtures temporales; no se imprimen, no se entregan y se eliminan sus bases al terminar. No se reaudito la base legal ni se amplio el ledger de tres documentos.

## Contrato y arquitectura elegidos antes de implementar

Nuevo sistema/api/isolated_session.py: IsolatedSessionApp hereda IsolatedLoginApp. Conserva su __call__ y reemplaza solo el destino de las rutas no-login con session_route; no modifica isolated_login.py ni access_policy.py. Se rechazo copiar los guards porque duplicaria una frontera ya corregida por PR12. El host debe elegir esta clase expresamente: nadie cambia automaticamente el servicio existente.

Flujo: WSGI confiable -> opt-in y loopback PR12 -> marca aislada de despacho -> ruta logout -> validacion -> BEGIN IMMEDIATE -> marca revalidada -> UPDATE por hash -> COMMIT -> JSON. La lectura sigue usando el lector exacto y la politica persistente PR10. No cambios de esquema, dependencias nuevas, migracion o listener automaticos.

POST /api/v2/logout con Authorization Bearer valido, sin query ni cuerpo. Origin y Transfer-Encoding presentes, aun vacios, se rechazan. Solo Content-Length ausente, vacio o literal 0. Bearer43..128 caracteres URL-safe, mismo formato que la politica. No cookies ni CORS. Respuestas no-store/nosniff. 405metodo,403origen/transfer/aislamiento,400cuerpo/query,401bearer invalido,503store/reloj invalido. No se lee un cuerpo rechazado; la gestion de framing/timeouts del servidor WSGI sigue fuera del modulo.

UPDATE parametrizado limita token_sha256 exacto, revoked_at IS NULL y user_id fixture-*. No necesita grant,usuario habilitado ni sesion vigente para retirar una credencial. No crea cuentas/sesiones/grants ni borra filas. Repetir logout conserva primer timestamp; token desconocido y repetido devuelven el mismo 200 con logged_out:true y environment:isolated_test, sin revelar existencia. Una sesion nofixture no se modifica: este endpoint no sirve para cuentas reales. logged_out es resultado idempotente dentro del contrato ficticio, no comprobante de existencia previa ni de revocacion de una cuenta fuera del alcance.

Reloj no finito/negativo/bool:503 sin falso exito. Un retroceso finito no bloquea logout: se guarda ese entero y PR10 niega cualquier revoked_at no NULL, incluso anterior a valid_from. No cambia el high-water del LOGIN. El cliente futuro debe eliminar su token local; no existe UI nueva ni almacenamiento cliente en este incremento.

## Instrumentos y resultados

Dos archivos de codigo publicados comparados byte por byte con los ensayados: True/True. Desde git archive de455182 se ejecuto:

- python3 tests/test_isolated_session.py:10tests,14.189s,exit0.
- python3 tests/test_login_guards.py:18tests,25.927s,exit0;incluye12login heredados, no se ejecutan aparte.
- python3 tests/test_access_policy.py:15tests,5.253s,exit0.
- python3 tests/test_exact_http.py:15tests,1.490s,exit0.
- python3 tests/test_clean_snapshot_sol.py:21tests,6.869s,exit0.
- py_compile de modulo y banco nuevos:exit0.

Total79tests en esos cinco procesos;10son nuevos. No se suma la repeticion previa como tests distintos. No se afirma cobertura de lineas/ramas ni carga medida.

El banco nuevo reutiliza solo setup/helpers de LoginTests, no hereda sus test methods. Usa HTTP real en loopback y SQLite temporal. Mide lectura200 antes,logout200,lectura siguiente403; recrear app sobre mismo store conserva revocacion. Eso NO es reinicio de maquina/crash recovery. Comprueba hash del candidato ficticio sin cambios, otras dos sesiones200, idempotencia, ausencia de nuevos grants/sesiones, usuario deshabilitado+sesion expirada, request invalido, marca ausente, no-loopback, opt-in apagado, reloj invalido, tabla rota, rollback y nofixture. Cleanup detiene server,cierra socket y verifica thread detenido; no se deja listener de pruebas.

Tres mutaciones en copias separadas de de455182 produjeron exit1 por assertions, no errores de importacion:
1. SET revoked_at=? -> SET revoked_at=NULL y parametros ajustados: None !=1000 en la revocacion persistida.
2. WHERE token_sha256=? -> WHERE ? IS NOT NULL: segunda sesion da403 donde corresponde200.
3. Quitar AND revoked_at IS NULL: repeticion cambia1000a1010.

Los comandos completos y stderr de los nueve procesos estan en docs/agents/evidencia/2026-09-18-04-logout.json. El sujeto de los seis procesos normales es de455182; las ultimas tres filas son copias deliberadamente mutadas. Instrumento propio con logs crudos, no auditoria externa nueva. Las mutaciones corrieron localmente, NO se afirma haber puesto rojo GitHub CI.

[CI stable_identity](https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35398783629/job/105773630435):completed/success,21:50:55Z..21:51:26Z. Workflow mantiene checkout SHA pinneado,contents:read,persist-credentials:false,timeout global5min,bash set-euo-pipefail y timeout por banco. Agrega paths,compile y ejecucion del modulo nuevo sin duplicar LoginTests. Copilot solicitado; get_reviews devolvio [], NO aprobacion.

## Seguridad y limites

[OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) consultado18-sep:logout debe invalidar del lado servidor. Se implementa esa propiedad en el store aislado; no se declara cumplimiento OWASP completo ni auditoria de CVEs del runtime. No nuevas dependencias externas.

Revisados en este diff: SQL parametrizado, ausencia de credenciales/logs propios, no token en URL/body/errores, no cookies/CORS, bounds, marcador dentro de transaccion, no cambios de permisos CI. No se agrega SSRF ni ejecucion de comandos a la ruta. Los guards son administrativos, no una frontera contra operador hostil o proxy publico que presenta loopback. No exponer este wrapper a red publica.

Una lectura cuyo SELECT de autorizacion empezo antes de confirmar logout puede terminar; no se retira texto ya entregado. No atomicidad entre store y candidato. Un administrador que restaura el store puede restaurar sesiones; no se midieron DBrollback,contencion10x,crash recovery ni adversarios de host. BEGIN IMMEDIATE puede encontrar el lock del KDF heredado y devuelve503 al fallar el timeout; no asegura logout bajo saturacion. No debe interpretarse error como salida exitosa.

No logout global,reset/recuperacion,UI,provisionamiento real,actas juridicas,grants reales,TLS o despliegue. Son etapas pendientes del plan, no capacidades certificadas por79tests. Antes de activar piloto quedan integracion/revision autorizada,restauracion demostrada,seguridad de host y aprobaciones humanas. Siguiente avance de producto propuesto: vista aislada de entrada/lectura/salida usando estos contratos, con fixtures y sin publicar el servicio; no iniciado ni presentado como unico pendiente.

## Gate y QA TITAN FULL

Afirmacion -> instrumento -> podia dar rojo -> veredicto:
- Revoca sesion presentada -> HTTP+consultaSQLite+mutante no_revocation -> si -> medido en fixture.
- No revoca otras sesiones -> dos lecturas HTTP y mutante all_sessions -> si -> medido.
- Conserva idempotencia -> timestamp persistido y mutante overwrite_timestamp -> si -> medido.
- Funciona en produccion -> ninguno -> no -> NO MEDIDO/no autorizado.

81/90=90/100 exclusivamente para este modulo aislado. DevOps/despliegue10N/A:no se despliega;CI si observado. Completitud14/15(modulo,banco,contrato completo acotado);ejecutabilidad15/15(py_compile79tests publicado);seguridad13/15(SQL/guards/errores y limites explicitos, sin host audit);testing12/15(10nuevos79regresion3mutantes,sin coverage/carga);arquitectura9/10(wrapper reutiliza PR12 sin duplicar,no benchmark);documentacion10/10(contratos,limites,reproduccion,crudos);innovacion4/5(idempotencia,revocar aun expirada,aislamiento entre sesiones);proceso4/5(git/CI/crudos,review externa pendiente en PR13). No score de producto,merge o piloto.

Roles aplicados:Architect(contrato/composicion),Builder(modulo y banco),Security(frontera HTTP/SQL),Tester(HTTP,regresion,mutaciones),QA(diff publicado y checks). Todos ejecutados por Brain; no se inventan otros agentes. Sin nuevas conclusiones juridicas.

Registro propio: la primera materializacion local de archivos retuvo signos + del transporte; py_compile lo detecto y se genero copia limpia antes de ensayo/push. Una consulta de evidence.json llego antes del primer test terminado; se verifico el proceso existente y se espero, sin relanzar la corrida. No confundir archivo aun no escrito con prueba fallida.
