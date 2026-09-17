# Corpus v2: arranque A01 y avance A02

## Pedido y autorizacion
Abraham confirmo ejecutar el plan por etapas respetando los gates humanos, y autorizo usar la conexion GitHub del workspace para publicar la rama. Esta autorizacion no aprueba merges, despliegues, gastos, contacto institucional ni dictamen juridico.

## Estado de las unidades
- A01: inventario operativo realizado, candidatos a respaldo identificados y comprobados en lectura. No equivale a restore probado ni respaldo externo.
- A02: cotejo inicial main/PR1/paginacion/servidor desplegado realizado. Reconciliacion integral de IDs y contratos entre todos los arboles sigue pendiente.
- B01: no iniciado. No se declara completado el plan.

## Medicion de A01
Fecha UTC: 2026-09-17T04:30:25.982949+00:00. corpus-api, cloudflared-corpus, nginx y gitea activos. RAG_DB comprobado en el entorno del proceso sin imprimir otras variables: /home/ubuntu/rag-abogacia-v7.db.

Lectura SQLite con mode=ro, query_only=ON y transaccion: 6079 documentos, 78930 pasajes, 6079 UID unicos. /censo y /estado devolvieron HTTP200 con esos mismos conteos. Fuentes: LexiVox15, Tarija1034, GENESIS5030. La consulta ley tiene32896 pasajes coincidentes: NO es el total del corpus. Correccion de anteriores resumenes propios que confundieron ese resultado con el total.

MemAvailable6299896KiB (aprox6.01GiB), 2CPU, disco disponible31875313664bytes; SwapTotal4194300KiB. Es una foto, no un benchmark de carga. Corpus en127.0.0.1:8080, Gitea en127.0.0.1:3000.

## Respaldos candidatos
Los archivos locales .previo, v9 y .antes-de-vigencia abren, quick_check devuelve ok, contienen6079 documentos y78930pasajes y el mismo digest del conjunto de UID. El JSON conserva nombres, tamanos y hashes. Igualdad de UID no prueba igualdad de todos los campos, vigencia, permisos ni frescura. No se restauro ni se creo un backup nuevo. F03 y RPO/RTO siguen pendientes.

## A02: que corre realmente
Main observado245cafb381884eed1d6f017de5f92f51745b9559. PR1 abierto en2360f27d43fdc9a1e2a74a3f6465698918df2ad1. Rama paginacion comparada84358cc821490cd90e31cb3f049ef7e691ccc4da.

El servidor productivo /home/ubuntu/api.py tiene18140bytes, SHA25601daf5e1cf7e75eb5adff0bdeb5fdd57af1ab5b3b79a5d56466b1179f34d5b48. Coincide con sistema/api/servidor.py de paginacion SALVO la ultima linea: bind y mensaje cambian0.0.0.0 por127.0.0.1. Esto identifica ese archivo, no todo el deployment. Conservar el endurecimiento al integrar. No reemplazarlo con main sin matriz de compatibilidad.

Rutas legacy: /buscar, /texto, /verificar, /censo, /estado, /salud. El servidor versionado main presenta otra topologia. B02 debera fijar el contrato realmente consumido, no asumir equivalencia por nombre de archivo.

## Hallazgo reciente de SOL
Leido docs/auditorias/2026-09-17-04-bypass-aprobaciones-plan.md de245cafb: C04/C06.1 pueden alcanzar trabajo sin algunos gates; el I09 unico no limita por si solo cada lote. No ejecutar esas ampliaciones ni reutilizar una aprobacion fuera de alcance. A01/A02 no dependen de esos gates. No se ha modificado la v2 ni tomado esto como nueva autorizacion.

## Publicacion
El clon fallaba con exit128 en push --dry-run: no podia obtener username no interactivo. La lectura publica funcionaba. La conexion del workspace autorizada creo esta rama desde245cafb; este recibo se publica por esa conexion, no mediante secretos antiguos ni credenciales copiadas del chat.

## Evidencia y limites
Companion: docs/agents/evidencia/2026-09-17-05-arranque-corpus-v2.json contiene campos seleccionados verbatim de las mediciones y diff completo del servidor. No es el volcado completo de todos los listeners ni de esquemas. Salidas completas conservadas en brain-env: corpus-audit-20260917/a01-live.txt, a01-backups.txt, a02-live-diff.txt; corpus-stage1-20260917/a02.json.

No se modificaron base, codigo productivo, credenciales, servicios ni configuracion del corpus. No se crearon110tareas, no se simularon entrevistas ni firmas. A02 parcial y B01 pendiente permanecen explicitos.

Doc publico: https://app.clickup.com/90171457413/docs/2kza6fw5-12557
