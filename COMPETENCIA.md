# Que existe ya en Bolivia, que se puede COPIAR, y donde esta el hueco real

**Investigado el 2026-09-03.** Y **corregido el mismo dia**, porque la primera version de este
archivo tenia dos afirmaciones que no aguantaron una medicion.

---

## Lo primero: se puede pagar y copiar el corpus de la competencia?

Hay que separar tres cosas que no son lo mismo.

### Los comerciales: NO

| producto | lo que declara | se puede copiar? |
|---|---|---|
| **LeyNova** | 35.000+ normas, 163.000+ extractos TCP/TSJ, control de vigencia, verificacion de citas | **No.** Vende consultas por suscripcion, con el analisis corriendo en su propia infraestructura. No publicita descarga masiva ni API de datos. |
| **Difusion Juridica** | 163.000 resoluciones judiciales (47.236 TCP, 49.406 TSJ, 25.271 Corte Suprema) | **No.** Base de datos por suscripcion. |
| **SILEG / Bolivia Legal** | 100.000+ textos concordados, 25 anos de trabajo | **No.** Licencias por terminal, instalacion corporativa. |
| **Derechoteca, Lexius** | jurisprudencia TCP/TSJ con IA | **No.** Suscripcion mensual o anual. |

Eso es el modelo de negocio: **el corpus ES el activo.** Pagar da derecho a consultar, no a
quedarse con la base. Y bajarla masivamente para alimentar una IA propia va contra sus terminos,
aparte de ser un problema legal para un estudio de abogados, que es el peor lugar posible para
tener uno.

### Las fuentes oficiales: SI, y son gratis

Medido hoy, todas responden:

| fuente | estado |
|---|---|
| `lexivox.org` | 200 |
| `bolivia.justia.com` | 200 |
| `krima.organojudicial.gob.bo` (Tribunales Departamentales) | 200 |
| `buscador.tcpbolivia.bo` (Tribunal Constitucional) | 200 |
| `genesis.tsj.bo` | 200, y ya lo usamos: 2.862 resoluciones |
| `gacetaoficialdebolivia.gob.bo` | **no resuelve** desde aca |

O sea: **lo que los comerciales venden sale, en su mayor parte, de fuentes publicas.** Eso es lo
que hicimos nosotros con Tarija y con el TSJ.

### Los repos de GitHub: SI, y uno tiene justo lo que nos falta

| repo | estado medido | licencia | que trae |
|---|---|---|---|
| **`strysg/aBOgacion`** | **VIVO, 921 MB clonados** | GPLv3 (README; GitHub no declara una) | **27.210 normas nacionales en markdown**: 13.204 leyes, 8.732 decretos supremos, 3.945 decretos presidenciales, 330 resoluciones ministeriales, 311 decretos ley. Rango **1826-2026**. Mas `metadatos.json` con 21.475 entradas. Fuente: lexivox + Gaceta. |
| **`israelmamani/tcp-bolivia-mcp`** | VIVO, 10 MB | **MIT** | MCP del Tribunal Constitucional con referencias reproducibles por parrafo. Codigo, no corpus. |
| **`datosbolivia/tramites-bo`** | VIVO, 14 MB | **CC0** | tramites del Estado, no normativa. |
| **`Ansvar-Systems/Bolivian-law-mcp`** | **404 con token: NO EXISTE publicamente** | -- | ver correccion abajo |

---

## CORRECCION 1 · cite un repo que no existe

En la primera version de este archivo escribi que `Ansvar-Systems/Bolivian-law-mcp` tenia "casi
nuestra misma arquitectura" (2.497 leyes, SQLite FTS5, BM25, MCP con validacion de citas). Lo
tome de un resultado de busqueda web y **lo presente como hecho verificado sin abrirlo**.

Medido con token: **HTTP 404.** No existe publicamente, o fue borrado o renombrado.

Peor: mi primera medicion, sin token, dio **403** y yo lo lei como "no accesible publicamente"
para los cuatro repos, incluido uno que si existe. Un 403 de rate limit leido como ausencia es
**el mismo cero disfrazado de medicion** que me mordio con la credencial de Kaggle esta manana.
Dos veces el mismo patron en un dia.

## CORRECCION 2 · y esta va contra nuestra ventaja

Escribi: *"nuestras 784 normas departamentales de Tarija no estan en ninguno de esos productos"*.

**Es falso.** `aBOgacion` tiene **79 leyes departamentales**, y al leer su texto:

| departamento | leyes |
|---|---|
| **Tarija** | **36** |
| Santa Cruz | 28 |
| La Paz | 15 |

Con texto completo y estructurado (verificado abriendo `2010/ley-departamental---1.md`, La Paz).

**Nuestra ventaja sigue existiendo, pero es mas chica de lo que dije:**

| | aBOgacion | nosotros |
|---|---|---|
| leyes departamentales de Tarija | 36 | **784** (leyes + resoluciones del pleno) |
| jurisprudencia del TSJ filtrada por Tarija | 0 | **2.862** |
| normas nacionales | **27.210** | 0 |
| hash de procedencia por documento | no | si |
| cola de revision humana declarada | no | si |

La diferencia real es **cobertura y metodo**, no existencia. Decir "nadie lo tiene" era comodo y
era falso.

---

## Lo que esto cambia en la estrategia

1. **Lo que nos falta ya esta disponible y abierto.** 27.210 normas nacionales en markdown, con
   los decretos supremos incluidos. Sumarlas es escribir **un adaptador**, no scrapear por meses.
   Ojo: los **codigos** (Civil, Penal, Familia, Procesal) **no aparecen por nombre** en ese
   corpus; hay 16 archivos tipo `codigo` y ninguno matchea los grandes. Habria que buscarlos por
   contenido o ir a lexivox directo. **NO MEDIDO todavia.**
2. **Lo departamental sigue siendo el hueco, pero hay que medirlo por departamento.** Santa Cruz
   y La Paz ya tienen algo publicado; los otros seis, ni eso.
3. **KRIMA es la oportunidad que nadie toco:** resoluciones de Tribunales Departamentales y
   Juzgados, o sea primera y segunda instancia de Tarija. Ni los comerciales lo publicitan en
   volumen, ni esta en GitHub.
4. **Nuestra ventaja defendible no es el volumen, es el metodo:** procedencia verificable con
   sha256, alcance declarado, cola de revision humana y API pensada para agentes. Un corpus mas
   grande sin eso sirve menos para una IA que no puede inventar.

## NO MEDIDO

- **Si los codigos nacionales estan en `aBOgacion`** bajo otro nombre. Es la medicion siguiente y
  decide si sumamos ese corpus o vamos a lexivox.
- **La licencia de los DATOS de `aBOgacion`.** El README declara GPLv3 "para el software"; los
  textos legales son de dominio publico por naturaleza, pero conviene confirmarlo antes de
  redistribuir.
- **Cuanto tiene KRIMA para Tarija.**
- **Si LeyNova o Lexius tienen algo departamental** sin publicitarlo.
