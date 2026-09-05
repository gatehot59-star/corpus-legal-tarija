#!/usr/bin/env python3
"""Diagnostica un censo de la Gaceta y lo cruza contra el censo del buscador.

Tres cosas que mide y que NO son lo mismo:

  1. SOLAPAMIENTO: que resolucion aparece en DOS tomos. El RESUMEN solo dice
     si hay o no (unicas != suma). Este dice CUAL y en cuales tomos, porque
     un solapamiento real y un ID mal parseado se ven igual en el total.

  2. IDs MALFORMADOS: mi regex `[0-9]{3,4}/[0-9]{4}[-A-Za-z0-9]*` acepta un
     guion final sin sala ("0339/2018-"). Eso inventa una resolucion fantasma
     y sube el conteo. Es un defecto MIO, no de la fuente.

  3. EL CRUCE contra el buscador. Dos fuentes del mismo ano tienen que dar
     numeros parecidos; si no, uno de los dos sujetos esta mal definido.

Uso: python3 diagnosticar_cruce.py <gestion>
"""
import glob
import json
import re
import sys

# Censo del buscador (EXP-TCP-002), distrito 7 = Tarija, por gestion.
# Instrumento B: tipoBusqueda=1 con el termino "notifiquese". Es COTA INFERIOR:
# en 2015 el instrumento A dio 349 y B dio 344, o sea B subcuenta ~1,4 %.
BUSCADOR = {
    "1999": 1, "2000": 0, "2001": 0, "2002": 37, "2003": 91, "2004": 88,
    "2005": 71, "2006": 83, "2007": 48, "2008": 4, "2009": 1, "2010": 126,
    "2011": 96, "2012": 163, "2013": 236, "2014": 281, "2015": 349,
    "2016": 380, "2017": 293, "2018": 301, "2019": 290,
}

RE_BIEN = re.compile(r"^[0-9]{3,4}/[0-9]{4}(-[A-Za-z0-9]+)?$")


def main():
    gestion = sys.argv[1] if len(sys.argv) > 1 else "2018"
    d = "mediciones/gaceta-%s" % gestion
    tomos = []
    for p in sorted(glob.glob(d + "/Tomo*.json")):
        tomos.append(json.load(open(p)))
    if not tomos:
        print("ROJO: cero tomos en %s" % d)
        raise SystemExit(2)

    # donde vive cada resolucion
    donde = {}
    for t in tomos:
        for r in t.get("tarija_resoluciones", []):
            donde.setdefault(r, []).append(t["tomo"])

    repetidas = {r: v for r, v in donde.items() if len(v) > 1}
    malformados = sorted(r for r in donde if not RE_BIEN.match(r))
    # una resolucion sin sala cuyo numero/anio SI existe con sala: candidata a
    # ser la misma cortada por el parser
    sospechosas = {}
    for m in malformados:
        base = m.rstrip("-")
        hermanas = [r for r in donde if r != m and r.startswith(base + "-")]
        if hermanas:
            sospechosas[m] = sorted(hermanas)

    unicas = len(donde)
    suma = sum(t["tarija_total"] for t in tomos)
    limpias = len([r for r in donde if RE_BIEN.match(r)])

    print("GESTION %s" % gestion)
    print("  tomos                  : %d" % len(tomos))
    print("  Tarija unicas (crudo)  : %d" % unicas)
    print("  Tarija suma por tomo   : %d" % suma)
    print("  Tarija con ID valido   : %d" % limpias)
    print("  IDs malformados        : %s" % (malformados or "ninguno"))
    for m, h in sospechosas.items():
        print("    '%s' tiene hermana con sala: %s -> probablemente la MISMA" % (m, h))
    if repetidas:
        print("  REPETIDAS entre tomos  : %d" % len(repetidas))
        for r, v in sorted(repetidas.items()):
            print("    %s en %s" % (r, v))
    else:
        print("  REPETIDAS entre tomos  : ninguna")

    # EL CRUCE
    b = BUSCADOR.get(gestion)
    print("  --- CRUCE ---")
    if b is None:
        print("  buscador: SIN DATO para %s (fuera del tramo 1999-2019)" % gestion)
        return
    print("  buscador (cota inferior): %d" % b)
    print("  gaceta   (ID valido)    : %d" % limpias)
    delta = limpias - b
    pct = (100.0 * delta / b) if b else 0.0
    print("  delta                   : %+d (%+.1f %%)" % (delta, pct))
    if limpias > b:
        print("  LECTURA: la Gaceta encuentra MAS. Coherente con que el buscador")
        print("           exige un termino de texto y por eso es cota inferior.")
    else:
        print("  LECTURA: la Gaceta encuentra MENOS que una COTA INFERIOR ajena.")
        print("           Eso NO se explica por el sesgo del buscador: o la Gaceta")
        print("           no publica todo, o mi parser pierde resoluciones.")
        print("           Falsador barato: tomar 5 numeros que el buscador tiene y")
        print("           la Gaceta no, y buscarlos a mano en el texto del tomo.")


if __name__ == "__main__":
    main()
