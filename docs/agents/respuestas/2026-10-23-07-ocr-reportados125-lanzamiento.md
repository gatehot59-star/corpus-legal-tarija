# OCR candidato: lote autorizado de cuatro PDF y 125 páginas

## Estado observado, no resultado final

La tanda real se lanzó el 23-oct-2026 a las 23:22:40 ART. Captura del 23-oct a las 23:23:47 ART: primer trabajo running, fase loading, cero páginas terminadas. Se observaron runner PID 121728, servidor candidato PID 121734 y worker PID 121738, start_ticks 3416747, dentro de corpus-ocr-reported125-_la5lozi.service. Job 8cbfcde8623a4827aa679acde29fbcca. El estado no acredita extracción terminada, exactitud legal ni promoción.

Autorización: approve_corpus_reported_ocr_125_pages, recibida 23:06 ART. Salidas candidatas separadas, sin reemplazar Corpus, cerrar reportes, mergear PR33 o pagar GPU. Es una regresión dirigida a documentos con problemas conocidos, no un banco ciego ni gold humano. No se publican comentarios privados ni identidades de quienes reportaron.

## Fuentes exactas y orden

1. Resoluciones 161 a 200, 2013/2014: 44 páginas, 2.875.681 bytes. UID dep-tar-compilado-de-sin-numero-2013-6b9dcffa. SHA256 6b9dcffaffdfb997dc4227dea2d89d0a01b4474d6c00abfa4bb4152ca4750784. Fuente: https://www.tarija.gob.bo/gaceta-oficial/resoluciones-del-pleno-de-la-asamblea?download=832:resoluciones-del-pleno-de-la-asamblea-161-al-200-del-2013-2014&start=500
2. Resoluciones 21 a 40, 2010/2011: 24 páginas, 2.426.652 bytes. UID dep-tar-compilado-de-sin-numero-2010-90d0176a. SHA256 90d0176a4a677f43436224a49f4a4fbd38aa030e6971d00e749a003afc538364. Fuente: https://www.tarija.gob.bo/gaceta-oficial/resoluciones-del-pleno-de-la-asamblea?download=859:resoluciones-del-pleno-de-la-asamblea-21-al-40-del-2010-2011&start=480
3. Resoluciones 266 a 305, 2011/2012: 39 páginas, 2.536.194 bytes. UID dep-tar-compilado-de-sin-numero-2011-0b1c20d7. SHA256 0b1c20d7ce63679204e2c28fd03f46ae0238873d5c85666de9bdfa0be71e3b8c. Fuente: https://www.tarija.gob.bo/gaceta-oficial/resoluciones-del-pleno-de-la-asamblea?download=846:resoluciones-del-pleno-de-la-asamblea-266-al-305-del-2011-2012&start=500
4. Resoluciones 86 a 103, 2010/2011: 18 páginas, 1.707.581 bytes. UID dep-tar-compilado-de-sin-numero-2010-0cc4b4a2. SHA256 0cc4b4a2f21be21002a741ceebdbc27f3e65799daca8177ac3e695bee755d053. Fuente: https://www.tarija.gob.bo/gaceta-oficial/resoluciones-del-pleno-de-la-asamblea?download=856:resoluciones-del-pleno-de-la-asamblea-86-al-103-del-2010-2011&start=480

Orden: documentos 1,2,3,4; páginas ascendentes; bloques consecutivos de hasta cuatro páginas. 11+6+10+5 = 32 trabajos. Sin cambio del límite MAX_PAGES=4 del candidato.

## Preparación PASS

Las cuatro copias coincidieron en hash, bytes y páginas. Se dividieron con pdfseparate/pdfunite. Para cada una de las 125 páginas se renderizaron original y subconjunto con los argumentos exactos del candidato: pdftoppm, 300 dpi, scale-to 5000, gray, PNG. Comparación 125/125 igual tanto en SHA256 del PNG como en SHA256 de píxeles, dimensiones y modo. Preparación finalizada 23:22:36 ART; 605,2224372749988 s. Esto prueba paridad de entradas, no OCR correcto.

## Instrumentos y pruebas

- Ejecutor publicado en scripts/ocr/reported125_20261023.py, commit da01df8bb459081bef8838fe76109f916ea54a85; bytes iguales al ejecutado como reported125-v2.py. 20.294 bytes; SHA256 a2ee42bcc8df2fa1afa2bce1b0c6cd1180fcaa1238627a20662ab95aa38a7c53. Lectura Git posterior exit0 e igualdad exacta.
- Preparador publicado como reported125_prepare_20261023.py, ejecutado como prepare125.py: SHA256 4211227801e3449ddfe7e00bfd008590e01638eff92e61b2eac3f0895157c0a4.
- Lanzador publicado como reported125_launch_20261023.py, ejecutado como launch_once.py: SHA256 a68f695d2481ab24ad20e6ddcdad6f648adf819d76eb9c610eeb2d163cc01244.
- Prueba publicada como test_reported125_orchestration_20261023.py, ejecutada como test_orchestration.py: SHA256 2c976ea4d37e994fd4b1e0614f398beed20d232dfa9170dc553d97f98afddbfb.
- Self-test: tres controles positivos y quince mutantes rechazados. Incluye página faltante/duplicada, fuente alterada, texto agregado contradictorio, imagen incorrecta, certificación falsa, bypass nativo y tiempo inválido.
- Orquestación sintética: recorrido completo de 32 trabajos/125 páginas y cuatro negativos (worker fallido, crudo contradictorio, demanda productiva, fuente alterada). Suite exit0; cada negativo devolvió exit1 y cero páginas confirmadas. API, procesos y recursos fueron dobles. NO son inferencias OCR ni prueba de aislamiento real.
- VM: self-test, orquestación, verify del runtime y pip freeze terminaron exit0 antes de inferir.
- Archivo de evidencia: un test real dio FileNotFoundError al faltar el padre archive. Corregido a mkdir(parents=True); nueva ejecución conservó state.json y partial.json byte a byte y produjo el manifiesto. La versión defectuosa nunca ejecutó OCR.

## Runtime y aislamiento

Candidato PR33 bb5578f798a5846fe1388c4e84dc2332ea537197, ocr_service.py SHA256 90df955df6edec61cc2c27876997848ba25c014d8dc5661fc2f1e91c6cf69a97. Producto conservado SHA256 ba6319aed537f601745e9d54c1156ce5ee2dd3da500581a94347fc4b64ce5e0f.

PaddleOCR 3.7.0, PaddleX 3.7.2, PaddlePaddle 3.3.1, Pillow 13.0.0. Modelo VL-1.6 revisión c5630abae1d940eafe0697512a0325494b02ab42; layout revisión 241f8bdfc77a7c7bee915a5057aaee58c235a8d3. CPU, un hilo, batch1, sin MKLDNN, LOW_MEMORY=0. Máximo 4096 tokens por página, warmup sintético128 por job. Semilla no fijada, sin cambio respecto del candidato. Freeze SHA256 80cbf340217d6c084fb017d1a3a644e773f6a13467606b5b1c41b4dde826f3a7. Modo ocr explícito.

MemoryMax6G, swap máximo3G, CPUQuota100%, Nice10, TasksMax96, LimitNOFILE1024, LimitFSIZE64M. Usuario ubuntu resuelto realmente UID/GID2000. PrivateNetwork, PrivateDevices, ProtectSystem strict, ProtectHome read-only, NoNewPrivileges, capacidades vacías, AF_UNIX únicamente. Escritura limitada al estado experimental. Un worker por job, sin paralelismo ni retries. Sondeos cada5s; ante cola/carga OCR productiva se aborta sólo el experimento.

Timeout del worker7200s intacto. El ejecutor espera hasta7260s por trabajo. Presupuesto global232920s (64h42m); límite externo233100s (64h45m). Son techos de seguridad, NO estimaciones de finalización. No hay garantía de disponibilidad continua de la VM ni notificación automática.

## Procedencia y persistencia

VM: /home/ubuntu/ocr-reported125-20261023-_la5lozi. Sello seal.json SHA256 054b612b7037dca17f82277a1e32af989f1dd15c60444cf54853447c74dfb01e. Las fuentes originales, subconjuntos, mapas, imágenes comparadas y comandos completos se conservan allí. Cada job terminal se copia a state/run/archive antes de admitir el siguiente, fuera de la retención24h del servidor; ante fallo se preservan parciales. Blancos explícitos no se contarán como inferencias.

Snapshot local de textos anteriores: baseline-before-ocr.json,419120bytes,SHA256 afe1b86f77d0a3ec2b19dcf740af21f4ce3d23be42fca3db298d766842545b48. Base abierta exclusivamente en modo lectura.48/18/32/11 chunks; chunks NO son páginas. No se alimentó ese texto al OCR ni se publicó la base.

Captura íntegra textual en brain-env: /workspace/corpus-ocr-reported125-20261023/captured-launch.json. Paquete completo local evidence-package.json:31 archivos, JSON descomprimido744991bytes SHA256 a1b5fe3055432607225e31af979fede804cd5db482e3e8e910ed9cd6212f2531; XZ39804bytes SHA256 5f3847def075e430f7361d2af74828702c57bd2803c653c5c214993fa9415637. No se commitea ese paquete ni binarios; este recibo no sustituye los registros completos conservados en VM y brain-env. Las cuatro fuentes de los instrumentos sí quedan en Git. Sello/manifiesto completo y evidencia final deberán acompañar el cierre posterior del lote.

## Incidentes y límites honestos

El primer preparador falló antes de crear salidas por UID1000 asumido erróneamente; se resolvió ubuntu como UID2000 y sólo se corrigió el directorio experimental. Segundo preparador terminó125/125. Se observó corte SSH durante la preparación; host recuperó acceso y después también brain-env. No se relanzó OCR. Se consultó inicialmente un nombre de API inexistente corpus-api-staging; el servicio real corpus-api.service permaneció activo PID726. Django PID727 y OCR productivo PID739, ambos activos, NRestarts0; mismos PIDs al capturar lanzamiento.

Corrección del mensaje del commit da01df8: la cifra43/45 y95,56/100 no estaba sustentada por una rúbrica medida. Se retira como aprobación. No se acredita cobertura formal, OWASP, auditor externo ni CI verde. Estas pruebas sólo justifican el arranque experimental dentro del alcance aprobado, nunca producción.

PASS: fuentes/paridad125, controles del instrumento y pins comprobados. EN CURSO: OCR real. NO MEDIDO: exactitud de las125 páginas, cotejo final con los PDFs/texto previo, adjudicación humana, latencia total y robustez general. Ninguna tarea o reporte cerrado.
