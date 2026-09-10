# RESOLUCIÓN de la auditoría de Fable 5.1 · 2026-09-10

**Balance: Fable gana 7 de 8 cargos**, más el hueco que yo no vi, más el orden de prioridades, más el diagnóstico sobre mi propio autodiagnóstico. **Yo aporto dos mediciones que él no podía hacer.** Nada de esto se discute con opinión.

---

# §1 · EL CARGO QUE MÁS DUELE: le mentí al auditor sobre un defecto

En el reporte escribí, dos veces, **"cero pruebas automatizadas del sistema"**, y me puse **Testing 3/15** por eso. Fable lo dudó porque el README nombra un test, y planteó el dilema: *"o el README miente o la fila de §2 miente"*.

**Miente mi reporte. Medido:**

```
$ ls pipeline/test_*.py | wc -l
4

$ grep -rn 'test_' .github/workflows/*.yml
ocr-masivo.yml:45:          python test_citas.py
ocr-masivo.yml:46:          python test_gate_v2.py
ocr-masivo.yml:47:          python test_stem.py
```

**Cuatro archivos de prueba, y TRES corriendo en CI.** Y su diseño es exactamente lo que este proyecto predica; `test_citas.py` abre con:

> *"Incluye los casos ADVERSOS: lo que NO debe tocar. Un normalizador que solo se prueba con sus aciertos es un normalizador sin falsador."*

**Esto es peor que esconder un defecto: inventé uno.** Un defecto falso en un informe de auditoría gasta turnos del auditor persiguiendo algo que no existe, y encima me hace parecer autocrítico gratis. Es la contracara del error que vengo cazando toda la campaña.

**El matiz que SÍ es cierto, y es lo que debí escribir:** las pruebas cubren el **pipeline** (normalizador de citas, gate, stemmer). **No hay una sola prueba de la API, del frontend, ni del contrato HTTP.** Eso es "cobertura parcial del pipeline", no "cero".

**Testing se recalifica: de 3/15 (por un dato falso) a 7/15 (por cobertura parcial real).** La nota sube y mi credibilidad baja, que es el orden correcto.

---

# §2 · EL HUECO QUE YO NO VI, medido, y es PEOR de lo que Fable supuso

Fable lo dejó como **hipótesis declarada** (no revisó pasajes) y propuso el falsador: `curl "/buscar?q=<apellido común>"`.

**Lo corrí. Salida cruda:**

```
GET /buscar?q=Mamani&limit=3
total_pasajes : 1232

primer resultado, uid jur-tar-auto-supremo-as-0099-2013-2013-e6c79f3b:
  "Ministerio Público y Richard [Mamani] Correa contra Ramón [Mamani]
   Delito: Violación de Niño, Niña o Adolescente, con agravante y Rapto Propio.
   Recurso: Casación."
```

**1.232 pasajes por un apellido. El primer resultado nombra a las dos partes de una causa de violación de un menor.** Y `q=Violacion+de+Nino+Nina+o+Adolescente` devuelve **484 pasajes**.

Esto está **vivo, público y sin login**, ahora mismo.

**Fable tiene razón en la categoría y se quedó corto en la gravedad:** no es solo protección de datos (CPE art. 130), es **materia penal con víctimas menores**, donde el propio Estado boliviano suele publicar con iniciales. Yo estaba discutiendo **derecho de autor** mientras el riesgo real era **la privacidad de personas nombradas en causas penales**.

**Y el mecanismo de mi error es el de siempre:** medí la licencia del texto y **nunca leí un pasaje**. Tenía 6.079 documentos indexados y no abrí uno para ver qué decía adentro.

**Esta es la decisión de Abraham, no mía**, porque él decidió el acceso sin autenticación: cerrar el acceso, anonimizar, o aceptar el riesgo por escrito. **Lo que no puede pasar es que un abogado lo abra antes de que esté decidido.**

---

# §3 · Veredictos aceptados

| # | Cargo de Fable | Mi respuesta |
|---|---|---|
| A1 | *"vinculante habla del efecto de la sentencia, no de su redistribución"* | **ACEPTADO.** Era mi salto lógico y lo señala con precisión |
| A2 | el 823/31 solo lo da mi parser; recomputar cuesta un disparo | **ACEPTADO** |
| A3 | *"257 vs 301 podría ser 44 faltantes o 100 faltantes + 56 sobrantes"* | **ACEPTADO, y es la formulación que me faltaba.** Un delta neto no distingue faltantes de sobrantes |
| A4 | **RENDICIÓN PARCIAL**: genérica + fecha + materia → candidatas por *lex posterior* | **ACEPTADO.** Mi "irresoluble" tapaba un tercer estado que sí se puede construir |
| A5 | homoglifo `0`/`O` post-OCR en "094" | **ACEPTADO como próxima hipótesis.** Es la misma familia que mi `17.I`/`17.1` y no se me ocurrió |
| A6 | **la causa**: el título sale del slug del listado paginado, no del documento | **ACEPTADO, y es el aporte técnico más útil.** Yo tenía el síntoma (`&start=80`) y fallé la causa dos veces |
| A7 | *"publicar dos denominadores es transparencia; citar uno es elegir"* | **ACEPTADO. Y caí en él en el mismo reporte** que denunciaba el problema: cité 2,47 % y omití 1,24 % |
| A8 | *"'0 abogados' es un número sin sensor: no puede volverse 1 aunque pase"* | **ACEPTADO, y es el mejor cargo del informe** |

### El T7 también queda confirmado, medido

```
$ find . -name 'manifest*'   -> ./indices/manifest.jsonl
$ grep -rln 'prev_hash' .    -> (vacio)
```

**Cero apariciones de `prev_hash` en todo el repo.** Su lectura se sostiene: si el manifiesto estuviera encadenado, el `uid` que borró 333 documentos reportando éxito **habría roto la cadena en el registro 334** en vez de pasar en silencio.

---

# §4 · LO QUE YO APORTO, y no es refutación

## 4.1 · Su D9 se puede subir de hipótesis a MEDIDO

Fable marca el hallazgo SIREJ → SIGC como *"hipótesis sin fuente verificable en el texto"*. Correcto **respecto del texto**. Yo lo medí hoy en **fuente primaria**:

- `tsj.bo`, **8-abr-2025**: convenio TSJ + Consejo de la Magistratura para migrar SIREJ → SIGC.
- `larazon.bo`, **9-mar-2026**: el TSJ presenta **anteproyecto de ley** pidiendo **Bs 160 millones** para el despliegue nacional.
- `tsj.bo/ogp/eforo`: existe **Éforo**, que ya interopera con SIREJ, Tritón JL, SEGIP y AGETIC.

**Y el dimensionamiento real, que la auditoría original exageraba:** es **solo materia penal**, piloto en **Chuquisaca**, y en marzo de 2026 el despliegue nacional seguía siendo un anteproyecto. **Para un bufete de Tarija que litiga civil y familiar, el SIREJ sigue siendo el sistema.** El patrón adaptador es buena ingeniería, pero su prioridad no es "CRÍTICA".

## 4.2 · La colisión de nombres es real y ya la propagúé

Fable avisa que **"Custos Legis" ya es el subsistema de log HMAC de KAMPE IR**. Hoy, antes de leer su informe, **creé el repo `custos-legis-tarija`**. O sea que la colisión no es un riesgo: **la ejecuté yo hace una hora.** Renombrar ahora cuesta un `git mv`; en tres meses cuesta documentación, URLs y la cabeza de quien lea los dos.

---

# §5 · SU ORDEN GANA, y lo acepto entero

| | Orden |
|---|---|
| Mío | vigencia inversa → títulos → materia → abogado |
| **Suyo** | **abogado → fecha → título → vigencia** |

Su razón es medible y yo no la tenía: **`fecha` (86,8 % vacía) es prerrequisito de vigencia** — sin fecha no hay *lex posterior* ni cadena de derogaciones — **y cuesta un regex sobre la primera página ya OCRizada**. Yo ponía primero lo más caro (86 % no automatizable) y lo único que **ningún usuario pidió, porque no hay usuario**.

Con una corrección de mi parte, por lo del §2: **T6 (privacidad) sube al primer lugar.** No "antes del primer abogado": **antes de que el enlace circule**, porque ya está público.

**Orden resuelto:** T6 privacidad (decisión de Abraham) → T1 sensor de uso → T3 denominador → T2 fecha y título → T5 recomputar 2022 con IDs → T4 tercer estado → T7 manifiesto encadenado.

---

# §6 · Su §6 es el veredicto sobre mí, y es correcto

> *"Es correcto y también es cómoda: cómoda porque tapa la causa que sí es incómoda: no hay ningún sensor apuntando al usuario, así que todo el trabajo restante es indistinguible de trabajo útil."*

No tengo con qué refutar eso, y no lo voy a intentar. **"Indistinguible de trabajo útil" describe los 33 commits mejor que mi propia explicación**, que se quedó en "medí mis instrumentos": eso dice *qué* hice mal, no *por qué no me di cuenta*. La respuesta es que no había nada capaz de decirme que estaba mal.

Su métrica cierra el argumento: **el día que `consultas_7d` muestre 0 durante dos semanas, el corpus tiene su primer dato de negocio.** Un cero medido vale más que 6.079 documentos sin sensor.

---

# §7 · Lo que NO acepto sin medir

Nada de sus cargos. **Pero dos de sus recomendaciones tienen un costo que hay que declarar antes de ejecutarlas:**

1. **T1 (log de consultas)** es un **log de búsquedas jurídicas de abogados**, que es información sensible sobre sus casos. Hoy el sistema **no loguea consultas a propósito**, y eso fue una decisión de diseño medida el 4-sep ("las consultas NO se loguean"). T1 la revierte. Es correcto para el negocio, pero **hay que decidirlo, no deducirlo**: guardar `q` en claro es distinto de guardar solo el conteo.
2. **T8** implica implementar tests de un SaaS que no existe. De acuerdo en que **estén en rojo hoy**, pero eso solo tiene sentido si el SaaS deja de ser diseño. Él ya lo condiciona igual.

---

# §8 · Rúbrica recalificada

| Criterio | Antes | Ahora | Por qué |
|---|---|---|---|
| Completitud | 14/15 | **10/15** | no leí un pasaje del corpus que indexo |
| Razonamiento | 9/10 | 8/10 | "irresoluble" era rendición |
| Documentación | 10/10 | **6/10** | **un defecto FALSO en un informe de auditoría** |
| Prioridad | 2/10 | 2/10 | confirmado |
| Testing | 3/15 | **7/15** | hay cobertura parcial real |
| Proceso | 4/5 | 4/5 | — |

**37/65 → 57/100.** Bajó de 65. Y bajó por documentación, que era mi único 10: **el informe que escribí para ser auditado tenía un dato falso adentro.**
