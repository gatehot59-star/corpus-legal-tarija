"""Gate de calidad v2. El v1 estaba MAL y lo agarro su primera corrida real.

Que paso, medido: el v1 exigia >=15% de "lexico legal" por pagina. La Ley Departamental 336
(Fomento a la Produccion de Semillas) salio con un OCR excelente (texto perfectamente
legible, 12.162 caracteres, `Articulo 1. (Objeto)` limpio) y el gate la marco
REVISION_HUMANA en 4 de 4 paginas, con 2,5% a 12,5% de lexico.

La causa no es el OCR: es el instrumento. Una ley SUSTANTIVA habla de su tema (semillas,
ecotipos, certificacion), no repite "ley/asamblea/resolucion". La densidad de lexico legal
mide "que tan boilerplate es el documento", no "que tan bien salio el OCR". Con el v1
puesto, cientos de documentos buenos habrian caido en la cola de revision humana y la cola
habria dejado de significar algo.

El discriminador correcto de un OCR fallido es OTRO: un OCR que fracasa no produce texto
tematicamente distinto, produce **sopa de caracteres**. Asi que se mide eso:

  1. volumen: caracteres por pagina.
  2. basura: proporcion de caracteres que no son letra, digito, espacio ni puntuacion
     normal. Un escaneo mal leido se llena de simbolos y cajas.
  3. plausibilidad lexica: proporcion de palabras de 3+ letras que tienen al menos una
     vocal. El castellano real esta cerca del 100%; la sopa de OCR, muy abajo.
  4. ancla legal a nivel DOCUMENTO, no de pagina: una norma dice "ley", "articulo",
     "resolucion" o "asamblea" en algun lado. Basta que aparezca, no que abunde.

El paso 4 es el que corrige el error de categoria del v1: el ancla es una condicion de
"esto es un documento legal", y se pregunta una vez por documento, no pagina por pagina.
"""
import re
import unicodedata

VOCALES = set("aeiou")
ANCLAS = re.compile(r"\b(ley|articulo|resolucion|asamblea|decreto|departamental)\b")
# Puntuacion que SI aparece en un documento legal bien leido.
PUNTUACION_OK = set(" \n\r\t.,;:()[]-/%\"'?!$&+*=#@")

UMBRAL_CHARS = 120
UMBRAL_BASURA = 0.25
UMBRAL_PLAUSIBLES = 0.80
UMBRAL_PAGINAS_OK = 0.50


def plano(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower()


def medir_pagina(texto: str) -> dict:
    p = plano(texto)
    utiles = [c for c in p if not c.isspace()]
    basura = sum(1 for c in utiles if not (c.isalnum() or c in PUNTUACION_OK))
    pct_basura = basura / len(utiles) if utiles else 1.0

    palabras = re.findall(r"[a-z]{3,}", p)
    con_vocal = sum(1 for w in palabras if any(v in w for v in VOCALES))
    pct_plausibles = con_vocal / len(palabras) if palabras else 0.0

    ok = (len(texto) >= UMBRAL_CHARS
          and pct_basura <= UMBRAL_BASURA
          and pct_plausibles >= UMBRAL_PLAUSIBLES)
    return {"chars": len(texto), "palabras": len(palabras),
            "pct_basura": round(100 * pct_basura, 1),
            "pct_palabras_plausibles": round(100 * pct_plausibles, 1),
            "ok": ok}


def evaluar(paginas: list) -> dict:
    """paginas = lista de textos, una por pagina. Devuelve el veredicto del documento."""
    filas = [dict(medir_pagina(t), pagina=i) for i, t in enumerate(paginas, start=1)]
    buenas = sum(1 for f in filas if f["ok"])
    total = len(filas) or 1
    completo = plano("\n".join(paginas))
    anclas = len(ANCLAS.findall(completo))

    motivos = []
    if buenas / total < UMBRAL_PAGINAS_OK:
        motivos.append(f"solo {buenas}/{total} paginas pasan volumen/basura/plausibilidad")
    if anclas < 1:
        motivos.append("ninguna ancla legal en todo el documento: puede no ser una norma")

    return {"paginas": len(filas), "paginas_ok": buenas,
            "pct_paginas_ok": round(100.0 * buenas / total, 1),
            "anclas_legales": anclas,
            "veredicto": "APTO" if not motivos else "REVISION_HUMANA",
            "motivo": "; ".join(motivos),
            "detalle": filas}
