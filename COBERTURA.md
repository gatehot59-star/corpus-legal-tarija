> # ⚠️ ESTE ARCHIVO QUEDÓ VIEJO Y EN UN PUNTO QUE IMPORTA
>
> **Aviso agregado el 2026-09-10.** Lo de abajo se midió el **2026-09-03** y se
> conserva tal cual, porque borrar una medición vieja es peor que fecharla. Pero
> hay que leerlo sabiendo dos cosas:
>
> **1. Dice "Jurisprudencia: Autos Supremos del Tribunal Supremo... Nada", y hoy
> el corpus tiene 5.030 Autos Supremos.** La composición medida el 2026-09-09 en
> `/estado` es: GENESIS **5.030** + Gaceta Tarija **1.034** + LexiVox **15** =
> **6.079 documentos**. O sea que la jurisprudencia no solo existe: es el **82,7 %
> del corpus**.
>
> **2. El error no es que el dato envejeció: es que midió un sujeto y concluyó
> sobre otro.** Este archivo midió `indices/manifest.jsonl` (**1.031**
> documentos, el pipeline de la Gaceta departamental) y tituló la conclusión
> "qué cubre este corpus". El **mismo día**, `BUSCADOR.md` reportaba **3.646
> documentos indexados** y sus propios ejemplos traían *"Autos Supremos de Sala
> Civil sobre usucapión (2016, 2018, 2023)"*. Dos documentos, misma fecha, dos
> universos: 1.031 y 3.646. El manifiesto de un pipeline no es el corpus.
>
> **Por qué esto no es una errata cosmética:** quien lea este archivo concluye
> que el corpus no tiene jurisprudencia, y de ahí que no hay nombres de partes,
> y de ahí que no hay riesgo de privacidad. **La fuga medida el 2026-09-10 está
> exactamente ahí:** `q=Mamani` devolvía 1.232 pasajes y el primero nombraba a
> las dos partes de una causa de violación de un menor. Un documento que
> tranquiliza sobre el riesgo real es peor que un documento desactualizado.
>
> **Lo que sigue siendo cierto de abajo:** el inventario de lo que **falta**
> (Códigos, CPE completa, leyes nacionales, normativa municipal, reglamentos
> departamentales del Ejecutivo) y el análisis de materias sobre la normativa
> departamental. Y el defecto propio del `iva`/`LEGISLATIVA`, que sigue siendo
> una buena lección.
>
> **Estado del acceso al escribir este aviso:** el buscador público está
> **cerrado** desde el 2026-09-10 06:29 UTC (ver `CIERRE-PUBLICO-2026-09-10.md`).
> La composición de arriba sale del snapshot de `/estado` del 2026-09-09, no de
> una consulta de hoy.

---

# Que cubre este corpus, y que NO

**Medido el 2026-09-03** sobre `indices/manifest.jsonl` (1.031 documentos) y sobre los 784
textos OCReados de `corpus/texto/`.

**Sujeto de esta medición, agregado el 2026-09-10 para que no se vuelva a mezclar:** el
pipeline de la **Gaceta departamental de Tarija**. NO el corpus completo, que ya en esa fecha
incluía documentos que este manifiesto no lista.

## La respuesta corta: NO alcanza para "los rubros legales" de un estudio

El corpus tiene **una sola jurisdiccion** y **dos tipos de norma**:

| jurisdiccion | documentos |
|---|---|
| `departamental_tarija` | 1.031 |

| tipo de norma | documentos |
|---|---|
| Ley Departamental | 511 |
| Resolucion del Pleno de la Asamblea | 520 |

Gestiones **2010 a 2026** (mas una `2078` que es un error de extraccion y un `?`).

## Materias presentes, medidas sobre el texto real

Contando menciones con limites de palabra sobre los 784 documentos OCReados:

| materia | documentos | % | menciones |
|---|---|---|---|
| presupuestario | 325 | 41,5% | 1.378 |
| ambiental / hidrocarburos | 149 | 19,0% | 305 |
| obras publicas | 127 | 16,2% | 435 |
| salud / educacion | 114 | 14,5% | 379 |
| honores y distinciones | 103 | 13,1% | 232 |
| constitucional (citas a la CPE) | 69 | 8,8% | 347 |
| tributario | 45 | 5,7% | 146 |
| contrataciones publicas | 32 | 4,1% | 80 |
| municipal | 17 | 2,2% | 27 |
| civil / contratos | 16 | 2,0% | 29 |
| agrario / tierras | 12 | 1,5% | 20 |
| **penal** | **3** | 0,4% | 4 |
| **laboral** | **2** | 0,3% | 2 |
| **procesal** | **1** | 0,1% | 1 |
| **familia** | **0** | 0,0% | 0 |

**Limite del instrumento, declarado:** esto cuenta MENCIONES, no cobertura normativa. Que 69
documentos citen la Constitucion no significa que el corpus tenga la Constitucion; significa
que la mencionan.

**Y un error propio en esta misma medicion:** la primera pasada dio "tributario en el 100% de
los documentos". Buscaba `iva` como substring y **LEGISLATIVA contiene "iva"**. Un 100%
clavado tenia que ser sospechoso desde el numero mismo. Con limites de palabra, 5,7%.

> **Nota del 2026-09-10:** estos porcentajes de materia describen la **normativa
> departamental**, y siguen siendo válidos para ese sujeto. NO describen el corpus de hoy: los
> 5.030 Autos Supremos tienen otra distribución de materias, y ahí sí hay penal, familia y
> violencia. Eso es justamente lo que activa la reserva legal de la compuerta.

## Lo que FALTA, y no es un detalle

Un estudio juridico en Tarija litiga sobre normativa **nacional**, y de eso el corpus no tiene
nada:

- **Codigos:** Civil, Penal, Procesal Civil, Procesal Penal, de Familia, Tributario, Comercio.
- **Constitucion Politica del Estado** (texto completo; solo hay citas de terceros).
- **Leyes nacionales clave:** Ley General del Trabajo, Ley 1178 (SAFCO), Ley 025 (Organo
  Judicial), Ley 348, Ley 031 (Marco de Autonomias), Codigo Nino Nina Adolescente.
- ~~**Jurisprudencia:** Autos Supremos del Tribunal Supremo, Sentencias Constitucionales del
  TCP. Nada.~~ **SUPERADO (2026-09-10): hay 5.030 Autos Supremos vía GENESIS, y son el 82,7 %
  del corpus.** Lo que sigue faltando son las **Sentencias Constitucionales del TCP**. La
  fuente que se midio el 2026-09-02 (GENESIS) es una SPA con API propia y quedo pausada por
  decision del usuario; el otro candidato resulto ser un observatorio de genero con spam en su
  API, no un repositorio de Autos Supremos.
- **Normativa municipal** de Tarija, Yacuiba, Villamontes, Bermejo: ordenanzas y leyes
  municipales autonomas.
- **Reglamentos y decretos departamentales** del Organo Ejecutivo (el corpus solo tiene el
  Legislativo).

## Para que SI sirve hoy

Para lo que es: **la normativa departamental de Tarija, completa y verificable, 2010-2026.**
Eso es exactamente lo que no esta en ningun buscador y lo que un estudio no puede consultar
sin ir a la Gaceta a mano. Es un anexo de alto valor, no la biblioteca.

> **Corrección del 2026-09-10 a este último párrafo:** sigue siendo cierto que la normativa
> departamental es el aporte único, pero **por documento es el 17,3 % del corpus**. El 82,7 %
> son Autos Supremos, y ese es el material que la compuerta de Custos Legis retiene de la capa
> pública por tener nombres de partes. O sea: **la parte del corpus que se puede publicar
> abierta es la minoría**, y eso cambia el diseño del producto que lo consume. Medido con
> `custos-legis-tarija/backend/impacto_compuerta.py`.
