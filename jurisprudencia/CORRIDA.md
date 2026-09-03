# Historico completo de jurisprudencia: Tarija, 2015-2026

Disparado el 2026-09-03. **12 jobs en paralelo, uno por gestion**, cada uno con los **3 tipos**
de resolucion (Auto Supremo, Sentencia, Resolucion) y las 15 salas.

## Lo que se corrigio antes de lanzar

La corrida anterior (194 resoluciones de 2026) uso `idTipoRes=1` **sin haber preguntado que
otros tipos existen**. El catalogo tiene tres. O sea que esas 194 no eran "la jurisprudencia de
Tarija 2026": eran sus Autos Supremos. El censo lo confirmo con numero: **2015 sola tiene 345
resoluciones de Tarija con los tres tipos**, contra 194 de 2026 con uno solo.

## Censo previo, medido por gestion

| gestion | resoluciones de Tarija |
|---|---|
| 2015 | 345 |
| 2016 | 303 |
| 2017 | 240 |
| 2018 | 235 |
| 2019 | 248 |
| 2020 | 179 |

El censo siguio corriendo despues de lanzar; el total real lo escribe el propio job.

## Por que matriza por gestion y no por shard global

El reparto por gestion es **estable y legible**: si 2019 falla, se re-corre 2019 y nada mas.
Un shard global de 20 mezcla anos y obliga a re-correr todo para arreglar uno.

El resultado (estados, tipos, vias de obtencion del texto, duplicados descartados y cobertura
12/12) lo escribe el job en `RESUMEN.md` y `COBERTURA.txt` de este directorio.
