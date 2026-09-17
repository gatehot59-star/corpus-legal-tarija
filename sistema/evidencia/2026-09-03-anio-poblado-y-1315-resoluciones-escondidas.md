# Evidencia cruda: el año poblado, y 1.315 resoluciones escondidas

**2026-09-03.** Máquina: `brain-env` (gateway MUDH, servicio `build`). Commit `c372c28`.

Verbatim. El veredicto va aparte al final.

---

## 1. Por qué NO se lee el año del nombre de archivo

El auditor propuso un regex sobre el nombre. Medido antes de escribir nada:

```plain
departamentales: 784
con anio extraible del nombre: 16 de 784
  tarija_leyes-047-a5771928.txt -> 1928
  tarija_leyes-200-2c1a2054.txt -> 2054      <- futuro
  tarija_leyes-269-8d190942.txt -> 1909
  tarija_leyes-106-7811932f.txt -> 1932
  tarija_leyes-226-1959667d.txt -> 1959
```

Los 16 son el **hash hexadecimal del uid**. Ese fix escribía 16 años inventados y dejaba 768
vacíos. Queda como test: `test_el_hash_nunca_es_un_anio` da ROJO si alguien vuelve a intentarlo.

---

## 2. Dónde sí está: el título

```plain
campos con un anio dentro: {'titulo': 754, 'archivo_texto': 16, 'sha256_real': 141, ...}

  'titulo': 'ley departamental 142 2016&start=360'
  'titulo': 'r p a n 074 2021 2022 aprobar la resolucion de distincion con insignia'
```

Dos formas: la ley trae **un** año; la RPA trae **dos**, que son la gestión legislativa. Se guarda
el inicio como `anio` y la gestión aparte, porque colapsarlas pierde un dato que la fuente sí da.

---

## 3. El hallazgo que apareció midiendo eso: 39 archivos no son una norma

```plain
{'ley_departamental': 402, 'RPA_individual': 343, 'COMPILADO_de_varias_RPA': 39}

  chars: 66662 | resoluciones del pleno de la asamblea 1 al 35 del 2013 2014
  chars: 61270 | resoluciones del pleno de la asamblea 291 al 324 del 2012 2013
  chars: 54906 | resoluciones del pleno de la asamblea 71 al 104 del 2012 2013
  chars: 52290 | resoluciones del pleno de la asamblea 141 al 177 del 2014 2015

compilados parseables: 39
resoluciones CONTENIDAS en esos archivos, sumando rangos: 1315
```

**El corpus departamental es más grande de lo que decía el inventario y a la vez menos citable:**
402 leyes + 343 RPA sueltas + **1.315 RPA dentro de 39 archivos sin número propio**. Un abogado que
busque la RPA 145 cae en un archivo de 52.290 caracteres con 37 resoluciones adentro, y un agente
que lo cite está citando "las resoluciones 141 al 177" como si fueran una.

No se parten en este cambio: **se marcan**. Partirlos es un extractor aparte con su propia
verificación; hacerlo a ciegas mezclaría resoluciones.

---

## 4. Tests

```plain
$ python3 -m unittest -v test_normalizar
test_detecta_el_compilado_y_cuenta_lo_que_contiene ... ok
test_el_hash_nunca_es_un_anio ... ok
test_ley_con_un_anio ... ok
test_limpia_la_paginacion_del_scraping ... ok
test_rango_invertido_es_NO_MEDIDO_no_cero ... ok
test_rechaza_anios_imposibles ... ok
test_rpa_con_gestion_de_dos_anios ... ok
test_sin_anio_queda_vacio_y_lo_declara ... ok
test_titulo_vacio_no_explota ... ok
test_una_norma_individual_no_es_compilado ... ok
Ran 10 tests in 0.001s
OK

$ python3 -m unittest test_alias test_ingesta test_procedencias test_normalizar
Ran 29 tests in 2.564s
OK
```

---

## 5. Reconstrucción completa, con el año poblado

```plain
$ python3 ingesta.py --origen /workspace/corpus-todo --db /workspace/bolivia-v3.db
  tarija_gaceta: 784 documentos
  tsj_genesis: 2862 documentos

documentos canonicos: 3606 | chunks: 56311 | procedencias: 3646
por jurisdiccion: {'departamental': 784, 'jurisprudencia': 2822}
cola de revision humana: 3651
segundos: 12.4 | indice: 155.0 MB

VERIFICACION: {"ofrecidos": 3646, "canonicos_nuevos": 3606, "duplicados_por_contenido": 40,
"alias_nuevos": 3646, "sin_rastro": 0, "en_base": 3606, "alias_en_base": 3646,
"documentos_sin_procedencia": 0, "contenidos_con_varias_fuentes": 15, "veredicto": "VERDE"}
```

### El año, antes y después

**Antes: `(sin anio) 784`.** Ahora:

```plain
(sin anio) 30
2010 13 | 2011 33 | 2012 34 | 2013 42 | 2014 26 | 2015  6
2016 66 | 2017 75 | 2018 87 | 2019 30 | 2021 137 | 2022 145
2023  2 | 2024  2 | 2025 56
```

### Y el tipo

```plain
('Ley Departamental', 402)
('Resolucion del Pleno', 343)
('Compilado de Resoluciones del Pleno', 39)

cola: ('cita_ambigua', 6) ('unidad_no_citable', 39) ('vigencia_no_medida', 3606)

dep-tar-compilado-de-sin-numero-2013-0010ab32 | compilado de resoluciones 71 al 109:
   contiene 39 resoluciones que no tienen registro propio
```

---

## 6. Un TERCER hallazgo que el año hizo visible

Con el año poblado aparecen **huecos de cobertura por gestión que antes eran invisibles**:

| año | documentos |
|---|---|
| 2020 | **0** |
| 2023 | **2** |
| 2024 | **2** |
| 2026 | **0** |

Contra 137 en 2021 y 145 en 2022. **Mientras el campo estaba vacío, el corpus parecía completo
2010-2026 y no lo es.** Tres posibilidades y ninguna medida: la Gaceta no publicó esas gestiones,
la descarga las perdió, o el título de esos documentos no trae año. Es la próxima medición, y no
la hago hoy para no afirmar la causa sin verla.

---

## 7. Veredicto derivado (conclusión, no medición)

**VERDE.** El año pasó de 0 a 754 de 784 (96,2%) desde la fuente correcta, con el falso positivo
del hash convertido en test. La reconstrucción sigue sin pérdida (`sin_rastro: 0`).

**Y el paso barato encontró dos cosas más grandes que él mismo:** 1.315 resoluciones sin registro
propio, y cuatro gestiones con cobertura casi nula que el campo vacío escondía. Es el argumento a
favor de hacer los fixes baratos primero: no por lo que arreglan, por lo que destapan.

## 8. NO MEDIDO

- **La causa del hueco de 2020, 2023, 2024 y 2026.** Tres hipótesis, ninguna verificada.
- **Los 30 sin año:** la fuente no lo da en el título. Habría que sacarlo del texto.
- **Partir los 39 compilados** en sus 1.315 resoluciones: marcado, no hecho.
- **La base servida sigue siendo `bolivia-v2.db`.** La nueva es `bolivia-v3.db`; cambiar la ruta
  de producción es decisión de Abraham.
- **Vigencia:** 3.606 sin medir. Este cambio no la toca.
- **El frontend no se volvió a abrir** después de este cambio: el filtro por año ahora debería
  ofrecer 15 opciones para lo departamental, y eso **no está verificado en navegador**.
