# Sistema: backend, API para agentes y frontend

Corpus legal boliviano consultable. Hoy tiene Tarija; el esquema y la ingesta estan hechos para
todo el pais desde el dia uno.

## Levantarlo

```bash
# 1. Construir la base desde los corpus crudos (una vez, y cada actualizacion)
python3 sistema/api/ingesta.py --origen <dir-con-corpus> --db bolivia.db

# 2. Levantar API + frontend
python3 sistema/api/servidor.py --db bolivia.db --puerto 8080
# -> http://127.0.0.1:8080
```

Cero dependencias: solo Python 3. **A proposito.** El que va a correr esto es un estudio
juridico, no un equipo de plataforma; un backend con dependencias es un backend que en tres
meses nadie levanta, y el corpus muere con el.

## Medido (2026-09-03, en brain-env: Celeron N4020, 2 cores)

| | |
|---|---|
| documentos | **3.606** |
| caracteres | **72.089.578** |
| chunks | 56.311 |
| ingesta completa | **31,7 s** |
| indice | 153,1 MB |
| falsador de la API | **33/33 verde** |
| busqueda | 5-20 ms |

Verificacion de la ingesta, que es el numero que importa:
`{"ofrecidos": 3646, "reemplazados": 40, "en_base": 3606, "perdidos": 0, "veredicto": "VERDE"}`

Los 40 reemplazados son documentos con **el mismo hash**, o sea el mismo texto listado dos veces
en la fuente: deduplicacion real, no perdida. La ingesta lo distingue porque el uid lleva el
hash del contenido.

## Como se suma una fuente nueva (lo nacional, otro departamento, un municipio)

Se escribe un **adaptador**: una funcion que recibe un directorio y devuelve `Documento`s.
Nada mas. El uid unico, los chunks con solape, las citas y la cola de revision son comunes, asi
que ninguna fuente nueva puede olvidarse de la parte que importa.

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
| `GET /api/v1/documento/{uid}` | documento completo con su cita y su cola de revision |
| `GET /api/v1/agente/consultar?q=...&presupuesto=8000` | contexto recortado y citable |
| `GET /api/v1/agente/manifiesto` | contrato para un agente: herramientas y reglas |
| `GET /api/v1/alcance` | que cubre y que **NO** cubre |
| `GET /api/v1/catalogos` | valores validos de cada filtro |
| `GET /api/v1/revision` | cola de revision humana |
| `GET /openapi.json` | OpenAPI 3.0.3 |

## Un error que quedo escrito en el codigo

La primera version del `uid` se armaba con tipo+numero+ano, y para la Gaceta de Tarija el ano
viene vacio. Tres RPA con numero 022 de gestiones distintas generaban el mismo uid y el ultimo
pisaba a los otros dos: **entraron 3.646 documentos y quedaron 3.313.** Peor que fallar: borraba
datos y reportaba exito.

Ahora el uid lleva los 8 primeros caracteres del sha256 (estable entre corridas, unico por
construccion) y `Corpus.verificar()` compara lo ofrecido contra lo que quedo en la base y sale
con codigo 3 si difiere. Un pipeline que no puede detectar su propia perdida de datos no esta
medido, esta supuesto.
