"""Regenera resumen.json, RESUMEN.md y revision_humana.jsonl desde `registros.jsonl`.

Existe porque el resumen es una VISTA de los registros, no un dato propio, y despues de
regatear.py o de reintentar_rotados.py los registros cambian y la vista queda vieja. Tener
que volver a bajar los artefactos para actualizar un markdown es acoplar la lectura al
transporte.

(Y lo aprendi rompiendolo: corri consolidar.py apuntado a /dev/null para "solo rehacer el
resumen" y me dejo un RESUMEN.md con 0 documentos. El consolidador junta shards; resumir es
otra operacion y ahora tiene su propio archivo.)
"""
import argparse
import collections
import json
from pathlib import Path


def resumir(base: Path) -> dict:
    regs = [json.loads(l) for l in (base / "registros.jsonl").read_text(encoding="utf-8").splitlines()
            if l.strip()]
    estados = collections.Counter(r["estado"] for r in regs)
    fuentes = collections.Counter(r.get("fuente_id") or "?" for r in regs)
    procesados = [r for r in regs if r["estado"] in ("OK", "REVISION_HUMANA")]
    paginas = sum(r.get("paginas", 0) for r in procesados)
    chars = sum(r.get("chars", 0) for r in procesados)
    segundos = sum(r.get("segundos", 0) for r in regs)
    a_revisar = sum(r.get("citas_a_revisar", 0) for r in regs)

    cola = []
    for r in regs:
        for c in r.get("revision_citas", []):
            cola.append({"tipo": "cita_ambigua", "documento": c.get("documento"),
                         "linea": c.get("linea"), "crudo": c.get("crudo"),
                         "canonico_probable": c.get("canonico_probable"),
                         "contexto": c.get("contexto")})
        if r["estado"] == "REVISION_HUMANA":
            cola.append({"tipo": "gate_no_pasa",
                         "documento": r.get("archivo_texto") or r.get("numero"),
                         "motivo": r.get("motivo")})

    resumen = {
        "documentos": len(regs), "estados": dict(estados), "por_fuente": dict(fuentes),
        "paginas_ocr": paginas, "caracteres": chars,
        "archivos_texto": len(list((base / "texto").glob("*.txt"))) if (base / "texto").exists() else 0,
        "segundos_cpu": round(segundos, 1),
        "seg_por_pagina": round(segundos / paginas, 2) if paginas else None,
        "citas_a_revisar": a_revisar,
        "cola_revision_humana": len(cola),
    }
    (base / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    (base / "revision_humana.jsonl").write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in cola) + ("\n" if cola else ""),
        encoding="utf-8")

    md = ["# OCR del corpus escaneado de Tarija", "",
          f"**{len(regs)} documentos procesados** \u00b7 {paginas} paginas \u00b7 {chars} caracteres \u00b7 "
          f"{resumen['archivos_texto']} archivos de texto", "",
          "| estado | documentos |", "|---|---|"]
    for e, n in estados.most_common():
        md.append(f"| {e} | {n} |")
    md += ["", f"**Costo medido:** {round(segundos / 3600, 2)} h de CPU"
               + (f", {round(segundos / paginas, 2)} s/pagina." if paginas else "."), "",
           f"**Cola de revision humana:** {len(cola)} items ({a_revisar} citas ambiguas). "
           "Vive en `revision_humana.jsonl`.", "",
           "## Que NO hace este corpus", "",
           "El texto crudo es la fuente y **no se reescribe nunca**. Las citas ambiguas "
           "(`Art. 17.1` que probablemente era `Art. 17.I`) se anotan aparte y se indexan en "
           "las dos formas; corregir la ley por inferencia fabricaria una norma que no existe.", ""]
    (base / "RESUMEN.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    return resumen


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    a = ap.parse_args()
    resumir(Path(a.corpus))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
