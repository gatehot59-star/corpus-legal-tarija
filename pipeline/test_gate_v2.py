"""Falsador del gate v2: tiene que aprobar los OCR buenos MEDIDOS y rechazar sopa.

Un gate que solo se prueba con texto bueno aprueba todo, y un gate que aprueba todo no es
un gate. Los casos buenos son texto real de la corrida; los malos, sopa construida.

Las rutas de los casos buenos son opcionales: si el texto no esta en la maquina donde corre
el test, el caso se omite y se dice. Un test que se salta en silencio es un cero disfrazado.
"""
import random
from pathlib import Path

import gate_v2

fallos = []
omitidos = []


def esperar(nombre, paginas, esperado):
    r = gate_v2.evaluar(paginas)
    ok = r["veredicto"] == esperado
    print(("VERDE " if ok else "ROJO  ")
          + f"{nombre}: {r['veredicto']} ({r['paginas_ok']}/{r['paginas']} pag ok, "
            f"{r['anclas_legales']} anclas)"
          + ("" if ok else f"  ESPERADO {esperado}; motivo: {r['motivo']}"))
    if not ok:
        fallos.append(nombre)
    return r


# BUENOS: texto real de OCR que se leyo y esta bien.
BUENOS = [
    ("/workspace/ab007/val/texto/tarija_leyes-336-ba4b71c7.txt", "Ley 336 (la que el v1 rechazo)"),
    ("/workspace/ab007/val/texto/tarija_leyes-142-21597dc5.txt", "Ley 142"),
    ("/workspace/wt-ocr/docs/agents/corpus-legal-tarija/ab-ocr/resultados/tesseract/texto_tesseract_psm3.txt",
     "Ley 007 psm3 (38/40 datos juridicos)"),
]
for ruta, nombre in BUENOS:
    p = Path(ruta)
    if not p.exists():
        omitidos.append(nombre)
        print("OMITIDO (no esta en esta maquina): " + nombre)
        continue
    crudo = p.read_text(encoding="utf-8", errors="replace")
    esperar(nombre, crudo.split("\f") if "\f" in crudo else [crudo], "APTO")

# Un buen caso que viaja con el test, para que el falsador nunca quede vacio.
esperar("ley sustantiva sintetica (poco lexico legal, castellano perfecto)",
        ["LEY DEPARTAMENTAL DE FOMENTO A LA PRODUCCION DE SEMILLAS. Articulo 1. El objeto "
         "de la presente norma es la recuperacion de ecotipos locales, el incentivo y "
         "fomento a la produccion y uso de semillas de calidad debidamente certificadas, "
         "para promover el desarrollo agropecuario del departamento, garantizando metodos "
         "convencionales y promoviendo la recuperacion de practicas ancestrales de los "
         "productores campesinos e indigenas de las once secciones de provincia."],
        "APTO")

# MALOS: sopa de OCR fallido.
random.seed(7)
esperar("sopa de simbolos",
        ["".join(random.choice("~|<>{}\\^_") for _ in range(2000))],
        "REVISION_HUMANA")
esperar("palabras sin vocales",
        [" ".join("".join(random.choice("bcdfghjklmnpqrstvwxz") for _ in range(6))
                 for _ in range(300))],
        "REVISION_HUMANA")
esperar("pagina casi vacia", ["Ley\n\nArticulo"], "REVISION_HUMANA")
esperar("castellano perfecto pero no es una norma",
        ["La receta lleva harina, huevos y manteca. Se mezcla todo con cuidado y se hornea "
         "durante cuarenta minutos a temperatura media hasta que la masa quede dorada por "
         "arriba y firme por abajo, momento en el cual conviene dejarla enfriar un rato "
         "largo sobre una rejilla antes de cortarla en porciones parejas."],
        "REVISION_HUMANA")

print()
if omitidos:
    print("casos omitidos por falta de texto local: " + ", ".join(omitidos))
if fallos:
    print("ROJO: fallaron " + ", ".join(fallos))
    raise SystemExit(1)
print("VERDE: el gate v2 aprueba los OCR buenos y rechaza la sopa")
