# SOL: contexto recuperado antes de auditar Corpus actual

17-sep-2026, ART. Pedido: recuperar auditorias previas y plan antes de revisar lo nuevo. Este cierre NO es la auditoria de PR7 ni aprobacion de producto.

## Antecedentes recuperados y autoria

1. SOL preparo el relevamiento del 16-sep: mediciones/2026-09-16-20-relevamiento-bibliotecas-piloto-membresia.md. Corpus independiente de Custos; bibliotecas utiles, piloto en dos universidades, feedback y posterior membresia. USD10 es objetivo, no precio/periodicidad ni demanda ya validados.
2. SOL preparo docs/agents/respuestas/2026-09-17-01-plan-integral-corpus-titan-full.md (86d57c2). BRAIN audito ese plan, no al reves. SOL acepto los reparos y produjo 2026-09-17-03-enmienda-plan-corpus-v2.md (3b6cb6d). Los reportes Nexus28/29/31 registran esa secuencia.
3. docs/auditorias/2026-09-17-04-bypass-aprobaciones-plan.md (245cafb) es AUTOPRUEBA de la enmienda: C06.1/C04 alcanzables sin ciertas decisiones y un I09 reutilizable para tres lotes. No prueba permisos productivos vulnerados. La enmienda conserva su hash publicado; no aparecio otra posterior en su historial de main consultado.
4. Revision de SOL a PR2: docs/auditorias/2026-09-17-05-revision-avance-brain.md (cb08206). Antecedente:34tests y3mutantes; detecto manifiesto ausente confundido con vacio y raiz de textos symlink externa. SOL implemento despues PR3 (Nexus34): esa implementacion no es revision independiente propia.
5. Revision de SOL a PR4/PR5: docs/auditorias/2026-09-17-09-revision-pr4-pr5.md (f128953). Antecedente:74tests,15textos nacionales y3fuentes preservadas; PR5 aceptaba cuerpo bajo hidden/template. No demostro perdida juridica en esas fuentes.
6. SOL implemento PR6 (Nexus36). Su docs/auditorias/2026-09-17-11-pr6-cierres-cruzados.md (28e299c) fue AUTOPRUEBA: tres bypass table/template/object comparados con Chromium mientras pasaban29tests. BRAIN reprodujo esos casos y corrigio los cierres posteriormente.

W-01: retomar el rol SOL no vuelve ajeno el codigo antes implementado por SOL. Separar esa autoria de la correccion posterior de BRAIN y no certificar independencia por cambio de nombre. Los commits usan una identidad Git compartida; la atribucion se contrasto con documentos y Nexus, no se dedujo del autor Git.

## Plan que gobierna

V2:80tipos,110ocurrencias individuales de hasta4h estimadas. Diagnostico/contratos; primeros lotes autorizados; calibracion I08; demo cerrada M04; decision I09 antes de ampliar; coleccion revisada; piloto gratuito D09; validacion comercial despues. Buscar, verificar, guardar, compartir y reportar errores son el objetivo, no descargar indefinidamente.

Estimaciones del plan:demo165hbase,piloto323h,total417h; no runtime ni plazo comprometido. Revision juridica, recursos humanos, permisos y disponibilidad no quedan satisfechos por tests. Los reparos al grafo siguen como antecedentes que no se deben dar por cerrados solo porque la v2 diga vigente. No se modifico ni ejecuto el plan en este turno.

La auditoria de cinco registros es antecedente de BRAIN segun la propia enmienda, no de SOL: Ley483 con230000frente390000 en imagen; fechas/titulo; LexiVox etiquetado oficial; edicion y abrogacion de Familia. Son criterios de aceptacion pendientes de comprobar, no cotejos repetidos hoy.

## Sujeto actual fijado

Main leido fdfea3d5a7876164f60478a427116d98012cea67. API GitHub confirma PR2-6 mergeados; PR1 abierto2360f27d43fdc9a1e2a74a3f6465698918df2ad1; PR7 abierto d78ad5977ec723fa39a421d4eb2f80d19a2a5f62. Codigo PR7 declarado probado188ae7df0c32344507de9b0031e5b0f3714fb1c9. DiffPR7:5archivos, incluye clean_snapshot.py,10tests yworkflow.

Primero revisar integracion exacta de PR2-6 y correccion de BRAIN, despues PR7. Los87tests del merge y los6079UID preservados en copia son afirmaciones de sus recibos: NO fueron reejecutadas hoy. En PR7 comprobar origen intacto,6076documentos/pasajes no seleccionados,3versiones archivadas,identidad estable,rollback,lector,FTS,citas y procedencia.

Que NO se midio que importaba: UID estable no conserva por si solo enlaces nro/desde, ranking, fidelidad juridica o vigencia. BRAIN ya reconoce enlaces profundos pendientes,oficial:true incorrecto para LexiVox y que publication_authorized:false no es barrera ejecutable. Son limites conocidos, no hallazgos nuevos de SOL. No autorizar publicacion con esta recuperacion de contexto.

## Fuentes ClickUp

[Plan v2](https://app.clickup.com/90171457413/docs/2kza6fw5-12477/2kza6fw5-14737) · [Auditoria de BRAIN al plan](https://app.clickup.com/90171457413/docs/2kza6fw5-12497/2kza6fw5-14757) · [Autoprueba del plan](https://app.clickup.com/90171457413/docs/2kza6fw5-12537/2kza6fw5-14797) · [Revision PR2](https://app.clickup.com/90171457413/docs/2kza6fw5-12597/2kza6fw5-14857) · [Revision PR4/PR5](https://app.clickup.com/90171457413/docs/2kza6fw5-12697/2kza6fw5-14957) · [Autoprueba PR6](https://app.clickup.com/90171457413/docs/2kza6fw5-12737/2kza6fw5-14997) · [Auditoria de fuentes](https://app.clickup.com/90171457413/docs/2kza6fw5-12457/2kza6fw5-14717) · [Merge](https://app.clickup.com/90171457413/docs/2kza6fw5-12797/2kza6fw5-15057) · [Entrega PR7](https://app.clickup.com/90171457413/docs/2kza6fw5-12817/2kza6fw5-15077).

## Metodo y limites

Instrumentos:Docs relevantes,git clone/fetch/log/ls-tree/show/diff,API publica de PRs,SELECT Nexus por servicio(tablas,reportes,estado/eventos,mensajes pertinentes). Inventario de entornos y permisos del metodo leidos desde git mudh-mobile. No orden Corpus adicional localizada en el arbol consultado; no inventar una. Nexus recuperado no acredita que todos los agentes reportaran lo ultimo. Un resultado corpus de DualBrain se excluyo por sujeto equivocado.

Clon separado: directorios iniciales eran resultados sin git y otro clon tenia cambios preparados; quedaron intactos. Se descarto tambien un comando mal transportado, no se declaro fallo de la maquina. No tests nuevos,VM,GPU,Actions,OCR,despliegue,ingesta ni cambios de permisos.

Rubrica de contexto:completitud acotada a antecedentes centrales;razonamiento separa autoria/momento/sujeto;documentacion enlaza fuentes y evidencia;proceso preserva trabajo ajeno y declara lo no ejecutado. No porcentaje de avance ni certificacion exhaustiva. NO MEDIDO:auditoria actual de PR7,produccion,restore,RPO/RTO,revision juridica,privacidad,demanda y preparacion comercial.

Resultado:contexto recuperado; auditoria actual pendiente, sin aprobacion anticipada.
