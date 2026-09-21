# Qué falta para terminar Corpus, sin confundir proceso con producto

21-sep-2026 ART. Explicación del estado verificado en la auditoría01; no otra corrida ni estimación de plazos. Nexus consultado: sin reportes posteriores a104. Eso no descarta cambios fuera del registro.

Abraham tiene razón en cuestionar la demora: las fuentes revisadas no justifican atribuir semanas de trabajo únicamente a complejidad técnica. Se encadenaron auditorías de auditorías, bancos de pruebas y un laboratorio de CI mientras la entrega completa seguía pendiente. Ese trabajo encontró fallos reales, pero no equivale a terminar el sistema. Mi recomendación anterior volvió a poner el laboratorio primero: no demostré que sea dependencia funcional del piloto. Fue una mala prioridad presentarlo como si destrabara por sí mismo el producto.

Ya existe el núcleo: almacenamiento/lectura por versión, permisos y sesiones. En ramas están el recorrido de navegador, búsqueda protegida y descarga de referencias, probados con datos ficticios. No falta inventar todo eso otra vez.

Falta para una entrega usable:
1. Integrar las piezas de navegador/búsqueda/referencias después de la revisión independiente requerida; la restricción sobre PR17/18/19 no se levanta en esta explicación.
2. Conectar una colección real delimitada y autorizada, cuentas reales y sus permisos. No sirve quitar las restricciones del lanzador sintético y llamarlo producción.
3. Completar el envío privado de errores y la operación mínima: entorno aprobado, respaldo y recuperación que permita volver a servir sin restaurar accesos revocados.
4. Probar ese recorrido con usuarios y entregar instrucciones para que otra persona lo opere.

Revisión de documentos, licencias y privacidad es una aceptación del contenido, no una nueva función informática. No se acreditó una muestra aprobada en las fuentes examinadas; no se afirma inexistencia universal.

Conclusión: hay componentes construidos, pero falta integración y entrega real. Los tests y reportes no sustituyen ese resultado. Recomiendo fijar una única versión mínima y cerrar su recorrido; nuevas auditorías solo sobre cambios o riesgos concretos. El fallo del observador debe impedir aprobar su experimento, no convertirse sin evidencia en bloqueo de todo Corpus. No se eliminan controles necesarios ni se conceden merges/despliegues.

No hay medición válida del esfuerzo restante: prometer dos días o un porcentaje sería inventar. Tampoco se ha medido una atribución cuantitativa de todo el tiempo histórico.

Evidencia: docs/auditorias/2026-09-21-01-brain-lab-observer.md en a7544842862f2798790bb2f00ab4687e9b8ee27f; Doc https://app.clickup.com/90171457413/docs/2kza6fw5-14337 y Nexus104. Esta nota no afirma que se hayan reejecutado pruebas ni que una búsqueda de reportes sea comprobación exhaustiva del repo.
