# Diseño: publicar documentación sin eludir la revisión del código

20-sep-2026 ART. Pedido: diseñar el circuito documental sin debilitar revisión. Es una propuesta, no una modificación de reglas, permisos, workflows ni del método vigente. PR17/18/19 quedan abiertos hasta revisión independiente de PR18 conforme a la orden posterior de Abraham. PR1/20 intactos.

## Decisión propuesta

**Separar publicación verificable de aceptación en main.** Todo cambio a main, documentación incluida, pasa por PR y aprobación independiente. Los informes pueden quedar disponibles inmediatamente en una rama documental y un Doc público, sin fingir que ya están aceptados en main. Así no necesitamos una cuenta exenta que también pueda colar código.

No promete documentación integrada inmediatamente sin revisor: eso sería incompatible con exigir aprobación para todo main. Sí permite registrar trabajo y continuar sin perder contexto mientras se espera la revisión.

## Circuito

1. Al cerrar una ejecución, crear rama docs/<fecha>-<entrega> desde main vigente y publicar informe, fuentes del instrumento y evidencia sintética. Capturar comandos/salidas completos y excluir secretos antes de cualquier push; la rama sigue siendo pública. No modificar ramas de producto ni usar force-push para reescribir evidencias previas.
2. Recuperar los bytes del commit remoto, reconstruir los paquetes y comparar con la captura local. Enlazar siempre blob/<SHA>/ruta, no depender de una rama mutable. Fuente del candidato y fuente del instrumento llevan sus propias revisiones.
3. Crear Doc público y registro Nexus con estado PUBLICADO, PENDIENTE DE REVISIÓN: SHA documental, SHA de producto, archivo, hashes, límites y PR documental si existe. Abrir o actualizar el PR documental con el visto bueno exigido para crear solicitudes o notificar; no enviar pedidos duplicados. Se pueden agrupar recibos compatibles para reducir carga de revisión, manteniendo sus identidades y fuentes.
4. Otra cuenta autorizada revisa y aprueba el último cambio. El PR documental NO aprueba el producto al que se refiere, ni su autor puede convertir su propio informe en aprobación independiente. Un recibo experimental puede ser válido aunque todavía espere aceptación documental.
5. Integrar solo al cumplir la política, comprobar que el contenido aceptado coincide con lo revisado y que está en main, y actualizar Doc/Nexus a INTEGRADO. Nuevos hallazgos se añaden como correcciones trazables, no borrando resultados adversos. No es necesario otro commit solo para decir que el anterior fue integrado.

## Protección propuesta para main

Requerir PR, al menos una aprobación válida, descarte de aprobaciones obsoletas y aprobación del último push por una cuenta distinta de quien lo hizo. Aplicar también a administradores, sin bypass para Brain, Astra, bots ni publicadores documentales. Bloquear force-push y eliminación. Una cuenta distinta es condición técnica necesaria, no prueba de independencia intelectual: quien revise no debe haber escrito el cambio y debe declarar alcance y pruebas.

No exceptuar docs/** ni *.md del requisito de revisión. Un archivo Markdown puede contener instrucciones operativas, una fuente de test o contenido que después consume un build. CODEOWNERS puede ayudar a enrutar revisores y proteger .github y su propio archivo, pero no reemplaza aprobación ni justifica dar bypass al publicador. No proponer aprobaciones automáticas emitidas por la misma identidad autora.

## CI documental que no afloje el de código

Antes de activar checks obligatorios, adaptar su disparo para que no queden pendientes eternos en PR solo-documentales. La configuración clean-snapshot observada usa filtros de paths: exigirla sin adaptar su disparo puede bloquear PR documentales.

Propuesta a implementar por PR revisado: un workflow en pull_request sin filtros globales de paths, un clasificador conservador y un resultado final requerido. Documentación pura recibe validación de formato, manifiestos, hashes y límites de paquetes. Cualquier ruta no reconocida, rename desde fuera del área permitida, symlink, cambio de modo o mezcla con producto requiere las suites de código; fallo o incertidumbre al clasificar bloquea, nunca aprueba por defecto. AGENTS, instrucciones operativas, política, manifiestos consumidos por producto, workflows y el propio clasificador son cambios de control, no una vía rápida editorial.

El resultado final debe ejecutarse aunque un job anterior falle y COMPROBAR sus conclusiones: usar always() no convierte fallos o cancelaciones en éxito. Solo acepta omisión de suites de código cuando el clasificador válido demuestra que no corresponden. No usar [skip ci] para destrabar un check requerido. Fijar el origen esperado del check cuando GitHub lo permita; mantener aprobación humana independiente incluso si CI da verde. No ejecutar scripts extraídos de evidencia ni texto de documentos como parte del validador. Descompresión con límites de tamaño/tiempo; enlaces se validan de manera restringida, sin exponer secretos ni permitir acceso arbitrario a servicios internos.

Estos controles son DISEÑO, no tests implementados ni una certificación del clasificador futuro. Hasta validar ese CI, es preferible ejecutar suites existentes también para docs antes que añadir una excepción silenciosa.

## Cambio necesario en nuestro método

Hoy el cierre completo exige informe en main y admite push directo documental. El nuevo circuito requiere aprobar una enmienda explícita: PUBLICADO pendiente de revisión es un checkpoint durable, no entrega integrada; COMPLETO mantiene como requisito incorporación a main más Doc y Nexus verificados. No reescribir retrospectivamente el estado de entregas anteriores.

Con una sola cuenta habilitada, los PR documentales podrían publicarse pero NO aprobarse conforme a esta política. Antes de activar protección hace falta un revisor real con otra cuenta y permisos suficientes. Ningún token nuevo de la misma cuenta resuelve esto. Sin ese revisor, preservar ramas/Docs permite avanzar en documentación, pero no integrar a main.

## Pruebas de aceptación previas a activar

En repositorio o rama de ensayo autorizados: push directo de docs rechazado; push directo de código rechazado; PR documental sin aprobación bloqueado; PR documental aprobado con checks válidos integrable; PR mixto activa controles de código; cambio de workflow/clasificador no toma vía editorial; nuevo commit obliga nueva aprobación según política; autor no se autoaprueba; administrador no tiene bypass; fallo/cancelación de test o clasificación no puede producir éxito final. Verificar lectura de informe por SHA antes y después del merge y continuidad aunque la rama se elimine en otro momento.

Son pruebas PROPUESTAS, no ejecutadas. No probar barreras escribiendo en main del proyecto sin autorización.

## Implementación por etapas, pendiente de aprobación

Primero incorporar revisor independiente y acordar enmienda del método. Después construir y revisar el circuito documental/CI en PR separado, probar la matriz anterior y recién entonces activar protección de main. No activar primero para descubrir después que nadie puede aprobar o que los checks de docs no corren. La aprobación de este diseño no autoriza invitaciones, cambios de permisos, CI, reglas ni merges de PR abiertos.

## Estado consultado y fuentes

Consulta en este turno: main ffbfd7ea0200b244343485985840b04b14953a42; reglas aplicables a main vacías; PR1/17/18/19/20 abiertos con sus cabezas previas. La consulta autenticada inmediatamente anterior listó únicamente la cuenta propietaria gatehot59-star como colaborador admin. No se ha demostrado otro revisor elegible.

GitHub: [protección de ramas](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule), [CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners), [checks requeridos y workflows omitidos](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks).

## Método y cierre de esta propuesta

Lectura de estado y documentación oficial; diseño acotado, no auditoría experimental nueva. Gate de runtime N/A: no se implementó ni ejecutó el nuevo circuito. Esta propuesta se publica bajo la regla documental ACTUAL, antes de cualquier protección; no constituye una excepción al diseño futuro. Archivo versionado y Doc público con lectura posterior, más continuidad Nexus. Sin modificaciones de configuración ni nuevos PR/comentarios/review requests/invitaciones/merges/despliegues.
