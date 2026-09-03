"""Extrae y normaliza citas legales SIN tocar el texto de la ley.

El defecto medido: Tesseract lee `Art. 17.I` como `Art. 17.1` y `Art. 17.II` como
`Art. 17.11`. Sobre 2.624 paginas eso son cientos de citas mal escritas, y una cita mal
escrita en un estudio juridico no es una errata: manda a leer otro articulo.

**La decision de diseno, y es la parte importante:** este modulo NO reescribe el cuerpo
del documento. Reescribir la fuente legal por inferencia es exactamente lo que no se
puede hacer: si el OCR dice `17.1` y el papel decia `17.1`, corregirlo a `17.I` fabrica
una ley que no existe. Asi que:

  1. El texto crudo queda verbatim y sigue siendo la fuente.
  2. Se emite una lista de CITAS con el crudo, la forma canonica probable y si es AMBIGUA.
  3. Las ambiguas van a una cola de revision humana con su linea y su contexto.
  4. El indice de busqueda recibe las DOS formas, asi que buscar "Art. 17.I" encuentra el
     documento aunque el OCR haya escrito "17.1", sin haber alterado la ley.

Por que `1` y `11` son sospechosos y `V` no: en la numeracion de paragrafos boliviana el
romano I es el que colisiona con el digito 1 y con la l minuscula. `V`, `X` y `IV` no
tienen homoglifo digito, y de hecho `Art. 64.V` y `Art. 7.V` salieron correctos en la
misma pagina donde `17.I` fallo. La ambiguedad es del caracter, no del motor.
"""
import json
import re
import unicodedata

# Sufijo de paragrafo: corrida de caracteres que PUEDEN ser el romano I mal leido.
# `1`, `l` (ele minuscula), `I`, `i` y `|` son los homoglifos que produce el OCR.
HOMOGLIFOS_DE_I = "1lIi|"

# IGNORECASE porque los encabezados vienen en mayusculas (`ARTICULO 3.II`) y el cuerpo en
# minusculas. El \b inicial evita engancharse al `art` que vive dentro de `cuarta` o `reparto`.
CITA = re.compile(
    r"""\bArt(?:\.|iculo)?                    # Art. / Articulo / ARTICULO / art
        \s*
        (?P<numero>\d{1,4})                   # 17
        \s*\.\s*
        (?P<sufijo>[1lIi|VXvx]{1,6})           # I / II / V / 1 / 11
        (?=\b|\.|,|\s|$)
    """,
    re.VERBOSE | re.IGNORECASE,
)


def plano(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def a_romano(sufijo: str):
    """Devuelve el romano canonico si el sufijo se puede leer como romano, si no None."""
    s = sufijo.strip()
    if not s:
        return None
    # Todo homoglifo de I: la cantidad de caracteres es la cantidad de I.
    if all(c in HOMOGLIFOS_DE_I for c in s):
        if len(s) > 3:            # IIII no existe en numeracion de paragrafos
            return None
        return "I" * len(s)
    # Mezclas con V/X: se normalizan los homoglifos a I y se valida el romano resultante.
    candidato = "".join("I" if c in HOMOGLIFOS_DE_I else c.upper() for c in s)
    if re.fullmatch(r"(?:I{1,3}|IV|V|VI{1,3}|IX|X|XI{1,3})", candidato):
        return candidato
    return None


def es_ambigua(sufijo: str) -> bool:
    """Ambigua = el sufijo tiene al menos un digito o una `l`, o sea pudo ser un inciso
    arabigo legitimo. `Art. 17.V` no es ambigua; `Art. 17.1` si."""
    return any(c in "1l|" for c in sufijo)


def extraer(texto: str, documento: str = "") -> dict:
    """Devuelve las citas halladas, la cola de revision y el texto de indice."""
    lineas = texto.splitlines()
    citas, revisar = [], []

    for n, linea in enumerate(lineas, start=1):
        for m in CITA.finditer(plano(linea)):
            crudo = m.group(0)
            sufijo = m.group("sufijo")
            romano = a_romano(sufijo)
            if romano is None:
                continue
            canonico = f"Art. {m.group('numero')}.{romano}"
            ambigua = es_ambigua(sufijo)
            registro = {
                "documento": documento,
                "linea": n,
                "crudo": crudo,
                "canonico_probable": canonico,
                "ambigua": ambigua,
                "contexto": linea.strip()[:200],
            }
            citas.append(registro)
            if ambigua and crudo.replace(" ", "") != canonico.replace(" ", ""):
                revisar.append(registro)

    # El indice recibe las dos formas. El cuerpo NO se toca.
    formas = sorted({c["canonico_probable"] for c in citas} | {c["crudo"] for c in citas})
    texto_indice = texto if not formas else texto + "\n\n[CITAS-NORMALIZADAS] " + " | ".join(formas)

    return {
        "documento": documento,
        "citas": citas,
        "total_citas": len(citas),
        "revision_humana": revisar,
        "total_revision": len(revisar),
        "texto_indice": texto_indice,
    }


def main() -> int:
    import argparse
    from pathlib import Path

    ap = argparse.ArgumentParser()
    ap.add_argument("--texto", required=True, help="archivo .txt con la salida cruda del OCR")
    ap.add_argument("--salida", default="", help="donde escribir citas.json (opcional)")
    a = ap.parse_args()

    p = Path(a.texto)
    r = extraer(p.read_text(encoding="utf-8", errors="replace"), documento=p.name)
    print(f"{p.name}: {r['total_citas']} citas, {r['total_revision']} a revision humana")
    for c in r["revision_humana"]:
        print(f"  linea {c['linea']}: '{c['crudo']}' -> probable '{c['canonico_probable']}'")
    if a.salida:
        salida = Path(a.salida)
        salida.parent.mkdir(parents=True, exist_ok=True)
        cuerpo = dict(r)
        cuerpo.pop("texto_indice")
        salida.write_text(json.dumps(cuerpo, ensure_ascii=False, indent=1), encoding="utf-8")
        (salida.parent / (p.stem + ".indice.txt")).write_text(r["texto_indice"], encoding="utf-8")
        print("escrito:", salida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
