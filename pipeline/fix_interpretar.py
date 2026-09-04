#!/usr/bin/env python3
"""ROJO del banco: 'Ley 1970' devolvia cita_no_interpretable. Mi regex borraba 1970
como ANIO y no quedaba numero. El Codigo de Procedimiento Penal ES la Ley 1970: la
cita mas importante del corpus era la que el endpoint no entendia.

Y de paso el denominador de /estado: 1049 mete las Resoluciones del Pleno, que no son
leyes. Se declaran los DOS numeros en vez de elegir el que conviene.

Entrada api_v4.py md5 3ef17284a5abf4415d1214e71e89ba3a
"""
import hashlib, sys

VIEJO = "3ef17284a5abf4415d1214e71e89ba3a"

VIEJO_INTERP = '''    anio = None
    ma = ANIO_CITA.search(plano)
    numero = None
    sin_anio = ANIO_CITA.sub(" ", plano) if ma else plano
    mn = NUM_CITA.search(sin_anio)
    if mn:
        numero = int(mn.group(1))
        if mn.group(2):
            anio = mn.group(2)
    if ma and not anio:
        anio = ma.group(1)
    return tipo, numero, anio'''

NUEVO_INTERP = '''    # 'Ley 1970' es el Codigo de Procedimiento Penal, no una ley del ano 1970. Con UN
    # solo numero en la cita, ese numero es el NUMERO. El ano solo existe si hay otro
    # numero, o si viene precedido de 'de'/'del'.
    anio = None
    numero = None
    m_barra = re.search(r"\\b(\\d{1,4})\\s*/\\s*(19\\d\\d|20\\d\\d)\\b", plano)
    if m_barra:
        return tipo, int(m_barra.group(1)), m_barra.group(2)
    m_de = re.search(r"\\bde[l]?\\s+(?:\\d{1,2}\\s+de\\s+\\w+\\s+de\\s+)?(19\\d\\d|20\\d\\d)\\b", plano)
    if m_de:
        anio = m_de.group(1)
        plano_sin = plano[:m_de.start()] + " " + plano[m_de.end():]
    else:
        plano_sin = plano
    nums = re.findall(r"\\d{1,4}", plano_sin)
    if not nums and anio:
        # la cita era solo el ano: no alcanza para identificar una norma
        return tipo, None, anio
    if len(nums) >= 2 and not anio:
        for i, n in enumerate(nums):
            if re.fullmatch(r"19\\d\\d|20\\d\\d", n) and i > 0:
                anio = n
                nums = nums[:i] + nums[i + 1:]
                break
    if nums:
        numero = int(nums[0])
    return tipo, numero, anio'''

VIEJO_NOTA = ('"nota": "Un Auto Supremo no se abroga: la vigencia normativa no le aplica. "\n'
              '                                 "El denominador honesto son las normas, no el corpus entero."},')
NUEVO_NOTA = ('"solo_leyes_y_nacionales": leyes_nac,\n'
              '                         "cobertura_solo_leyes_por_ciento": round(100.0 * medidas / leyes_nac, 2) if leyes_nac else 0,\n'
              '                         "nota": "Un Auto Supremo no se abroga: la vigencia normativa no le aplica. '
              'Se publican DOS denominadores porque los dos son defendibles: 1.049 incluye las Resoluciones del Pleno, '
              'y el mas estricto son las %d leyes departamentales mas las nacionales." % leyes_nac},')

VIEJO_Q = '    normas = DBC.execute'
NUEVO_Q = '    normas = DBC.execute'

R = [(VIEJO_INTERP, NUEVO_INTERP), (VIEJO_NOTA, NUEVO_NOTA),
     ('    con_nota = q("SELECT count(*) n FROM documentos WHERE derogada_por IS NOT NULL AND derogada_por <> \'\'")',
      '    con_nota = q("SELECT count(*) n FROM documentos WHERE derogada_por IS NOT NULL AND derogada_por <> \'\'")\n'
      '    leyes_nac = q("SELECT count(*) n FROM documentos WHERE tipo_norma=\'Ley Departamental\' OR jurisdiccion=\'nacional\'")')]

VERDES = ["m_barra", "m_de", "solo_leyes_y_nacionales", "leyes_nac", "cobertura_solo_leyes_por_ciento"]

def main(ruta):
    h = open(ruta, encoding="utf8").read()
    a = hashlib.md5(h.encode()).hexdigest()
    print("entrada md5", a)
    if a != VIEJO:
        print("ROJO: entrada inesperada, esperaba", VIEJO); return 1
    for i, (v, n) in enumerate(R, 1):
        c = h.count(v)
        if c != 1:
            print("ROJO: ancla", i, "aparece", c, "veces:", v[:70].replace("\n", " ")); return 1
        h = h.replace(v, n, 1)
        print("  ancla", i, "aplicada")
    for t in VERDES:
        if t not in h:
            print("ROJO: falta", t); return 1
    open(ruta, "w", encoding="utf8").write(h)
    print("VERDE salida md5", hashlib.md5(h.encode()).hexdigest())
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "api.py"))
