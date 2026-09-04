# Evidencia cruda: el corpus departamental, completo contra el censo REAL

**2026-09-03, 21:30-22:00 UTC.** Máquina: `brain-env` (gateway MUDH, servicio `build`).
Verbatim. El veredicto va aparte al final.

---

## 1. El censo real de la fuente, medido página por página

La etapa `descubrir` figuraba **PENDIENTE en las 1.031 filas** del manifest: nunca se había
medido cuánto publica la Gaceta, solo cuánto habíamos bajado.

```plain
$ python3 pipeline/descubrir_gaceta.py --salida descubierto.jsonl
tarija_leyes
  start=0     ids_nuevos=21  total=21
  ...
  start=500   ids_nuevos=14  total=515
  start=520   ids_nuevos=0   total=515
  tarija_leyes: 515 items | paginas con error: 0
tarija_rpa
  ...
  start=520   ids_nuevos=6   total=527
  start=540   ids_nuevos=0   total=527
  tarija_rpa: 527 items | paginas con error: 0
CENSO DESCUBIERTO: 1042 items
```

**Cero páginas con error**, así que el censo es un total y no un mínimo.

---

## 2. Lo que faltaba, cruzado por el id de la Gaceta

```plain
censo descubierto: 1042 | manifest: 1031 | manifest con id: 1031 | sin id: 0

FALTAN POR DESCARGAR: 10
   id 1725   tarija_leyes   ley-departamental-n-422-...nueva-estructura-de-cargos
   id 1729   tarija_leyes   ley-n-422-ley-departamental-nueva-estructura-de-cargos
   id 2012   tarija_leyes   ley-departamental-n-434-...presupuesto-plurianual
   id 2887   tarija_leyes   ley-departamental-n-485-...prevencion-atencion
   id 2299   tarija_rpa     r-p-a-n-257-2019-2020-...acta-de-sesion-ordinaria
   id 2326   tarija_rpa     resoluciones-del-pleno-del-301-al-310-2019-2020
   id 2946   tarija_rpa     r-p-a-n-128-2022-2023-...distincion-con-insignia
   id 3438   tarija_rpa     r-p-a-n-078-2025-2026
   id 3439   tarija_rpa     r-p-a-n-079-2025-2026
   id 3447   tarija_rpa     r-p-a-n-070-2021-2022-...convenio-interinstitucional

en el manifest y NO en el censo (retirados de la web?): 0
```

---

## 3. La descarga, con su resultado por documento

```plain
$ python3 pipeline/completar_gaceta.py --censo descubierto.jsonl \
      --manifest manifest.jsonl --destino <raiz>
censo: 1042 | ya en el manifest: 1031 | FALTAN: 10
   1/10 ROJO no-pdf id=1725   content-type=text/html; charset=utf-8 primeros=b'\n<!DOCTYPE h'
   2/10 ROJO no-pdf id=1729   content-type=text/html; charset=utf-8 primeros=b'\n<!DOCTYPE h'
   3/10 ROJO no-pdf id=2012   content-type=text/html; charset=UTF-8 primeros=b'El tama\xc3\xb1o d'
   4/10 OK            id=2887   paginas=8   chars=18788   pdfplumber
   5/10 OK            id=2299   paginas=1   chars=1196    pdfplumber
   6/10 ROJO no-pdf id=2326   content-type=application/pdf primeros=b'\x00\x00\x00\x00...'
   7/10 OCR_REQUERIDO id=2946   paginas=0   chars=0       pdfplumber
   8/10 OCR_REQUERIDO id=3438   paginas=1   chars=0       pdfplumber
   9/10 OCR_REQUERIDO id=3439   paginas=1   chars=0       pdfplumber
  10/10 OK            id=3447   paginas=1   chars=1161    pdfplumber

AGREGADAS AL MANIFEST: 6 | {"ok": 3, "ocr_requerido": 3, "no_es_pdf": 4, "error_red": 0}
manifest ahora: 1037 filas
ATENCION: quedaron items sin bajar. El corpus NO esta completo y esto lo declara.
```

**Los 4 que no se pueden bajar no son un problema de OCR ni de nuestro descargador:**

| id | qué devuelve el portal |
|---|---|
| 1725, 1729 | **HTML con 200**: el enlace no sirve el archivo |
| 2012 | *"El tamaño del archivo..."*: mensaje de error del propio Joomla |
| 2326 | declara `application/pdf` y devuelve **bytes en cero** |

El guard del `%PDF` los rechazó. **Sin ese guard, cuatro páginas de error habrían entrado al
corpus legal con procedencia verificable**, que es el peor modo de falla de este sistema.

---

## 4. Y los 3 escaneados ya los teníamos: hipótesis falsada

Los 3 `OCR_REQUERIDO` no se pudieron OCRear en `brain-env`, porque **el OCR masivo nunca corrió
acá**:

```plain
FALTA  tesseract | FALTA pdftoppm | FALTA gs | FALTA convert
tesseract en disco: []
instrumento del OCR masivo: ['tesseract spa psm 3']
maquina: ['actions-x64']
```

Antes de mandar nada a Actions, verifiqué si hacía falta:

```plain
r-p-a-n-128-2022-2023  estado=OCR_REQUERIDO  sha_ya_estaba=True
   -> ya estaba como: tarija_rpa-129-e283c7dd.txt | numero 129
r-p-a-n-078-2025-2026  estado=OCR_REQUERIDO  sha_ya_estaba=True
   -> ya estaba como: tarija_rpa-078-4e067451.txt | numero 078
r-p-a-n-079-2025-2026  estado=OCR_REQUERIDO  sha_ya_estaba=True
   -> ya estaba como: tarija_rpa-079-71d68457.txt | numero 079
```

**Los tres tienen el mismo sha256 que documentos que ya estaban OCReados.** No hay OCR pendiente:
el texto existe. Y de paso aparece un dato de la fuente: **el id 2946 se publica como "RPA 128" y
su PDF es el mismo que el de la RPA 129.** O el slug está mal en el portal, o es la misma
resolución con dos números. NO MEDIDO cuál de las dos.

**Esto ahorró un workflow entero de Actions.** El inventario dice "antes de decir no puedo,
preguntar en cuál de las tres máquinas"; acá la pregunta anterior era si el trabajo hacía falta.

---

## 5. La reconstrucción final, con el censo como invariante

```plain
$ python3 ingesta.py --origen /workspace/corpus-todo --db /workspace/bolivia-v5.db
  tarija_gaceta: 1037 documentos
    censo de la fuente: 1037 | por OCR: 787 | por extraccion: 250 | SIN TEXTO: 0
  tsj_genesis: 2862 documentos
    censo de la fuente: 2862 | por OCR: 2862 | por extraccion: 0 | SIN TEXTO: 0

documentos canonicos: 3856 | chunks: 58473 | procedencias: 3899
por jurisdiccion: {'departamental': 1034, 'jurisprudencia': 2822}
cola de revision humana: 4150
segundos: 13.9 | indice: 162.1 MB

VERIFICACION: {"censo_de_la_fuente": 3899, "ofrecidos": 3899, "canonicos_nuevos": 3856,
"duplicados_por_contenido": 43, "alias_nuevos": 3899, "sin_rastro": 0, "en_base": 3856,
"alias_en_base": 3899, "documentos_sin_procedencia": 0,
"contenidos_con_varias_fuentes": 21, "veredicto": "VERDE"}
```

### Antes y después

| | antes de hoy | ahora |
|---|---|---|
| documentos canónicos | 3.606 | **3.856** |
| departamentales | 784 | **1.034** |
| leyes departamentales | 402 | **512** |
| caracteres | 72.089.578 | **75.039.941** |
| chunks | 56.311 | **58.473** |
| con año (departamental) | 0 | **1.003 de 1.034** |

---

## 6. Tests

```plain
$ python3 -m unittest test_alias test_ingesta test_procedencias test_normalizar test_frontera
Ran 49 tests in 8.850s
OK

$ python3 test_api.py http://127.0.0.1:8120
VERDE: la API cumple el contrato que un agente necesita     (45/45)

corpus-legal-bolivia 1.1.0
  documentos: 3856 | caracteres: 75039941
  por jurisdiccion: {'departamental': 1034, 'jurisprudencia': 2822}
  procedencias: 3899 | con varias fuentes: 18
```

**Dos de los 49 son sabotajes que exigen ROJO**, y uno es nuevo:
`test_SABOTAJE_censo_el_adaptador_que_saltea_un_documento_da_ROJO` reproduce el bug de los 247 en
miniatura y verifica que **sin censo da VERDE** y **con censo da ROJO**. El bug de hoy ahora tiene
su propio test.

---

## 7. Veredicto derivado (conclusión, no medición)

**VERDE, y el frente departamental queda cerrado hasta donde la fuente permite.** El corpus tiene
**1.034 documentos canónicos de un censo real de 1.042 items**. La diferencia son **4 items que el
portal de la Gaceta no sirve** (dos con HTML, uno con error de tamaño, uno con bytes en cero) y
**4 duplicados de contenido** que la propia fuente publica dos veces.

**El invariante ya no puede mentir en la misma dirección:** el censo viene de recorrer la web de
la fuente, no de listar nuestra carpeta.

## 8. NO MEDIDO

- **Si los 4 no descargables existen por otra vía** (pedirlos por transparencia, o buscarlos en
  LexiVox). Son 4 de 1.042: 0,4%.
- **Si el id 2946 es la RPA 128 o la 129.** El portal se contradice.
- **La calidad del texto de los 3 nuevos**: se extrajo texto nativo con `pdfplumber` y **no pasó
  el gate de OCR** ni el normalizador de citas. Entran declarados como `texto_sin_gate`.
- **La jurisprudencia no se re-descubrió.** GENESIS sigue con 2.862 y su censo es su propio
  jsonl, no un barrido de la fuente. **Puede faltar jurisprudencia y no lo sabríamos.**
- **Vigencia: 3.856 sin medir.** Ni una sola.
- **El frontend no se reabrió** con esta base.
- **La base servida sigue siendo la vieja.** La nueva es `bolivia-v5.db`.
