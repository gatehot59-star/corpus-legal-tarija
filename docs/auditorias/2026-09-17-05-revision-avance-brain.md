# Brain avanzó en código y pruebas; PR2 requiere dos aclaraciones/correcciones antes de mi aprobación

17-sep-2026. Pedido de Abraham: auditar avance de Brain y actuar como revisor. Se revisó el nuevo incremento del corpus y el correctivo de CI de Custos, sujeto del Doc seleccionado. No se revisaron exhaustivamente otros proyectos o toda producción. No se hizo merge, despliegue ni se envió una review/comentario a GitHub en nombre del usuario.

## Dictamen de revisor

**Avance real confirmado.** Corpus PR2 incorpora contratos ejecutables y un lector nacional que ahora compara el hash; reproduje23tests de contratos,11del lector ylos3mutantes detectados. El CI del head exacto está success. No corresponde decir que Brain solo escribió informes.

**Solicito cambios acotados antes de aprobar PR2:** diferenciar manifiesto ausente de fuente vacía y definir/hacer cumplir la política de symlinks del directorio raíz de textos. Ambos casos fueron ejecutados con fuentes sintéticas sobre el archivo real de la rama. No pido otra arquitectura ni nuevas rondas de aprobación del plan para arreglarlos.

Esto no implica una vulnerabilidad remota de producción. El lector todavía no está integrado; la rama se presenta honestamente como prototipo aislado. El código válido yel rechazo de hashes ya avanzaron. Mi conclusión es sobre su contrato de entrada, no sobre un HTTP que no lo llama.

## Alcance y revisiones

- Corpus [PR2](https://github.com/gatehot59-star/corpus-legal-tarija/pull/2), rama titan/corpus-v2-stage1, head `eac03e8ac3670638fada9d1baad682edb798b5bf`: abierto ysin merge en la consulta. Diff completo12archivos,842adiciones leído. Su título/cuerpo inicial todavía describe23tests yB03pendiente; head yrecibo posterior incluyen lector y34tests.
- [CI del head](https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35183522895/job/105080589252): contracts completed/success,04:51:56Z a04:52:04Z. Es posterior al job citado en el Doc de Brain; no se asumió equivalencia por nombre.
- Custos main `0f1fdae90b88014b45e58c4e1b86f21cbe449b48`: leídos commits yworkflow; ejecutada regresión del falsador. El commit de merge PR6 `3a2664aa9f2654fed3590c420f4b922fb6591aa2` está en el historial consultado. No se repitió CI completo/API/PostgreSQL en esta auditoría.
- Nexus al abrir: últimos reportes eran los de Sol hasta32. No había nuevo cierre de Brain en esos reportes, pero sí PR yDocs recientes: ausencia de reporte no se interpretó como ausencia de avance.

Fuentes declarativas examinadas: [A01/A02](https://app.clickup.com/90171457413/docs/2kza6fw5-12557) y [incremento PR2](https://app.clickup.com/90171457413/docs/2kza6fw5-12577). Se usaron para seleccionar afirmaciones; las verificaciones técnicas se hicieron contra Git yprocesos de prueba.

## Lo que confirmé ejecutando

En directorio nuevo del taller se descargaron seis archivos del head exacto, incluidos fuente/tests/workflow, con hashes conservados. No se mezclaron archivos sucios del clon de trabajo.

```text
python3 tests/test_provenance_v2.py                 exit0,23tests OK
python3 tests/test_fuente_nacional_integridad.py    exit0,11tests OK
python3 tests/check_provenance_mutations.py         exit0
  hash_ignored: exit1,detected=true,4fallos
  authority_inferred_from_method: exit1,detected=true,2fallos
  duplicate_overwrite: exit1,detected=true,1fallo
```

Los mutantes efectivamente fallan en aserciones relevantes ycompilan. No los interpreto como cobertura total ni autenticidad jurídica. Los23y11son métodos de test; subtests no inflan ese34.

Contratos `Work`, `Version`, `DatedEvidence`, `Extraction` yserialización están presentes en [provenance_v2.py](https://github.com/gatehot59-star/corpus-legal-tarija/blob/eac03e8ac3670638fada9d1baad682edb798b5bf/contracts/provenance_v2.py). Separan autoridad de extracción, fechas, obra/edición, hash original/texto yrequieren referencia de revisión para estado evaluado. **UUID válido no valida que exista aprobación humana**, límite que Brain ya declara; no lo cuento como nuevo hallazgo oculto.

El [lector real](https://github.com/gatehot59-star/corpus-legal-tarija/blob/eac03e8ac3670638fada9d1baad682edb798b5bf/sistema/api/fuente_nacional.py) rechaza hash faltante/corto/malformado/discordante,bytesalterados,UTF8inválido,textovacío,escape por nombre de archivo ysymlink del archivo final. Eso sí cierra el defecto anterior del hash en este lector. No acredita la corrección en el servicio vivo.

## R1 · Manifiesto ausente se presenta como censo vacío sin anomalía

Archivo `sistema/api/fuente_nacional.py`, función `_lineas_json`, comienzo:

```python
if not ruta.exists():
    return []
```

Construí un directorio sintético con `texto/law.txt` válido, sin `normas.jsonl`. Constructor no lanza excepción; informe:

```json
{"censo_manifest":0,"resueltos_por_ocr":0,"resueltos_por_extraccion":0,"sin_texto":0,"faltantes":[]}
```

Crear un manifest vacío produce el mismo resultado. El control `{broken` sí lanza ValueError; un manifest válido informa censo1 ypermite leer. **La falta del archivo no se distingue de cero registros**, mientras el rechazo del JSON roto sí está implementado.

Impacto P2 de integridad/observabilidad de ingesta: configuración oarchivo ausente puede reducir el universo a0sin error señalado en este componente. **No se probó pérdida productiva ni éxito de un publicador aguas abajo**; no hay integración nacional en main que permita inferir ese efecto desde este test.

Cambio solicitado: manifest obligatorio cuando se selecciona FuenteNacional, o estado explícito fuente-no-configurada/ausente que el caller debe resolver antes de continuar. Mantener vacío legítimo si se decide permitirlo, pero diferenciándolo. Añadir pruebas ausente/vacío/válido/malformado yrechazo de publicación cuando una fuente esperada falta. Hoy `test_valid` crea el lector sin manifest ypor eso normaliza esta ambigüedad.

## R2 · Se rechaza symlink de archivo, pero se acepta symlink del directorio texto

El lector hace `root=(self.base/'texto').resolve()` antes de validar el archivo. Creé `base/texto` como enlace a `outside/`, ambas carpetas dentro de mi temporal, con un texto sintético yhash correcto. El enlace estaba fijo antes de construir el lector; **ninguna carrera ni modificación concurrente**.

```json
{"case":"texto_directory_symlink","accepted":true,"resolved_outside_base":true,"concurrent_changes":false}
```

El control `base/texto/link.txt` enlazado aotro archivo se rechaza. Por tanto, la frase «rechaza symlinks/rutas fuera del directorio» no cubre el directorio raíz. La precondición declarada de inmutabilidad evita otra amenaza, no este enlace estático.

Impacto P2 ycondicionado aconfiguración local: si la raíz autorizada es `base/texto`, resolverla sin verificar su cadena cambia silenciosamente esa raíz. Si se quiere permitir enlazar directorios de fuentes inmutables, **documentarlo como política explícita** yvalidar la raíz resuelta contra una ubicación autorizada. No llamarlo symlink-rejected en general. No se leyó ningún archivo del sistema ni se obtuvo acceso remoto.

Cambio solicitado: decidir raíz confiable, verificar symlink/root/parent según política ysumar tests positivo/negativo de raíz yarchivo. No hace falta afirmar defensa frente aatacante de mismo UID; ese límite puede seguir declarado.

## Documentación y custodia

El ADR todavía dice «B03 sigue abierto», el cuerpo del PR aún lista23tests yCI remoto pendiente. El recibo posterior corrige estado. No son fallos funcionales nuevos, pero el revisor debe actualizar cuerpo/ADR al head para que no haya dos estados incompatibles del mismo incremento.

Los logs completos de Brain estaban solo en el taller ysuJSON se declara resumen. Es honesto, pero no equivale acustodia completa enGit. En esta auditoría se conservan los logs de la nueva ejecución íntegros, comprimidos sin pérdida en el JSON de evidencia, además de las sondas legibles. No se reetiquetan sus viejos extractos como verbatim completo.

## Custos: correctivo concreto confirmado, no nueva certificación integral

Se extrajo `git archive 0f1fdae90b88014b45e58c4e1b86f21cbe449b48` aotro directorio, sin resetear el clon existente. Se leyó [test_falsador_caso.py](https://github.com/gatehot59-star/custos-legis-tarija/blob/0f1fdae90b88014b45e58c4e1b86f21cbe449b48/backend/test_falsador_caso.py) antes de ejecutar; usa sintéticos ybash, no base ni credenciales.

```text
python3 backend/test_falsador_caso.py
Ran 9 tests in 2.746s
OK
exit0
```

Confirmado: target-then-crash yrecibo incoherente se rechazan; el fallo objetivo con cierre completo se acepta. Esto verifica el correctivo de regresión incorporado por Brain. **No transforma una línea de cierre en prueba inviolable de trabajo realizado**: escenarios de fabricación deliberada de etiquetas mantienen el límite discutido anteriormente. No reejecuté los45checks HTTP ni todoCI ni declaro listoCustos.

## Estado de avance y próximo orden que revisaría

A01: Brain documentó inventario/respaldos a04:30UTC. No los remidí enVM en esta auditoría, por tanto **antecedente ajeno, no confirmación mía de disponibilidad actual**. A02 sigue parcial, con identidad del servidor yconjuntos cotejados según su reporte, no reconstrucción total por ramas. No afirmo producción intacta por leer el recibo; solo que mis pruebas no la tocaron.

B01/I05: contratos aislados verificados;persistencia,cachés,relación legacy yrevisores pendientes. B03: hash corregido en rama, dos casos de borde aresolver. A04: guion de entrevistas existe, no entrevistas. Colecciones/cuentas/piloto/cobro no implementados por estos34tests. Los controles del plan con fallas previas no se consideran reparados por este PR.

**Orden de revisión:** resolver R1/R2 con política yregresiones;actualizar ADR/cuerpoPR;publicar logs completos yrepetirCI del nuevohead. Después revisar B02/contrato legacy ypersistencia. No ordenar nuevos lotes, adopción, merge odeploy desde esta auditoría. El próximo evaluador debe revisar el head corregido, no volver aemitir un score sobre este mismo código.

## Método, evidencia y límites

TITAN FULL, lectura de PR/docs/checkruns/commits, pruebas de fuente exacta enbrain-env. Este incremento lo escribió Brain, no esta ejecución de auditoría. No se simularon aprobaciones humanas ni se confundieron los commits anteriores de Sol con avance ajeno. No se presentó revisión formal enGitHub ni se enviaron comentarios/DMsin confirmación.

Archivos de salida: `docs/auditorias/2026-09-17-05-revision-avance-brain.md` y`docs/auditorias/2026-09-17-05-revision-avance-brain-evidencia.json`. Logs crudos locales `/workspace/sol-review-corpus-20260917-1153/review-raw.json`, SHA256 `30fa0f2a6d483874d2d3c311a67f679098eefbd4dc384d1515555c89ed327800`. Incluyen todos los stdout/stderr,hashes de fuentes ysondas sin datos productivos.

NO MEDIDO: estado vivo actual deVM, cambios campo a campo de base, permisos de despliegues ajenos, restore,RPO/RTO,scan OWASP completo,coverage formal,performance10x,ejecución de todas las suitesCI deCustos, licencias/revisiónjurídica. No conté testimonios sintácticos como autenticidad, `require_url` como protecciónSSRF ni inmutabilidad como defensa contra races.

Rúbrica del informe41/45=91,1/100: completitud14/15 (scope acotado), razonamiento9/10 (no inferir producción),documentación9/10 (fuentes ylogs),aporte5/5 (casos de borde reales),QA4/5 (sin revisión institucional ajena). N/A55 de producto nuevo. **No es aprobación del PRni porcentaje de avance.** Dictamen: cambios solicitados antes de mi aprobación como contrato de ingesta.
