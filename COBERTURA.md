# Que cubre este corpus, y que NO

**Medido el 2026-09-03** sobre `indices/manifest.jsonl` (1.031 documentos) y sobre los 784
textos OCReados de `corpus/texto/`.

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

## Lo que FALTA, y no es un detalle

Un estudio juridico en Tarija litiga sobre normativa **nacional**, y de eso el corpus no tiene
nada:

- **Codigos:** Civil, Penal, Procesal Civil, Procesal Penal, de Familia, Tributario, Comercio.
- **Constitucion Politica del Estado** (texto completo; solo hay citas de terceros).
- **Leyes nacionales clave:** Ley General del Trabajo, Ley 1178 (SAFCO), Ley 025 (Organo
  Judicial), Ley 348, Ley 031 (Marco de Autonomias), Codigo Nino Nina Adolescente.
- **Jurisprudencia:** Autos Supremos del Tribunal Supremo, Sentencias Constitucionales del
  TCP. Nada. La fuente que se midio el 2026-09-02 (GENESIS) es una SPA con API propia y quedo
  pausada por decision del usuario; el otro candidato resulto ser un observatorio de genero
  con spam en su API, no un repositorio de Autos Supremos.
- **Normativa municipal** de Tarija, Yacuiba, Villamontes, Bermejo: ordenanzas y leyes
  municipales autonomas.
- **Reglamentos y decretos departamentales** del Organo Ejecutivo (el corpus solo tiene el
  Legislativo).

## Para que SI sirve hoy

Para lo que es: **la normativa departamental de Tarija, completa y verificable, 2010-2026.**
Eso es exactamente lo que no esta en ningun buscador y lo que un estudio no puede consultar
sin ir a la Gaceta a mano. Es un anexo de alto valor, no la biblioteca.
