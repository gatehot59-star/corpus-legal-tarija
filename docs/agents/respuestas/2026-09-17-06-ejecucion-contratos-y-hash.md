# Corpus v2: primer incremento ejecutable, no cierre de todo el plan

Pedido: realizar todos los pasos, con autorización por etapas y GitHub del workspace ya confirmada. Rama titan/corpus-v2-stage1, PR https://github.com/gatehot59-star/corpus-legal-tarija/pull/2. Doc https://app.clickup.com/90171457413/docs/2kza6fw5-12577.

## Ejecutado
B01/I05: contracts/provenance_v2.py materializa identidades, fechas tipadas, autoridad independiente de OCR/HTML, hashes de original/texto y manifiesto determinista. Es prototipo aislado, no contrato público desplegado. No migra UID legacy. Persistencia, referencia a revisores reales e invalidación de cachés siguen pendientes.
B03: sistema/api/fuente_nacional.py recupera el lector del PR1 y valida hash completo sobre bytes de texto; rechaza errores de hash, UTF8, archivos vacíos, escape de rutas y symlinks. Manifiesto roto produce error en vez de perder registros silenciosamente. PR1 no modificado. No corrige producción hasta integración y despliegue autorizados.

A02 adicional: copias /workspace/deploy/rag-abogacia-v7.db y /workspace/snapshots/vm-corpus-20260904-1845/rag-abogacia-v7.db tienen6079documentos,78930pasajes e igual SHA256 del conjunto ordenado de UID que la VM:31481e481177eb6d487492f7f30b7f8e1c21843f092054bf5288e298e2c542d0. No prueba igualdad campo a campo ni restore. Reconstrucción de corpus por rama pendiente.
A04: guion de consentimiento/tareas preparado, no entrevistas ni participantes obtenidos.

## Medición sobre archivos publicados
Candidato1bc07a4332d5bf7da31fe0904ec7945309169b0e, extraído con git archive en temporal de brain-env. Test de contratos23/23, banco nacional11/11, tres mutantes compilables rechazados. Banco nacional contra lector histórico2360f27d43fdc9a1e2a74a3f6465698918df2ad1:13fallos de aserción y1error en11tests (incluye subtests), exit1. El positivo válido pasa en ambas versiones.

Extractos verbatim, NO logs íntegros:
```
new ['python3', 'tests/test_fuente_nacional_integridad.py'] 0
Ran 11 tests in 0.013s
OK
new ['python3', 'tests/test_provenance_v2.py'] 0
Ran 23 tests in 0.006s
OK
new ['python3', 'tests/check_provenance_mutations.py'] 0
old ['python3', 'tests/test_fuente_nacional_integridad.py'] 1
Ran 11 tests in 0.018s
FAILED (failures=13, errors=1)
```
El nuevo banco usa sólo fixtures temporales para el escape de rutas. Una ejecución anterior leyó /etc/passwd del taller con el lector viejo: corregí el instrumento y repetí; su contenido NO se publica. Primera materialización de contratos tuvo marcadores + de transporte: se corrigió antes de publicar y se corrió desde git archive, no desde el archivo defectuoso.

Logs completos del contraste conservados en /workspace/corpus-v2-b03-results/results.json; mutaciones anteriores en /workspace/corpus-v2-exec-1a5c40/mutations.json. Los extractos de este recibo no sustituyen esos logs. Comandos y fixtures están versionados para repetir el veredicto.

CI: https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35183386834/job/105080181387, contracts completed/success. Revisión automática solicitada; get_reviews devolvió[]: no aprobación emitida.

## Pendientes sin falsas firmas
A01 inventario identificado, no restore probado. A02 parcial en reconstrucción por ramas. B01/I05/B03 comprobados como unidades aisladas, no aceptados como producto integrado. B02/B04/B06/B07 y otros técnicos siguen pendientes. A03/I01/I02/I03 requieren revisión jurídica real. A05/I04/M04/G requieren personas, consentimiento y observaciones. A08/A09/I09/I10 requieren decisiones con alcance/presupuesto: no se fabricaron. H07 no existe antes del período real de renovación. No declarar las110ocurrencias cerradas por34tests.

## Seguridad y QA
Sin cambios en producción, credenciales, base, main ni otros árboles. Sin despliegue ni merge. SHA no certifica derecho ni OCR. require_url valida sintaxis, no SSRF. UUID de revisión no certifica existencia ni autorización de un revisor. Directorio de ingesta presupone inmutabilidad: no se afirma defensa contra atacante local concurrente.
QA integral NO APROBADO: faltan integración, cobertura formal, rendimiento, review externa y pruebas del producto. El CI prueba este bloque aislado. No porcentaje de avance artificial.
