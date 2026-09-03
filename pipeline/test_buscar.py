"""Falsador del buscador: consultas con resultado ESPERADO conocido, y consultas que deben
devolver CERO. Un buscador que solo se prueba con lo que encuentra no esta medido.

Los casos positivos se apoyan en documentos que ya medimos a mano en este proyecto (la Ley
Departamental 007/2010 y el Auto Supremo 0122/2026 de Sala Civil). Los negativos existen para
detectar el modo de falla mas peligroso de un indice: devolver cualquier cosa siempre.
"""
import sys

import buscar

DB = sys.argv[1] if len(sys.argv) > 1 else "corpus.db"
fallos = []


def caso(nombre, consulta, espera_min=1, debe_contener="", **filtros):
    filas = buscar.buscar(DB, consulta, limite=10, **filtros)
    ok = len(filas) >= espera_min
    detalle = ""
    if ok and debe_contener:
        hallado = any(debe_contener.lower() in (str(f.get("archivo", "")) + " "
                                                + str(f.get("numero", "")) + " "
                                                + str(f.get("fragmento", ""))).lower()
                      for f in filas)
        ok = hallado
        detalle = "" if hallado else (" (ninguno de los " + str(len(filas)) + " contiene "
                                      + repr(debe_contener) + ")")
    print(("VERDE " if ok else "ROJO  ") + nombre + ": " + str(len(filas)) + " resultados" + detalle)
    if not ok:
        fallos.append(nombre)


def caso_cero(nombre, consulta):
    filas = buscar.buscar(DB, consulta, limite=5)
    ok = len(filas) == 0
    print(("VERDE " if ok else "ROJO  ") + nombre + ": " + str(len(filas)) + " resultados"
          + ("" if ok else " (deberia ser 0)"))
    if not ok:
        fallos.append(nombre)


# Positivos sobre documentos ya verificados a mano.
caso("frase juridica comun", "prescripcion adquisitiva", espera_min=3)
caso("sin tildes encuentra con tildes", "prescripcion", espera_min=3)
caso("con tildes encuentra sin tildes", "prescripci\u00f3n", espera_min=3)
caso("numero de resolucion con barras", "AS/0122/2026", espera_min=1, debe_contener="0122")
caso("cita de articulo con romano", "Art. 17.I", espera_min=1)
caso("ley departamental por tema", "ejecutivos seccionales de desarrollo", espera_min=1)
caso("filtro por fuente", "recurso de casacion", espera_min=3, fuente="jurisprudencia_tsj")
caso("filtro por sala", "casacion", espera_min=1, sala="Sala Penal")
caso("materia que antes no existia", "beneficios sociales", espera_min=1)

# Negativos: si esto devuelve algo, el indice esta matcheando cualquier cosa.
caso_cero("palabra inexistente", "zzqxwvkj")
caso_cero("frase imposible", '"tribunal supremo de justicia de finlandia"')

print()
if fallos:
    print("ROJO: fallaron " + ", ".join(fallos))
    raise SystemExit(1)
print("VERDE: el buscador encuentra lo que debe y no inventa lo que no hay")
