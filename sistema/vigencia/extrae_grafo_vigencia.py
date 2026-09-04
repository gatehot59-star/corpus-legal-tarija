#!/usr/bin/env python3
"""extrae_grafo_vigencia.py - construye el grafo de abrogaciones desde el lado
del ABROGADOR, no de la victima.

Por que asi y no al reves: una norma NO se entera de su propia muerte. El texto
de la Ley 129 no dice que la Ley 500 la abrogo. Preguntarle a cada ley si esta
vigente devuelve silencio en el 100% de los casos, y ese silencio no es prueba
de vigencia. La unica evidencia posible esta en el texto del que mata.

Separa TRES clases de clausula, porque tratarlas igual es el error caro:

  con_destino  "Se abroga la Ley Departamental N 129"  -> arista real
  generica     "Quedan derogadas todas las disposiciones contrarias"
               -> NO mata a nadie en particular. Contarla como derogacion
                  mataria media biblioteca.
  sin_destino  clausula que no nombra objetivo ni es generica -> NO MEDIDO

Uso:
    python3 extrae_grafo_vigencia.py <base.db> <salida.json>
"""
import collections
import json
import re
import sqlite3
import sys
import unicodedata

CLAU = re.compile(
    r"(se\s+abrog\w*|abrog[ao]se|qued[ao]n?\s+abrogad\w*|se\s+derog\w*"
    r"|derog[ao]se|qued[ao]n?\s+derogad\w*|d[ee]jase\s+sin\s+efecto)", re.I)
OBJ_DEP = re.compile(r"Ley(?:es)?\s+Departamental(?:es)?[^\d\n]{0,30}(\d{1,3})", re.I)
OBJ_MAS = re.compile(r"N[^\d\n]{0,4}(\d{1,3})")
GENERICA = re.compile(
    r"(todas?\s+las?\s+disposicion\w*|cualquier\s+disposici"
    r"|disposicion\w*\s+contrari|normas?\s+contrari)", re.I)
PARCIAL = re.compile(r"parcial|el\s+articulo|los\s+articulos|paragrafo|inciso", re.I)
VENTANA = 700

# Pares que ya conociamos por lectura directa. Si el extractor no los encuentra,
# no sirve y no se escribe nada.
CONTROL_POSITIVO = [
    ("500", "129"), ("500", "432"), ("129", "7"), ("520", "500"),
    ("517", "94"), ("519", "29"), ("519", "109"), ("398", "304"),
    ("523", "504"), ("454", "139"),
]
CONTROL_NEGATIVO = "888"


def limpia(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(x for x in s if not unicodedata.combining(x))
    return re.sub(r"\s+", " ", s).strip()


def carga(db):
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    leyes = {r[0]: {"numero": r[1], "anio": r[2], "titulo": r[3]}
             for r in con.execute(
                 "SELECT uid,numero,anio,titulo FROM documentos WHERE tipo_norma=?",
                 ("Ley Departamental",))}
    # UN barrido de chunks. chunks es FTS5 sin indice por uid: 512 consultas
    # sueltas son 512 barridos completos y el script no termina nunca.
    texto = collections.defaultdict(list)
    for uid, cuerpo in con.execute("SELECT uid,cuerpo FROM chunks"):
        if uid in leyes:
            texto[uid].append(cuerpo)
    return leyes, texto


def objetivos_de(ventana):
    """Numeros de ley departamental nombrados dentro de la clausula."""
    nums = []
    for om in OBJ_DEP.finditer(ventana):
        nums.append(int(om.group(1)))
        # "Leyes Departamentales N 94, N 279 y N 293": la enumeracion sigue
        # despues del primer numero, hasta que arranca otra disposicion.
        cola = ventana[om.end():om.end() + 260]
        corte = re.split(r"(?:Se\s+abrog|Se\s+derog|Articulo|ARTICULO|Disposicion)",
                         cola)[0]
        for extra in OBJ_MAS.finditer(corte):
            nums.append(int(extra.group(1)))
    return sorted(set(n for n in nums if 1 <= n <= 999))


def extrae(leyes, texto):
    aristas, genericas, sin_destino = [], [], []
    cuenta = collections.Counter()
    for uid, meta in leyes.items():
        completo = limpia(" ".join(texto.get(uid, [])))
        if not completo:
            cuenta["SIN_TEXTO"] += 1
            continue
        # Los pasajes se solapan a proposito (ventanas corridas), asi que la
        # misma clausula aparece hasta 5 veces. Se deduplica por firma.
        vistos = set()
        for m in CLAU.finditer(completo):
            ventana = completo[m.start():m.start() + VENTANA]
            firma = ventana[:120].lower()
            if firma in vistos:
                continue
            vistos.add(firma)
            cita = ventana[:330]
            parcial = bool(PARCIAL.search(ventana[:300]))
            objetivos = objetivos_de(ventana)
            if objetivos:
                for obj in objetivos:
                    aristas.append({
                        "abrogador": str(meta["numero"]),
                        "abrogador_anio": meta["anio"],
                        "abrogada": str(obj),
                        "parcial": parcial,
                        "cita": cita,
                        "uid_abrogador": uid,
                    })
            elif GENERICA.search(ventana[:300]):
                genericas.append({"ley": str(meta["numero"]), "anio": meta["anio"],
                                  "cita": cita})
            else:
                sin_destino.append({"ley": str(meta["numero"]), "anio": meta["anio"],
                                    "cita": cita})
    return aristas, genericas, sin_destino, cuenta


def control(aristas):
    print("=== CONTROL POSITIVO: pares ya conocidos por lectura directa ===")
    hallados = 0
    for ab, vic in CONTROL_POSITIVO:
        hay = any(a["abrogador"].lstrip("0") == ab and a["abrogada"].lstrip("0") == vic
                  for a in aristas)
        hallados += hay
        print("   LD %-4s abroga LD %-4s -> %s"
              % (ab, vic, "HALLADO" if hay else "NO HALLADO"))
    print("   CONTROL POSITIVO: %d/%d" % (hallados, len(CONTROL_POSITIVO)))
    victimas = set(a["abrogada"].lstrip("0") for a in aristas)
    neg = CONTROL_NEGATIVO in victimas
    print("=== CONTROL NEGATIVO: LD %s (no existe) nombrada como abrogada: %s"
          " (debe ser False)" % (CONTROL_NEGATIVO, neg))
    return hallados == len(CONTROL_POSITIVO) and not neg


def main():
    if len(sys.argv) < 3:
        print("uso: extrae_grafo_vigencia.py <base.db> <salida.json>")
        return 2
    db, salida = sys.argv[1], sys.argv[2]
    leyes, texto = carga(db)
    print("leyes departamentales: %d | con texto: %d" % (len(leyes), len(texto)))
    aristas, genericas, sin_destino, cuenta = extrae(leyes, texto)
    print()
    print("aristas abrogador->abrogada: %d" % len(aristas))
    print("clausulas GENERICAS (no matan a nadie en particular): %d" % len(genericas))
    print("clausulas SIN DESTINO legible (NO MEDIDO): %d" % len(sin_destino))
    if cuenta:
        print("otros: %s" % dict(cuenta))
    print()
    victimas = collections.Counter(a["abrogada"].lstrip("0") for a in aristas)
    presentes = set(str(v["numero"]).lstrip("0") for v in leyes.values())
    en_corpus = [v for v in victimas if v in presentes]
    print("leyes NOMBRADAS como abrogadas: %d" % len(victimas))
    print("   de esas, presentes en el corpus: %d" % len(en_corpus))
    print("   nombradas pero AUSENTES del corpus: %d"
          % (len(victimas) - len(en_corpus)))
    print()
    verde = control(aristas)
    print()
    json.dump({"aristas": aristas, "genericas": genericas,
               "sin_destino": sin_destino},
              open(salida, "w"), ensure_ascii=False, indent=1)
    print("escrito %s" % salida)
    if not verde:
        print("VEREDICTO: ROJO -> el extractor no pasa sus propios controles")
        return 1
    print("VEREDICTO: VERDE -> controles en verde, grafo utilizable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
