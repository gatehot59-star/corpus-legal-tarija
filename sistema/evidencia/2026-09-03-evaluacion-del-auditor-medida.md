# Evaluacion medida de la posicion del auditor

**2026-09-03.** Maquina: `brain-env` (gateway MUDH, servicio `build`). Todo lo que sigue es
**medicion sobre la base y sobre el clon de `aBOgacion`**, no lectura del informe.

Criterio: cada cargo del auditor se trata como una **hipotesis falsable**. Se acepta lo que la
medicion confirma, se rechaza lo que la medicion contradice, y se declara lo que no se puede
medir desde aca.

---

## Veredicto en una linea

**Gana en lo sustantivo (3 cargos confirmados, uno de ellos el mas valioso del dia), pero DOS de
sus ocho pasos de continuacion son inejecutables como los escribio, y lo mido.**

---

## 1. CONFIRMADO, y es el cargo mas valioso: hay un codigo muerto con nombre de vivo

Su cargo 3. Medido:

```plain
1975/codigo---12760a.md -> 325634 chars | art:946
  ['# Bolivia: Codigo de Procedimiento Civil, 6 de agosto de 1975', ...]

2013/ley---439.md       -> 341724 chars | art:552
  ['# Bolivia: Codigo Procesal Civil, 19 de noviembre de 2013', '[Ley N 439]']
```

**Tiene razon.** El archivo de 946 articulos es el **Codigo de Procedimiento Civil de 1975**,
abrogado por la Ley 439. Si se integraba `aBOgacion` sin verificar, entraba un codigo entero
muerto etiquetado como vigente, y **el sistema habria mentido con procedencia verificable**: el
hash y la URL correctos sobre un texto derogado. Es el peor modo de falla posible para este
producto, porque la parte auditable no lo detecta.

**Su numero no lo confirmo:** dice que la Ley 439 tiene 509 articulos y mi conteo da 552, pero mi
regex cuenta **menciones** de "articulo N", no articulos unicos, asi que **no lo contradice ni lo
verifica**. El mecanismo se sostiene sin ese numero.

**Y generaliza mas de lo que el dice:** el problema no es un archivo, son los 14 que liste en el
inventario. Lo mismo aplica al Codigo Penal (la Ley 1173 de 2019 **esta** en el repo, 199
referencias) y al Procedimiento Civil. Cada uno necesita su verificacion antes de entrar.

---

## 2. CONFIRMADO: la vigencia condicional existe en el corpus

Su cargo (a). Buscado en los 784 documentos departamentales:

```plain
puesta en vigencia plena       -> 1
vigencia plena del Estatuto    -> 1
transitoria                    -> 162
```

La clausula que el describe **existe**, y "transitoria" aparece en 162. Un enum de tres estados
(`vigente / abrogada / no medido`) no puede representar *"vigente hasta la puesta en vigencia
plena del Estatuto"*. **Acepto el rediseno del campo antes de llenarlo**, y acepto su regla:
llenarlo mal es peor que dejarlo en cero, porque un `vigente` falso se lee con la misma
confianza que uno verdadero.

Su Ley 007 como test case: esta en el corpus, `dep-tar-ley-departam-007-a3afdb90`, 14.898
caracteres. **Es un buen test y lo tomo.**

---

## 3. RECHAZADO POR MEDICION: su paso 1, el "fix barato de una tarde", no funciona

Propone extraer el ano de los 784 **desde el nombre del archivo con un regex**. Medido:

```plain
departamentales: 784
con anio extraible del nombre: 16 de 784
  tarija_leyes-047-a5771928.txt -> 1928
  tarija_leyes-200-2c1a2054.txt -> 2054
  tarija_leyes-269-8d190942.txt -> 1909
  tarija_leyes-106-7811932f.txt -> 1932
```

**Los nombres de archivo NO traen el ano, y los 16 que matchean son FALSOS POSITIVOS del hash
hexadecimal**: `a5771928` da "1928", `2c1a2054` da "2054", `8d190942` da "1909". Su regex, corrido
tal cual, habria escrito 16 anos inventados (uno de ellos en el futuro) en un corpus legal y los
768 restantes se quedaban vacios igual. **Un fix que produce datos falsos es peor que el hueco.**

**Donde SI esta el ano, medido sobre `registros.jsonl`:**

```plain
campos con un anio dentro: {'titulo': 754, 'archivo_texto': 16, 'sha256_real': 141, ...}
  'titulo': 'ley departamental 142 2016&start=360'
  'titulo': 'r p a n 074 2021 2022 aprobar la resolucion de distincion...'
```

**En el campo `titulo`: 754 de 784, o sea el 96%.** Su conclusion ("sin el ano el diferencial no
es consultable") es correcta y el remedio es otro. Y quedan **30 sin ano por ninguna via**, mas un
caso que su propuesta no ve: las RPA traen **dos** anos (`074 2021 2022`), que es la gestion
legislativa, no el ano de la norma. Eso necesita una decision, no un regex.

---

## 4. RECHAZADO POR MEDICION: su paso 3(a) no tiene insumos

Propone poblar la vigencia "automatico, detectando en el texto de cada norma *abroga/modifica la
Ley Departamental N...*". Medido sobre los 3.606:

```plain
se abroga            -> 8 chunks
se deroga            -> 4 chunks
modificase           -> 1 chunks
queda derogada       -> 0 chunks
se modifica          -> 53 chunks
```

En el corpus departamental entero: **8 "se abroga" y 2 "se deroga"**. No hay cientos de clausulas
derogatorias esperando a un extractor: **hay decenas**. La via automatica cubriria una fraccion
marginal y el trabajo real es **documental y manual**, exactamente lo que el pone como paso (b)
secundario.

**Por que importa el orden:** su plan da la impresion de que lo automatico hace el grueso y lo
manual completa. Medido, es al revES. Un plan que subestima la parte manual planifica una tarde y
cuesta semanas. **La tabla de relaciones sigue siendo correcta; el mecanismo para llenarla, no.**

---

## 5. ENCUADRE INCORRECTO, HALLAZGO CORRECTO: el metadato de los 2.822

Dice: *"Corregi el metadato a `origen_departamental: Tarija`, no `jurisdiccion: Tarija`"*.

**La base no dice eso.** Medido:

```plain
('departamental',    'Tarija', 'Asamblea Legislativa Departamental de Tarija',  784)
('jurisprudencia',   'Tarija', 'Tribunal Supremo de Justicia',                 2822)
```

`jurisdiccion` vale `jurisprudencia`, no `Tarija`. El campo que el critica **no existe con ese
valor**, asi que el cargo, literal, es sobre un sujeto equivocado.

**Pero el problema sustantivo es real y tengo el caso que el no tenia:**

```plain
AS/0003/2025 | Sala Plena | Internacional | departamento: Tarija
   partes: Embajada de la Republica Argentina ... c/ Ram...
AS/0140/2025 | Sala Plena | Internacional | departamento: Tarija
   partes: Embajada de la Republica Argentina c/ Elsa Choque Miranda.

Sala Plena, total: 49 documentos
```

**Dos extradiciones pedidas por la Embajada Argentina, etiquetadas `departamento: Tarija`.** Eso no
es derecho tarijeño en ningun sentido util: es competencia originaria del Supremo en Sala Plena.
Su diagnostico (el agente va a razonar mal) es correcto, y el caso lo prueba mejor que su
argumento. **Acepto el cargo por su conclusion, no por su enunciado.**

---

## 6. ACEPTADO: el Gran Chaco no estaba en mi inventario

Su cargo (d). Es cierto: no figura ni en lo que hay ni en lo que falta. Y medido, el material de
entrada **ya esta al alcance**:

```plain
en el corpus:  "Gran Chaco" -> 297 chunks | "Asamblea Regional" -> 20 | "Yacuiba" -> 1152
en aBOgacion:  2017/ley---927.md  (existe)
```

El corpus ya habla del Gran Chaco 297 veces y **no tiene una sola norma de su Asamblea Regional**.
Hueco real, con la fuente identificada.

---

## 7. Mi objecion a SU orden, y es una inconsistencia interna de su informe

En el punto (e) escribe que **la jurisprudencia departamental real es del TDJ (Autos de Vista, via
KRIMA)**. Estoy de acuerdo. Pero despues, en sus ocho pasos de continuacion, **KRIMA no aparece en
ninguno**, y en "lo que dejaria para el final" manda TCP y otros departamentos con el criterio
correcto de "no mejora el diferencial de Tarija".

**Por su propio criterio, KRIMA deberia estar arriba:** es lo unico que le da al estudio la
jurisprudencia de los tribunales donde litiga todos los dias, nadie lo cubre, y es diferencial
puro. Identifico el activo y no lo puso en el plan.

---

## 8. Lo que NO puedo evaluar desde aca (y no lo firmo ni en contra ni a favor)

- **Que solo Uriondo tenga Carta Organica y Yacuiba haya sido rechazada en 2018.** No lo medi;
  viene de sus rondas anteriores. Si es cierto, su correccion al tamaño del hueco municipal es
  buena y hace el trabajo **mas chico** de lo que yo dije.
- **Que Lexivox tenga leyes departamentales de Tarija sin hash ni Resoluciones del Pleno.** No lo
  verifique hoy. Si es cierto, mi "diferencial unico" se acota a **el texto verificable y las
  Resoluciones**, no a la existencia del dato.
- **Que el RE-SABS y los Decretos Departamentales sean el 50% del derecho departamental.** Es una
  estimacion suya, no un conteo. La direccion es plausible y la fraccion **no esta medida**.
- **El Estatuto del Gran Chaco 2016 y el 45% de regalias.** No verificado por mi.

---

## 9. Veredicto derivado (conclusion, no medicion)

**El auditor aporta mas de lo que le refuto.** Su cargo del codigo muerto evita el peor error
posible de este sistema, y su rediseño del campo de vigencia es correcto por una razon que yo no
habia visto: el derecho autonomico boliviano tiene vigencia **condicional**, y eso no entra en un
booleano.

**Y dos de sus pasos no se pueden ejecutar como estan escritos**, los dos por el mismo motivo:
**estimo el insumo sin medirlo.** El ano no esta donde el supone y las clausulas derogatorias son
decenas, no cientos. Es el mismo error que yo cometi esta mañana con los codigos nacionales, en la
direccion contraria: yo declare ausente lo que estaba, el declaro disponible lo que no esta.

**Orden que sale de cruzar los dos:**

1. Ano de las 784 **desde `titulo`** (96%), con los 30 restantes y las RPA de doble gestion
   declarados aparte.
2. **Verificar los 14 textos nacionales contra sus reformas** antes de integrar nada. Es lo que
   evita el codigo muerto.
3. **Rediseñar vigencia** como enum + tabla de relaciones, con la Ley 007 como test.
4. **Poblarla asumiendo que es trabajo manual**, con lo automatico como ayuda marginal.
5. Corregir el metadato de los 49 de Sala Plena y separar `origen` de `jurisdiccion`.
6. **Gaceta del Ejecutivo departamental** (su paso 6): acepto, misma institucion ya scrapeada.
7. **KRIMA / Autos de Vista del TDJ**, que su plan omitio.
8. Gran Chaco, municipal, y al final TCP y otros departamentos.
