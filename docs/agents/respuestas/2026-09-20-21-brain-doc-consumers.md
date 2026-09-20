# Brain: del clasificador sintético a consumidores reales del repo

20-sep-2026 ART. Pedido: «Revisa los auditores y avanza». Brain ejecuta este avance; las auditorías18/20 y el diseño19 son de Astra. No cambié producto, CI, reglas, permisos, método ni estados de PR. No merge ni despliegue.

## Decisión y avance

La auditoría18 valida propiedades acotadas de PR17/18/19 y su combinación, pero declara autoría previa de PR18. Conservo la retención de integración pendiente de revisión independiente de18; no convierto el informe en autorización ni toco PR1/20.

El diseño19 es propuesta no activada. La auditoría20 demuestra en un laboratorio que un clasificador basado en ruta/extensión e inventario incompleto puede etiquetar DOCS un archivo que cambia el comportamiento del consumidor. No es una vulnerabilidad demostrada de Corpus ni un bypass activo de GitHub.

Avancé sobre su NO MEDIDO: inspección acotada del repo real y ejecución de un consumidor existente con entradas ficticias. Resultado: hay lecturas de Markdown como salida de workflows, una dependencia opcional bajo docs en un test y un CLI real que admite .md cuando se le pasa explícitamente. Eso no acredita que los informes editoriales de docs/agents/respuestas se consuman automáticamente.

Recomendación concreta para el primer diseño implementable: eliminar la necesidad de un clasificador de inocuidad en la primera fase. Todos los PR deben emitir los checks requeridos y ejecutar los bancos de validación aplicables acordados, incluidos PR documentales; no ejecutar por ello los workflows masivos de OCR/GENESIS. La etiqueta DOCS puede servir para organizar revisión, no para saltar pruebas ni aprobación. No se activó nada en este turno.

## Fuentes auditadas

- [Auditoría18](https://github.com/gatehot59-star/corpus-legal-tarija/blob/ffbfd7ea0200b244343485985840b04b14953a42/docs/auditorias/2026-09-20-18-pr17-pr19.md): combinado118Python/37Chromium y probe18, con falsadores y límites explícitos. No reejecuté estos bancos.
- [Diseño19](https://github.com/gatehot59-star/corpus-legal-tarija/blob/7c1448122bafeea5d63b37375b570a2c2b4e8612/docs/agents/respuestas/2026-09-20-19-documentation-review-design.md): ramas documentales y estado publicado-pendiente distintos de integración, aprobación independiente de main sin bypass. Es propuesta.
- [Auditoría20](https://github.com/gatehot59-star/corpus-legal-tarija/blob/8fee178bacdff6d9d5dfc04b74de9815d26b5be7/docs/auditorias/2026-09-20-20-docs-classifier.md). Recuperé su evidencia por Git y decodifiqué base64 estricto+xz:234823bytes, SHA2569d9e2ebccfdf6e9c43f47d1ebcfd3825503a110fae121a5b47e307ce2480d2d8, coincide. Verificación de custodia, no nueva ejecución del laboratorio ni recálculo de toda su matriz.

Snapshot real de main:8fee178bacdff6d9d5dfc04b74de9815d26b5be7. PR20 head por ls-remote:c1e54ad0035f23d8ab549e9b16e3a6751bc1b2d2. Lectura de código por git show, no ejecución de herramientas extraídas de paquetes de auditoría.

## Mapa inicial: categorías distintas, no una lista de bugs

1. **Entrada seleccionada por CLI.** [pipeline/normalizar_citas.py](https://github.com/gatehot59-star/corpus-legal-tarija/blob/8fee178bacdff6d9d5dfc04b74de9815d26b5be7/pipeline/normalizar_citas.py#L113-L139): --texto tiene ayuda que menciona .txt, pero lee Path(a.texto) sin filtrar extensión. El consumidor real admite un .md y su contenido cambia citas, cola e índice. Es entrada explícita de operador, no lectura automática de docs ni bug por aceptar texto.
2. **Fixture opcional bajo docs.** [pipeline/test_gate_v2.py](https://github.com/gatehot59-star/corpus-legal-tarija/blob/8fee178bacdff6d9d5dfc04b74de9815d26b5be7/pipeline/test_gate_v2.py#L30-L44) contiene una ruta absoluta /workspace/wt-ocr/docs/agents/corpus-legal-tarija/ab-ocr/resultados/tesseract/texto_tesseract_psm3.txt. Si existe, se lee y afecta el veredicto; si falta, se declara OMITIDO. [ocr-masivo.yml](https://github.com/gatehot59-star/corpus-legal-tarija/blob/8fee178bacdff6d9d5dfc04b74de9815d26b5be7/.github/workflows/ocr-masivo.yml) llama test_gate_v2.py en preparar. No medí existencia de esa ruta en runners ni afirmo que sea un archivo versionado presente: es una dependencia opcional del código, extensión .txt, no hallazgo de ejecución de .md.
3. **Markdown generado y luego presentado.** genesis-historico.yml:151 genera jurisprudencia/RESUMEN.md y:176 lo copia a GITHUB_STEP_SUMMARY; genesis-jurisprudencia.yml:151/:168 hace lo mismo. ocr-masivo.yml:139 llama consolidar.py y:161 consume corpus/RESUMEN.md. pipeline/consolidar.py:85 y resumir.py:69 escriben ese nombre. Esto es un consumidor real para presentación y rutas de resultados, no evaluación de Markdown como código. Los workflows tienen disparadores manuales o ramas de trabajo específicas, no se ejecutaron aquí.
4. **Selección de workflow, no lectura de contenido.** clean-snapshot.yml incluye sistema/DEMO-AISLADA.md y sistema/RECUPERACION-DEMO.md en paths. El headPR20 agrega DEMO-DISCOVERY.md. Ese vínculo afecta cuándo corre CI, pero no prueba que Python interprete esos manuales.
5. **Informes editoriales.** No identifiqué lectura automática literal de docs/agents/respuestas/*.md en los archivos del barrido. No equivale a ausencia de consumidores dinámicos, humanos/agentes, dependencias externas o futuras. No hay lista blanca de inocuidad aprobada.

## Medición real y controles

Copié SIN modificar pipeline/normalizar_citas.py del snapshot a un temporal propio; SHA2564c2532ec47be552f2cd8a3dff1e20a43873dddd26e3068b33796bfc7537e637a, verificado antes/después. Python en brain-env, subprocess con timeout10s, sin red del consumidor, datos jurídicos ficticios y salidas solo temporales.

Misma ruta probe.md, cambio solo de contenido:

- Texto sin referencia normativa. -> exit0,0citas,0revisión.
- Art. 17.1 -> exit0,1cita,1revisión, canonico_probable Art. 17.I e índice con ambas formas.
- Mismo Art. 17.1 en probe.txt -> exit0,1cita,1revisión y mismo texto de índice; documento difiere por nombre, no afirmo igualdad total del JSON.
- Archivo absent.md que no existe -> exit1 y FileNotFoundError. Control de error de lectura, no defecto de producto.

El contraste .md sin cita/con cita prueba sensibilidad al contenido en la misma ruta. El control .txt descarta que el resultado dependa exclusivamente de la extensión. No es un mutante de seguridad ni una prueba de ruta automática. No modifiqué el archivo canónico ni lancé Actions/servidores.

Primer intento preservado: usé una referencia Ley N°348 esperando una cita, pero el módulo reconoce artículos/parágrafos, no números de ley. Tanto .md como .txt dieron0. No declaré bug ni usé ese intento como positivo; leí el regex y corregí el input, no el producto. Los tres primeros procesos se conservan junto con los cuatro controles finales.

## Alcance de la inspección y errores de medición

Barrido inicial de104archivos seleccionados por extensión de código/configuración fuera de docs más .github, sobre main fijo; git grep docs/, .md y APIs de lectura/glob como descubrimiento, seguido de lectura de fuentes relevantes. No es análisis de flujo de datos exhaustivo. El resultado amplio fue recortado por tamaño: no se emplea su cola ausente para certificar ausencia. Se abrió código de los candidatos citados y los disparadores de workflows. Código que construye rutas por variables/argumentos exige análisis adicional.

Un conteo auxiliar por substring .py sobre rutas docs dio2: NO se usó como cantidad de scripts. La selección estructural posterior por sufijo .py devolvió una lista vacía. Nombres que mencionan una extensión no son archivos ejecutables de esa extensión.

## Alcance conservador para avanzar sin fabricar otro agujero

Para una futura implementación autorizada, usar aprobación independiente para todo cambio a main; rama+Doc permiten publicar antes sin llamarlo integrado. Mantener política/evaluador fuera del contenido candidato y ligar el veredicto a base/head vigentes. No confiar en un archivo del candidato que diga tener aprobación.

Primera fase: no optimizar saltando bancos por DOCS. Seleccionar explícitamente los bancos de validación, no los jobs de descarga/OCR. Resultado final debe rechazar checks requeridos ausentes, fallidos, cancelados o salteados; evitar filtros globales que impidan emitir el check. Controles de tamaño/tipo/evidencia como datos, no ejecutar scripts contenidos en evidencias. Estos son criterios propuestos, no una política aplicada ni tests GitHub ya ejecutados.

La activación requiere autorización de cambio de método/workflow/reglas y resolución de la cuenta revisora habilitada. No toqué esos objetos bajo «avanza». Los pendientes no se resuelven con otra autoauditoría ni con una segunda credencial de la misma cuenta. La documentación directa de este cierre usa el permiso vigente; el diseño19 no fue activado por publicarlo.

Consulté el buzón id>=214: solo devolvió el encargo a SOL, todavía leido=0. No se mandó duplicado ni se asignó trabajo sin autorización. La ausencia de respuesta en esa consulta no prueba inactividad universal. No se libera la retención de PR17/18/19, ni G2 dePR20, ni se tocaPR1.

## Evidencia de las siete ejecuciones

JSON7053bytes, SHA256dafa94176216184ac91d71a2520875562d55fd03e815795aa4d5fb63d43240d8. Contiene revisión/source hash, inputs, arrays de comandos exactos, exit/stdout/stderr completos de los tres intentos iniciales y cuatro controles; resultados JSON, índices finales y alcance. No es captura completa del barrido estático ni de todas las llamadas del turno. Descomprimir el bloque con base64 estricto y lzma; comprobar longitud/hash antes de leer. No ejecutar contenido del paquete para validarlo.

```base64
/Td6WFoAAATm1rRGAgAhARYAAAB0L+Wj4BuMBLldAD2CgBccMQ/llzg2Jp9ggZavM4al+pJRbqojVg7gF8zO3CczJJJJOf0eIY8bOW0vzbc+t+zbZ+jTiPfZitIw9HZL2TW1uK6Ya1ek3KfcDisDCaoGyVIvm9yJ2pq0/dPF/SqVnufJxGEhAvSQ1cECDVHe8cY8egh9cYZXl0+lfvavfRoDMv328GpIDj09zUOP17Y/E0HPXF/QIQGO8Wcqco3gHCmSlr/8EtC6GhCc8s9ZTw29vIPB/rMAscP5/rcMjK9UVXO6qEwa9f2rvzLPPwSjSoH7leihL+mWTVW+8AnqvMAhuGrY3YK4AV/2/AOikNGn2Wl5tF0nAxYhqSllpLHew+pJmMoSDPxK826UfnmzTzmccl1FEvCnJ/nu5v1aI+J3rWJTFsy/ofwJSbMU0pJs2e8hn7QVdY7r8E/SJcEiJY8orm06g9u0WDrKOqWzueLRctS36WIDN/Pz39/OswKrhemazaIrMunKiHv9y6A2F5wD6mndLb7WH2CcQb0d2x21KOimyLWD2kCuNHcD0ugtlk3mk6F7LINu1lSct2jFE+7q9aDyv43tT38W/S6WRUU6EkC8S5g53wGUCFB5b+jlksastAmc1XpCZmATRwrVBk1NCfS+lubytIgQfyckLvEGj6n4ccOwCdHo4B+nJ+Sa99UD2rPO9mImZ1CNJrEltBRLRkp2fZCyVqe9N1xEHGKLyA9m0l3WvIrY78njXpCARV90RDmGif1KqDSYwMEfHenc27WIcB/ls7PnEbWvrFW6WoVSxWJJPVzJcuJ6WH3P8uYdFTBCkyWhx+qVqec/W5wMIAM+9jHidbtbCgTi7NXrGFVaX8IMnjpXhu1fYL17tj+cjIwvmRPkyt8z09PtZ2MYSv2DSBmung0HnL1h+3igP3NvPvuTh9VwgNX03k5OdXoVvSgP1Lik7jqHcFcVgv00Rf8eFQpVm1QrW8sftnhpqFzQuN/WdUJpnWiqA+LTDk2w+j9OT1EIBJ1j4h4M3D0X1EiOoJhqOlDNlDVBA/KkZ1OCYj4N+IvvfQeqt8jNklr9e4m6MHkn34n054DoPQ996FmainaNzJtkR3U0WahXjwznVgKX91oGyfJ3IhYhiekCML7ssKnLFtluIFlY3wSoGdtRkGr9OhJ9C/Be84IRRYUQT8dSu6+p1pt5YTxyyKj9dE7aZXQ1XZCxjYbQvxn8sLkUA3O0SWY7PlwxNS4Z7yxLX9W/JQKxyIudUbhmEJczrc8ih3J0s674Mcypg7zF4paLY13JA0sSLQySoHiHwgs+xFCOsX54QEEYFXoxGDYtGWsljKt4iU6O6YydyeirPitB/riXBCw9AA51siCQLWLoVgMvIBhJkHHeE0h61ZhoKcLyt1HJ8TQn6NzEPjM5aZ1Umu3L0aPAIyPMvc1Uf5noRj8rkVz+cJLIL/KDmfxThVWCT/d5/rtX4ZICUkeCkXLfVqXs2fkOK8j5FwlEWRP9j18RefF4JuNHs9ft+BOymTt6He+dwij9d4Q8qY43faRXqVjTkOCQ7AWclq+R5qmOwxepGmLTlxHWUDaOWA/QaDi6ApqWMiR7xSu1OZjdIOy4xcNNNoUUrm+8e2Ld8bzJiaz+oAAAAAAvYHTbtVTG/wAB1QmNNwAAw6ahsrHEZ/sCAAAAAARZWg==
```

## Método de Brain

LIGERO: ensayo aislado sin modificar producto, documentación y propuesta acotada. Runtime propio brain-env, git show, Python y archivos temporales; ningún proceso persistente o servidor. Fuente real sin mutaciones, inputs/control negativo y salidas íntegros; errores propios preservados. Rúbrica numérica N/A, no score de producto ni aprobación externa. Inventario no exhaustivo; consumidores dinámicos/despliegue/GitHub checks/reglas NO MEDIDOS. Cierre durable: este archivo con evidencia, Doc público y Nexus; presencia remota, decodificación y comparación se verifican antes de responder.
