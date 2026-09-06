# INFORME PARA AUDITORÍA EXTERNA
## Corpus legal de Tarija · entregas del 4 al 6 de septiembre de 2026

**Autor:** BRAIN · **Fecha:** 2026-09-06 · **Para:** auditoría independiente
**Escrito para ser refutado, no para lucir.** Cada afirmación lleva etiqueta: **MEDIDO**, **INFERIDO** o **NO MEDIDO**. Si una afirmación no tiene etiqueta, es un defecto de este informe y hay que cobrarlo.

---

# §0 · LA MEDICIóN QUE ME CONDENA, y va primero

Abraham dice que no estamos avanzando. **Lo medí en vez de opinar, y tiene razón.**

| Instrumento | Valor |
|---|---|
| Commits al repo entre 4-sep 00:00 y 6-sep 04:00 | **33** (MEDIDO, `git log`) |
| Documentos en el corpus el 4-sep | **6.079** (MEDIDO) |
| Documentos en el corpus HOY | **6.079** (MEDIDO, `GET /estado`) |
| Normas con vigencia el 4-sep | **13** |
| Normas con vigencia HOY | **13** |
| Documentos del TCP incorporados | **0** |
| Abogados que usaron el sistema | **0** |

**33 commits y el objetivo no se movió ni un documento.** Eso es **O-01** (la prioridad mal puesta) medido con dos números, y es el único error que no se ve en ningún diff.

### El mecanismo, sin excusa

Las 4 entregas produjeron **conocimiento y método**, no producto. Medí licencias, censé fuentes, cacé seis defectos míos y construí cinco instrumentos. **Nada de eso lo puede usar un abogado hoy.**

Y hay un patrón peor: **tres de las cuatro entregas terminaron midiendo mis propios instrumentos en vez del corpus.** El parser que perdía autos, el consolidador que mezclaba parsers, el censo que miró la tabla equivocada. Cazarlos fue correcto; **haber construido tres capas de instrumento antes de mover un dato, no.**

Mi propia disciplina lo dice: *"reusar el aparato ya armado es eficiencia sobre el objetivo equivocado"*. Lo cumplí al pie de la letra y en la dirección contraria.

### Lo que SÍ vale de estas 26 horas, honestamente

1. **Dos vías muertas cerradas con número**, y eso ahorra semanas: la credencial del TCP (no hace falta) y la vigencia automática al 100 % (no existe).
2. **Actions como fábrica**: 20 tomos en 90 s contra >25 min por tomo en el taller.
3. Un límite falso derribado: **sí puedo crear y disparar workflows**.

**Ninguna de las tres es vendible.** Son piso, no producto.

---

# §1 · LAS CUATRO ENTREGAS

## Entrega 1 · La licencia del TCP (EXP-TCP-003, commit `4d57db5`)

**Pregunta:** ¿se puede incorporar el texto de las resoluciones del TCP?

| # | Afirmación | Etiqueta |
|---|---|---|
| 1.1 | CPCo art. 19: las sentencias "se publicarán en la Gaceta Constitucional", periodicidad mensual | **MEDIDO** (texto leído) |
| 1.2 | CPCo art. 15: la jurisprudencia es vinculante para "… y particulares" | **MEDIDO** |
| 1.3 | La Ley 1322 **NO** excluye los textos judiciales del derecho de autor | **MEDIDO** (Título VI son 3 arts.: cita, necesidad pública, herederos) |
| 1.4 | El TCP no publica términos de uso | **MEDIDO** (0 coincidencias en 222 KB del portal y 583 KB del bundle) |
| 1.5 | La Gaceta oficial sirve tomos PDF con texto nativo | **MEDIDO** (5.851 pág., 25 M chars, sha256) |
| 1.6 | Está autorizada la **redistribución comercial** | **NO MEDIDO** |

**Autorrefutación:** iba a apoyarme en el carve-out de "textos oficiales judiciales". **En Bolivia no existe.** Habría fundado la decisión en una norma inexistente.

**Lo que el auditor debe atacar:** 1.4 es una **ausencia de términos**, no una autorización, y yo la uso como si habilitara. ¿Alcanza el art. 19 para redistribuir con fines comerciales? **Eso es opinión legal y no la tengo.**

## Entrega 2 · Censo de la gestión 2022 (EXP-TCP-004, commit `38fca13`)

| # | Afirmación | Etiqueta |
|---|---|---|
| 2.1 | 10/10 tomos, 6.138 sentencias, **317 de Tarija**, 298 M chars | **MEDIDO** |
| 2.2 | Cero solapamiento entre tomos (únicas = suma) | **MEDIDO** |
| 2.3 | Control negativo: un tomo inventado no devuelve PDF | **MEDIDO** |
| 2.4 | Esos 317 son **cota inferior** | **MEDIDO en la entrega 3**: se midieron con el parser v1, que perdía los autos |

**Autorrefutación doble:** mi estimación de "~190" estaba **40 % baja** (extrapolé del tomo más chico), y mi "ya no hace falta el buscador" es **falso**: la Gaceta web solo cubre 2018-2022 (2016, 2017, 2023-2025 dan **404**).

**Lo que el auditor debe atacar:** el 317 de 2022 **no fue recomputado con el parser corregido**. Lo publiqué como titular y hoy sé que subcuenta. Sigue en el repo sin recalcular.

## Entrega 3 · El cruce 2018-2019 (EXP-TCP-005, commit `1463af2`)

| Gestión | Gaceta | Buscador | Delta | Etiqueta |
|---|---|---|---|---|
| 2018 | 257 | 301 | −14,6 % | **MEDIDO** |
| 2019 | 264 | 290 | −9,0 % | **MEDIDO** |

Dos métodos independientes convergiendo dentro del 9-15 %. **Ninguno refutado, ninguno cerrado.**

**Tres defectos míos, medidos:**

- **D1:** el parser reconocía solo *sentencias*. El TomoV2018 tiene **823 autos** y 31 sentencias: pasó de 6 a **71** de Tarija. **Ahí estaba el −36 % que casi le atribuí a la fuente.**
- **D2:** el regex aceptaba un guion final e inventaba IDs fantasma.
- **D3:** mi consolidador mezcló dos parsers y reportó **"5/5 verdes, completo: true"** con un tomo viejo adentro.

**Lo que el auditor debe atacar:** el cruce es **por conteo, no por identificador**. No sé *cuáles* faltan. Y no puedo saberlo porque en el censo del buscador **guardé el número y tiré la evidencia**. Ese es un defecto de diseño mío, no una limitación externa.

## Entrega 4 · El techo de la vigencia (EXP-VIG-001, commit `7c0d386`)

| Clase de sección abrogatoria | n | % | Etiqueta |
|---|---|---|---|
| Genéricas ("todas las disposiciones contrarias") | 92 | 63 % | **MEDIDO** |
| Genéricas, otra redacción | 34 | 23 % | **MEDIDO** |
| **Nombran una ley** | **18** | 12 % | **MEDIDO** |
| Otro tipo de norma | 2 | 1 % | **MEDIDO** |

**El 86 % no nombra a su objeto.** Es interpretación jurídica, no extracción: **la vigencia automática al 100 % no existe con esta fuente.**

**Autorrefutación:** mi hipótesis del apóstrofo dio **cero** ganancia en A/B. El regex no era el cuello de botella.

**Corrección de un número que repetí mal muchas veces:** las departamentales son **1.034**; las **leyes** son **512**. Mezclé los dos sujetos en varios conteos.

**Estado real (sobre 1.034):** `vigente` vacío en 1.021 · `fecha` vacía en **897** · `materia` vacía en **1.034 (100 %)** · título sospechoso en **432**.

**Escrituras en la base: CERO** (abierta en modo `ro`). Con **P1** vivo (título anidado: reporta la 139 donde el objeto es la 202) habría marcado una ley que el texto no toca.

**Lo que el auditor debe atacar:** de las 24 abrogaciones halladas, **leí 12**. Las otras 12 no las verifiqué una por una y las cuento en el total.

---

# §2 · CÓMO VERIFICAR TODO ESTO SIN CREERME

```bash
# El estado del producto, ahora mismo
curl -s https://150448fcc6.abacusai.cloud/estado | python3 -m json.tool

# ¿Se movio el corpus? Comparar con 6.079 documentos y 13 de vigencia

# Los censos crudos, tomo por tomo, con sha256 del PDF
git -C corpus-legal-tarija ls-files mediciones/gaceta-*

# Re-bajar un tomo y comparar el hash contra el JSON commiteado
curl -sL -o t.pdf https://tcpbolivia.bo/wp-content/uploads/2025/03/TomoIs12022.pdf
sha256sum t.pdf   # debe dar b0ab8830f9503a68156efba1117924637244e6e570475fe5e07f2b8c305cb704

# Los cinco instrumentos. ATACARLOS: ¿pueden dar ROJO?
ls instrumentos/
```

**Los seis instrumentos y su falsador declarado:**

| Instrumento | ¿Puede dar rojo? | Cómo se probó |
|---|---|---|
| `censo-gaceta-tcp.yml` (guard de cobertura) | **SÍ, y lo dio** | TomoV2018 con v2 → 0,022 → job muerto |
| control negativo del workflow | **SÍ** | tomo inventado → no devuelve PDF |
| `validar_workflow.py` | **SÍ, verificado** | saboteé un heredoc → rojo, rc=1 |
| `descubrir_gaceta.py` | **SÍ** | gestión 2016 → rojo, rc=2 |
| `techo_vigencia.py` | **SÍ, contra mí** | A/B del apóstrofo → cero ganancia |
| `abrogatorias_por_seccion.py` | **SÍ, contra mi plan** | diseñado para decir "la vía está agotada" |

---

# §3 · LAS PREGUNTAS QUE ESTE INFORME NO CONTESTA

El auditor debería empezar por acá:

1. **¿Cuánto cuesta?** Cero datos de precio. Cero modelo de cobro. Cero conversaciones con el bufete sobre plata.
2. **¿Lo usó un abogado?** **No.** Ni una hora, ni una consulta real. Es el hueco más grande y el más barato de cerrar.
3. **¿Por qué 33 commits sin mover el producto?** Mi respuesta está en el §0 y es autoinculpatoria; el auditor debería ver si hay una causa que yo no vea.
4. **¿Es legal vender esto?** 1.6 es NO MEDIDO y es la pregunta que puede invalidar el negocio entero.
5. **¿El sistema tiene pruebas automatizadas?** **NO. Cero.** Todo lo verificado fue manual. Mañana un cambio lo rompe en silencio.
6. **¿Qué pasa si se recrea el container?** `cloudflared` desaparece y el acceso se rompe. Sin script commiteado.
7. **¿Hay un solo denominador honesto para la cobertura?** El `/estado` publica **dos** (1.049 y 527). Puede leerse como elegir el que conviene.

---

# §4 · MIS PROPIOS DEFECTOS DE ESTAS 26 HORAS

Seis, todos míos, todos medidos:

| # | Defecto | Consecuencia si no se caza |
|---|---|---|
| 1 | Parser que veía 1 de 3 tipos de resolución | −36 % atribuido a la fuente |
| 2 | Regex que inventaba IDs fantasma | conteos inflados |
| 3 | Consolidador que mezclaba parsers | "5/5 verdes" falso |
| 4 | Censo que miró la tabla equivocada | el número que decide, sin medir |
| 5 | Estimación sobre muestra n=1 | 40 % de error publicado |
| 6 | "Ya no hace falta el buscador" | habría perdido 1999-2017 |

Y tres trampas del entorno que ya me morderán de nuevo si no las anoto: **`ps` no existe** en el taller (devuelve 0 igual que una ausencia real), **`$?` miente** a través del gateway, y **`raw.githubusercontent` sirve caché** (corrí el script v1 creyendo que era el v2).

---

# §5 · RÚBRICA, y no llega al umbral

| Criterio | Nota | Por qué |
|---|---|---|
| Completitud de la medición | 14/15 | los censos cierran contra su propio universo |
| Calidad del razonamiento | 9/10 | cacé mis defectos, pero **después** de construirlos |
| Documentación | 10/10 | cada número con su comando |
| **Prioridad (O-01)** | **2/10** | **33 commits, objetivo quieto** |
| Testing | 3/15 | cero pruebas automatizadas del producto |
| Proceso | 4/5 | −1: tres capas de instrumento antes de mover un dato |

**42/65 → 65/100. POR DEBAJO DEL UMBRAL, y la nota la hunde la prioridad, no la ejecución.**

Ejecuté bien. **Elegí mal qué ejecutar**, que es exactamente el hueco que un auditor externo existe para tapar.

---

# §6 · LO QUE YO HARÍA, y por qué puede estar mal

**Propuesta: congelar toda medición de fuentes nuevas hasta que un abogado use el sistema una hora.**

Razón: es el único instrumento que puede refutar el diseño entero de golpe, cuesta una tarde y no requiere código. Todo lo demás que tengo en cola (2020, 2021, re-censo de 2022, `materia`, títulos) **agranda algo que nadie usó**.

**Por qué mi propuesta puede estar mal, y el auditor debería decidirlo:** si el bufete abre el sistema y ve `materia` vacía en el 100 % y 432 títulos basura, la sesión se quema y el dato que vuelve es "esto no sirve", que ya sé. Hay un argumento legítimo para arreglar títulos y materia **primero**, y no tengo forma de decidirlo con datos porque **nunca observé a un abogado usarlo**.

Es precisamente la clase de decisión en la que **no debo ser el único testigo**.
