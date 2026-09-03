"""Tests del normalizador de citas. Incluye los casos ADVERSOS: lo que NO debe tocar.

Un normalizador que solo se prueba con sus aciertos es un normalizador sin falsador.
"""
import normalizar_citas as nc


def caso(nombre, texto, espera_canonicos=(), espera_revision=0, espera_citas=None):
    r = nc.extraer(texto, documento=nombre)
    ok = True
    canonicos = [c["canonico_probable"] for c in r["citas"]]
    for e in espera_canonicos:
        if e not in canonicos:
            print(f"ROJO {nombre}: falta canonico {e!r}, hallados {canonicos}")
            ok = False
    if r["total_revision"] != espera_revision:
        print(f"ROJO {nombre}: revision {r['total_revision']} != {espera_revision} -> {r['revision_humana']}")
        ok = False
    if espera_citas is not None and r["total_citas"] != espera_citas:
        print(f"ROJO {nombre}: citas {r['total_citas']} != {espera_citas} -> {canonicos}")
        ok = False
    print(("VERDE " if ok else "ROJO  ") + nombre)
    return ok


todo = []

# El defecto medido en la Ley 007, textual del OCR de Tesseract.
todo.append(caso("defecto medido 17.1 y 17.11",
                 "en su Art. 17.1 establece que, los Ejecutivos\nen su Art. 17.11 establece que los recursos",
                 espera_canonicos=("Art. 17.I", "Art. 17.II"), espera_revision=2, espera_citas=2))

# Los que YA salian bien y no deben cambiar ni entrar a revision.
todo.append(caso("V no es ambigua", "estableció en su Art. 64.V. la elección",
                 espera_canonicos=("Art. 64.V",), espera_revision=0, espera_citas=1))
todo.append(caso("V simple", "en su Art. 7.V, establece que",
                 espera_canonicos=("Art. 7.V",), espera_revision=0, espera_citas=1))

# Ya canonico: se detecta pero NO va a revision, porque no hay nada que corregir.
todo.append(caso("ya canonico I", "el Art. 17.I dispone",
                 espera_canonicos=("Art. 17.I",), espera_revision=0, espera_citas=1))

# ADVERSOS: nada de esto debe generar una cita.
todo.append(caso("articulo sin sufijo no es cita", "el Art. 272, la disposición adicional",
                 espera_revision=0, espera_citas=0))
todo.append(caso("ley con numero no es articulo", "la Ley 4021 de Régimen Electoral",
                 espera_revision=0, espera_citas=0))
todo.append(caso("monto con puntos no es cita", "un monto de Bs. 1.000.000 para el POA 2011",
                 espera_revision=0, espera_citas=0))
todo.append(caso("resolucion con barra no es cita", "Res. Pref. 144/2007 de 27 de abril",
                 espera_revision=0, espera_citas=0))
todo.append(caso("IIII no es paragrafo valido", "el Art. 5.1111 dice",
                 espera_revision=0, espera_citas=0))

# ARTICULO en mayusculas y con tilde, que es como aparece en los encabezados.
todo.append(caso("ARTICULO mayusculas", "ARTICULO 3.II establece",
                 espera_canonicos=("Art. 3.II",), espera_revision=0, espera_citas=1))
todo.append(caso("Articulo con tilde", "el Artículo 9.1 remite",
                 espera_canonicos=("Art. 9.I",), espera_revision=1, espera_citas=1))

# El texto de indice conserva el cuerpo intacto: la ley no se reescribe.
cuerpo = "en su Art. 17.1 establece que, los Ejecutivos"
r = nc.extraer(cuerpo, "intacto")
if not r["texto_indice"].startswith(cuerpo):
    print("ROJO: el cuerpo del documento fue alterado")
    todo.append(False)
elif "Art. 17.I" not in r["texto_indice"]:
    print("ROJO: el indice no recibio la forma canonica")
    todo.append(False)
else:
    print("VERDE cuerpo intacto y las dos formas en el indice")
    todo.append(True)

print(f"\n{sum(todo)}/{len(todo)} verdes")
raise SystemExit(0 if all(todo) else 1)
