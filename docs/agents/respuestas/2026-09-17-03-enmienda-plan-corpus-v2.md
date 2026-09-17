# Enmienda v2 del plan Corpus: calibrar antes de ampliar; piloto gratuito separado del pago

17-sep-2026. Pedido de Abraham: enmendar el plan con los hallazgos verificados de Brain. Esta es la **enmienda operativa vigente** del plan publicado en commit86d57c2790082b25b81554acdd20d77d86d59730. Sustituye precedencias, multiplicadores implícitos, secuencia de integración, autorización de acceso y cifras de esfuerzo. Conserva fuentes, arquitectura general y criterios de calidad no contradichos aquí. No autoriza ejecutar tareas ni marca gates humanos como aprobados.

[Auditoría de Brain](https://app.clickup.com/90171457413/v/dc/2kza6fw5-12497) · [Antecedente documental leído](https://app.clickup.com/90171457413/docs/2kza6fw5-12457) · [Plan base histórico](https://github.com/gatehot59-star/corpus-legal-tarija/blob/86d57c2790082b25b81554acdd20d77d86d59730/docs/agents/respuestas/2026-09-17-01-plan-integral-corpus-titan-full.md) · [Doc del plan, actualizado con esta enmienda](https://app.clickup.com/90171457413/docs/2kza6fw5-12477).

## 1. Cambios vinculantes de planificación

Las72 unidades originales con multiplicadores eran102 ocurrencias. Ahora se listan **110 ocurrencias explícitas:102 originales y8 nuevas**, de80tipos de unidad. Cada una≤4h. Los sufijos .1,.2 son lotes/semanas distintos: no volver a multiplicarlos.

B05 precede a C01.1,C03.1,C05.1. I08 usa solamente esos primeros lotes yB05. I09 exige calibración,demostración cerrada,reestimación ydisponibilidad humana antes de C01.2,C02.2,C03.2,C05.2,C06.2 y siguientes. C08 depende expresamente deI08/I09 ytodos los lotes aceptados.

A08/I02 preceden a integración adoptadaD01 ypublicadorB08;A08 precedeC08. A07 se termina después deA02, no simultáneamente con su insumo. Puede adelantarse la lectura exploratoria de candidatos, no cerrar su adopción.

D09 define habilitación gratuita. E03/E04/F08 exigenD09. H02 reutiliza ese permiso para períodos pagados **después deG08**:H02/H03/H04 no son prerrequisitos del piloto. No hay segunda puerta de autorización.

D06 trabaja inicialmente conM02,snapshot mínimo, noC08. E03/E04 ylos gates finales conservan la prueba de colección ampliada antes del piloto. Los ciclosG03.n/G04.n/G05.n se relacionan por semana; no esperan semanas futuras para corregir la primera.

## 2. Nuevas unidades, alcance y autorizaciones

| ID | Entregable y aceptación | Rol | h |
| --- | --- | --- | ---: |
| A09 | Acta de ensayo reversible: primer lote por serie yB05, topes yrecursos J/D. No autoriza integración ni ampliación | A |2|
| D09 | Permiso gratuito por grupo,colección,inicio,vencimiento yrevocación; cuenta sin permiso rechazada yparticipante legítimo admitido | E |4|
| M01 | Revisión jurídica/privacidad de muestra mínima, incluyendoC02.1 yrelación temporal familiar; lista exacta de documentos/tareas permitidos | J |4|
| M02 | Snapshot mínimo aislado de la muestra, procedencia yretirada; no colección completa | E |4|
| M03 | Seguridad yrestore demo:TLS,cookies,CSRF,reset,permisos,cierre lateral,retirada yrecuperación. No omitir controles por llamarse demo | E |4|
| M04 | Observar buscar→verificar→guardar→reportar en demo cerrada, tareas equivalentes ytiempos por rol. No piloto institucional | D |4|
| I09 | Acta ampliar/reducir/parar trasI08/M04: costo actualizado,disponibilidad J/D,límite inversión ylote siguiente autorizado | A |2|
| I10 | Antes de oferta: costos/contribución,presupuesto aprendizaje,mínimos de pagos/renovación yregla seguir/parar | A |2|

E=Brain técnico;J=revisor jurídico boliviano a designar;D=docente/editor a designar;A=Abraham para decisiones. Son necesidades funcionales,no asignaciones emitidas. Las actas deben existir realmente, no inferirse de esta enmienda.

**A09 no aprueba todo el presupuesto.** B05 yC01.1/C03.1/C05.1 suman16h estimadas de muestra/comparación, además de sus prerequisitos. El acta registra ese subtotal yqué prerequisitos se autorizan. Sin J/D oal exceder el tope,no corre el lote. B01/B02/B03/B04/B06/B07 pueden generar diagnósticos/prototipos aislados reversibles; no instalación global,adopción odespliegue. Los primeros lotes son muestras exploratorias bajoA09;A08 aprueba alcance comprometido eI09 su ampliación.

La demostración utiliza solo documentos revisados,no expedientes ni un proyecto distinto. M01 puede detener por contenido;M03 por seguridad/restore. Su total incluye trabajo previo yno se promete una demo barata de un día. Si una unidad no cabe en4h,se divide yreestima antes de continuar.

## 3. Acceso: un permiso, dos orígenes

Contrato propuesto AccessGrant: id,user_id,group_id,collection_id,origin(pilot o paid),valid_from,valid_until,revoked_at,issued_by,evidence_id. Fechas ycolección son explícitas. Cuenta creada no equivale a colección autorizada.

Se autoriza solo con usuario/sesión válidos,permiso vigente no revocado,grupo/colección coincidentes ydocumento permitido no retirado. Origin explica el origen, no crea otra puerta. El rol docente/abogado/estudiante no abre toda la biblioteca; compartir enlace no elude permisos.

D09 emite habilitación gratuita con acta de grupo piloto. H02 crea permisos por pagos conciliados sobre la misma decisión de autorización. Cancelar renovación conserva tiempo abonado;revocar por seguridad es otra acción con motivo. Sin tarjetas almacenadas ni activación por captura.

Pruebas D09/M03,repetidasE03/E04: cuenta válida sin permiso;permiso no iniciado,vencido,revocado;otro grupo/colección;enlace revocado;exportación de documento retirado. Todas rechazan el acceso indebido. Controles positivos: participante gratuito vigente en colección aprobada y,después,miembro pagado vigente. El piloto no necesita pago para tener control positivo.

## 4. Defecto real → trabajo → prueba → revisor → versión

Antecedentes documentales: auditoría de Brain sobre cinco registros,leída,no reejecutada contra producción en esta enmienda. No inferir tasa de error global. El hash se reprodujo antes de forma aislada.

| Defecto | Unidad yprueba exigida | Revisor yregistro |
| --- | --- | --- |
| Ley483:230.000 OCR frente a390.000 original según auditoría | B05/C03.1/M01/I06: página1,fila/celda contra imagen;original yOCR preservados,anotación revisada. Resto de tabla se revisa,sin corregir por aritmética sola | J:source_hash,página/celda,observado/corrección,review_id,snapshot_version yfixture al ejecutar |
| Fecha vacía ytítulo con &start=340 | B01/C03.1/E02: separar promulgación,sanción,sesión/edición;quitar transporte sin inventar fecha | D coteja,J validaI06;source_url/localizador/fecha_tipo/review_id/snapshot_version |
| LexiVox oficial por método HTML | B01/B02/E04: autoridad/emisor separados de OCR/HTML,fidelidad yvigencia;metadata consistente búsqueda/lector/cita/exportación | E prueba,J atribución;fixture_id yrelease exacto |
| Familia histórico con enmienda1988 yabrogación no enlazada | C01.1/C02.1/M01: identificar edición yrelación sustentada Ley996/Ley603;no artículo inventado ni transición inferida | J:disposición/página/fecha/review_id/versión;historia preservada |
| Hashincorrecto/ausente aceptado | I05/B03/E02: correcto acepta;incorrecto,malformado,ausente no autorizado rechazan;hashtexto/PDF separados | E:salida cruda,fixture,commit;fallo bloquea publicación |

DefectAcceptance: defect_id,source_evidence,work_occurrence,fixture_id,reviewer,review_result,code_commit,snapshot_version,release_check. Valores aún desconocidos quedan PENDIENTE,no se fabrican revisores/releases. C08/E08 requieren filas cerradas para la colección ofrecida. Excluir documento se declara,no equivale a arreglar defecto. Ajusta unidades existentes,sin duplicar cinco trabajos;si crece,se recalibra.

## 5. Horas por hito, con antecesores completos

| Hito | E | J | D | A | Base | Reserva30% E+D | Orientativo |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Demo cerradaM04 |99|36|26|4|165|37,5|202,5|
| AutorizaciónI09 |99|36|26|6|167|37,5|204,5|
| AperturaF08 |147|116|50|10|323|59,1|382,1|
| Ruta completa |203|132|58|24|417|78,3|495,3|

Sustituye391/464,5 del original. Ocho unidades nuevas agregan26h. Antes del piloto299h pasa a323h. No se oculta aumento para conservar cifra atractiva.

**Aritmética de hipótesis,no productividad o fecha probadas.** J116h previas al piloto a4h/semana hipotéticas=29semanas de esfuerzo jurídico;a8h=14,5. Demo requiereJ36h,no112,pero no es gratis. Confirmar recursos ymedir códigos/anexos antes de comprometer fechas. No cubrir indisponibilidad humana con más horas deIA.

I08 registra tiempo real por documento/página/relación,causas de desvío ycalidad,calcula pendientes. I09 exige disponibilidad J/D,costos de edición/revisión/soporte ytope;autoriza lote siguiente,no toda la hoja de ruta. Nuevo exceso vuelve a decisión. Privacidad,permisos yrestore no se recortan.

## 6. Aprendizaje ydecisión comercial antes de medir

I10 registra valores numéricos acordados de inversión máxima de aprendizaje,horas mensuales máximasJ/D/soporte,contribución neta mínima por miembro,mínimos de pagadores/renovadores ydenominadores,fecha de evaluación,periodicidad/moneda deUS$10. Campos vacíos bloqueanG07. Esta enmienda no aprueba esos valores porAbraham.

Reglas:calidad/privacidad abierta→no ofertar;contribución neta≤0→no escalar;inversión llega al tope→parar adquisición/expansión yrevisar;mínimos no logrados al cierre→no declarar validación comercial ni renovar presupuesto automático. Muestra insuficiente→INCONCLUSO,extensión con presupuesto explícito. Si cumple,A decide escala limitada,no despliegue ilimitado automático. Equilibrio=techo(costos fijos/contribución neta por miembro),solo con valores reales ycontribución positiva.

Embudo por rol/institución:invitados→habilitados→activos→recibieron oferta→pagaron→elegibles para renovar→renovaron. Conversión entre activos elegibles con oferta. Renovación solo entre quienes alcanzaron vencimiento;mostrar excluidos aún no vencidos. No mezclar gratis ypagadores.

Tiempos:pares de tareas equivalentes revisados,asignar aleatoriamente orden corpus/manual ypares por participante,conservar semilla/asignación. No repetir la misma consulta ya conocida para fabricar ahorro. Registrar asignadas,abandono,acierto,cita,tiempo;holdout fuera del ajuste. M04 calibra método antes deG02;G02 aplica banco final.

## 7. Grafo operativo completo

**Esta tabla reemplaza dependencias yrepeticiones del plan base.** Cada aceptación/rol/hora original se hereda del ID base salvo cambio explícito. Los110renglones son ejecuciones individuales;no multiplicarlos de nuevo. Sufijo identifica lote/semana. C08/E08 exigen ocurrencias aceptadas oenmienda de alcance aprobada;consumir horas no satisface un gate fallido.

| Ocurrencia | Precedencias directas | Rol | h |
| --- | --- | --- | ---: |
| A01 | Inicio | E | 4 |
| A02 | A01 | E | 4 |
| A03 | A02 | J | 4 |
| A04 | Inicio | D | 2 |
| A05.1 | A04 | D | 4 |
| A05.2 | A04, A05.1 | D | 4 |
| A05.3 | A04, A05.2 | D | 4 |
| A05.4 | A04, A05.3 | D | 4 |
| A06 | A03, A05.1, A05.2, A05.3, A05.4 | J | 4 |
| A07 | A02 | E | 4 |
| A08 | A06, A07, I01, I03 | A | 2 |
| A09 | A03, A04 | A | 2 |
| B01 | A02 | E | 4 |
| B02 | B01, A07 | E | 4 |
| B03 | B01, I05 | E | 3 |
| B04 | B03 | E | 4 |
| B05 | A07, A09 | E | 4 |
| B06 | B01 | E | 4 |
| B07 | A02 | E | 4 |
| B08 | B02, B06, B07, A08, I02 | E | 4 |
| C01.1 | A06, B04, B05, A09 | J | 4 |
| C01.2 | A06, B04, C01.1, I09 | J | 4 |
| C01.3 | A06, B04, C01.2, I09 | J | 4 |
| C01.4 | A06, B04, C01.3, I09 | J | 4 |
| C02.1 | C01.1 | J | 4 |
| C02.2 | C01.2, C02.1, I09 | J | 4 |
| C02.3 | C01.3, C02.2, I09 | J | 4 |
| C02.4 | C01.4, C02.3, I09 | J | 4 |
| C03.1 | A06, B07, B05, A09 | D | 4 |
| C03.2 | A06, B07, C03.1, I09 | D | 4 |
| C03.3 | A06, B07, C03.2, I09 | D | 4 |
| C03.4 | A06, B07, C03.3, I09 | D | 4 |
| C04 | B06, A06 | E | 4 |
| C05.1 | A06, B05, A09 | J | 4 |
| C05.2 | A06, C05.1, I09 | J | 4 |
| C05.3 | A06, C05.2, I09 | J | 4 |
| C05.4 | A06, C05.3, I09 | J | 4 |
| C05.5 | A06, C05.4, I09 | J | 4 |
| C05.6 | A06, C05.5, I09 | J | 4 |
| C06.1 | A06, B06 | J | 4 |
| C06.2 | A06, B06, C06.1, I09 | J | 4 |
| C07 | A03 | D | 4 |
| C08 | B08, C01.1, C01.2, C01.3, C01.4, C02.1, C02.2, C02.3, C02.4, C03.1, C03.2, C03.3, C03.4, C04, C05.1, C05.2, C05.3, C05.4, C05.5, C05.6, C06.1, C06.2, C07, I06, I07, A08, I08, I09 | E | 4 |
| D01 | A07, B02, A08, I02 | E | 4 |
| D02 | D01 | E | 4 |
| D03 | D02 | E | 4 |
| D04 | D02, B02 | E | 4 |
| D05 | D04 | E | 4 |
| D06 | D04, M02 | E | 4 |
| D07 | D02, B02 | E | 4 |
| D08 | D01, D07 | E | 4 |
| D09 | D03, B02, A08 | E | 4 |
| E01.1 | A06, C08 | J | 4 |
| E01.2 | A06, C08, E01.1 | J | 4 |
| E01.3 | A06, C08, E01.2 | J | 4 |
| E01.4 | A06, C08, E01.3 | J | 4 |
| E02 | B03, B04, B08 | E | 4 |
| E03 | D05, D07, C08, D09 | E | 4 |
| E04 | E02, E03, D09 | E | 4 |
| E05 | B06, D08 | E | 4 |
| E06 | D06, D07 | E | 4 |
| E07 | E03, D08 | E | 4 |
| E08 | E01.1, E01.2, E01.3, E01.4, E04, E05, E06, E07 | J | 4 |
| F01 | E02, E04, A07 | E | 4 |
| F02 | D01, F01 | E | 4 |
| F03 | F02, C08, D03, D05, D07, D08 | E | 4 |
| F04 | F03, E08 | E | 4 |
| F05 | A01, F04 | E | 4 |
| F06 | D06, F04 | D | 4 |
| F07 | A08, E08, F06, I01, I03, I04, I08 | A | 2 |
| F08 | F05, F07, D09 | A | 2 |
| G01 | F08 | D | 4 |
| G02 | G01, E01.1, E01.2, E01.3, E01.4 | D | 4 |
| G03.1 | G01 | E | 4 |
| G03.2 | G01, G05.1 | E | 4 |
| G03.3 | G01, G05.2 | E | 4 |
| G03.4 | G01, G05.3 | E | 4 |
| G04.1 | G02 | J | 4 |
| G04.2 | G02, G05.1 | J | 4 |
| G04.3 | G02, G05.2 | J | 4 |
| G04.4 | G02, G05.3 | J | 4 |
| G05.1 | G03.1, G04.1 | E | 4 |
| G05.2 | G03.2, G04.2 | E | 4 |
| G05.3 | G03.3, G04.3 | E | 4 |
| G05.4 | G03.4, G04.4 | E | 4 |
| G06 | G02, G04.1, G04.2, G04.3, G04.4, G05.1, G05.2, G05.3, G05.4 | E | 4 |
| G07 | G06, A08, I10 | A | 2 |
| G08 | G06, G07 | A | 2 |
| H01 | A08 | A | 4 |
| H02 | D03, H01, D09, G08, I10 | E | 4 |
| H03 | H02 | E | 4 |
| H04 | H03, F03 | E | 4 |
| H05 | H04, G08 | A | 2 |
| H06 | H05 | E | 4 |
| H07 | H06 | E | 4 |
| H08 | H07 | A | 2 |
| I01 | A03 | J | 4 |
| I02 | A07 | J | 4 |
| I03 | Inicio | J | 4 |
| I04 | A04, A05.1, A05.2, A05.3, A05.4 | D | 4 |
| I05 | B01 | E | 4 |
| I06 | C03.1, C03.2, C03.3, C03.4, C04 | J | 4 |
| I07 | C07, I02 | J | 4 |
| I08 | B05, C01.1, C03.1, C05.1 | E | 4 |
| I09 | I08, M04 | A | 2 |
| I10 | G06, H01, I03 | A | 2 |
| M01 | C01.1, C02.1, C03.1, C05.1, I01 | J | 4 |
| M02 | M01, B08, A08, I02 | E | 4 |
| M03 | M02, D03, D05, D07, D08, D09, E05, I08 | E | 4 |
| M04 | M03, D06, A08 | D | 4 |

## 8. Verificación, QA ylímites

110IDs únicos,horas≤4,referencias existentes,DAG sin ciclos. Invariantes:I08/I09 antes de ampliación/C08;A08/I02 antesD01;D09 antesE03/E04/F08/H02;I10 antesG07;M04 antes de ampliación sin dependerC08;C02.1 antesM01/demo. H02 no precedeF08 intencionalmente: piloto gratuito.

Mutaciones de copias en memoria: retirar rutas de calibración vuelve falso su invariante;retirarI02 deD01 vuelve falso licencia;retirar aristasD09 vuelve falso permiso piloto. Esto prueba discriminación del instrumento,no implementación del producto.

Primera ejecución del verificador agotó tiempo por recorrer repetidamente elDAG;se rehízo memoizado. Una comprobación posterior contó también las8filas del resumen como operativas;se corrigió delimitando sección7 yconfirmó110filas iguales alJSON. No son defectos del plan publicados como si hubieran pasado: se descartaron esas corridas.

QA de otra instancia rechazó primero la ausencia deC02.1 en demo. Se conectó aM01 yse recalculó: demo165h,J36;piloto323 ytotal417 no cambian. Revisión final del contenido/tabla confirmó invariantes ysumas. El100% que esa revisión asignó no se adopta como garantía total: evaluación conservadora **43/45=95,6/100**, Completitud14/15,Razonamiento9/10,Documentación10/10,Innovación5/5,QA5/5. Se retienen descuentos por estimaciones sin calibrar ydependencias humanas externas. N/A55 de producto:ejecutabilidad15,seguridad15,testing15,DevOps10. Score de enmienda documental,no avance ni seguridad deCorpus.

TITAN FULL,enmienda de planificación. No AccessGrant implementado,no pruebas nuevas productivas,no decisiones humanas aprobadas. NO MEDIDO:productividad,servicio actual,costos,J/D,correcciones OCR efectivas,demanda/conversión. El registro de hallazgos no reemplaza revisión jurídica independiente.

Archivo vigente: docs/agents/respuestas/2026-09-17-03-enmienda-plan-corpus-v2.md. Evidencia: docs/agents/evidencia/2026-09-17-03-enmienda-plan-corpus-v2.json. El Doc original recibe aviso de enmienda;las secciones históricas no prevalecen sobre esta tabla.
