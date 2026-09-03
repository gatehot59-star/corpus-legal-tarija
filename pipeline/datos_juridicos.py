"""Lista de datos juridicos verificables de la Ley Departamental 007/2010 de Tarija.

Portada verbatim desde revision/contraste-ley007/verifica_datos_juridicos.py (misma
lista con la que se midio el OCR de Tesseract el 2026-09-02): 27 GRAVE + 13 MEDIO.
Se compara sobre texto SIN acentos: en Unicode los acentuados son caracteres de
palabra y comparar la codificacion en vez del contenido ya produjo 8 falsos faltantes.
"""
import re
import unicodedata


def plano(s: str) -> str:
    """Quita acentos y colapsa espacios. Sin esto se mide codificacion, no contenido."""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s)


DATOS = [
    ("GRAVE", "numero de la ley: 007", r"LEY\s*N.{0,3}\s*0?07\b"),
    ("GRAVE", "fecha: 06 DE NOVIEMBRE DE 2010", r"06 DE NOVIEMBRE DE 2010"),
    ("GRAVE", "Ley 4021 Regimen Electoral", r"Ley 4021 de Regimen Electoral"),
    ("GRAVE", "Art. 64.V de la Ley 4021", r"Art. 64.V"),
    ("GRAVE", "Ley nacional 017 referenciada", r"Ley N.{0,3} 017 del 24 de mayo de 2010"),
    ("GRAVE", "Art. 7.V de la Ley 017", r"Art. 7.V"),
    ("GRAVE", "Art. 17.I de la Ley 017", r"Art. 17.I\b"),
    ("GRAVE", "Art. 17.II de la Ley 017", r"Art. 17.II"),
    ("GRAVE", "Res. Pref. 144/2007 de 27 abril", r"144/2007 de 27 de abril del 2007"),
    ("GRAVE", "Res. Pref. 317/2007 de 17 sept", r"317/2007 de 17 de septiembre del 2007"),
    ("GRAVE", "Res. Pref. 131/2009 de 17 julio", r"131/2009 de fecha 17 de julio 2009"),
    ("GRAVE", "Res. Pref. 069/2010 de 23 feb", r"069/2010 del 23 de febrero del 2010"),
    ("GRAVE", "monto Bs. 1.000.000", r"Bs. 1.000.000"),
    ("GRAVE", "D.S. 0567 de 2 de julio de 2010", r"D.S. 0567 de fecha 2 de julio de 2010"),
    ("GRAVE", "Decreto Supremo 0181", r"Decreto Supremo N.{0,3} 0181"),
    ("GRAVE", "Art. 272 de la CPE", r"Art. 272"),
    ("GRAVE", "Art. 61 Ley Marco Autonomias", r"Art. 61 de la Ley Marco de Autonomias"),
    ("GRAVE", "Art. 28 de la Ley 1178", r"Art. 28 de la Ley 1178"),
    ("GRAVE", "articulo 72 de las NB-SABS", r"articulo 72 de las NB-SABS"),
    ("GRAVE", "Contratacion Menor: Bs 1 a 20.000", r"Bs.- 1 a Bs.- 20.000"),
    ("GRAVE", "ANPE: Bs 20.001 a 1.000.000", r"Bs. 20.001 a Bs.- 1.000.000"),
    ("GRAVE", "once secciones de provincia", r"once secciones de provincia"),
    ("GRAVE", "ocho secciones que no pertenecen", r"ocho secciones de provincia"),
    ("GRAVE", "las restantes ocho, a la Asamblea", r"restantes\s+ocho Ejecutivos"),
    ("GRAVE", "POA 2011", r"POA 2011"),
    ("GRAVE", "promulgada: veinticinco de nov", r"veinticinco dias del mes de noviembre de 2010"),
    ("GRAVE", "sancionada: seis de noviembre", r"seis dias del mes de noviembre de dos mil diez"),
    ("MEDIO", "ARTICULO PRIMERO (OBJETO)", r"ARTICULO PRIMERO. \(OBJETO\)"),
    ("MEDIO", "ARTICULO SEGUNDO (ATRIBUCIONES)", r"ARTICULO SEGUNDO. \(ATRIBUCIONES"),
    ("MEDIO", "ARTICULO TERCERO (AUTORIZACION)", r"ARTICULO TERCERO. \(AUTORIZACION\)"),
    ("MEDIO", "ARTICULO CUARTO (CONTINUIDAD)", r"ARTICULO CUARTO. \(CONTINUIDAD\)"),
    ("MEDIO", "ARTICULO QUINTO (ADMIN Y CONTROL)", r"ARTICULO QUINTO. \(ADMINISTRACION Y CONTROL\)"),
    ("MEDIO", "DISPOSICION TRANSITORIA UNICA", r"DISPOSICION TRANSITORIA"),
    ("MEDIO", "firma Aluida Vilte Farfan", r"Aluida Vilte Farfan"),
    ("MEDIO", "firma Justino Zambrana Cachari", r"Zambrana Cachari"),
    ("MEDIO", "firma Jose Amas Veliz", r"Am[a-z]s Veliz"),
    ("MEDIO", "firma Jose Quecana Quispe", r"Que[a-z]a[a-z]a Quispe"),
    ("MEDIO", "Entre Rios, provincia O'Connor", r"Entre Rios, provincia O'Connor"),
    ("MEDIO", "entidades SEDAG PRONEFA CODEFAUNA", r"SEDAG, PRONEFA, CODEFAUNA"),
    ("MEDIO", "direccion Calle 15 de Abril", r"Calle 15 de Abril"),
]


def puntuar(texto: str) -> dict:
    """Devuelve el detalle y el agregado de los datos hallados en un texto OCR."""
    todo = plano(texto)
    filas, faltan_grave, faltan_medio = [], 0, 0
    for grav, etq, pat in DATOS:
        hallado = bool(re.search(pat, todo))
        if not hallado:
            faltan_grave += grav == "GRAVE"
            faltan_medio += grav == "MEDIO"
        filas.append({"gravedad": grav, "dato": etq, "hallado": hallado})
    total = len(DATOS)
    hallados = total - faltan_grave - faltan_medio
    return {
        "total": total,
        "hallados": hallados,
        "faltan_GRAVE": faltan_grave,
        "faltan_MEDIO": faltan_medio,
        "pct": round(100.0 * hallados / total, 1),
        "veredicto": "APTO" if faltan_grave == 0 else "REVISAR: falta dato GRAVE",
        "filas": filas,
    }
