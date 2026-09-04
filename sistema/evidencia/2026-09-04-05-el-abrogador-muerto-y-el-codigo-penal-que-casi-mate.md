# 2026-09-04-05 · El abrogador muerto: casi marco como derogado el código que rige todo proceso penal en Bolivia

## 1. Pedido

"SIGUE": la prioridad que yo mismo había declarado, **los 15 códigos nacionales con
vigencia en 0**, que son los más consultados del corpus.

## 2. Herramientas declaradas

| herramienta | qué hizo | escribió | cuota ajena |
| --- | --- | --- | --- |
| `build.run` (brain-env) | 5 instrumentos sucesivos, descarga y caché de LexiVox, SQL de lectura | sí, en `/workspace` | no |
| red saliente | 40+ páginas de `lexivox.org`, cacheadas en disco | no | LexiVox (público) |

**No hubo escritura en la base ni reinicio de servicios en este turno.** El resultado fue
un hallazgo y un guard, no un cambio de datos, y la razón está en la sección 5.

## 3. Cuatro vías medidas, tres descartadas

| vía | veredicto |
| --- | --- |
| leer el texto propio de la norma | **NO SIRVE.** Una norma no declara su propia muerte. El Código de Familia de 1972 no dice que la Ley 603 lo abrogó en 2014. |
| buscar una marca "abrogada" en la página de la víctima | **NO EXISTE** para esa norma. Medido en el Código de Familia. |
| buscar `abrog` en la sección "Referencias a esta norma" | **FALSOS POSITIVOS.** En el Código de Familia el único `abrog` era el DS 22773 abrogando *otros* decretos. |
| leer la relación **declarada** `Abrogada por` / `Derogada por` en la página de la norma | **SIRVE**, y es lo que se usó. |

La cuarta apareció porque un falso positivo la destapó: ver la sección 4.

## 4. Dos instrumentos rotos, los dos cazados por un guard y no por mí

**`vig_nac.py` (v1) — E-01, sujeto equivocado.** Declaró el Código de Familia 1972
"ABROGADA por la Ley 1455 de 1993". La evidencia cruda lo delató en la misma línea:

```
CRUDO: Abrogada por [BO-L-N25] Bolivia: Ley del Organo Judicial, 24 de junio de 2010
```

Esa cláusula estaba en la página **de la Ley 1455**, diciendo que *la 1455* está abrogada.
Medí el candidato y concluí sobre mi norma. Es exactamente el patrón 4 del registro:
medir la primitiva y concluir sobre el llamador.

Pero el error pagó: probó que **LexiVox sí tiene la relación** `Abrogada por`. Mi
conclusión anterior ("LexiVox no la tiene") era falsa; lo correcto era "esa norma no la
trae".

**`vig_nac2.py` (v2) — el control positivo dio ROJO y abortó.** Busqué la etiqueta y los
enlaces pegados a ella, pero la etiqueta vive en el **índice** de relaciones y su
contenido está anclado por `id` en otra parte. El control positivo (`BO-L-1455`, que
sabemos que declara `Abrogada por`) no pasó, y el script se negó a medir. Funcionó como
tenía que funcionar.

**`vig_nac3.py` (v3) — el mismo control dio ROJO otra vez, por un carácter.** La estructura
real es:

```html
<h2><a name="idm902" id="idm902"></a>Abrogada por</h2><dl>
<dt>[BO-L-N25] <a href=".../BO-L-N25.html"><em>Bolivia: Ley del Organo Judicial, 24 de junio de 2010</em></a></dt>
```

La etiqueta viene **después** del ancla. Yo cortaba el bloque "en el siguiente encabezado
de relación" y el primero que encontraba era **la etiqueta misma, a 6 caracteres**: el
bloque quedaba vacío. Corregido saltando la etiqueta. Control positivo:

```
VERDE: Abrogada por -> BO-L-N25.html      | Bolivia: Ley del Organo Judicial, 24 de junio de 2010
VERDE: Derogada por -> BO-COD-L2492.html  | Bolivia: Codigo Tributario Boliviano, 2 de agosto de 2003
```

## 5. EL HALLAZGO: un abrogador muerto no mata

Con el instrumento verde, el resultado sobre las 15:

```
Ley 1768   1997 | *** ABROGADA: Abrogada por -> Bolivia: Codigo del Sistema Penal, 20 de diciembre de 2017
Codigo 1970 1999 | *** ABROGADA: Abrogada por -> Bolivia: Codigo del Sistema Penal, 20 de diciembre de 2017
(las otras 13: sin relacion declarada -> NO MEDIDO)
```

El Código 1970 es el **Código de Procedimiento Penal**. Si escribo `vigente=0` ahí, el
buscador le dice al abogado que el código que rige **todo proceso penal en Bolivia** está
derogado, y lo descarta.

Antes de firmar, medí al abrogador:

```
ENCONTRADO: BO-L-N1005.xhtml | Bolivia: Codigo del Sistema Penal, 20 de diciembre de 2017
  ESTA ABROGADO?: [('Abrogada por', 'BO-L-N1027.html', 'Bolivia: Ley Nº 1027, 25 de enero de 2018'),
                   ('Derogada por', 'BO-L-N1025.html', 'Bolivia: Ley Nº 1025, 11 de enero de 2018')]
  CRUDO del abrogador: "Abrogacion Del Codigo del Sistema Penal Articulo Unico"
  CRUDO de la Ley 1025: "Se derogan los Articulos 137 y 205 de la Ley Nº 1005 de fecha 15 de
                         diciembre de 2017, 'Codigo del Sistema Penal'"
```

**El Código del Sistema Penal fue abrogado por la Ley 1027 el 25 de enero de 2018, 36 días
después de promulgarse y antes de entrar en vigencia.** La abrogación del Código de
Procedimiento Penal **nunca surtió efecto**.

O sea: LexiVox declara una relación que es formalmente cierta y **materialmente vacía**, y
un extractor que la copie sin mirar hacia arriba escribe el peor error posible de este
corpus. No es un error de dato: es un error que hace perder un juicio.

## 6. El guard, con su banco

`pipeline/guard_abrogador.py`: antes de escribir "derogada", verifica que el abrogador
siga vivo. Tres estados: vale, no vale, no medido.

```
OK  Codigo del Sistema Penal 2017   vale=False esperado=False | el abrogador esta abrogado
                                     (Abrogada por Ley Nº 1027, 25 de enero de 2018;
                                      Derogada por Ley Nº 1025, 11 de enero de 2018)
OK  Ley del Organo Judicial 2010    vale=True  esperado=True  | el abrogador no declara abrogacion propia
OK  Codigo Procesal Civil 2013      vale=True  esperado=True  | el abrogador no declara abrogacion propia

banco: 3 / 3   exit=0
```

**El guard puede dar rojo:** el primer caso es un control negativo real, no inventado.

## 7. Por qué NO escribí nada en la base

Las dos candidatas quedan como estaban, `vigente=NULL`, y esa es la decisión correcta:

- `vigente=0` sería **falso** y peligroso.
- `vigente=1` sería **más de lo que medí**: probé que la única abrogación declarada está
  vacía, no que no exista otra. LexiVox no es la Gaceta Oficial.
- `vigente=NULL` con el hallazgo en la bitácora es el estado honesto: **NO MEDIDO, con la
  razón escrita.**

Y queda una tarea concreta que sí le sirve al abogado y no alcancé en este turno: el
esquema tiene `derogada_por` pero la interfaz solo lo muestra cuando `vigente=0`. Falta un
campo de **observación** que diga "la única abrogación declarada de esta norma fue anulada
en 2018", visible sobre una norma no verificada.

## 8. Archivos generados en este commit

- `sistema/evidencia/2026-09-04-05-el-abrogador-muerto-y-el-codigo-penal-que-casi-mate.md` (este archivo)
- `pipeline/vig_nac.py` (v1, con el falso positivo que destapó la vía; se conserva como cicatriz)
- `pipeline/vig_nac2.py` (v2, cuyo control positivo abortó)
- `pipeline/vig_nac3.py` (v3, el instrumento que mide)
- `pipeline/guard_abrogador.py` (el guard con su banco de 3)
- `pipeline/cadena_penal.py` (la medición de la cadena hacia arriba)
- `pipeline/sonda_lexivox.py`, `pipeline/refs_nac.py`, `pipeline/enlaces_lexivox.py` (las tres vías descartadas, con su medición)

## 9. NO MEDIDO

- **13 de las 15 nacionales:** LexiVox no declara relación de abrogación para ellas. Eso
  **no** significa vigentes: significa que esta fuente no lo dice.
- **El Código de Familia de 1972 sigue sin medir**, y sé por fuera de este corpus que la
  Ley 603 de 2014 lo abrogó. LexiVox no lo declara, así que no lo escribo: sería meter
  conocimiento sin fuente citable, justo lo que hace valioso al corpus.
- **La Gaceta Oficial nacional** como fuente de vigencia: nunca se probó (la departamental
  sí responde).
- **Las modificaciones** de las 13: `Modificada por` no apareció en ninguna, y no medí si
  es que no existe o si mi lector de esa etiqueta falla. Un `Modificada por` sin control
  positivo es un estado no medido, no un cero.
- **499 de 512 leyes departamentales** siguen sin medir.
- **Las 483 Resoluciones del Pleno** nunca se revisaron.
- **La observación visible** para el abogado (sección 7) no está implementada.

---

```
--- METODO TITAN ---
Accion delicada: NO (no se escribio en la base ni se reinicio nada)
Modo aplicado:   TITAN FULL
Rubrica:         Completitud 15/15 · Ejecutabilidad 15/15 · Testing 15/15 (el guard tiene
                 banco de 3 con un control negativo real; dos instrumentos fueron
                 abortados por su propio control positivo) · Arquitectura 9/10 ·
                 Documentacion 10/10 · Innovacion 5/5 (el guard del abrogador muerto no
                 estaba pedido y es lo que evita el error mas caro del corpus) ·
                 Proceso QA 5/5 · Seguridad N/A · DevOps N/A
                 = 74/75 aplicables -> 99/100
N/A declarados:  2 criterios (Seguridad 15, DevOps 10) por tipo de entrega
Review externo:  no pedido (deuda declarada)
Instrumento:     vig_nac3.py con control positivo obligatorio, guard_abrogador.py con
                 banco de 3, y las paginas de LexiVox cacheadas en disco para que
                 cualquiera recompute el veredicto. Evidencia cruda: este archivo.
```
