# Astra: auditoría posterior al merge de PR14

Fecha: 19-sep-2026 (ART). Revisor, verificador experimental y control final: mismo operador Astra; no constituyen tres revisiones externas.

## Resultado y alcance

Sin nuevos defectos de producto demostrados en el contrato aislado seleccionado. CONFIRMADOS: composición CLI real, lectura exacta, logout selectivo persistente entre procesos, rechazo de estados inválidos sin reparación automática y recuperación tras solicitudes incompletas inactivas. REFUTADA como extrapolación: «dos segundos de timeout son un plazo total por solicitud». NO MEDIDO: producción, recuperación tras crash, concurrencia sostenida, TLS y validez jurídica.

Encargo: `docs/auditorias/2026-09-19-02-encargo-astra-pr14.md`, commit b720dd0c04e4548f1f297cf3bfa87463eac2131a, Nexus 50. No se sustituyó por la auditoría de PR16 ya entregada.

Repo: gatehot59-star/corpus-legal-tarija. Revisión congelada y ejecutada: 9913d8dd5074d6aedd0d261c42caea6480e794fe, merge de PR14 que incorpora PR15. Main inicial: b720dd0c04e4548f1f297cf3bfa87463eac2131a; merge ancestro y delta fuera de docs vacío. PR14 consultado individualmente: cerrado, merged=true, head e7e06e9cc94a917160e522fa409bc66f6829b2ee.

Sujeto: `sistema/api/demo_aislada.py`, `tests/test_demo_aislada.py`, `sistema/DEMO-AISLADA.md`, `.github/workflows/clean-snapshot.yml`. Consumidor: CLI init/serve real, IsolatedSessionApp, login, política y lector exacto. No es el servidor histórico ni un servicio vivo. PR1, PR16 y restauración están excluidos.

## Instrumento y controles

Banco propio `probe.py`: subprocess real, sockets loopback, SQL sintético y oráculo fijo externo al lector. Golden: `DEMO FICTICIA, SIN VALOR JURIDICO\nArtículo único: Ñ, ⚖ y e\u0301.\r\n`; versión calculada sobre esos bytes, paginación de 11 caracteres. Dos identidades; dos sesiones de una identidad y una de la otra. El launcher produce el servicio, no el esperado.

La primera corrida propia fue INVÁLIDA: `import http.client` quedó sombreado por una función llamada `http`; el primer login lanzó AttributeError. No fue fallo del producto. Se conservan banco, salidas y resultados originales. Corrección mínima solo del instrumento: importar y usar HTTPConnection directamente. Se repitieron baseline, repetición y los tres mutantes en scratch nuevo.

Banco corregido: 142 aserciones, cero fallos, exit 0. Repetición completa en otro store: 142, cero, exit 0. Son dos ejecuciones del mismo banco, no 284 pruebas independientes. La suite del autor se ejecutó una vez; el supervisor corregido omitió repetirla.

Falsadores locales, ninguno publicado como producto:

- Quitar opt-in: el mismo positivo que no crea directorio ni emite ready ahora falla. Mutante: 10 aserciones, cuatro fallos específicos (`optin_init_exit`, `optin_no_creation`, `optin_serve_exit`, `optin_serve_no_ready`).
- Borrar revoked_at al arrancar: `revoked_after_restart` recibe 200 en vez de 403; también fallan comparación lógica y bytes. 38 aserciones, tres fallos. El otro usuario/sesión no es el oráculo de la revocación objetivo.
- Quitar guard Host/Origin: `bad_host`, `empty_origin`, `origin` reciben 200 en vez de 403. 14 aserciones, tres fallos. Host esperado sin Origin pasa en positivo.

Los tres salen 1 por la propiedad intencional, no por un import roto. Diffs y aserciones completas están en la evidencia corregida.

## Afirmaciones, resultados e impacto

1. CONFIRMADO: init y serve reales componen la demo. Se observó el PID anunciado y el socket literal 127.0.0.1 en `/proc/net/tcp`; no se dedujo el bind solo de stdout. Lectura paginada coincide exactamente con el golden Unicode/CRLF.
2. CONFIRMADO: logout 200 revoca solo el bearer elegido; siguiente lectura 403, otra sesión de la misma identidad y otra identidad 200. Logout repetido no cambia el primer timestamp, comprobado por SQL.
3. CONFIRMADO: SIGTERM, salida del proceso A y arranque B con PID distinto y el mismo store mantienen revocación y otras sesiones. Hash lógico y hashes fríos de archivos no cambian por serve/reinicio. Candidate preservado. No es prueba de apagón ni kill -9.
4. CONFIRMADO: retirar grant y luego hacer login no restaura permisos. Login 200, lectura 403; la otra identidad sigue en 200.
5. CONFIRMADO: sin opt-in no hay creación ni ready; init sobre destino existente, store/marca/reloj ausentes, texto alterado, symlink, hardlink, FIFO, permisos amplios, sidecar y puerto ocupado rechazan con estado capturado sin cambios. El listener que ocupa el puerto es del instrumento y sigue vivo. No se prueba resistencia contra root o mismo UID hostil.
6. CONFIRMADO: Host equivocado, Origin vacío y Origin no vacío reciben 403 por socket real; Host esperado sin Origin recibe 200.
7. CONFIRMADO con límite: solicitudes incompletas inactivas terminan cerca de dos segundos y luego una lectura autorizada recibe 200. No queda inutilizado el servicio por esos casos.

No se tocaron producto, VM, cuentas reales ni bases vivas. No se emitió autorización de merge, deploy o piloto.

## Red, tiempos y límite de interpretación

Criterio previo para inactividad: 1,5 a 4,5 segundos alrededor de los dos segundos declarados; espera máxima de parada: cinco segundos. Brain-env: Python 3.12.14, SQLite 3.46.1, FTS5 funcional, dos CPU. Hubo breve solapamiento entre suite heredada y banco corregido; estos tiempos no son benchmark de rendimiento.

- Header incompleto: EOF sin respuesta a 2,0533 s; repetición 2,0147 s.
- Body incompleto de login: 503 genérico LOGIN_UNAVAILABLE y EOF a 2,00316 s; repetición 2,00374 s.
- SIGTERM durante header incompleto: terminó a 1,9435 s; repetición 1,8709 s. Son paradas ordenadas.
- Envío de un byte cada 0,65 s durante cuatro iteraciones: conexión todavía esperando a 2,70086 s y 2,70098 s. Se observó ese intervalo, no una retención infinita.

La extrapolación «timeout total de dos segundos» queda REFUTADA; la propiedad real es inactividad. No lo clasifico como defecto nuevo del contrato de demo local ni como ataque remoto demostrado. Si se cambia el contrato para exposición o servicio compartido, el responsable del servidor debe definir plazo total/concurrencia y ensayarlos antes de habilitarlo; no implementé ese cambio.

Los casos de header incompleto dejan traceback de TimeoutError de socketserver/http.client en stderr local. La captura conserva los 1527 bytes del diagnóstico de cada servidor pertinente. No se devolvió ese traceback al cliente en el caso medido ni se demostró caída del proceso. No afirmo logs vacíos.

## Suite del autor y CI

Los dos bloques exactos del workflow se ejecutaron localmente: 97 casos pasan, desglosados en 21 clean_snapshot_sol + 15 exact_http + 15 access_policy + 18 login_guards + 10 isolated_session + 18 demo. No sumé otra vez los 12 casos heredados de login.

Control independiente del bloque shell de demo: shim de python3 sale 23 y segundo shim imprimiría SHOULD_NOT_RUN. Resultado: bloque sale 23, stdout/stderr vacíos, segundo paso no ejecutado. Comprueba propagación local, no un nuevo run rojo en GitHub.

Metadata histórica consultada: job 105817429355, stable_identity, success, 2026-09-19 01:42:12 a 01:42:43 UTC. Fuente: https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35413461264/job/105817429355 . No reejecuté Actions ni presento esa metadata como log completo de una corrida propia.

## Recursos y deuda heredada

Observador con referencias retenidas mide cierre explícito, no supervivencia tras salir del proceso. Positivo del contador: conexión cerrada; negativo deliberado: una conexión sin close detectada. En captura corregida: 65 registros de procesos, 330 conexiones abiertas y 329 cerradas; la única restante es ese control negativo PID 2134. No se exige que el falsador pase.

En los procesos de suites heredadas se observaron cierres explícitos faltantes: clean_snapshot_sol 2, exact_http 17, access_policy 63, login_guards 69, isolated_session 35. No son cinco nuevos defectos productivos ni fugas que sobreviven al proceso. El antecedente de exact_http ya estaba documentado; aquí el argv identifica cada suite. La suite demo no mostró ese reparo. Recomendación separada para mantenedor de tests: cerrar fixtures explícitamente y repetir el contador; no modifiqué su banco.

Escaneo combinado final: 69 procesos hijos ausentes y 21 puertos cerrados. SQLite propio se cierra explícitamente; no se hizo checkpoint sobre bases ajenas. Hashes comparados solo con conexiones escritoras cerradas, agregando estado lógico para no confundir checkpoint con cambio de filas.

## Evidencia y reproducción

Archivo único de texto: `docs/auditorias/2026-09-19-03-astra-pr14-integrado/evidence.xz.b64`, commit 5db5d6df82eda5db8d8ac1e168acb846c2c4ad8a.

https://github.com/gatehot59-star/corpus-legal-tarija/blob/5db5d6df82eda5db8d8ac1e168acb846c2c4ad8a/docs/auditorias/2026-09-19-03-astra-pr14-integrado/evidence.xz.b64

34204 bytes ASCII, base64 estricto y xz; JSON recuperado: 308634 bytes, SHA256 `4764df2c1a270414709f7d07628271ce93dc4c5f36df7bb0eb0f117bc401f521`. Recuperado de git y comparado byte por byte con original: idéntico; commit pertenece a main. No requiere concatenar revisiones históricas.

Decodificar con base64.b64decode(payload, validate=True), luego lzma.decompress; comprobar longitud/SHA anteriores y json.loads. `corrected_capture.instruments` contiene probe, supervisor y resource_observer; `original_failed_instrument_capture` conserva error anterior. También incluye finalizer_source, comandos, diffs, resultados, stdout/stderr, recursos y control shell.

Para repetición: extraer repo congelado en directorio nuevo; guardar el texto `corrected_capture.instruments.probe` como probe.py; ejecutar `python3 probe.py FROZEN_REPO NEW_OUTPUT all`. Repetir en otro output. Inspeccionar supervisor y sus rutas antes de reutilizarlo; no ejecutarlo ciegamente contra directorios existentes. Mutaciones y modos están registrados en commands; reproducirlas solo en copias. El observador requiere su configuración de subprocess registrada. El banco sin observador reproduce comportamiento, no acredita por sí solo el conteo de cierres.

Exclusiones declaradas de captura: valores Authorization, tokens sintéticos, passwords de requests de login, digests individuales de credenciales y archivos SQLite. Fixtures reproducibles e instrumentos sí incluidos. Captura íntegra respecto de esas exclusiones; no se reconstruyen datos deliberadamente excluidos.

## Control final

Gate I: PASA para el instrumento corregido. Sujeto y consumidor fijados; oracle independiente; baseline y repetición positivos; tres falsadores causales; recursos propios cerrados con control negativo identificado; captura completa declarada. Banco inicial FALLA por instrumento y no participa del veredicto. Suites heredadas PASAN funcionalmente pero mantienen el reparo de cierre explícito descrito; no se los disfraza como Gate I propio.

Gate II: PASA en este alcance. Cada afirmación queda delimitada; distingue instrumento/producto/entorno, límite temporal y deuda de tests. Reproducción, impacto y exclusiones explícitos; no se inventó un fallo de producto ni se implementó un arreglo.

Gate III al publicar esta primera versión del informe: INCOMPLETA, aunque la evidencia ya fue verificada. Faltan readback del informe, Doc público y continuidad Nexus. El acta hermana `docs/auditorias/2026-09-19-03-astra-pr14-integrado/cierre.json` registrará el estado posterior, URLs, hashes y controles efectivos; no inferir cierre solo por este párrafo.

N/A justificado: despliegue, intervención VM, provisión real y restauración PR16 no forman parte del encargo. No se asignó una nota ni se atribuyó independencia a otro modelo.

Qué no se midió que importaba: plazo total/concurrencia frente a emisores lentos, recuperación por crash, entorno real y datos jurídicos. Esas exclusiones impiden certificar producción; no invalidan el ciclo aislado probado. Los informes locales históricos 01/03 siguen sin cierre propio y no quedan publicados por asociación con esta entrega.
