# Revision de la nueva auditoria Astra: hallazgos reproducidos, un falso rojo del instrumento

18-sep-2026 ART. Pedido: revisar su auditoria, referido a la instancia nueva Astra. Sujeto: informe2026-09-18-01-astra-corpus.md, commit LOCAL a7ff6c54f3c0fd9e0b7f3cb4d73db5cdcf2cff43, sobre productoPR11 3a60627101859ca92c9b0a4fdd436205b99bb504. No confundir con la auditoria anterior de OPUS ni con el Doc seleccionado que era antecedente.

## Dictamen

**El trabajo se sostiene en los casos reejecutados y corrige las debilidades metodologicas antes observadas en OPUS. Tiene un reparo real en el propio fixture SQLite: una conexion no cerrada puede cambiar el hash del archivo principal por checkpoint WAL y hacer fallar el cierre.** No es prueba de corrupcion de Corpus. No se modifico producto ni la entrega original del auditor.

El cierre remoto esta explicitamente pendiente de que el usuario elija conexion GitHub en aquella conversacion. No se le imputa haber ocultado ese pendiente ni se publica su commit en su nombre. Esta revision tiene sus propios artefactos.

## Sujeto y custodia local comprobados

El informe adjunto dice pruebas ejecutadas/publicacion pendiente. Su commit local contiene informe y evidencia. Se decodifico el wrapper local y el wrapper recuperado desde git LOCAL: coinciden y reconstruyen1380040bytes, SHA256895ab2adc8f47ae2cc3ab77db51542442a08d13348812c52248afdc13a0299f0, igual al declarado. Git remoto y Nexus no mostraban un cierre nuevo al iniciar. No inferir de eso que no haya ejecutado nada: los archivos e instrumentos estan y fueron inspeccionados.

## Reejecucion del banco

Se copiaron instrumentos y arbol a directorios nuevos, sin pisar resultados del auditor. astra_bench.py completo devuelveexit0,76comprobaciones y failed=0. No se las llama76tests independientes: incluyen paginas del mismo recorrido. El texto Unicode/CRLF/repetido se conserva; permisos, revocaciones y limites se comportan segun sus expectativas. No se reejecutaron de nuevo las63pruebas del autor en esta revision; permanecen como evidencia historica de la auditoria original.

Se reejecuto astra_followup.py sin cambios. Sus cuatro mutantes detectaron las propiedades objetivo correctas: exact_text_137, withdrawn_after_first_page, session_boundary_2900 y wrong_password. Cada mutante falla una asercion que el baseline satisface. Esto resuelve el problema anterior de declarar mutacion detectada solo porque cualquier proceso sale1.

## Minimizacion del lector heredado: confirmada en la familia declarada

Se reprodujo la enumeracion consecutiva de1795entradas, sin busqueda binaria. Familia: Ley 1 seguido de salto de linea, k letras A y salto final, k entero positivo. Primer fallo k1795, total1802caracteres. El caso1801 pasa. No afirmo minimo global y el auditor tampoco.

Los tres casos completos recorren la CLI real, ledger, lector exacto y handler HTTP historico:

| Caso | Esperado/ledger/exacto | Historico fusionar | ConcatenadorPR11 |
| --- | ---: | ---: | ---: |
| Repetitivo mas corto |1801|1801|2002|
| Primer fallo de esa familia |1802|1801|2003|
| No repetitivo de igual longitud |1802|1802|2003|

El historico conserva status200 al omitir un caracter. Al haber repeticion, confunde201caracteres con el solape real200. Es un defecto del consumidor historico, no del texto almacenado ni una regresion del lector versionado. El informe distingue correctamente ambos lectores y no concluye sobre produccion.

## Retroceso de reloj: observacion confirmada, gravedad acotada

Login ficticio a tiempos2000,2050,2049,1999 produce200,200,200,503. Reproducido por nuestra corrida HTTP. La frase general Clock rollback/nonfinite time fails closed existe en el reciboPR11, pero el codigo compara con inicio de ventana del presupuesto, no con la ultima autenticacion. La critica documental es sustentable; no prueba reloj controlable por cliente ni bypass de permisos.

## H1 del instrumento: conexion de origen queda abierta antes del hash

En nuestra reejecucion SIN CAMBIOS, el supervisor followup terminaexit1 al exigir source_unchanged. Para shorter_control ese campo esfalse; para los otros casostrue. Los tres candidatos permanecen iguales y todos los listeners se detienen. Los resultados de texto y los cuatro falsadores coinciden con el informe.

La preparacion usa with sqlite3.connect(source) as c y sale del bloque antes de medir source_hash, pero ese contexto confirma la transaccion: no cierra la conexion. El esquema usa WAL. Al cerrarse/recolectarse esa conexion mas tarde, SQLite puede trasladar datos del WAL al archivo principal: cambia el hash fisico sin cambiar filas.

Control mecanico separado: una baseWAL sintetica pasa de4096a8192bytes al recolectar la conexion, con filas exactamente iguales. No es un cambio al producto. En una COPIA de astra_followup.py agregamos solamente c.close() antes de source_hash: el supervisor terminaexit0, los tres controles de hash pasan y se conservan los mismos hallazgos y los cuatro falsadores. Se guardan la corrida roja, el control, la modificacion exacta y la corrida corregida.

El resultado original del auditor habia dado los tres source_unchanged=true: eso existe en sus archivos y no se declara inventado. Lo refutado es la reproducibilidad estable de ese control fisico sin cerrar el fixture, no la preservacion logica del escritor. Sugerencia: cerrar explicitamente fixtures antes de fijar el hash y definir si se comparan main+WAL o una instantanea consolidada. No atribuir automaticamente un cambio fisico a corrupcion.

## Comparacion justa con el trabajo anterior

En esta entrega hay baseline limpio, falsadores por asercion objetivo, consumidores identificados por revision, captura sin cortes explicita y minimizacion con alcance honesto. Es una mejora verificable respecto de las deficiencias que se habian marcado. No prueba superioridad de modelos: no es experimentoA/B y esta instancia revisa con informacion posterior. Las auditoriasSOL previas de esta conversacion siguen siendo antecedentes propios, no opiniones ahora certificadas por un tercero.

## Que no se midio

No hubo produccion, usuarios, derecho, TLS, carga, reposiciones de permisos, ni nueva verificacion de los6079registros. No se comprobo minimo global. No se publico ni reparo el commit del otro auditor. No se ejecutaron todas las posibles familias de entrada, carreras o sidecars. Ningun resultado autoriza merge o despliegue.

## Evidencia de esta revision

Carpeta hermana2026-09-18-02-revision-astra, dos archivos evidence.xz.b64.part0/part1. Concatenar en ese orden, base64 estricto y lzma decompress. JSON502161bytes, SHA2560fef94c8b379b33194b9abc2516c41c41e9966d8810da18e6a892228b71899a5. Incluye instrumentos originales, baseline nuevo con trafico, stdout/stderr completos de supervisores, cuatro mutaciones y sus procesos,1795entradas de scan, tres recorridoscompletos, diagnosticoWAL y control c.close. Los tokens sinteticos fueron redactados por el instrumento original al capturar; esa exclusion se mantiene declarada. No hay bases vivas ni texto de causas.

Rutas locales en el bundle son contexto de la corrida, no garantia de disponibilidad futura. Fuentes e inputs permiten reconstruir: extraerPR11 a repo/, restaurar astra_bench.py y astra_followup.py, recuperar lector84358cc en legacy84358.py, ejecutar baseline hacia baseline.json y despues followup con raiz propia. El ultimo puede fallar por el controlWAL documentado; el reemplazo de una linea del control esta preservado, no aplicado al original.

Metodo:lectura del mensaje e informe adjunto, git local/remoto, Nexus, Python/SQLite/HTTP, clones separados, falsacion de instrumento y comparacion de bytes. Alcance acotado y limitaciones expresas, no porcentaje de producto. La publicacion de esta revision no convierte en remoto el commit de la instancia nueva.
