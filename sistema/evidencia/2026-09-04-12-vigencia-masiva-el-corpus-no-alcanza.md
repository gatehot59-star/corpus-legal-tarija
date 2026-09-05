# 2026-09-04 · Vigencia masiva: el corpus **no alcanza**, y mi control de 17/17 no podía cazar falsos positivos

Abraham pidió arrancar la vigencia masiva de las 499 leyes sin estado. Se hizo, y el resultado importante es un **techo medido**, no una cifra grande.

## Primero, un incumplimiento mío del método

El grafo se extrajo y verificó **hace casi tres horas** y no se commiteó ni se escribió nada. Quedó en el taller, en archivos sueltos (`vig_grafo7.json`, `extrae_grafo_vigencia.py`). La regla es commitear antes de redactar; si se cae la sesión, el trabajo no existe. Queda anotado.

## Lo que se midió

Se leyeron los **512** textos de leyes departamentales completos buscando cláusulas abrogatorias y derogatorias:

```
leyes departamentales: 512 | con texto: 512
aristas abrogador->abrogada:                          26
clausulas GENERICAS (no matan a nadie en particular):  86
clausulas de EXCEPCION (nombran a la excluida):         1
clausulas SIN DESTINO legible (NO MEDIDO):              6
leyes NOMBRADAS como abrogadas:                        22
   de esas, presentes en el corpus:                    22
   nombradas pero AUSENTES del corpus:                  0
```

## EL TECHO: el corpus no puede dar la vigencia de las 499

**86 de las 113 cláusulas encontradas son genéricas**: "se abrogan todas las disposiciones de igual o inferior jerarquía que contradigan la presente". Eso no mata a nadie en particular, y resolverlo exigiría comparar el contenido de cada ley contra cada ley posterior, que es un juicio jurídico, no una consulta.

Solo **22 leyes** son nombradas con número por alguien. Después de adjudicar, **21 leyes reciben estado**. Las otras **491 siguen sin poder medirse desde el corpus**, y no porque falte trabajo: porque **la información no está ahí**. Una ley no se entera de su propia muerte, ya lo aprendimos con el Procesal Civil de 1975.

**Conclusión que corrige mi propia recomendación de esta tarde:** le dije a Abraham "la vigencia masiva antes de más corpus, ya tengo el instrumento". El instrumento existe y funciona, pero su techo es 21 de 512, **4,1%**. Para pasar de ahí hace falta **otra fuente** (Gaceta con índice de derogaciones, o la Asamblea Departamental), no más pasadas sobre el mismo texto. Priorizar mal cuesta una tarde ajena, y esta la corrijo antes de gastarla.

## Mi control daba 17/17 y me equivoqué en 2 de 18

El extractor tenía banco 10/10 y control 17/17 sobre pares conocidos por lectura directa. Los dos números eran ciertos y el instrumento igual estaba mal, porque **el control solo tenía casos positivos**: 17 pares que SÍ existen. Un control de puros positivos mide *recall*, no *precisión*. **No puede cazar un falso positivo por construcción.**

Por eso las 18 aristas totales se leyeron una por una. Verbatim completo en `sistema/evidencia/2026-09-04-vigencia-las-18-clausulas-verbatim.md`.

### Falso positivo 1: casi mato la Ley de Administración del Presupuesto

> Se abroga la Ley Departamental **204** de Modificacion al articulo 27 de la Ley Departamental **139** de Administracion del Presupuesto...

Muere la **204**. La **139** es la ley que la 204 *modificaba*. Mi extractor tomó los dos números de la misma oración.

**Forma general:** `Se abroga la Ley X de Modificación a la Ley Y` mata a **X**, nunca a **Y**. Es la misma clase de error que ya cometí dos veces este mes: medir la entidad citada y concluir sobre el sujeto.

Y hay una vuelta más, porque la regla no es "si hay dos números, tomá el primero": la LD 500 abroga **129 y 432 juntas**, y ahí las dos mueren de verdad. La diferencia es que en la LD 500 la 129 aparece como **ítem de una lista**, con su propio título y su propia fecha; en la LD 454 la 139 aparece como **complemento del nombre** de la 204. Un patrón de regex no distingue eso. Un lector sí.

### Falso positivo 2: casi mato la autonomía del Gran Chaco

> Se abrogan las Leyes Departamentales N° **109** ... y N° **029** ...

El `10` salió del propio `109`. Leído el texto completo de la LD 519 (50.596 caracteres), la única ley departamental nombrada en la cláusula es la 109. Se evitó marcar muerta la **LD 010/2010 "Ley de Reconocimiento a la Autonomía Regional del Gran Chaco Tarijeño"**.

## El abrogador muerto, resuelto con la regla legal y no con la intuición

Mi primera resolución iteraba a punto fijo: si el abrogador está muerto, su abrogación no cuenta. Con esa regla la LD 129 y la LD 432 **revivían**, porque su verdugo (LD 500) fue abrogado por la LD 520.

**Eso es legalmente falso.** La abrogación es instantánea y definitiva: que el abrogador muera después no restituye la vigencia de la abrogada, salvo cláusula expresa de restitución. Medido, no supuesto: se buscó `restituy|restablec|recobra|revive|recupera vigencia` en el texto completo de la LD 520 (32.558 caracteres) y de la LD 500 (38.159). **Ninguna tiene.** La 129 y la 432 quedan muertas.

La lección es de categoría (E-01): el "abrogador muerto" del frente nacional era un problema de **existencia** (el abrogador no existía). Este es un problema de **doctrina**. Le apliqué la regla de un problema al otro porque compartían el nombre.

## Lo escrito

```
ANTES    con estado: 13 | con nota: 14
DESPUES  con estado: 21 | con nota: 22
respaldo: bolivia-v7.db.antes-de-vigencia-masiva
ok: las 2 rechazadas siguen sin estado de abrogacion

guard_base.py -> VEREDICTO: VERDE 9/9  (rc=0 medido con subprocess)
   integrity_check ok | documentos 6079 | chunks 78930
   leyes_departamentales 512 | docs_sin_chunk 0 | huerfanos 0 | duplicados 0
```

**16 abrogadas** (LD 7, 29, 94, 109, 129, 204, 206, 279, 293, 300, 420, 432, 484, 500, 504, 505) y **3 vigentes con artículos derogados** (LD 151, 202, 438).

Aplicador: `sistema/vigencia/aplica_vigencia_adjudicada.py`, con las 2 rechazadas y su motivo escritos en el código para que no vuelvan, y una comprobación final que da ROJO si alguna rechazada quedó marcada muerta.

## Defectos de datos que asomaron al listar las leyes

**64 leyes departamentales tienen como título un fragmento de URL**: `ley departamental 089 2013&start=420`. Es basura del scraping que quedó de título. Son 64 de 512, **12,5%**, y un abogado que busque por nombre no las encuentra.

**1 documento tiene como título el texto de un artículo:** la LD 139 tiene un segundo registro titulado `Artículo 3. (REPORTE).- El Órgano Ejecutivo Deberá reportar...`. Es un pasaje registrado como documento.

**3 números con dos registros:** LD 512, LD 485 y LD 139.

Nada de esto se tocó en este turno. Queda anotado y medido.

## NO MEDIDO

- **491 leyes departamentales sin estado de vigencia.** Techo del corpus alcanzado; hace falta otra fuente.
- Las 86 cláusulas genéricas: no se pueden resolver sin juicio de contenido.
- Las 6 cláusulas sin destino legible.
- La "Ley sin número de fecha 6 de enero de 2016" que abroga la LD 517: sin número no se resuelve.
- La vigencia de las 15 normas nacionales y de los 5.030 documentos de jurisprudencia.
- Los 64 títulos basura y el pasaje registrado como documento.
- Nada desplegado: la VM sigue apagada.

## Fase 1 de decretos, en paralelo

```
[ 740/931] ok=731  pobres=0  fallos=9  | 2,0 doc/min | faltan ~95 min
```

Siguen siendo los mismos 9 fallos.
