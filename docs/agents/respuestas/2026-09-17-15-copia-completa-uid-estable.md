# Texto limpio en copia completa conservando UID

Pedido: PUES SIGUE, continuación autorizada por etapas.
PR7 https://github.com/gatehot59-star/corpus-legal-tarija/pull/7
Doc https://app.clickup.com/90171457413/docs/2kza6fw5-12817
Base fdfea3d5a7876164f60478a427116d98012cea67. Código188ae7df0c32344507de9b0031e5b0f3714fb1c9. No merge, deploy ni cambio de producción.

## Implementado y corrido
pipeline/clean_snapshot.py conecta el extractor B04 con una copia SQLite completa. Exige mapeo con hash fijado, UID, hash anterior, URL fuente, título esperado y hash HTML. Sólo nacionales LexiVox, lote1..100. Archivo original/base/mapeo confiables e inmutables durante operación. No cambia UID ni doc_id.

SQLite backup a temporal, transacción de los cambios, archivo de filas/chunks anteriores más extracción nueva en corpus_cleanup_versions; resegmentación con trozar existente. Conteo/conjuntoUID,FK,quick_check e integridadFTS antes de salida exclusiva0600. Destino existente nunca reemplazado. HTML original no se modifica; fragmentoHTML sigue no sanitizado.

## Base real de ensayo
Origen: copia local /workspace/deploy/rag-abogacia-v7.db, no snapshot nuevo de VM.6079documentos,3seleccionados (Familia,Comercio,CPE),6076filas no seleccionadas y sus chunks idénticos. UID set antes/después31481e481177eb6d487492f7f30b7f8e1c21843f092054bf5288e298e2c542d0.3registros de historial.78930->78064pasajes por limpieza/resegmentación. Identidad de cada doc preservada.
SHA256 origen antes/después1147cf4ba6b02a6c148cd0c87aabd6cc99ae88a7dc6cc4e8c64d02eca01ec3ed,idéntico. Candidato queda sólo en el taller; NO se commitea ni adjunta base completa por contener material sensible.

## Lector real, alcance de la prueba
Servidor legacy versionado84358cc821490cd90e31cb3f049ef7e691ccc4da importado con base candidata, HTTP127.0.0.1puerto efímero, cerrado al finalizar.3UID existentes responden200,navegación comprobada ausente; documento(uid) reconstruye el texto completo con SHA igual al nuevo almacenado. /censo6079docs/78064pasajes.
UID preserva enlace al documento, NO semántica de localizadores nro/desde antiguos: hace falta versión explícita antes de servir enlaces profundos.

## Bloqueo antes de publicar
La API legacy devolvió oficial=true para los3textosLexiVox. No ignoro ese resultado ni publico así: necesita consultar autoridad/versionado explícito. Nuevas extracciones registran secondary en ledger; métodohtml NO basta. Aliases anteriores se conservan con sus hashes; exponer relación con versión nueva sigue pendiente. Citas expandidas antiguas se guardan en historial pero no se reutilizan en nuevoschunks: regeneración/evaluación pendiente. publication_authorized=false es metadata declarativa, NO control de acceso.

## Pruebas y falsador
10tests CLI SQLite desde git archive188ae7 exit0. Mutación que elimina condición hashprevio/URL:2tests negativos fallan exit1; controlbase pasa. SHA del módulo probado y publicadoa851d3d0157584dac362466d916b6e68a3e3f13994a7b3a7105814727deff257 idéntico.
CI stable_identity completed/success20:31:50Z-20:32:00Z:
https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35271344017/job/105371267223
CI corre10fixtures,no base real. Copilot solicitado,noaprobacióninferida.

## Reproducción
python3 tests/test_clean_snapshot.py
python3 pipeline/clean_snapshot.py --help
Para lote real elegir output NUEVO y mapping revisado con --mapping-sha256, --expected-count6079 y --expected-uid-sha256; nunca pasar la baseviva como destino. Logs completos de construcción/readback/mapping/lector en /workspace/corpus-clean-copy/results; companionJSON incluye prueba nueva y readbacks pertinentes, no textos de causas.

## Límites
Sin garantía ante adversario local concurrente, cortes eléctricos,RPO/RTO,dictamenjurídico,anonimización o rendimiento10x. No se cambióLey483,vigencia,cuentas o toda la colección. Cap100entradas no equivale a presupuesto total de memoria. Revisión de antecedentes del plan/PRs antes de escribir; no se pisóPR1.
Error de transporte detectado por base64/SHA antes de escribir; retransferencia por bloques y pruebas publicadas descartan dar verde al archivo truncado.
Próximo: lector con autoridad y versión/localizadores coherentes, evaluación de búsqueda y publicación autorizada. Plan integral NO terminado.
