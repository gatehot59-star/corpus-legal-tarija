# Qué activa a Brain para retomar el laboratorio

20-sep-2026 ART. Pedido: Find what actually wakes Brain to resume work.

## Respuesta operativa

Enviar una nueva instrucción humana en la conversación Ask AI que implementaba el laboratorio: [SIGAMOS CON LOS PR DONDE NOS QUEDAMOS?.](https://app.clickup.com/90171457413/chat/r/2kza6fw5-5157/t/80170043695235). No basta con dejar la aprobación en git, Nexus o un Doc. Esos registros proporcionan contexto cuando Brain es invocado; no se comprobó ningún mecanismo que convierta sus escrituras en una nueva invocación de esa conversación.

Mensaje mínimo para enviar en ese hilo: «Retomá el laboratorio. Ya aprobé conservar el README vacío y main adicional: leé el registro98 de Nexus y docs/adr/2026-09-20-28-lab-initialization-approved.md en main, y continuá la preparación dentro del alcance aprobado».

[La aprobación pública](https://app.clickup.com/90171457413/docs/2kza6fw5-14217) también sirve como referencia directa. No se pide volver a autorizar lo mismo; se da la instrucción de continuar en el hilo correcto.

## Cómo se identificó el destino

La búsqueda de mensajes corpus-docs-trigger-lab / 267 omitidos / mantener README / 80170047155408 devolvió las respuestas de implementación bajo parent comment:80170043695235. Su raíz cargada es SIGAMOS CON LOS PR DONDE NOS QUEDAMOS?., URL https://app.clickup.com/90171457413/chat/r/2kza6fw5-5157/t/80170043695235, tipo Ask AI Conversation dentro de Brain, luz delmis tarraga. Entre sus respuestas están los lotes y el laboratorio: https://app.clickup.com/90171457413/chat/r/2kza6fw5-5157/t/80170047156119 y https://app.clickup.com/90171457413/chat/r/2kza6fw5-5157/t/80170047153775.

Este hilo de auditoría es distinto: comment:80170046873506. Hablar acá invoca esta conversación, no demuestra que se reanude la conversación implementadora.

La carga del hilo original omitió250 respuestas por tamaño. Se usa para verificar la identidad de la raíz y la relación de los resultados de búsqueda, no para afirmar que se leyó todo el historial ni para medir su estado de ejecución actual.

## Chat con Brain no equivale a Super Agent

La búsqueda dedicada de agentes por nombre Brain devolvió cero coincidencias. Eso no demuestra que no existan agentes con otro nombre; sí impide inventar un Super Agent llamado Brain y asignarle un disparador.

Nexus agentes contiene una fila brain con rol vacío y última_actividad2026-09-06T14:45:30.741Z. Es metadata vieja, no una identidad de Super Agent, un heartbeat actual ni un scheduler.

La documentación oficial consultada distingue conversaciones Brain y Super Agents. [Collaborate with ClickUp Brain anywhere in your Workspace](https://help.clickup.com/hc/en-us/articles/20658787666071-Collaborate-with-ClickUp-Brain-anywhere-in-your-Workspace) describe continuar una conversación desde AI Chats e interactuar enviando preguntas/instrucciones; también permite @brain en Chat/comentarios, pero eso no garantiza retomar esta misma instancia. [AI Hub](https://help.clickup.com/hc/en-us/articles/36954958035863-AI-Hub) distingue Recent Chats de los agentes. [Super Agent instructions, Skills, triggers, knowledge, and memory](https://help.clickup.com/hc/en-us/articles/37092796379927-Super-Agent-instructions-Skills-triggers-knowledge-and-memory) atribuye disparadores manuales, programados y automatizados a Super Agents configurados, no a cualquier conversación Ask AI.

Por eso el camino mínimo para esta instancia es un mensaje humano en su hilo original. Crear un agente o una automatización sería otro proyecto/configuración, no una condición necesaria para retomar esta conversación.

## Corrección de la expectativa anterior

Los registros28-30 demostraban aprobación disponible y ausencia de acuse visible. No demostraban que publicar esos registros notificara o activara a la otra conversación. Dejar memoria disponible no es despertar al ejecutor. No correspondía sugerir espera de un acuse automático sin identificar antes un disparador.

## Límites y acciones

Mecanismo documentado y destino identificado; reanudación efectiva NO EJECUTADA en este turno. No se envió mensaje ni se intentó simular una entrada humana, no se invocó otro agente ni se cambiaron triggers. No se afirma que Brain esté actualmente corriendo o que pueda acceder a todas las herramientas desde cualquier identidad.

No cambia permiso98/ADR28, hold17/18/19, condición de merge21 ni prohibición de despliegue. Método: búsqueda de agente y mensajes, carga de identidad del hilo, consulta Nexus y soporte oficial; rúbrica N/A para identificación acotada, sin pruebas de producto. Publicación de nota y Doc con readback y continuidad. Esta nota tampoco es un trigger.
