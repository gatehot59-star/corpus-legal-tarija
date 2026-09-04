#!/usr/bin/env python3
"""Extrae el TITULO REAL de una norma departamental desde su propio texto.

Por que no desde la URL: el titulo de 718 documentos es el slug de descarga de la
Gaceta ("ley departamental 007 2010&start=460"), que no es un titulo. Y en la LD 129
el titulo era el texto del articulo 2, o sea peor: parece un titulo.

El titulo de una ley departamental de Tarija vive en el encabezado, en mayusculas,
entre la firma del gobernador y el TITULO I. Dos formas medidas:

  A) "...ha sancionado la siguiente Ley Departamental:" + BLOQUE EN MAYUSCULAS
  B) sin ese marcador: el bloque en mayusculas que sigue a la linea de la fecha

TRES ESTADOS. Si no encuentra un bloque que pase los filtros, devuelve None y el
documento queda como estaba. Un titulo inventado es peor que un slug feo: el slug
se ve mal y no engana.
"""
import re, unicodedata

# el texto tiene una de estas formulas antes del titulo. "decreta:" sola es la mas
# comun en las leyes viejas y sin ella el extractor devolvia None: la linea DECRETA
# esta en mayusculas y se pegaba al titulo, arruinando el bloque.
MARCADORES = ("sancionado la siguiente", "sancionado la siquiente",
              "promulga la siguiente", "decreta:", "sanciona:")
# el corte usa (\s|$|[\d.:]) y no solo \s porque las lineas llegan sin espacios al
# final: "ARTICULO" pelado no matcheaba y se pegaba al titulo.
CORTES = re.compile(r"^\s*(t[ií]tulo|cap[ií]tulo|art[ií]?[ck]?ulo|exposici[oó]n\s+de\s+motivos|"
                    r"considerando|por\s+tanto|disposicion|secci[oó]n)(\s|$|[\d.:])", re.I)
# ruido del OCR y del membrete que nunca es titulo
# ruido del membrete y del OCR que NUNCA es titulo. El caso que lo obligo: la LD 007
# encabeza con 'LEY N" 007' y 'LEY DE 06 DE NOVIEMBRE DE 2010' en lineas contiguas, y
# sin filtrarlas el extractor devolvia el numero y la fecha como si fueran el titulo.
COMILLAS = "\u00b0\u00ba\u201c\u201d\u2018\u2019\"'`o*?"
RUIDO = re.compile(r"(asamblea\s+legislativa|gobernador|departamental\s+tarija|^tarija$|"
                   r"^ley\s+n?[" + COMILLAS + r"]*\s*\d|"
                   r"^ley\s+(departamental\s+)?(nro?\.?|n[" + COMILLAS + r"]*)\s*\d|"
                   r"^ley\s+de\s+\d|^ley\s+del?\s+\d{1,2}\s+de\s+|"
                   r"^del?\s+\d{1,2}\s+de\s+|^\d{1,2}\s+de\s+\w+\s+de\s+\d|"
                   r"presidente|vicepresidente|secretari|^decreta|^sanciona|^promulga)", re.I)
PALABRAS_TITULO = ("ley", "estatuto", "reglamento")
DESIGNACION = re.compile(r"^ley(\s+departamental)?(\s+transitoria)?\s*"
                         r"(n[" + COMILLAS + r"]*\s*)?\d+\s*(/\s*\d+)?\s*", re.I)

def _sin_tildes(s):
    return "".join(ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn")

def _mayus(linea):
    """La linea es un renglon de titulo en mayusculas? Ignora digitos y signos."""
    letras = [ch for ch in linea if ch.isalpha()]
    if len(letras) < 4:
        return False
    return sum(1 for ch in letras if ch.isupper()) / len(letras) >= 0.85

def extraer(texto, limite=3000):
    cabeza = (texto or "")[:limite]
    lineas = [l.strip(" \t\u201c\u201d\"'*_-") for l in cabeza.split("\n")]
    # arranque: justo despues del marcador si existe, si no desde el principio
    arranque = 0
    plano = _sin_tildes(cabeza).lower()
    for m in MARCADORES:
        i = plano.find(m)
        if i != -1:
            arranque = cabeza[:i].count("\n") + 1
            break
    bloques, actual = [], []
    for l in lineas[arranque:]:
        # una linea vacia NO corta el titulo: el OCR mete blancos entre renglones
        # del mismo encabezado, y cortar ahi devolvia 'LEY DEPARTAMENTAL TRANSITORIA
        # DE ATRIBUCIONES Y' a medio terminar. Lo que corta es una linea que no esta
        # en mayusculas, o un marcador de estructura.
        if not l:
            continue
        if CORTES.match(l):
            if actual:
                bloques.append(actual)
            actual = []
            if bloques:
                break
            continue
        # "LEY N* 043/2012 DESAYUNO ESTUDIANTIL DEPARTAMENTAL" es designacion Y titulo
        # en el mismo renglon: el filtro de ruido la tiraba entera. Se la exime aca y
        # la designacion se recorta despues, sobre el bloque armado.
        trae_titulo = False
        if DESIGNACION.match(l):
            trae_titulo = len(DESIGNACION.sub("", l, count=1).split()) >= 3
        if _mayus(l) and (trae_titulo or not RUIDO.search(l)):
            actual.append(l)
        else:
            if actual:
                bloques.append(actual); actual = []
    if actual:
        bloques.append(actual)
    for b in bloques:
        t = re.sub(r"\s+", " ", " ".join(b)).strip(" .,:;\u201c\u201d\"'")
        # el OCR confunde L inicial con l minuscula: 'lEY DE ORGANIZACiON...'
        t = re.sub(r"^l(EY\b)", r"L\1", t)
        prim = _sin_tildes(t).lower().split()
        if not prim:
            continue
        if prim[0] not in PALABRAS_TITULO:
            continue
        if len(t) < 18 or len(t) > 300:
            continue
        # un titulo tiene al menos 4 palabras: "LEY N 007" no es un titulo
        if len(prim) < 4:
            continue
        # un titulo no es una fecha ni un numero: si sacando digitos y meses no queda
        # nada sustantivo, no es un titulo
        # quita la designacion si adelante viene el titulo de verdad:
        # "LEY N* 043/2012 DESAYUNO ESTUDIANTIL" -> "DESAYUNO ESTUDIANTIL"
        sin_desig = DESIGNACION.sub("", t, count=1).strip(" .,:;-")
        if len(sin_desig.split()) >= 3:
            t = sin_desig
        limpio = re.sub(r"\d+|\b(de|del|la|el|los|las|y|ley|leyes|departamental|"
                        r"transitoria|transitorio|nro|nra|no|n)\b|"
                        r"\b(enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
                        r"septiembre|setiembre|octubre|noviembre|diciembre)\b|[^\w\s]", " ",
                        _sin_tildes(t).lower())
        # si sacando "ley departamental transitoria N 004/2010" no queda nada
        # sustantivo, eso era la DESIGNACION de la norma, no su titulo
        if len(limpio.split()) < 2:
            continue
        return t
    return None
