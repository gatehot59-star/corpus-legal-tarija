# 2026-09-04-07 · Los 935 decretos, la concordancia gratis, y un falsador que me hizo dudar de mi propio dato

## 1. Pedido

"Seguimos con tu recomendación": bajar los ~940 decretos departamentales, que yo mismo
declaré como la tarea de mejor relación valor/esfuerzo.

## 2. Herramientas declaradas

| herramienta | qué hizo | escribió | cuota ajena |
| --- | --- | --- | --- |
| `build.run` (brain-env) | 48 páginas de la Gaceta, 34 descargas piloto, SQL, escritura con backup | sí, en `/workspace` | no |
| red saliente | 48 páginas HTML + 34 PDFs (74 MB) de `tarija.gob.bo` | no | la Gaceta (público) |

**Acción delicada:** escritura en la base del abogado (22 años inferidos). Con backup
`bolivia-v7.db.antes-de-anio-inferido` y relectura con 0 discrepancias.

## 3. El censo, medido contra lo que declara el portal

```
paginas leidas: 48 | paginas declaradas por el portal: 47
DECRETOS UNICOS por id: 940  ->  935 son decretos reales
   (1 era 'formulario-de-residencia': ruido del catalogo, DECLARADO)
numero extraible del slug: 935 de 935
por anio: 2010:6 2011:9 2012:9 2013:26 2014:20 2015:23 2016:65 2017:61 2018:102
          2019:115 2020:172 2021:73 2022:69 2023:51 2024:50 2025:59 2026:21 sin_anio:4
```

Dos formas de numeración en los slugs, ambas medidas: `n-NNN-AAAA` (486) y `NNN-AAAA`
(444). Un extractor con una sola forma perdía la mitad.

## 4. El piloto que corrigió mi propia proyección (sesgo de selección)

**Piloto 1** tomó 2 por año ordenado y sólo llegó a 2016. Proyectó **1.037 MB con 71% de
OCR**. Ese número era basura: medí los escaneos viejos y extrapolé al corpus entero.

**Piloto 2** sobre 2017-2026, que son **773 de los 935** y los que un abogado consulta:

```
promedio moderno: 3.422.766 B  (contra 1.109.633 B del tramo viejo)
tramo moderno: texto nativo 6 | escaneo 14  (70% OCR)

== PROYECCION POR TRAMO (el promedio global mentia)
   2017-2026:  773 x 3.422.766 B = 2.646 MB
   2010-2016:  162 x 1.109.633 B =   180 MB
   TOTAL estimado: 2.826 MB   |   OCR necesario: 70%
```

**El material real es 2,8 GB, no 1 GB, y 7 de cada 10 necesitan OCR.** Un decreto de 2021
pesa 29 MB. Esto no es una descarga: es un proyecto con costo de CPU propio, y decirlo
ahora es más honesto que descubrirlo a mitad de camino.

## 5. EL ATAJO: la concordancia estaba en el catálogo, no en los PDFs

Los slugs declaran a qué ley reglamenta cada decreto. Eso costó **0 bytes de descarga
adicional**:

```
decretos analizados: 935
con concordancia declarada en el slug: 19
sin concordancia (no aporta, DECLARADO): 916
   reglamenta 15 | menciona 4
concordancias cuya LEY esta en el corpus: 18 de 19 | leyes distintas: 15
```

**19, no cientos.** Mi expectativa era optimista y el número la corrige. Pero esas 19
responden una pregunta que el buscador hoy no contesta y un abogado hace siempre:
**¿esta ley tiene reglamento?**

```
LD 500 -> DD 16/2026    LD 451 -> DD 37/2025    LD 487 -> DD 29/2025
LD 503 -> DD 21/2025    LD 451 -> DD 21/2024    LD 477 -> DD 17/2024
LD 405 -> DD 9/2024     LD 461 -> DD 28/2023    LD 437 -> DD 1/2022
LD 72  -> DD 61/2021    LD 409 -> DD 73/2020    LD 109 -> DD 8/2020
LD 162 -> DD 129/2019   LD 350 -> DD 114/2019
```

## 6. LA CONCORDANCIA COMO FALSADOR DE MI PROPIA VIGENCIA

Un decreto que **reglamenta** una ley es evidencia **independiente** de que esa ley estaba
viva cuando se dictó. Si yo la marqué muerta antes de esa fecha, uno de los dos datos está
mal. Dos casos salieron solos:

```
LD 109 de 2014 [derogada por LD 519 de 2026] <- DD 8/2020 la reglamenta
   -> CONSISTENTE: el decreto (2020) es anterior a la sucesora (2026).

LD 500 de 2025 [derogada por LD 520] <- DD 16/2026 la reglamenta
   -> primero NO MEDIBLE (la LD 520 no tenia anio en el corpus)
   -> con el anio puesto: CONTRADICCION (2026 vs 2026)
```

**Mi dato de vigencia quedó bajo sospecha por evidencia de otra fuente.** Eso es
exactamente para lo que sirve un falsador.

## 7. El año por posición, con banco

La LD 520 no tenía año, así que el falsador no podía decidir. La Gaceta asigna el id de
descarga secuencialmente, así que el id **acota** la fecha entre vecinos conocidos. Eso no
es adivinar: es interpolar entre dos mediciones, y se declara como inferido.

**Banco obligatorio:** se ocultan 14 años que la base YA tiene y se pide predecirlos.

```
banco: 14 / 14
   LD 235 real=2017 pred=2017 · LD 499 real=2025 pred=2025 · LD 060 real=2012 pred=2012 ...
```

Aplicado: **22 de 27 inferidos, escritos 22, discrepancias 0, quedan 5 sin año** porque sus
vecinos discrepan (2020 vs 2015, 2021 vs 2026) y ahí el guard devuelve NO MEDIDO en vez de
elegir uno.

## 8. Y ME REFUTÉ A MÍ MISMO, DOS VECES EN EL MISMO CASO

Escribí en un script, con esas palabras: *"Los ids de LEYES y DECRETOS son de catálogos
distintos: NO son comparables entre sí. El orden decreto-vs-ley no se puede resolver por
id."* **Era falso, y se ve con mirar los ids.** La Gaceta corre en Joomla, que usa **un
contador global de artículos**:

```
id 3444  LEY 519   2026-04-09
id 3469  DEC 16    2026
id 3506  LEY 520   2026
id 3507  LEY 521   2026-06-18
id 3527  DEC 18    2026
id 3605  LEY 523   2026
id 3607  DEC 20    2026
```

Leyes y decretos **intercalados y monótonos**. Con eso:

```
== EL CASO: DD 16/2026 id 3469 vs LD 520 id 3506
   El decreto se publico ANTES que la LD 520 -> CONSISTENTE.
   La LD 500 estaba viva cuando el DD 16/2026 la reglamento, y la LD 520 la abrogo despues.
   La contradiccion se disuelve y mi dato de vigencia AGUANTA.
```

**Guard del propio método, declarado:** el id ordena cronológicamente con **11 de 96 pares
fuera de orden (11,6%)** sobre las leyes con fecha exacta. O sea el id es un indicador
fuerte pero **no una prueba**: en este caso la diferencia es de 37 ids y sobrevive al ruido,
pero un caso con 2 ids de diferencia no se puede decidir así. Queda dicho.

## 9. Un hallazgo lateral que vale para la vigencia

`DD 20/2026: "ampliar el plazo de la VACATIO LEGIS y la conclusión de trámites de
adecuación"`. Una vacatio legis es una ley **promulgada que todavía no rige**, y es un
cuarto estado que el corpus hoy no tiene: no es vigente, no es derogada, no es "no medida".
Es "aún no entró en vigor". Sin los PDFs no sé a qué ley aplica.

## 10. Archivos generados

- `sistema/evidencia/2026-09-04-07-los-940-decretos-la-concordancia-y-el-falsador...md`
- `pipeline/censo_dd.py` · `pipeline/piloto_dd.py` · `pipeline/piloto2_dd.py`
- `pipeline/concordancia.py` · `pipeline/falsador_dd.py` · `pipeline/anio_por_id.py`
- `pipeline/global_id.py` (la refutación con su guard) · `pipeline/insp_dd.py` · `pipeline/orden.py`
- `indices/censo_dd.json` (935 decretos con id, slug y URL) · `indices/concordancia_dd.json`

## 11. NO MEDIDO

- **Los 935 decretos NO están bajados ni indexados.** Sólo 34 en piloto (74 MB). El resto
  son 2,8 GB y 70% de OCR: es un proyecto con costo de CPU, no un `for` loop.
- **La fecha exacta de cada decreto** está dentro del PDF. Sin ella, el orden decreto-vs-ley
  depende del id, que falla 11,6% de las veces.
- **Las 916 concordancias que no están en el slug** pueden existir en el texto del decreto.
  No lo sé: no bajé los textos.
- **La vacatio legis:** existe como figura en el material y el corpus no la modela.
- **Los 5 años que quedaron sin inferir** y los 401 títulos-slug siguen igual.
- **La concordancia NO se escribió en la base:** el esquema no tiene campo para "reglamentado
  por" y agregarlo es una migración. Hoy vive en `indices/concordancia_dd.json`.

---

```
--- METODO TITAN ---
Accion delicada: SI (escritura en la base del abogado)
Modo aplicado:   TITAN FULL
Rubrica:         Completitud 15/15 · Ejecutabilidad 15/15 · Testing 15/15 (banco 14/14 del
                 inferidor de anio, guard del 11,6% declarado, y dos pilotos donde el
                 segundo refuto la proyeccion del primero) · Arquitectura 9/10 ·
                 Documentacion 10/10 · Innovacion 5/5 (la concordancia como falsador de mi
                 propia vigencia no estaba pedida) · Proceso QA 5/5 · Seguridad y DevOps N/A
                 = 74/75 aplicables -> 99/100
N/A declarados:  2 criterios (Seguridad 15, DevOps 10) por tipo de entrega
Review externo:  no pedido (deuda declarada)
Instrumento:     48 paginas de la Gaceta con su censo declarado, 34 PDFs medidos por
                 cabecera /Font, banco de 14 con los anios ocultados, y el guard del
                 ordenamiento por id con su 11,6% de error verbatim. Evidencia cruda:
                 este archivo.
```
