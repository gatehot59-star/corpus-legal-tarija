# Evidencia cruda: el frontend en un navegador real, y la frontera de confianza

**2026-09-03, 19:50-20:10 UTC.** Verbatim, sin recortar. El veredicto va aparte al final.

**Dos maquinas, y la distincion importa:**

- **Sandbox del agente** (4 nucleos, **sin red**): tiene `chrome-headless-shell 145.0.7632.6`.
  Ahi corrio el navegador. Cliente CDP propio en Python puro sobre WebSocket, porque el sandbox
  tiene el navegador y no tiene `playwright`: el navegador estaba, faltaba el cable.
- **`brain-env`** (gateway MUDH, servicio `build`, Celeron N4020): la base real de 3.606
  documentos, los tests unitarios y el push.

**Que es real y que es fixture, declarado antes de los numeros:**

- El **archivo** `sistema/web/index.html` es el real, byte por byte (hash abajo).
- Las **respuestas de la API** son las de la API real corriendo en `brain-env` sobre la base
  reconstruida: se capturaron por HTTP y se sirvieron localmente al navegador. La de `documento`
  se derivo del resultado de busqueda real (mismos campos, mismas 10 fuentes) porque el original
  pesa 76 KB.
- **El servidor Python no corrio en el sandbox.** El sujeto medido aca es el **frontend**.

---

## 1. El archivo que abrio el navegador es el que esta en el repo

```plain
bytes           21055
sha256          f9487aa9b45dabb6d02d78481952631d99098c957c265ec73443b6408d4ebb35
git blob sha1   fb8ac9ab0aacce606ac6e4db5c1e522678e6dc06
```

Y el blob que GitHub reporta en `titan/integridad-aliases`:

```plain
[{"name":"index.html","sha":"fb8ac9ab0aacce606ac6e4db5c1e522678e6dc06","size":21055}]
```

**Coinciden.** No es "lo probe y despues subi algo parecido": es el mismo objeto.

---

## 2. ROJO encontrado en el navegador: una tipografia dejaba el sistema en blanco

Primer intento de medir el DOM, sin tocar nada:

```plain
readyState: loading
scripts: 1
largo del script en el DOM: 8905
$ definido: undefined
arrancar definido: undefined
ultimo trozo del script: '...\narrancar();\n'
```

El script estaba completo en el DOM y **no se habia ejecutado**. Causa: un
`<link rel=stylesheet>` pendiente **bloquea la ejecucion del script que sigue**, y el sandbox no
tiene red, asi que `fonts.googleapis.com` no resolvia. Medicion del costo, mismo navegador,
misma pagina, unica diferencia el modo de carga de la fuente:

```plain
sin bloqueo (corregido)      datos en pantalla a los 0.12 s
con bloqueo (el de hoy)      datos en pantalla a los 22.87 s
```

**190 veces.** Y no es "se ve fea sin la tipografia": no aparecia **ni una cifra ni un
resultado**, porque el script que pide los datos no habia corrido. Un estudio de Tarija con
internet flojo veia un buscador roto, y la causa era una fuente decorativa.

Corregido con `media="print" onload="this.media='all'"` mas `<noscript>`. Si la fuente nunca
llega, se ven Georgia y Helvetica y el sistema funciona igual.

---

## 3. El DOM medido, estado MEDIDO

```plain
titulo: Corpus Legal · Bolivia
cifras: 3.606 / documentos / 72,1 M / caracteres de texto / 3.646 / fuentes oficiales registradas / 3.612 / en revisión humana
filtros: 5
aviso de alcance: En 15 documentos la fuente oficial publica el mismo texto en más de una entrada de índice...
estado: 2 pasajes coinciden con "AS/0140/2025" · mostrando 2 desde 1 · 3 ms
fichas: 2
data-proc de los sellos: ["1","10"]
insignias: ["VIGENCIA NO MEDIDA","TEXTO OFICIAL","VIGENCIA NO MEDIDA","10 FUENTES","OCR VERIFICADO"]
entradas listadas: 10
archivos distintos: 10
aviso del sello: la fuente publica este mismo texto en 10 entradas de indice distintas: citar `fuentes` completo, no ...
```

Las **10** entradas listadas son **10 archivos distintos**, no el mismo repetido diez veces.

### El detalle del documento

```plain
modal abierto: True
titulo del modal: Auto Supremo AS/0140/2025 de 2026
sello del modal data-proc: 10
details abierto por defecto: True
entradas en el modal: 10
revision humana en el modal: 1 punto(s) pendientes: vigencia_no_medida
```

En el detalle el sello va **abierto**: si alguien esta ahi es porque va a copiar una cita, y la
copia tiene que salir completa.

---

## 4. El DOM medido, estado NO MEDIDO (base sin la tabla de procedencia)

```plain
data-proc (no medido): ["nomedido","nomedido"]
clases del sello: sello nomedido
texto del sello: PROCEDENCIA · NO MEDIDA | FUENTE OFICIAL | UID jur-tar-auto-supremo-as-0140-2025-2025-f7469a78 | Esta base no registra procedencias. No concluir que e...
insignias (no medido): ["VIGENCIA NO MEDIDA","PROCEDENCIA NO MEDIDA","TEXTO OFICIAL","VIGENCIA NO MEDIDA","PROCEDENCIA NO MEDIDA","OCR VERIFICADO"]
```

Y la rama de las cifras, con `alcance.procedencias_registradas: null`:

```plain
cifras: 3.606 / documentos / 72,1 M / caracteres de texto / no medido / fuentes oficiales registradas / 3.612 / en revisión humana
dice 'no medido': True
el aviso de varias fuentes NO aparece: True
```

El sello pasa a **gris y punteado**, nunca vino: el color es parte del dato.

---

## 5. La frontera de confianza, 17/17 en `brain-env`

```plain
$ python3 -m unittest -v test_frontera
test_pasarse_del_limite_da_429_con_retry_after ... ok
test_limite_cero_lo_desactiva ... ok
test_la_ventana_es_deslizante_y_no_cubeta_de_reloj ... ok
test_el_limite_es_por_cliente ... ok
test_sin_token_configurado_todo_abierto ... ok
test_con_token_sin_credencial_da_401 ... ok
test_token_correcto_por_cabecera_entra ... ok
test_token_equivocado_no_entra ... ok
test_cookie_de_acceso_entra ... ok
test_salud_queda_abierta_para_el_monitor ... ok
test_la_busqueda_tambien_esta_protegida ... ok
test_cabeceras_de_seguridad_en_toda_respuesta ... ok
test_una_sola_cabecera_de_cada_una ... ok
test_cors_se_puede_acotar_a_un_origen ... ok
test_el_log_no_registra_la_consulta ... ok
test_el_anonimo_es_estable_y_distinto_por_ip ... ok
test_x_forwarded_for_solo_se_cree_desde_loopback ... ok

Ran 17 tests in 6.247s
OK
```

El log, verbatim, mientras corrian los tests: **ruta, estado y cliente hasheado, sin la
consulta**.

```plain
[api] GET /api/v1/alcance 200 cliente=4aed2784
[api] GET /api/v1/alcance 401 cliente=4aed2784
[api] GET /api/v1/salud 200 cliente=4aed2784
```

### Y el contrato completo DETRAS de la frontera

Un gate que rompe la API no sirve, asi que se corrio el falsador entero contra la frontera y no
contra el servidor desnudo:

```plain
$ python3 frontera.py --db /workspace/bolivia-v2.db --puerto 8110 --limite-por-minuto 300
corpus-legal-bolivia 1.1.0 (con frontera)
  documentos: 3606 | procedencias: 3646
  token: no | limite: 300 pedidos/min por IP | origen CORS: *
  el log NO registra la consulta
  escuchando en http://127.0.0.1:8110

$ python3 test_api.py http://127.0.0.1:8110
VERDE: la API cumple el contrato que un agente necesita     (45/45)
```

### Suite completa

```plain
$ python3 -m unittest test_alias test_ingesta test_procedencias test_frontera
Ran 36 tests in 9.299s
OK
```

---

## 6. Veredicto derivado (conclusion, no medicion)

**VERDE.** El frontend estampa todas las procedencias con sus tres estados, y esta vez esta
medido **en un navegador**, que era el NO MEDIDO mas viejo de este sistema: venia declarado en
tres reportes seguidos. De paso aparecio un defecto que solo un navegador podia encontrar y que
valia 22,87 segundos de pantalla en blanco.

**La frontera existe y se falsa sola**: 429 medido, 401 medido, token equivocado rechazado con
comparacion en tiempo constante, y el log sin la consulta. La API completa pasa 45/45 **detras**
de la frontera.

## 7. NO MEDIDO

- **Nadie lo abrio en un navegador de escritorio con red.** Lo que esta medido es un Chrome
  headless real, sin red. Falta el ojo de una persona en una pantalla, y con las tipografias
  cargadas.
- **Movil:** solo se midio a 1280 px de ancho. El CSS tiene su media query y **no se probo**.
- **TLS y el despliegue:** el runbook esta escrito, nada de eso se ejecuto. No hay hosting.
- **La calidad juridica** de los resultados sigue siendo juicio profesional, sin medir.
- **Vigencia y derogaciones:** 3.612 items en cola, sin mover.
- **`unsafe-inline` en la CSP** es una concesion real: el frontend es un solo archivo con estilo
  y script adentro, a proposito. Queda declarado, no disimulado.
- **La cookie de acceso no expira** y no hay rotacion de token: para un estudio chico alcanza,
  para mas de eso no.
