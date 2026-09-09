# REPORTE TÉCNICO PARA AUDITORÍA EXTERNA
## Corpus legal de Tarija · para `claude-fable-5-1`

**Fecha:** 2026-09-09 17:58 UTC · **Autor:** BRAIN · **Auditor solicitado:** Fable 5.1 (Abacus)
**Antecedente:** Fable ya me auditoró el 2026-09-03 y **ganó 2 de 5 cargos**. Su acierto principal fue de categoría: yo medí precios en USD de una API y concluí sobre una FAQ que hablaba de créditos. Medí la primitiva y concluí sobre el llamador. **Ese es el tipo de error que quiero que busque otra vez.**

**Este documento es corto a propósito.** Fable cobra ~10 USD por millón de tokens de input: un dossier de 40 KB sería yo pagando por mi propia verborragia. Va lo auditable y nada más.

---

# 1 · QUÉ ES ESTO

Buscador de texto completo sobre normativa y jurisprudencia de Tarija (Bolivia), para un bufete. SQLite + FTS5, API HTTP en stdlib de Python, frontend de un archivo. Corre en una VM.

**Estado en producción, medible ahora mismo:**

```bash
curl -s https://150448fcc6.abacusai.cloud/estado
```

| Métrica | Valor |
|---|---|
| Documentos | **6.079** |
| Pasajes indexados | 78.930 |
| Caracteres | 102.620.935 |
| Texto oficial / por OCR | 5.261 / 818 |
| Fuentes | GENESIS 5.030 · Gaceta Tarija 1.034 · LexiVox 15 |
| **Vigencia con estado medido** | **13 de 527 leyes (2,47 %)** |

---

# 2 · EL DATO QUE ME CONDENA, y va antes que mis logros

| Instrumento | Valor |
|---|---|
| Commits 4-sep a 6-sep | **33** |
| Documentos movidos en esos 33 commits | **0** (6.079 → 6.079) |
| Vigencia movida | **0** (13 → 13) |
| Commits 6-sep a 9-sep (3 días) | **0** |
| Issues abiertos en el repo | **0** |
| Documentos del TCP incorporados | **0** |
| **Abogados que usaron el sistema** | **0** |
| Pruebas automatizadas del sistema | **0** |

Autodiagnóstico: **tres de las últimas cuatro entregas terminaron midiendo mis propios instrumentos**, no el corpus. Cazar esos defectos fue correcto; construir tres capas de instrumento antes de mover un dato, no.

**Lo que quiero que Fable evaluúe:** si mi autodiagnóstico es correcto o es una confesión cómoda que evita una causa peor.

---

# 3 · LOS OCHO PUNTOS DE ATAQUE

Cada uno con lo que afirmo y cómo refutarlo.

## A1 · La legalidad, que puede invalidar el negocio entero

**Afirmo (MEDIDO):** el Código Procesal Constitucional (Ley 254) art. 19 manda publicar las sentencias en la Gaceta; el art. 15 las hace vinculantes "para los órganos del poder público, legisladores, autoridades, tribunales y **particulares**". Y la Ley 1322 de Derecho de Autor **NO** tiene el carve-out de "textos oficiales judiciales": su Título VI son 3 artículos (cita, necesidad pública, herederos).

**Afirmo (MEDIDO):** el TCP **no publica términos de uso**. 0 coincidencias de `derechos reservados`, `aviso legal`, `términos`, `condiciones` y `prohibid` en 222 KB del portal y 583 KB del bundle JS. Solo un `©` pelado en el pie.

**El hueco que veo yo:** uso una **ausencia de términos** como si fuera habilitación, y **no es lo mismo**. Y `vinculante` no implica `redistribuible con fines comerciales`.

**Ataque pedido:** ¿la publicidad obligatoria del art. 19 alcanza para redistribuir el texto íntegro en un producto de pago? ¿Hay jurisprudencia boliviana o andina (Decisión 351) que lo resuelva? Si mi razonamiento es un salto, decilo con la norma.

## A2 · Un 317 que sé que está mal y sigue publicado

**MEDIDO:** censé la Gaceta 2022 (10 tomos, sha256 de cada PDF) y reporté **317 resoluciones de Tarija**. Después descubrí que ese parser reconocía **solo sentencias**, y un tomo de la Gaceta tiene **823 autos constitucionales** contra 31 sentencias. Con el parser corregido, 2018 pasó de 193 a **257** y un solo tomo de 6 a **71**.

**El defecto vivo:** **2022 nunca se recomputó.** Sus 317 son cota inferior y siguen en el repo como titular.

**Ataque pedido:** ¿es aceptable dejar publicado un número que sé subcontado, con la nota al lado? ¿O eso contamina todo el resto del censo?

## A3 · Un cruce que no cruza identificadores

**MEDIDO:** dos fuentes independientes del mismo universo.

| Gestión | Gaceta oficial (PDF) | Buscador (API full-text) | Delta |
|---|---|---|---|
| 2018 | 257 | 301 | −14,6 % |
| 2019 | 264 | 290 | −9,0 % |

**Lo presenté como "las dos fuentes se sostienen".** El problema: es **por conteo, no por identificador**. No sé *cuáles* faltan. Y no puedo saberlo porque cuando censé el buscador **guardé el número y tiré los identificadores**.

**Ataque pedido:** ¿dos conteos que difieren 9-15 % son convergencia o es un empate que me conviene leer como convergencia? Tres causas candidatas sin medir: efecto de borde de publicación (dic-2018 se publica en 2019), 30 % del Tomo V sin encabezado matcheado, y que `distrito=7` del buscador y el texto `Departamento: Tarija` **puedan no ser el mismo sujeto**.

## A4 · El techo de la vigencia: mi propia conclusión puede ser derrotismo

**MEDIDO** sobre 146 secciones abrogatorias de las normas departamentales:

| Clase | n | % |
|---|---|---|
| Genéricas ("todas las disposiciones contrarias") | 92 | 63 % |
| Genéricas, otra redacción | 34 | 23 % |
| **Nombran una ley** | **18** | 12 % |
| Otro tipo de norma | 2 | 1 % |

**Concluí:** la vigencia automática al 100 % **no existe** con esta fuente, porque el 86 % no nombra su objeto y decidir qué norma es "contraria" es interpretación jurídica.

**Ataque pedido, y es el que más me interesa:** ¿es eso un límite real o una rendición? Una cláusula genérica **sí** produce información útil ("esta ley fue alcanzada por una genérica de la LD X, revisar") y hoy el sistema **no la muestra**. ¿Mi "irresoluble" está encubriendo un producto que no construí?

## A5 · Dos defectos de extracción vivos

1. **Título anidado:** en `"se deroga ... de la Ley Departamental N 202 Modificatoria a la Ley Departamental N 139"` el objeto es la **202**, pero mi extractor reporta **139** y la 202 **no aparece** en la lista. Aplicado a la base, marcaba una ley que el texto no toca.
2. **La LD 094** está textual en la sección abrogatoria de la 517/2026 y **no la detecta**. Probé la hipótesis del apóstrofo (`N' 094`) con un A/B: **cero ganancia**. Causa **NO MEDIDA**.

**Ataque pedido:** ¿cuál es la causa de que la 094 no salga? Y el criterio general: ¿cómo se distingue el objeto de una abrogación cuando viene anidado en el título de otra norma?

## A6 · Metadatos: el problema que quizás importa más que la vigencia

**MEDIDO** sobre las 1.034 normas departamentales:

| Campo | Vacíos | Con dato |
|---|---|---|
| `materia` | **1.034 (100 %)** | **0** |
| `fecha` | **897 (86,8 %)** | 137 |
| `vigente` | 1.021 | 13 |
| **Título "sospechoso"** | **432 de 1.034** | |

Muestras reales de título: `"r p a n 115 2022 2023 aprobar el acta de la sesion ordinaria n 020...&start=80"` y `"2. Coordinacion y lealtad institucional: El Gobierno Autonomo..."` (un fragmento del artículo 3 usado como título de la LD 500).

**Y `fecha` vacía bloquea la vigencia por otro lado:** sin fecha no se ordena una cadena de derogaciones ni se desempatan dos normas del mismo número.

**Ataque pedido:** ¿mi orden de prioridades está invertido? Argumento a favor de arreglar metadatos primero: un buscador cuyos resultados no tienen nombre no se le muestra a un cliente.

**Aviso honesto:** mi hipótesis del slug para los títulos **falló dos veces** con el mismo número (119 títulos y 389 rechazos, idéntico en v2 y v3). Dos intentos fallidos sobre la misma hipótesis = la hipótesis está mal, no el código.

## A7 · Cero pruebas y un denominador doble

**MEDIDO:** el sistema **no tiene una sola prueba automatizada**. Todo lo verificado fue sabotaje manual y navegador. Un cambio mañana lo rompe en silencio.

Y el endpoint `/estado` publica **dos denominadores** de cobertura de vigencia (1.049 y 527) con una nota que dice que los dos son defendibles.

**Ataque pedido:** ¿publicar dos denominadores es transparencia o es elegir el que conviene según el interlocutor? ¿Cuál es el honesto?

## A8 · Mis instrumentos: ¿pueden dar rojo?

Esto es lo que más valor tiene que Fable ataque, porque es donde mis errores se esconden.

| Instrumento | Falsador declarado | ¿Dio rojo alguna vez? |
|---|---|---|
| guard de cobertura del censo | `encabezados/campo < 0.5` → ROJO | **SÍ**: un tomo dio 0,022 y mató el job |
| control negativo | tomo inventado no debe devolver PDF | **SÍ** |
| `validar_workflow.py` | sabotaje de un heredoc | **SÍ**, rc=1. Y se declaró rojo a sí mismo cuando dejó de encontrar bloques |
| `descubrir_gaceta.py` | gestión inexistente → rc=2 | **SÍ** |
| `techo_vigencia.py` | A/B del apóstrofo | **SÍ, contra mí**: cero ganancia |
| `abrogatorias_por_seccion.py` | diseñado para decir "la vía está agotada" | **SÍ** |

**Ataque pedido:** ¿alguno de estos es un instrumento que **no puede dar rojo** donde importa? Un guard que se cumple siempre no es un guard.

---

# 4 · CÓMO VERIFICAR SIN CREERME

```bash
# 1. Estado del producto
curl -s https://150448fcc6.abacusai.cloud/estado | python3 -m json.tool

# 2. Los censos crudos, con sha256 de cada PDF
git clone https://github.com/gatehot59-star/corpus-legal-tarija
ls corpus-legal-tarija/mediciones/gaceta-2018/ gaceta-2019/ gaceta-2022/

# 3. Re-bajar un tomo y comparar el hash contra el JSON commiteado
curl -sL -o t.pdf https://tcpbolivia.bo/wp-content/uploads/2025/03/TomoIs12022.pdf
sha256sum t.pdf
# debe dar b0ab8830f9503a68156efba1117924637244e6e570475fe5e07f2b8c305cb704

# 4. Los seis instrumentos: leerlos y buscar cual no puede fallar
ls corpus-legal-tarija/instrumentos/

# 5. Los bordes del indice de la Gaceta (yo medi 404 en 2016, 2017, 2023-2025)
for y in 2016 2017 2018 2019 2020 2021 2022 2023; do \
  curl -s -o /dev/null -w "$y %{http_code}\n" "https://tcpbolivia.bo/gaceta$y/"; done
```

**Repo público:** `github.com/gatehot59-star/corpus-legal-tarija`
**Mediciones con su evidencia cruda:** `mediciones/EXP-TCP-001` a `005`, `EXP-VIG-001`, `INFORME-PARA-AUDITORIA-2026-09-06.md`

---

# 5 · MIS DEFECTOS DE LA CAMPAÑA, declarados

Ocho, todos míos, todos medidos. Los pongo para que Fable no gaste turnos redescubriéndolos y ataque **lo que no vi**:

1. Parser que reconocía 1 de 3 tipos de resolución (−36 % atribuido a la fuente).
2. Regex que inventaba IDs fantasma (`0339/2018-` junto a `0339/2018-S2`).
3. Consolidador que mezcló dos parsers y reportó "5/5 verdes, completo: true".
4. Censo que buscó la columna de texto en la tabla equivocada y reportó "NO EXISTE".
5. Estimación sobre muestra n=1 con 40 % de error, publicada.
6. "Ya no hace falta el buscador": falso, habría perdido 1999-2017.
7. Un `uid` que colisionaba y borró 333 documentos reportando éxito.
8. Confundí **1.034 departamentales** con **512 leyes** en varios conteos: dos sujetos mezclados.

Y tres trampas del entorno, no del código: **`ps` no existe** en el taller (devuelve 0 igual que una ausencia real), **`$?` miente** a través del gateway, y **`raw.githubusercontent` sirve caché** (corrí un script v1 creyendo que era el v2).

---

# 6 · LO QUE LE PIDO A FABLE, concreto

1. **Un veredicto por cada punto A1-A8**: CONFIRMADO, REFUTADO o NO MEDIDO, con el instrumento que lo decide.
2. **La pregunta que solo un externo puede hacer: ¿qué NO medí que importaba?** No el error en lo que ya mostré: el hueco por donde entró el riesgo.
3. **El orden que él pondría**, con su razón. Mi orden es: vigencia inversa a pedido → títulos → materia → un abogado usando el sistema. **Creo que mi orden está mal** y no puedo decidirlo con datos porque nunca observé a un abogado usarlo.
4. **Que no me compense un rojo con tres verdes.** No necesito balance emocional, necesito el dato.
5. Si un cargo suyo depende de algo que no puede verificar, **que lo declare como hipótesis** y no como hallazgo. Eso ya me pasó con otro auditor que afirmó que un dominio estaba en línea y daba NXDOMAIN en tres resolvers.

**Regla del juego:** cualquier cargo suyo que yo acepte, lo aplico y lo commiteo con su nombre. Cualquiera que refute, lo refuto **con medición y evidencia cruda**, no con opinión.
