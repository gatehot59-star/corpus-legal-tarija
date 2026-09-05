#!/usr/bin/env python3
"""Censa una gestion de la Gaceta Constitucional Plurinacional del TCP.

Que mide, por tomo:
  status HTTP, bytes, content-type, sha256, paginas, caracteres nativos,
  SCP unicas, autos, declaraciones, y cuantas dicen "Departamento: Tarija".

Por que puede dar ROJO (y no es decorativo):
  1. CONTROL NEGATIVO: pide un tomo INVENTADO. Si ese devuelve 200 con PDF,
     entonces el servidor contesta cualquier cosa y TODOS los 200 de esta
     corrida quedan sin valor. Sin este control, un 200 no distingue
     existe de no existe.
  2. GUARD POR TOMO: un tomo con 0 SCP o 0 "Departamento:" se marca ROJO.
     Un PDF escaneado sin capa de texto dara exactamente eso, y hay que
     verlo, no promediarlo.
  3. Dos URLs del portal vienen SIN extension .pdf (TomoIII de los dos
     semestres). Se mide el content-type real en vez de confiar en el nombre.

Uso: python3 censo_gaceta_tcp.py <gestion> [--solo-cabecera]
"""
import hashlib
import json
import ssl
import sys
import re
import os
import urllib.request as U

BASE = "https://tcpbolivia.bo/wp-content/uploads/2025/03/"
ROMANOS = ["I", "II", "III", "IV", "V"]
CTX = ssl._create_unverified_context()
HD = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}


def urls_de(gestion):
    """Los 10 tomos de una gestion, mas el control negativo."""
    out = []
    for sem in (1, 2):
        for r in ROMANOS:
            nombre = "Tomo%ss%d%s" % (r, sem, gestion)
            # el portal sirve TomoIII sin .pdf en los dos semestres
            for cand in (nombre + ".pdf", nombre):
                out.append((nombre, BASE + cand))
    out.append(("CONTROL_NEGATIVO", BASE + "TomoXXs9%s.pdf" % gestion))
    return out


def bajar(url, destino):
    try:
        r = U.urlopen(U.Request(url, headers=HD), timeout=300, context=CTX)
        cuerpo = r.read()
        with open(destino, "wb") as f:
            f.write(cuerpo)
        return r.status, len(cuerpo), r.headers.get("Content-Type", "")
    except Exception as e:
        return ("ERR:%s" % type(e).__name__), 0, str(e)[:90]


def censar_texto(txt):
    scp = set(re.findall(r"SENTENCIA CONSTITUCIONAL PLURINACIONAL\s+([0-9]{3,4}/[0-9]{4}[-A-Za-z0-9]*)", txt))
    return {
        "caracteres": len(txt),
        "scp_unicas": len(scp),
        "autos": len(re.findall("AUTO CONSTITU", txt, re.I)),
        "declaraciones": len(re.findall("DECLARACI", txt)),
        "departamento_campo": len(re.findall(r"Departamento:", txt)),
        "tarija": len(re.findall(r"Departamento:\s*Tarija", txt)),
        "tarija_menciones": len(re.findall("Tarija", txt)),
    }


def main():
    gestion = sys.argv[1] if len(sys.argv) > 1 else "2022"
    solo_cab = "--solo-cabecera" in sys.argv
    os.makedirs("tomos", exist_ok=True)
    vistos = set()
    res = []
    for nombre, url in urls_de(gestion):
        if nombre in vistos and nombre != "CONTROL_NEGATIVO":
            continue
        destino = os.path.join("tomos", nombre + ".pdf")
        st, n, ct = bajar(url, destino)
        fila = {"tomo": nombre, "url": url, "status": st, "bytes": n, "ctype": ct}
        es_pdf = isinstance(ct, str) and "pdf" in ct.lower() and n > 100000
        if not es_pdf:
            fila["veredicto"] = "NO_ES_PDF"
            res.append(fila)
            if os.path.exists(destino):
                os.remove(destino)
            continue
        vistos.add(nombre)
        with open(destino, "rb") as f:
            fila["sha256"] = hashlib.sha256(f.read()).hexdigest()
        if solo_cab:
            fila["veredicto"] = "CABECERA_OK"
            res.append(fila)
            continue
        try:
            import pypdf
            r = pypdf.PdfReader(destino)
            fila["paginas"] = len(r.pages)
            txt = "".join((p.extract_text() or "") for p in r.pages)
            with open(os.path.join("tomos", nombre + ".txt"), "w") as f:
                f.write(txt)
            fila.update(censar_texto(txt))
            # GUARD: puede dar rojo
            if fila["scp_unicas"] == 0 or fila["departamento_campo"] == 0:
                fila["veredicto"] = "ROJO_SIN_TEXTO_UTIL"
            else:
                fila["veredicto"] = "VERDE"
        except Exception as e:
            fila["veredicto"] = "ERR_EXTRACCION:%s" % type(e).__name__
        res.append(fila)
        with open("censo-%s.json" % gestion, "w") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)

    ctrl = [x for x in res if x["tomo"] == "CONTROL_NEGATIVO"]
    verdes = [x for x in res if x.get("veredicto") == "VERDE"]
    resumen = {
        "gestion": gestion,
        "tomos_verdes": len(verdes),
        "scp_unicas_total": sum(x["scp_unicas"] for x in verdes),
        "tarija_total": sum(x["tarija"] for x in verdes),
        "caracteres_total": sum(x["caracteres"] for x in verdes),
        "paginas_total": sum(x.get("paginas", 0) for x in verdes),
        "control_negativo": ctrl[0] if ctrl else None,
    }
    if ctrl and ctrl[0].get("veredicto") not in ("NO_ES_PDF",):
        resumen["ALERTA"] = "el control negativo devolvio un PDF: los 200 no valen"
    with open("censo-%s.json" % gestion, "w") as f:
        json.dump({"resumen": resumen, "tomos": res}, f, ensure_ascii=False, indent=1)
    print(json.dumps(resumen, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
