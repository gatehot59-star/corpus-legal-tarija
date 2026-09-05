# Produccion esta viva, y mi sonda sin User-Agent la declaraba muerta

**2026-09-05 04:40 UTC.** Abraham mando la captura del panel de Abacus: punto verde en "Computadora", boton **Detener** disponible, URL publica `https://150448fcc6.abacusai.cloud`, y en el explorador de archivos `api.py`, `corpus-api.service`, `rag-abogacia-v7.db`, `index.html`, `permalink_inject.js`.

---

## 1. Pedido

Una captura, sin texto. Lo que pide implicitamente: verificar si la VM esta prendida y retomar desde ahi.

## 2. Herramientas y maquina

**brain-env** por el gateway MUDH, servicio `build`, tool `run`: 7 llamadas, **solo lectura**. Los cuatro scripts fueron en base64 con md5 verificado en las dos maquinas. **Cero escrituras en cualquier base. Cero runtime ajeno.**

## 3. Que se midio

| medicion | resultado |
|---|---|
| `/` sin User-Agent | **403**, `error code: 1010`, `server: cloudflare` |
| `/` con UA de Chrome | **200**, `text/html`, `<title>CORPUS · Corpus legal boliviano</title>` |
| `/censo` | **200**: 6.079 documentos, 78.930 pasajes, 102.620.935 caracteres, 112 ms, `estado: vivo` |
| `/buscar?q=usucapion` | **200**, `total_pasajes: 1741` |
| `/buscar?q=zzzqqqxxnoexiste` | **200**, `total: 0` **(control negativo)** |
| vigencia en produccion | `vigencia_no_verificada: 6066` de 6.079, o sea **13** |
| rutas que existen | `/`, `/censo`, `/buscar`, `/texto`. **No** hay `/agente/manifiesto` ni `/estadisticas` |
| SSH por IPv4 | 22172, 22 y 443: **timeout**, sin cambio |
| endpoint SSH oficial | **IPv6-only**, y este container no tiene IPv6 |

## 4. Evidencia cruda verbatim

```plain
$ md5sum /workspace/sonda_http_ua.py
1b23bf2111f284ef138964e2881c6699

[sin UA] 403 https://150448fcc6.abacusai.cloud/
    server=cloudflare cf-ray=a36286f4af6b3f3a-EZE
    b'error code: 1010\n'

[sin UA] 403 https://150448fcc6.abacusai.cloud/buscar?q=usucapion&limit=1
    server=cloudflare cf-ray=a36286f5cd8e7842-EZE
    b'error code: 1010\n'

[UA de Chrome] 200 https://150448fcc6.abacusai.cloud/
    server=cloudflare ct=text/html; charset=utf-8
    b'<!doctype html>\n<html lang="es-BO">\n<head>...<title>CORPUS \xc2\xb7 Corpus legal boliviano</title>'

[UA de Chrome] 200 https://150448fcc6.abacusai.cloud/buscar?q=usucapion&limit=1
    server=cloudflare ct=application/json; charset=utf-8
    b'{"consulta": "usucapion", "expresion": "\\"usucapion\\"", "total_pasajes": 1741,
      "devueltos": 1, "limit": 1, "offset": 0, "ms": 61.0, "filtros": {},
      "facetas": {"materia": [{"v": "Civil", "n": 394}, ...'

$ python3 sonda_censo.py   (md5 e84a6d509d26125d7f557f8b176baa91)
censo bytes: 1507
documentos: 6079
pasajes: 78930
caracteres: 102620935
tipo: Auto Supremo 4966 | Ley Departamental 512 | Resolucion del Pleno 483 |
      Sentencia 59 | Compilado 39 | Codigo 7 | Ley 6 | Resolucion 5 |
      Constitucion 1 | Decreto Ley 1
jurisdiccion: jurisprudencia 5030 | departamental 1034 | nacional 15
via: html_oficial 4817 | ocr 785 | texto_extraido 249 | texto_nativo_pdf 195 |
     ocr_pdf_escaneado 33
vigencia_no_verificada: 6066
ms: 112.19
estado: vivo

$ rutas desconocidas
/agente/manifiesto -> 404 {"error":"ruta desconocida",
                          "rutas":["/","/censo","/buscar","/texto"]}

$ sondas de contenido (con UA)
hay decretos?     q='decreto departamental' -> 200 total=659
control positivo  q='usucapion'             -> 200 total=1741
la vigencia       q='Ley Departamental 500'  -> 200 total=138
debe dar CERO     q='zzzqqqxxnoexiste'       -> 200 total=0

$ SSH, sin cambio
TCP 150448fcc6.ssh4.abacusai.cloud 22172 AF_INET rc 11
TCP 150448fcc6.ssh4.abacusai.cloud    22 AF_INET rc 11
TCP 150448fcc6.ssh4.abacusai.cloud   443 AF_INET rc 11
TCP 150448fcc6.ssh.abacusai.cloud  22172 AF_INET6 rc 99

$ tamanos, para decidir el transporte
v7 bytes            212426752
v7 comprimida bytes  66815638
dd_txt bytes         17007121   (los 926 textos de decretos)
```

## 5. La leccion, que es la tercera de la misma forma

**Un rechazo del cliente se disfraza de ausencia del servidor.** Ya paso con el 401 del TCP (era una firma `x-hash`, no un login), con el 403 de GitHub (era rate limit, no un repo inexistente), y ahora con este 403/1010 de Cloudflare, que es un bloqueo por firma de navegador. Las tres veces el instrumento contestaba sobre **si** y yo concluia sobre **el otro**.

**Y lo que NO puedo afirmar, declarado:** anoche mi sonda sin UA recibio **404**, no 403, asi que el estado del hostname **si** cambio. Pero **nunca probe con UA anoche**, o sea que no puedo descartar que la API ya estuviera arriba y mi instrumento no pudiera verla. **NO MEDIDO.** El arreglo permanente es que toda sonda contra ese hostname lleve UA de navegador, y que un 403 se lea como "mi cliente" hasta probar lo contrario.

## 6. El estado real, en una linea

**Se puede LEER produccion y no se puede ESCRIBIR en ella.** La API responde 200 con datos, pero sirve la base vieja (13 vigencias, sin los 355 titulos arreglados, sin los 926 decretos), y la unica via de escritura que existe es SSH, que sigue en timeout por IPv4 y es IPv6-only en el endpoint oficial.

## 7. NO MEDIDO

- **Si la API estaba arriba anoche.** Mi sonda de anoche no podia distinguirlo.
- **Por que el `ssh4` no rutea con la VM prendida.** Puede ser un alias vencido, un puerto distinto o una regla nueva: no lo se.
- **Si GitHub Actions tiene IPv6.** Seria la via al endpoint oficial y se mide con un workflow que commitea su propio resultado. No se corrio.
- Los **titulos y la vigencia** de produccion contra la base nueva, fila por fila: solo se comparo el agregado.
- **Los 926 decretos siguen sin ingestar. Nada desplegado.**
