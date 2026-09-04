#!/usr/bin/env python3
"""EL HALLAZGO: la concordancia funciona como FALSADOR de mi propia vigencia.

Un decreto que REGLAMENTA una ley es evidencia independiente de que esa ley estaba viva
cuando se dicto el decreto. Si yo marque la ley como derogada ANTES de esa fecha, uno de
los dos datos esta mal, y el que viene de una fuente distinta gana.

Dos casos aparecieron solos en la muestra:
  LD 500 [derogada por LD 520] <- DD 16/2026 la reglamenta
  LD 109 [derogada por LD 519 de 2026] <- DD 8/2020 la reglamenta
"""
import json, re, sqlite3
c = sqlite3.connect("file:/workspace/bolivia-v7.db?mode=ro", uri=True); c.row_factory = sqlite3.Row
conc = json.load(open("/workspace/ab-probe-20260903/concordancia_dd.json"))
leyes = {}
for r in c.execute("SELECT uid,numero,anio,fecha,titulo,vigente,derogada_por FROM documentos "
                   "WHERE tipo_norma='Ley Departamental' AND numero GLOB '[0-9]*'"):
    leyes.setdefault(str(int(r["numero"])), []).append(dict(r))

print("== CONTRADICCIONES: un decreto reglamenta una ley que yo marque muerta")
alertas = []
for h in conc:
    f = (leyes.get(h["ley"]) or [None])[0]
    if not f or f["vigente"] != 0:
        continue
    # de que ano es la norma que la mato?
    m = re.search(r"(\d{1,4})", f["derogada_por"] or "")
    sucesora = (leyes.get(str(int(m.group(1)))) or [None])[0] if m else None
    anio_suc = sucesora["anio"] if sucesora else None
    print()
    print("  LD %s de %s | marcada DEROGADA por: %s" % (h["ley"], f["anio"] or "?", f["derogada_por"]))
    print("     titulo: %s" % (f["titulo"] or "")[:80])
    print("     la sucesora en el corpus: LD %s de %s" % (m.group(1) if m else "?", anio_suc or "SIN ANIO"))
    print("     PERO el DD %s de %s la %s" % (h["decreto"], h["anio_decreto"], h["relacion"]))
    try:
        ad, asuc = int(h["anio_decreto"] or 0), int(anio_suc or 0)
    except ValueError:
        ad = asuc = 0
    if ad and asuc and ad < asuc:
        print("     -> CONSISTENTE: el decreto (%d) es ANTERIOR a la sucesora (%d)." % (ad, asuc))
        print("        La ley estaba viva cuando se la reglamento y murio despues.")
    elif ad and asuc and ad >= asuc:
        print("     -> CONTRADICCION: el decreto (%d) es POSTERIOR o igual a la sucesora (%d)." % (ad, asuc))
        print("        Un decreto no reglamenta una ley ya abrogada: revisar la derogacion.")
        alertas.append(h)
    else:
        print("     -> NO MEDIBLE: falta el ano de la sucesora en el corpus.")
        alertas.append(h)
print()
print("casos que exigen revision humana:", len(alertas))
print()
print("== y el dato que le sirve al abogado HOY, sin OCR ni descargas")
print("   Cada una de estas leyes tiene su reglamento identificado por numero y ano.")
print("   Hoy el buscador NO lo dice, y es una pregunta que un abogado hace siempre:")
print("   'esta ley tiene reglamento?'")
n = 0
for h in sorted(conc, key=lambda x: -int(x["anio_decreto"] or 0)):
    f = (leyes.get(h["ley"]) or [None])[0]
    if not f or h["relacion"] != "reglamenta":
        continue
    n += 1
    if n <= 15:
        print("   LD %-4s -> reglamentada por DD %s/%s" % (h["ley"], h["decreto"], h["anio_decreto"]))
print("   total con reglamento identificado:", n)
c.close()
