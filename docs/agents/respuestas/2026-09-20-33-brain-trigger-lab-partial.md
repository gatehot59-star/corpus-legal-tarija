# Laboratorio documental: cuatro eventos ejecutados, veredicto INCOMPLETO

BRAIN, 20-sep-2026 ART. No se apagó ni encendió Actions. Este archivo NO declara completado el experimento ni autoriza el merge condicional de PR21.

## Ejecución real

Se completaron los 21 archivos originales aprobados y el README vacío autorizado. El cotejo de los 21 SHA256 dio igualdad; el árbol tiene 22 archivos modo 100644 y siete ramas, incluida main vacía salvo README. Base vieja congelada c82c684f71a235960504cf46092053c653fd7f48. Base nueva fdf2519ecb12fcb3e1fcb7eedc1151c23d0d04cc. La única diferencia entre bases es la eliminación de las 24 líneas de pull_request.paths, workflow nuevo byte-idéntico al de PR21. Hashes YAML: viejo 005b9214aa1695edb4fdfb1675cbba813fbe6ce921d3d4f06ae0b0c83687e4df; nuevo c69a9f1a21a348bd400fff15165fc55e7e8e7c94fdee1a4a6b7e604d47d0ce72.

Los cuatro diffs acumulados locales y las cuatro listas de archivos REST contienen solamente su probe. Los controles de código agregan el comentario autorizado y conservan el AST. No se importaron los seis workflows excluidos. Baseline REST: cero runs.

Se abrieron los cuatro PRs no draft el 21-sep 00:35:28 UTC (20-sep 21:35:28 ART):

- [NEW-CODE, PR1](https://github.com/gatehot59-star/corpus-docs-trigger-lab/pull/1), head 531e500ae8b073003d73f7020fd6cfd50e7dde29: run35548189544, job106177854186, success, 00:35:36..00:36:19 UTC.
- [OLD-DOCS, PR2](https://github.com/gatehot59-star/corpus-docs-trigger-lab/pull/2), head85635ef92e8a0a72937ca55e5b507b6ceed62103: cero checks en la consulta autenticada. No se firma todavía la ausencia durante la ventana completa.
- [NEW-DOCS, PR3](https://github.com/gatehot59-star/corpus-docs-trigger-lab/pull/3), headf39c3e93ef1bdcdcf4630fae56a6f7cd60695cee: run35548190401, job106177856329, success, 00:35:37..00:36:19 UTC.
- [OLD-CODE, PR4](https://github.com/gatehot59-star/corpus-docs-trigger-lab/pull/4), head48eb96eff0219414ccaf1eb9b45d959ab7cf36f7: run35548189753, job106177854805, success, 00:35:36..00:36:13 UTC.

Los tres jobs se leyeron también por sus endpoints públicos: siete pasos completed/success cada uno, incluidos los tres bloques de compilación/tests. El recibo adjunto conserva íntegros los resultados del conector de checks; no atribuye a esos resultados un conteo de tests que no contienen.

## Qué falta y por qué no hay merge

Se consumieron CUATRO de los SEIS episodios autorizados. NO se hicieron los dos synchronize documentales. NO se cerró con una consulta final registrada la primera ventana de cinco minutos. Por eso el veredicto del protocolo completo es INCOMPLETO, aunque los tres brazos positivos efectivamente corrieron y terminaron correctamente.

El observador externo pasó 26 controles, incluidos SHA/evento/PR equivocados, páginas faltantes, HTTP error, duplicados, ejecución fallida, skipped y ausencia prematura. Tomó cuatro muestras REST iniciales sin errores. Se detuvo expresamente al quedar una consulta en la cuota pública; el endpoint rate_limit preliminar había mostrado 60, pero las cabeceras reales del recurso mostraron el presupuesto compartido casi agotado. Se continuó leyendo checks mediante el conector autenticado y jobs mediante lectura web pública. NO se cumplió la cadencia de 15 segundos durante toda la ventana. Esta desviación no se oculta ni se convierte en aprobación.

No hubo un error del producto. No se cambiaron permisos ni se extrajeron credenciales. No se reejecutó ningún job. La falta de continuidad del observador no se presenta como fallo del workflow.

## Custodia y recuperación

Recibo publicado: docs/agents/respuestas/2026-09-20-33-lab-checks-raw.json. Es la respuesta completa de cada una de las cuatro consultas autenticadas de checks, sin campos sintetizados dentro de las respuestas.

Existe además un paquete local con 19 archivos, fuentes del observador y del runner local, manifest, preflight, episodios, cabeceras y cuerpos REST completos, checks, tres jobs completos y ejecución local de integración. Decodificado: 461371 bytes, SHA256 46e4a729db67a34e761d20601346a0758fddc8f4a419b66285005d68015e3f47. Su base64 zlib ocupa 41628 bytes. NO está publicado completo en git: no confundir el hash local con custodia W-01 completa.

Directorio de recuperación para el próximo ejecutor: /workspace/brain-trigger-experiment. Paquete partial-evidence.zlib.b64; observer.py, episodes.json, preflight.json, old-base-readback.json, http.jsonl, observation.json. El archivo stop está presente y el observador está detenido intencionalmente. No relanzarlo ciegamente ni consumir más eventos antes de recuperar la lectura.

La integración local de main f150c50b7fd224d598fc0e85ea2e684b9ecc4912 con el head autorizado produjo árbol0898d3432b547f0356dded07edbe8b3f010aa4fb sin conflicto y solo los dos archivos esperados. Los tres bloques heredados terminaron exit0 según el recibo local; su salida completa permanece en el paquete local, por lo que aquí no se firma una custodia publicada de esos tests.

## Estado de Corpus y autorización

PR21 sigue sin merge por BRAIN, head autorizado3b92dc432f285c00d5a45e717883c5c6e3fe46f9. Última consulta: open, reviews[], un check success106134315051. mergeable_state unknown en esa lectura: no convertirlo en clean. La autorización condicional sigue vigente, pero este cierre incompleto NO satisface su condición experimental.

PR1/17/18/19/20 de Corpus no se tocaron. Hold17/18/19 e independencia de review18 conservados. Ningún despliegue, cleanup o eliminación. Las aprobaciones previas de 21 archivos, README/main y seis episodios no necesitan repetirse.

Siguiente acción concreta: cerrar la primera observación por una vía disponible y preservar la respuesta, luego emitir exactamente los dos synchronize documentales aprobados, observarlos al menos cinco minutos y publicar toda la evidencia. Solo después reevaluar PR21 y, si se cumplen las condiciones, mergear exclusivamente ese PR con expectedHeadSha. No repetir los cuatro opened ni crear más PRs.

## Errores propios y método

El primer transporte comprimido del observador falló al descomprimir; no ejecutó código. La copia literal posterior corrió sus 26 controles. La primera ruta relativa de apply_patch no fue admitida; la ruta absoluta del sandbox sí. Los footers de preparación no son una rúbrica final ni una revisión independiente.

--- METODO TITAN ---
Accion delicada: experimento de runtime previamente autorizado; este commit es documental.
Modo aplicado: TITAN FULL.
Rubrica: INCOMPLETO, no se emite score aprobatorio de experimento ni merge.
N/A declarados: deployment y producto nuevo fuera de alcance.
Review externo: sin nueva aprobación formal; no solicitado en este turno.
Instrumento: Git diff/hash/AST, observador adverso, GitHub check runs y jobs. Recibo de checks publicado; custodia integral pendiente.
