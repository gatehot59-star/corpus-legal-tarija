# Evidencia cruda: reconstrucción de la base con procedencia

**2026-09-03.** Máquina: `brain-env` (gateway MUDH, servicio `build`), Celeron N4020, 2 cores.
Commit medido: `2a30a639732d8f5433cbc32adc79e3f36470eff3`.

Esta evidencia va **verbatim, sin recortar**. El veredicto se deriva aparte, al final.

---

## 1. Falsadores de procedencia e ingesta

```plain
$ python3 -m unittest -v test_alias test_ingesta
test_auditoria_ve_el_documento_sin_procedencia (test_alias.AliasTest...) ... ok
test_dos_fuentes_distintas_conservan_las_dos (test_alias.AliasTest...) ... ok
test_hash_de_la_fuente_gana_al_del_texto (test_alias.AliasTest...) ... ok
test_misma_url_generica_con_archivos_distintos_no_se_pisa (test_alias.AliasTest...) ... ok
test_reintento_exacto_es_idempotente (test_alias.AliasTest...) ... ok
test_SABOTAJE_procedencia_que_no_escribe_da_ROJO (test_ingesta.IngestaTest...) ... ok
test_dos_textos_distintos_son_dos_canonicos (test_ingesta.IngestaTest...) ... ok
test_la_vigencia_sin_medir_entra_a_la_cola (test_ingesta.IngestaTest...) ... ok
test_los_chunks_no_se_duplican_por_una_segunda_procedencia (test_ingesta.IngestaTest...) ... ok
test_mismo_texto_en_dos_archivos_no_borra_al_primero (test_ingesta.IngestaTest...) ... ok
test_reingesta_identica_es_idempotente (test_ingesta.IngestaTest...) ... ok
test_un_documento_deja_un_canonico_y_una_procedencia (test_ingesta.IngestaTest...) ... ok
test_una_fuente_no_registrada_no_entra_en_silencio (test_ingesta.IngestaTest...) ... ok

----------------------------------------------------------------------
Ran 13 tests in 1.444s

OK
```

**Primera corrida, en ROJO, sin recortar** (el fallo era del test y quedó como caso propio):

```plain
sqlite3.IntegrityError: FOREIGN KEY constraint failed
  File "/workspace/clt/sistema/api/ingesta.py", line 186, in agregar
    cur = self.con.execute(
Ran 12 tests in 1.153s
FAILED (errors=7)
```

Causa medida: el esquema corre con `PRAGMA foreign_keys=ON` y `documentos.fuente_id` referencia
a `fuentes`. Ingerir sin registrar la fuente **no entra en silencio**, revienta. Ahora es el test
`test_una_fuente_no_registrada_no_entra_en_silencio`.

---

## 2. Reconstrucción completa de la base

```plain
$ python3 ingesta.py --origen /workspace/corpus-todo --db /workspace/bolivia-v2.db
  tarija_gaceta: 784 documentos
  tsj_genesis: 2862 documentos

documentos canonicos: 3606 | chunks: 56311 | procedencias: 3646
por jurisdiccion: {'departamental': 784, 'jurisprudencia': 2822}
cola de revision humana: 3612
segundos: 13.1 | indice: 154.9 MB

VERIFICACION: {"ofrecidos": 3646, "canonicos_nuevos": 3606, "duplicados_por_contenido": 40,
"alias_nuevos": 3646, "alias_reintento_exacto": 0, "sin_rastro": 0, "en_base": 3606,
"alias_en_base": 3646, "documentos_sin_procedencia": 0,
"contenidos_con_varias_fuentes": 15, "veredicto": "VERDE"}
```

Integridad referencial de la base resultante:

```plain
huerfanos: 0
alias sin documento: 0
documentos: 3606 | alias: 3646
```

---

## 3. Falsador de la API contra la base reconstruida

```plain
$ python3 test_api.py http://127.0.0.1:8099
VERDE salud responde 200
VERDE alcance declara documentos
VERDE alcance declara lo que NO cubre
VERDE alcance advierte a los agentes
VERDE manifiesto lista herramientas
VERDE manifiesto prohibe citar sin fuente
VERDE openapi valido
VERDE busqueda encuentra
VERDE cada resultado trae cita citable
VERDE cada resultado declara confianza del texto
VERDE vigente se preserva (null = NO MEDIDO)
VERDE null viaja como null en el JSON
VERDE cero resultados dice hallado=false
VERDE cero resultados trae advertencia
VERDE la advertencia prohibe inferir inexistencia
VERDE el filtro por sala filtra de verdad
VERDE el filtro por jurisdiccion filtra
VERDE el presupuesto se respeta
VERDE consultar incluye instrucciones
VERDE consultar incluye el alcance
VERDE documento por uid estable
VERDE documento trae texto completo
VERDE documento trae su cita
VERDE documento inexistente da 404
VERDE catalogos trae jurisdicciones y materias
VERDE catalogos declara las fuentes
VERDE consulta hostil no rompe: 'AS/0122/2026'
VERDE consulta hostil no rompe: 'Art. 17.I'
VERDE consulta hostil no rompe: 'ley "007"'
VERDE consulta hostil no rompe: 'casacion OR'
VERDE consulta hostil no rompe: 'NEAR('
VERDE consulta hostil no rompe: '*'
VERDE consulta hostil no rompe: '"'

VERDE: la API cumple el contrato que un agente necesita
```

---

## 4. Qué son realmente los 40 duplicados

Hasta hoy estaban explicados como *"el mismo texto listado dos veces en la fuente"*. Eso era
cierto y **no decía el mecanismo**, así que no se podía descartar la hipótesis caE: que el
descargador hubiera traído el mismo PDF para ids distintos y faltaran 40 resoluciones. Medido:

```plain
sha256| alias | urls_distintas | archivos_distintos | uids_distintos
6fd6faa1b7 10 1 10 1
249b908c4a 6 1 6 1
2ce8eb2e43 5 1 5 1
49f3a5258f 4 1 4 1
594c9d0a44 4 1 4 1
b402418d54 4 1 4 1
f216241a07 4 1 4 1
3963fe04ed 3 1 3 1
d15cc75d84 3 1 3 1
58b408328a 2 1 2 1
6f6240556c 2 1 2 1
c8834507dc 2 1 2 1
d239fb2adf 2 1 2 1
d5909385ea 2 1 2 1
f6e80df5f8 2 1 2 1

hashes con MAS DE UNA url: 0
hashes con mas de un uid: 0
apariciones extra totales: 40
```

Y el metadato crudo de los diez registros del caso peor, del propio `resoluciones.jsonl`:

```plain
--- tsj-Tarija-2026-AS_0140_2025-94749.txt / 94750 / 94752 / 94753 / 94754 / 94759 ...
    nro_resolucion = AS/0140/2025
    gestion = 2026
    fecha_emision = 12/05/2026
    sala = Sala Penal
    materia = Penal
    demandante = MINISTERIO PUBLICO y Gobierno Municipal de Villa Montes
    demandado = Marco Antonio Paravicini Sanabria, Jose Antonio Alurralde Tejerina,
                Jesus Jose Varca Flores, Claudio Marcelo Calizaya Mo...
    url_pdf_escaneado = https://apigestortsj.organojudicial.gob.bo/api/v1/documentos/
                        6384310d-d729-4770-b2a2-0112b4181972/pdf
    sha256_pdf = 6fd6faa1b7e89b21524474ccf8ea9582a4163495d919139a5cc4a5ee29512ca3
    id = 94749 | 94750 | 94752 | 94753 | 94754 | 94759
    procesos = Incumplimiento de deberes
```

---

## 5. Veredicto derivado (conclusión, no medición)

**VERDE.** La procedencia está conectada a la ingesta y la base se reconstruyó sin pérdida:
3.646 documentos ofrecidos, 3.646 procedencias registradas, 3.606 documentos canónicos, cero
sin rastro y cero huérfanos. El guard puede dar rojo: el test de sabotaje lo demuestra.

**Los 40 duplicados no son pérdida de cobertura.** GENESIS publica varias filas de índice, con
ids distintos, que apuntan **al mismo UUID de documento y al mismo sha256 del PDF**. Un solo
caso concentra diez ids. La lectura más plausible es una fila por parte procesal (el campo
`demandado` lista varios imputados), pero **eso es inferencia y no está medido**.

## 6. NO MEDIDO

- **Por qué** GENESIS repite el índice. La coincidencia con el número de imputados es plausible
  y no verificada.
- **La API todavía no expone las procedencias.** El dato existe en la base y ningún endpoint lo
  devuelve, así que hoy un agente no puede citar las diez fuentes de ese Auto Supremo.
- **La base vieja no se tocó.** `bolivia-v2.db` es la nueva; `bolivia.db` sigue en su lugar, sin
  borrar ni sobrescribir.
- **Vigencia y derogaciones:** 3.612 items en cola, igual que antes. Este cambio no los mueve.
