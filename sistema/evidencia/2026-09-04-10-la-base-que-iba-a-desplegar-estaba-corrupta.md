# 2026-09-04 · La base que iba a desplegar estaba CORRUPTA, y produccion iba 22 años atrás

Esto salio de apagar la VM. Bajar la base antes de cortar no era ceremonia: destapo tres cosas que ningun test nuestro estaba mirando.

## 1. `bolivia-v8.db` esta corrupta. Era la base de la fase 2

Es la base donde la corrida de ingesta que **mate hace dos horas** (dos procesos sobre el mismo directorio temporal de OCR) estaba escribiendo.

```
PRAGMA integrity_check(20)
*** in database main ***
Tree 5 page 51866: btreeInitPage() returns error code 11
Tree 7 page 51879: btreeInit...
```

| medida | bolivia-v8 (corrupta) | produccion v7 (sana) |
|---|---|---|
| `integrity_check` | **btree roto** | `ok` |
| documentos | 5.991 | 6.079 |
| Leyes Departamentales | **469** | **512** |
| Decretos Departamentales | 38 | 0 |
| chunks | **ilegible** (`database disk image is malformed`) | 78.930 |

**Perdio 43 leyes departamentales y la tabla de busqueda entera.** Y lo peor: `SELECT COUNT(*) FROM documentos` **contestaba igual**, con un numero plausible. 5.991 no grita nada. Si hubiera seguido el plan (ingestar los 935 decretos en v8 y desplegar), publicaba una base sin 43 leyes y sin buscador, y el conteo del home me lo hubiera confirmado como exito.

Los 38 decretos que quedaron adentro son basura de la corrida abortada: se descartan, el cache manda.

Accion: `bolivia-v8.db` → `bolivia-v8.db.CORRUPTA-NO-DESPLEGAR`. La fase 2 se ingesta sobre `bolivia-v9-decretos.db`, copia byte-identica de `bolivia-v7.db` (md5 `dff1634200dac9793b625380f9ad8297` las dos), con guard verde antes de empezar.

## 2. Produccion servia una base con 22 años vacios

Comparando fila por fila la base rescatada de la VM contra la local, mismos 6.079 documentos, mismos 102.620.935 caracteres, **0 documentos de diferencia**, y un solo campo distinto:

```
campos que difieren: {'anio': 22}
  dep-tar-ley-departam-476-...  prod=''  local='2023'
  dep-tar-ley-departam-522-...  prod=''  local='2026'
  dep-tar-ley-departam-523-...  prod=''  local='2026'
```

El trabajo de normalizar el año se hizo local y **nunca se desplego**. Un abogado filtrando por 2023 no veia la Ley 476. Es un bug de producto, silencioso, y lo iba a seguir siendo si apagaba la VM sin bajar la base.

Corolario del metodo: la copia local **no** es respaldo de produccion ni al reves. Cada una tenia algo que la otra no. La canonica ahora es `bolivia-v7.db` local (año normalizado + 13 vigencias + 512 leyes + `integrity_check ok`).

## 3. El guard que habria cazado esto, con su control negativo

`sistema/guards/guard_base.py`. Mide 9 invariantes y **no confunde NO MEDIDO con verde**: si `chunks` es ilegible, esa fila sale `NO MEDIDO` y el veredicto es ROJO, no "0 chunks".

```
CONTROL POSITIVO  bolivia-v7.db                       VEREDICTO: VERDE 9/9   (22,8 s)
CONTROL NEGATIVO  bolivia-v8.db.CORRUPTA              VEREDICTO: ROJO ->
     integrity_check=ROJO, documentos=ROJO, leyes_departamentales=ROJO,
     chunks=NO MEDIDO, docs_sin_chunk=NO MEDIDO, chunks_huerfanos=NO MEDIDO,
     uids_duplicados=NO MEDIDO
BASE FASE 2       bolivia-v9-decretos.db              VEREDICTO: VERDE 9/9   (23,9 s)
```

Banco en `sistema/guards/banco_guard.py`: **6/6 verde**, incluidos los dos controles del instrumento.

### Dos errores mios en el propio guard, medidos

**a) El guard se colgaba y era culpa mia.** La v1 preguntaba los documentos sin chunk con un `NOT EXISTS` correlacionado. `chunks` es **FTS5, sin indice por uid**: eso son 6.079 barridos completos. Un `COUNT(*) FROM chunks` tarda 1,0 s, asi que el guard iba a tardar horas. Reescrito como diferencia de conjuntos: **1,5 s**. Un guard que no termina es un guard que nadie corre.

**b) Casi declaro roto el guard cuando lo roto era el termometro.** El guard daba `VEREDICTO: ROJO` pero el shell reportaba `salida=0`. Antes de tocar el codigo, control del instrumento:

```
python3 -c 'import sys; sys.exit(3)' ; echo $?   ->  0
false ; echo $?                                  ->  0
rc=$? ; echo $rc                                 ->  (vacio)
```

**El `$?` del shell de brain-env no propaga nada.** El guard siempre estuvo bien: medido con `subprocess`, devuelve rc=1 en corrupta, rc=0 en sana, rc=1 con `--rapido`, rc=1 si la base no existe. Queda anotado como trampa del entorno: **en este shell los codigos de salida no se miden con `$?`**. Y por eso el banco arranca probando que sabe distinguir un 3 de un 0.

## 4. Los 9 decretos que la fuente no sirve

Detalle completo en `sistema/evidencia/2026-09-04-decretos-no-servidos-por-la-fuente.json`. Resumen: **3** devuelven literal `El tamaño del Archivo es nulo` (30 bytes) y **6** devuelven la pagina de listado (205.723 bytes) con **HTTP 200**. Quien no mire el magic `%PDF-` cuenta 9 exitos.

Control positivo del descargador: los ids 3607 y 3552 bajan `application/pdf` de 3,1 y 3,3 MB. **El defecto es de la fuente.** Vias agotadas: sesion con cookies + Referer, `?view=document`, `?task=document.download`, ruta estatica (no existe: el componente strimea sin redirigir) y Wayback (sin capturas, y el control positivo tampoco tiene: esa forma de URL nunca fue crawleada).

## Estado de la fase 1 al cierre

```
[ 360/931] ok=351  pobres=0  fallos=9  | 4,0 doc/min | faltan ~143 min
cache: 359 documentos, 8,8 MB de texto
vivos: 3 procesos extrae_dd + 2 tesseract (medido en /proc, no con ps: aca ps no existe)
```

Los 9 fallos son **los mismos 9 del principio**: no aparecio ninguno nuevo en 368 registros.

## Lo que queda anotado para la fase 2

1. Ingestar sobre `bolivia-v9-decretos.db`, nunca sobre v8.
2. `guard_base.py` verde **antes** y **despues**, con baseline reescrito recien cuando el despues es verde.
3. Al desplegar, produccion gana los 22 años que le faltan.
4. La concordancia de decretos (19 cruces medidos) sigue **fuera de la base**: falta decidir tabla de relacion vs campo.
