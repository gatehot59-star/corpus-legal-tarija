# EXP-TCP-001 · El buscador del TCP no pide credencial: el 401 era una firma de cliente

Fecha de medicion: 2026-09-03 (America/Argentina)
Maquina: brain-env (urllib) + navegador real headless (Chromium 140)
Sujeto: https://buscador.tcpbolivia.bo

## Lo que yo habia afirmado (Y ESTABA MAL / NO MEDIDO)

En chat afirme que para pasar el `401` de la API del TCP hacia falta **conseguir una credencial
institucional** (usuario/clave, API key o cookie de sesion), y ofreci redactar la solicitud.
**Eso no estaba medido.** Nunca observe el trafico real de la aplicacion antes de decirlo.
Lo que medi hoy lo refuta.

## Medicion 1 · El HTML crudo NO trae el texto (SPA vacia)

`GET` directo con urllib, sin JS, User-Agent de navegador:

| URL | status | bytes | sha256[:12] | trae texto |
|---|---|---|---|---|
| /robots.txt | 200 | 53174 | f19393e1d425 | no |
| /resolucion/139630 | 200 | 53174 | f19393e1d425 | no |
| /resolucion/208211 | 200 | 53174 | f19393e1d425 | no |
| /resolucion/139631 | 200 | 53174 | f19393e1d425 | no |
| /resolucion/1 | 200 | 53174 | f19393e1d425 | no |
| /resolucion/99999999 | 200 | 53174 | f19393e1d425 | no |

**Los seis devuelven el MISMO cuerpo byte a byte**, incluido `robots.txt` y un id inexistente.
Es el shell de una SPA Angular (`<app-root>`). Consecuencia operativa: **un `200` de esta ruta no
prueba que la resolucion exista**, y `robots.txt` no es consultable por esta via (NO MEDIDO si
existe uno real detras del rewrite).

## Medicion 2 · Renderizado en navegador real: el texto COMPLETO es publico

`/resolucion/139630` en Chromium headless, sin login, sin cookies previas:

- SCP **1313/2015-S2**, Sucre, 16 de diciembre de 2015, Sala Segunda.
- Expediente **11838-2015-24-AAC**, `Departamento: Tarija`, accion de amparo constitucional
  (Asamblea Regional del Chaco Tarijeno).
- **43.786 caracteres** de texto renderizado.
- Contiene `FUNDAMENTOS JURIDICOS DEL FALLO`, `POR TANTO` y las firmas de los magistrados.

O sea: **no es un encabezado, es la resolucion entera**, y es publica.

## Medicion 3 · Por que daba 401: tres cabeceras, ningun credencial

La unica llamada de datos que hizo la pagina fue:

`GET https://buscador.tcpbolivia.bo/api/buscador-resolucion/getResolucion/139630` -> **200 OK**

Cabeceras de esa peticion, verbatim de lo capturado:

```
x-client-id: angular-app
x-timestamp: 1788486796857
x-hash: 4e39661f698e15fe743fd4784147e04245ad02f7d0e144fdbb4383dc85d8cb4e
accept: application/json, text/plain, */*
referer: https://buscador.tcpbolivia.bo/resolucion/139630
```

**No hay `Authorization`, no hay `Cookie`, no hay token de sesion.** El `401` que yo habia
observado venia de la ausencia de `x-client-id` / `x-timestamp` / `x-hash`: es una **firma de
integridad de cliente** que calcula el JS publico, no una autenticacion de usuario.

## Que se cae de mi respuesta anterior

1. **No hay credencial que pedir para LEER.** Pedir acceso institucional al TCP sigue siendo
   sano para volumen, licencia y redistribucion, pero **no es un prerrequisito tecnico**.
2. **No hace falta la cuenta de ningun abogado.** La hipotesis "usar la cuenta de un abogado de
   Yacuiba" queda descartada por innecesaria, no solo por prestada.
3. El camino tecnico es **renderizar con navegador real** (la app firma sola) o replicar la firma.
   Preferencia: navegador real, lento y respetuoso, porque no toca el mecanismo del sitio.

## NO MEDIDO (explicito, no se cierra en verde)

- **Censo**: cuantas resoluciones con `Departamento: Tarija` existen, y por gestion. Sin medir.
- **Enumeracion legitima**: la ruta de busqueda con filtros (`getListResolucion` y familia) no fue
  ejercida todavia. Iterar ids a ciegas queda descartado como metodo.
- **Licencia y politica de reuso**: no medida. El texto es publico; **publico no es lo mismo que
  redistribuible**. Falta leer terminos del sitio y la norma de publicidad de la Gaceta
  Constitucional Plurinacional antes de integrar al corpus.
- **PDF oficial**: si existe un documento firmado descargable por resolucion. Sin medir.
- **Rate limit** del backend. Sin medir.

## Estado

TCP: **VIVO y publico, con texto integral verificado en 1 documento**. Integrado al corpus: **NO**.
Censo: **NO MEDIDO**. Licencia: **NO MEDIDA**, y bloquea la ingesta hasta resolverse.
