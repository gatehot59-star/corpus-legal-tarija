"""Junta los 20 shards en un corpus y mide el resultado agregado.

Cada shard corrio aislado a proposito: 20 jobs escribiendo el mismo manifiesto es como se
pierde una corrida de 8 horas. La consolidacion es un paso aparte y con su propio veredicto.
"""
import argparse
import collections
import json
import shutil
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--crudo", required=True)
    ap.add_argument("--salida", required=True)
    a = ap.parse_args()

    crudo, salida = Path(a.crudo), Path(a.salida)
    (salida / "texto").mkdir(parents=True, exist_ok=True)

    registros = []
    for j in sorted(crudo.rglob("shard-*.jsonl")):
        for linea in j.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea:
                registros.append(json.loads(linea))

    copiados = 0
    for t in sorted(crudo.rglob("texto/*.txt")):
        destino = salida / "texto" / t.name
        if not destino.exists():
            shutil.copy2(t, destino)
            copiados += 1

    estados = collections.Counter(r["estado"] for r in registros)
    fuentes = collections.Counter(r.get("fuente_id") or "?" for r in registros)
    procesados = [r for r in registros if r["estado"] in ("OK", "REVISION_HUMANA")]
    paginas = sum(r.get("paginas", 0) for r in procesados)
    chars = sum(r.get("chars", 0) for r in procesados)
    segundos = sum(r.get("segundos", 0) for r in registros)
    a_revisar = sum(r.get("citas_a_revisar", 0) for r in registros)

    # Cola de revision humana: citas ambiguas + documentos que no pasaron el gate.
    cola = []
    for r in registros:
        for c in r.get("revision_citas", []):
            cola.append({"tipo": "cita_ambigua", "documento": c.get("documento"),
                         "linea": c.get("linea"), "crudo": c.get("crudo"),
                         "canonico_probable": c.get("canonico_probable"),
                         "contexto": c.get("contexto")})
        if r["estado"] == "REVISION_HUMANA":
            cola.append({"tipo": "gate_no_pasa", "documento": f"{r.get('fuente_id')}-{r.get('numero')}",
                         "motivo": r.get("motivo"), "gate": r.get("gate", {}).get("pct_paginas_ok")})

    resumen = {
        "documentos": len(registros), "estados": dict(estados), "por_fuente": dict(fuentes),
        "paginas_ocr": paginas, "caracteres": chars,
        "archivos_texto": copiados,
        "segundos_cpu": round(segundos, 1),
        "seg_por_pagina": round(segundos / paginas, 2) if paginas else None,
        "citas_a_revisar": a_revisar,
        "cola_revision_humana": len(cola),
    }
    (salida / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    (salida / "registros.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in registros) + "\n", encoding="utf-8")
    (salida / "revision_humana.jsonl").write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in cola) + ("\n" if cola else ""), encoding="utf-8")

    md = ["# OCR del corpus escaneado de Tarija", "",
          f"**{len(registros)} documentos procesados** \u00b7 {paginas} paginas \u00b7 "
          f"{chars} caracteres \u00b7 {copiados} archivos de texto", "",
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
    (salida / "RESUMEN.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
