# Evidencia cruda: la API devuelve todas las procedencias

**2026-09-03.** Máquina: `brain-env` (gateway MUDH, servicio `build`), Celeron N4020, 2 cores.
Commit medido: `0a083c5a30d55836eaf79a3eb175142d797fa3e4`. API `1.1.0`.

Verbatim, sin recortar. El veredicto va aparte al final.

---

## 1. Tests unitarios (19/19)

```plain
$ python3 -m unittest -v test_alias test_ingesta test_procedencias
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
test_BASE_VIEJA_dice_NO_MEDIDO_y_no_cero (test_procedencias.ProcedenciaEnLaApiTest...) ... ok
test_alcance_cuenta_procedencias (test_procedencias.ProcedenciaEnLaApiTest...) ... ok
test_el_documento_expone_su_procedencia (test_procedencias.ProcedenciaEnLaApiTest...) ... ok
test_la_busqueda_lleva_las_fuentes_en_cada_resultado (test_procedencias.ProcedenciaEnLaApiTest...) ... ok
test_la_cita_trae_las_dos_fuentes (test_procedencias.ProcedenciaEnLaApiTest...) ... ok
test_uid_inexistente_devuelve_None (test_procedencias.ProcedenciaEnLaApiTest...) ... ok

----------------------------------------------------------------------
Ran 19 tests in 2.560s

OK
```

---

## 2. Falsador HTTP contra la base reconstruida (45/45)

```plain
$ python3 servidor.py --db /workspace/bolivia-v2.db --puerto 8101
corpus-legal-bolivia 1.1.0
  documentos: 3606 | caracteres: 72089578
  por jurisdiccion: {'departamental': 784, 'jurisprudencia': 2822}
  procedencias: 3646 | con varias fuentes: 15
  escuchando en http://127.0.0.1:8101

$ python3 test_api.py http://127.0.0.1:8101
VERDE salud responde 200
VERDE alcance declara documentos
VERDE alcance declara lo que NO cubre
VERDE alcance advierte a los agentes
VERDE alcance cuenta las procedencias registradas
VERDE manifiesto lista herramientas
VERDE manifiesto prohibe citar sin fuente
VERDE manifiesto obliga a citar TODAS las fuentes
VERDE openapi valido
VERDE openapi declara procedencias
VERDE busqueda encuentra
VERDE cada resultado trae cita citable
VERDE cada resultado declara confianza del texto
VERDE vigente se preserva (null = NO MEDIDO)
VERDE cada resultado trae sus procedencias
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
VERDE documento trae sus procedencias con sha256
VERDE documento inexistente da 404
VERDE la API lista los documentos con varias fuentes
VERDE y aclara que varias fuentes NO es un duplicado del corpus
VERDE procedencias devuelve TODAS las fuentes del documento
VERDE cada fuente trae url oficial, archivo y sha256
VERDE un documento con varias fuentes lo ADVIERTE
VERDE y el documento advierte lo mismo en su cita
VERDE procedencias de un uid inexistente da 404
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

## 3. El caso decisivo, servido por HTTP

```plain
$ GET /api/v1/procedencias?limite=3
total con varias: 15

$ GET /api/v1/procedencias/jur-tar-auto-supremo-as-0140-2025-2026-6fd6faa1
{
 "uid": "jur-tar-auto-supremo-as-0140-2025-2026-6fd6faa1",
 "referencia": "Auto Supremo AS/0140/2025",
 "procedencias": 10,
 "fuentes": [
  {
   "fuente_id": "tsj_genesis",
   "fuente_url": "https://apigestortsj.organojudicial.gob.bo/api/v1/documentos/6384310d-d729-4770-b2a2-0112b4181972/pdf",
   "archivo": "tsj-Tarija-2026-AS_0140_2025-94749.txt",
   "sha256": "6fd6faa1b7e89b21524474ccf8ea9582a4163495d919139a5cc4a5ee29512ca3"
  },
  {
   "fuente_id": "tsj_genesis",
   "fuente_url": "https://apigestortsj.organojudicial.gob.bo/api/v1/documentos/6384310d-d729-4770-b2a2-0112b4181972/pdf",
   "archivo": "tsj-Tarija-2026-AS_0140_2025-94750.txt",
   "sha256": "6fd6faa1b7e89b21524474ccf8ea9582a4163495d919139a5cc4a5ee29512ca3"
  },
  ... (10 en total, ids 94749 a 94759)
 ]
}
```

---

## 4. Costo en latencia, medido (5 corridas por consulta)

```plain
prescripcion adquisitiva de dominio -> 36 resultados   | min 14.3 ms | max 17.0 ms
beneficios sociales                 -> 1729 resultados | min 38.7 ms | max 46.2 ms
```

La consulta de procedencias es **una sola** por página de resultados, en lotes de 400 uids, no
una por resultado. Con `limite=100` eso es 1 consulta extra y no 100.

---

## 5. La base VIEJA real, sin la tabla: contesta `null`, no cero

No es un mock: es una copia de `/workspace/ab007/bolivia.db`, la base de las 15:00, servida por
el código nuevo.

```plain
$ python3 servidor.py --db /workspace/vieja.db --puerto 8102
corpus-legal-bolivia 1.1.0
  documentos: 3606 | caracteres: 72089578
  procedencias: None | con varias fuentes: None

procedencias en la cita: None | fuentes: None
advertencia: NO MEDIDO: esta base no registra procedencias (es anterior a documento_aliases).
             No concluir que el documento tiene una ...
null crudo en el JSON: True

$ GET /api/v1/procedencias
{
 "medido": false,
 "total": null,
 "documentos": null,
 "advertencia": "NO MEDIDO: esta base no registra procedencias."
}

alcance.procedencias_registradas: None
```

---

## 6. Veredicto derivado (conclusión, no medición)

**VERDE.** El dato que estaba en la base y no salía por la API ahora viaja en el contrato: cada
cita lleva `fuentes` completo y `procedencias` contado, hay endpoint propio por uid, hay listado
de los 15 documentos con varias entradas, y el manifiesto **obliga** a citarlas todas. El caso
del AS/0140/2025 devuelve sus 10 fuentes por HTTP.

**El tercer estado se mantiene separado.** Una base sin la tabla contesta `null` con advertencia,
no `0` ni lista vacía, y eso está medido contra la base vieja de verdad, no contra un doble.

## 7. NO MEDIDO

- **El frontend no muestra las procedencias.** `sistema/web/index.html` sigue mostrando una sola
  fuente en el sello. El dato ya viaja por la API; la pantalla no lo usa.
- **Nadie abrió el frontend en un navegador.** Sigue igual que a las 15:00.
- **Por qué GENESIS repite el índice.** Sin verificar.
- **Vigencia y derogaciones:** 3.612 items en cola, sin mover.
- **La ruta canónica de la base no cambió.** `bolivia-v2.db` es la buena; quién se sirve en
  producción es decisión de Abraham.
