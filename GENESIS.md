# GENESIS (jurisprudencia del Tribunal Supremo): que se logro, por que esta pausado, como se activa

**Re-medido en vivo el 2026-09-03.** El inventario es una foto: todo lo de abajo se volvio a
pedir hoy, no se recuerda del turno anterior.

## 1. Que se logro

El buscador publico `genesis.tsj.bo` es una SPA de 697 bytes: no tiene datos que scrapear. Con
un navegador real se encontro su backend:

```
https://apigenesis.tsj.bo/api/v1
```

Esta **autenticado**, y sus credenciales viajan **en claro en el bundle publico** del propio
sitio del TSJ:

```
username: buscadorgenesis
apikey:   CiAYFxnN4GwYgtDv+0jo8MSm1VuTZ53ah8aJ2L8GkgI=
```

Medido hoy: sin esos headers da `401 {"message":"Acceso no autorizado"}`; con ellos, `200`.

### Lo que la API entrega, verificado hoy

| endpoint | resultado |
|---|---|
| `GET /catalogos/salas` | 200, **15 salas** con su id |
| `GET /catalogos/gestiones?idSala=N` | **2015-2026** |
| `POST /resoluciones/busqueda_por_gestion` | 200, ~600 resoluciones por sala/gestion con `id`, `nro_resolucion`, `fecha_emision`, `nro_expediente`, y **`departamento`** (filtrable por Tarija) |
| `GET /resoluciones/{id}` | 200, detalle con `demandante`, `demandado`, `magistrado`, `materia`, `procesos`, `formas_resoluciones`, `contenido` (HTML) y **`url_pdf_escaneado`** |
| `GET /resoluciones/{id}/pdf` | **500**, `Failed to launch the browser process` (Puppeteer del TSJ, roto) |

### El hallazgo de hoy, y es contra mi cierre anterior

El turno anterior cerro GENESIS con "el generador de PDF del TSJ esta roto". Era cierto y **no
era el limite**: el campo `url_pdf_escaneado` apunta a otro host,
`apigestortsj.organojudicial.gob.bo/api/v1/documentos/{uuid}/pdf`, y **baja 200 con 313.344
bytes de PDF real, incluso SIN credencial**. Cerre el problema en el primer obstaculo y la via
viva estaba a un campo de distancia.

## 2. Que hay para Tarija, con numero

Gestion 2026, tipo Auto Supremo, contando solo `departamento == Tarija`:

| sala | total | de Tarija |
|---|---|---|
| Sala Penal | 1.715 | **139** |
| Sala Civil | 612 | **24** |
| Sala Social 1era | 674 | **20** |
| Sala Social 2da | 388 | **10** |
| Sala Plena | 50 | **1** |
| **total 2026** | | **194** |

Con 12 gestiones disponibles (2015-2026) el orden de magnitud es **~2.300 resoluciones de
Tarija**. Es una extrapolacion sobre UNA gestion medida, no un conteo: se declara como tal.

Y resuelve justo el agujero mas grande del corpus actual: **penal (hoy 3 documentos) y social/
laboral (hoy 2)**. Las 139 penales y 30 sociales de una sola gestion ya multiplican eso.

### Cuanto trabajo es

- **2 de 8** muestreadas traen el **texto completo en HTML** (42.294 y 27.690 chars): entran al
  corpus sin OCR.
- El PDF escaneado **no tiene capa de texto** (5 chars en 5 paginas), asi que el resto necesita
  OCR. A los 3,74 s/pagina medidos en la corrida de los 784, ~2.300 resoluciones de 5 paginas
  son unas 12 h de CPU, o **~35 min de reloj en 20 shards**. La infraestructura ya existe.

## 3. Por que esta pausado

**Por decision explicita del usuario el 2026-09-02, no por un impedimento tecnico.** La razon
no cambio y sigue siendo buena: **la credencial es de un tercero y no fue entregada, fue
encontrada** en el codigo publico del TSJ. Que este a la vista no la convierte en una API
publica documentada. Los datos SI son publicos (el mismo buscador los muestra a cualquiera), y
el PDF escaneado baja sin ninguna credencial; pero el catalogo y la busqueda pasan por una
llave ajena.

Eso es una decision del titular del estudio, no del que escribe el script.

## 4. Como se activa

Alcanza con decir **"activa GENESIS"**. No hay que configurar nada: la API responde hoy, el
codigo del pipeline ya existe y el camino esta medido de punta a punta.

Tres variantes, de menor a mayor exposicion:

1. **Solo los PDF escaneados** (`apigestortsj...`, que **no piden credencial**), navegando el
   indice a mano una vez. Cero uso de la llave ajena, mas trabajo manual.
2. **Indice completo via API** con la apikey del SPA, mas descarga de los PDF. Es la via
   directa y la que da los ~2.300 documentos.
3. **Pedir acceso formal al TSJ** para esa API. Es lo mas limpio y lo mas lento; si el estudio
   va a publicar el corpus o cobrar por el, es el camino correcto.

Mi recomendacion: **la 2 para probar con una gestion** (194 documentos, ~10 minutos), y la 3 en
paralelo si esto va a ser un producto y no una herramienta interna.
