"""Normalizacion de metadatos de la Gaceta de Tarija: el anio, y el tipo de unidad.

**Por que NO se lee el anio del nombre de archivo.** Un auditor externo propuso justamente eso,
como "fix de una tarde con un regex". Medido sobre los 784: **16 de 784 matchean, y los 16 son
falsos positivos del hash hexadecimal del uid**:

```plain
tarija_leyes-047-a5771928.txt -> "1928"
tarija_leyes-200-2c1a2054.txt -> "2054"   <- ano futuro
tarija_leyes-269-8d190942.txt -> "1909"
```

Ese fix habria escrito 16 anos inventados en un corpus legal (uno en el futuro) y habria dejado
los otros 768 vacios igual. **Un fix que produce datos falsos es peor que el hueco**, porque el
hueco se ve y el dato falso no. Por eso esta funcion **ignora el nombre de archivo por diseno** y
hay un test que lo exige.

**Donde SI esta el anio: en el titulo, 754 de 784 (96%).** Con dos formas distintas medidas:

```plain
"ley departamental 142 2016&start=360"              -> un anio, el de la norma
"r p a n 074 2021 2022 aprobar la resolucion..."    -> DOS anios: es la GESTION legislativa
```

Las RPA llevan la gestion (2021-2022), que no es el ano de la norma sino el periodo. Se guarda el
ano de **inicio** de la gestion y la gestion completa aparte, porque colapsarlos pierde el dato y
inventar un ano exacto que la fuente no da seria peor.

**Y el hallazgo que aparecio midiendo esto: 39 de los 784 NO son una norma.** Son compilados:

```plain
"resoluciones del pleno de la asamblea 141 al 177 del 2014 2015"   52.290 caracteres
"resoluciones del pleno de la asamblea 1 al 35 del 2013 2014"      66.662 caracteres
```

Sumando los rangos: **1.315 resoluciones estan adentro de esos 39 archivos**, sin numero propio y
sin poder citarse una por una. Eso significa dos cosas a la vez: el corpus departamental es **mas
grande** de lo que el inventario decia (402 leyes + 343 RPA sueltas + ~1.315 dentro de compilados),
y **una parte no es citable como norma individual**. Un agente que cite uno de esos archivos esta
citando "las resoluciones 141 al 177" como si fueran una.

Esta funcion **no parte los compilados**: los marca. Partirlos es un extractor aparte, con su
propia verificacion, y hacerlo a ciegas mezclaria resoluciones.
"""
from __future__ import annotations

import re

# Ventana defendible: la Asamblea Legislativa Departamental existe desde 2010, y el corpus llega
# a 2026. Se acepta desde 1990 para no descartar una norma citada de antes, y se RECHAZA el
# futuro: un ano mayor al maximo es un error de extraccion, no un dato.
ANIO_MINIMO = 1990
ANIO_MAXIMO = 2030

_RX_RUIDO = re.compile("&start=[0-9]+")
_RX_ANIO = re.compile("(?<![0-9])(19[0-9]{2}|20[0-9]{2})(?![0-9])")
_RX_COMPILADO = re.compile(
    "resoluciones del pleno de la asamblea[ ]+([0-9]+)[ ]+al[ ]+([0-9]+)", re.I)


def limpiar_titulo(titulo: str) -> str:
    """Saca el ruido del scraping. `&start=360` es paginacion de la Gaceta, no contenido."""
    return _RX_RUIDO.sub(" ", str(titulo or "")).strip()


def anios_de(titulo: str) -> list:
    """Todos los anos plausibles del titulo, en orden de aparicion y sin duplicados."""
    vistos, salida = set(), []
    for a in _RX_ANIO.findall(limpiar_titulo(titulo)):
        n = int(a)
        if ANIO_MINIMO <= n <= ANIO_MAXIMO and a not in vistos:
            vistos.add(a)
            salida.append(a)
    return salida


def compilado_de(titulo: str) -> dict | None:
    """Si el titulo describe un rango de resoluciones, devuelve el rango y cuantas contiene.

    Devuelve None cuando es una norma individual. El llamador decide que hacer; lo que NO puede
    hacer es tratarlo como una norma citable.
    """
    m = _RX_COMPILADO.search(limpiar_titulo(titulo))
    if not m:
        return None
    desde, hasta = int(m.group(1)), int(m.group(2))
    if hasta < desde:
        return {"desde": desde, "hasta": hasta, "contiene": None,
                "advertencia": "rango invertido en la fuente: NO MEDIDO cuantas contiene"}
    return {"desde": desde, "hasta": hasta, "contiene": hasta - desde + 1}


def metadatos_de(titulo: str) -> dict:
    """Anio, gestion y unidad documental a partir del titulo. Nunca del nombre de archivo.

    `anio` queda en `""` cuando la fuente no lo da: vacio es NO MEDIDO y es la respuesta correcta.
    Inventar un ano probable en un corpus legal es exactamente el error que este modulo evita.
    """
    t = limpiar_titulo(titulo)
    anios = anios_de(t)
    comp = compilado_de(t)
    unidad = "compilado" if comp else "norma"

    # Dos anos = gestion legislativa ("r p a n 074 2021 2022"). Se guarda el inicio como anio y
    # la gestion textual aparte: colapsarla pierde informacion que la fuente si da.
    if len(anios) >= 2:
        return {"anio": anios[0], "gestion": anios[0] + "-" + anios[1], "unidad": unidad,
                "compilado": comp, "fuente_del_anio": "titulo:gestion"}
    if len(anios) == 1:
        return {"anio": anios[0], "gestion": "", "unidad": unidad,
                "compilado": comp, "fuente_del_anio": "titulo"}
    return {"anio": "", "gestion": "", "unidad": unidad, "compilado": comp,
            "fuente_del_anio": "NO MEDIDO: el titulo no trae anio"}
