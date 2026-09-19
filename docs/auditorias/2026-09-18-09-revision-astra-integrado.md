# Revisión de Astra integrado: auditoría reproducida, persistencia falsable

Fecha de trabajo: 18-sep-2026, ART (UTC-3). Capturas pueden estar fechadas 19-sep UTC.

## Veredicto y sujeto

CONFIRMADO dentro del alcance: la auditoría de Astra `docs/auditorias/2026-09-18-08-astra-integrado.md`, publicada en c7b6ed79640c37547607332e9a49276543696907, tiene evidencia remota íntegra y sus afirmaciones centrales se reproducen. No encontré un nuevo reparo que invalide sus conclusiones. No es una aprobación universal de Corpus, de producción ni de superioridad entre modelos.

Producto integrado: 30189275ea996e23aa7804e2334f0b9ba93dd8d1, tree 110dccfa2da21ff08fbac7b875d705f6cf496ade. Revisión archivada para las ejecuciones: 526a29a92144f24853f56595d2eea4bdb836967c. Los seis archivos clave de producto/README extraídos del paquete original coinciden con Git. El diff fuera de docs desde esa revisión hasta la publicación de evidencia 784f04408989981ef760242e919f5ba660201039 está vacío. No extender este resultado a cambios posteriores no revisados.

Modo: revisión del instrumento, custodia, conclusiones y entrega de otro auditor. Revisor, verificador experimental y control final son funciones de este mismo operador, no tres revisores independientes. SOL/Astra tiene autorías anteriores en Corpus; no se las cuenta como evidencia externa. La expectativa sintética y los falsadores son el fundamento, no la etiqueta del modelo.

## Antecedentes y delimitación

Se revisó la respuesta al encargo `2026-09-18-06-brain-main-encargo-astra.md`, no la auditoría matutina ni la publicación conjunta anterior. Nexus 43/44 delimita integración y locks; Nexus 45 registra el cierre de Astra. La auditoría 08 sí publica su informe, sus tres partes de evidencia y su Doc; no corresponde trasladarle la deuda de los informes locales 01/03.

El instrumento original establece un golden sintético de 1793 caracteres con Unicode, CRLF y 37 repeticiones, dos identidades y varias sesiones emitidas por login real, permisos separados de autenticación, SQL directo y reloj controlado. El esperado no se calcula usando el lector que se está juzgando.

## Resultados por afirmación

### 1. Evidencia original publicada: CONFIRMADO

Se reconstruyeron las tres partes remotas de la auditoría 08, de 8000, 8000 y 7916 caracteres, desde su cadena publicada, última parte en d60ac0498a2993b900f67f79d6918c8f9cc8c890. Base64 estricto y descompresión xz entregan 550961 bytes con SHA256 2db93dea9e58bab24545763c2fb7b12349fcf7cf2b2cd0c0f14dd69fbbb0aa08. Comparación con el original del taller: idénticos. Los instrumentos reejecutados se obtuvieron de esa evidencia, no de una variante local presumida equivalente.

### 2. Banco positivo y recursos: CONFIRMADO

`review_run.py` reejecutó `integrated_probe.py`, `integrated_mutate.py` y `documented_host_probe.py` en scratch propio y revisión archivada. Comandos exactos, cwd, códigos de salida y stdout/stderr se preservan en el paquete. La corrida sin modificaciones produjo 69 comprobaciones correctas, cero fallos y salida 0. La repetición original de Astra (69/0 en otro store) fue inspeccionada como antecedente, no se cuenta como otra corrida propia ni como 138 pruebas independientes.

Procesos reales de la corrida propia: 31887 y 31888, ambos salida 0 y ausentes después. Conexiones registradas creadas/cerradas: 109/109 y 21/21; cero abiertas al terminar. Se comprobó cierre de listeners. La comparación física se refiere al archivo principal del candidato sintético cerrado, no a una base de producción ni a bytes de un WAL activo.

El banco conserva controles de paginación exacta, login sin grant, pausa/restauración, retiro de documento y permiso, logout selectivo e idempotente, reloj fraccionario, high-water tras password erróneo y throttling natural. La ausencia de login_clock hace fallar login, pero no lectura/logout existentes; está declarada como política, no se inventa una exigencia de migración automática.

### 3. Cuatro mutantes de Astra: CONFIRMADO

La aserción objetivo pasa en el positivo y falla con la modificación correspondiente. No se infiere detección de `returncode != 0` a secas.

- `no_revoke`: 65 correctas / 4 fallos, incluye `revoked_next_page`.
- `revoke_every_session`: 64 / 5, incluye `same_identity_other_session`.
- `ignore_clock`: 67 / 2, incluye `rollback_after_wrong_password`.
- `ignore_dispatch_marker`: 68 / 1, falla `pause_read`.

Los resultados completos y las modificaciones originales quedan preservados. Los trabajadores terminaron y cerraron sus recursos; los fallos son observaciones semánticas previstas, no imports rotos ni procesos colgados.

### 4. Persistencia entre procesos y falsador propio: CONFIRMADO con límite

No fue solamente construir un nuevo objeto Python: se terminó ordenadamente un proceso y se abrió otro proceso del sistema operativo sobre el mismo store. La sesión revocada siguió devolviendo 403 y las otras sesiones siguieron funcionando.

Para probar que ese oráculo puede dar rojo precisamente por pérdida al reiniciar, se creó `probe_restart_sabotage.py`, copia separada del instrumento. Único cambio causal: antes de `running=[True]`, al arrancar cada trabajador:

```python
with closing(sqlite3.connect(store)) as db, db:
    db.execute("UPDATE access_sessions SET revoked_at=NULL")
```

El primer trabajador encuentra el fixture sin revocaciones; el segundo borra las que dejó el primero. No se modifica producto ni el instrumento original. `run_restart_sabotage.py` ejecuta este control y conserva resultados/logs completos.

Resultado: salida del verificador 1, 68 correctas y un único fallo `new_process_revoked`; observado HTTP 200, esperado 403. Los controles anteriores siguen pasando. Trabajadores 31901/31917 terminan con salida 0; conexiones 110/110 y 23/23 cerradas, listeners cerrados y procesos ausentes.

Este falsador no descubre una pérdida real del producto: demuestra sensibilidad causal del banco. NO MEDIDO: crash abrupto, corte de energía, reinicio de máquina o recuperación de almacenamiento.

### 5. Consumidor documentado sin composición aislada: CONFIRMADO, límite conocido

La corrida propia del Handler de `sistema/api/servidor.py`, conforme al punto de entrada documentado en `sistema/README.md`, observó health 200, login 501, logout 501 y texto v2 404. El listener terminó. Ese Handler no monta IsolatedSessionApp.

Esto respalda el siguiente trabajo acotado propuesto por Astra: arranque explícito de demo aislada y aprovisionamiento sintético. No equivale a demostrar cuál es el entrypoint del host vivo. No es un nuevo defecto de autorización ni un despliegue. No se implementó el lanzador.

## Gate I: instrumento

PASA en los criterios seleccionados: sujeto y revisión exactos; golden externo al lector; positivo 69/0; cuatro mutantes con fallos objetivo; falsador adicional de pérdida en segundo proceso; cierre explícito e inspección de recursos; repetición en scratch propio; fuentes/resultados/stdout/stderr íntegros respecto de la captura declarada.

Los doce trabajadores de baseline, cuatro mutantes y falsador propio finalizaron con salida 0 y sin conexiones registradas abiertas. Los códigos de los verificadores se distinguen de los códigos de sus trabajadores. El Handler documentado tiene su propio control de listener detenido.

N/A: minimización de un defecto nuevo, porque no se identificó uno; replay de 79 tests del autor por ceremonia, porque el encargo era revisar al auditor; cambio de producto, merge, despliegue y acciones sobre cuentas reales, no autorizados.

## Gate II: informe

PASA para afirmaciones centrales, causalidad, revisión/consumidor, recursos y límites. No se fabrica un rojo para justificar la revisión. Validez experimental y entrega se evalúan aparte. No hay una nota numérica ni afirmación de independencia por modelo.

Lo que importa y NO se midió: servidor vivo y sus rutas efectivas; recuperación abrupta; concurrencia exhaustiva, TLS y operación real; cobertura/validez jurídica; piloto con usuarios y rentabilidad. La matriz amplia de locks es evidencia de la revisión 07, no se atribuye como reejecución completa de este turno. El banco de Astra sí ejercita su control acotado de writer lock.

## Custodia de esta revisión

Scratch propio: `/workspace/review-astra-integrated-am8919ui`. No es fuente canónica ni requisito para consumir el paquete remoto.

Evidencia: carpeta hermana `2026-09-18-09-revision-astra-integrado/`, archivos `evidence.xz.b64.part0` y `evidence.xz.b64.part1`. Orden 0,1; códec xz+base64, sin recortes ni binarios en Git.

- part0: 11600 bytes ASCII; SHA256 e5c1430d2eb2e183e1a48043ac9aeb3fb15cbb4e5b0683d76932bacacc691c0c.
- part1: 11520 bytes ASCII; SHA256 6f80ab1e7c43956ebb73de0d025218dd81086fdddd34938c7d67dd8bb717b21a.
- Captura reconstruida: 570136 bytes; SHA256 3533901e95f4b6c0fe2635ebe4b7c6cc8768060bbe3a3eff27e12323ea898fec.
- Commit con las dos partes: 784f04408989981ef760242e919f5ba660201039, descendiente de la parte inicial 5579580db7d16662c3142933ee6a669870ac3d07.

Readback ejecutado desde Git: ambas partes recuperadas, base64 validado estrictamente, lzma descomprimido, comparación byte por byte contra `review-evidence-full.json` verdadera; pertenencia a main verdadera; diff fuera de docs vacío. No se infiere publicación del mero hash local.

El paquete conserva todos los archivos generados de la revisión incluidos en su captura, instrumentos, fuentes, comandos, salidas, retornos, resultados, custodia y control estructural. El paquete original de Astra se referencia por commit/hash y no se duplica dentro de esta captura. Contraseñas/cabeceras de autorización se excluyen y los tokens sintéticos se redactan conforme a la captura original; no se prometen requests secretos crudos. La verificación de publicación sucede después de cerrar la captura y su resultado se registra aquí, no se pretende que estuviera en los bytes que ella misma verificó.

Reconstrucción sin ejecutar instrumentos:

```python
import base64, hashlib, lzma
from pathlib import Path
p = Path('docs/auditorias/2026-09-18-09-revision-astra-integrado')
encoded = b''.join((p / ('evidence.xz.b64.part' + str(i))).read_bytes() for i in range(2))
data = lzma.decompress(base64.b64decode(encoded, validate=True))
assert len(data) == 570136
assert hashlib.sha256(data).hexdigest() == '3533901e95f4b6c0fe2635ebe4b7c6cc8768060bbe3a3eff27e12323ea898fec'
```

Es el mismo algoritmo de reconstrucción ejecutado para la verificación remota, aquí expresado para lectura desde un checkout.

## Gate III: entrega y continuidad

Evidencia Git: PUBLICADA Y VERIFICADA. Doc: PÚBLICO en el Space validado, creado y recuperado por su página: [Revisión de Astra integrado: auditoría reproducida y persistencia falsable, sin nuevos reparos](https://app.clickup.com/90171457413/docs/2kza6fw5-13157).

Este informe se incorpora a main mediante publicación documental; su commit se recupera y comprueba antes del chat. El cierre definitivo de continuidad se registra en Nexus bajo turno `2026-09-18-09-revision-astra-integrado`, con el commit resultante y el Doc. Hasta esos dos controles finales, el estado formal es INCOMPLETA; el recibo Nexus acreditará COMPLETA solamente después de verificarlos. Ningún cierre retrospectivo se inventa dentro del archivo que aún se está publicando.

Escrituras realizadas: instrumentos/fixtures propios, dos bloques de evidencia, este informe, Doc público y registro propio de continuidad. Sin cambios de producto, servicios productivos, bases vivas, credenciales, issues, mensajes a agentes, merges ni despliegues.

Pendientes ajenos a este cierre: publicación grande autorizada de la revisión conjunta anterior; experimento con/sin skill; situación histórica de informes locales 01/03. La nueva auditoría 08 no los cierra retroactivamente. El lector de pérdida mínima global tampoco forma parte de esta revisión.

## Fuentes permanentes

- [Auditoría 08 revisada](https://github.com/gatehot59-star/corpus-legal-tarija/blob/c7b6ed79640c37547607332e9a49276543696907/docs/auditorias/2026-09-18-08-astra-integrado.md).
- [Evidencia propia publicada](https://github.com/gatehot59-star/corpus-legal-tarija/tree/784f04408989981ef760242e919f5ba660201039/docs/auditorias/2026-09-18-09-revision-astra-integrado).
- [Encargo de integración y prioridades](https://app.clickup.com/90171457413/docs/2kza6fw5-13097).
- [Antecedente de locks, no reejecución completa aquí](https://app.clickup.com/90171457413/docs/2kza6fw5-13117).
