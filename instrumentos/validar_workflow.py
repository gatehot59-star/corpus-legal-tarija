#!/usr/bin/env python3
"""Valida un workflow ANTES de dispararlo.

Por que existe: un heredoc de Python roto dentro de un step no lo caza el
parser de YAML. El job arranca, baja 40 MB de PDF, y recien ahi explota. Ya
pase por eso con los heredocs del shell del gateway.

Que chequea:
  1. El YAML parsea.
  2. CADA bloque `python3 - <<'PY' ... PY` compila con ast.parse.
  3. Que la cantidad de bloques encontrados sea > 0 (si es 0, el validador no
     estaba mirando nada y decir VERDE seria un instrumento que no puede
     dar rojo).

Uso: python3 validar_workflow.py <archivo.yml>
"""
import ast
import sys

import yaml


def bloques_py(texto_run):
    lineas = texto_run.split("\n")
    abre = [i for i, x in enumerate(lineas) if "python3 - " in x]
    cierra = [i for i, x in enumerate(lineas) if x.strip() == "PY"]
    out = []
    for a in abre:
        siguientes = [c for c in cierra if c > a]
        if not siguientes:
            out.append((a, None, None))
            continue
        b = siguientes[0]
        out.append((a, b, "\n".join(lineas[a + 1:b])))
    return out


def main():
    ruta = sys.argv[1]
    d = yaml.safe_load(open(ruta))
    print("YAML OK. jobs: %s" % list(d["jobs"].keys()))
    total = 0
    rojos = 0
    for jn, j in d["jobs"].items():
        for st in j.get("steps", []):
            run = st.get("run", "")
            if not run or "python3 - " not in run:
                continue
            for a, b, cuerpo in bloques_py(run):
                total += 1
                if cuerpo is None:
                    print("ROJO %s: heredoc sin cierre PY (linea %d)" % (jn, a))
                    rojos += 1
                    continue
                try:
                    ast.parse(cuerpo)
                    print("OK %-18s bloque de %d caracteres" % (jn, len(cuerpo)))
                except SyntaxError as e:
                    print("ROJO %s: %s (linea %s)" % (jn, e.msg, e.lineno))
                    rojos += 1
    print("bloques encontrados: %d | rojos: %d" % (total, rojos))
    if total == 0:
        print("ROJO DEL VALIDADOR: cero bloques. No estaba mirando nada.")
        raise SystemExit(3)
    if rojos:
        raise SystemExit(1)
    print("VERDE")


if __name__ == "__main__":
    main()
