# Dos bypass del grafo enmendado, sin cambiarlo: trabajo fuera de gates y aprobación reutilizada

17-sep-2026. Pedido de Abraham: intentar saltear los gates de aprobación del plan enmendado. **Prueba adversarial de mi propia entrega**, no una auditoría independiente. No ejecuté tareas reales, no falsifiqué actas reales y no modifiqué el plan ni permisos del producto.

## Veredicto

**La tabla todavía permite dos clases de ejecución que sus reglas en prosa no autorizan.** C04 y C06.1 son alcanzables sin A08/A09/I02/I08/I09; además, una única finalización de I09 sirve como dependencia para varios lotes aunque el acta sintética autorice solo uno. Las44 invariantes anteriores siguen pasando exactamente.

Esto **no significa que la prosa conceda permiso**, ni demuestra una vulnerabilidad remota o que un ejecutor real haya aceptado esa ejecución. Demuestra que las dependencias y su verificación no bastan para imponer el alcance de la aprobación. Un humano o un ejecutor que valide el acta correctamente debe rechazar las trazas descritas. La advertencia «las actas deben existir realmente» se conserva, pero no está representada como predicado verificable en la tabla.

Sujeto exacto: [enmienda v2](https://github.com/gatehot59-star/corpus-legal-tarija/blob/3b6cb6d85a012e8a277668fa8c12515236b91c27/docs/agents/respuestas/2026-09-17-03-enmienda-plan-corpus-v2.md), SHA256 `92f3bbc2d6b15a8896e43dffeef526813aff1ddf594d85f898562ee550a08d90`. Instrumento anterior: [44 invariantes publicadas](https://github.com/gatehot59-star/corpus-legal-tarija/blob/82bc3cd0e7e5c437ab0563d49f7daae00ecc20b6/docs/agents/evidencia/2026-09-17-03-enmienda-plan-corpus-v2.json).

## 1. Trabajo que escapa a la aprobación de la muestra

Manteniendo como NO COMPLETADAS las cinco decisiones A08,A09,I02,I08,I09, el recorrido topológico alcanza:

- **C04:** adaptador local piloto, censo y muestra Tarija/Gran Chaco; depende solo de B06 y A06.
- **C06.1:** primer lote agrario/laboral de hasta cinco instrumentos; depende solo de A06 y B06.

Trayectoria común reproducida:

```text
A01 → A04 → A02 → A05.1 → A03 → A05.2 → B01 → A05.3 → B06 → A05.4 → A06 → C04
```

La última tarea puede ser C06.1 con los mismos antecesores. Las flechas representan orden de una traza permitida, no necesariamente aristas directas. A03/A06 implican trabajo jurídico previo: **no digo que no haya revisión jurídica alguna**; digo que ninguna de las cinco decisiones bloqueadas se necesita para llegar.

La enmienda §2 dice que A09 cubre «primer lote por serie y B05» y enumera B01/B02/B03/B04/B06/B07 como diagnósticos/prototipos reversibles. C06.1 no tiene A09 como antecesor; C04 tampoco está en la lista de excepciones y puede producir un adaptador. **C06.1 es el ejemplo inequívoco del lote omitido.** Si C04 se pretende solo exploratorio, debe especificarse esa frontera y separarse de la integración adoptada, en lugar de asumir aprobación implícita.

Controles: con las mismas decisiones bloqueadas, **C01.1 no es alcanzable**, porque requiere A09/B05; **D01 tampoco**, porque requiere A08/I02. El instrumento no permite pasar todo por construcción.

Consecuencia: alcance/costo de trabajo anterior al piloto todavía puede crecer fuera del mecanismo que se agregó para limitarlo. Las barreras posteriores de publicación no se eliminan: no demostramos un acceso a F08 sin permisos ni una publicación real no autorizada.

## 2. I09 aprobado una vez se puede reutilizar para lotes no cubiertos

La enmienda §5 dice:

> I09 exige disponibilidad J/D,costos de edición/revisión/soporte ytope;autoriza lote siguiente,no toda la hoja de ruta. Nuevo exceso vuelve a decisión.

Pero el grafo tiene **un solo nodo I09** y todas las ocurrencias siguientes dependen de ese mismo nodo. No hay una nueva autorización por lote ni consumo del límite en el contrato de dependencias.

Fixture sintética declarada: I09 contiene aprobación válida únicamente para **C01.2**, con máximo **4h**. Se consideran completados, con resultados aceptados sintéticos, todos los antecesores necesarios para comenzar C01.2. No se usa una aprobación falsa ni se aprueba nada real.

| Ocurrencia | Dependencias cumplidas | Acta cubre ocurrencia y saldo | Horas previas simuladas |
| --- | --- | --- | ---: |
| C01.2 | sí | sí |0|
| C01.3 | sí | **no** |4|
| C01.4 | sí | **no** |8|

El grafo permite encadenar las tres y acumular12h, aunque la aprobación cubría4h y una sola ocurrencia. El predicado de alcance usado como control rechaza C01.3/C01.4. **No es una prueba de que un software de autorización existente acepte esa acta**: no se encontró ni invocó un ejecutor de approvals; es un contraejemplo a convertir el DAG del plan en autorización suficiente.

No hace falta alterar una sola arista para producirlo. El grafo tampoco lleva versión del alcance, vigencia/revocación de la decisión ni saldo consumido: evaluar permisos con esos atributos requiere un contrato adicional, no otra búsqueda de antecesores.

## 3. Por qué las44 comprobaciones no lo vieron

Volví a evaluar todas las claves publicadas de `positive_invariants` sobre la enmienda sin cambios: **44/44 idénticas y verdaderas**. Preguntan si I08/I09 preceden C01.2 y siguientes, si D09 precede F08, si el piloto evita pagos y si la demo evita C08.

Ninguna exige que C06.1 tenga autorización de muestra. Ninguna pregunta si el acta I09 vigente **autoriza esta ocurrencia**, esta versión de alcance y este costo. Es la diferencia entre **precedencia estructural** y **autorización aplicable**. Las44 no eran falsas, pero no justificaban la garantía más amplia que quería obtener.

## 4. Corrección recomendada, no aplicada

1. Clasificar cada ocurrencia como lectura/ensayo reversible/integración/curación/publicación/gasto y verificar que tenga el gate exigido para esa clase. C06.1 necesita autorización de muestra; C04 debe separar exploración de adopción o depender de la aprobación correspondiente.
2. Modelar `ApprovalDecision`: decision_id,scope_revision,allowed_occurrences,budget_hours y/o importe/moneda,issuer,decision,valid_from,expires_at,revoked_at,evidence_digest. No basta marcar el nodo completado.
3. Repetir decisión por lote o usar un gate parametrizado obligatorio al iniciar cada ocurrencia: autorización vigente, alcance exacto, saldo suficiente y reserva de saldo atómica. Repetir/reintentar una tarea debe ser idempotente, no doble consumo ni doble permiso. Cambiar alcance, retirar aprobación o exceder presupuesto bloquea hasta decisión nueva.
4. Hacer tests de trazas, no solo ancestros: acta para otro lote, acta rechazada/expirada/revocada, cambio de versión, agotamiento y ejecución paralela contra un mismo saldo. Mantener controles positivos para lectura permitida y lote legítimo; no frenar toda investigación por defecto.

No agregué estas reglas a la enmienda: el pedido fue atacarla. El plan vigente no cambió en este turno.

## 5. Evidencia y reproducción

Instrumento: Python3 en **brain-env vía gateway build.run**. Descarga del raw exacto, SHA256 contra pin conocido, parser restringido a §7,110nodos. Estado de ejecución enteramente sintético. No se importaron ejecutores, plugins o contenido de proveedores para correrlos.

Algoritmo utilizado:

- Construir diccionario de dependencias con regex de IDs y sufijos; sumar ancestros con caché por grafo.
- Recalcular las44 claves del JSON previo; exigir igualdad con sus valores publicados.
- Para cada objetivo, tomar su conjunto de ancestros y completar únicamente nodos no bloqueados cuyas dependencias estén aceptadas. Registrar el orden íntegro.
- Para replay, comenzar con los ancestros de C01.2 completados sintéticamente. Acta solo para C01.2 y4h. Por cada lote2,3,4 comparar `set(deps)<=done` contra `target in allowed_occurrences and spent+hours<=max_hours`. Registrar y avanzar únicamente el modelo de dependencias.

**Salida cruda completa:** `docs/auditorias/2026-09-17-04-bypass-aprobaciones-plan.json`, mismo commit. Exit0 significa ensayo ejecutado, no plan correcto. Estado local `/workspace/corpus-plan-gates-bypass-20260917/raw-result.json`.

### Método y límites

Pedido: bypass de gates de la enmienda. Lectura de Nexus, archivo exacto Git e invariantes previas; inventario/método leídos en la conversación y sin afirmar nuevos límites de máquinas. Ejecución acotada propia, no auditor independiente de mi implementación. Escrituras: reporte y evidencia, Doc público y cierre Nexus; no plan/actas/producto.

QA aplicable al **informe**, no al plan: Completitud14/15 (dos ataques y controles, no barrido exhaustivo), razonamiento9/10 (separa tabla de autoridad real), documentación9/10 (salida íntegra y algoritmo; no ejecutor real), innovación5/5 (replay de alcance más allá de ancestros), proceso4/5 (self-test declarado, evidencia cruda).41/45=91,1/100;N/A55 de ejecutabilidad/seguridad/testing/DevOps de producto. No invocar ese score como aprobación de la secuencia atacada.

NO MEDIDO: cualquier sistema real que consuma las actas, comportamiento humano futuro, correcciones de contenido, productividad, recursos J/D, producción y permisos remotos. No se prueba vulnerabilidad de AccessGrant del producto ni se falsifica una decisión humana.

**Qué faltaba medir y sí importaba:** cobertura de gates por clase de trabajo y aplicabilidad de un acta al lote actual. Las dos preguntas no se resuelven demostrando que una aprobación ocurrió antes.
