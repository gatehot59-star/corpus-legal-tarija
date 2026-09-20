# Ataque al clasificador documental: la ruta no demuestra que un cambio sea inocuo

20-sep-2026 ART. Aprobación: comentario80170047149689, test_docs_classifier_prototype. Alcance: construir y atacar un prototipo en repositorios sintéticos aislados, publicar evidencia; no implementar CI, reglas ni cambios de producto/PR/merge. Diseño juzgado: docs/agents/respuestas/2026-09-20-19-documentation-review-design.md en7c1448122bafeea5d63b37375b570a2c2b4e8612.

## Resultado que cambia la decisión

**No habilitar todavía la omisión de pruebas de código por clasificación documental.** Construí dos modelos y ejecuté23 casos con Git real, repetidos en23 repos nuevos. El modelo conservador distingue los ataques estructurales ensayados, pero tiene un contraejemplo semántico reproducido: un archivo .md permitido es leído por un programa y altera su salida, aunque el clasificador declara DOCS cuando falta en su inventario de inputs consumidos.

No es un bypass de GitHub ni un defecto demostrado de Corpus: el consumidor y el archivo fueron sembrados por mí en una fixture explícita. Es una refutación experimental de que rutas/extensiones y un inventario incompleto basten para acreditar ausencia de efecto en runtime. La propuesta original ya excluía inputs consumidos, pero no definía cómo obtener un inventario completo y confiable. Ese hueco sigue abierto.

El modelo mínimo docs/** + sufijo .md se equivoca en14 entradas de la matriz. No son14 vulnerabilidades independientes: incluyen variantes y precondiciones que ese modelo deliberadamente ignora. Nunca existió como implementación publicada del diseño19; lo escribí para representar una simplificación peligrosa, no para atribuirle defectos a software inexistente.

## Instrumentos y contrato

Git2.47.3 y Python3.12 en brain-env, vía Gateway build/run. Fuente lab.py SHA256 fde9eac5b1286d3aea09d634d94f85d9db91dbccf01a8ba4abf0f4c9ec168d13 incluida íntegra en evidencia. Matriz escrita antes de ejecutar. Archivos, commits, renombres, enlaces simbólicos, modos ejecutables y gitlinks reales en repos propios sin remotos; ningún checkout/reset/escritura sobre el árbol de trabajo del producto. Toda captura incluye argv, exit, stdout y stderr.

Modelo mínimo: examina nombres entregados, acepta todos bajo docs/ terminados en .md. El experimento de truncamiento le entrega solo100 de121 nombres reales; el de rename solo el destino. Es una simulación explícita de transporte incompleto, no una llamada a una API paginada real.

Prototipo conservador v1: ejecutado desde fuera del árbol candidato; verifica hashes completos, head esperado, existencia de commits y que base sea ancestro; obtiene el diff entero local con git diff --raw --no-abbrev --no-renames -z. Comprueba status y modos, separa nombres por NUL y bloquea caracteres de control. Solo permite archivos regulares100644 en dos patrones de informes fechados: docs/auditorias y docs/agents/respuestas. Inputs consumidos conocidos son excluidos mediante lista confiable externa al candidato. Resto: CODE o BLOCK. DOCS significa elegible para validación documental, NO aprobación ni autorización de merge.

Es un subconjunto deliberadamente más estrecho que el diseño: no habilita JSON, paquetes ni fuentes de evidencia como documentación rápida. El futuro validador de contenido/paquetes no se implementó. No atribuir al prototipo cobertura de todos los formatos del flujo documental.

## Casos medidos

| Familia | Observación v1 |
| --- | --- |
| Informe nuevo y modificación de informe regular | DOCS, controles positivos |
| Informe mezclado con código | CODE |
| Código renombrado hacia docs; documento renombrado a src | CODE, no ignora el path anterior |
| Symlink .md, .md ejecutable, gitlink .md | CODE por tipo/modo |
| Nombre con salto de línea | BLOCK |
| .md.py, .MD y extensión con letra Unicode semejante | CODE |
| docs/AGENTS.md y docs/review-policy.md | CODE |
| Borrado de informe | CODE |
| 120 informes y un cambio de código | CODE; el modelo con lista truncada dice DOCS |
| Cambio del propio classifier.py más informe | CODE; no se ejecuta el clasificador del candidato |
| Input .md consumido y registrado | CODE |
| Diff vacío, head distinto del esperado, objeto ausente, base divergida | BLOCK |
| Mismo input .md consumido pero NO registrado | **DOCS incorrecto para decidir omitir pruebas** |

23 salidas coinciden con la matriz en cada ejecución. **23/23 NO significa23 cambios seguros**: la última expectativa es observar el punto ciego, no certificarlo. No contar las repeticiones como46 casos únicos. Los casos estructurales detectados no demuestran cobertura exhaustiva del espacio de nombres ni de todos los transportes.

## Contraejemplo decisivo y control causal

Fixture: consumer.py lee docs/auditorias/2026-09-20-runtime.md. Base contiene ALLOW=0; head cambia SOLO ese .md a ALLOW=1. Se ejecutó consumer.py desde archives nuevos de ambos commits, no se dedujo la salida solo leyendo el archivo. En las dos repeticiones: base stdout ALLOW=0, head stdout ALLOW=1, los cuatro procesos exit0 y stderr vacío.

Con ese path en la exclusión confiable, el prototipo devuelve CODE. Sin la exclusión, los mismos cambios devuelven DOCS. El contenido cambió el comportamiento del consumidor, pero el nombre no permitió descubrirlo. Si un agregador aceptase DOCS para saltarse las suites, podría omitir pruebas pertinentes aun con una implementación correcta de las comprobaciones de modos y rutas. La revisión independiente sigue obligatoria: no se demostró que GitHub permitiría merge sin ella.

Otro falsador causal: el candidato rechaza un symlink .md. Quitar SOLO el control de modos lo convierte en DOCS. El mismo input pasa el criterio de rechazo en el prototipo y lo viola en el mutante; no es un fallo de importación ni preparación.

## Agregación: modelo local, no GitHub

Ejecuté9 casos de una función de decisión separada: DOCS con validación correcta y aprobación booleana verdadera pasa; sin aprobación falla; CODE exige pruebas exitosas; skipped/failure/cancelled no sirven para CODE; BLOCK siempre falla; documentación inválida falla; el string true no se acepta como booleano verdadero.

Esto no comprueba autenticidad, vigencia ni independencia de una aprobación GitHub. La aprobación es un dato ficticio del test. Tampoco demuestra resistencia a cambios de workflow o suplantación de checks. No usar9/9 como recibo de protección de ramas.

## Cambios que exige el diseño antes de implementar

1. DOCS debe ser solo una sugerencia de ruta de validación, nunca prueba automática de que no hay impacto de código. Hasta demostrar aislamiento de los paths editoriales respecto de builds/runtime/instrucciones operativas, ejecutar las suites de código también en PR documentales.
2. Políticas, versión del clasificador, base y head deben proceder de contexto confiable y quedar ligados al resultado. El prototipo contrasta head esperado y ascendencia, pero NO obtiene por sí solo el estado vigente del PR ni una base esperada independiente. Un caller que elija mal las revisiones puede invalidar la conclusión; hace falta revalidación al integrar.
3. Obtener el diff completo con origen y destino/modos; si una API enumera archivos, verificar paginación, límites y completitud en vez de asumir que una página es todo. Aquí se ensayó truncamiento artificial, no límites del proveedor.
4. Mantener aprobación independiente para cualquier cambio a main, también docs; nunca conceder bypass al publicador. Separar publicación durable de aceptación sigue siendo válido.

No se editó el diseño19 ni se implementaron estos cambios en el producto. Son reparos y criterios de corrección para su siguiente revisión.

## Qué NO se midió que importaba

No se construyó un inventario real de consumidores de Corpus; no se demostró que el repo actual lea ese path ficticio. No se probaron GitHub Actions, políticas de branch protection, permisos, revisores, webhooks, race conditions de merge ni cambios concurrentes de base después del chequeo. No se ensayaron diff gigantes que agoten memoria, todas las codificaciones de nombres, archivos comprimidos, descompresión, enlaces externos ni validación de secretos. Los subprocesos tienen timeout, pero el prototipo no impone un límite de bytes al diff capturado: no es una implementación lista para producción.

Soy autor del prototipo y operador de sus pruebas. Hay fixtures y expectativas explícitas, falsadores causales y evidencia cruda, no un segundo revisor personal. No firmo revisión externa de PR18 o PR20 ni cambia la orden de mantener17/18/19 abiertos. PR1/20 quedan intactos.

## Custodia, errores y cierre

[Evidencia íntegra](https://github.com/gatehot59-star/corpus-legal-tarija/blob/dae0e9e865a0a6a046ef3983245f2ed735faeead/docs/auditorias/2026-09-20-20-docs-classifier/evidence.xz.b64): base64 estricto+xz,234823bytes JSON, SHA2569d9e2ebccfdf6e9c43f47d1ebcfd3825503a110fae121a5b47e307ce2480d2d8. Incluye ambos experimentos completos, fuentes, matrices, comandos Git, diff y salidas, decisiones y9casos del agregador por ejecución, más4corridas base/head del consumidor. Recuperada del commit mediante git fetch/show y comparada byte por byte con el paquete local; decodificación y hash verificados. No contiene tokens, bases reales ni binarios versionados. Fixtures sintéticas permanecen locales para reproducir; no se lanzaron servidores ni procesos detached.

La enumeración pública de PR devolvió403 por límite de solicitudes; git fetch y lectura del diseño funcionaron. Se verificaron las cinco cabezas de PR mediante git ls-remote, iguales a las previas. Eso comprueba heads, no estado open/closed: no se afirma reconsulta final de estado API. No hubo llamada de merge o actualización de PR. El transporte del script antepuso signos+; se normalizó antes de validar sintaxis y ejecutar, sin corrida experimental inválida. Los dos laboratorios terminaron0.

Método: auditoría adversarial de prototipo aislado, no TITAN de despliegue o cambio de permisos. Gate I PASA para los experimentos acotados y sus controles; la afirmación de seguridad general del clasificador FALLA por el contraejemplo. Gate II: causalidad, origen sintético, autoría y exclusiones declaradas; sin nota de seguridad global. Gate III: evidencia recuperada idéntica; informe, Doc público y Nexus se verifican antes del chat. Ningún cambio de CI, reglas, permisos, método, producto ni PR; solo publicación documental autorizada bajo el método vigente.
