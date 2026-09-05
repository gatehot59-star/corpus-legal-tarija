# La fase 1 de decretos cerro sola, y la base de decretos esta 3 horas atrasada

**Turno de retomo, 2026-09-05 04:22 UTC.** Pedido literal: *"revisa tu documento de capacidades y entorno.md y retomemos el ultimo proyecto corpus"*. Se leyo el inventario, se re-midio el estado real y **no se escribio nada en la base**.

---

## 1. Pedido

Revisar `00-ENTORNOS-Y-CAPACIDADES.md` y retomar el proyecto del corpus legal, que quedo a las 01:15 UTC con la VM apagada y la fase 1 de decretos corriendo.

## 2. Herramientas y maquina

- **brain-env** por el gateway MUDH, servicio `build`, tool `run`: 8 llamadas, lectura y una sola escritura (ninguna a la base).
- **API de GitHub** (`githubmcp`): lectura del inventario en `mudh-mobile`, de los commits de `corpus-legal-tarija` en `titan/paginacion-permalinks`, y escritura de este archivo.
- **ClickUp**: lectura de los dos Docs del turno anterior y creacion del Doc espejo.
- Cuota ajena gastada: **cero**. Runtime de la VM: **cero, sigue apagada**.

## 3. Que se midio

| medicion | numero | instrumento |
|---|---|---|
| fase 1 de decretos | **CERRADA**: 926 ok, 9 no_pdf, 536,6 min | `tail extrae_dd.log` |
| textos en disco | **926** archivos en `dd_txt` | `ls | wc -l` |
| jsonl acumulado | **935** lineas, 926 `ok` + 9 `no_pdf`, **0 ids repetidos** | `json.loads` sobre cada linea |
| decretos en la base | **0** de tipo Decreto Departamental en las dos bases | `sqlite3` |
| VM publica | **404** de Cloudflare | `curl -w '%{http_code}'` |
| puertos de la VM | 22172, 22 y 443: **errno 11 (timeout) los tres** | `socket.connect_ex` |
| **v7 contra v9** | vigencia **21 vs 13**, titulos con `start=` **1 vs 401** | `sqlite3` en `mode=ro` |

## 4. Evidencia cruda verbatim

```plain
$ tail extrae_dd.log
  [ 920/931] ok=911 pobres=0 fallos=9 | 1.7 doc/min | faltan ~6 min

EXTRAIDOS ok: 922 | texto pobre: 0 | fallos: 9 | minutos: 536.6

$ ls dd_txt | wc -l   -> 926
$ ls dd_pdf | wc -l   -> 935
$ wc -l extrae_dd.jsonl -> 935
$ date -u             -> Sat Sep  5 04:22:37 UTC 2026

$ python3 (conteo del jsonl)
lineas 935
claves ['anexo', 'anio', 'chars', 'estado', 'id', 'numero', 'pags', 'seg', 'sha256', 'slug', 'url', 'via']
Counter({'ok': 926, 'no_pdf': 9})
uids repetidos []

$ curl -s -o /dev/null -w 'PUBLICO http=%{http_code}' https://corpus-tarija.abacusai.cloud/
PUBLICO http=404

$ python3 (connect_ex a 150448fcc6.ssh4.abacusai.cloud)
[(22172, 11), (22, 11), (443, 11)]

$ python3 (las dos bases en mode=ro)
[('bolivia-v7.db', 6079, 21, 1, 1), ('bolivia-v9-decretos.db', 6079, 13, 401, 1)]
   formato: (archivo, documentos, vigencia no nula, titulos con 'start=', decretos)

$ tail ingesta_dd.log   (el intento del 2026-09-04 18:21, que MURIO)
  [  38/935] DD 42    2025  texto_nativo_pdf     4345 car   3 ch   0.1s
FileNotFoundError: [Errno 2] No such file or directory:
  '/workspace/ab-probe-20260903/ocr_run'

$ mtime de las bases
bolivia-v7.db           Sep  5 01:05   <- vigencia 21 y titulos aplicados
bolivia-v9-decretos.db  Sep  4 19:55   <- copia ANTERIOR a los dos arreglos
```

## 5. El hallazgo: la base de decretos se bifurco

`bolivia-v9-decretos.db` se copio a las **19:55 UTC**. La vigencia masiva se aplico a las **00:43** y los titulos entre las **00:58 y las 01:06**, las dos sobre `bolivia-v7.db`. O sea que la base donde iban a entrar los 926 decretos **no tiene ninguno de los dos arreglos de anoche**: vigencia 13 en vez de 21, y 401 titulos con parametro de URL en vez de 1.

Ingestar ahi no habria dado error: habria dado **un tercer estado de la verdad**, y el trabajo de anoche desaparecia en silencio al desplegar. Es la misma forma del `uid` que colisionaba y reportaba exito.

**Decision derivada:** la ingesta de los 926 decretos va sobre `bolivia-v7.db`, con respaldo previo y el guard de integridad 9/9 despues. No se corrio en este turno.

## 6. NO MEDIDO

- **Los 926 decretos NO estan ingestados.** El corpus sigue en 6.079 documentos.
- Los **9 `no_pdf`** no se re-intentaron, y las **5 diferencias** entre las 940 del censo y las 935 del jsonl no se explicaron.
- Si `ingesta_dd.py` corre bien leyendo de `dd_txt` en vez de OCRear: su ultima corrida murio en el documento 38.
- **4.650 Autos Supremos sin titulo** (94% de la jurisprudencia): medido ayer, sigue sin tocar.
- La causa del 404 del hostname: se mide con la VM prendida, no antes.
- **Nada desplegado.**
