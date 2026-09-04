"""Corpus nacional desde LexiVox, con verificación de identidad norma por norma.

**Por que NO se toma de los productos comerciales.** LeyNova, SILEG, Difusion Juridica y
Derechoteca son bases cerradas por suscripcion. Copiar de ahi tiene tres problemas y el tercero
es el que mata al proyecto:

1. Sus terminos lo prohiben, y es una base con nombre y responsable identificable.
2. Su texto no es citable: si el corpus dice "segun LeyNova", el abogado no puede verificar nada
   contra el Estado.
3. **Destruye el unico diferencial que tenemos.** El valor de este corpus es que **cada documento
   se puede verificar contra la fuente oficial**, con su URL y su sha256. Un texto de tercero sin
   procedencia oficial convierte el sistema en una copia peor de lo que copia.

Lo correcto es lo contrario: **usar el trabajo ajeno como INDICE y bajar de la fuente oficial.**
Eso es legitimo, es gratis, y produce un documento citable. `aBOgacion` (repo publico) dice que
la Ley X existe; LexiVox (que publica el texto oficial) la entrega con su URL.

**Dos guards que salieron de medir LexiVox hoy, y los dos son trampas silenciosas:**

1. **Devuelve HTTP 200 para normas que NO tiene**, con el cuerpo "Norma inexistente en la base de
   datos" y 216 caracteres. Un `status == 200` **no prueba que el documento exista**: hay que leer
   el cuerpo. Sin este guard entran fantasmas de 216 bytes como si fueran códigos.
2. **El patron del identificador CAMBIA entre normas**, y confundirlo trae la norma equivocada con
   el numero correcto:

```plain
BO-L-1970   -> Codigo de Procedimiento Penal, 25-mar-1999   437 articulos   OK
BO-L-N1970  -> INEXISTENTE (con HTTP 200)
BO-L-N439   -> Codigo Procesal Civil, 19-nov-2013           509 articulos   OK
BO-L-439    -> Ley N 439 de 18 de diciembre de 1968         3 articulos     OTRA NORMA
```

**`BO-L-439` y `BO-L-N439` son normas distintas con el mismo numero.** Por eso cada objetivo
declara **que titulo espera**, se prueban las variantes de identificador, y **se acepta solo si el
titulo real coincide**. Un numero de ley no identifica una norma; el numero mas el ano si.

**Y el 509 confirma al auditor:** dijo que la Ley 439 tiene 509 articulos y este script cuenta
509 unicos en el texto oficial. Su dato era exacto.

Uso:

```bash
python3 pipeline/nacional_lexivox.py --salida /ruta/nacional
```
"""
import argparse
import hashlib
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.request

BASE = "https://www.lexivox.org/norms/%s.xhtml"
UA = {"User-Agent": "Mozilla/5.0 (compatible; corpus-legal-bolivia/1.0; +publico)"}
INEXISTENTE = "Norma inexistente en la base de datos"

_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE

# Cada objetivo declara el TITULO QUE ESPERA. Si el que llega no coincide, se rechaza: es la
# unica defensa contra traer la norma equivocada con el numero correcto.
# (clave, variantes de identificador, fragmento esperado del titulo, tipo, numero, anio, materia)
OBJETIVOS = [
    ("cpe_2009", ["BO-CPE-20090207"], "constituci", "Constitucion Politica del Estado",
     "CPE", "2009", "Constitucional"),
    ("codigo_civil", ["BO-DL-12760", "BO-COD-DL12760"], "c\u00f3digo civil", "Codigo",
     "12760", "1975", "Civil"),
    ("codigo_procesal_civil", ["BO-L-N439"], "c\u00f3digo procesal civil", "Codigo",
     "439", "2013", "Civil"),
    ("codigo_procedimiento_penal", ["BO-L-1970"], "1970", "Codigo",
     "1970", "1999", "Penal"),
    ("codigo_penal", ["BO-DL-10426", "BO-COD-DL10426", "BO-DL-1768", "BO-L-1768"],
     "c\u00f3digo", "Codigo", "10426", "1972", "Penal"),
    ("codigo_familia", ["BO-COD-DL10426"], "c\u00f3digo de familia", "Codigo",
     "10426", "1972", "Familia"),
    ("codigo_comercio", ["BO-DL-14379", "BO-COD-DL14379"], "comercio", "Codigo",
     "14379", "1977", "Comercial"),
    ("codigo_tributario", ["BO-L-2492", "BO-L-N2492"], "tributario", "Codigo",
     "2492", "2003", "Tributaria"),
    ("codigo_nna", ["BO-L-N548"], "ni\u00f1a", "Codigo", "548", "2014", "Familia"),
    ("ley_trabajo", ["BO-DL-19421208", "BO-L-19421208", "BO-DL-224"], "trabaj", "Ley",
     "LGT", "1942", "Del Trabajo"),
    ("ley_1178_safco", ["BO-L-1178"], "1178", "Ley", "1178", "1990", "Administrativa"),
    ("ley_348", ["BO-L-N348"], "violencia", "Ley", "348", "2013", "Penal"),
    ("ley_1173", ["BO-L-N1173"], "abreviaci", "Ley", "1173", "2019", "Penal"),
    ("ley_025_organo_judicial", ["BO-L-N25", "BO-L-N025", "BO-L-25"], "judicial", "Ley",
     "025", "2010", "Administrativa"),
    ("ley_031_autonomias", ["BO-L-N31", "BO-L-N031", "BO-L-31"], "autonom", "Ley",
     "031", "2010", "Administrativa"),
    ("codigo_seguridad_social", ["BO-COD-19561214", "BO-DL-19561214"], "seguridad social",
     "Codigo", "CSS", "1956", "Seguridad Social"),
]


def bajar(url, intentos=3):
    ultimo = ""
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90, context=_CTX) as r:
                return r.status, r.read().decode("utf-8", "replace"), ""
        except urllib.error.HTTPError as e:
            return e.code, "", "HTTP " + str(e.code)
        except Exception as e:
            ultimo = type(e).__name__ + ": " + str(e)[:50]
            time.sleep(3 * (i + 1))
    return "ERR", "", ultimo


def a_texto(html: str) -> str:
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</(p|div|tr|h[1-6]|li)>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    for a, b in (("&nbsp;", " "), ("&#160;", " "), ("&amp;", "&"), ("&lt;", "<"),
                 ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'")):
        s = s.replace(a, b)
    # La cabecera de la interfaz de LexiVox no es parte de la norma.
    for ruido in ("Aumentar el tama\u00f1o del texto", "Reducir el tama\u00f1o del texto",
                  "Ver el documento PDF", "Conectarse al sistema", "Suscribirse a LexiVox"):
        s = s.replace(ruido, " ")
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def titulo_de(html: str) -> str:
    m = re.search(r"(?is)<title>(.*?)</title>", html)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def articulos_unicos(texto: str) -> int:
    return len(set(re.findall(r"(?i)art[\u00ed i]culo\s*(\d+)", texto)))


def resolver(variantes, esperado):
    """Prueba las variantes de identificador y acepta la primera cuyo TITULO coincida.

    Devuelve (identificador, url, titulo, html, intentos). El registro de intentos importa: deja
    escrito que un 200 con "Norma inexistente" no es un hallazgo.
    """
    intentos = []
    for v in variantes:
        url = BASE % v
        st, html, err = bajar(url)
        if err or not html:
            intentos.append({"id": v, "resultado": "error", "detalle": err or "vacio"})
            continue
        if INEXISTENTE in html:
            intentos.append({"id": v, "resultado": "inexistente_con_200"})
            continue
        tit = titulo_de(html)
        if esperado.lower() not in tit.lower():
            intentos.append({"id": v, "resultado": "titulo_no_coincide", "titulo": tit})
            continue
        return v, url, tit, html, intentos
    return None, None, None, None, intentos


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", required=True)
    ap.add_argument("--minimo-chars", type=int, default=3000)
    a = ap.parse_args()

    os.makedirs(os.path.join(a.salida, "texto"), exist_ok=True)
    jsonl = os.path.join(a.salida, "normas.jsonl")
    filas, fallidos = [], []

    for clave, variantes, esperado, tipo, numero, anio, materia in OBJETIVOS:
        ident, url, tit, html, intentos = resolver(variantes, esperado)
        if not ident:
            fallidos.append({"clave": clave, "intentos": intentos})
            print("  ROJO   %-28s -> ninguna variante sirvio: %s" %
                  (clave, json.dumps(intentos, ensure_ascii=False)[:110]), flush=True)
            continue
        texto = a_texto(html)
        if len(texto) < a.minimo_chars:
            fallidos.append({"clave": clave, "id": ident,
                             "motivo": "texto de %d chars, menos que el minimo" % len(texto)})
            print("  ROJO   %-28s -> texto corto: %d chars" % (clave, len(texto)), flush=True)
            continue
        sha = hashlib.sha256(texto.encode("utf-8")).hexdigest()
        nombre = clave + ".txt"
        open(os.path.join(a.salida, "texto", nombre), "w", encoding="utf-8").write(texto)
        # Señales de abrogacion en el propio texto. NO deciden la vigencia: la declaran para que
        # un humano la revise. Poner `vigente=True` sin verificar es el error que este proyecto
        # ya midio con un Codigo de 1975 indexado como si estuviera vivo.
        senales = {m: len(re.findall(m, texto, re.I))
                   for m in ("abrogad", "derogad", "modificad")}
        fila = {"clave": clave, "id_lexivox": ident, "fuente_url": url, "titulo": tit,
                "tipo_norma": tipo, "numero": numero, "anio": anio, "materia": materia,
                "chars": len(texto), "articulos_unicos": articulos_unicos(texto),
                "sha256": sha, "archivo_texto": nombre,
                "senales_de_cambio": senales, "vigente": None,
                "intentos_descartados": intentos}
        filas.append(fila)
        print("  OK     %-28s %-14s art:%-5d %7d chars | %s" %
              (clave, ident, fila["articulos_unicos"], len(texto), tit[:52]), flush=True)

    with open(jsonl, "w", encoding="utf-8") as f:
        f.write("# corpus nacional desde LexiVox " + time.strftime("%Y-%m-%dT%H:%M:%S") + "\n")
        for fila in filas:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")

    print()
    print("NORMAS OBTENIDAS: %d de %d objetivos" % (len(filas), len(OBJETIVOS)))
    print("caracteres:", sum(x["chars"] for x in filas))
    if fallidos:
        print("NO OBTENIDAS:", len(fallidos))
        for x in fallidos:
            print("   ", json.dumps(x, ensure_ascii=False)[:150])
        print("El corpus nacional NO esta completo y esto lo declara.")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
