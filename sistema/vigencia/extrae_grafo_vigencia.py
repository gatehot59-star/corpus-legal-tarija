#!/usr/bin/env python3
"""extrae_grafo_vigencia.py - construye el grafo de abrogaciones desde el lado
del ABROGADOR, no de la victima.

Por que asi y no al reves: una norma NO se entera de su propia muerte. El texto
de la Ley 129 no dice que la Ley 500 la abrogo. Preguntarle a cada ley si esta
vigente devuelve silencio en el 100% de los casos, y ese silencio no es prueba
de vigencia. La unica evidencia posible esta en el texto del que mata.

CLASES DE CLAUSULA (tratarlas igual es el error caro):

  con_destino  "Se abroga la Ley Departamental N 129"  -> arista real
  generica     "Quedan derogadas todas las disposiciones contrarias"
               -> NO mata a nadie en particular
  excepcion    "...contrarias, CON EXCEPCION de la Disposicion Transitoria
               Primera de la Ley Departamental N 304" -> la ley nombrada es la
               EXCLUIDA, no la matada. Leerla como victima invierte el sentido
  sin_destino  clausula sin objetivo ni formula generica -> NO MEDIDO

HISTORIAL DE MIS PROPIOS ERRORES, que es la parte util del archivo. Seis
versiones, y CADA UNA pasaba sus controles del momento:

v1  40 aristas, CONTROL POSITIVO 10/10, y 18 de las 40 eran basura. Un control
    positivo prueba que lo bueno esta, NUNCA que lo malo no esta.
      a) EL DIA DE SANCION SE DISFRAZA DE NUMERO DE LEY: "...contrarias a la
         presente Ley Departamental. Es sancionada a los 28 dias del mes de
         noviembre" -> la LD 253 abrogaba una "LD 28" inexistente. 13 aristas.
      b) EL MEMBRETE: la LD 129 abrogaba la "LD 425" porque el pie de pagina dice
         "Calle 15 de Abril N 425 esq. Gral. Trigo". Una direccion postal.
v2  banco negativo con esas frases + marcador obligatorio. Dos fallas nuevas, y
    una era MIA:
      c) El OCR tambien destruye la N: "Ley Departamental ~o 206". Exigir
         marcador SIEMPRE perdia abrogaciones expresas.
      d) MI EXPECTATIVA ESTABA MAL: puse que "Se derogan los articulos 19 y 20 de
         la Ley Departamental W 129" debia dar [19, 20, 129]. Falso: 19 y 20 son
         ARTICULOS. El parser daba [129] y tenia razon. Corregi el test.
v3  30 aristas. Al leerlas una por una, cuatro seguian mal:
      e) NUMERO CORTADO POR EL BORDE DE LA VENTANA: "N* 504" truncado a "N* 5"
         entregaba una "LD 5". El (?!\\d) no protege cuando la cadena termina.
      f) EL MARCADOR CON DIGITOS ROBA EL NUMERO: "Ley Departamental I49 204"
         daba 49; "bl(2 139" daba 2. La basura del OCR va ANTES del numero real,
         asi que dentro de la ventana del ancla hay que tomar el ULTIMO.
      g) LA CLAUSULA DE EXCEPCION LEIDA AL REVES: la LD 398 abroga lo contrario
         "con excepcion de la Disposicion Transitoria Primera de la LD 304".
         La 304 es la EXCLUIDA. La v3 la anotaba como abrogada, y ese par ya
         estaba escrito en la base como derogacion.
      h) "Se deroga el Art. 2 de la Ley 438" salia TOTAL porque el detector de
         parcialidad no conocia la abreviatura "Art.".
v4  guarda de truncado demasiado duro: rechazaba CUALQUIER numero al final de la
    cadena, aunque la frase estuviera completa. El truncado es un problema del
    BORDE DE LA VENTANA, no del texto.
v5  29 aristas, banco 18/18, y TRES seguian mal, todas por el ancla suelta:
      i) "a la presente Ley. 1111 r Jr II lIU1 ll" -> ruido de OCR leido como
         "LD 1".
      j) "Ley de Organiza-:1on del EJecutivo" -> el OCR convirtio "cion" en
         ":1on" y salio otra "LD 1". El ancla estaba dentro del TITULO citado,
         no de una referencia numerada.
      k) "y la Ley 483 478 Departamental" -> texto destruido; elegir el ultimo
         (478) es adivinar. Mejor NO MEDIDO.
v6  (esta) DOS clases de ancla: "Ley Departamental" admite marcador ilegible
    (ahi es donde el OCR lo come), pero el ancla suelta "Ley" EXIGE marcador.
    Un titulo citado no tiene marcador, y el ruido tampoco.

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
# (fecha de sancion, remision, membrete, telefonos) NO es disposicion. Guarda
# estructural: sin el, ningun patron alcanza.
CORTE = re.compile(
    r"(Es\s+[Ss]ancionad|Es\s+sFinc|Remitase|Por\s+tanto|POR\s+TANTO"
    r"|Reg[ie]strese|Calle\s|Telf|Fax|esq\.)", re.I)

MESES = (r"enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre"
         r"|setiembre|octubre|noviembre|diciembre")
# Dos clases de ancla, con exigencias distintas. Ver v6 en el historial.
ANCLA_DEP = re.compile(r"Ley(?:es)?\s+Departamental(?:es)?", re.I)
ANCLA_LEY = re.compile(r"\bLey(?:es)?\b", re.I)
VENTANA_ANCLA = 22
NUM = re.compile(r"(\d{1,3})(?!\d)")
MARCA = r"(?:N|W|No|Nro|Num)[^\dA-Za-z\n]{0,4}"
MARCA_NUM = re.compile(MARCA + r"\s*(\d{1,3})(?!\d)", re.I)
# Lo que delata a un numero como no-ley: es un dia, o arranca una fecha.
NO_ES_LEY = re.compile(r"^\s*(?:dias?\b|de\s+(?:" + MESES + r")\b)", re.I)
# Si esto aparece justo antes del ancla, la ley nombrada es la EXCLUIDA.
EXCEPCION = re.compile(r"(con\s+excepcion|salvo|excepto|a\s+excepcion)", re.I)

GENERICA = re.compile(
    r"(todas?\s+las?\s+disposicion\w*|cualquier\s+disposici"
    r"|disposicion\w*\s+contrari|normas?\s+contrari|leyes\s+contrari"
    r"|normas?\s+juridicas\s+que\s+sean\s+contrari"
    r"|de\s+igual\s+o\s+(?:menor|inferior)\s+jerarquia)", re.I)
PARCIAL = re.compile(
    r"parcial|el\s+articulo|los\s+articulos|el\s+art\.|los\s+art\."
    r"|\bart\.\s*\d|el\s+inc|paragrafo|inciso", re.I)
VENTANA = 700

# Pares conocidos por lectura directa del PDF.
CONTROL_POSITIVO = [
    ("500", "129"), ("500", "432"), ("129", "7"), ("520", "500"),
    ("517", "94"), ("519", "29"), ("519", "109"),
    ("523", "504"), ("454", "139"), ("443", "206"), ("432", "129"),
    ("405", "129"), ("276", "151"), ("444", "438"), ("523", "505"),
    ("454", "202"), ("517", "279"),
]

# BANCO NEGATIVO: frases textuales del corpus que alguna version leyo como
# abrogacion. Cada una debe devolver CERO objetivos.
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
    ("clausula de EXCEPCION: la ley nombrada es la excluida",
     "Se abrogan y derogan todas las normas de igual o menor jerarquia, que sean "
     "contrarias a la presente Ley Departamental, con excepcion de la "
     "Disposicion Transitoria Primera de la Ley Departamental N* 304"),
    ("ruido de OCR detras del ancla suelta",
     "Se derogan y abrogan todas las disposiciones contrarias a la presente Ley. "
     "1111 r Jr II lIU1 ll, 111141111111 ASAMBLEA LEGISLATIVA DEPARTAMENTAL"),
    ("el ancla cae dentro de un TITULO citado, no de una referencia",
     'Se abroga la Ley Departamental W 500 "Ley de Organiza-:1on del EJecutivo '
     'Departamental" del 20 de marzo de 2025 y sus disposiciones conexas'),
    ("texto destruido: dos numeros sin marcador es adivinar",
     "y la Ley 483 478 Departamental Modificatoria a la ley"),
]

# Caso de truncado: hay que construir una ventana que llegue al borde duro, que
# es el unico escenario donde un numero puede venir cortado a la mitad.
CONTROL_TRUNCADO = ("numero cortado por el borde de la ventana",
                    "x" * (VENTANA - 35) + "Se abroga la Ley Departamental N* 5")

# BANCO POSITIVO: abrogaciones expresas reales, con el marcador tal como lo dejo
# el OCR. El caso de los articulos esta a proposito: debe devolver SOLO la ley.
CONTROL_ARISTA = [
    ("Se abroga la Ley Departamental N 129 de Organizacion", [129]),
    ("Se derogan los articulos 19 y 20 de la Ley Departamental W 129", [129]),
    ("Se abrogan las Leyes Departamentales N 109, de 14 de mayo de 2014 y N 029",
     [29, 109]),
    ("Se abroga la Ley N 504 Estructura de Cargos", [504]),
    ("Se abroga la Ley Departamental ~o 206 de transferencia", [206]),
    ("Se abroga la Ley Departamental N' 094 Departamentalizacion de Carreteras",
     [94]),
    ("Se abroga la Ley Departamental I49 204 de Modificacion al articulo 27", [204]),
    ("Se deroga el articulo 2 de la Ley Departamental bl(2 139 de Administracion",
     [139]),
    ("Se deroga el Art. 2 de la Ley N* 438 de Aprobacion", [438]),
    ('Se abroga la Ley Departamental W 500 "Ley de Organizacion" y la Ley '
     'Departamental N* 432', [432, 500]),
]


def limpia(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(x for x in s if not unicodedata.combining(x))
    return re.sub(r"\s+", " ", s).strip()


def recorta(ventana):
    """Deja solo la parte dispositiva: corta en el protocolo de cierre."""
    m = CORTE.search(ventana)
    return ventana[:m.start()] if m else ventana


def _delatado(texto, fin):
    """True si lo que sigue al numero lo delata como dia o fecha."""
    return bool(NO_ES_LEY.match(texto[fin:fin + 22]))


def objetivos_de(ventana, truncada=False):
    """Numeros de ley nombrados como objetivo en la parte dispositiva.

    truncada=True solo cuando la ventana llego al borde duro de VENTANA: ahi, y
    solo ahi, un numero pegado al final puede estar cortado a la mitad.
    """
    disp = recorta(ventana)
    borde = truncada and len(ventana) >= VENTANA

    def cortado(texto, fin):
        return borde and fin >= len(texto)

    def elige(desde, exige_marca):
        """Ultimo numero valido en la ventana del ancla.

        Se toma el ULTIMO y no el primero porque la basura del OCR va ANTES del
        numero real: en "Ley Departamental I49 204" el 49 es el marcador roto.
        exige_marca=True cuando el ancla es la palabra "Ley" suelta: ahi un
        numero sin marcador es un titulo citado o ruido, no una referencia.
        """
        trozo = disp[desde:desde + VENTANA_ANCLA]
        patron = MARCA_NUM if exige_marca else NUM
        elegido = None
        for m in patron.finditer(trozo):
            fin_abs = desde + m.end()
            if _delatado(disp, fin_abs) or cortado(disp, fin_abs):
                continue
            elegido = (int(m.group(1)), fin_abs)
        return elegido

    nums = []
    anclas = ([(a, False) for a in ANCLA_DEP.finditer(disp)]
              + [(a, True) for a in ANCLA_LEY.finditer(disp)])
    for anc, exige in anclas:
        # Guarda de excepcion: si justo antes del ancla dice "con excepcion de",
        # la ley que sigue es la EXCLUIDA, no la abrogada.
        antes = disp[max(0, anc.start() - 70):anc.start()]
        if EXCEPCION.search(antes):
            continue
        elegido = elige(anc.end(), exige)
        if not elegido:
            continue
        valor, fin = elegido
        nums.append(valor)
        cola = disp[fin:fin + 200]
        corte = re.split(
            r"(?:Se\s+abrog|Se\s+derog|Articulo|ARTICULO|Disposicion|DISPOSICION)",
            cola)[0]
        for extra in MARCA_NUM.finditer(corte):
            if _delatado(corte, extra.end()) or cortado(corte, extra.end()):
                continue
            nums.append(int(extra.group(1)))
    return sorted(set(n for n in nums if 1 <= n <= 999))


def extrae(leyes, texto):
    aristas, genericas, excepciones, sin_destino = [], [], [], []
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
            objetivos = [o for o in objetivos_de(ventana, truncada=True)
                         if str(o) != propio]
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
            elif EXCEPCION.search(ventana[:300]):
                excepciones.append({"ley": str(meta["numero"]), "anio": meta["anio"],
                                    "cita": cita})
            elif GENERICA.search(ventana[:300]):
                genericas.append({"ley": str(meta["numero"]), "anio": meta["anio"],
                                  "cita": cita})
            else:
                sin_destino.append({"ley": str(meta["numero"]), "anio": meta["anio"],
                                    "cita": cita})
    return aristas, genericas, excepciones, sin_destino, cuenta


def banco():
    """Banco del instrumento. Sin esto verde, no se mide el corpus."""
    print("=== BANCO NEGATIVO: frases reales que alguna version leyo mal ===")
    limpio = True
    for nombre, frase in CONTROL_NEGATIVO:
        objs = objetivos_de(limpia(frase))
        ok = not objs
        limpio = limpio and ok
        print("   %-60s -> %-14s %s"
              % (nombre, objs if objs else "sin objetivo", "ok" if ok else "FALLA"))
    nombre, frase = CONTROL_TRUNCADO
    objs = objetivos_de(frase, truncada=True)
    ok = not objs
    limpio = limpio and ok
    print("   %-60s -> %-14s %s"
          % (nombre, objs if objs else "sin objetivo", "ok" if ok else "FALLA"))
    total = len(CONTROL_NEGATIVO) + 1
    print("   BANCO NEGATIVO: %s"
          % ("%d/%d" % (total, total) if limpio else "HAY FALLAS"))
    print()
    print("=== BANCO POSITIVO: abrogaciones expresas con marcador roto ===")
    todo = True
    for frase, esperado in CONTROL_ARISTA:
        objs = objetivos_de(limpia(frase))
        ok = objs == sorted(esperado)
        todo = todo and ok
        print("   %-74s -> %-12s %s"
              % (frase[:74], objs, "ok" if ok else "FALLA, esperaba %s" % esperado))
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
    aristas, genericas, excepciones, sin_destino, cuenta = extrae(leyes, texto)
    print()
    print("aristas abrogador->abrogada: %d" % len(aristas))
    print("clausulas GENERICAS (no matan a nadie en particular): %d" % len(genericas))
    print("clausulas de EXCEPCION (nombran a la excluida): %d" % len(excepciones))
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
               "excepciones": excepciones, "sin_destino": sin_destino},
              open(salida, "w"), ensure_ascii=False, indent=1)
    print("escrito %s" % salida)
    if not verde:
        print("VEREDICTO: ROJO -> falta algun par conocido")
        return 1
    print("VEREDICTO: VERDE -> banco y control en verde")
    return 0


if __name__ == "__main__":
    sys.exit(main())
