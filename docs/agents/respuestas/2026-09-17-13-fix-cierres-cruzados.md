# Fix crossed closing tags and rerun real sources

Pedido ejecutado en PR6, sin merge ni deploy. Código76d9544b4da6207e1af8fbd61b3a81ccdc3b4b37. Doc https://app.clickup.com/90171457413/docs/2kza6fw5-12777.

## Cambio
handle_endtag fuera del cuerpo sólo acepta cierre del ancestro superior. Cierre cruzado, sin apertura o de elemento void: ExtractionError. No borra ancestros intermedios. Conserva selección original del cuerpo y formato de salida.

## Pruebas
SOL exact6cases: visible acepta,hidden_balanced rechaza,cross_table rechaza,cross_template rechaza,closed_hidden_sibling acepta,cross_object rechaza. Los3bypasses antes aceptados ahora fallan. SHA256 módulo a833b2f8bb6d77eb3a1b62ea52fccac95e8298d22d4b389c616605721cbdc418 coincide en pruebas y archivo publicado.
29testsHTML anteriores+4nuevos pasan. Mismo banco nuevo contra lector452a756:5fallos de aserción (incluye3subtests),exit1. Además20lector,23contratos,11ingesta:87tests locales, y3runners de mutación exitosos. CI remoto prueba33HTML ymutantesHTML, no se le atribuyen87tests.
CI preservation success: https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35249847865/job/105299219468,16:58:28Z a16:58:33Z. Copilot solicitado; no aprobación inferida.

## Fuentes reales reejecutadas
Descargas nuevas Family/Commerce/CPE. Mismos bytes de cada fuente contra viejo y nuevo: diccionario de resultado COMPLETO idéntico, no sólo largo o hash del texto. BeautifulSoup confirma flujo no blanco. Familia195893caracteres/496párrafos,Comercio693914/1697,CPE263357/435. No certificación de artículos ni vigencia.
https://www.lexivox.org/norms/BO-COD-DL10426.xhtml
https://www.lexivox.org/norms/BO-COD-DL14379.xhtml
https://www.lexivox.org/norms/BO-CPE-20090207.xhtml

## Límites
Rechazo conservador de cierres externos malformados, incluso después del cuerpo; no HTML5 completo ni CSS ni garantía de todas las plantillas. HTML resultante sigue no sanitizado. No cambios en corpus,manifiestos,UIDs,credenciales o servicio. No se mergeó PR6 ni la cadena pendiente.

## Evidencia
Companion docs/agents/evidencia/2026-09-17-13-crossed-tags.json: JSON lossless zlib+base64. Decodificar base64 y zlib.decompress, verificar SHA256.8926bytes: logs íntegros de4tests nuevos/viejo,6inputs deSOL/resultados,fuentes reales y resumen deotrosrunners. No se presenta el resumen como log íntegro de87tests.
Comandos: python3 tests/test_legal_html.py; python3 tests/test_legal_html_crossed.py; python3 tests/check_legal_html_mutations.py. La comparación old/new se hizo en copias temporales y restauró el archivo publicado al finalizar.
