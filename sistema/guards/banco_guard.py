#!/usr/bin/env python3
"""banco_guard.py - el banco que le exige rojo al guard.

Por que existe con controles del instrumento adentro: midiendo este guard, el
`$?` del shell de brain-env dio 0 para un `python3 -c "sys.exit(3)"` y 0 para
un `false`. Estuve a punto de declarar roto el guard cuando lo roto era el
termometro. Por eso el banco mide los codigos de salida con subprocess y arranca
probando que sabe distinguir un 3 de un 0.

Uso:
    cd <dir con las bases>  &&  python3 banco_guard.py

Espera encontrar, relativo al cwd:
    bolivia-v7.db                          base sana
    bolivia-v8.db.CORRUPTA-NO-DESPLEGAR    base con el btree roto
"""
import os
import subprocess
import sys

GUARD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guard_base.py")
SANA = "bolivia-v7.db"
CORRUPTA = "bolivia-v8.db.CORRUPTA-NO-DESPLEGAR"

CASOS = [
    ("control instrumento exit 3", [sys.executable, "-c", "import sys; sys.exit(3)"], 3),
    ("control instrumento exit 0", [sys.executable, "-c", "import sys; sys.exit(0)"], 0),
    ("guard sobre base SANA", [sys.executable, GUARD, SANA], 0),
    ("guard sobre base CORRUPTA", [sys.executable, GUARD, CORRUPTA], 1),
    ("guard con --rapido (NO MEDIDO no es verde)", [sys.executable, GUARD, SANA, "--rapido"], 1),
    ("guard sobre base INEXISTENTE", [sys.executable, GUARD, "no-existe.db"], 1),
]


def main():
    todo = True
    for nombre, cmd, esperado in CASOS:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        ok = proc.returncode == esperado
        todo = todo and ok
        print("%-44s rc=%s esperado=%s %s"
              % (nombre, proc.returncode, esperado, "ok" if ok else "FALLA"))
        veredicto = [l for l in proc.stdout.splitlines()
                     if l.startswith("VEREDICTO") or l.startswith("ROJO")]
        if veredicto:
            print("      ", veredicto[0][:120])
    print()
    print("BANCO DEL GUARD: %s" % ("%d/%d VERDE" % (len(CASOS), len(CASOS)) if todo
                                   else "HAY FALLAS"))
    return 0 if todo else 1


if __name__ == "__main__":
    sys.exit(main())
