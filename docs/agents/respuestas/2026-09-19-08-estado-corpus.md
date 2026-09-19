# Estado de Corpus: demo técnica integrada, producto para usuarios pendiente

19-sep-2026 ART. Pedido: estado del proyecto. Consulta documental de estado, no nueva auditoría ni ejecución de tests.

## Respuesta

Corpus tiene una demo local aislada con datos ficticios: arranque explícito, login, permisos, lectura exacta por versión y cierre de sesión persistente entre reinicios. La restauración fría sintética queda en cuarentena, sin reabrir accesos. PR14/15 y PR16 están integrados en main. Estas capacidades están respaldadas por las auditorías históricas citadas, no por una corrida nueva en este turno.

No hay avance nuevo registrado desde la última auditoría: main sigue en f2b43ce8422702dc82511e7914dd322f694d7b36 y Nexus termina en el reporte55. Esto no descarta trabajo local no publicado.

PR17 sigue abierto con cabeza 3eedba5460495bb1c329e0cd87d8305fd0e9e00a. Corrige tres sitios del fixture HTTP y fue auditado incluso con excepciones inyectadas; todavía no está integrado. El diagnóstico de169 omisiones de cierre explícito restantes corresponde a10 sitios de4 archivos de pruebas, no a169 defectos productivos. Los17 eventos HTTP corregidos en la rama de PR17 no están incluidos en esos169. El criterio de cierre todavía no protege CI.

La prioridad de producto sigue siendo concretar el recorrido buscar, verificar fuente y versión, guardar referencia y reportar un error. La matriz de reutilización e integración con la interfaz histórica continúa pendiente en los registros revisados. Recomiendo terminar el arreglo acotado del banco y pasar a ese recorrido, no abrir otra ronda global de auditorías sin cambios.

No presentarlo como producto listo para cobrar: no se acredita despliegue productivo, piloto con usuarios ni validación jurídica. Tampoco se acredita reconciliación de permisos actuales y reapertura después de restaurar. PR1 permanece abierto y excluido.

## Fuentes leídas

- docs/agents/respuestas/2026-09-19-05-auditores-cierre-http-pr17.md
- docs/auditorias/2026-09-19-07-auditoria-brain-pr17.md (veredicto, resultados y pendientes; la visualización conjunta quedó cortada posteriormente, sin usar ese recorte como evidencia experimental completa).
- docs/auditorias/2026-09-19-04-revision-astra-merge-pr16.md (resultado, integración, instrucciones y límites).
- Nexus reportes48 a55 y listado GitHub de PRs abiertos, consultados de nuevo.

[PR17](https://github.com/gatehot59-star/corpus-legal-tarija/pull/17). [PR1 excluido](https://github.com/gatehot59-star/corpus-legal-tarija/pull/1). [Última auditoría](https://github.com/gatehot59-star/corpus-legal-tarija/blob/f2b43ce8422702dc82511e7914dd322f694d7b36/docs/auditorias/2026-09-19-07-auditoria-brain-pr17.md).

## Instrumento y evidencia de estado

Herramientas: GitHub para PRs y publicación documental; Gateway build para fetch/lectura de Git, sqlite para Nexus; ClickUp para Doc público. Sin merge, despliegue, cambios de producto, nuevas suites ni Actions.

Tras git fetch origin main, exit0, estas salidas se obtuvieron en /workspace/sol-contexto-corpus-20260917. Todos los stderr de los cuatro comandos siguientes fueron vacíos.

```text
$ git rev-parse origin/main
f2b43ce8422702dc82511e7914dd322f694d7b36
exit=0

$ git diff --name-only 2e06380900eef97ec7290e5cd25e38d1ef96e17e origin/main
docs/agents/evidencia/2026-09-19-05-cierre-http.json
docs/agents/respuestas/2026-09-19-05-auditores-cierre-http-pr17.md
docs/auditorias/2026-09-19-04-revision-astra-merge-pr16.md
docs/auditorias/2026-09-19-04-revision-astra-merge-pr16/evidence.xz.b64
docs/auditorias/2026-09-19-06-sqlite-callers.md
docs/auditorias/2026-09-19-06-sqlite-callers/evidence.json
docs/auditorias/2026-09-19-07-auditoria-brain-pr17.md
docs/auditorias/2026-09-19-07-auditoria-brain-pr17/evidence.xz.b64
exit=0

$ git merge-base --is-ancestor 9913d8dd5074d6aedd0d261c42caea6480e794fe origin/main
stdout vacío; exit=0

$ git merge-base --is-ancestor 2e06380900eef97ec7290e5cd25e38d1ef96e17e origin/main
stdout vacío; exit=0
```

La comparación sólo enumera documentación posterior al último merge productivo. La API GitHub listó PR17 y PR1 abiertos, con cabezas 3eedba5460495bb1c329e0cd87d8305fd0e9e00a y2360f27d43fdc9a1e2a74a3f6465698918df2ad1 respectivamente. Nexus último55, turno2026-09-19-07-auditoria-brain-pr17, fecha2026-09-19 16:32:53. Son lecturas de estado, no un test de producción.

## Cierre

Archivo generado: este informe. CONFIRMADO documentalmente: revisiones y PRs abiertos, integración previa y ausencia de delta de producto publicado. NO MEDIDO en este turno: runtime, CI nuevo, trabajo local no publicado, piloto, utilidad jurídica y comercial. Gates experimentales N/A: no se ejecutó un banco nuevo. Publicación, lectura remota, Doc público y Nexus se verifican antes del chat; este texto no los anticipa como ya completados.
