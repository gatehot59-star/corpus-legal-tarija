# La aprobación está localizable; lectura por otra instancia no demostrada

20-sep-2026 ART. Pedido: Check whether Brain can find my approval.

CONFIRMADO: la aprobación se recupera por los tres puntos de entrada compartidos que se comprobaron ahora:

1. Nexus: SELECT id,agente,turno,resumen,ts FROM reportes ORDER BY id DESC LIMIT 3 devuelve98 como primer registro, con APROBACION HUMANA EXPLICITA, alcance22/7 y links a Git/Doc. También devuelve97 pendiente como antecedente, expresamente superado por98.
2. Git: fetch origin main, log -3 y ls-tree devuelven ae9d345efecdb9b5fb1b2d851e098d558529eed3 como último commit al consultar y docs/adr/2026-09-20-28-lab-initialization-approved.md presente. git show origin/main de ese archivo recupera la aprobación literal y sus límites.
3. ClickUp: búsqueda de documentos del workspace con términos Aprobado conservar README vacío main adicional devuelve la página de aprobación como primer resultado y el Doc público también entre los resultados. Está indexado; no hace falta conocer su identificador ni pedir al usuario que lo reenvíe.

[Decisión canónica en git](https://github.com/gatehot59-star/corpus-legal-tarija/blob/ae9d345efecdb9b5fb1b2d851e098d558529eed3/docs/adr/2026-09-20-28-lab-initialization-approved.md).

[Doc público de aprobación](https://app.clickup.com/90171457413/docs/2kza6fw5-14217).

NO MEDIDO: que una instancia distinta de Brain ya lo haya leído o haya reanudado el laboratorio. Encontrabilidad no acredita recepción ni ejecución. No se invocó un agente, no se envió mensaje ni se modificó el laboratorio. La comprobación acredita disponibilidad por estas herramientas compartidas, no permisos de todas las identidades hipotéticas.

Conclusión: sí puede localizarlo por su consulta de continuidad, main o búsqueda ClickUp. No necesita una nueva aprobación del mismo desvío. Los demás controles y condiciones de merge permanecen.

Método: lookup acotado, no nueva auditoría de producto. Fuente primaria humana preservada en ADR28; Nexus y git reconsultados, índice consultado en vivo. Sin nueva prueba de runtime, rúbrica N/A. Publicación de esta nota, espejo público y continuidad antes del cierre; no confundir esas escrituras con notificación a Brain.
