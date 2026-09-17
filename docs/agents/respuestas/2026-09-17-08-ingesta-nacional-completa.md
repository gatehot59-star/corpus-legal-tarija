# Continúo PR3: candidato nacional completo o rechazo

Pedido: SIGUE desde el Doc del PR3. Rama titan/national-batch-candidate, PR4 apilado sobre PR3, sin merge ni despliegue.

Doc: https://app.clickup.com/90171457413/docs/2kza6fw5-12657
PR: https://github.com/gatehot59-star/corpus-legal-tarija/pull/4

## Ejecutado
Conservado lector PR3 b61ac872316dba4ea5b1e04d44a3a195f32c4dfa sin cambios (diff vacío). Repetidos20tests lector,23contratos y3mutantes. Fuente real /workspace/nacional:15archivos aceptados por hash completo,0rechazados. No textos originales alterados.

Se reprodujo combinación sintética de ingesta PR1 con lector PR3: dos textos correctos dan2documentos yexit0; uno alterado da1documento yexit0/VERDE. El log SI declara SIN TEXTO1: no está oculto, pero el VERDE acredita lo aceptado, no integridad del lote entero. No se ejecutó sobre producción.

Nueva entrada sistema/api/ingesta_nacional_segura.py: exige digest/conteo esperado del manifiesto, valida todo antes de escribir, no ajusta el objetivo según rechazos, rechaza colisiones UID y metadata incompleta. Construye una base temporal, verifica UID/SQLite, realiza SQLite backup y crea destino exclusivo sin sobrescribir. Permisos0600. No modifica ingesta.py del legado ni llama un despliegue.

Candidato real:15documentos,3473pasajes,15vigenciasNULL,quick_checkok; UID nacionales iguales a la copia local deploy:15/15,0perdidos,0nuevos. NO es reemplazo del corpus6079documentos. SHA256 base569f4da804f10f7c9c2f92c9970a43e7e7fbee3172c05d3353d071761457e6a0. Manifiesto e650ef071bdf62fb647ff5156666f7aaa643d069332aefa484d5de2f6bdbd696, sin alterar.

## Prueba sobre código publicado
Revisión68fc7ff9cfeb5807e054eed6c639862920dd33a9 extraída con git archive:20+23+11=54tests,exit0. Falsador de lote: dos defensas redundantes removidas en copia (omitir rechazado y anular conteo), test exige exit2 pero mutante produce0, detectado exit1. No confundir mutante rechazado con candidato defectuoso.
CI contracts completed/success: https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35220753599/job/105200019902,12:22:40Z-12:22:46Z. Review Copilot solicitada; no aprobación inferida.

## Reproducción
python3 tests/test_fuente_nacional_integridad.py
python3 tests/test_provenance_v2.py
python3 tests/check_provenance_mutations.py
python3 tests/test_ingesta_nacional_segura.py
python3 tests/check_batch_mutation.py

python3 sistema/api/ingesta_nacional_segura.py --source /workspace/nacional --output /workspace/corpus-pr3-continue/national-candidate.db --expected-records 15 --manifest-sha256 e650ef071bdf62fb647ff5156666f7aaa643d069332aefa484d5de2f6bdbd696
El output debe NO existir. Elegir nombre nuevo, no borrar ni sustituir producción para repetir.

## Límites
El consumidor legacy sigue intacto; esta CLI requiere invocación explícita. No arregla etiquetas de API, HTML contaminado, vigencia, OCR, revisión jurídica o privacidad global. La fuente se presupone inmutable; sin defensa TOCTOU contra mismoUID ni nuevos topes de tamaño. No garantía ante corte eléctrico ni RPO/RTO. No se sirven datos desde esta base, no se carga material sensible.

B03 avanza a construcción nacional aislada; integración/publicación autorizada de corpus completo y B04 siguen pendientes. Nada autoriza C04/C06, revisión jurídica o ampliación de presupuesto. QA de producto NO APROBADO; no porcentaje artificial.

## Evidencia
Companion docs/agents/evidencia/2026-09-17-08-national-batch.json conserva salida completa de los11tests nuevos, falsador nuevo, candidato real y ambos brazos del llamador. Los43tests heredados fueron reejecutados; resumen en ese archivo y logs completos de la nueva ejecución en /workspace/corpus-pr3-continue/published-reader.log y published-contracts.log; evidencia original del PR3 ya versionada en su recibo. No se presenta un resumen como log crudo.

Código y tests son archivos completos versionados. Ninguna base binaria se commitea. Un error de transporte de base64 se rechazó antes de materializar y se corrigió cotejando el SHA del payload; las pruebas finales se ejecutaron desde git archive de la revisión publicada.
