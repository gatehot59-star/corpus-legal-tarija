# Inventario medido: que existe, que vale, que falta

**Medido el 2026-09-03** sobre la base reconstruida (`bolivia-v2.db`) en `brain-env`, y sobre el
clon local de `strysg/aBOgacion`. Nada de esto viene de memoria: cada numero tiene su consulta.

---

## 1. EL CORPUS que existe

| | |
|---|---|
| documentos canonicos | **3.606** |
| caracteres de texto | **72.089.578** |
| chunks indexados | **56.311** |
| procedencias registradas | **3.646** |
| documentos con varias procedencias | **15** |
| tamano del indice | 154,9 MB |

### Por jurisdiccion y tipo

| jurisdiccion | tipo | documentos | caracteres |
|---|---|---|---|
| jurisprudencia | Auto Supremo | **2.758** | 65.760.861 |
| jurisprudencia | Sentencia | 59 | 2.184.537 |
| jurisprudencia | Resolucion | 5 | 34.853 |
| departamental | Ley Departamental | **402** | 1.691.664 |
| departamental | Resolucion del Pleno | **382** | 2.417.663 |

### Por materia

`Penal 1.273` · `(sin materia) 1.272` · `Civil 623` · `Del Trabajo 281` ·
`Administrativa 73` · `Tributaria 31` · `Familia 31` · `Contenciosa 14` ·
`Seguridad Social 5` · `Internacional 2` · `Comercial 1`

**Los 1.272 sin materia son casi todos los 784 departamentales**: la Gaceta no clasifica por
materia y nadie la infirio. Es un hueco de metadato, no de texto.

### Por sala (jurisprudencia)

`Sala Penal 1.246` · `Sala Civil 647` · `Sala Social 1era 515` · `Sala Social 2da 306` ·
`Sala Plena 49` · `Sala Social 2da Liquidadora 36` · `Sala Penal Liquidadora 23`

### Por gestion

`2015: 345` · `2016: 303` · `2017: 240` · `2018: 235` · `2019: 248` · `2020: 179` ·
`2021: 268` · `2022: 271` · `2023: 160` · `2024: 216` · `2025: 198` · `2026: 159`

**Y `(sin anio): 784`**, o sea los departamentales enteros. El ano existe en el nombre del
archivo y **nunca se normalizo al campo**. Consecuencia concreta: el filtro por ano del frontend
no sirve para la normativa de Tarija.

### Calidad del texto, por via de extraccion

| via | confianza | documentos |
|---|---|---|
| `html_oficial` | **alta** | 2.594 |
| `ocr` | media | 778 |
| `texto_nativo_pdf` | media | 195 |
| `ocr_pdf_escaneado` | media | 33 |
| `ocr` | **revision_humana** | 6 |

**El 72% del corpus es texto oficial, no OCR.** Eso no era obvio y cambia el riesgo: el ruido
de OCR afecta a un cuarto del corpus, no a todo.

### Vigencia

```plain
vigente = NULL  ->  3.606 documentos  (100%)
```

**Cero documentos con vigencia verificada.** La cola de revision humana tiene **3.606**
`vigencia_no_medida` mas **6** `cita_ambigua`. El sistema no miente (declara `null` = NO MEDIDO),
pero tampoco responde la pregunta que un abogado hace primero.

---

## 2. EL SISTEMA que existe

### `sistema/api/` — backend

| archivo | que es |
|---|---|
| `esquema.sql` | jurisdiccion / departamento / organo / tipo, chunks FTS5, cola de revision |
| `ingesta.py` | ingesta generica por adaptadores, uid con hash, invariante de no-perdida |
| `alias.py` | procedencias: una tabla, unicidad por fuente+url+archivo+hash, auditoria |
| `servidor.py` | API 1.1.0, 11 rutas, solo biblioteca estandar |
| `frontera.py` | limite por IP, token, cabeceras, log sin la consulta |

### `sistema/web/index.html` — frontend

Un archivo, 21.055 bytes, cero build. Lenguaje visual del expediente; el sello estampa **todas**
las procedencias con tres estados (varias / una / NO MEDIDO). Medido en un navegador real.

### Tests

| suite | casos |
|---|---|
| `test_api.py` (por HTTP) | **45** |
| `test_frontera.py` (por HTTP) | **17** |
| `test_ingesta.py` | 8 |
| `test_procedencias.py` | 6 |
| `test_alias.py` | 5 |
| `pipeline/test_*.py` | 4 archivos |

**36 unitarios + 45 de contrato, todos verdes.** Dos son de **sabotaje**: uno rompe el registro de
procedencia y exige ROJO, otro borra la tabla y exige `null`. Un guard que no puede dar rojo no
mide nada.

### `pipeline/` — lo que construye el corpus

16 archivos: `ocr_masivo.py`, `gate_v2.py`, `normalizar_citas.py`, `genesis_bajar.py`,
`indexar_fts.py`, `consolidar.py`, `datos_juridicos.py`, `reintentar_rotados.py`, `buscar.py`,
`resumir.py`, `regatear.py` y sus falsadores.

---

## 3. QUE VALE, sin inflarlo

**Lo unico de verdad: las 784 normas departamentales de Tarija** con texto completo, sha256 y URL
oficial. Los competidores **declaran por escrito** que no cubren lo departamental (LeyNova,
SILEG, Difusion Juridica, y el README de `Bolivian-law-mcp`). Eso no esta en ningun producto.

**Segundo: 2.822 resoluciones del TSJ filtradas por Tarija**, con procedencia verificable. Los
comerciales tienen mas volumen nacional; lo de Tarija con hash y URL por documento, no.

**Tercero, y es lo que escala: la arquitectura.** Sumar una fuente es un adaptador de ~30 lineas;
el uid, los chunks, la procedencia y la cola de revision son comunes. Los filtros y el alcance
salen de la base, asi que el dia que entre La Paz aparece sola.

**Cuarto: el corpus es abierto y auditable.** Cada documento con su hash y su fuente; el pipeline
entero se puede correr de nuevo. Los comerciales son cajas cerradas por suscripcion y **no pueden
copiar esto sin dejar de ser lo que son**.

**Lo que NO vale como diferencial:** el volumen nacional. Ahi somos chicos contra 25 anos de
SILEG y contra 163.000 extractos con control de vigencia.

---

## 4. QUE FALTA, ordenado por cuanto duele

### 4.1 Vigencia y derogaciones — el agujero mas caro

**3.606 de 3.606 sin medir.** El campo existe, la API lo declara honestamente y nadie lo lleno.
Un abogado pregunta "esto sigue vigente" antes que cualquier otra cosa. Necesita: tabla de
derogaciones, deteccion de "se deroga la Ley X" en el texto, y revision humana de lo dudoso.

### 4.2 Lo nacional — y aca corrijo un error mio de esta manana

Esta manana escribi que faltaban **dos codigos principales y la Ley General del Trabajo**.
**Es falso y lo mido:** el clon de `aBOgacion` tiene **27.208 normas normalizadas, 1826-2026**
(178 anos), y los codigos **estan**:

| norma | archivo | articulos |
|---|---|---|
| Constitucion Politica del Estado 2009 | `2009/constitucion-politica-del-estado---20090207.md` | **416** |
| Codigo de Comercio (DL 14379/1977) | `1977/codigo---14379.md` | **1.842** |
| Codigo Civil (DL 12760/1975) | `1975/codigo---12760b.md` | **1.642** |
| Codigo de Procedimiento Civil (DL 12760/1975) | `1975/codigo---12760a.md` | 946 |
| Codigo Penal (DL 10426/1972) | `1972/codigo---10426.md` | — |
| Codigo Tributario (Ley 2492/2003) | `2003/codigo---2492.md` | 284 |
| Codigo de Familia (1972) | `1972/codigo-de-familia.md` | — |
| Codigo de Seguridad Social (1956) | `1956/codigo---19561214.md` | 393 |
| Ley General del Trabajo (1942) | `1942/codigo-del-trabajo.md` | **90** |
| Ley 025 del Organo Judicial | `2010/ley---25.md` | 271 |
| Ley 031 Marco de Autonomias | `2010/ley---31.md` | 301 |
| Ley 548 Codigo Nina, Nino y Adolescente | `2014/ley---548.md` | 373 |
| Ley 348 | `2013/ley---348.md` | — |
| Ley 1178 SAFCO | `1990/ley---1178.md` | — |

**Y casi me equivoco dos veces mas en la misma medicion:** busque `ley---025` y `ley---031` y me
dieron vacio. **El repo no escribe los ceros a la izquierda**: son `ley---25.md` y `ley---31.md`.
Buscar por el nombre que uno espera, y no por el que la fuente usa, produce un "no existe" falso
con tono seguro.

**Lo que falta de verdad, medido por ausencia en el listado ordenado (esta `1969`, esta `1971`,
`1970` no):**

- **Codigo de Procedimiento Penal (Ley 1970 de 1999): AUSENTE.** Para un estudio que litiga en
  penal es de los mas usados, y el corpus tiene 1.273 documentos de materia Penal que lo citan.
- **La Ley General del Trabajo esta con 90 articulos y 28,7 KB.** El texto base esta; sus
  decretos reglamentarios y modificaciones **no estan verificados**. NO MEDIDO si eso alcanza.
- **`aBOgacion` no tiene archivo de licencia.** Su README dice que los datos salen de
  **lexivox.org** y de la Gaceta Oficial. Redistribuir sin licencia declarada es un riesgo, asi
  que lo correcto es **usarlo como indice y bajar de la fuente oficial**, no republicar su copia.

### 4.3 Jurisprudencia que no tenemos

- **Tribunal Constitucional Plurinacional**: cero sentencias constitucionales. Medido en su
  momento que su buscador existe; **no integrado**.
- **KRIMA** (Tribunales Departamentales y Juzgados): cero. Es la unica fuente que llega por
  debajo del Supremo, o sea a lo que un estudio de Tarija litiga todos los dias.
- **Autos de Vista de Tarija**: cero.

### 4.4 Normativa que no tenemos

- **Municipal**: cero. Tarija, Yacuiba, Villa Montes, Bermejo. Nadie lo tiene tampoco: es el
  segundo hueco de mercado.
- **Ejecutivo departamental**: cero decretos y reglamentos. El corpus solo tiene el Legislativo.
- **Los otros ocho departamentos**: cero.

### 4.5 Sistema

- **Ano no normalizado** en los 784 departamentales: el filtro no sirve para ellos.
- **Materia no inferida** en 1.272 documentos.
- **Busqueda semantica / hibrida**: los embeddings estan **medidos y viables** (MiniLM, 384
  dimensiones, discrimina 0,82 vs 0,02) y proyectan **19,63 h** en el Celeron. Sin correr.
- **Servidor MCP nativo**: hay manifiesto y OpenAPI, que ya alcanzan para un agente HTTP. Un MCP
  de verdad **no existe**.
- **Despliegue**: runbook escrito (Caddy, systemd, respaldo, healthcheck) y **nada ejecutado**.
  Sin hosting decidido, el sistema vive en el taller.
- **Movil**: el CSS tiene su media query y **no se probo**.
- **Actualizacion automatica**: no hay. Cada gestion nueva se baja a mano.

### 4.6 Lo que ningun test reemplaza

- **Benchmark juridico con un abogado**: que el buscador encuentre y no invente esta medido; que
  el primer resultado sea el mas util para un caso real **no**.
- **Que alguien del estudio lo use una semana.**

---

## 5. NO MEDIDO en este mismo inventario

- **No verifique norma por norma** el contenido de las 27.208 de `aBOgacion`: mire nombres,
  tamanos, primeras lineas y conteo de articulos de los principales.
- **No revise si esos textos estan actualizados** con sus modificaciones posteriores. Un Codigo
  Civil de 1975 sin sus reformas es una trampa peor que no tenerlo.
- **No busque el CPP por vias alternativas** (LexiVox directo, Gaceta): esta declarado ausente
  **en `aBOgacion`**, no en el mundo.
- **No medi el volumen del TCP ni de KRIMA** hoy. Los numeros de la competencia son
  autodeclarados en su propio marketing.
- **No medi cuanto tarda** integrar lo nacional de punta a punta. El adaptador es chico; la
  verificacion de procedencia de 27.208 documentos no.
