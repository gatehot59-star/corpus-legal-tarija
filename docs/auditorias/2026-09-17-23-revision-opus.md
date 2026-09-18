# Revision del auditor OPUS: trabajo real, cierre de evidencia incompleto

17-sep-2026 ART. Sujeto exacto: informe docs/auditorias/2026-09-18-opus-pr8-pr11-independent.md, commit982b82cb1b5925ba45175a3dd185ffeca6eb6b72, y su banco en el taller. Pedido: revisar que hizo el auditor, no arreglar Corpus ni reaprobar la auditoria anterior de SOL.

## Dictamen

**El auditor ejecuto trabajo real y amplio las pruebas. Sus conclusiones tecnicas principales se reproducen, pero la entrega necesita completar custodia de evidencia y corregir el criterio de exito del banco. La comparacion llamada legacy debe identificar que lector uso.** No se invalida toda su auditoria ni se inventa un fallo del producto.

## Lo confirmado por esta revision

Se leyeron el Doc de OPUS, su informe commiteado, los cuatro instrumentos locales y el bundle. Se reejecuto opus_bench.py sobre su candidato en un directorio nuevo, sin pisar sus bases ni corridas. Resultado:54casos,53pasan y uno falla; thread detenido. Los grupos corresponden a19fidelidad,23permisos y12login. El unico fallo base es B6c, espacio final del header, que OPUS habia descartado expresamente como normalizacion del transporte y no defecto de Corpus.

Se repitieron los cuatro bancos mutados de OPUS en directorios nuevos: truncar pagina produce cuatro fallos de texto; ignorar retiro agrega el fallo de retiro; ampliar expiracion agrega el fallo del limite temporal; aceptar cualquier password rompe password incorrecta y su secuencia5+1. Los cuatro terminanexit1 por aserciones relevantes, no errores de import. Por eso la deteccion de esos cuatro defectos se sostiene, aunque el agregador sea mejorable.

No se reejecutaron aqui otra vez las63pruebas de BRAIN. Se inspeccionaron sus logs dentro del bundle de OPUS y se contrastaron con la corrida previa en esta conversacion; eso es comprobacion documental, no nueva corrida63.

## H1: evidencia nueva no acompana al informe en main

El commit982b82c contiene UN archivo: el informe de44lineas. El arbol completo de docs/auditorias en esa revision no contiene el banco, resultados o bloques nuevos de OPUS. Su Doc nombra el archivo pero no enlaza a la evidencia nueva recuperable desde git.

La evidencia existe localmente: /workspace/opus-audit-20260918/evidencia-opus.json,51615bytes; SHA2566983abd5aa2c0556b6947625b224b16c928092e4b26f75e5096b2195d71177ba, igual al declarado. Esto refuta que faltara toda evidencia o que hubiera inventado el hash; NO completa su publicacion remota. El informe dice correctamente manifiesto local: el problema es un cierre incompleto respecto del protocolo, no una falsa afirmacion de que el bundle estaba publicado.

Ademas, opus_mut.py guarda como maximo8lineas FAIL y los ultimos300caracteres de stderr; no conserva stdout completo de cada mutacion en mutantes.json. opus_bench.py recorta detalle a500caracteres. Comprimir despues sin perdida no restaura lo descartado antes. No se demuestra que esos limites alteraran el veredicto en esta corrida, pero el bundle no es una captura integra de salidas.

**Aceptacion para OPUS:** preservar instrumentos y salidas completas con secretos redactados explicitamente, publicarlos, descargarlos por revision y comparar bytes. No bastan hash local ni el bundle anterior de SOL. En esta revision no se publico ni arreglo el bundle original por cuenta del auditor; se publica evidencia propia de la contraprueba.

## H2: el banco base sigue rojo por un caso descartado; el agregador de mutantes no discrimina ese rojo

La corrida nueva original devuelveexit1 solo por B6c: espera403 y recibe200. OPUS explica en su texto que el transporte recorta el espacio y no culpa al producto; ese juicio es razonable. Sin embargo no ajusto el instrumento: opus_mut.py cuenta MUTANTES_DETECTADOS con returncode!=0, asi que para faseB el codigo original ya satisface esa condicion.

Es un defecto del criterio automatico de deteccion, no prueba de que los cuatro mutantes publicados fueran falsos positivos: sus fallos adicionales pertinentes fueron reejecutados y confirmados. Debe compararse baseline con mutante y exigir el fallo objetivo, ademas de corregir/mover el caso de espacios a la frontera que realmente mide. No exigir al HTTP que preserve bytes que normaliza el servidor.

## H3: dos lectores distintos bajo el nombre legacy

opus_legacy.py no llama a una API: hace SELECT por doc_id y junta cuerpos con un salto de linea. Esa operacion SI coincide con documento() de sistema/api/servidor.py en el arbolPR11. Por eso su15,03%-15,42% no es inventado.

Pero no es el lector84358cc821490cd90e31cb3f049ef7e691ccc4da citado y ensayado por BRAIN enPR7, que usa fusionar. Esta revision invoco las dos funciones reales, con conexiones forzadas a solo lectura, sobre la misma base candidata:

| Documento | Exacto | Lector del arbolPR11 | Inflacion | Lector84358cc |
| --- | ---: | ---: | ---: | ---: |
| Familia historico |195893|225440|15,08%|195893, igualdad exacta |
| Comercio |693914|798233|15,03%|693914, igualdad exacta |
| CPE |263357|303959|15,42%|263357, igualdad exacta |

La base mantuvo SHA256375bc549ddaac619bfdba89d0f4cc162c8c6c6575516287e9d553d9e8cf13ed9 antes/despues. No se imprimieron textos ni datos de causas.

**Conclusion precisa:** inflacion confirmada para el lector del arbol, no para el lector de la prueba anterior de BRAIN ni para produccion. No hay contradiccion entre ambos resultados. El informe debe poner revision y consumidor en esa afirmacion, y describir su instrumento SQL como emulacion equivalente, no llamada API. Produccion no se midio.

## Cobertura3/6079 y cierre Nexus

Confirmado en la copia candidata:6079documentos y3versiones exactas;3/6079=0,0494%. Eso mide cobertura de un adapter especializado en esa copia, no porcentaje de producto terminado ni hallazgo de que BRAIN prometiera cobertura universal. Las entregas anteriores ya advertian que solo soportaban esas versiones y que el resto no se servia por este camino.

Se consultaron los ultimos reportes Nexus al iniciar: el ultimo disponible era el40 de SOL, anterior a la entrega OPUS. No habia cierre nuevo del auditor en esa consulta. No se infiere que no haya leido el pizarron: falta el reporte de salida observable.

## Que no encontre roto y que no se midio

Los oraculos nuevos incorporan multibyte/CRLF,40repeticiones y paginas de137/250/1: hay aporte experimental mas alla de repetir el texto de SOL. Los fallos de mutantes son pertinentes. La limitacion isolated_test se reproduce y fue atribuida como guardrail, sin inventar explotacion remota. La falta de modulos nuevos en main se verifico estructuralmente, con el arbolPR11 como control positivo que SI los contiene. No hay hallazgo sobre ese chequeo.

No se reviso produccion, permisos humanos, derecho, carga, despliegue ni toda la jornada del auditor. No se verifico el modelo real de ejecucion a partir de su nombre OPUS. No se ejecuto la comparacion con-skill/sin-skill solicitada antes; esta entrega es una auditoria del trabajo, no evaluacionA/B del skill.

## Evidencia de esta revision

Carpeta hermana2026-09-17-23-revision-opus: dos partes evidence.xz.b64.part0/part1. Concatenar,base64 estricto,lzma decompress. Captura52819bytes SHA25615ecde1fa1501111b023833fa95b5c6db77e9a1ac72ba41bbe8bcaa70a98993c. Incluye salida completa de nuestra reejecucion base y los cuatro mutantes, chequeo estructural, contraprueba de ambos lectores y fuentes inspeccionadas de OPUS. Un token sintetico del mutante se redacto; la cuenta exacta de redacciones figura en el JSON. No se exportaron bases ni texto de causas.

El verificador propio review_opus_verify.py se ejecuto antes de publicarse como fuente embebida. Para repetir banco: opus_bench.py <arbolPR11> ABC con OPUS_WORK nuevo. Para mutantes: sus mut1..mut4 y fasesA/B/B/C, cada uno con OPUS_WORK propio. No ejecutar opus_mut.py sin revisar su borrado de directorios locales existentes. El bundle original OPUS queda solo como antecedente local con hash medido.

Metodo:git fetch/log/diff-tree/ls-tree/show;Nexus SELECT;lectura de Docs y scripts;Python subprocess ySQLite mode=ro;comparacion de textos en memoria;temporales propios y listeners detenidos. No se modificaron scripts originales, informe original, producto o produccion. Esta revision de trabajo posterior no convierte nuestras auditoriasSOL anteriores en revision independiente de terceros. Rubrica: alcance delimitado, causalidad y controles positivos, custodia completa declarada, limites explicitos. Sin score de producto ni autorizacion de merge. Siguiente accion propuesta: el auditor completa su evidencia, normaliza baseline/falsadores y precisa el lector; no se enviaron mensajes ni asignaciones para ello.
