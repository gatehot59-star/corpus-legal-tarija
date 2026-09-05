# EXP-TCP-005 · El cruce 2018-2019, y los tres defectos míos que destapó

**Medido:** 2026-09-05 · GitHub Actions, parser `v3-tipos-flexibles`
**Datos:** `mediciones/gaceta-2018/` y `mediciones/gaceta-2019/` (25 JSON + 2 RESUMEN)

---

## EL CRUCE

| Gestión | Gaceta oficial (v3) | Buscador (cota inferior) | Delta |
|---|---|---|---|
| 2018 | **257** | 301 | −44 (−14,6 %) |
| 2019 | **264** | 290 | −26 (−9,0 %) |

**Veredicto: las dos fuentes se sostienen mutuamente dentro del 9-15 %.** Son métodos completamente distintos (full-text sobre una API firmada contra parseo de PDF oficial) sobre el mismo universo, y convergen. Ninguno queda refutado.

**Pero ninguno queda cerrado tampoco.** La Gaceta sigue dando MENOS que una cota inferior ajena, y eso no se explica por el sesgo del buscador. Tres causas candidatas, **ninguna medida**:

1. **Efecto de borde de publicación.** Una resolución de diciembre de 2018 puede publicarse en la Gaceta de 2019. El buscador ordena por fecha de resolución; la Gaceta, por tomo de publicación. **No son el mismo eje.**
2. **Cobertura del parser.** El TomoV2018 tiene cobertura encabezado/campo de **0,692**: ~30 % de sus resoluciones no matchean encabezado, y ahí puede haber Tarija sin atribuir.
3. **Sujeto distinto.** El buscador filtra por `distrito=7`; la Gaceta, por el texto `Departamento: Tarija`. Que coincidan no está medido.

### El falsentador que falta, y por qué no lo corrí

El cruce **a nivel de identificador**: tomar los números que el buscador devuelve y ver cuáles no están en el listado de la Gaceta. Es el único que dice *cuáles* faltan en vez de *cuántos*.

No lo puedo correr hoy porque **cuando censé el buscador guardé el conteo y no los identificadores**. Es un defecto de mi propio EXP-TCP-002: medí el número y tiré la evidencia que permitía auditarlo. Se arregla re-corriendo esas consultas capturando el campo `resolucion`.

---

## TRES DEFECTOS MÍOS, medidos y corregidos

El −36 % inicial no era de la Gaceta. Era mío, tres veces.

### D1 · El parser reconocía UN tipo de resolución de tres

`v1` partía el texto solo por encabezado de `SENTENCIA CONSTITUCIONAL PLURINACIONAL`. Medido en el TomoV2018:

```
v1: scp_unicas 29    campo_departamento 1307   tarija 6
v3: SCP 31 · ACP 823 · DCP 64 = 905 resoluciones   tarija 71
```

**El tomo de autos pasó de 6 a 71 resoluciones de Tarija.** Un tomo entero de la Gaceta es casi todo *autos constitucionales*, y mi instrumento no los veía. Ahí estaba la mayor parte del −36 %.

Y casi lo atribuí a la fuente: mi diagnóstico decía "o la Gaceta no publica todo, o mi parser pierde resoluciones". Tenía las dos hipótesis escritas y **la barata era la mía**.

### D2 · El sufijo de sala inventaba identificadores fantasma

`[-A-Za-z0-9]*` acepta un guion final sin sala. Producía `0339/2018-` **junto a** `0339/2018-S2`: dos IDs para una resolución. Corregido a `(-[A-Za-z0-9]+)?`.

### D3 · Mi consolidador mezcló dos parsers y reportó 5/5 VERDES

El `juntar` copiaba los JSON nuevos **sobre** los ya commiteados. Cuando el TomoV falló con `v2`, su archivo `v1` sobrevivió, y el RESUMEN salió con **4 tomos v2 + 1 tomo v1** diciendo `tomos_verdes: 5` y `completo: true`.

Es exactamente el patrón que este proyecto persigue: **un documento que no se enteró de que el mundo cambió**, cometido por mi propio instrumento. Corregido con `rm -rf` del directorio antes de consolidar y una etiqueta de parser obligatoria por tomo (`tomos_de_otro_parser_descartados`).

---

## Lo que SÍ funcionó, y hay que decirlo

**El guard nuevo cazó D1 antes que yo.** Al agregar `cobertura_encabezado_vs_campo < 0.5 → ROJO`, el TomoV2018 con `v2` dio **0,022** y el job murió. No pasó como verde: el instrumento se negó a entregar un número malo.

Y el `v3` agrega el diagnóstico que faltaba: cuando el guard da rojo, imprime **el encabezado real verbatim**. La causa de que `v2` fallara era medible y no la había medido: los autos del TomoV **no llevan la palabra `PLURINACIONAL`**, y `v2` la exigía. Adiviné el formato una vez; ahora el instrumento lo dice.

**El descubridor evitó un error mayor.** El patrón de URL **no es uniforme**:

| Gestión | Estructura | Tomos |
|---|---|---|
| 2018 | página plana | 5 |
| 2019 | **cuatro subpáginas trimestrales** t1..t4 | 20 |
| 2020 | dos subpáginas semestrales | 10 |
| 2022 | dos subpáginas semestrales | 10 |

Si hubiera generalizado el patrón de 2022, habría pedido 10 URLs inexistentes en 2019 y concluido que la gestión no está publicada.

**Los solapamientos entre tomos existen y se detectan:** 1 en 2018 (`SCP 0353/2018-S2` en TomoII y TomoV) y 2 en 2019. Las únicas se deduplican; la suma cruda no.

---

## Total medido de la Gaceta oficial hasta ahora

| Gestión | Tomos | Resoluciones | Tarija | Caracteres |
|---|---|---|---|---|
| 2018 | 5/5 | 4.291 | **257** | 148.995.233 |
| 2019 | 20/20 | 4.824 | **264** | 184.051.706 |
| 2022 | 10/10 | 6.138 (solo SCP, parser v1) | 317 (v1) | 298.202.742 |

**2022 está medido con `v1` y por lo tanto SUBCONTADO.** Sus 317 son cota inferior: falta re-correrlo con `v3`. No lo presento como cerrado.

---

## Trampas del entorno cazadas en esta corrida

1. **El `$?` del shell del gateway MIENTE.** El descubridor sale con código 2 ante una gestión inexistente; `echo $?` devolvió **0**. Control positivo por `subprocess`: `rc_real 2` y un `raise SystemExit(2)` de control también 2. **El script está bien; el instrumento de lectura estaba roto.**
2. **El shell se come las variables.** `for T in TomoI2018 ...; do curl .../$T.json` creó un archivo llamado `.json`. Rehecho con URLs literales.
3. **`raw.githubusercontent.com` sirve caché**: mostró el RESUMEN viejo minutos después del push. Se lee por API o pinneando el SHA del commit.

---

## NO MEDIDO

- **El cruce por identificador** (falta re-censar el buscador guardando los números).
- **2022 con `v3`**: sus 317 son cota inferior.
- Gestiones **2020 y 2021**.
- El ~30 % del TomoV2018 sin encabezado matcheado.
- Si `distrito=7` del buscador y `Departamento: Tarija` del texto son el mismo sujeto.
- **Ingesta: cero documentos del TCP en el corpus.** Sigue en 6.079.
