# 2026-09-04 · Cache sellado, VM rescatada y apagada (verificado desde afuera)

Orden de Abraham: "Apagá la VM y guardá el cache primero". Se ejecutó en ese orden y cada paso quedó medido.

## 1. El cache, sellado antes de tocar nada

Snapshot en `/workspace/snapshots/cache-dd-20260904-1840/` (brain-env):

| item | medido |
|---|---|
| documentos extraídos copiados | 46 JSON |
| tamaño | 1,2 MB |
| manifiesto | `MANIFEST-dd_txt.sha256` (46 líneas, un sha256 por archivo) |
| sello del manifiesto | `adfdff9ace0114685c93631b3b54c6dfed4848a6734400566a15f5236ffeece6` |
| PDFs fuente | 81 archivos, 183,1 MB, quedan en el working dir (INC-002: nada de binarios a git) |

## 2. Lo que vivía SOLO en la VM y ahora está local

Hallazgo: la base servida en producción **no era byte-idéntica a ninguna copia local**. VM `rag-abogacia-v7.db` = `aaad5f53016ab1931eb1cd638138043e`; local `bolivia-v7.db` = `dff1634200dac9793b625380f9ad8297`, `bolivia-v8.db` = `5513658bb2f6a7f96d2587f509b9fd34` y **sin columna `vigencia_estado`** (5.991 documentos). Los 13 estados de vigencia y las notas de derogación estaban escritos en la base de la VM. Apagar sin bajarla habría apostado ese trabajo a que el disco de Abacus persista, que era un NO MEDIDO.

Rescate en `/workspace/snapshots/vm-corpus-20260904-1845/` vía `tar` por túnel ssh (212.510.720 bytes), verificado md5 contra el origen:

| archivo | md5 en VM | md5 local | ¿igual? |
|---|---|---|---|
| `rag-abogacia-v7.db` (212 MB, la del unit) | `aaad5f53016ab1931eb1cd638138043e` | `aaad5f53016ab1931eb1cd638138043e` | sí |
| `api.py` (18.111 B, con /verificar) | `7784b52dd0dee59b465cb612115586a1` | `7784b52dd0dee59b465cb612115586a1` | sí |
| `index.html` (38.887 B) | `cbd49360ec471c976a6e06fe23630690` | `cbd49360ec471c976a6e06fe23630690` | sí |
| `estado.html` (10.049 B) | `32e0582502cb4d851e590b268bcc5640` | `32e0582502cb4d851e590b268bcc5640` | sí |

También bajados: `corpus-api.service`, `corpus.conf`, `corpus-legal.conf` (el de `/home/ubuntu` y el de `/etc/nginx/conf.d`), `nuevo_host.sh`, `api.log`.

## 3. Apagado

1. `systemctl stop corpus-api nginx` → los dos pasan de `active` a `inactive`.
2. Quedan **`enabled`**: al volver a prender la VM, el buscador y la API levantan solos.
3. `-wal` en 0 bytes y `sync` antes del corte; md5 de la base sin cambios después de parar los servicios.
4. `poweroff`.

### Verificación desde afuera (no desde la propia VM, W-01)

| instrumento | resultado |
|---|---|
| `ssh -p 22172` | `connect to host ... port 22172: Connection timed out` |
| `curl https://corpus-tarija.abacusai.cloud/` | HTTP **503** |
| `curl .../estado` | `Unavailable` |

El costo de hosting era **1 crédito cada 5 minutos mientras corre** (doc oficial de Abacus). Dato del mismo doc que corrige una suposición: el auto-apagado se dispara cuando **no hay tareas ni servicios corriendo**; con `corpus-api` y `nginx` activos la VM no se iba a apagar sola, salvo que estuviera el toggle *Always On*. Por eso se pararon los servicios además de dar la orden de apagado.

## 4. La extracción NO se tocó: corre en brain-env

Medido en `/proc` (no con `ps`: en este shell `ps` y `pgrep` no existen, y confundir "no está la herramienta" con "el proceso está muerto" es NO MEDIDO disfrazado de rojo):

```
vivos: 17947, 17949, 17950  python3 -u extrae_dd.py --workers=2
        19031  tesseract .../ocr_17949_3126/p-046.png -l spa --psm 4
        19035  tesseract .../ocr_17950_3125/p-045.png -l spa --psm 4
```

**Me refuto la lectura fácil del log.** El log quedó clavado en `[40/931]` desde las 18:27 y el impulso era declararlo colgado. La medición dice otra cosa: los dos workers están OCReando dos gacetas de **165 y 123 páginas**, a ~2,4 páginas/min por worker. El log escribe cada 20 documentos, así que el silencio es el formato del log, no una muerte. Y el ETA que imprime el propio script (~112 min) está mal: asume 8 doc/min, ritmo de texto nativo, no de OCR página por página.

## Estado al cierre

- Producción: **caída a propósito**, 0 créditos de hosting corriendo.
- Nada perdido: base, API, frontend y config verificados byte a byte en brain-env.
- Fase 1 de decretos: 46 de 935 extraídos, corrida viva.
- Para volver a publicar: prender la VM (los servicios están `enabled`) o redeployar desde el snapshot.
