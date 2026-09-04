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

HISTORIAL DE MIS PROPIOS ERRORES, que es la parte util del archivo:

v1: devolvio 40 aristas y su CONTROL POSITIVO dio 10/10. Igual 18 de las 40
    eran basura. Un control positivo prueba que lo bueno esta, NUNCA que lo malo
    no esta. Tres trampas:
      a) EL DIA DE SANCION SE DISFRAZA DE NUMERO DE LEY. Toda ley cierra con
         "...contrarias a la presente Ley Departamental. Es sancionada a los 28
         dias del mes de noviembre". El patron veia "Ley Departamental" y
         agarraba el 28: la LD 253 abrogaba una "LD 28" inexistente. 13 aristas.
      b) EL MEMBRETE. La LD 129 salia abrogando la "LD 425" porque el pie de
         pagina dice "Calle 15 de Abril N 425 esq. Gral. Trigo". Una direccion.
      c) LA BASURA DEL OCR ROBA DIGITOS. "Ley Departamental I49 204" capturaba
         49 en vez de 204; "bl(2 139" capturaba 2 en vez de 139.

v2: agregue banco negativo con esas frases textuales y exigi un marcador de
    norma (N, W, No...). Aparecieron DOS fallas nuevas, y una era MIA:
      d) El OCR tambien destruye la N: "Ley Departamental ~o 206" no tiene
         marcador reconocible. Exigir marcador perdia abrogaciones expresas.
      e) MI EXPECTATIVA ESTABA MAL. Puse que "Se derogan los articulos 19 y 20
         de la Ley Departamental W 129" debia devolver [19, 20, 129]. Falso:
         19 y 20 son ARTICULOS, no leyes. El parser devolvia [129] y tenia
         razon; el que estaba equivocado era el test. Corregido el test.

v3 (esta): el marcador es OPCIONAL, porque los guardas ya no dependen de el:
    la ventana se corta en el protocolo de cierre (asi el dia de sancion y el
    membrete nunca llegan al matcher) y se rechaza todo numero seguido de
    "dias" o de un mes. La enumeracion SI exige marcador, para no comerse
    numeros de articulo.

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

# La disposicion termina donde arranca el protocolo de cierre. Todo lo que sigue
# (fecha de sancion, remision, membrete, telefonos) NO es disposicion. Este
# corte es el guarda estructural: sin el, ningun patron alcanza.
CORTE = re.compile(
    r"(Es\s+[Ss]ancionad|Remitase|Por\s+tanto|POR\s+TANTO|Reg[ie]strese"
    r"|Calle\s|Telf|Fax|esq\.)", re.I)

MESES = (r"enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre"
         r"|setiembre|octubre|noviembre|diciembre")
# Marcador de norma, tolerante: N, No, W, y la basura que deja el OCR (~o, bl(2,
# I49, N9). Se usa SOLO para la enumeracion, donde hace falta distinguir
# "y N 029" de un numero de articulo suelto.
MARCA = r"(?:N|W|No|Nro|Num)[^\dA-Za-z\n]{0,4}"
# Objetivo principal: el numero va detras de "Ley Departamental", con o sin
# marcador legible. Hasta 10 caracteres no numericos de basura en el medio.
OBJ_DEP = re.compile(
    r"Ley(?:es)?\s+Departamental(?:es)?[^\d\n]{0,10}(\d{1,3})(?!\d)", re.I)
# "Se abroga la Ley N 504 'Ley Departamental Estructura...'"
OBJ_LEY = re.compile(r"\bLey\s+[^\d\n]{0,6}(\d{1,3})(?!\d)", re.I)
OBJ_MAS = re.compile(MARCA + r"\s*(\d{1,3})(?!\d)", re.I)
# Lo que delata a un numero como no-ley: es un dia, o arranca una fecha.
NO_ES_LEY = re.compile(r"^\s*(?:dias?\b|de\s+(?:" + MESES + r")\b)", re.I)

GENERICA = re.compile(
    r"(todas?\s+las?\s+disposicion\w*|cualquier\s+disposici"
    r"|disposicion\w*\s+contrari|normas?\s+contrari|leyes\s+contrari"
    r"|de\s+igual\s+o\s+(?:menor|inferior)\s+jerarquia)", re.I)
PARCIAL = re.compile(
    r"parcial|el\s+articulo|los\s+articulos|el\s+inc|paragrafo|inciso", re.I)
VENTANA = 700

# Pares conocidos por lectura directa del PDF.
CONTROL_POSITIVO = [
    ("500", "129"), ("500", "432"), ("129", "7"), ("520", "500"),
    ("517", "94"), ("519", "29"), ("519", "109"),
    ("523", "504"), ("454", "139"), ("443", "206"), ("432", "129"),
    ("405", "129"), ("276", "151"),
]

# BANCO NEGATIVO: frases textuales del corpus que la v1 leyo como abrogacion.
# Cada una debe devolver CERO objetivos.
CONTROL_NEGATIVO = [
    ("dia de sancion tras clausula generica",
     "Quedan abrogadas y derogadas todas las disposiciones contrarias a la "
     "presente Ley Departamental. Es sancionada a los 28 Dias del mes de "
     "noviembre de 2017 anos, en la Sala de Sesiones"),
    ("dia 01 de julio",
     "Se abrogan y derogan todas las disposiciones contrarias a la presente Ley "
     "Departamental. Es sancionada al 01 dia del mes de julio del ario 2024"),
    ("dia 05 de febrero",
     "Quedan abrogadas y derogadas todas las disposiciones departamentales "
     "contrarias a la presente Ley Departamental. Es sancionada a los 05 dias "
     "del mes de febrero del ano 2020"),
    ("dia 20 de octubre",
     "Quedan abrogadas y derogadas todas las disposiciones departamentales "
     "contrarias a la presente Ley Departamental. Es sancionada a los 20 dias "
     "del mes de octubre del ano 2022"),
    ("membrete con direccion postal",
     "Se abrogan todas las disposiciones contrarias. Calle 15 de Abril N 425 "
     "esq. Gral. Trigo Telf.: 4 6113308 Fax: 4 6113313"),
    ("normas de igual o inferior jerarquia, sin destino",
     "Se derogan y abrogan todas las normas de igual o inferior jerarquia "
     "vigentes que contradigan lo establecido en la presente Ley."),
    ("generica pura, sin ninguna cifra",
     "Se abrogan y derogan todas las leyes contrarias a la presente Ley."),
]

# BANCO POSITIVO: abrogaciones expresas reales, con el marcador tal como el OCR
# lo dejo. El caso de los articulos esta a proposito: debe devolver SOLO la ley.
CONTROL_ARISTA = [
    ("Se abroga la Ley Departamental N 129 de Organizacion", [129]),
    ("Se derogan los articulos 19 y 20 de la Ley Departamental W 129", [129]),
    ("Se abrogan las Leyes Departamentales N 109 y N 029", [29, 109]),
    ("Se abroga la Ley N 504 Estructura de Cargos", [504]),
    ("Se abroga la Ley Departamental ~o 206 de transferencia", [206]),
    ("Se abroga la Ley Departamental N' 094 Departamentalizacion de Carreteras",
     [94]),
]


def limpia(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(x for x in s if not unicodedata.combining(x))
    return re.sub(r"\s+", " ", s).strip()


def recorta(ventana):
    """Deja solo la parte dispositiva: corta en el protocolo de cierre."""
    m = CORTE.search(ventana)
    return ventana[:m.start()] if m else ventana


def _valido(texto, fin):
    """False si lo que sigue al numero lo delata como dia o fecha."""
    return not NO_ES_LEY.match(texto[fin:fin + 22])


def objetivos_de(ventana):
    """Numeros de ley nombrados como objetivo dentro de la parte dispositiva."""
    disp = recorta(ventana)
    nums = []
    for patron in (OBJ_DEP, OBJ_LEY):
        for om in patron.finditer(disp):
            if not _valido(disp, om.end()):
                continue
            nums.append(int(om.group(1)))
            cola = disp[om.end():om.end() + 200]
            corte = re.split(
                r"(?:Se\s+abrog|Se\s+derog|Articulo|ARTICULO|Disposicion)", cola)[0]
            for extra in OBJ_MAS.finditer(corte):
                if _valido(corte, extra.end()):
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
        propio = str(meta["numero"]).lstrip("0")
        vistos = set()
        for m in CLAU.finditer(completo):
            ventana = completo[m.start():m.start() + VENTANA]
            firma = ventana[:120].lower()
            if firma in vistos:
                continue
            vistos.add(firma)
            cita = ventana[:330]
            parcial = bool(PARCIAL.search(ventana[:300]))
            objetivos = [o for o in objetivos_de(ventana) if str(o) != propio]
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


def banco():
    """Banco del instrumento. Sin esto verde, no se mide el corpus."""
    print("=== BANCO NEGATIVO: frases reales que la v1 leyo como abrogacion ===")
    limpio = True
    for nombre, frase in CONTROL_NEGATIVO:
        objs = objetivos_de(limpia(frase))
        ok = not objs
        limpio = limpio and ok
        print("   %-48s -> %-14s %s"
              % (nombre, objs if objs else "sin objetivo", "ok" if ok else "FALLA"))
    print("   BANCO NEGATIVO: %s"
          % ("%d/%d" % (len(CONTROL_NEGATIVO), len(CONTROL_NEGATIVO)) if limpio
             else "HAY FALLAS"))
    print()
    print("=== BANCO POSITIVO: abrogaciones expresas con marcador roto ===")
    todo = True
    for frase, esperado in CONTROL_ARISTA:
        objs = objetivos_de(limpia(frase))
        ok = objs == sorted(esperado)
        todo = todo and ok
        print("   %-62s -> %-14s %s"
              % (frase[:62], objs, "ok" if ok else "FALLA, esperaba %s" % esperado))
    print("   BANCO POSITIVO: %s"
          % ("%d/%d" % (len(CONTROL_ARISTA), len(CONTROL_ARISTA)) if todo
             else "HAY FALLAS"))
    return limpio and todo


def control(aristas):
    print("=== CONTROL sobre el corpus: pares conocidos por lectura directa ===")
    hallados = 0
    for ab, vic in CONTROL_POSITIVO:
        hay = any(a["abrogador"].lstrip("0") == ab and a["abrogada"].lstrip("0") == vic
                  for a in aristas)
        hallados += hay
        print("   LD %-4s abroga LD %-4s -> %s"
              % (ab, vic, "HALLADO" if hay else "NO HALLADO"))
    print("   CONTROL: %d/%d" % (hallados, len(CONTROL_POSITIVO)))
    return hallados == len(CONTROL_POSITIVO)


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


def main():
    if len(sys.argv) < 3:
        print("uso: extrae_grafo_vigencia.py <base.db> <salida.json>")
        return 2
    db, salida = sys.argv[1], sys.argv[2]

    if not banco():
        print()
        print("VEREDICTO: ROJO -> el instrumento no pasa su banco. "
              "No se mide el corpus ni se escribe salida.")
        return 1
    print()

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
        print("VEREDICTO: ROJO -> falta algun par conocido")
        return 1
    print("VEREDICTO: VERDE -> banco y control en verde")
    return 0


if __name__ == "__main__":
    sys.exit(main())
