# Evidencia cruda: el corpus nacional, 15 normas verificadas

**2026-09-04, 00:20-00:45 UTC.** Máquina: `brain-env` (gateway MUDH, servicio `build`).
Verbatim. El veredicto va aparte al final.

---

## 1. Por qué NO se copia de las empresas que ya lo hicieron

El pedido incluía "podrías explorar esas empresas que ya hicieron ese trabajo para tomarlo de
ahí". **No se hizo, y el motivo no es solo legal:**

1. **LeyNova, SILEG, Difusión Jurídica y Derechoteca son bases cerradas por suscripción.** Sus
   términos lo prohíben y tienen responsable identificable.
2. **Su texto no es citable.** Si el corpus dice "según LeyNova", el abogado no puede verificar
   nada contra el Estado.
3. **Destruye el único diferencial que tenemos.** El valor de este corpus es que **cada documento
   se verifica contra la fuente oficial**, con su URL y su sha256. Un texto de tercero sin
   procedencia oficial convierte el sistema en una copia peor de lo que copia.

**Lo que SÍ se hizo es la versión legal y mejor de esa idea: usar el trabajo ajeno como ÍNDICE y
bajar de la fuente oficial.** `aBOgacion` (repo público) dice qué normas existen; **LexiVox**
entrega el texto con su URL citable.

---

## 2. Las fuentes oficiales, medidas antes de elegir

```plain
https://www.lexivox.org/                       -> 200
https://www.lexivox.org/norms/BO-CPE-20090207  -> 200
http://www.gacetaoficialdebolivia.gob.bo/      -> ERR: urlopen error timed out
https://tcpbolivia.bo/tcp/                     -> ERR: read operation timed out
https://buscador.tcpbolivia.bo/                -> 200
```

**La Gaceta Oficial nacional NO responde** (dos intentos, HTTP y HTTPS). LexiVox sí. Y el buscador
del TCP responde: queda anotado para la próxima fuente.

---

## 3. Dos trampas de LexiVox, y las dos son silenciosas

### 3.1 Devuelve HTTP 200 para normas que NO tiene

```plain
BO-DL-10426 -> 200 | 216 chars | "Norma inexistente en la base de datos"
```

**Un `status == 200` no prueba que el documento exista.** Sin leer el cuerpo, entran fantasmas de
216 bytes indexados como si fueran códigos.

### 3.2 El patrón del identificador cambia, y trae la norma equivocada con el número correcto

```plain
BO-L-1970   -> Codigo de Procedimiento Penal, 25-mar-1999   437 articulos   CORRECTO
BO-L-N1970  -> INEXISTENTE (con HTTP 200)

BO-L-N439   -> Codigo Procesal Civil, 19-nov-2013           509 articulos   CORRECTO
BO-L-439    -> Ley N 439 de 18 de diciembre de 1968           3 articulos   OTRA NORMA
```

**`BO-L-439` y `BO-L-N439` son normas distintas con el mismo número.** Un número de ley no
identifica una norma; el número más el año sí. Por eso cada objetivo declara **qué título
espera** y se acepta solo si coincide.

**Y el 509 confirma al auditor:** dijo que la Ley 439 tiene 509 artículos, y el conteo sobre el
texto oficial da 509 únicos. Su dato era exacto.

---

## 4. ROJO propio: mi guard dejó pasar el Código de Familia como Código Penal

Primera corrida, verbatim:

```plain
  OK     codigo_penal    BO-COD-DL10426 art:480  208036 chars | Bolivia: Código de Familia, 23 de agosto de 1972
  ROJO   ley_1178_safco  -> titulo_no_coincide: "Bolivia: Ley de Administración y Control Gu..."
```

**Dos errores míos de configuración, no del mecanismo:**

- para `codigo_penal` puse el esperado en `"codigo"`, que matchea cualquier código, y **aceptó el
  Código de Familia como si fuera el Penal**;
- para la Ley 1178 puse `"1178"` y su título real no lleva el número, así que **rechazó una norma
  correcta**.

**Un guard con el patrón equivocado es peor que ninguno: da la sensación de haber verificado.** El
patrón esperado tiene que ser **discriminante**: lo más corto que distinga esta norma de sus
vecinas.

---

## 5. Las 15 normas obtenidas, con su identidad verificada

```plain
  OK  cpe_2009                    BO-CPE-20090207  art:412   1717132 chars
  OK  codigo_procesal_civil       BO-L-N439        art:509    342895 chars
  OK  codigo_procedimiento_penal  BO-L-1970        art:437    262805 chars
  OK  codigo_familia              BO-COD-DL10426   art:480    208036 chars
  OK  codigo_comercio             BO-COD-DL14379   art:1692   709343 chars
  OK  codigo_tributario           BO-L-2492        art:198    304273 chars
  OK  codigo_nna                  BO-L-N548        art:349    296701 chars
  OK  codigo_procesal_trabajo     BO-COD-DL16896   art:255     85425 chars
  OK  ley_1178_safco              BO-L-1178        art:63     226346 chars
  OK  ley_348                     BO-L-N348        art:114    130203 chars
  OK  ley_1173                    BO-L-N1173       art:139    166186 chars
  OK  ley_025_organo_judicial     BO-L-N25         art:235    171186 chars
  OK  ley_031_autonomias          BO-L-N31         art:178    337544 chars
  OK  ley_1768_modif_penal        BO-L-1768        art:59      46333 chars
  OK  dl_13214_seguridad_social   BO-DL-13214      art:91      45061 chars

NORMAS OBTENIDAS: 15 de 18 objetivos | caracteres: 5.049.469
```

### Los 3 que faltan, y son de los más usados

```plain
ROJO codigo_civil         -> BO-DL-12760, BO-COD-DL12760, BO-CC-12760, BO-L-12760: inexistentes
ROJO codigo_penal         -> BO-DL-10426, BO-CP-DL10426, BO-COD-DL1768: inexistentes
ROJO ley_general_trabajo  -> BO-DL-19421208, BO-L-19421208, BO-LGT-19421208: inexistentes
```

**Ningún patrón probado los devuelve en LexiVox.** `BO-CODIGO-DL12760` responde 200 con 8.890
bytes pero es una página de interfaz vacía ("Mostrar información"), sin el texto ni links al
texto. Y en el camino aparecieron dos normas que SÍ son útiles y no estaban en la lista: el
**Código Procesal del Trabajo** (`BO-COD-DL16896`) y la **Ley 1768 de Modificaciones al Código
Penal**.

**Los 3 existen en `aBOgacion`** (Código Civil con 1.570 artículos, LGT con 90), pero su
procedencia ahí es **de segunda mano**: el repo declara que bajó de LexiVox y no tiene licencia.
Meterlos con esa procedencia contradice la regla de este corpus, así que **es decisión de
Abraham**, no mía.

---

## 6. La reconstrucción con lo nacional adentro

```plain
$ python3 -m unittest test_alias test_ingesta test_procedencias test_normalizar
Ran 32 tests in 3.175s
OK

$ python3 ingesta.py --origen /workspace/corpus-todo --db /workspace/bolivia-v7.db
  tarija_gaceta: 1037 documentos
    censo de la fuente: 1037 | por OCR: 787 | por extraccion: 250 | SIN TEXTO: 0
  lexivox_nacional: 15 documentos
    censo de la fuente: 15 | por OCR: 0 | por extraccion: 15 | SIN TEXTO: 0
  tsj_genesis: 5070 documentos
    censo de la fuente: 5070 | por OCR: 5070 | por extraccion: 0 | SIN TEXTO: 0

documentos canonicos: 6079 | chunks: 78930 | procedencias: 6122
por jurisdiccion: {'departamental': 1034, 'jurisprudencia': 5030, 'nacional': 15}
cola de revision humana: 6388
segundos: 19.6 | indice: 217.6 MB

VERIFICACION: {"censo_de_la_fuente": 6122, "ofrecidos": 6122, "canonicos_nuevos": 6079,
"sin_rastro": 0, "documentos_sin_procedencia": 0, "veredicto": "VERDE"}

$ python3 test_api.py http://127.0.0.1:8160
VERDE: la API cumple el contrato que un agente necesita     (45/45)
  documentos: 6079 | caracteres: 102620935
  por jurisdiccion: {'departamental': 1034, 'jurisprudencia': 5030, 'nacional': 15}
```

**Y ahora se busca en lo nacional:**

```plain
"asistencia familiar"  -> 30 pasajes en normas NACIONALES
"sociedad anonima"     -> 26 pasajes
"usucapion"            ->  2 pasajes
```

---

## 7. La vigencia: por qué queda en `None` incluso sin señales

Las 15 entran con `vigente = None`. **Incluso las que no mencionan ninguna abrogación**, y el
motivo es el caso que ya nos mordió: el Código de Procedimiento Civil de 1975 está **abrogado**
por la Ley 439 y **su propio texto no lo dice**, porque una norma no se entera de su propia
muerte.

**No mencionar una abrogación no es prueba de estar vigente.** Las señales (`abrogad`, `derogad`,
`modificad`) entran a la cola como pistas: 15 items `posible_cambio_normativo`, más el estado
`vigencia_sin_senales` para las que callan.

---

## 8. Veredicto derivado (conclusión, no medición)

**VERDE con alcance declarado.** El corpus tiene **6.079 documentos y 102,6 millones de
caracteres**, con las tres jurisdicciones vivas: nacional, departamental y jurisprudencia. Las 15
normas nacionales entran con **texto oficial, URL citable, sha256 e identidad verificada contra su
título real**.

**Y el corpus nacional NO está completo:** faltan Código Civil, Código Penal y Ley General del
Trabajo, que son tres de los cuatro que un abogado abre todos los días.

## 9. NO MEDIDO

- **Las reformas de las 15.** Se verificó **identidad**, no vigencia del contenido. Un Código de
  Comercio de 1977 con 1.692 artículos puede tener modificaciones posteriores que este texto no
  refleja, y eso **no está medido**.
- **Si LexiVox publica el texto consolidado o el original.** No lo declara en la página.
- **El Código Civil, el Penal y la LGT por otra vía**: el buscador del TCP responde 200 y no se
  exploró; la Gaceta Oficial nacional no responde.
- **Vigencia: 6.079 sin medir.** Ni una.
- **Los textos nacionales no se subieron al repo**: 5 MB en `brain-env`. Publicarlos es decisión
  de Abraham.
- **El frontend no se reabrió** con esta base, y la base servida sigue siendo la vieja.
