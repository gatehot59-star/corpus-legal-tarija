# Corpus legal del Departamento de Tarija, Bolivia

Pipeline reproducible de descarga, OCR y verificacion sobre **fuentes oficiales del Estado**
boliviano, para busqueda documental en un estudio juridico.

## Lo que hay medido (2026-09-03)

| | |
|---|---|
| documentos descargados | **1.031** (1.521,8 MB, 1.031 md5 unicos) |
| con texto nativo | 247 documentos, 1.822 paginas |
| escaneados, requieren OCR | **784 documentos, 2.624 paginas** |
| distribucion de los escaneados | mediana 1 pagina, p90 4, max 58 |
| velocidad de OCR medida | **11,1 s/pagina** en Actions x64 (4 vCPU EPYC) |
| costo total del OCR | 8,1 h de CPU en serie, **~25 min de reloj en 20 shards** |
| calidad medida sobre la Ley 007 | CER 6,2% · WER 9,3% · F1 de bolsa 0,947 · **38/40 datos juridicos** |

## Tres reglas que no se negocian

**1. No se commitea un solo PDF.** Cada corrida re-descarga de la fuente oficial y verifica
el `sha256` registrado en `indices/manifest.jsonl`. Si el hash no coincide, el documento se
marca `HASH_DISTINTO` y **no** se procesa: un PDF que cambio en el servidor del Estado es
una noticia, no un archivo a procesar en silencio.

**2. El texto crudo del OCR es la fuente y nunca se reescribe.** Tesseract lee `Art. 17.I`
como `Art. 17.1` porque el romano I y el digito 1 son homoglifos. Corregirlo por inferencia
fabricaria una norma que no existe. Entonces: el cuerpo queda verbatim, las citas ambiguas
se anotan aparte con linea y contexto, y el **indice de busqueda recibe las dos formas**, asi
buscar `Art. 17.I` encuentra el documento sin haber alterado la ley. Medido sobre la Ley 007:
el crudo da 38/40 datos juridicos y el indice 40/40, con el cuerpo intacto.

**3. Nada privado entra aca.** El manifiesto marca cada documento como `PUBLICO` o `PRIVADO`
y la primera linea del procesamiento descarta lo que no es publico, antes de tocar la red.
Este repo solo contiene normativa del Estado; los documentos del estudio viven aparte.

## Estructura

```
indices/manifest.jsonl   el indice: 1 documento por linea, con sha256, fuente_url y estado por etapa
pipeline/ocr_masivo.py   OCR shardeado: baja, verifica hash, rasteriza, OCR, gate de calidad
pipeline/normalizar_citas.py  extractor de citas legales que NO toca el cuerpo
pipeline/test_citas.py   tests del normalizador, incluidos los casos adversos
pipeline/consolidar.py   junta los shards y produce el veredicto agregado
corpus/                  el texto resultante, mas la cola de revision humana
```

## Tres estados, no dos

Cada documento termina en **OK**, en **REVISION_HUMANA** (el gate de calidad no paso, o hay
una cita ambigua) o en un estado declarado de por que no se pudo: `HASH_DISTINTO`,
`PDF_ILEGIBLE`, `DESCARGA_FALLIDA`, `DEMASIADAS_PAGINAS`, `OMITIDO_PRIVADO`. Un OCR que
nadie midio no entra al corpus como si estuviera bien.

## Fuente

Gaceta Oficial del Gobierno Autonomo Departamental de Tarija (`tarija.gob.bo`): leyes
departamentales y resoluciones de la Asamblea Legislativa Departamental.
