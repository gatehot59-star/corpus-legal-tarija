# EXP-TCP-003 · La licencia, medida en la ley · y la fuente correcta no era el buscador

**Medido:** 2026-09-05 · brain-env
**Pregunta que bloqueaba la ingesta:** ¿se puede incorporar y redistribuir el texto de las resoluciones del TCP?

---

## Resumen

El camino cambió. **No hay que scrapear la SPA:** el propio TCP publica la **Gaceta Constitucional Plurinacional** en tomos PDF descargables **con texto nativo**, y esa publicación **está mandada por ley**. Y de paso **refuto una suposición cómoda mía**: la ley de derecho de autor boliviana **no** excluye los textos judiciales.

---

## 1 · Lo que dice la ley, medido en el texto (no de memoria)

Fuente: `https://www.lexivox.org/norms/BO-L-N254.html` (Código Procesal Constitucional), 148.444 B, extraídos 97.696 caracteres.

**Art. 19 (Publicación), verbatim:**

> «Las sentencias, declaraciones y autos constitucionales se publicarán en la Gaceta Constitucional, cuya periodicidad será mensual. El Tribunal Constitucional Plurinacional difundirá sus resoluciones, además de los mecanismos electrónicos, a través de los medios que vea conveniente.»

**Art. 15 (Carácter obligatorio, vinculante y valor jurisprudencial), verbatim:**

> «Las razones jurídicas de la decisión, en las resoluciones emitidas por el Tribunal Constitucional Plurinacional constituyen jurisprudencia y tienen carácter vinculante para los Órganos del poder público, legisladores, autoridades, tribunales y **particulares**.»

Dos hechos legales, no opiniones: la publicación es **obligatoria**, y la jurisprudencia obliga **a los particulares**. Una norma que obliga a un particular tiene que poder ser conocida por él.

## 2 · REFUTO mi propia suposición: la Ley 1322 NO excluye los textos judiciales

Iba a apoyarme en el carve-out clásico de "textos oficiales de carácter legislativo, administrativo o judicial". **En Bolivia no existe.** Bajé la Ley 1322 (97.031 B) y leí su **Título VI, De las limitaciones al Derecho de Autor**, entero. Tiene **tres artículos y ninguno es ese**:

| Art. | Qué permite |
|---|---|
| 24 | derecho de **cita** (fragmentos cortos, con fuente y autor) |
| 25 | utilización por **necesidad pública**, con indemnización |
| 26 | publicación por terceros si los herederos no publican en 5 años |

Busqué `judicial` en toda la ley: **3 apariciones**, y las tres son procesales (persecución judicial, Judicatura Penal, custodia judicial). **Cero exclusión de textos oficiales.**

O sea: el argumento fuerte **no** es "no está protegido por derecho de autor", es **la publicidad mandada por los arts. 15 y 19 del CPCo**. Si hubiera citado el carve-out habría fundado la decisión en una norma inexistente.

## 3 · Qué dice el TCP en su propio sitio: nada

| Sujeto medido | `derechos reservados` | `aviso legal` | `términos` | `condiciones` | `prohibid` |
|---|---|---|---|---|---|
| `tcpbolivia.bo` (222.431 B) | 0 | 0 | 0 | 0 | 0 |
| bundle del buscador (583.304 B) | 0 | 0 | 0 | 0 | 0 |

Lo único que hay es el pie de página, verbatim: `© Tribunal Constitucional plurinacional de bolivia`.

**Y esto NO es una autorización.** Es una **ausencia de términos**, que es otra cosa. Un símbolo © sin condiciones no concede permiso ni lo niega. Lo registro como ausencia medida, no como luz verde.

## 4 · El hallazgo que cambia el plan: la Gaceta oficial sirve los tomos

Encontrado leyendo el HTML del portal, no adivinando: `https://tcpbolivia.bo/gaceta/`, con años 2018 a 2022 y desglose por semestre. En `gaceta2022s1` hay **5 tomos PDF** (`TomoIs12022.pdf` … `TomoVs12022.pdf`).

Bajé y medí **uno**:

```
tomo 200 41436252 application/pdf
sha256 b0ab8830f9503a68156efba1117924637244e6e570475fe5e07f2b8c305cb704
paginas 5851
chars extraidos 25.094.238   (texto NATIVO, sin OCR)
SCP unicas          388
"Departamento:"     389
"Departamento: Tarija"  19
DECLARACI...         5
AUTO CONSTITU...    31
```

Tres cosas que esto habilita y el buscador no:

1. **Es la fuente oficial mandada por el art. 19**, no una API interna. Un PDF con sha256 es procedencia verificable; una SPA firmada con `x-hash` no lo es.
2. **Texto nativo, cero OCR.** El corpus no degrada su `confianza_texto`.
3. **389 `Departamento:` contra 388 SCP**: el campo aparece en casi todas, así que se puede filtrar Tarija desde el propio documento oficial.

---

## Trampas de medición cazadas en esta corrida

1. `grep -c` cuenta **líneas**, no resoluciones: daba 392 donde las SCP únicas son **388**. Reporté el número fino con regex, no el del grep.
2. Mis primeros conteos de `AUTO CONSTITUCIONAL` y `DECLARACION CONSTITUCIONAL` dieron **0 y 0**, y era **falso**: buscaba sin tilde. Con `DECLARACI` y `AUTO CONSTITU` dan 5 y 31. Un cero por acento es un cero que miente.
3. `pdftotext` **no existe** en brain-env (`sh: 1: pdftotext: not found`), y `time` tampoco. Se hizo con pypdf, ~9 minutos para 5.851 páginas.
4. Un grep sin match sale con código 1 y arrastra el `exit` de todo el comando: el veredicto se leyó del texto, no del código.

## Estimación, declarada como tal (NO medida)

19 de Tarija en 1 de 10 tomos anuales sugiere ~190 por gestión. **Es una regla de tres sobre n=1 tomo, no un censo.** Mi censo del buscador dio 380 para 2016 en distrito 7, así que los dos números no cierran todavía y **eso mismo es un instrumento**: si al bajar los 10 tomos de una gestión el total de Tarija no se acerca al del buscador, uno de los dos sujetos está mal definido.

## NO MEDIDO

- Los otros 4 tomos de s1-2022 y los 5 de s2-2022. **Un tomo no es una gestión.**
- Las gestiones **2018 a 2021**, y si existe Gaceta **anterior a 2018** o **posterior a 2022** (el índice se corta ahí: si el art. 19 manda periodicidad mensual, faltan años y eso es un hallazgo abierto).
- `jurisprudencia.tcpbolivia.bo`, un tercer host que apareció en el portal y **dio timeout**. Sin medir.
- Si el índice del tomo permite partir por resolución de forma fiable.
- **Una autorización expresa del TCP**: no existe ni a favor ni en contra. Sigue siendo prudente pedirla para redistribución comercial.

## Veredicto operativo

La vía legítima es **ingerir desde la Gaceta Constitucional Plurinacional oficial**, conservando URL, tomo, página y sha256 del PDF, y citando el art. 19 del CPCo como fundamento de publicidad. **Deja de ser necesario tocar la API interna del buscador.**

Lo que **no** afirmo: que esté autorizada la redistribución comercial del texto íntegro. Eso es una decisión de Abraham con su abogado, y el dato que la informa es que la publicación es obligatoria por ley y el Tribunal no publica términos de uso.
