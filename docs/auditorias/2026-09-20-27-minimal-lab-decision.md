# Decisión mínima para destrabar la preparación del laboratorio

20-sep-2026 ART. Pedido: Identify the smallest decision unblocking the remote laboratory. Es identificación del permiso pendiente, no aprobación, ejecución ni nueva auditoría completa.

## Recomendación

Aceptar conservar el README.md vacío y la rama main predeterminada que ya existen en gatehot59-star/corpus-docs-trigger-lab. Enmendar SOLO ese desvío de inicialización: bases con22 archivos (21 originales previstos más README vacío) y siete ramas totales (seis experimentales más main), en lugar de21 archivos y seis ramas.

Texto mínimo de la decisión propuesta: «Autorizo conservar el README vacío y main adicional en el laboratorio existente; el resto del alcance aprobado no cambia».

Es la opción menor porque no borra archivos, no reescribe historia, no recrea el repositorio y no cambia el workflow ni el estímulo experimental. No requiere reaprobar todo el experimento. Los cuatro PRs, seis episodios máximos y demás límites del plan siguen siendo los antecedentes reportados por Brain; este pedido no los amplía, ni recaptura sus autorizaciones originales.

## Qué destraba y qué no

Resuelve el freno de alcance para continuar la preparación. Todavía hay que completar los11 originales faltantes, verificar hashes de las bases, diferencias old/new y diffs de los PRs, y preparar la captura antes de emitir eventos. No significa laboratorio listo ni ensayo remoto demostrado. El README debe mantenerse idéntico en los brazos y fuera de los diffs experimentales.

No es permiso nuevo para mergear PR21. La condición de ensayo concluyente y los controles vigentes siguen pendientes. No cambia la retención de PR17/18/19 ni la revisión del logout. No se envió mensaje a Brain ni se alteró el laboratorio.

## Estado reconsultado para este pedido

Nexus: el último reporte es96, auditoría26; Brain95 documenta explícitamente que el único permiso nuevo pendiente es conservar la inicialización extra. Se abrió ese registro, no se infirió de un recuerdo.

Salida actual de git ls-remote del laboratorio:

```text
0fa35d85569916c8525c490cfe854faee4a6fa14 HEAD
2480cbc16f7daf4cd41d018f591170e807a2e5e5 refs/heads/lab/docs-trigger-old-base
0fa35d85569916c8525c490cfe854faee4a6fa14 refs/heads/main
```

Respuestas actuales de GET /pulls?state=all&per_page=100 y GET /actions/runs?per_page=100:

```json
{"prs": [], "runs": {"total_count": 0, "workflow_runs": []}}
```

Main Corpus reconsultado: cc20e62cfc1ec438f87c37befb48fb0b1f027742, último informe26. Sin evidencia de ejecución remota posterior. Git refs prueban identidad de ramas, no permisos administrativos; la API acredita cero PRs/runs al consultar, no ausencia eterna.

El contenido y los diez originales ya copiados se verificaron byte por byte en la auditoría26; este turno comprueba que el head del laboratorio sigue siendo el mismo, sin repetir las111 pruebas.

[Auditoría26 y evidencia](https://github.com/gatehot59-star/corpus-legal-tarija/blob/cc20e62cfc1ec438f87c37befb48fb0b1f027742/docs/auditorias/2026-09-20-26-brain-ci-lab.md).

## Método y límites

Consulta acotada de decisión, no veredicto nuevo de producto. Instrumentos: Nexus por servicio SQLite, git fetch/log/ls-remote y REST público por brain-env. No ejecución de producto, consumo de Actions ni cambio administrativo. Se buscó actividad o decisión posterior que volviera obsoleto el bloqueo: no apareció en las fuentes consultadas. No se inspeccionaron conversaciones privadas ni la configuración global de Apps/hooks.

Rúbrica numérica N/A para esta aclaración; no se firma listo, mergeable ni verde. Escrituras limitadas a esta nota, su Doc público y continuidad Nexus; readback antes de responder. El usuario todavía no aprobó la decisión propuesta en este turno.
