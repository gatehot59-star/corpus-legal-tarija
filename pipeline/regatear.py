"""Recalcula el veredicto de calidad sobre el texto YA extraido, sin repetir el OCR.

Existe porque el gate v1 se equivoco despues de que la corrida ya habia empezado, y repetir
8 h de CPU para arreglar una etiqueta es tirar el trabajo bueno junto con el instrumento
malo. El OCR es el paso caro y su salida es valida; el veredicto es un calculo sobre esa
salida y se puede volver a hacer cuando el instrumento mejora.

Lee `registros.jsonl` y los `.txt` del corpus, aplica `gate_v2` y reescribe el estado y la
cola de revision humana. Conserva el veredicto viejo en `gate_v1_veredicto` para que el
cambio sea auditable: sin eso, nadie puede medir cuantos documentos cambiaron de lado.
"""
import argparse
import collections
import json
from pathlib import Path

import gate_v2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True, help="directorio con registros.jsonl y texto/")
    a = ap.parse_args()

    base = Path(a.corpus)
    reg_p = base / "registros.jsonl"
    if not reg_p.exists():
        print("ROJO: no existe " + str(reg_p))
        return 2

    registros = [json.loads(l) for l in reg_p.read_text(encoding="utf-8").splitlines() if l.strip()]
    cambios = collections.Counter()
    nuevos = []
    for r in registros:
        archivo = r.get("archivo_texto")
        if not archivo or r["estado"] not in ("OK", "REVISION_HUMANA"):
            nuevos.append(r)
            continue
        t = base / "texto" / archivo
        if not t.exists():
            r["motivo"] = (r.get("motivo") or "") + " | texto ausente al regatear"
            nuevos.append(r)
            continue
        crudo = t.read_text(encoding="utf-8", errors="replace")
        paginas = crudo.split("\f") if "\f" in crudo else [crudo]
        g = gate_v2.evaluar(paginas)
        viejo = r["estado"]
        r["gate_v1_veredicto"] = viejo
        r["gate"] = g
        r["estado"] = "OK" if g["veredicto"] == "APTO" else "REVISION_HUMANA"
        r["motivo"] = "" if g["veredicto"] == "APTO" else g["motivo"]
        cambios[viejo + " -> " + r["estado"]] += 1
        nuevos.append(r)

    reg_p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in nuevos) + "\n",
                     encoding="utf-8")
    print("transiciones de veredicto:")
    for k, n in cambios.most_common():
        print("  " + str(n) + "  " + k)
    estados = collections.Counter(r["estado"] for r in nuevos)
    print("\nestados finales: " + json.dumps(dict(estados), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
