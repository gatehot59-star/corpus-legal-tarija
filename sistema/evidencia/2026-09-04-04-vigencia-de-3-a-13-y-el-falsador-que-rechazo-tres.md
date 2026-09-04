# 2026-09-04-04 · La vigencia pasa de 3 a 13, el falsador rechazó tres, y el denominador estaba mal medido

## 1. Pedido

"SIGUE": cerrar la deuda declarada del turno anterior (los 4 tests de aceptación no
re-corridos contra el HTML nuevo) y seguir con lo que quedaba: la vigencia en 3 de 6.079.

## 2. Herramientas declaradas

| herramienta | qué hizo | escribió | cuota ajena |
| --- | --- | --- | --- |
| `playwright` (Chromium real) | los 4 tests de aceptación más 2 casos nuevos del permalink | no | no |
| `build.run` (brain-env) | censo SQL, extractor de vigencia, falsador, escritura con backup | sí, en `/workspace` | no |
| `ssh` / `scp` a la VM | copia de la base, reemplazo, `systemctl restart corpus-api` | **sí, en producción** | la VM del usuario |
| `curl` a la API pública | `/censo`, `/buscar` | no | no |
| `git` | commit y push | sí | no |

**Acción delicada:** escritura en la base del abogado y reinicio del servicio público.
Backup previo `bolivia-v7.db.antes-de-vigencia-v2` y relectura con 0 discrepancias.

## 3. Los 4 tests, ahora sí contra el HTML desplegado

HTML medido: `cbd49360ec471c976a6e06fe23630690`, **un solo bloque de script**, 0 errores de
consola en toda la sesión.

```
T1 carga p1     ?q=usucapion       1.741 pasajes · mostrando 1–12  · pagina 1 de 146   orden 01   primera as-0361-2012|9
T1 click p3     ?q=usucapion&p=3   1.741 pasajes · mostrando 25–36 · pagina 3 de 146   orden 25   primera as-0616-2020|14
T3 atras        ?q=usucapion       mostrando 1–12  · pagina 1      primera as-0361-2012|9
T3 adelante     ?q=usucapion&p=3   mostrando 25–36 · pagina 3      primera as-0616-2020|14
T4 filtro 2018  ?q=usucapion&anio=2018   230 pasajes · mostrando 1–12 · pagina 1 de 20   orden 01

T2 permalink en frio
  ?q=usucapion&p=3&abrir=jur-tar-auto-supremo-as-0616-2020-2020-066dd4e7|14
  apuntado as-0616-2020|14, ficha 25, lector en 14.943–17.854 de 42.769 caracteres, aviso_roto=false
```

### Los dos casos nuevos del permalink

**Reubicación.** Enlace SIN número de página, a un pasaje que vive en la 3:

```
entra  ?q=usucapion&abrir=jur-tar-auto-supremo-as-0616-2020-2020-066dd4e7|14
sale   ?q=usucapion&p=3   ficha 25 apuntada, lector abierto en 14.943–17.854
```

Recorrió las páginas por la API y saltó a la que contenía el pasaje.

**Control negativo.** Enlace a un pasaje que no está en esa búsqueda:

```
entra  ?q=usucapion&abrir=dep-tar-ley-departam-500-2025-b3adb533|11
aviso  "El enlace apuntaba a un pasaje que no esta en estos resultados. Pedia el pasaje 11
        del documento dep-tar-ley-departam-500-2025-b3adb533 para la busqueda «usucapion»,
        y no aparece en las primeras 144 coincidencias."
boton  "abrir ese documento igual" -> Ley Departamental 500 · texto continuo 13.368–16.465 de 33.335
```

El fallo silencioso quedó cerrado: ahora el instrumento **puede dar rojo y lo dice**.

## 4. El denominador estaba mal medido (E-01)

"0 de 6.079 sin vigencia" mide el sujeto equivocado. Censo por jurisdicción:

| jurisdicción | tipo | documentos |
| --- | --- | --- |
| jurisprudencia | Auto Supremo | **4.966** |
| jurisprudencia | Sentencia / Resolución | 64 |
| departamental | Ley Departamental | **512** |
| departamental | Resolución del Pleno | 483 |
| departamental | Compilado de Resoluciones | 39 |
| nacional | Código / Ley / CPE / DL | 15 |

**Un Auto Supremo no se abroga: es una resolución judicial.** Preguntarle su "vigencia"
normativa es como preguntarle su número de artículos. Los 5.030 de jurisprudencia (82% del
corpus) no tienen esa propiedad. El denominador real de la vigencia normativa son
**512 leyes departamentales + 15 nacionales = 527**, y ahí 13 medidas es 2,5%, no 0,2%.

Sigue siendo poco. Pero medir contra 6.079 exageraba el agujero y escondía dónde trabajar.

## 5. El extractor v2 y sus tres correcciones, cada una por un caso medido

1. **La v1 tomaba un número por cláusula.** "Se abrogan las Leyes Departamentales N° 109 ...
   y N° 029" son DOS leyes muertas y sólo entraba una. La LD 029 la encontré leyendo el
   texto crudo, no corriendo el script.
2. **La v1 aceptaba el número sin mirar el título.** Ahora exige que la cláusula NOMBRE el
   título del objetivo (≥25 caracteres de coincidencia) o su FECHA exacta.
3. **`difflib` con `autojunk=True` devuelve 0 coincidencias en textos largos**, porque trata
   los caracteres frecuentes como basura. Va `autojunk=False`. Sin eso el falsador rechazaba
   hallazgos verdaderos: un instrumento que da rojo por su propia configuración.

Y una cuarta, del turno anterior en el mismo archivo: `"DISPOSICIÓN ABROGATORIA"` es el
**encabezado** de una abrogación TOTAL, y la v1 lo leía como derogación parcial porque
buscaba "disposición" cerca del verbo. 4 de 8 hallazgos mal clasificados. **Marcar "parcial"
una abrogación total es peor que no marcarla: la ley queda como si siguiera viva.**

## 6. Lo que el falsador RECHAZÓ, verbatim

```
LD 017 <- LD 504 | coincidencia 5 car
   "Se abroga la Ley Departamental N° 'Ley Departamental Estructura de Cargos 17 2024 y
    Escala Salarial...'"
   -> el "17" es de un titulo de 2024, no la LD 017 de 2011. FALSO POSITIVO.

LD 049 <- LD 454 | coincidencia 3 car
   "Se deroga el articulo 2 ... de la Ley Departamental NI) 202 Modificatoria a la Ley
    Departamental N° 139"
   -> LD 049 es "PARQUES INDUSTRIALES". El numero 49 no sale de esta clausula. FALSO POSITIVO.

LD 237 <- LD 517 | coincidencia 6 car
   "Se abroga la Resolucion del Consejo Departamental N° 237/2008"
   -> es una Resolucion del Consejo, NO una Ley Departamental. Rechazo correcto.

LD 129 <- LD 405 | coincidencia 14 car
   "Se deroga el articulo 6 de la Ley Departamental N° 129, en lo referente a las empresas
    publicas departamentales"
   -> ESTO ES VERDADERO y el falsador lo rechazo: la clausula no nombra el titulo ni la
      fecha. Falso negativo declarado. No cambia el resultado (la LD 129 ya esta abrogada
      TOTAL por la LD 500), pero el sesgo existe y es conservador a proposito.
```

## 7. Las 14 con vigencia real, después de escribir

```
LD 94        vigente=0     <- Ley Departamental 517 de 2026
LD 007 2010  vigente=0     <- Ley Departamental 129 de 2015
LD 029 2011  vigente=0     <- Ley Departamental 519 de 2026   (Turismo Rural Comunitario)
LD 094 2013  vigente=0     <- Ley Departamental 517 de 2026
LD 109 2014  vigente=0     <- Ley Departamental 519 de 2026   (Turismo)
LD 129 2015  vigente=0     <- Ley Departamental 500 de 2025
LD 139 2016  vigente=NULL  <- parcialmente por Ley Departamental 454 de 2022
LD 279 2018  vigente=0     <- Ley Departamental 517 de 2026
LD 293 2018  vigente=0     <- Ley Departamental 517 de 2026
LD 300 2018  vigente=0     <- Ley Departamental 517 de 2026
LD 304 2018  vigente=0     <- Ley Departamental 398 de 2019
LD 432 2021  vigente=0     <- Ley Departamental 500 de 2025
LD 504 2025  vigente=0     <- Ley Departamental 523
LD 500 2025  vigente=0     <- Ley Departamental 520
```

Escritos 10, discrepancias 0. `vigente=0` pasa de 3 a **13**, con nota de 4 a **14**.

Y en el buscador público, medido con `curl`:

```
q=turismo rural comunitario
   Ley Departamental 029 2011 | LEY DE FOMENTO AL TURISMO RURAL COMUNITARIO | vig derogada | Ley Departamental 519 de 2026
   Ley Departamental 519 2026 | Ley departamental de turismo del departamento de tarija | vig no_verificada
```

La ley muerta y su sucesora, una debajo de la otra, con el estado a la vista.

## 8. Despliegue, con sus sellos

```
bolivia-v7.db (taller)            aaad5f53016ab1931eb1cd638138043e  212.422.656 bytes
rag-abogacia-v9.db (VM)           aaad5f53016ab1931eb1cd638138043e  212.422.656 bytes
rag-abogacia-v7.db (en servicio)  aaad5f53016ab1931eb1cd638138043e
corpus-api                        active
censo publico                     6.079 documentos · 78.930 pasajes · 102.620.935 caracteres
                                  sin vigencia verificada: 6.066  (era 6.076)
```

El censo no se movió: la escritura tocó vigencia, no contenido.

## 9. Archivos generados en este commit

- `sistema/evidencia/2026-09-04-04-vigencia-de-3-a-13-y-el-falsador-que-rechazo-tres.md` (este archivo)
- `pipeline/vigencia_dept.py` (v1, con el fix de PARCIAL)
- `pipeline/vig_v2.py` (v2, con el falsador adentro)
- `pipeline/falsa_vig.py` (el falsador manual que cazó los dos OCR)
- `pipeline/censo_vig.py` (el censo que corrigió el denominador)

## 10. NO MEDIDO

- **LD 202 <- LD 454.** El OCR escribió `NI) 202` y mi extractor exige `N` seguido de dígito
  con signos conocidos. Se pierde una derogación parcial REAL, leída a mano en el texto.
  No aflojé el patrón: aflojarlo mete falsos positivos. Queda declarado.
- **La ambigüedad 139 / 202.** El título de la LD 202 contiene el título de la LD 139, así
  que el falsador por título no puede distinguirlas. La nota parcial quedó en la 139 (venía
  del turno anterior) y la 202 sin nota. Un abogado que cite el artículo 2 de la 202 no
  queda advertido.
- **Qué artículo** derogó la LD 454 a la 139: la nota dice "parcialmente" y no dice cuál.
- **Las Resoluciones del Pleno (483) y los Compilados (39)**: nunca se les buscó derogación.
- **Los 15 nacionales:** 0 medidos. Y son los más usados.
- **499 leyes departamentales sin vigencia medida** de 512.
- **186 títulos** que no empiezan por su especie, y **401 slugs** que el extractor no resuelve.
- **La faceta cuenta sobre un pool de 400 pasajes**, no sobre el total.
- **Sin suite automatizada:** los 6 casos del navegador se corrieron a mano.

---

```
--- METODO TITAN ---
Accion delicada: SI (escritura en la base del abogado + reinicio del servicio publico)
Modo aplicado:   TITAN FULL
Rubrica:         Completitud 15/15 · Ejecutabilidad 15/15 · Testing 14/15 (6 casos en
                 navegador real, falsador con 4 rechazos incluido 1 falso negativo
                 declarado; sin suite automatizada) · Arquitectura 9/10 ·
                 Documentacion 10/10 · Innovacion 5/5 (el falsador por titulo-o-fecha,
                 la correccion del denominador, la reubicacion del permalink) ·
                 Proceso QA 5/5 · Seguridad N/A · DevOps N/A
                 = 73/75 aplicables -> 97/100
N/A declarados:  2 criterios (Seguridad 15, DevOps 10) por tipo de entrega
Review externo:  no pedido (deuda declarada)
Instrumento:     Chromium real via el servicio playwright, SQL sobre la base, el propio
                 falsador con sus rechazos verbatim, md5 en los tres lugares de la base,
                 y curl contra la API publica. Evidencia cruda: este archivo.
```
