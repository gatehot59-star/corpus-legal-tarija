"""Test del nombre de archivo seguro. Existe porque este bug tiro 18 de 20 shards.

El OCR de los 20 shards salio bien (paso 5 = success en los 20). Lo que fallo fue SUBIR el
artefacto, y la causa es un nombre: 41 de los 784 documentos no tienen `numero` en el
manifiesto y el codigo escribia "?" literal, que upload-artifact v4 rechaza.

La prediccion que lo confirmo: los unicos shards que podian subir eran los que NO escribieron
ningun archivo con "?", o sea aquellos donde todos sus documentos sin numero superaban las 40
paginas y se descartaban antes de escribir. Predijo [16, 17]; los que subieron fueron
exactamente [16, 17].
"""
import ocr_masivo as om

CASOS = [
    ("tarija_leyes", "007", "tarija_leyes-007-abcd1234"),
    ("tarija_rpa", None, "tarija_rpa-sin-numero-abcd1234"),
    ("tarija_rpa", "", "tarija_rpa-sin-numero-abcd1234"),
    ("tarija_rpa", "?", "tarija_rpa-sin-numero-abcd1234"),
    ("tarija_rpa", "N* 002", "tarija_rpa-N_002-abcd1234"),
    ("tarija_rpa", "12/2020", "tarija_rpa-12_2020-abcd1234"),
    ("tarija_rpa", "N\u00ba 480", "tarija_rpa-N_480-abcd1234"),
    (None, "007", "sin-fuente-007-abcd1234"),
]

PROHIBIDOS = set("?*:\"<>|\\/ ")
fallos = []

for fuente, numero, esperado in CASOS:
    real = om.stem_seguro(fuente, numero, "abcd1234")
    ok = real == esperado and not (set(real) & PROHIBIDOS)
    print(("VERDE " if ok else "ROJO  ") + f"{fuente!r},{numero!r} -> {real!r}"
          + ("" if ok else f"  ESPERADO {esperado!r}"))
    if not ok:
        fallos.append((numero, real))

# Ningun stem puede quedar vacio, empezar con guion ni traer "..": un nombre asi rompe el
# glob del consolidador o se escapa del directorio.
for fuente, numero, _ in CASOS:
    s = om.stem_seguro(fuente, numero, "abcd1234")
    if not s or s.startswith("-") or ".." in s:
        print("ROJO stem degenerado: " + repr(s))
        fallos.append((numero, s))

print()
if fallos:
    print("ROJO: " + repr(fallos))
    raise SystemExit(1)
print("VERDE: ningun stem lleva caracteres que upload-artifact rechaza")
