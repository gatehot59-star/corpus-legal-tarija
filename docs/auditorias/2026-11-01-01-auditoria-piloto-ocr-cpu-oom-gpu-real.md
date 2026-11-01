# Auditoría del piloto CPU / API / GPU: CPU OOM, GPU real, comparación incompleta

Fecha: 1-nov-2026, ART. Pedido: «AUDITA EL TRABAJO DE ASTRA 6.1 TIERRA». Sujeto: el piloto OCR iniciado el 31-oct en esta conversación, no toda la obra de un modelo ni el producto Corpus completo.

## Conclusión

Hubo trabajo real y una nueva ejecución válida de GPU. No se completó una comparación de CPU, API comercial y GPU que permita decidir costo, latencia web o despliegue. El operador anterior no afirmó haber terminado esa comparación: la dejó pendiente. No confundir una entrega incompleta con resultados inventados.

Hallazgos principales:

1. **ALTA: configuración CPU regresiva frente al antecedente conocido.** El piloto impuso 5 GiB RAM, 1 GiB swap y CPUQuota 50%. El perfil instalado era 6 GiB, 3 GiB y 100%. El README ya documentaba que el intento inicial de 5 GiB había muerto por OOM. El kernel confirma que el nuevo piloto agotó tanto sus 5 GiB de RAM como su 1 GiB de swap durante la carga. Se mató al worker a las 15:08:48 ART del 31-oct. Esto prueba el fracaso de esa configuración, no la inviabilidad general de CPU ni que 6 GiB basten para esta página.
2. **ALTA: falta de seguimiento terminal.** El servicio terminó con Result=oom-kill, MainPID=0, ActiveState=failed. El trabajo persistido seguía diciendo running/loading, con cero páginas completadas. El estado JSON no era prueba de vida. La afirmación anterior de que estaba corriendo correspondía a una observación previa, no se la refuta retroactivamente. El defecto es dejar ese estado sin reconciliación ni cierre de los trabajos ya lanzados.
3. **MEDIA: detector externo capaz de aceptar una salida vacía.** La expresión original clasifica completed si encuentra la subcadena event: complete. Dos controles sintéticos con finalización sin texto OCR fueron aceptados. El positivo con texto y el negativo con error se comportaron como se esperaba. Es un falso éxito potencial reproducido localmente, no un falso éxito observado en el proveedor: las dos solicitudes reales devolvieron error.
4. **Entrega del piloto incompleta.** No se entregó una tabla final comparable, costo medido ni cierre Git+Doc verificado. En el main inspeccionado no había un commit nuevo del piloto y no apareció un reporte/trabajo pertinente en las consultas de Nexus. No se afirma que no exista un documento en ningún lugar: la búsqueda de ClickUp no fue exhaustiva. Suspender por falta de una API viable era legítimo; no se exige contratarla. Faltó recoger y registrar los resultados terminales de lo ya iniciado.

## Sujeto, versiones y autoría

Main inicial: b722bda135943a125152f0031accd15b2ab7b238. No se auditó PR33 como si estuviera desplegado.

Servicio instalado: SHA256 ba6319aed537f601745e9d54c1156ce5ee2dd3da500581a94347fc4b64ce5e0f, idéntico al [código versionado](https://github.com/gatehot59-star/corpus-legal-tarija/blob/5a108c028792b409974b00ebe04be5e1215f9029/sistema/ocr_sidecar/ocr_service.py). El [README de esa revisión](https://github.com/gatehot59-star/corpus-legal-tarija/blob/5a108c028792b409974b00ebe04be5e1215f9029/sistema/ocr_sidecar/README.md) documenta el OOM previo y el perfil instalado.

Kernel nuevo: [Kaggle, versión 1](https://www.kaggle.com/code/abrahammendieta/corpus-ocr-piloto-20261031-1805). Fuente descargada y fuente enviada idénticas, SHA256 45e21541e97a7e4ca0103f7f35bf7bd2e815bea33ff7fa03402c78a04ac1aff9. Runner: cb225c31f9883cd18829633d7fcf210372db7a3d207592b3f11c789a0c6b7521.

Esta verificación continúa la misma conversación. No se presenta como revisión por un operador independiente ni como prueba de superioridad de un modelo. Los oráculos pertinentes son el kernel/systemd, los bytes descargados de Kaggle y expectativas sintéticas fijadas fuera del detector juzgado. No se volvió a ejecutar OCR durante la auditoría.

## Resultados y límites por afirmación

- **CONFIRMADO: identidad de entrada CPU/GPU.** PNG público de Ley 524, página 1: 4.443.312 bytes; SHA256 669c89a75a4e3ad2ecc567f03a13e50c2552265b3baf4e4f547e362acbb9c3c4. La CPU reencodificó el PNG: cambiaron los bytes del archivo, no sus píxeles RGB. Ambos RGB dan 7e71fb47a5464b0ad49ecd5d6f6f2b867e36492b8524b2a37887216e00d5a870. La API verificó el hash local antes de enviar; no devolvió un hash del servidor.
- **REFUTADO como estado actual: CPU running.** El estado guardado contradice al servicio y al evento OOM. No hay resultado OCR CPU. No fue el límite de 45 minutos: el fallo fue de memoria durante la carga.
- **CONFIRMADO: GPU terminó.** Una página, 2.845 caracteres, 16 bloques, parámetros en gpu:0, Tesla T4, exit 0. Había dos T4 disponibles, pero no se acreditó uso de ambas.
- **CONFIRMADO como tiempo de inferencia del runner: 39,331635054 s.** Carga: 5,815086787 s; calentamiento: 2,536742792 s; proceso de inferencia completo: 60,056716705 s. Desde el timestamp del recibo de envío hasta completar el bootstrap: 1.021,510914 s, aproximadamente 17 min 2 s. Este intervalo incluye espera y preparación; los relojes son de máquinas distintas. No es una cola aislada ni latencia de una página web.
- **CONFIRMADO: salida GPU íntegra.** Texto ensamblado igual al JSON crudo en UTF-8 exacto. Crudo SHA256 260943a380eca8a1f01bdf46ce6cd9b24b8744158410e39d0cd217b336b7feae. Coincide con el crudo histórico del 16-oct; eso por sí solo no demuestra contaminación. Hay código, logs y timestamps de ejecución nueva. No se midió fidelidad jurídica humana.
- **CONFIRMADO: dos intentos externos fallaron.** 68,943243913 s y 4,904236528 s hasta error. Causa upstream: NO MEDIDO. La [demo oficial](https://huggingface.co/spaces/PaddlePaddle/PaddleOCR-VL-1.6_Online_Demo) no equivale a una API comercial con precio, retención y SLA verificados. No se adjudica a esa demo el precio anunciado por otro proveedor.
- **CONFIRMADO, alcance estrecho: aislamiento del piloto.** Se usaron estado/socket propios, evitando admitir trabajo en el estado instalado que expira archivos antiguos. En las lecturas, OCR/API/staging seguían activos con inicios anteriores al piloto; fuente OCR sin cambio. Ausencia de impacto transitorio, cambios en todo el sistema o degradación de servicio: NO MEDIDO.
- **NO MEDIDO: speedup CPU/GPU, costo por página y comparación de tres vías.** No hay tiempo de OCR CPU completado ni salida API válida.
- **Límite reconocido, no falso hallazgo:** el protocolo declara una pasada exploratoria por brazo viable. No prometió tres repeticiones ni reproducibilidad. No se le imputa ese claim.

## Controles del auditor

Instrumento: verify_audit.py, SHA256 ec4f9d7f6b394f504409fc30f6e531265a20cfd9e7ec948c59cb16f112051f79.

Dos ejecuciones en scratch nuevo: exit 0, resultados decisivos idénticos. Seis controles propios: tres positivos y tres negativos para hash, estado vivo y ensamblado UTF-8. El mismo verificador acepta el positivo y rechaza la alteración pertinente. Cuatro respuestas SSE sintéticas: dos controles correctos y dos violaciones del contrato OCR reproducidas. La suite del autor pasó sus cinco casos del adaptador; no se la presenta como prueba independiente de OCR ni exactitud legal. Un replay adicional desde la selección publicable validó 19 archivos GPU y produjo los mismos resultados.

Se buscaron también: muestra equivocada, ejecución GPU sustituida por CPU, fuente distinta de la enviada, texto ensamblado distinto del crudo y modificación del archivo OCR instalado. No aparecieron esos fallos en el alcance medido.

Errores propios declarados: el primer lector del auditor no compiló por un byte nulo y no se ejecutó en la VM; la versión corregida sí. Lecturas anónimas de archivos privados devolvieron 404 y se resolvieron con la conexión autenticada. journalctl no tenía archivos; la evidencia OOM proviene de dmesg. La primera captura de kernel filtró palabras; se agregó el bloque completo de 114 líneas del segundo exacto del evento. No es un volcado completo del kernel.

## Qué no se midió que importaba

CPU con un presupuesto defendible; API real con credencial y condiciones comerciales; precio facturado; cola, carga y latencia navegador a resultado; concurrencia; recuperación tras OOM; retención y borrado de documentos; exactitud humana de cifras, negaciones y omisiones; múltiples páginas y repetibilidad. Nada de esto se arregla con que la GPU haya salido0.

## Aceptación propuesta de cierre, sin ejecutar arreglos

Responsable propuesto: quien implemente el piloto, no el auditor. No se creó una asignación ni un issue.

- CPU: registrar presupuesto y justificación antes de correr, controlar actividad productiva y capturar estado terminal. Una nueva corrida requiere un encargo de implementación, no se autoriza por este informe.
- Estado: una muerte del worker debe quedar como error identificable, no running. Probar positivo vivo y OOM simulado en recursos aislados.
- API: validar evento y salida OCR; rechazar null/vacío; lograr al menos un positivo real antes de comparar rendimiento. Si no hay acceso autorizado, declarar el brazo NO MEDIDO.
- Entrega: matriz con mismos inputs, diferencias de configuración, tiempos separados, errores y costo observado o NO MEDIDO. Sin convertir una demo pública en SLA comercial.

## Método, evidencia y entrega

--- METODO PROMETEO ---

Modo: auditoría acotada. Funciones: revisor, verificador experimental y control final del mismo operador. Lecturas en brain-env, VM por SSH, GitHub, Kaggle y Nexus; controles Python locales. Escrituras autorizadas: archivos propios de auditoría, documentación/evidencia Git, Doc y reporte propio Nexus. Sin inferencias nuevas, compras, credenciales nuevas, merge, deploy ni reparación de producto. Las comprobaciones del transporte Git en el host no modificaron repositorios ni servicios; la conexión GitHub siguió disponible.

Reglas aplicadas: E-01 (sujeto/momento), W-01 (capacidad del instrumento e independencia), cierre durable de PROMETEO. No se asigna una nota numérica que compense fallos.

Gate I, instrumento: PASA para estas propiedades acotadas. Sujeto, oráculos, positivos/negativos, recursos, repetición y captura seleccionada comprobados. Revisión por otro operador: NO MEDIDO. Pruebas de producto, despliegue y accuracy: N/A al encargo de auditoría.

Gate II, informe: PASA en el alcance seleccionado. Distingue diseño, seguimiento, límite declarado y fallo reproducido; no culpa al producto de errores del auditor ni convierte 39 s en latencia web.

Gate III, entrega: INCOMPLETA al crear este archivo. Falta adjuntar/verificar el paquete de evidencia y cerrar Doc/Nexus. Se actualizará sólo después de comprobarlos. El veredicto experimental no depende de simular ese cierre.

Paquete preparado: evidencia seleccionada sin truncar los archivos incluidos, 179.702 bytes, SHA256 5227f193d7d4cf29b4f59a046123e5448ef58fb6030ebe6822ac151ff10034ac. Compresión reversible XZ+base64. Incluye fuentes del piloto, salidas crudas seleccionadas, estados, configuración, evento OOM y controles. Excluye binarios, metadatos auxiliares de instalación, mensajes ajenos y credenciales. El servicio instalado se referencia por Git inmutable con identidad de bytes comprobada. La selección y las exclusiones están dentro del paquete.

## Cierre comprobado, 1-nov-2026

Informe y selección de evidencia publicados en main en f937fe3cf4a5346287adc341fa5d4cc501da8ce2. Se recuperaron por Contents API y raw; ambas vías dieron los mismos bytes y sus blobs Git coincidieron. El script reducido extraído de Git coincide byte a byte con public_controls.py ejecutado localmente y volvió a producir el mismo stdout, exit0 y stderr vacío. Se compararon seis bloques JSON GPU publicados contra los archivos originales.

[Doc público de la auditoría](https://app.clickup.com/90171457413/docs/2kza6fw5-26077), ubicado en Space > Doc, creado y leído de vuelta. Continuidad propia registrada en Nexus, reporte140. No se marcaron trabajos ajenos terminados ni se cambiaron mensajes.

Nueva lectura terminal a2026-11-01T04:35:51.313072+00:00: piloto CPU failed/oom-kill sin PID; GPU COMPLETE; OCR/API/staging activos con los mismos inicios y cero reinicios automáticos. Cero nuevas inferencias en la auditoría.

**Gate III sigue INCOMPLETA por una razón concreta:** el paquete ampliado íntegro no se publicó en Git. Sí están publicados y comprobados el informe y la selección explícita de capturas y controles. El paquete local de179.702bytes y su SHA indicado arriba quedan registrados en Nexus para continuidad. No se atribuye este pendiente al producto, a falta de permisos ni a una caída de las conexiones. No se presenta la selección como captura completa ni se firma aprobación de producción.
