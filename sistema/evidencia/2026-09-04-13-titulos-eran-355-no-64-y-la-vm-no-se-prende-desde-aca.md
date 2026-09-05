# 2026-09-04 · Los títulos basura eran **355, no 64**, y la VM no se prende desde acá

Abraham pidió dos cosas: arreglar los 64 títulos basura y despertar la VM. La primera se hizo y resultó más grande de lo que yo había reportado. La segunda **no la puedo hacer desde brain-env**, y lo mido abajo.

## 1. Mi propio número estaba corto: eran 355

Anoche reporté "64 leyes departamentales con título basura, 12,5%". El 64 era cierto **pero acotado a `tipo_norma = 'Ley Departamental'`**, que es el filtro que yo mismo había puesto. Contando el corpus entero:

```
titulos con &start= por tipo
   Resolucion del Pleno                 298
   Compilado de Resoluciones del Pleno   39
   Ley Departamental                     18   (tras arreglar 46 de las 64)
   total                                355
```

El 64 no era falso: era **la respuesta a una pregunta más chica que el problema**. Medir la parte que ya estaba mirando en vez del universo es la misma clase de error que hoy me hizo gritar ROJO sobre una escritura limpia (punto 4).

## 2. Los 46 títulos reconstruidos del texto oficial

Mi extractor anterior (`pipeline/titulos_desde_texto.py`) exigía que el título **empezara por su especie** (ley, estatuto, reglamento). Medido: devolvía **None en las 64**. El criterio era falso para una clase entera de leyes de Tarija, las que nombran su materia directamente:

```
LEY DEPARTAMENTAL N*089
LA ASAMBLEA LEGISLATIVA DEPARTAMENTAL DE TARIJA
SANCIONA:
"PROMOCION DEL RIEGO TECNIFICADO EN EL DEPARTAMENTO DE TARIJA"
```

Ese es el título y no empieza por "ley". **El ancla correcta es la fórmula de sanción, no la primera palabra del título.** Nuevo extractor en `sistema/titulos/titulo_sancionado.py`.

Resultado: **46 resueltos, 18 NO MEDIDO** (8 sin fórmula de sanción legible, 10 sin título detrás de ella). Los 18 no se tocaron.

Ejemplos de lo recuperado: `PERSONALIDAD Y NATURALEZA JURIDICA DE LA EMPRESA PUBLICA DEPARTAMENTAL DE SERVICIOS ELECTRICOS DE TARIJA SETAR` (LD 065), `DOTACION DE MARCAPASOS A PACIENTES CON RITMOS CARDIACOS ANORMALES` (LD 121), `RECONOCIMIENTO Y DECLARACION DEL ARETE GUASU COMO PATRIMONIO CULTURAL` (LD 075).

### El banco de negativos ganó su sueldo el mismo día

Esta tarde un control de puros positivos me dejó pasar 2 falsos positivos en la vigencia. Puse negativos en este banco desde el arranque, y **cazó un invento en la primera corrida**: para la LD 006 el extractor devolvió `y el parágrafo II del mismo Artículo señala que`, una cita entre comillas que no es título. Regla agregada: un título no arranca en minúscula ni con un conector.

Y el banco corrigió un segundo criterio mío: `ASAMBLEA LEGISLATIVA` no puede ser ruido a secas, porque la **LD 022 se titula "Asamblea Legislativa Departamental de Niñas, Niños y Adolescentes"**. Es ruido solo cuando la línea *es* el órgano.

Banco final: **10/10 verde** (4 positivos, 6 negativos), rc=0 medido con subprocess.

### El apóstrofo de O'Connor truncaba títulos

Leyendo los 48 primeros resultados uno por uno aparecieron 5 malos, y la causa de dos era mía: tenía `'` y `’` en la lista de comillas delimitadoras, así que **`SUBGOBERNACION O'CONNOR` se cortaba en `SUBGOBERNACION O`**. O'Connor es una provincia entera del departamento. Corregido: delimitan solo `“ ” "`, nunca el apóstrofo.

Los otros tres: uno terminaba en preposición colgada (bloque truncado) y la **LD 240 devolvía `Artículo 1. (OBJETO) L Aprobar la Modificación...`**, cuerpo de artículo disfrazado de título, la misma basura que ya arreglamos una vez. Filtros nuevos: se rechaza cola colgada y se rechaza lo que arranca en ARTÍCULO. Tras los filtros: 48 → **46, y 0 sospechosos**.

## 3. Los 354 recortes

Para los 298 Resoluciones del Pleno y 39 Compilados no hace falta reconstruir nada: el slug **ya trae la descripción** y solo sobra el parámetro de paginación.

```
ANTES: r p a n 115 2022 2023 aprobar el acta de la sesion ordinaria n 020 2022 2023&start=80
AHORA: r p a n 115 2022 2023 aprobar el acta de la sesion ordinaria n 020 2022 2023
```

`sistema/titulos/limpia_start.py` **no infiere, recorta**: por eso es seguro sobre los 355 sin banco. Escritos **354**. El único no tocado es una Resolución donde el fragmento no está al final: no se toca a ciegas.

**355 → 1** título con parámetro de URL en todo el corpus.

## 4. Me refuto la verificación: grité ROJO sobre una escritura limpia

Mi propio chequeo posterior imprimió:

```
titulos vacios tras el recorte: 4709 (esperado 0)
VEREDICTO: ROJO
```

**El ROJO era mío, no de la escritura.** Contaba los títulos vacíos **de todo el corpus** en vez de los del subconjunto que toqué. Medido contra el respaldo: los 4.709 **ya estaban vacíos antes** y de los 354 tocados quedaron vacíos **cero**.

```
vacios ANTES: 4709 | vacios DESPUES: 4709
de los 355 tocables: cambiados 354 | sin cambio 1 | QUEDARON VACIOS 0
```

Medir el universo en vez del sujeto que toqué. Tercera vez hoy que la categoría del error es la misma.

## 5. Y el ROJO falso destapó algo peor que los slugs

Esos **4.709 documentos con título vacío** son un defecto de producto más grave que los 355 slugs, y nadie lo había mirado:

```
Auto Supremo   4650
Sentencia        54
Resolucion        5
```

**4.650 Autos Supremos sin título, de 4.966.** El 94% de la jurisprudencia, que son 5 de cada 6 documentos del corpus, se lista sin nada que leer. Queda medido, no tocado.

## 6. La VM: no se puede prender desde brain-env

No es que no lo intenté. Medido:

| instrumento | resultado |
|---|---|
| `curl https://corpus-tarija.abacusai.cloud/` | **404 `not found`, `server: cloudflare`** |
| puertos 22172 / 22 / 443 en 208.122.8.11 | los tres **sin respuesta** |
| CLI `abacusai` / SDK python | **no instalados** en brain-env |
| `nuevo_host.sh` (registrar el hostname) | usa `169.254.169.254`, metadata que **solo responde DESDE la VM** |
| doc oficial de Abacus | el arranque es "visit supercomputer.abacus.ai"; no hay endpoint REST documentado |

Dos cosas importantes de esa tabla. Primero: el 404 **no lo contesta nuestro nginx**, lo contesta Cloudflare, o sea **la ruta del hostname se soltó con el apagado**. Ayer, apenas apagada, daba 503; ahora 404. Segundo: el hostname se re-registra con la metadata interna, así que **eso tampoco se puede desde acá**: hay que correrlo dentro de la VM.

Conclusión honesta: **el arranque es un click tuyo en https://supercomputer.abacus.ai**. Es la única vía que existe.

## 7. Todo listo para que el despliegue sea un comando

`sistema/despliegue/despliega.sh`, probado ahora mismo contra la VM apagada (falla con el mensaje correcto en el paso 1, no a ciegas). Hace: chequear que la VM contesta, parar el servicio, respaldar la base remota, subir, **comparar md5 contra el origen y abortar si difiere**, levantar servicios, re-registrar el hostname y **verificar desde afuera con curl**, no desde la VM.

Base lista en `/workspace/deploy/rag-abogacia-v7.db`, md5 `87b2aa0a43e2a8ad2945fa5e246a9b00`, 212.426.752 bytes:

```
integrity_check   ok
documentos        6079
con vigencia      21   (produccion tiene 13)
titulos basura     1   (produccion tiene 355)
anio vacio        10   (produccion tiene 32)
guard_base.py     VERDE 9/9
```

## NO MEDIDO

- **4.650 Autos Supremos sin título.**
- Los 18 títulos de ley que siguen con el slug, y la Resolución con el fragmento en el medio.
- Reconstruir las Resoluciones del Pleno desde su cláusula RESUELVE.
- Si al prender la VM los servicios `enabled` levantan solos: no se puede saber hasta prenderla.
- **Nada desplegado.** La VM sigue apagada y el hostname sin ruta.

## Fase 1 de decretos

```
[ 760/931] ok=751  pobres=0  fallos=9  | faltan ~87 min
```
