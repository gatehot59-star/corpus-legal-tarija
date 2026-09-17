"""Fuente Tarija: el adaptador recorre el MANIFEST, no un directorio.

**Por que existe este archivo, con el numero que lo obligo.** El adaptador anterior hacia
`glob("corpus/texto/*.txt")`. Habia 1.031 documentos descargados y extraidos, pero 247 de ellos
viven en otro directorio (`11_TEXTO/`), asi que **para el adaptador no existian**. Entraron 784.
Y el invariante de la ingesta comparaba *lo que el adaptador ofrece* contra la base, o sea
comparaba el error consigo mismo: cerro en VERDE con `perdidos: 0` mientras faltaba el 24% del
corpus departamental, 2.928.976 caracteres, con 2019 al 24% y 2020 y 2026 en cero.

**La correccion de fondo no es agregar el directorio que faltaba: es cambiar quien manda.** El
censo es el **manifest de descarga**, que es el registro de lo que la fuente oficial entrego. Se
recorre fila por fila, y cada fila tiene que resolver su texto **o quedar declarada como
faltante con su motivo**. Un documento no puede desaparecer por vivir en la carpeta equivocada,
porque ya no se descubre por carpeta.

**Estructura esperada del directorio de origen:**

```plain
<origen>/
  indices/manifest.jsonl       <- censo: una Norma por linea (1.031)
  corpus/registros.jsonl       <- OCR masivo con citas normalizadas (784)
  corpus/texto/*.txt           <- su texto, con .indice.txt al lado
  11_TEXTO/*.txt               <- texto extraido por el pipeline (247)
```

Si falta el manifest, el adaptador **no adivina**: avisa y se comporta como el viejo, pero
declarando que corre sin censo. Degradar en silencio es lo que produjo este bug.

**Que texto se prefiere y por que:** cuando un documento tiene las dos vias, gana `corpus/texto`,
porque paso el OCR masivo y trae su indice de citas normalizadas al lado. `11_TEXTO` es el texto
que dejo la etapa `extraer` y no tiene citas. Medido hoy: la particion es **limpia**, 784 en una
via y 247 en la otra, cero solapamiento, cero archivos vacios.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


def _lineas_json(ruta: Path):
    """Lee jsonl tolerando comentarios de cabecera. El manifest v2 arranca con un `#`."""
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


def citas_de(p: Path) -> str:
    """Citas normalizadas del indice que dejo el OCR, si existe."""
    idx = p.with_name(p.stem + ".indice.txt")
    if not idx.exists():
        return ""
    m = re.search(r"\[CITAS-NORMALIZADAS\](.*)$",
                  idx.read_text(encoding="utf-8", errors="replace"), re.S)
    return m.group(1).strip() if m else ""


class FuenteTarija:
    """Resuelve, para cada fila del manifest, su texto y su procedencia.

    Lleva la cuenta de lo que resolvio y de lo que no, para que la ingesta pueda exigir que el
    total coincida con el censo.
    """

    def __init__(self, base: Path):
        self.base = Path(base)
        self.manifest = _lineas_json(self.base / "indices" / "manifest.jsonl")
        self.registros = _lineas_json(self.base / "corpus" / "registros.jsonl")
        # El sha256 del PDF es la unica clave que cruza las dos vias. Medido: 784/784 cruzan.
        self.por_sha = {}
        for r in self.registros:
            sha = str(r.get("sha256_esperado") or "")
            if sha:
                self.por_sha[sha] = r
        self.faltantes = []
        self.via = {"ocr": 0, "extraido": 0}

    @property
    def censo(self) -> int:
        """Cuantos documentos declara la fuente. 0 significa que no hay manifest."""
        return len(self.manifest)

    def _texto_ocr(self, fila) -> tuple:
        """Via preferida: el texto que paso el OCR masivo, con sus citas."""
        r = self.por_sha.get(str(fila.get("sha256") or ""))
        if not r:
            return None, None, None
        nombre = str(r.get("archivo_texto") or "")
        p = self.base / "corpus" / "texto" / nombre
        if not nombre or not p.exists():
            return None, None, None
        return p.read_text(encoding="utf-8", errors="replace"), r, p

    def _texto_extraido(self, fila) -> tuple:
        """Via de respaldo: el texto que dejo la etapa `extraer`, sin citas."""
        rt = str(fila.get("ruta_texto") or "")
        if not rt:
            return None, None
        p = self.base / rt
        if not p.exists():
            return None, None
        return p.read_text(encoding="utf-8", errors="replace"), p

    def resolver(self, fila) -> dict | None:
        """Texto + metadatos de una fila del manifest. None si no se pudo, y queda declarado."""
        texto, reg, ruta = self._texto_ocr(fila)
        if texto is not None:
            self.via["ocr"] += 1
            return {"texto": texto, "registro": reg, "ruta": ruta, "via": "ocr",
                    "citas": citas_de(ruta)}
        texto, ruta = self._texto_extraido(fila)
        if texto is not None:
            self.via["extraido"] += 1
            return {"texto": texto, "registro": {}, "ruta": ruta, "via": "extraido",
                    "citas": ""}
        etapas = fila.get("etapas") or {}
        self.faltantes.append({
            "numero": fila.get("numero"), "gestion": fila.get("gestion"),
            "sha256": fila.get("sha256"), "ruta_texto": fila.get("ruta_texto"),
            "motivo": "sin texto en ninguna via",
            "etapas": {k: (v or {}).get("estado") for k, v in etapas.items()}})
        return None

    def informe(self) -> dict:
        return {"censo_manifest": self.censo, "resueltos_por_ocr": self.via["ocr"],
                "resueltos_por_extraccion": self.via["extraido"],
                "sin_texto": len(self.faltantes),
                "faltantes": self.faltantes[:20]}


def confianza_de(fila, reg, via: str) -> str:
    """Confianza del texto, y NUNCA se infla por conveniencia.

    Los 148 documentos que la etapa `estructurar` marco `REVISION_HUMANA` entran con esa
    etiqueta, no con `media`. Entran porque un documento que existe y se declara dudoso es mas
    util que un documento ausente, y la API ya obliga al agente a advertirlo antes de citar
    textual. Lo que estaria mal es meterlos callado.
    """
    if str(reg.get("estado") or "") == "REVISION_HUMANA":
        return "revision_humana"
    etapas = fila.get("etapas") or {}
    estructurar = str((etapas.get("estructurar") or {}).get("estado") or "")
    if estructurar == "REVISION_HUMANA":
        return "revision_humana"
    if via == "ocr":
        return "media"
    # El texto extraido sin OCR ni gate no tiene control de calidad medido.
    return "media" if int(fila.get("caracteres") or 0) > 0 else "revision_humana"
