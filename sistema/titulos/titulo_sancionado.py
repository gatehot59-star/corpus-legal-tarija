#!/usr/bin/env python3
"""Extrae el titulo de una ley departamental desde su FORMULA DE SANCION.

Por que existe otro extractor: el anterior (pipeline/titulos_desde_texto.py) exigia
que el titulo empezara por su especie (ley, estatuto, reglamento). Por eso dejo 64
leyes con el slug de descarga como titulo: devolvio None en las 64, medido. El
criterio era falso para una clase entera de leyes de Tarija, las que nombran su
materia directamente:

    LEY DEPARTAMENTAL N*089
    LA ASAMBLEA LEGISLATIVA DEPARTAMENTAL DE TARIJA
    SANCIONA:
    "PROMOCION DEL RIEGO TECNIFICADO EN EL DEPARTAMENTO DE TARIJA"

Ese es el titulo y no empieza por "ley". El ancla correcta es la formula de sancion,
no la primera palabra del titulo.

CUATRO COSAS QUE CORRIGIO LA LECTURA DE LOS RESULTADOS, y ninguna se veia antes:

1. La LD 006 tiene entre comillas, detras de SANCIONA:, la frase "y el paragrafo II
   del mismo Articulo senala que:". La devolvia como titulo. Un titulo NO arranca en
   minuscula ni con un conector.
2. "ASAMBLEA LEGISLATIVA" no puede ser ruido a secas: la LD 022 se titula "Asamblea
   Legislativa Departamental de Ninas, Ninos y Adolescentes". Es ruido solo cuando la
   linea ES el organo, o sea cuando termina ahi o en "de Tarija".
3. EL APOSTROFO CERRABA EL BLOQUE. Tenia ' y \u2019 en la lista de comillas, asi que
   "SUBGOBERNACION O'CONNOR" se cortaba en "SUBGOBERNACION O". Delimitan solo \u201c
   \u201d y ", nunca el apostrofo: en castellano boliviano aparece en O'Connor, que es
   una provincia entera del departamento.
4. La LD 240 devolvia "Articulo 1. (OBJETO) L Aprobar la Modificacion...": cuerpo de
   articulo disfrazado de titulo, la misma clase de basura que ya arreglamos una vez.

Si nada pasa los filtros devuelve (None, motivo) y el documento no se toca: un titulo
inventado es peor que un slug feo, porque el slug se ve mal y no engana.

Devuelve siempre una tupla (titulo_o_None, via).
"""
import re
import unicodedata

# Delimitadores de bloque citado. SIN apostrofo: ver punto 3 del encabezado.
DELIMITADORES = "\u201c\u201d\""
# Para limpiar bordes si el OCR dejo un apostrofo suelto, ahi si se saca.
BORDES = "\u201c\u201d\u2018\u2019\"'"
MARCADORES = ("sanciona:", "decreta:", "sancionado la siguiente",
              "sancionado la siquiente", "promulga la siguiente",
              "sanciona la siguiente", "decreta la siguiente")
ESTRUCTURA = re.compile(r"^\s*(t[i\u00ed]tulo|cap[i\u00ed]tulo|art[i\u00ed]?[ck]?ulo|art\.|"
                        r"considerando|por\s+tanto|por\s+cuanto|disposici[o\u00f3]n|"
                        r"secci[o\u00f3]n|exposici[o\u00f3]n\s+de\s+motivos)(\s|$|[\d.:])",
                        re.I)
# Lo que NUNCA es titulo, aunque venga en mayusculas o entre comillas.
RUIDO = re.compile(
    r"(^la\s+asamblea\s+legislativa|"
    r"^asamblea\s+legislativa\s+departamental(\s+de\s+tarija)?\s*$|"
    r"gobernador|vicegobernador|presidente|secretari|"
    r"^tarija$|^bolivia$|^ley\s+n\S{0,3}\s*\d|^ley\s+de\s+\d|"
    r"^\d{1,2}\s+de\s+\w+\s+de\s+\d{4}|^del?\s+\d{1,2}\s+de\s+|"
    r"^por\s+(cuanto|tanto)|^sanciona|^decreta|^promulga|^remitase|^es\s+dada)",
    re.I)
# Un titulo no empieza NI TERMINA con un conector o una preposicion suelta.
# Si termina asi, el bloque quedo truncado y no se escribe.
CONECTORES = {"y", "o", "que", "el", "la", "los", "las", "de", "del", "en", "a",
              "al", "con", "por", "para", "se", "su", "sus", "lo", "un", "una",
              "como", "pero", "asimismo", "mismo", "misma", "e", "u", "i", "l"}


def sin_tildes(s):
    return "".join(ch for ch in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(ch) != "Mn")


def _mayus(linea):
    letras = [ch for ch in linea if ch.isalpha()]
    if len(letras) < 4:
        return False
    return sum(1 for ch in letras if ch.isupper()) / len(letras) >= 0.85


def _limpia(t):
    return re.sub(r"\s+", " ", t or "").strip(" \t" + BORDES + "*_-.,;:")


def _aceptable(t):
    """Filtros duros. Devuelve el titulo limpio o None."""
    t = _limpia(t)
    if not t:
        return None
    palabras = t.split()
    if len(palabras) < 3 or len(t) < 14 or len(t) > 320:
        return None
    llano = sin_tildes(t)
    if RUIDO.search(llano) or ESTRUCTURA.match(llano):
        return None
    primera_letra = next((ch for ch in t if ch.isalpha()), "")
    if primera_letra and primera_letra.islower():
        return None
    if sin_tildes(palabras[0]).lower().strip(".,;:") in CONECTORES:
        return None
    # cola colgada: el bloque quedo cortado a mitad de frase
    if sin_tildes(palabras[-1]).lower().strip(".,;:" + BORDES + "()-") in CONECTORES:
        return None
    letras = [ch for ch in t if ch.isalpha()]
    if len(letras) < 12 or len(letras) / len(t) < 0.6:
        return None
    return t


def extraer(texto, limite=2200):
    cabeza = (texto or "")[:limite]
    plano = sin_tildes(cabeza).lower()
    corte = -1
    for marcador in MARCADORES:
        i = plano.find(marcador)
        if i != -1 and (corte == -1 or i + len(marcador) < corte):
            corte = i + len(marcador)
    if corte == -1:
        return None, "sin_formula_de_sancion"
    resto = cabeza[corte:]

    # 1) bloque entre comillas: el caso limpio
    m = re.search("[" + DELIMITADORES + "]([^" + DELIMITADORES + "]{10,320})["
                  + DELIMITADORES + "]", resto, re.S)
    if m:
        t = _aceptable(m.group(1))
        if t:
            return t, "entre_comillas"

    # 2) bloque en mayusculas hasta el primer corte de estructura
    bloque = []
    for linea in resto.split("\n"):
        l = linea.strip(" \t" + BORDES + "*_-")
        if not l:
            if bloque:
                break
            continue
        if ESTRUCTURA.match(l):
            break
        if not _mayus(l) or RUIDO.search(sin_tildes(l)):
            if bloque:
                break
            continue
        bloque.append(l)
    if bloque:
        t = _aceptable(" ".join(bloque))
        if t:
            return t, "bloque_mayusculas"
    return None, "sin_titulo_legible"
