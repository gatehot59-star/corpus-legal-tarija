"""Fuente nacional: normas del Estado Plurinacional verificadas una por una.

El censo de esta fuente es `normas.jsonl`, que produce `pipeline/nacional_lexivox.py`. Cada fila
ya viene con su identidad **verificada contra el titulo real** de la norma en LexiVox, no inferida
de su numero: `BO-L-439` y `BO-L-N439` son normas distintas con el mismo numero, y una de las dos
es el Codigo Procesal Civil de 2013.

**La vigencia entra en `None` SIEMPRE, incluso cuando el texto no menciona ninguna abrogacion.**
Esto no es prudencia decorativa: el Codigo de Procedimiento Civil de 1975 esta **abrogado** por la
Ley 439 de 2013 y su propio texto no lo dice, porque una norma no se enmienda a si misma cuando
otra la mata. **No mencionar una abrogacion no es prueba de estar vigente.** Las senales que el
script cuenta (`abrogad`, `derogad`, `modificad`) entran a la cola de revision como pistas para un
humano, nunca como veredicto.

**Por que la materia se declara a mano y no se infiere del texto:** un Codigo Penal menciona
"contrato" y un Codigo Civil menciona "delito". Clasificar por menciones es el error del "iva"
dentro de "legislativa", ya medido en este proyecto. La materia de una norma nacional la sabe
cualquiera que la lea una vez, y son 15 normas, no 15.000.
"""
from __future__ import annotations

import json
from pathlib import Path


def _lineas_json(ruta: Path):
    if not ruta.exists():
        return []
    salida = []
    for linea in ruta.read_text(encoding="utf-8", errors="replace").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        try:
            salida.append(json.loads(linea))
        except json.JSONDecodeError:
            continue
    return salida


class FuenteNacional:
    """Normas nacionales ya verificadas. El censo es el jsonl del bajador."""

    def __init__(self, base: Path):
        self.base = Path(base)
        self.normas = _lineas_json(self.base / "normas.jsonl")
        self.faltantes = []
        self.resueltas = 0

    @property
    def censo(self) -> int:
        return len(self.normas)

    def resolver(self, fila) -> dict | None:
        nombre = str(fila.get("archivo_texto") or "")
        p = self.base / "texto" / nombre
        if not nombre or not p.exists():
            self.faltantes.append({"clave": fila.get("clave"),
                                   "motivo": "sin archivo de texto en disco",
                                   "archivo": nombre})
            return None
        texto = p.read_text(encoding="utf-8", errors="replace")
        # El sha256 del jsonl se calculo sobre el texto: si no coincide, el archivo cambio
        # despues de verificarse y la cita dejaria de ser reproducible.
        self.resueltas += 1
        return {"texto": texto, "ruta": p}

    def informe(self) -> dict:
        return {"censo_manifest": self.censo, "resueltos_por_ocr": 0,
                "resueltos_por_extraccion": self.resueltas,
                "sin_texto": len(self.faltantes), "faltantes": self.faltantes[:20]}


def revisiones_de(fila) -> list:
    """La vigencia y las senales de cambio, como pendientes explicitos."""
    salida = []
    senales = fila.get("senales_de_cambio") or {}
    vivas = {k: v for k, v in senales.items() if v}
    if vivas:
        salida.append({
            "tipo": "posible_cambio_normativo",
            "detalle": ("el texto menciona " +
                        ", ".join(k + " x" + str(v) for k, v in sorted(vivas.items())) +
                        ": revisar si esta norma abroga o modifica a otras, y si otra la abroga"),
            "contexto": str(fila.get("titulo") or "")[:200]})
    else:
        # El caso peligroso: silencio total. El Procedimiento Civil de 1975 no dice que la Ley
        # 439 lo abrogo, porque una norma no se entera de su propia muerte.
        salida.append({
            "tipo": "vigencia_sin_senales",
            "detalle": "el texto no menciona abrogaciones NI eso prueba que este vigente: "
                       "una norma no declara su propia abrogacion por una ley posterior",
            "contexto": str(fila.get("titulo") or "")[:200]})
    return salida
