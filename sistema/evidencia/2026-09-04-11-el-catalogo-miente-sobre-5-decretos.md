# 2026-09-04 · El catálogo miente sobre 5 decretos, y mi parser mintió tres veces antes de medirlo

Con la fase 1 corriendo, audité los 387 decretos ya extraídos contra **su propio sello**: la línea `Corresponde al Decreto Departamental N° <numero>/<anio>` que la Gobernación estampa en la cabecera. El número del catálogo del portal no es evidencia de nada; el sello sí.

## Resultado

```
IDENTIDAD sobre 387 documentos extraidos
   coincide                     365
   via_corresponde_al           266
   via_encabezado               104
   SIN_SELLO_cuerpo               9
   SIN_SELLO_anexo                8
   DIFIERE                        5
   anio_recuperado_del_sello      4
```

Los **4 documentos cuyo slug no traía año** quedaron resueltos: el sello se lo puso. Eso son 4 registros menos con año vacío, el mismo defecto que en las leyes departamentales escondía años enteros.

## Los 5 que difieren, uno por uno

| id | catálogo | sello del documento | veredicto |
|---|---|---|---|
| **3396** | 071/2021 | **070/2021** | **el portal sirve el PDF equivocado.** sha256 idéntico al id 2049, que sí es el 070/2021. El DD 071/2021 **no está en el corpus** |
| **2166** | 021/2022 | **057/2022** | **bug mío.** El slug arranca `decreto-departamental-057-2022-...` y más adelante cita el 021/2022. Mi extractor tomó el número citado. Es el DD 57/2022 |
| **1793** | 163/2021 | **018/2021** | catálogo o portal equivocado. El texto es único (no es copia de otro), así que el contenido ES el 018/2021. Un DD 163 en 2021 es implausible: la serie de ese año llega a 71 |
| **1674** | 129/2020 | **129/2019** | número coincide, año no. Vía OCR, así que puede ser un 0 leído como 9. **NO MEDIDO** hasta ver la fecha del PDF |
| **3062** | 010/2025 | ilegible (`N2 0101)/2025`) | **la capa de texto nativa del PDF está podrida**, no es OCR: el mismo archivo escribe `ElEeryyjuk` donde va `DE TARIJA`. El catálogo probablemente tenga razón. **NO MEDIDO** |

El 3396 es exactamente la trampa del Código Procesal Civil de 1975: **hash correcto sobre el texto equivocado**. Sin este guard, el 070/2021 entraba dos veces, una firmada como 071, con procedencia impecable.

Corolario que me obliga a matizar algo que dije el 3-sep: **`texto_nativo_pdf` no es sinónimo de texto confiable.** El caso 3062 tiene capa nativa y está ilegible. La vía dice de dónde salió el texto, no cuánto vale.

## Mi propio parser falló TRES veces, y el control lo cazó las tres

Ninguna de las tres versiones anteriores habría servido, y las tres se veían bien mientras no las midiera contra sellos reales.

**v1 — medí la cita y concluí sobre el sujeto (E-01).** Buscaba el primer número de decreto del texto. Pero los decretos **citan otros decretos** en el CONSIDERANDO. Reportó **13 falsos positivos**, entre ellos cinco documentos "declarando" ser el 1/2020, que era la norma citada.

**v2 — exigí el símbolo de grado.** El OCR lo destroza sin piedad: `N9`, `N2`, `h12`, `N 9`, `W`, `N5`, `hig`, `N"`, `N?`. **101 documentos** quedaron marcados "sin sello" cuando el sello estaba ahí, a la vista.

**v3 — comodín `\S{0,4}` para la basura, y el comodín se comió el número.** Sobre `N0020/2026` devolvía **0/2026**. `\S` acepta dígitos, así que el comodín goloso le robaba los dígitos al número. **27 falsos positivos**, y todos parecían hallazgos.

**v4 (la que anda) — anclar en el año y tomar los últimos 3 dígitos que lo preceden.** Así la basura no puede robar dígitos. Con el separador tolerante a `)`, espacios y guiones, el control pasa **12/12** sobre sellos reales sacados del corpus.

El guard **se niega a medir si no pasa su propio control**: si el parser no lee sus 12 sellos, imprime ROJO y no evalúa ni un documento. Un guard con el patrón equivocado es peor que ninguno, y ya me pasó una vez este mes con el Código de Familia.

## Lo demás que salió de la auditoría

**Los duplicados de número son anexos legítimos, no basura.** El DD 019/2024 aparece 6 veces: el cuerpo (4 páginas) más 5 anexos que son planes de contingencia completos (35, 38, 29, 35 y 40 páginas: heladas, sequías, granizada, incendios, lluvias). El DD 070/2021 son 3: reglamento más organigrama más tabla de equivalencias. **14 anexos** detectados y marcados. La clave `(numero, anio)` **no es única** y la ingesta no puede usarla como identidad.

**Un duplicado real del portal:** ids 3300 y 3301, mismo slug, mismo sha256, mismo DD 008/2026 publicado dos veces. Se resuelve con alias de procedencia, como los 40 duplicados de GÉNESIS.

**Calidad del texto, medida:** 329 nativos y 54 por OCR sobre 383. Mediana de 11.177 caracteres, 2.534 páginas procesadas. Rendimiento por página casi igual entre vías (mediana 2.600 nativo vs 2.359 OCR), lo que dice que **el OCR propio no está perdiendo texto**. Ninguno por debajo de 500 caracteres: cero extracciones vacías disfrazadas.

## NO MEDIDO

- Los 544 decretos que faltan extraer: el guard se re-corre al cerrar la fase 1.
- La fecha de promulgación del PDF, que resolvería el 1674 y el 1793.
- Si el DD 071/2021 existe por otra vía: el portal no lo sirve.
- Los 9 cuerpos sin sello legible, a revisar a mano.
- Nada de esto está en la base todavía. Fase 2 no arrancó.

## Estado de la fase 1

```
[ 380/931] ok=371  pobres=0  fallos=9  | 3,1 doc/min
```

Siguen siendo **los mismos 9 fallos** del principio: los 9 que la fuente no sirve.
