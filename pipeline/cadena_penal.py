"""ANTES DE FIRMAR: el instrumento dice que el Codigo de Procedimiento Penal (Ley 1970)
y la Ley 1768 estan 'Abrogadas por el Codigo del Sistema Penal, 20 de diciembre de 2017'.

Pero un abrogador puede estar muerto. Si la norma que mata fue abrogada ANTES de entrar
en vigencia, la abrogacion nunca surtio efecto y la victima sigue VIVA. Escribir
'derogada' ahi seria el peor error posible en la base de un abogado: le hace descartar
el codigo que si tiene que aplicar.

Se mide la cadena hacia arriba con el MISMO instrumento, y se lee el texto del abrogador
del abrogador. Sin esto no se escribe nada.
"""
import os, re, ssl, sys, urllib.request
sys.path.insert(0, "/workspace/ab-probe-20260903")
from vig_nac3 import leer, baja

def texto(h):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))

# el Codigo del Sistema Penal es la Ley 1005 de 2017
for ident in ("BO-COD-L1005.xhtml", "BO-L-N1005.xhtml", "BO-COD-20171220.xhtml"):
    h = baja(ident)
    if h.startswith("ERROR:") or "inexistente" in h[:3000]:
        print(ident, "-> no existe o error")
        continue
    print("=" * 78)
    print("ENCONTRADO:", ident, "| bytes", len(h))
    t = texto(h)
    print("  titulo:", t[:110].strip())
    r, err = leer(ident)
    if err:
        print("  no medible:", err); continue
    muertes, cambios = r
    print("  ESTA ABROGADO?:", muertes or "NO declara abrogacion")
    for e, i, tt in muertes:
        print("     ", e, "->", i, "|", tt[:80])
        # y el que lo abroga, que dice en su texto
        h2 = baja(i.replace(".html", ".xhtml"))
        if not h2.startswith("ERROR:"):
            t2 = texto(h2)
            print("      titulo del abrogador:", t2[:100].strip())
            for m in re.finditer(r"(?:se\s+)?(?:abrog|derog)\w*[^.;]{0,240}", t2, re.I):
                frag = m.group(0)
                if "1005" in frag or "Sistema Penal" in frag:
                    print("      CRUDO:", frag[:260])
                    break
    break
