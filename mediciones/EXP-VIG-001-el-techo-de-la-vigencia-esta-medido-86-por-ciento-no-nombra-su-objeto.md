# EXP-VIG-001 · El techo de la vigencia está medido: el 86 % no nombra su objeto

**Medido:** 2026-09-06 · base de producción `rag-abogacia-v7.db` en la VM, **abierta en modo solo-lectura**
**Escrituras:** **CERO.** Marcar "derogada" mal en el corpus de un abogado es el error más caro del proyecto; el paso de escritura va en su propio turno con guards.

---

## El número que decide

De **146 secciones abrogatorias con verbo** en las departamentales:

| Clase | Secciones | % |
|---|---|---|
| **Genéricas** ("todas las disposiciones contrarias") | **92** | 63 % |
| Genéricas con otra redacción ("cualquier norma de igual o menor jerarquía") | **34** | 23 % |
| **Nombran una ley departamental** | **18** | 12 % |
| Abrogan otro tipo de norma (Resolución del Consejo) | 2 | 1 % |

**El 86 % de las abrogaciones del corpus NO nombra a su objeto.** Verbatim de tres de ellas:

> «Se dispone la Derogación y Abrogación de cualquier Norma Departamental de igual o menor jerarquía contraria a la presente Ley.»

> «Se abrogan y derogan todas las normas de igual o menor jerarquía, que sean contrarias a la presente Ley Departamental.»

**Eso no lo resuelve ningún parser.** Decidir qué norma es "contraria" a otra es interpretación jurídica, no extracción de texto. **La vigencia al 100 % de las 512 no existe con esta fuente**, y ninguna mejora de mi código la va a producir.

Y es un dato Útil para el abogado, no un hueco: "esta ley fue alcanzada por una cláusula genérica de la LD X" es información que hoy el sistema no muestra.

---

## ME REFUTO: mi hipótesis del apóstrofo dio CERO ganancia

Al leer los hallazgos vi `Ley Departamental N' 094` con **apóstrofo** en vez de grado, y supuse que mi regex perdía leyes por eso. Construí un regex tolerante (acepta `'`, `´`, `’`, coma, punto y coma) y lo corrí contra el estricto como A/B:

```
secciones que SOLO el regex tolerante lee: 0
```

**Cero.** El regex **no era el cuello de botella**. Si hubiera "arreglado" eso sin medir, habría declarado una mejora que no mueve el número, que es exactamente lo que me pasó tres veces con los títulos (119 y 389, dos veces igual).

---

## Lo que SÍ ganó: restringir a la SECCIÓN en vez de buscar por proximidad

| Método | Hallazgos | Calidad |
|---|---|---|
| proximidad ±300 caracteres del verbo | 17 | **casi todos falsos** |
| solo dentro de la sección abrogatoria | **24** | reales, leídos uno por uno |

Los falsos del método por proximidad, verbatim:

```
454/2022 -> 139 : "los articulos modificados y complementados con la presente
                   norma a la Ley N 139"                        <- MODIFICA
485/2024 -> 350 : "el Consejo Departamental creado mediante la Ley Dept N 350"
                                                                  <- CITA
191/2016 -> 139 : "conforme al Articulo 31 de la Ley Departamental Nro 139"
                                                                  <- CITA
```

La causa: la disposición abrogatoria es una sección de cierre estándar, y **cerca de ella hay muchas menciones a otras normas por motivos que no son abrogarlas**. La proximidad no es el sujeto (E-01).

### La cadena, y un eslabón nuevo

Con el método por sección, leído verbatim del texto:

- **LD 07 ← abrogada por LD 129/2015**: «queda abrogada la Ley Departamental N° 07 Transitoria de Atribuciones y Funciones de los Ejecutivos Seccionales»
- **LD 129 y LD 432 ← abrogadas por LD 500/2025**: «Se abroga la Ley Departamental N° 129 … Ley Departamental N° 432»
- **LD 500 ← abrogada por LD 520**: «Se abroga la Ley Departamental W 500»
- **NUEVO: LD 094 y complementarias ← abrogadas por LD 517/2026**: «Se abroga la Resolución del Consejo Departamental N° 237/2008 … la Ley Departamental N' 094 Departamentalización de Carreteras … las Leyes Departamentales Complementarias»

Cadena de Organización del Ejecutivo: **07 → 129 → 500 → 520**. Vigente al final: **520**.
Cadena nueva de Carreteras: **094 + complementarias → 517**.

12 leyes distintas aparecen como objeto: `7, 19, 109, 129, 139, 279, 293, 300, 420, 432, 484, 500`.

---

## DOS DEFECTOS DE MI EXTRACTOR, cazados LEYENDO y no contando

### P1 · Título anidado: atribuye la abrogación a la ley equivocada

```
"Se deroga el articulo 2 respecto los articulos 11 y 21 ... de la
 Ley Departamental N 202 Modificatoria a la Ley Departamental N 139"
```

El objeto es la **202**. La **139** aparece solo dentro del *título* de la 202. Mi extractor reportó **139** y **la 202 no está en la lista de objetos**. Si esto se aplicaba a la base, marcaba parcialmente derogada una ley que ese texto no toca.

### P2 · La LD 094 no aparece entre los objetos

Está textual en la sección de la 517 y **no la detectó**. Causa **NO MEDIDA**: el A/B del apóstrofo dio cero, así que la explicación fácil está descartada y no tengo otra. Queda como rojo abierto, no como "ya sé por qué".

---

## Corrección de un número que vengo repitiendo mal

Vengo diciendo **"las 512 departamentales"**. Medido:

| Sujeto | Cantidad |
|---|---|
| documentos con `jurisdiccion = departamental` | **1.034** |
| de esos, `tipo_norma` tipo Ley | **512** |

Los 512 son las **leyes**; las 1.034 incluyen resoluciones de la Asamblea y actas. Cuando digo "512" hablo de leyes, y varios de mis conteos anteriores de campos vacíos estaban tomados sobre 1.034. **Son dos sujetos y los mezclé.**

### Estado real de los campos (sobre 1.034)

| Campo | Vacíos | Con dato |
|---|---|---|
| `vigente` | 1.021 | **13** |
| `derogada_por` | 1.020 | 14 |
| `fecha` | **897** | 137 |
| `materia` | **1.034** | **0** |
| `anio` | 32 | 1.002 |

**`materia` está vacía en el 100 %.** Y `fecha` en el 86,8 %, que **bloquea la vigencia por otro lado**: sin fecha no se puede ordenar una cadena de derogaciones ni desempatar dos normas del mismo número.

---

## Otro defecto mío: mi propio censo miró la tabla equivocada

La v1 de `censo_vigencia_512.py` buscó la columna de texto en `documentos` y reportó **`columna_texto: NO EXISTE`**, dejando sin medir el número que decide todo. El texto vive en **`chunks.cuerpo`** y se une por `doc_id`. **Un instrumento que mira la tabla equivocada devuelve "no hay" igual que una ausencia real.**

---

## Veredicto operativo (cambia el plan, y no a mi favor)

1. **La vigencia completa de las 512 NO es alcanzable con esta fuente.** Medido, no estimado: 86 % de las abrogaciones no nombra su objeto.
2. Lo alcanzable son **~20 abrogaciones nombradas** más las **dos cadenas** resueltas. Eso es ~4 % de las leyes, no el 100 %.
3. Lo que SÍ mueve la aguja y no depende de más parseo: **el índice inverso a pedido**. Cuando el abogado cita la LD 129, el sistema responde "la LD 500 la abroga" leyendo el corpus en el momento. No hace falta pre-marcar 512 filas para eso.
4. **`materia` vacía al 100 %** es probablemente más barata de mover que la vigencia, y afecta a todas las búsquedas.

## NO MEDIDO

- La causa de P2 (la 094 sin detectar).
- El objeto real de las derogaciones parciales por artículo ("se derogan los artículos 19, 20, 21…" sin ley visible en la ventana).
- Si las 92 + 34 genéricas pueden al menos **listarse** como advertencia por ley.
- **Nada escrito en la base.** Los 13 `vigente` y 14 `derogada_por` actuales son de una corrida anterior, no de esta.
