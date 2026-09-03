# Buscador del corpus legal: que hay medido

**Medido el 2026-09-03 en `brain-env`** (Celeron N4020, 2 cores, sin AVX).

## Indice lexico FTS5 + BM25: andando

| | |
|---|---|
| documentos indexados | **3.646** |
| chunks | **57.651** |
| tiempo de construccion | **22,9 s** |
| tamano del indice | 151,1 MB |
| documentos sin metadatos | **0** |
| falsador | **11/11 verde** |

Busquedas reales cronometradas:

```
"prescripcion adquisitiva de dominio"                    -> 3 resultados en 17 ms
"beneficios sociales despido injustificado" (Sala Social) -> 2 resultados en  5 ms
```

Y los resultados son los correctos: la primera trae Autos Supremos de Sala Civil sobre
usucapion (2016, 2018, 2023), la segunda trae Sala Social 1era en materia Del Trabajo con las
partes identificadas.

### Como se usa

```bash
python pipeline/indexar_fts.py --corpus <dir> --salida corpus.db
python pipeline/buscar.py --db corpus.db "prescripcion adquisitiva"
python pipeline/buscar.py --db corpus.db "Art. 17.I" --fuente jurisprudencia_tsj
python pipeline/buscar.py --db corpus.db "casacion" --sala "Sala Penal" --gestion 2024
```

### El indice NO se commitea

151 MB que se regeneran en 23 segundos no son un artefacto, son una cache. Se commitea lo que
lo produce. Ademas GitHub rechaza archivos de mas de 100 MB, asi que ni la tentacion existe.

## Embeddings: medidos, viables, y NO en esta maquina

No estan descartados ni bloqueados. Estan **medidos**:

| | |
|---|---|
| torch en el Celeron sin AVX | **corre** (2.13.0+cpu, matmul 256x256 en 0,108 s) |
| modelo | `paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensiones |
| carga del modelo | 120,7 s la primera vez (458 MB de cache) |
| **velocidad** | **1,226 s por chunk** |
| **proyeccion 57.651 chunks** | **19,63 h de CPU en serie** |

Y discriminan de verdad, que es lo que no se ve mirando que el codigo no tire excepcion:

| par | similitud |
|---|---|
| mismo tema, laboral | **0,820** |
| mismo tema, civil | **0,710** |
| temas distintos | 0,223 |
| sin relacion (penal vs. una receta de cocina) | 0,019 |

Un modelo que devuelve 0,9 para todo pasa cualquier test de humo y no sirve para nada. Este
separa.

**Decision:** los embeddings van a Actions (gratis, 4 vCPU) o a la GPU de Kaggle, en una tanda
aparte. La busqueda lexica no espera por eso, porque contesta otra pregunta y ya funciona.

## Por que lexico primero, y no como consuelo

Un estudio busca "Ley 007", "Art. 17.I", "AS/0122/2026", "prescripcion adquisitiva". Eso es
busqueda **exacta**, y ahi BM25 le gana a la similitud semantica: un embedding puede traer un
fallo parecido en vez del que lleva ese numero. Los embeddings contestan "casos como este", que
es otra pregunta y se suma sin tirar nada de esto.

## Lo que sigue NO MEDIDO

- **La corrida de embeddings completa** y su fusion con BM25 (busqueda hibrida).
- **La calidad de los resultados juzgada por un abogado.** El falsador mide que el buscador
  encuentre y no invente; que el PRIMER resultado sea el mas util para un caso real es un
  juicio profesional que ningun test reemplaza.
- **Interfaz.** Hoy es linea de comandos: sirve para medir, no para que lo use el estudio.
