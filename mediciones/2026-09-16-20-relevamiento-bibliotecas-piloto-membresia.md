# Corpus a US$10: qué completar, qué corregir y qué debe probar el piloto

16-sep-2026. Relevamiento de auditor-sol por pedido de Abraham. [Doc público con el relevamiento y las tablas](https://app.clickup.com/90171457413/docs/2kza6fw5-12397).

**Recomendación:** construir una biblioteca de investigación jurídica de Tarija con base nacional confiable, citas verificables, colecciones y feedback. No competir por cantidad de PDFs ni agregar otro chat antes de resolver la fuente. El piloto debe probar utilidad y luego pago real: terminar cuatro semanas de uso gratuito no habilita automáticamente una membresía comercial.

**Precio objetivo del usuario: US$10.** Para los cálculos se supone mensual por persona, pendiente de confirmar; no se cambió a bolivianos ni se eligió un tipo de cambio. Si fueran US$10 anuales, la economía del producto sería otra. Este relevamiento no implementó cambios, no lanzó el piloto y no contactó universidades.

## 1. Hallazgos que cambian el orden de trabajo

### Primero, corregir qué documento creemos tener

El [manifiesto nacional del PR1](https://github.com/gatehot59-star/corpus-legal-tarija/blob/2360f27d43fdc9a1e2a74a3f6465698918df2ad1/indices/nacional-normas.jsonl) contiene **15 registros**, no cero: CPE, siete entradas de códigos y siete entradas adicionales de leyes/decreto ley. Incluye el Código de Familia de1972, DL10426; no incluye Ley603. [SILEP identifica Ley603 de19/11/2014 como Código de las Familias y del Proceso Familiar, vigente con modificaciones](http://www.silep.gob.bo/norma/13366/ley_actualizada).

**Consecuencia:** conservar el código histórico para investigación, pero completar el régimen actual y sus reformas; no usar «tenemos código de familia» como sinónimo de cobertura actual. La identidad requiere tipo, número, fecha y órgano: la [búsqueda oficial de603](http://www.gacetaoficialdebolivia.gob.bo/normas/buscar/603) también devuelve una ley de1984 y un decreto de2010. Buscar solo por número puede incorporar otra norma.

El manifest atribuye a la CPE1.717.132 caracteres y412 números únicos encontrados por regex. Es una señal para revisar la extracción, **no prueba de contaminación ni conteo jurídico validado**: el extractor elimina etiquetas del HTML sin delimitar inequívocamente el cuerpo normativo. Separar texto legal, navegación, concordancias y relacionados. [Extractor del PR](https://github.com/gatehot59-star/corpus-legal-tarija/blob/2360f27d43fdc9a1e2a74a3f6465698918df2ad1/pipeline/nacional_lexivox.py).

### Segundo, hay un control anunciado que no se ejecuta

Probé la clase real [FuenteNacional del PR](https://github.com/gatehot59-star/corpus-legal-tarija/blob/2360f27d43fdc9a1e2a74a3f6465698918df2ad1/sistema/api/fuente_nacional.py) con archivos sintéticos aislados. Acepta texto correcto y también texto alterado cuyo SHA256 no coincide; sí rechaza el archivo ausente. El comentario menciona el hash, pero el método no lo compara.

Esto demuestra el defecto de ese lector, **no corrupción de producción ni de los quince documentos**. Antes de incorporar más bibliotecas, exigir comparación completa y una prueba que cambie un byte y obtenga rechazo. Evidencia cruda: `2026-09-16-20-hash-nacional.json`, mismo directorio.

### Tercero, no hay que rehacer los decretos desde cero

Encontré [trabajo de extracción y auditoría departamental en otra revisión](https://github.com/gatehot59-star/corpus-legal-tarija/blob/84358cc821490cd90e31cb3f049ef7e691ccc4da/sistema/evidencia/2026-09-04-11-el-catalogo-miente-sobre-5-decretos.md): sobre387 documentos extraídos, el informe registró cinco discrepancias entre catálogo y sello. También identificó anexos legítimos y duplicados. Esa fotografía decía que aún no se habían incorporado a la base.

**Corregimos el diagnóstico:** ausencia en main no significa ausencia de trabajo. Recuperar rama, resultados y archivos, cotejar el destino actual y reconciliar IDs antes de descargar otra vez. No doy por concluida la extracción ni por incorporados los decretos.

### Cuarto, el precio necesita una ventaja demostrable

[D-Lex anuncia US$95,88 por año](https://www.derechoteca.com/legal-tech/d-lex-bolivia-suscripcion), equivalente aritmético a US$7,99 al mes con pago anual, no una oferta mensual a ese valor. [Pixi Lector publica Bs20/mes](https://www.pixilegal.com/planes) por búsqueda y lectura de jurisprudencia sin asistente; [LeyNova publica Bs50/mes profesional y Bs20/mes estudiante](https://leynova.com/). Son precios y promesas de sus vendedores, no calidad auditada.

**US$10 mensuales no es una ventaja de precio automática.** Se puede probar ese precio, pero hay que justificarlo con tiempo ahorrado, profundidad local, fuentes verificables y trabajo guardado. No convierto bolivianos a dólares sin una regla de cobro verificada. LexiVox y Gaceta son alternativas de consulta pública: cobrar solo por «tener leyes» es una propuesta débil.

## 2. Estado real: código, rama y servicio son tres cosas distintas

| Componente | Evidencia disponible | Implicación |
| --- | --- | --- |
| Buscador, frontend y API HTTP | Existen en main: FTS5/BM25, filtros, documentos, manifiesto para agentes y OpenAPI | Reusar; no reconstruir un buscador desde cero |
| OCR y revisión | Hay normalización de citas, pruebas y cola de revisión | Revisar calidad jurídica; pasar un filtro textual no certifica una norma |
| Procedencias, no-pérdida y frontera | Mejoras en PR1, head2360f27, abierto en la consulta | Auditar el head y probar antes de integrar; no asumir desplegado |
| Nacional |15 entradas del manifest en PR; Civil, Penal y LGT quedan pendientes en el pipeline leído | Cotejar archivos externos y base viva; manifest no prueba servicio |
| Decretos | Trabajo previo recuperable fuera de main | Reconciliar y terminar, no declarar cero ni completo |
| TCP y municipal | Sin integración acreditada en los adaptadores examinados | Diseñar incorporación selectiva desde fuentes verificadas |
| Cuentas, membresía, favoritos, colecciones y feedback | No encontrados como circuito completo en el alcance leído | Son trabajo de producto, no una opción que ya se pueda activar |
| Servicio vivo | No revalidado en este relevamiento | Falta cotejar revisión desplegada, base y rutas |

Main examinado: `4259ba81df9b32aefc2c09a3aa595bb0b1c13b38`. PR1: `2360f27d43fdc9a1e2a74a3f6465698918df2ad1`. Fuentes técnicas: [servidor main](https://github.com/gatehot59-star/corpus-legal-tarija/blob/4259ba81df9b32aefc2c09a3aa595bb0b1c13b38/sistema/api/servidor.py), [esquema main](https://github.com/gatehot59-star/corpus-legal-tarija/blob/4259ba81df9b32aefc2c09a3aa595bb0b1c13b38/sistema/api/esquema.sql), [ingesta PR](https://github.com/gatehot59-star/corpus-legal-tarija/blob/2360f27d43fdc9a1e2a74a3f6465698918df2ad1/sistema/api/ingesta.py), [frontera PR](https://github.com/gatehot59-star/corpus-legal-tarija/blob/2360f27d43fdc9a1e2a74a3f6465698918df2ad1/sistema/api/frontera.py).

El snapshot histórico de6.079 documentos no es inventario de hoy. No sumar documentos, artículos, pasajes, anexos y procedencias como si fueran la misma unidad. Los informes antiguos «sin códigos» y «sin pruebas» no son una base válida para planificar.

Custos queda separado: su núcleo pasó24 contratos HTTP en PostgreSQL16 y17, pero eso no verifica ni reemplaza al corpus. No trasladar expedientes, plazos o agentes procesales a este producto. [Evidencia Custos PG16](https://github.com/gatehot59-star/custos-legis-tarija/tree/c35fb90472492fee65280ad69b38b4b95cbb076d/docs/auditorias/2026-09-16-18-http-pg16).

## 3. Qué bibliotecas completar y de dónde

P0 significa necesario para el alcance inicial que se prometa; P1, expansión siguiente. Prioridad por utilidad curricular, profesional y trabajo existente, no orden de ingestión masiva.

| Biblioteca | Fuente comprobada | Qué hacer y criterio de cierre |
| --- | --- | --- |
| **Nacional troncal, P0** | [Gaceta avanzada](http://www.gacetaoficialdebolivia.gob.bo/normas/busquedaAvanzada), [CPE oficial](http://www.gacetaoficialdebolivia.gob.bo/app/webroot/archivos/CONSTITUCION.pdf), [SILEP](http://www.silep.gob.bo/) | Reconciliar15 registros; completar Civil, Penal, LGT y Familia603; verificar identidad, artículos y reformas contra publicación oficial |
| **Civil y procesal, P0** | [Civil SILEP](http://www.silep.gob.bo/norma/4451/ley_actualizada), [Procesal Civil](http://www.silep.gob.bo/norma/13172/ley_actualizada) | Lectura por artículo, fuente y fecha; búsqueda por número y concepto; distinguir código anterior y actual |
| **Penal y procedimiento, P0** | [Penal SILEP](http://www.silep.gob.bo/norma/4368/ley_actualizada), [Procedimiento Penal](http://www.silep.gob.bo/norma/4311/ley_actualizada) | Textos base y reformas pertinentes; no anunciar consolidación completa sin revisión |
| **Familias, niñez y violencia, P0** | [Ley603](http://www.silep.gob.bo/norma/13366/ley_actualizada), Gaceta y entradas548/348 del manifest | Completar603; mantener historia separada; evaluación jurídica del régimen actual, sin abrir causas sensibles por defecto |
| **Laboral, comercial, tributario y administrativo, P0 acotado** | Gaceta/SILEP; manifest contiene Comercio, Tributario, Procesal del Trabajo,1178,025 y031 | Textos base y reglamentos exigidos por tareas del piloto; LGT pendiente; no toda la jurisprudencia especializada antes de empezar |
| **Autonómica y departamental, P0** | [Leyes Tarija](https://www.tarija.gob.bo/gaceta-oficial/leyes-departamentales), [estatuto](https://www.tarija.gob.bo/gaceta-oficial/estatuto-autonomico-departamental), [Ley031](http://www.silep.gob.bo/norma/4139/texto_ordenado) | Reconciliar leyes/resoluciones; corregir fecha/título y catálogo-documento; mostrar jurisdicción y competencia, no solo jerarquía |
| **Ejecutivo departamental, P0 recuperar / P1 ampliar** | [Decretos Tarija](https://www.tarija.gob.bo/gaceta-oficial/decretos-departamentales) y extracción previa | Auditar resultados; cuerpo y anexos sin pisarlos; discrepancias de identidad y faltantes con razón |
| **Municipio Tarija, P0 muestra útil** | [Decretos municipales](https://www.tarija.bo/decretos-municipales/), [ediles](https://www.tarija.bo/decretos-ediles/), [Ley Municipal328](https://www.concejotarija.bo/storage/files/8/LEYES%202023/Ley%20Municipal%20328.PDF) | Temas locales elegidos con usuarios; distinguir Concejo/Ejecutivo y ley/decreto/resolución; índice no garantiza totalidad |
| **Yacuiba, P1** | [Carta Orgánica SEA](https://www.sea.gob.bo/wp-content/uploads/2020/04/ley-yacuyba.pdf), [Ley25/2024](http://www.concejomunicipalyacuiba.gob.bo/assets/gaceta/1762530899) | Fuente semilla, no censo; relacionar municipal y regional del Gran Chaco |
| **Villa Montes, P1** | [Índice municipal](https://www.gamvm.gob.bo/leyes-municipales/), [Ley432/2025](https://www.gamvm.gob.bo/wp-content/uploads/2025/06/ley_432.pdf) | Censar IDs/fechas y revisar OCR; índice breve no es colección completa |
| **Bermejo, P1 pendiente** | [Portal](https://gambermejo.gob.bo/), [entidad Gob.bo](https://www.gob.bo/entidades/gobierno-autonomo-municipal-de-bermejo) | No se verificó catálogo normativo completo; buscar archivo oficial o solicitar con autorización, sin inventar cobertura |
| **TSJ, P0 revisar existente** | [GENESIS](https://genesis.tsj.bo/resoluciones), [TSJ](https://tsj.bo/jurisprudencia/) | Reconciliar gestiones/salas e incorporados; selección compartible revisada, cita exacta y privacidad |
| **TCP, P0 selección / P1 ampliar** | [Jurisprudencia](https://jurisprudencia.tcpbolivia.bo/), [causas/resoluciones](https://buscador.tcpbolivia.bo/) | Fallos útiles para materias del piloto; distinguir resolución, resumen y ratio; fuente y privacidad |
| **Doctrina, P0 enlaces** | [Tribuna Jurídica UAJMS](https://dicyt.uajms.edu.bo/revistas/index.php/tribuna-juridica/issue/archive), [biblioteca TSJ](https://tsj.bo/servicios-judiciales/biblioteca/), [licencia UCB](https://lawreview.ucb.edu.bo/a/copyright-policy) | Catálogo y enlaces; acuerdos para materiales docentes; CC BY-NC-SA no autoriza incorporación comercial por defecto |

SILEP sirve para versiones y descubrimiento, pero remite a Gaceta para referencia legal definitiva. Lo oficial y consultable no equivale a licencia comercial general. No hacen falta libros pirateados: materiales propios/autorizados, referencias y enlaces permiten iniciar la biblioteca docente.

**La unidad de completitud no será «X mil documentos».** Será una lista acordada de normas, versiones y tareas por materia; cada faltante visible. Una fuente inaccesible o una norma histórica no se rellena por inferencia. Registrar además formato, accesibilidad de descarga, última consulta, URL primaria, hash del archivo y estado de revisión. Los portales dinámicos o sin licencia clara requieren investigar condiciones antes de automatizar, no evadir controles.

## 4. Producto funcional para cada público, sin construir un campus virtual

| Público | Trabajo a terminar | Mínimo antes del piloto |
| --- | --- | --- |
| Abogado | Encontrar norma/precedente, verificar fuente, guardar investigación | Número/texto/artículo, filtros útiles, cita copiable, versión/fecha, favoritos y colección privada |
| Profesor | Preparar lectura/ejercicio y compartir el mismo material | Colecciones con instrucciones propias, enlaces estables y versión fijada; permisos sobre cada documento |
| Estudiante | Encontrar, leer, citar y distinguir fuente/comentario/historia | Lectura móvil, teclado accesible, índice, glosario breve, cita exportable y límites visibles |
| Agente/plataforma | Contexto verificable sin extracción ilimitada | OpenAPI existente, identidad/versiones, errores claros y auth/cuotas por consumidor cuando se habilite |

Son hipótesis respaldadas por currículas, no entrevistas realizadas. No construir ahora calificaciones, videoclases, un LMS ni generación ilimitada de memoriales. Favoritos y colecciones pequeñas sí entran al piloto: son utilidad que luego se cobrará.

Búsqueda literal existente como base. Mejorar exactitud número/artículo, acentos y sinónimos revisados; semántica solo si un banco de consultas demuestra beneficio. Un chat no arregla fuentes equivocadas.

## 5. Feedback dentro del corpus

Botones en documento: **Reportar error** y **Guardar**; búsqueda vacía: **No encontré lo que buscaba**; menú: **Sugerir mejora** y **Mis reportes**.

Guardar ID, versión, UID/pasaje, categoría, descripción y estado. Categorías: OCR, identidad, cita/enlace, fecha, vigencia, faltante, uso, privacidad y sugerencia. Contacto según consentimiento del piloto. **No adjuntar automáticamente consulta, expediente ni captura con datos ajenos.**

Flujo: recibido → en revisión → corregido o descartado con motivo. Responsable real, revisión diaria de privacidad/bloqueantes y semanal del resto como capacidad a acordar. Incidentes sensibles en registro privado, no git/issues públicos. La cola interna de revisión existente no sustituye este circuito.

Reportes no reescriben la fuente: original, corrección revisada y versión. Compartir colección no concede acceso a documentos restringidos. Métricas mínimas/agregadas; no almacenar búsquedas jurídicas completas por defecto ni entrenar con ellas sin base y autorización apropiadas.

## 6. Backlog con aceptación

Paquetes propuestos, **no tareas creadas ni compromiso de horas**. Al ejecutar, dividir en unidades revisables de hasta4h. La revisión jurídica e institucional no se sustituye programando.

| Orden | Paquete | Aceptación |
| --- | --- | --- |
| P0-1 | Inventario único servido | Revisión servicio/base identificada; IDs censados/incorporados/excluidos/fallados reconciliados; razón por diferencia y anexos conservados |
| P0-2 | Identidad/extracción/hash | Alteración rechazada; ausencia de hash explícita; SHA PDF/texto separados; extracción sin navegación; identidad contra documento, no solo slug |
| P0-3 | Bibliotecas troncales | Lista por materia con citas;603 y pendientes nacionales resueltos o excluidos expresamente; desconocido nunca presentado como vigente |
| P0-4 | Privacidad/derechos | Colección y vías revisadas; rutas alternativas/exportaciones no recuperan contenido restringido; retirada y licencias documentadas |
| P0-5 | Release reproducible | PR auditado y probado, aprobación humana para integrar/desplegar; smoke real; backup restaurado y cotejado en aislamiento |
| P0-6 | Cuentas/experiencia | Alta, recuperación, sesión revocable; colecciones privadas/compartidas; móvil/citas; dos usuarios no leen guardados ajenos |
| P0-7 | Feedback/métricas | Reporte llega a cola privada con estado/versión; contador verificable sin q en logs; incidencia probada hasta resolución |
| P0-8 | Banco jurídico | Tareas/fuentes esperadas revisadas por docentes/abogados; tests negativos de identidad/versión/extracción; evaluación separada de ajuste |
| P1-1 | Membresía/pagos | Pago real activa; duplicado no duplica, falsificado no activa; fallo informa; cancelación respeta periodo pagado; vencimiento/reembolso según política |
| P1-2 | Operación comercial | Precio/periodo/impuestos definidos, factura resuelta, soporte con capacidad, límites y política de datos; costo y renovación medidos |

**No usar conteos que tapen omisiones.** Cada ID fuente queda incorporado, excluido justificadamente o fallado; conjuntos sin solapamientos. Alias conserva procedencias, reintentos no agregan documentos. Anexos jurídicamente necesarios no se excluyen por ser anexos.

**Prueba universitaria concreta:** múltiples alumnos comparten IP; rate-limit por IP del PR podría bloquear una clase. Probar cuenta y red compartida. **Prueba comercial concreta:** cancelación de renovación no debe revocar de inmediato tiempo abonado.

## 7. Dos universidades y piloto que mida utilidad

Candidatas, no acuerdos: [UAJMS Derecho](https://www.uajms.edu.bo/oferta-academica/carrera-de-derecho/) y [UPDS Tarija Derecho](https://www.upds.edu.bo/carrera/derecho-tarija/). UAJMS destaca investigación, TIC, argumentación y práctica profesional. UPDS incluye LegalTech I/II, investigación, redacción, jurisprudencia y prácticas forenses. Hay encaje curricular; interés institucional no medido.

Propuesta: un docente y10-15 estudiantes por universidad, más4-6 abogados con tareas no confidenciales. Una versión común, grupos diferenciados; no duplicar bibliotecas por defecto. Cuatro semanas desde P0, no desde hoy. Validar materias y selección documental con docentes antes de abrir.

Banco propuesto:60 tareas,20 de búsqueda exacta,20 temáticas y20 de contraste temporal/procedencia, distribuidas por materias. No exigir60 a cada usuario. Incluir número repetido, texto histórico, OCR ambiguo y PDF incorrecto bajo título correcto; fuentes esperadas revisadas por profesionales.

Comparar corpus con método habitual alternando orden para reducir aprendizaje. Medir tarea resuelta con fuente, tiempo hasta verificar, error material, colecciones, retorno y reportes cerrados; separar rol e institución.

Umbrales a acordar, **no resultados**:≥80% de tareas válidas resueltas, cero incidentes críticos de privacidad abiertos, cero errores materiales pendientes en conjunto evaluado, mediana de tiempo≥25% menor. Denominadores y dispersión visibles: muestra pequeña no certifica toda la colección.

Antes de terminar, mostrar oferta exacta US$10 por periodo confirmado con límites y beneficios. Medir compra real al abrir etapa paga, no solamente «pagaría»; luego medir renovación del siguiente periodo. Piloto gratuito, primera compra y retención son pruebas distintas.

## 8. Membresía a US$10, cobro y economía

Propuesta personal: biblioteca del alcance publicado, búsqueda, lectura, citas, favoritos/colecciones, cambios detectados en fuentes incluidas, reportes y soporte acotado. No todas las leyes vigentes, IA ilimitada, dictámenes, patrocinio ni expedientes sin límites. Alto volumen API y licencias institucionales con condiciones propias; no consumo ilimitado dentro del plan personal.

No bajar automáticamente precio estudiantil: medir quién paga, alumno o universidad. Si no hay conversión, decidir licencia institucional, becas limitadas, ajuste de valor/precio. No reemplazar US$10 por Bs69 ni asumir que docente paga cada alumno.

**Cobro disponible en oferta del proveedor, no habilitado para nosotros.** [Red Enlace](https://www.redenlace.com.bo/productos-y-servicios/quiero-cobrar-por-internet-en-mi-tienda-virtual) publica Bs/dólares, checkout alojado, recurrencia tokenizada, cuenta bancaria/NIT y requisitos del comercio. Comisión publicada hasta2,5%, no cotización total garantizada. [BNB Domiciliación](https://www.bnb.com.bo/PortalBNB/Domiciliacion/Empresas) es otra vía a evaluar. Elegibilidad y contratación no verificadas.

QR de renovación manual puede reducir implementación si se valida con banco. Activar por conciliación bancaria, no imagen de comprobante. Recurrencia: validar firma/consulta del proveedor, duplicados y desorden de eventos, no guardar tarjetas. Cancelación y reembolso visibles. Resolver facturación según régimen del vendedor con [SIN](https://siatinfo.impuestos.gob.bo/index.php/informacion/modalidades-facturacion/facturacion-portal-web), sin inventar obligación exacta o estructura empresarial.

### Escenarios, no promesas

US$10 mensuales:50 miembros=US$500 brutos,100=US$1.000,200=US$2.000. No es ganancia.

N=pagadores; p=comisión proporcional; t=cargo por operación; c=variable por usuario/mes; F=fijos mensuales.

`Contribucion_antes_impuestos_e_inversion = N * (10 * (1-p) - t - c) - F`

Incluir edición jurídica, actualización, soporte, infraestructura, correo, backup y licencias; no solo servidor o tokens.

Ejemplo hipotético: p=.025,t=0,c=US$2,F=US$150 → aporte US$7,75 por usuario, equilibrio20 pagadores; con100,US$625 antes de impuestos e inversión inicial. **No son costos medidos ni margen esperado.** Contrato y atención real cambian la cuenta.

Conversión=pagadores/activos elegibles que recibieron oferta; renovación2/pagadores1; minutos de soporte por usuario, bajas/motivos. No mezclar gratuidad estudiantil, licencias institucionales y profesionales en un porcentaje.

## 9. Derechos, privacidad y operación

Distinguir norma, sentencia con datos, doctrina, compilación y material propio. Revisar reutilización por fuente: un pie de derechos tampoco resuelve cada texto. **No concluimos que toda norma necesita permiso ni que todo sitio público autoriza republicación irrestricta.**

[UCB CC BY-NC-SA4.0](https://lawreview.ucb.edu.bo/a/copyright-policy) no autoriza usar artículos íntegros comercialmente por defecto. En UAJMS y otros verificar obra; mientras, referencias y enlaces. Materiales propios del docente requieren autorización clara y no incluyen automáticamente libros ajenos.

Revisión por abogado boliviano de colección sensible, términos, actividad y normativa aplicable. Login/cifrado/avisos no sustituyen selección/anonimización ni revisión jurídica. Retención, baja, administración y respuesta a filtraciones antes de piloto.

Operación: monitor sin datos sensibles, frescura por fuente, cola de fallos, copias cifradas, restauración, rollback y soporte. Acordar frecuencia por colección y mostrar fecha de consulta; no prometer siempre actualizado.

## 10. Próximo bloque y secuencia

**Primero reconciliar lo servido, main y ramas; cerrar hash nacional; elegir materias/textos con docentes.** Después identidad/privacidad, faltantes del alcance, cuentas/colecciones/feedback, piloto y pago real. No montar cobros para vender una colección aún mal identificada.

No se fija fecha de lanzamiento sin medir el inventario y capacidad de revisión. Separar preparación técnica de las cuatro semanas de piloto. No se contrató, contactó ni cambió prioridad operativa en esta investigación.

## 11. Método: pedido, herramientas, medición, evidencia, archivos y límites

**Pedido:** relevamiento de bibliotecas y mejoras necesarias para profesores, abogados y estudiantes; piloto en dos universidades y membresía posterior aUS$10.

**Herramientas/máquina:** investigación en tres frentes con lectura pública; GitHub, web oficial/proveedores y contexto ClickUp; lectura directa adicional de manifest/fuente nacional/decretos; ensayo de clase exacta en brain-env. Sin OCR masivo, expediente real, producción, merge, contratación ni contacto. TITAN LIGERO, rúbrica formal N/A; esto no es auditoría integral ni censo de todas las normas.

**Medición nueva:** ejecutar FuenteNacional.resolver del headPR con tres situaciones sintéticas. Módulo descargado sin modificación, importado fuera del producto. No se llama la ingesta completa ni se atribuye a su llamador una garantía probada solo para la clase.

Preparación y llamadas ejecutadas en `python3 -c` en brain-env (las sentencias centrales, no una supuesta suite del candidato):

```python
sha = "2360f27d43fdc9a1e2a74a3f6465698918df2ad1"
u = "https://raw.githubusercontent.com/gatehot59-star/corpus-legal-tarija/" + sha + "/sistema/api/fuente_nacional.py"
code = urllib.request.urlopen(u).read()
r = pathlib.Path(tempfile.mkdtemp(prefix="corpus-survey-hash-", dir="/workspace"))
p = r / "fuente_nacional.py"
p.write_bytes(code)
spec = importlib.util.spec_from_file_location("probe_fuente", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
(r / "texto").mkdir()
original = b"TEXTO SINTETICO ORIGINAL"
changed = b"TEXTO SINTETICO ALTERADO"
f = r / "texto/prueba.txt"
row = dict(clave="synthetic", archivo_texto="prueba.txt", sha256=hashlib.sha256(original).hexdigest())
(r / "normas.jsonl").write_text(json.dumps(row) + chr(10))
source = m.FuenteNacional(r)
for label, data in [("matching", original), ("changed", changed)]:
    f.write_bytes(data)
    v = source.resolver(row)
    # La salida JSON conserva sha_equal y accepted de cada llamada.
f.unlink()
v = source.resolver(row)
```

Importaciones de la ejecución: urllib.request,tempfile,pathlib,json,hashlib,importlib.util. Directorio de evidencia persistente `/workspace/corpus-survey-hash-rfnlmpci`, con módulo descargado y `result.json`. No se tocaron archivos de producto.

**Salida cruda íntegra:** archivo JSON adjunto en este commit. Proceso exit0: el ensayo corrió; resultado de integridad negativo por aceptar texto alterado. Módulo SHA256 `53e2c84d00bfae3bd064230dbdab1247433efbe94641e96a8b547cc127537fc0`.

El control ausente rechazado demuestra discriminación para ausencia, no detección de hash. El control matching aceptado confirma que el lector se ejecuta con fixture válida. No afirmo independencia de operador ni seguridad de producción a partir de este ensayo.

**Archivos generados:** este informe y `mediciones/2026-09-16-20-hash-nacional.json`; copia documental [Doc público](https://app.clickup.com/90171457413/docs/2kza6fw5-12397), Space > Doc. Sin scripts de producto ni modificaciones de PR.

**NO MEDIDO:** disponibilidad/colección productiva actual, PR integral, exactitud jurídica global, derechos de todas las fuentes, aceptación universitaria, costos/contratos/elegibilidad bancaria/impuestos del vendedor, disposición a pagar y retención. Precios visibles en páginas consultadas16-sep-2026, no auditoría de calidad de competidores. Fuentes oficiales verificadas como puntos de entrada o documentos concretos, no disponibilidad garantizada ni permiso de descarga masiva.
