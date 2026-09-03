# ROJO: faltan 247 documentos del corpus departamental, y no es culpa de la Gaceta

**2026-09-03.** Máquina: `brain-env` (gateway MUDH, servicio `build`). Todo medido, nada inferido.

Este archivo cierra la pregunta que dejé abierta hace una hora ("por qué faltan 2020, 2023, 2024
y 2026") y la respuesta es peor que las tres hipótesis que había planteado.

---

## 1. El hallazgo

```plain
manifest: 1031 | con texto en el corpus: 784
EN EL MANIFEST Y SIN TEXTO: 247

con archivo de texto EN DISCO: 247 de 247
donde: {'/workspace/corpus-legal/CORPUS_LEGAL_TARIJA_BOLIVIA_2026/11_TEXTO': 247}

caracteres declarados en el manifest para los que faltan: 2.928.976
con caracteres > 0: 247
```

**Los 247 están descargados, con el texto extraído y el archivo en disco.** No se perdieron: el
adaptador nunca los miró, porque lee `corpus/texto/*.txt` y ellos viven en `11_TEXTO/`.

**El corpus departamental debería tener 1.031 documentos y tiene 784: falta el 24% de nuestro
único diferencial real.**

---

## 2. Y explica exactamente el hueco de gestiones

```plain
gestion    manifest  c/texto   FALTAN
(vacio)          31       30        1
2010             14       13        1
2011             35       33        2
2012             40       34        6
2013             43       42        1
2014             26       26        0
2015              7        6        1
2016             78       66       12
2017             84       75        9
2018            108       87       21
2019            124       30       94     <-- pierde el 76%
2020             10        0       10     <-- pierde TODO
2021            155      137       18
2022            162      145       17
2023             21        2       19     <-- pierde el 90%
2024             17        2       15     <-- pierde el 88%
2025             69       56       13
2026              6        0        6     <-- pierde TODO
2078              1        0        1
```

**Ninguna de mis tres hipótesis era la correcta.** No es que la Gaceta no publicó (publicó 124
en 2019), no es que la descarga falló (`bajar: OK` en los 247), y no es que el título no traiga
año (el manifest tiene `gestion` en 1.000 de 1.031). **Es un empalme roto entre dos etapas del
pipeline propio.**

---

## 3. Por qué no entraron, medido

```plain
extraer=OK  estructurar=REVISION_HUMANA  -> 148
extraer=OK  estructurar=OK               -> 99

tipo: {'Resolucion del Pleno': 138, 'Ley Departamental': 109}
```

**Los 99 con `estructurar=OK` son lo grave:** pasaron todas las etapas del pipeline con estado
bueno y **no están en el corpus**. No hay motivo declarado en ninguna parte. Los otros 148 están
en `REVISION_HUMANA`, o sea el gate de calidad los marcó, y esos sí tienen una razón: entran con
`confianza: revision_humana` o no entran, pero **es una decisión, no un silencio**.

---

## 4. Por qué el guard de la ingesta no lo vio, y esto es lo que hay que arreglar

`Corpus.verificar()` compara **lo ofrecido por los adaptadores** contra lo que quedó en la base.
Los 247 **nunca fueron ofrecidos**, así que el invariante cerró en VERDE con `sin_rastro: 0` y
`perdidos: 0`. Es correcto y es insuficiente:

> **Un guard que solo compara la entrada del adaptador contra la base no puede detectar lo que el
> adaptador no lee.** El invariante correcto es contra el **manifest de descarga**, que es el
> censo de lo que la fuente ofreció, no contra la lista de archivos que el adaptador encontró.

Es el mismo patrón del `grep -c` que devuelve 0 y sale 1: el instrumento contesta sobre el sujeto
equivocado y su respuesta se lee como "todo bien".

---

## 5. Un ROJO adicional: el Código Penal que declaré no es el Código Penal

Verificando los textos nacionales por **encabezado real** en vez de por número:

```plain
Codigo Penal (lo que declare) | 1972/codigo---10426.md | 200615 B | 480 art
   encabezado REAL: "# Bolivia: Codigo de Familia, 23 de agosto de 1972"
   matrimonio: 184 | divorcio: 53 | asistencia familiar: 17
   parricidio: 0  | peculado: 0  | prevaricato: 0
```

Buscando por **contenido** (homicidio, parricidio, peculado, prevaricato, incumplimiento de
deberes), el Código Penal aparece en otros dos archivos:

```plain
marcas:5 | 184667 B | 2010/codigo---20101008.md | "Texto ordenado del Codigo Penal, 8 de octubre de 2010"
marcas:5 | 178841 B | 1972/codigo---1768.md     | "Codigo Penal, 23 de agosto de 1972"
```

**Y hay DOS "Código de Familia" que no son idénticos** (similitud 0,942, uno del 18 y otro del 23
de agosto de 1972). Cuál es el bueno **no está medido**.

**El error es mío y es el mismo de la mañana:** inferí la identidad del archivo por su número de
decreto ley en vez de leer su encabezado. El DL 10426 **es** el Código Penal en la realidad, pero
el archivo que lleva ese nombre en `aBOgacion` contiene el Código de Familia.

---

## 6. Y una que le debo al auditor

Dijo que la Ley 439 tiene **509 artículos** y yo escribí que no lo confirmaba porque mi regex
contaba menciones. Contando **artículos únicos**:

```plain
Codigo Procesal Civil (Ley 439) | 341724 B | 509 art_unicos
```

**Su número era exacto.** Mi objeción era sobre mi propio instrumento, no sobre su dato, y lo
correcto era arreglar el instrumento antes de dudar de él.

---

## 7. La tabla verificada de textos nacionales

Por **encabezado real** y **artículos únicos**, no por nombre de archivo:

| declarado | encabezado real del archivo | art. únicos | veredicto |
|---|---|---|---|
| CPE 2009 | Constitución Política del Estado de 2009 | 411 | **coincide** |
| Código Civil | Código Civil, 6-ago-1975 | 1.570 | coincide (reformas NO verificadas) |
| Proc. Civil | Código de Procedimiento Civil, 1975 | 795 | **ABROGADO** por Ley 439 |
| Código de Comercio | Código de Comercio, 25-feb-1977 | 1.692 | coincide (reformas NO verificadas) |
| **Código Penal** | **Código de Familia, 23-ago-1972** | 480 | **NO ES EL PENAL** |
| Código Tributario | Código Tributario Boliviano, 2003 | 221 | coincide |
| Código de Familia | Código de Familia, 18-ago-1972 | 472 | coincide, pero hay **dos** |
| Seguridad Social | Código de Seguridad Social, 1956 | 296 | coincide |
| Ley General del Trabajo | "Código del Trabjo" (sic), 1942 | 88 | coincide, con typo en la fuente |
| Ley 025 | Ley del Órgano Judicial, 24-jun-2010 | 235 | coincide |
| Ley 031 | Ley marco de Autonomías, 19-jul-2010 | 178 | coincide |
| Ley 548 | Código niña, niño y adolescente, 2014 | 349 | coincide |
| Ley 348 | Ley Integral... vida libre de violencia | 114 | coincide |
| Ley 1178 | Ley SAFCO, 20-jul-1990 | 56 | coincide |
| **Ley 439** | **Código Procesal Civil, 19-nov-2013** | **509** | **es el VIGENTE** |

---

## 8. Veredicto derivado (conclusión, no medición)

**ROJO en los datos, VERDE en el método.** El corpus departamental está al 76% de lo que ya
tenemos descargado, y lo que falta se concentra en las gestiones recientes, que son las que un
estudio consulta primero. Se recupera sin volver a bajar nada: el texto está en disco.

**Y la lección del día se repite tres veces:** el auditor estimó el insumo sin medirlo, yo
declaré ausentes códigos que estaban, y ahora declaré completo un corpus al que le falta un
cuarto. **Las tres veces el error fue confiar en un nombre en lugar de abrir el archivo.**

## 9. NO MEDIDO

- **Si los 148 en `REVISION_HUMANA` deben entrar** con `confianza: revision_humana` o esperar
  revisión. Es decisión de Abraham, no mía.
- **Por qué los 99 con todo OK quedaron afuera.** Tengo el síntoma, no la causa en el código del
  consolidador.
- **Cuál de los dos "Código de Familia" es el vigente**, y dónde está el Código Penal correcto
  entre `1972/codigo---1768.md` y `2010/codigo---20101008.md`.
- **Las reformas de los 12 textos que "coinciden".** Verifiqué la identidad, **no** la vigencia
  de su contenido. Un Código Civil de 1975 sin sus modificaciones sigue siendo una trampa.
- **El `2078`** sigue siendo un error de extracción conocido y sin corregir.
