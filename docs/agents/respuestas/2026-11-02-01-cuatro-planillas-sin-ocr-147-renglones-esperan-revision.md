# 2026-11-02-01 · Las otras cuatro páginas del banco ya tienen planilla de revisión humana sin OCR: 147 renglones esperan la revisión de Abraham

**Estado:** planillas entregadas, revisión humana pendiente. Ninguna de estas cuatro páginas tiene gold humano todavía.

## 1. Pedido

«Review the other four held-out pages», después de proponer repetir la planilla con las otras cuatro páginas del banco. Interpretación: hacer para Ley 524 p. 2 y Ley 523 pp. 1 a 3 lo mismo que se hizo para Ley 524 p. 1. Una planilla por página, con el escaneo oficial por franjas y debajo la referencia IA renglón por renglón, sin mostrar ningún OCR, para que Abraham la valide y cada página se congele como gold humano. Este turno entrega las planillas; la revisión es de Abraham. No se corrió ni se midió ningún OCR.

## 2. Herramientas y máquina

- **Sandbox de ClickUp, sin red.** poppler 22.12.0 (`pdftoppm`, `pdftotext`, `pdfinfo`), Pillow 12.2.0, WeasyPrint 69.0, fuentes DejaVu de matplotlib. `build4.py` generó los cuatro PDF y `manifest4.json`, `qa4.py` corrió el QA y `leak_positive.py` el control positivo del chequeo de fugas. Entradas verificadas por SHA-256 dentro de `build4.py`: PDF oficial de la Ley 524 (`29085b96…`), PDF oficial de la Ley 523 (`dd85855e…`) y `gold-ai-v1.json` (`36097a8d…`, `human_review=false`). En el sandbox no hay ninguna salida OCR: `find / -xdev -name '*-raw.json'` cuenta 0.
- **brain-env (taller).** `check_cuts.py` leyó solo cajas y etiquetas de diseño de las salidas GPU del 16-oct, nunca su texto, para verificar los cortes. Escribió en `/workspace/ocr-gold-humano-4p-20261102/`.
- **GitHub MCP** para este commit, directo a `main` porque es evidencia append-only. **ClickUp** para el Doc espejo con los cuatro PDF.
- No se tocó la VM de Corpus, sus servicios ni PR33. No hubo OCR, GPU, API externa ni Kaggle. Cuota gastada: ninguna.

## 3. Qué se midió

| Planilla | Página del banco | Renglones | Franjas | Hojas | Presentes con su ID | Mutantes de un carácter rechazados | IDs cruzados rechazados | Tokens solo-OCR buscados / hallados | Píxeles iguales al banco |
|---|---|---|---|---|---|---|---|---|---|
| A | Ley 524 p. 2 (`h01-p002`) | 25 (A01 a A25) | 11 | 7 | 25/25 | 25/25 | 25/25 | 5 / 0 | sí |
| B | Ley 523 p. 1 (`h02-p001`) | 47 (B01 a B47) | 7 | 7 | 47/47 | 47/47 | 47/47 | 3 / 0 | sí |
| C | Ley 523 p. 2 (`h02-p002`) | 52 (C01 a C52) | 7 | 7 | 52/52 | 52/52 | 52/52 | 2 / 0 | sí |
| D | Ley 523 p. 3 (`h02-p003`) | 23 (D01 a D23) | 11 | 7 | 23/23 | 23/23 | 23/23 | 4 / 0 | sí |
| **Total** | | **147** | **36** | **28** | **147/147** | **147/147** | **147/147** | **14 / 0** | **4/4** |

**Cortes**, con `check_cuts.py`: 32 cortes internos. Ninguno cruza una caja de diseño, ni en `parsing_res_list` ni en `layout_det_res`. Los 32 caen en el punto medio del blanco entre cajas, con desvío 0 o -0,5 px (el punto medio truncado). Las 36 franjas tienen al menos una caja. Los 4 controles negativos, un corte puesto en el centro de la caja más alta de cada página, dan 1 cruce cada uno.

**¿Podía cada instrumento dar rojo?**

| Afirmación | Instrumento | ¿Podía dar rojo? | Veredicto |
|---|---|---|---|
| Cada renglón de la referencia está en su planilla, con su ID | `qa4.py`: `pdftotext -raw` y búsqueda de «ID + texto» | Sí: los 147 mutantes de un carácter y los 147 IDs cruzados dan ausentes | medido, bien |
| La planilla no muestra texto OCR | (a) estructural: `build4.py` no abre ningún archivo OCR y en el sandbox no hay ninguno; (b) búsqueda de los 14 tokens que solo aparecen en el OCR | (b) sí: `leak_positive.py` renderiza esos 14 tokens con el CSS de las planillas y los encuentra 14/14 en párrafo, en renglón y en grilla | medido, bien. (b) cubre solo esos 14 tokens; la garantía general es (a) |
| Los cortes caen en blanco y en el punto medio | `check_cuts.py` sobre las cajas del 16-oct | Sí: 4/4 controles negativos | medido, bien. Mide cajas, no tinta |
| Cada renglón está en la franja que le corresponde | inspección visual de las hojas de contacto, por el mismo operador | No: no es un instrumento reproducible | NO MEDIDO como instrumento. La planilla pide revisar la página completa al final |
| La portada entra en una hoja | `pdftotext` hoja por hoja | Sí: en el primer build la hoja 2 de B y C empezaba con «Tiempo estimado» | medido, bien: la hoja 2 de las cuatro empieza con «Página completa» |

**Observación de `check_cuts.py`.** En tres cortes el blanco entre cajas es angosto: A en 1289 (7 px), C en 626 (20 px) y D en 625 (17 px). Con el margen de 20 px de cada franja, ahí se ve el borde del bloque vecino. Es contexto visual y no cambia qué renglones van en cada franja.

**Primer build, declarado.** Las portadas de B y C se desbordaban y la hoja 2 quedaba con una sola línea. Se corrigió solo la presentación: márgenes de los títulos (5 a 3,6 mm arriba, 2 a 1,6 mm abajo) y el tiempo estimado debajo del subtítulo. También se corrigió una frase de la portada: decía que de la corrida anterior «solo se usó la ubicación de los bloques», cuando la asignación de renglones a franjas también alineó su texto con la referencia; ahora dice que la corrida «se usó solo para ubicar». Hashes del primer build, no publicado: `build4.py` `97391dbb…`, `manifest4.json` `944021bb…`, PDF A `31a62032…`, B `33efb373…`, C `2d7ed22a…`, D `ee41b631…`. Su QA había dado los mismos números.

## 4. Evidencia cruda

`python3 build4.py`, exit 0:

```
BUILD_OK h01-p002 revision-humana-ley-524-p2.pdf pixel_identical True bands 11 lines 25
BUILD_OK h02-p001 revision-humana-ley-523-p1.pdf pixel_identical True bands 7 lines 47
BUILD_OK h02-p002 revision-humana-ley-523-p2.pdf pixel_identical True bands 7 lines 52
BUILD_OK h02-p003 revision-humana-ley-523-p3.pdf pixel_identical True bands 11 lines 23
```

`python3 qa4.py leak-tokens.json`, exit 0:

```
QA h01-p002 {"pdf_pages": 7, "lines_present_with_id": 25, "lines_total": 25, "mutant_controls_rejected": 25, "wrong_id_controls_rejected": 25, "ocr_only_tokens_checked": 5, "ocr_only_tokens_found": 0, "failing_rows": []}
QA h02-p001 {"pdf_pages": 7, "lines_present_with_id": 47, "lines_total": 47, "mutant_controls_rejected": 47, "wrong_id_controls_rejected": 47, "ocr_only_tokens_checked": 3, "ocr_only_tokens_found": 0, "failing_rows": []}
QA h02-p002 {"pdf_pages": 7, "lines_present_with_id": 52, "lines_total": 52, "mutant_controls_rejected": 52, "wrong_id_controls_rejected": 52, "ocr_only_tokens_checked": 2, "ocr_only_tokens_found": 0, "failing_rows": []}
QA h02-p003 {"pdf_pages": 7, "lines_present_with_id": 23, "lines_total": 23, "mutant_controls_rejected": 23, "wrong_id_controls_rejected": 23, "ocr_only_tokens_checked": 4, "ocr_only_tokens_found": 0, "failing_rows": []}
ALL_OK True
```

Portada y hoja 2, con `pdfinfo` y `pdftotext -f N -l N -raw`:

```
revision-humana-ley-524-p2.pdf sheets=7 | fin hoja1: • Ley Departamental N° 524, página 2 · planilla A de revisión humana · hoja 1 de 7  | inicio hoja2: Página completa
revision-humana-ley-523-p1.pdf sheets=7 | fin hoja1: • Ley Departamental N° 523, página 1 · planilla B de revisión humana · hoja 1 de 7  | inicio hoja2: Página completa
revision-humana-ley-523-p2.pdf sheets=7 | fin hoja1: • Ley Departamental N° 523, página 2 · planilla C de revisión humana · hoja 1 de 7  | inicio hoja2: Página completa
revision-humana-ley-523-p3.pdf sheets=7 | fin hoja1: • Ley Departamental N° 523, página 3 · planilla D de revisión humana · hoja 1 de 7  | inicio hoja2: Página completa
```

`python3 leak_positive.py`, exit 0:

```
LEAK_POSITIVE_CONTROL parrafo found 14 of 14
LEAK_POSITIVE_CONTROL renglon found 14 of 14
LEAK_POSITIVE_CONTROL tabla found 14 of 14
```

Salidas OCR presentes en el sandbox, y archivos que abre `build4.py`:

```
RAW_JSON_EN_SANDBOX=0
7:    with open(p, 'rb') as f: return sha_bytes(f.read())
72:ref = json.load(open('ref.json', encoding='utf-8'))
148:    im = Image.open(stem + '.png')
226:json.dump(manifest, open('manifest4.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
```

Los 14 tokens buscados en los archivos que se publican, antes de publicar:

```
build4.py tokens_found 0 of 14
qa4.py tokens_found 0 of 14
manifest4.json tokens_found 0 of 14
```

Este recibo y el Doc espejo se escanearon igual antes de publicar; el resultado está en el Doc.

`python3 check_cuts.py` en brain-env, exit 0, stdout `CUTS_OK True`, stderr vacío. Salida completa en `check-cuts-output.json`.

`sha256sum` en el sandbox:

```
8b124f2c0952d36bf85de650f131e2aed866a1ccdd749ce6a0fc9ff9c32e4a6e  build4.py
1d0cb27585e85080de846eab82c90033bb90bb44a477fd515afda6f91d7ef490  qa4.py
aac69395b992b6d608c20a1127747bf903a5467253743426da3c6c55184f2cf5  manifest4.json
e9c4bc3b6228d6ccf4e7ac9f8fcf74c87e128038c3acf6974e110ed5aecbbd48  revision-humana-ley-523-p1.pdf
3f681439f1396b4e2758379a9d415ba51f0ffbf754f119f00f2f4b0b279cefec  revision-humana-ley-523-p2.pdf
5c5c5ff6716720f62a4e84426debe1f04eee2c273577205389ff4082a8eda52c  revision-humana-ley-523-p3.pdf
026a75b7db2f064e7646eaaa568c5575684a605dd2e1b9a25cd58267081dd13c  revision-humana-ley-524-p2.pdf
```

## 5. Archivos generados

En este commit, bajo `docs/agents/evidencia/2026-11-02-01-planillas-revision-4-paginas/`:

| Archivo | Bytes | SHA-256 |
|---|---|---|
| `build4.py` | 19.164 | `8b124f2c0952d36bf85de650f131e2aed866a1ccdd749ce6a0fc9ff9c32e4a6e` |
| `qa4.py` | 2.963 | `1d0cb27585e85080de846eab82c90033bb90bb44a477fd515afda6f91d7ef490` |
| `manifest4.json` | 28.255 | `aac69395b992b6d608c20a1127747bf903a5467253743426da3c6c55184f2cf5` |
| `leak_positive.py` | 1.833 | `b7d050d929571506385524f5aa36c17eb2cf7cb25d0fcf295c6c41a30fe9ee0e` |
| `check_cuts.py` | 4.014 | `3f94b73014fa578f92c7534250e8134d7c6c47223de4d4e86b3aa3929dcaefe9` |
| `check-cuts-output.json` | 11.912 | `095784ab34c386ecc18d982dec85a5b7e1d492fa8070ea6471296bb20bdf004c` |

Fuera de Git, referenciados por hash:

| Archivo | Bytes | SHA-256 | Dónde |
|---|---|---|---|
| `revision-humana-ley-524-p2.pdf` (A) | 3.223.486 | `026a75b7…` | adjunto del Doc espejo |
| `revision-humana-ley-523-p1.pdf` (B) | 3.744.807 | `e9c4bc3b…` | adjunto del Doc espejo |
| `revision-humana-ley-523-p2.pdf` (C) | 4.233.377 | `3f681439…` | adjunto del Doc espejo |
| `revision-humana-ley-523-p3.pdf` (D) | 3.194.269 | `5c5c5ff6…` | adjunto del Doc espejo |
| `leak-tokens.json` | 257 | `c9e8b8f3f9e6dbfde7f57c9af258dc847647df30113f209538928025ed11d2cb` | retenido hasta cerrar las cuatro revisiones |

Los PNG de las franjas y el JPG de página completa son derivados: `build4.py` los regenera desde los PDF oficiales.

## 6. NO MEDIDO

- **La revisión humana.** Pendiente. Hasta que Abraham responda, estas cuatro páginas no tienen gold humano.
- **La exactitud de la referencia IA** en estas páginas.
- **Cualquier OCR contra gold humano** en estas páginas. Para ellas solo existe la salida GPU del 16-oct; no hay corrida CPU y no se lanza sin autorización.
- **Contaminación.** En este chat no se le mostró al revisor ninguna diferencia del OCR en estas páginas, pero el informe del 16-oct sobre la corrida GPU de las cinco páginas pudo haberlas mostrado.
- **Duración y exhaustividad** de la revisión, que no se registran.
- **La asignación de renglón a franja** como instrumento reproducible: solo hubo inspección visual del operador. El código que derivó los cortes corrió en línea en brain-env y no quedó en archivo; `check_cuts.py` verifica el resultado (cortes en blanco y en el punto medio), no reproduce la asignación.
- Reproducibilidad (tres corridas por página), otros documentos y certificación legal.

## Cómo sigue

1. Abraham responde por planilla: «A: sin cambios», o una línea por corrección, «A05: dice «…», debe decir «…»». Puede ir de a una página.
2. Cada respuesta se aplica a su renglón y la página se congela como `gold-human-v1` con `human_review=true`, revisor y fecha, igual que `h01-p001`.
3. Con las cuatro congeladas se publica `leak-tokens.json` y se mide la salida GPU del 16-oct contra el gold humano.

Doc espejo en ClickUp: «2-nov-2026 · Las otras cuatro páginas del banco ya tienen planilla de revisión humana…», público, en el Space del proyecto. Se crea después de este commit y el chat de este turno linkea los dos.

--- METODO TITAN / PROMETEO ---
Accion delicada: NO
Modo aplicado:   PROMETEO LIGERO
Maquina:         sandbox ClickUp (PDF, QA, control positivo) + brain-env (check_cuts.py, solo lectura de cajas)
Rubrica:         N/A (modo ligero)
N/A declarados:  rubrica completa (entrega chica: evidencia y planillas de revision)
Review externo:  no aplica a evidencia en main; el falsador pendiente es la revision humana
Instrumento:     build4.py y qa4.py (exit 0, ALL_OK True), leak_positive.py (exit 0, 14/14 en 3 contextos), check_cuts.py (exit 0, CUTS_OK True); salida cruda arriba y en check-cuts-output.json
Artefactos:      este archivo + Doc espejo en ClickUp (linkeado desde el chat)
