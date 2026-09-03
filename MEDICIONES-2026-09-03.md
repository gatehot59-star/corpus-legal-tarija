# Mediciones del 2026-09-03: los codigos nacionales y KRIMA

Dos preguntas pendientes, medidas. Con un error propio corregido en el medio.

---

## 1. Los codigos nacionales SI estan en el corpus abierto

### Primero, el error: mi medicion anterior era basura

La primera busqueda dio "13 de 14 presentes" y estaba **mal por diseno**. Buscaba la frase
`"codigo civil"` en el texto y devolvia el **primer archivo que la menciona**, ordenado por ano:

```
Codigo Civil -> 1833/ley---18331101.md  "Bolivia: Ley de 1 de noviembre de 1833"
Ley 348      -> 1994/convenio---1599.md "Convencion de Belem Do Para"
```

Una ley de 1833 que **cita** el codigo civil no es el Codigo Civil (que es el DL 12760 de 1975).
**Medi la mencion y conclui sobre la norma**, que es la tercera vez en el dia con la misma forma
de error.

### Re-medido por TITULO del documento + TAMANO

Un codigo son cientos de miles de caracteres; una ley que lo cita, mil. Con eso el instrumento
discrimina:

| norma | caracteres | archivo |
|---|---|---|
| **Codigo de Comercio** | **709.863** | `1977/codigo---14379.md` |
| **Codigo Civil** | **556.408** | `1975/codigo---12760b.md` |
| **Codigo Procesal Civil** | **341.724** | `2013/ley---439.md` |
| **Constitucion Politica del Estado 2009** | **271.631** | `2009/constitucion-politica-del-estado---20090207.md` |
| **Ley 031 Marco de Autonomias** | **243.623** | `2010/ley---31.md` |
| **Codigo Tributario** | **226.518** | `2003/codigo---2492.md` |
| **Codigo de Familia** | **200.615** | `1972/codigo---10426.md` |
| **Codigo Penal** (texto ordenado) | **180.080** | `2010/codigo---20101008.md` |
| **Ley 025 Organo Judicial** | **162.858** | `2010/ley---25.md` |
| **Ley 348** | **120.582** | `2013/ley---348.md` |
| Ley 1178 SAFCO | 44.210 | `1990/ley---1178.md` |
| Ley General del Trabajo | 57.752 | **solo el REGLAMENTO** (DS 224 de 1943), no la ley |
| **Codigo de Procedimiento Penal** | -- | **NO ESTA** |
| **Codigo Nina Nino Adolescente** | -- | **NO ESTA** |

**Veredicto: 10 de 14 completos, 2 parciales, 2 ausentes.** El agujero mas grande del corpus se
cierra con un adaptador, no con meses de scraping. Lo que falta se busca en lexivox directo.

---

## 2. KRIMA: encontre el backend, pero pide una llave que no esta a la vista

KRIMA es jurisprudencia de **Tribunales Departamentales y Juzgados**, o sea primera y segunda
instancia de Tarija: lo que ningun competidor publicita y no esta en GitHub.

Medido, en orden:

| paso | resultado |
|---|---|
| SPA de KRIMA | 200, 983 bytes (cascara vacia, como GENESIS) |
| `apikrima.organojudicial.gob.bo` | **no resuelve** |
| baseURL en el bundle `app.9daeed74.js` | **`https://wskrima.organojudicial.gob.bo/api/v1/`** |
| `/catalogos/*` | 404 |
| **`/resoluciones/busqueda_por_gestion`** | **401 `{"mensaje":"Acceso negado"}`** |
| `/departamentos` | 200, y **filtra a un tercer host**: `zeus.organojudicial.gob.bo/api/oficina/departamentos` |
| rutas que nombra el bundle (`resolucionesList`, `resolucionesListFilter`) | 404 tal cual |
| apikey / username / token en el bundle | **ninguno** |

**Diferencia clave con GENESIS:** ahi la apikey viajaba en claro en el bundle publico. Aca **no
esta**. El 401 en `busqueda_por_gestion` (y no 404) confirma que el endpoint existe y que las
convenciones son las mismas del Organo Judicial, pero falta la credencial.

**El volumen de KRIMA para Tarija queda NO MEDIDO.** Para verlo hace falta un navegador real que
intercepte el trafico, igual que con GENESIS la primera vez. Es trabajo de otro turno, no una
conclusion apurada, y aparecio un host nuevo (`zeus.organojudicial.gob.bo`) que tampoco estaba en
el mapa.

---

## Lo que esto cambia

1. **Los codigos entran ya.** 10 completos disponibles en markdown, de dominio publico por
   naturaleza. Es un adaptador de 30 lineas al pipeline que ya existe.
2. **KRIMA necesita una decision, no mas intentos a ciegas.** Es la unica fuente de primera y
   segunda instancia de Tarija, y esta detras de una llave.
3. **`zeus.organojudicial.gob.bo` es un host nuevo** que sirve catalogos de oficinas judiciales.
   NO MEDIDO que mas expone.
