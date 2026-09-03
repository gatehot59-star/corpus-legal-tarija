"""Segunda pasada sobre los documentos que el gate rechazo, probando orientaciones.

Por que existe, medido: de 784 documentos, 6 quedaron en REVISION_HUMANA y los 6 tienen el
MISMO defecto. Su texto sale asi:

    PUPeIA 87 'DS3 ans a/1e5 03"1P|2: MMM

que leido al reves es "Calle Sur Esq. La Madrid": **son escaneos rotados 180 grados.**
Tesseract lee la pagina invertida y devuelve algo que parece castellano roto pero no lo es.
Ninguna ancla legal aparece, y por eso el gate v2 los agarro.

Es un defecto de la FUENTE, no del motor, y tiene arreglo mecanico: se prueban las cuatro
rotaciones y gana la que el gate aprueba. Se hace en una segunda pasada y solo sobre los
rechazados porque son 6 de 784: rotar los 784 por si acaso seria pagar 4x el OCR completo
para arreglar el 0,8%.

El detector de orientacion de Tesseract (`--psm 0`, osd.traineddata) se consulta pero NO se
le cree solo: dio "Orientation in degrees: 0" con confianza 23 en una pagina derecha, y una
confianza de 23 no distingue nada. Asi que el juez es el gate sobre el texto resultante, que
es una medicion del producto y no una prediccion sobre la imagen.

DOS ERRORES CORREGIDOS EN LA PRIMERA CORRIDA DE ESTE ARCHIVO, y quedan escritos porque el
segundo se me escapo dos veces:

1. `pdftoppm -rotate` **no existe**: lo asumi sin verificar. El sintoma fue silencioso (tres
   rotaciones devolviendo lista vacia y el loop salteandolas), asi que el log solo mostraba
   "0 grados". Ahora se rota el PNG con Pillow.
2. El comentario decia que rotar el raster "degrada el trazo". **Falso** para 90/180/270: son
   permutaciones exactas de pixeles. Y como se rasteriza una sola vez, tambien es mas rapido.
"""
import argparse
import json
import subprocess
import tempfile
import time
from pathlib import Path

from PIL import Image

import gate_v2
import normalizar_citas as nc
from ocr_masivo import bajar

# Los nombres de PIL son antihorarios: para GIRAR la pagina 90 grados horario hay que
# aplicar ROTATE_270. Escrito explicito porque invertirlo da un texto igual de ilegible.
TRANSPOSICION = {90: Image.Transpose.ROTATE_270,
                 180: Image.Transpose.ROTATE_180,
                 270: Image.Transpose.ROTATE_90}


def rasterizar(pdf: Path, tmp: Path, pdftoppm: str, dpi: int) -> list:
    """Rasteriza a 0 grados UNA sola vez. Devuelve los PNG en orden de pagina."""
    base = tmp / "pag"
    cp = subprocess.run([pdftoppm, "-r", str(dpi), "-gray", "-png", str(pdf), str(base)],
                        capture_output=True, text=True)
    if cp.returncode != 0:
        print("    ROJO pdftoppm exit " + str(cp.returncode) + ": " + cp.stderr.strip()[:150])
        return []
    return sorted(base.parent.glob(base.name + "-*.png"),
                  key=lambda p: int(p.stem.split("-")[-1]))


def ocr_rotado(pngs: list, grados: int, tmp: Path, args) -> list:
    """OCR de las paginas rotadas `grados`, reusando la rasterizacion."""
    textos = []
    for i, png in enumerate(pngs, start=1):
        if grados:
            destino = tmp / f"rot{grados}-{i}.png"
            with Image.open(png) as im:
                im.transpose(TRANSPOSICION[grados]).save(destino)
        else:
            destino = png
        salida = tmp / f"txt{grados}-{i}"
        subprocess.run([args.tesseract, str(destino), str(salida),
                        "-l", args.lang, "--psm", str(args.psm)],
                       capture_output=True, text=True)
        t = salida.with_suffix(".txt")
        textos.append(t.read_text(encoding="utf-8", errors="replace") if t.exists() else "")
        if grados:
            destino.unlink(missing_ok=True)
        t.unlink(missing_ok=True)
    return textos


def osd(pngs: list, args) -> dict:
    """Lo que OPINA el detector de orientacion. Se registra como dato, no como decision."""
    if not pngs:
        return {}
    cp = subprocess.run([args.tesseract, "--psm", "0", str(pngs[0]), "-"],
                        capture_output=True, text=True)
    d = {}
    for linea in (cp.stdout + cp.stderr).splitlines():
        if ":" in linea:
            k, v = linea.split(":", 1)
            d[k.strip()] = v.strip()
    return {"rotate": d.get("Rotate"), "confianza": d.get("Orientation confidence")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--manifiesto", required=True)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--psm", type=int, default=3)
    ap.add_argument("--lang", default="spa")
    ap.add_argument("--tesseract", default="tesseract")
    ap.add_argument("--pdftoppm", default="pdftoppm")
    args = ap.parse_args()

    base = Path(args.corpus)
    regs = [json.loads(l) for l in (base / "registros.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    pendientes = {r["archivo_texto"]: r for r in regs
                  if r["estado"] == "REVISION_HUMANA" and r.get("archivo_texto")}
    if not pendientes:
        print("no hay documentos en REVISION_HUMANA: nada que reintentar")
        return 0
    print(f"a reintentar: {len(pendientes)} de {len(regs)}", flush=True)

    # El manifiesto se indexa por sha256 para reencontrar la URL de cada rechazado.
    por_sha = {}
    for l in Path(args.manifiesto).read_text(encoding="utf-8").splitlines():
        l = l.strip()
        if not l or l.startswith("#"):
            continue
        d = json.loads(l)
        if d.get("sha256"):
            por_sha[d["sha256"][:12]] = d

    resultados = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for archivo, reg in pendientes.items():
            doc = (por_sha.get((reg.get("sha256_real") or "")[:12])
                   or por_sha.get((reg.get("sha256_esperado") or "")[:12]))
            if not doc:
                print(f"  {archivo}: SIN_FUENTE en el manifiesto, no se puede reintentar")
                resultados.append({"archivo": archivo, "estado": "SIN_FUENTE"})
                continue
            try:
                crudo = bajar(doc["fuente_url"])
            except Exception as e:
                resultados.append({"archivo": archivo, "estado": "DESCARGA_FALLIDA",
                                   "error": str(e)[:150]})
                continue
            pdf = tmp / "doc.pdf"
            pdf.write_bytes(crudo)
            pngs = rasterizar(pdf, tmp, args.pdftoppm, args.dpi)
            if not pngs:
                resultados.append({"archivo": archivo, "estado": "RASTERIZADO_FALLIDO"})
                continue
            opinion = osd(pngs, args)

            elegido, mejor = None, None
            for grados in (180, 90, 270, 0):
                t0 = time.time()
                textos = ocr_rotado(pngs, grados, tmp, args)
                g = gate_v2.evaluar(textos)
                print(f"  {archivo} {grados:3d} grados: {g['veredicto']}, "
                      f"{g['anclas_legales']} anclas, {len(''.join(textos))} chars, "
                      f"{time.time() - t0:.0f}s", flush=True)
                if mejor is None or g["anclas_legales"] > mejor[1]["anclas_legales"]:
                    mejor = (grados, g, textos)
                if g["veredicto"] == "APTO":
                    elegido = (grados, g, textos)
                    break

            for p in pngs:
                p.unlink(missing_ok=True)

            grados, g, textos = elegido or mejor
            texto = "\n\f\n".join(textos)
            citas = nc.extraer(texto, documento=archivo)
            if elegido:
                (base / "texto" / archivo).write_text(texto, encoding="utf-8")
                (base / "texto" / archivo.replace(".txt", ".indice.txt")).write_text(
                    citas["texto_indice"], encoding="utf-8")
            resultados.append({
                "archivo": archivo, "estado": "OK" if elegido else "REVISION_HUMANA",
                "rotacion_aplicada": grados if elegido else None,
                "osd_opina": opinion, "anclas": g["anclas_legales"],
                "chars": len(texto), "citas_a_revisar": citas["total_revision"],
            })

    (base / "reintento_rotacion.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=1), encoding="utf-8")
    recuperados = sum(1 for r in resultados if r["estado"] == "OK")
    print(f"\nrecuperados: {recuperados} de {len(pendientes)}")
    for r in resultados:
        print("  ", r["archivo"], r["estado"], "rotacion", r.get("rotacion_aplicada"),
              "| osd opinaba", r.get("osd_opina"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
