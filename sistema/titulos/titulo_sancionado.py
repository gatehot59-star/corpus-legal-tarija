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

Despues del marcador se toma el bloque entre comillas y, si no hay comillas, el
bloque en mayusculas. Si nada pasa los filtros devuelve (None, motivo) y el
documento no se toca: un titulo inventado es peor que un slug feo, porque el slug
se ve mal y no engana.

Devuelve siempre una tupla (titulo_o_None, via).
"""
import re
import unicodedata

COMILLAS = "\u201c\u201d\u2018\u2019\"'"
MARCADORES = ("sanciona:", "decreta:", "sancionado la siguiente",
              "sancionado la siquiente", "promulga la siguiente",
              "sanciona la siguiente", "decreta la siguiente")
CORTES = re.compile(r"^\s*(t[i\u00ed]tulo|cap[i\u00ed]tulo|art[i\u00ed]?[ck]?ulo|considerando|"
                    r"por\s+tanto|por\s+cuanto|disposici[o\u00f3]n|secci[o\u00f3]n|"
                    r"exposici[o\u00f3]n\s+de\s+motivos)(\s|$|[\d.:])", re.I)
# Lo que NUNCA es titulo, aunque venga en mayusculas o entre comillas.
RUIDO = re.compile(
    r"(asamblea\s+legislativa|gobernador|vicegobernador|presidente|secretari|"
    r"^tarija$|^bolivia$|^ley\s+n\S{0,3}\s*\d|^ley\s+de\s+\d|"
    r"^\d{1,2}\s+de\s+\w+\s+de\s+\d{4}|^del?\s+\d{1,2}\s+de\s+|"
    r"^por\s+(cuanto|tanto)|^sanciona|^decreta|^promulga|^remitase|^es\s+dada)",
    re.I)


def sin_tildes(s):
    return "".join(ch for ch in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(ch) != "Mn")


def _mayus(linea):
    letras = [ch for ch in linea if ch.isalpha()]
    if len(letras) < 4:
        return False
    return sum(1 for ch in letras if ch.isupper()) / len(letras) >= 0.85


def _limpia(t):
    return re.sub(r"\s+", " ", t or "").strip(" \t" + COMILLAS + "*_-.,;:")


def _aceptable(t):
    """Filtros duros. Devuelve el titulo limpio o None."""
    t = _limpia(t)
    if not t:
        return None
    if len(t.split()) < 3 or len(t) < 14 or len(t) > 320:
        return None
    if RUIDO.search(sin_tildes(t)):
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
    m = re.search("[" + COMILLAS + "]([^" + COMILLAS + "]{10,320})[" + COMILLAS + "]",
                  resto, re.S)
    if m:
        t = _aceptable(m.group(1))
        if t:
            return t, "entre_comillas"

    # 2) bloque en mayusculas hasta el primer corte de estructura
    bloque = []
    for linea in resto.split("\n"):
        l = linea.strip(" \t" + COMILLAS + "*_-")
        if not l:
            if bloque:
                break
            continue
        if CORTES.match(l):
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
