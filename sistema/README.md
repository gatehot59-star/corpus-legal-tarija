# Sistema: backend, API para agentes y frontend

Corpus legal boliviano consultable. Hoy tiene Tarija; el esquema y la ingesta estan hechos para
todo el pais desde el dia uno.

## Levantarlo

```bash
# 1. Construir la base desde los corpus crudos (una vez, y cada actualizacion)
python3 sistema/api/ingesta.py --origen <dir-con-corpus> --db bolivia.db

# 2a. En el taller: API + frontend, sin nada en el medio
python3 sistema/api/servidor.py --db bolivia.db --puerto 8080

# 2b. Expuesto a otra gente: SIEMPRE por la frontera
python3 sistema/api/frontera.py --db bolivia.db --puerto 8080 \
        --limite-por-minuto 120 --token "$CORPUS_TOKEN"
# -> http://127.0.0.1:8080
```

Cero dependencias: solo Python 3. **A proposito.** El que va a correr esto es un estudio
juridico, no un equipo de plataforma; un backend con dependencias es un backend que en tres
meses nadie levanta, y el corpus muere con el.

## Medido (2026-09-03, en brain-env: Celeron N4020, 2 cores, sin AVX)

| | |
|---|---|
| documentos canonicos | **3.606** |
| procedencias registradas | **3.646** |
| documentos con varias procedencias | **15** |
| caracteres | **72.089.578** |
| chunks | 56.311 |
| ingesta completa | **13,1 s** |
| indice | 154,9 MB |
| tests unitarios | **36/36 verde** |
| falsador de la API por HTTP | **45/45 verde** |
| busqueda | 14-46 ms |
| primer dato en pantalla | **0,12 s** (era 22,87 s) |

Verificacion de la ingesta, que es el numero que importa:

```json
{"ofrecidos": 3646, "canonicos_nuevos": 3606, "duplicados_por_contenido": 40,
 "alias_nuevos": 3646, "sin_rastro": 0, "en_base": 3606, "alias_en_base": 3646,
 "documentos_sin_procedencia": 0, "contenidos_con_varias_fuentes": 15, "veredicto": "VERDE"}
```

## Procedencia: por que un documento puede tener diez fuentes

La fuente oficial publica **el mismo texto en varias entradas de indice**. El AS/0140/2025 de
Sala Penal aparece en GENESIS con **diez ids** (94749 a 94759), todos apuntando al mismo UUID de
documento y al mismo sha256 del PDF. Medido: de los 15 casos, **ninguno** tiene mas de una URL.

**Eso no es un duplicado del corpus y no es perdida de cobertura:** el documento entra una sola
vez y **cada aparicion queda registrada** en `documento_aliases`. La ingesta exige que todo
documento ofrecido deje rastro, y sale en ROJO si no.

Y hay **tres** estados, no dos:

| `cita.procedencias` | significa |
|---|---|
| `10` | la fuente lo publica en 10 entradas. **Citar `cita.fuentes` completo** |
| `1` | una sola fuente oficial |
| `null` | **NO MEDIDO**: esta base no registra procedencias. No concluir que tiene una sola |

## Como se suma una fuente nueva (lo nacional, otro departamento, un municipio)

Se escribe un **adaptador**: una funcion que recibe un directorio y devuelve `Documento`s.
Nada mas. El uid unico, los chunks con solape, las citas, la procedencia y la cola de revision
son comunes, asi que ninguna fuente nueva puede olvidarse de la parte que importa.

```python
def adaptador_gaceta_nacional(base: Path):
    for p in sorted((base / "nacional").glob("*.txt")):
        yield Documento(
            fuente_id="gaceta_nacional",
            jurisdiccion="nacional",              # <- lo unico que cambia de fondo
            organo="Asamblea Legislativa Plurinacional",
            tipo_norma="Ley", numero="1178", anio="1990",
            titulo="Ley de Administracion y Control Gubernamentales (SAFCO)",
            texto=p.read_text(encoding="utf-8"),
            fuente_url="https://gacetaoficialdebolivia.gob.bo/...",
            archivo=p.name,                        # <- entra en la clave de procedencia
            vigente=True,                          # si se VERIFICO; si no, dejar en None
        )

ADAPTADORES["gaceta_nacional"] = (adaptador_gaceta_nacional, (
    "gaceta_nacional", "Gaceta Oficial del Estado Plurinacional de Bolivia",
    "nacional", "", "Asamblea Legislativa Plurinacional",
    "https://gacetaoficialdebolivia.gob.bo"))
```

Y listo: los filtros del frontend, los catalogos y el alcance de la API se actualizan solos,
porque salen de la base y no de una lista escrita a mano.

**`vigente=None` no es un descuido:** significa NO MEDIDO y la ingesta lo manda automaticamente
a la cola de revision. Poner `True` sin haberlo verificado es exactamente el error que un agente
legal no puede permitirse.

## Endpoints

| ruta | para que |
|---|---|
| `GET /` | el frontend |
| `GET /api/v1/buscar?q=...` | busqueda BM25 con filtros y paginacion |
| `GET /api/v1/documento/{uid}` | documento completo con su cita, sus procedencias y su cola de revision |
| `GET /api/v1/procedencias/{uid}` | **todas** las fuentes oficiales de ese documento |
| `GET /api/v1/procedencias` | los documentos que la fuente publica mas de una vez |
| `GET /api/v1/agente/consultar?q=...&presupuesto=8000` | contexto recortado y citable |
| `GET /api/v1/agente/manifiesto` | contrato para un agente: herramientas y reglas |
| `GET /api/v1/alcance` | que cubre y que **NO** cubre |
| `GET /api/v1/catalogos` | valores validos de cada filtro |
| `GET /api/v1/revision` | cola de revision humana |
| `GET /api/v1/salud` | healthcheck; queda abierto incluso con token |
| `GET /openapi.json` | OpenAPI 3.0.3 |

## Runbook: sacarlo del taller

**`frontera.py` es el entrypoint cuando esto deja de ser localhost.** Envuelve a `servidor.py`
sin tocarlo y agrega cuatro cosas, cada una por un modo de falla concreto:

1. **Limite por IP** (`--limite-por-minuto`, default 120, ventana deslizante). Un cliente mal
   escrito hace 200 busquedas por segundo y el Celeron se queda sin buscador. Devuelve **429**
   con `Retry-After`.
2. **Token opcional** (`--token` o `CORPUS_TOKEN`). Comparado con `hmac.compare_digest`, no con
   `==`. Se acepta por `Authorization: Bearer`, por cookie, o una vez por `?clave=` (que deja la
   cookie y redirige, para que la clave no quede en el historial).
3. **Cabeceras de seguridad** y CORS acotable con `--origen`.
4. **El log NO registra la consulta.** En un estudio juridico la consulta **es el caso**:
   `servidor.py` loguea la linea completa (`?q=nombre+del+cliente`) y eso crea un expediente que
   nadie declaro. La frontera loguea ruta, estado y la IP hasheada con una sal del proceso.

**TLS lo pone un reverse proxy, no esto.** Un token sobre HTTP plano viaja en claro:

```bash
# Caddy: dos lineas y renueva el certificado solo
corpus.estudio.bo {
    reverse_proxy 127.0.0.1:8080
}
```

```bash
# systemd: que sobreviva a un reinicio, que es como muere un servicio de estudio
# /etc/systemd/system/corpus-legal.service
[Service]
EnvironmentFile=/etc/corpus-legal.env      # CORPUS_TOKEN=...
ExecStart=/usr/bin/python3 /opt/corpus-legal/sistema/api/frontera.py \
          --db /var/lib/corpus-legal/bolivia.db --puerto 8080 --limite-por-minuto 120
Restart=always
User=corpus
[Install]
WantedBy=multi-user.target
```

**Respaldo:** la base es **un archivo**. `sqlite3 bolivia.db ".backup copia.db"` en caliente, o
copiar el archivo con el servicio parado. Y si se pierde, **se reconstruye desde los corpus
crudos en 13 segundos**: el indice es derivado, la fuente de verdad son los textos y su manifest.

**Healthcheck:** `GET /api/v1/salud` (abierto siempre). Si devuelve 200 con `estado: ok`, la base
abrio.

**Donde NO va:** en Actions, que corta a las 6 h. Un proceso 24/7 necesita una maquina que no se
destruya.

## Dos errores que quedaron escritos en el codigo

**1. El uid que borraba datos en silencio.** La primera version se armaba con tipo+numero+ano, y
para la Gaceta de Tarija el ano viene vacio. Tres RPA con numero 022 de gestiones distintas
generaban el mismo uid y el ultimo pisaba a los otros dos: **entraron 3.646 documentos y quedaron
3.313.** Peor que fallar: borraba datos y reportaba exito. Ahora el uid lleva los 8 primeros
caracteres del sha256 y `Corpus.verificar()` sale con codigo 3 si algo no deja rastro.

**2. Una tipografia dejaba el sistema en blanco 22,87 segundos.** El frontend cargaba las
fuentes de Google con un `<link rel=stylesheet>` **bloqueante**, y un stylesheet pendiente frena
la ejecucion del script que sigue. Sin internet (o con la CDN bloqueada) no se veia **ni una
cifra ni un resultado** hasta que la peticion fallaba. Medido en un navegador real: **22,87 s
contra 0,12 s** sin bloquear. Nadie lo habia visto porque hasta hoy nadie habia abierto el
frontend en un navegador: se verificaba que el HTML se servia, que no es lo mismo.
