# CPU: terminó en 30 min 59 s; resultado terminal verificado sin relanzar

## 1. Pedido y veredicto

Pedido literal: «Verify the CPU run’s terminal result without relaunching it».

**PASA la terminación técnica de esta única corrida.** El trabajo terminó el 1-nov-2026 a las 02:50:38,782 ART (05:50:38,782 UTC), con worker_exit=0 y estado requires_review. El observador cerró a las 02:50:42,364 ART. Se leyó a las 03:12 ART y se verificó la evidencia recuperada de Git a las 03:17 ART. No se lanzó otra OCR ni se alteraron límites, entradas, servicios instalados o PR33.

**No significa precisión jurídica certificada ni reproducibilidad.** Es cierre del mismo operador, no auditoría independiente. El criterio verificado es ejecución, identidad de entrada/código, reconstrucción de la salida, presupuesto y ausencia actual de procesos propios.

Doc vivo y espejo para el usuario: [Piloto CPU](https://app.clickup.com/90171457413/docs/2kza6fw5-26097), ruta Space > Doc.

[Evidencia terminal acotada publicada](https://github.com/gatehot59-star/corpus-legal-tarija/blob/672c94ddca58d27117dcd0e950c0faeb5bdcf745/docs/agents/evidencia/2026-11-01-cpu-a415b433-terminal.json).

## 2. Herramientas, máquina y escrituras

Lectura de la VM Corpus por SSH verificado desde brain-env; Python y systemd/proc/cgroup como fuentes. Se ejecutó únicamente el lector collect.py y verificadores locales de archivos ya producidos. No se importó PaddleOCR ni se invocó un worker nuevo. El recolector sólo leyó archivos de la VM; guardó la captura en el taller.

GitHub MCP se usó para bitácora/evidencia append-only. ClickUp se actualiza como espejo; Nexus registra lectura y cierre del trabajo propio 22. No se tocaron registros ajenos. No se compró API ni se gastó otra sesión GPU.

Instrumento final: verify_terminal_v2.py, SHA256 `044337ebdbe5c3f01dc7220f112e97dcb33a938868c0951c9ad2188dc1b1dd94`, Python de brain-env y PyYAML 6.0.3 ya instalado. No es el validador del productor: reconstruye el texto desde raw y verifica estado, identidad, configuración, límites y procesos sin importar código OCR.

## 3. Resultado medido

Una página, 2.845 caracteres Unicode, 2.879 bytes UTF-8, 16 bloques (14 con texto y dos imágenes de encabezado sin texto). Documento y página conservan requires_review y fidelity_certified=false.

Tiempos del worker instalado, sin mezclarlos:

- Preparación: 1,4599625749979168 s.
- Carga del modelo: 156,0368849200895 s.
- Calentamiento: 54,03289021097589 s.
- Extracción de la página: 1.635,3817496990087 s, es decir 27 min 15,38 s.
- Pared del worker: 1.851,7276763680857 s.
- Pared del trabajo supervisado: 1.858,9963474780088 s, es decir 30 min 58,996 s.
- CPU acumulada del cgroup: 1.527,581055 s. No es tiempo de pared.

El total del trabajo incluye supervisión y salida del proceso; la suma de las cuatro etapas no incluye todo el overhead del worker. No se presenta ninguna de estas medidas como latencia web.

Límites reales, verificados antes de la admisión: 6 GiB RAM, 3 GiB swap, CPUQuotaPerSecUSec=1s (una CPU lógica), un thread. Timeout del trabajo 7.200 s, servicio 7.500 s y observador 7.560 s.

Picos del cgroup conservados antes de detenerlo:

- RAM: 6.442.450.944 bytes, exactamente 6 GiB y el límite fijado.
- Swap: 3.010.580.480 bytes, aproximadamente 2,80 GiB, por debajo de 3 GiB.
- memory.events: max=105654, oom=0, oom_kill=0, oom_group_kill=0. El contador max no es un OOM ni número de páginas; muestra presión contra el límite.

No fue una corrida holgada: llegó al techo de RAM y usó swap considerable. Que terminó no demuestra que estos recursos sirvan para concurrencia o páginas más difíciles.

## 4. Integridad y comparación acotada

Entrada original y copia del job: 4.443.312 bytes, SHA256 `669c89a75a4e3ad2ecc567f03a13e50c2552265b3baf4e4f547e362acbb9c3c4`. La entrada es la misma primera página pública de Ley 524, no la miniatura de la demo.

Código instalado leído nuevamente y declarado en la salida: SHA256 `ba6319aed537f601745e9d54c1156ce5ee2dd3da500581a94347fc4b64ce5e0f`.

result.json: SHA256 `b8e6b497100ad94efa45182fc65bab08ef687239b469c5dc038bfaae73c402b5`.
raw-0001.json CPU: SHA256 `f6c2890de753ecf6ebc882032e1b5f2e2287e93edd17ca39ed228d297552f3f0`.
Texto CPU: SHA256 `fc072bac865c7951fb687e77a9340696e7c0c2a3575705c79f6534e57b4e0451`.

Se recompuso el texto desde los 16 block_content crudos, en su orden, sin normalizar espacios, saltos o Unicode. Coincide con la página, el documento y su SHA256; también coinciden etiquetas, cajas y referencias de los bloques.

Se leyeron los archivos de la GPU del 31-oct ya conservados, sin ejecutar GPU: predictions.json, timings.json y h01-p001-raw.json. El texto GPU es idéntico byte a byte al CPU. Su raw tiene otro hash, `260943a380eca8a1f01bdf46ce6cd9b24b8744158410e39d0cd217b336b7feae`, lo cual no contradice igualdad del texto: las representaciones crudas y rutas no son el mismo archivo.

Extracción GPU existente: 39,33163505399989 s. Razón observada CPU/GPU: 41,57929736340051. Es una comparación descriptiva de dos corridas con distinta máquina, runtime y calentamiento, no un A/B que aísle causalmente el hardware, ni prueba de repetibilidad. En esta VM y esta página, 27 minutos de extracción no son una respuesta web interactiva rápida.

Las alertas del documento señalan formatos monetarios ambiguos. Coincidir con GPU no certifica que el texto sea correcto; ambos podrían reproducir el mismo error. No se calculó nueva exactitud contra la referencia IA ni se presentó esa referencia como gold humano.

## 5. Limpieza y servicios

El observador guardó final.json antes de salir y registró stop del servicio experimental con exit 0 y ningún PID restante en su cgroup.

En la lectura actual, ambas unidades transitorias propias estaban inactive/dead, MainPID=0 y LoadState=not-found. Es coherente con la recolección normal de unidades transitorias después de su cierre; el Result=success por defecto de una unidad inexistente NO se usa para probar el OCR. La prueba terminal es el estado del job, resultado no vacío, raw y recibo anterior al stop.

La enumeración de procesos encontró el servidor OCR instalado, no procesos del ensayo. Los servicios OCR, API y staging seguían activos, con los mismos PID 738, 727 y 728, NRestarts=0 e inicio del 25-oct-2026 a las 22:52:41 UTC. Esto prueba continuidad observada y ausencia actual de procesos propios, no ausencia absoluta de degradación transitoria o de eventos entre muestras.

El progress.json y partial.json quedaron como registros parciales del productor. No se les exige convertirse en recibos finales ni se los usa para negar un result.json y state.json terminales válidos.

## 6. Verificación falsable y error propio

La captura amplia local validó 27/27 hashes y longitudes. La publicación selecciona ocho archivos completos decisivos, más metadatos de comandos/procesos/hashes. La verificación sobre esa selección produce el mismo resultado terminal, controles y comparación que la captura completa.

Diez casos del verificador: un positivo real y nueve negativos deliberados en copias en memoria. Todos devolvieron lo esperado:

1. Salida real: PASS.
2. Worker exit distinto de cero: rechazado.
3. Hash de entrada incorrecto: rechazado.
4. Un carácter cambiado en raw: rechazado.
5. Cobertura de cero páginas: rechazada.
6. OOM aunque el observador declare completed: rechazado.
7. Proceso propio residual simulado: rechazado.
8. Límite de RAM alterado: rechazado.
9. Certificación de fidelidad inventada: rechazada.
10. Archivo alterado sin actualizar su hash: rechazado.

Además, una mutación de un carácter rompe la comparación exacta CPU/GPU. Estos controles no constituyen nuevas inferencias ni cobertura de todos los fallos posibles.

**Error del primer verificador, no fallo de OCR:** reserializó la configuración desde JSON y calculó otro hash. El YAML original tiene claves enteras 0..24 en layout_merge_bboxes_mode; JSON las vuelve cadenas, y sort_keys cambia el orden numérico por lexicográfico. Se reconstruyó el YAML real, se aplicaron sólo los dos model_dir que aplica el worker y se obtuvo exactamente el sello registrado: `4c838a0db033d971f13c97d856c52b2db2e297f40d75e236a802dbd3a96defd4`. La configuración reconstruida coincide con la serializada. El fallo inicial y el diagnóstico están publicados, sin reescribir la salida ni cambiar el producto.

## 7. Evidencia publicada y repetición desde Git

Archivo: docs/agents/evidencia/2026-11-01-cpu-a415b433-terminal.json, commit `672c94ddca58d27117dcd0e950c0faeb5bdcf745`.

Es un sobre JSON textual, encoding=xz+base64. Tras decodificar base64 y descomprimir XZ, se obtiene un JSON con archivos UTF-8 originales, tamaño y SHA256. No hay modelos ni imágenes codificados.

- Sobre publicado: 20.289 bytes; SHA256 `17c927d2366635b5cdeffff63c3fa2a719bf9d3af4a8f1c44391e92dbe63bf75`.
- Texto decodificado: 110.996 bytes; SHA256 `758121ff997667eb02d3adb81e2f8045c0c6ebd42ca65190edd974c0a27b59cf`.
- Texto comprimido: 15.000 bytes; SHA256 `98af227e4dbb5dfef4b931448871e2befc3c9e525d66bfd12d728f97a7b4135c`.

Contiene terminal-selected-capture.json, verify_terminal_v2.py, selected-verification.json, config-hash-diagnostic.json, initial-verifier-error.json y los tres archivos GPU. La captura seleccionada conserva íntegros baseline.json, final.json, limits.json, request.json, state.json, result.json, raw-0001.json y pipeline.yaml, además de las lecturas systemd/procesos/entrada/kernel.

Se recuperó el archivo por la API de GitHub usando el commit exacto. Coincidió byte a byte con el preparado localmente. Se comprobaron ambos sellos del sobre y los ocho archivos internos. Se extrajo a un directorio nuevo, con control de rutas, y se ejecutó:

```text
python3 /workspace/ocr-cpu-repiloto-20261101-a415b433/replay-git-0612/verify_terminal_v2.py /workspace/ocr-cpu-repiloto-20261101-a415b433/replay-git-0612/terminal-selected-capture.json /workspace/ocr-cpu-repiloto-20261101-a415b433/replay-git-0612/gpu
exit: 0
stderr: vacío
stdout_exactly_equal_original_verification: true
```

stdout completo del replay, también disponible verbatim en selected-verification.json dentro del sobre:

```json
{
  "capture_file_sha256": "96ad28d81c5d240d91b74f9e9b5f1c191dd424ef389b4c70c56661a59cba35db",
  "selected_files_integrity_passed": 8,
  "terminal": {
    "status": "PASS_TERMINAL_REQUIRES_REVIEW",
    "pages": 1,
    "characters": 2845,
    "utf8_bytes": 2879,
    "blocks": 16,
    "nonempty_blocks": 14,
    "text_sha256": "fc072bac865c7951fb687e77a9340696e7c0c2a3575705c79f6534e57b4e0451",
    "timings": {
      "preparation_seconds": 1.4599625749979168,
      "load_seconds": 156.0368849200895,
      "warmup_seconds": 54.03289021097589,
      "extraction_sum_seconds": 1635.3817496990087,
      "worker_wall_seconds": 1851.7276763680857
    },
    "job_wall_seconds": 1858.9963474780088,
    "ocr_completed_utc": "2026-11-01T05:50:31.622804+00:00",
    "job_terminal_utc": "2026-11-01T05:50:38.781743+00:00",
    "observer_terminal_utc": "2026-11-01T05:50:42.364042+00:00",
    "memory_peak_bytes": 6442450944,
    "swap_peak_bytes": 3010580480,
    "oom_events": {
      "low": 0,
      "high": 0,
      "max": 105654,
      "oom": 0,
      "oom_kill": 0,
      "oom_group_kill": 0
    },
    "cpu_usage_seconds": 1527.581055,
    "own_processes_remaining": 0,
    "production_pids_unchanged": [
      "738",
      "727",
      "728"
    ],
    "legal_fidelity": "NOT_MEASURED",
    "reproducibility": "NOT_MEASURED_SINGLE_OCR_RUN"
  },
  "controls": [
    {
      "case": "actual_positive",
      "expected": "PASS",
      "observed": "PASS"
    },
    {
      "case": "nonzero_worker_exit",
      "expected": "worker_terminal",
      "observed": "worker_terminal"
    },
    {
      "case": "wrong_input",
      "expected": "input_identity",
      "observed": "input_identity"
    },
    {
      "case": "altered_raw_text",
      "expected": "raw_text_reconstruction",
      "observed": "raw_text_reconstruction"
    },
    {
      "case": "zero_pages",
      "expected": "page_coverage",
      "observed": "page_coverage"
    },
    {
      "case": "oom_over_completed",
      "expected": "oom_events",
      "observed": "oom_events"
    },
    {
      "case": "residual_process",
      "expected": "no_remaining_own_process",
      "observed": "no_remaining_own_process"
    },
    {
      "case": "wrong_limits",
      "expected": "resource_limits",
      "observed": "resource_limits"
    },
    {
      "case": "false_certification",
      "expected": "review_not_certification",
      "observed": "review_not_certification"
    },
    {
      "case": "broken_file_hash",
      "expected": "file_integrity:state/4eb6c147c31d45b3b57c8a95669e8ac5/result.json",
      "observed": "file_integrity:state/4eb6c147c31d45b3b57c8a95669e8ac5/result.json"
    }
  ],
  "comparison": {
    "existing_gpu_only": true,
    "exact_utf8_equal": true,
    "gpu_text_sha256": "fc072bac865c7951fb687e77a9340696e7c0c2a3575705c79f6534e57b4e0451",
    "gpu_extraction_seconds": 39.33163505399989,
    "observed_extraction_ratio_cpu_over_gpu": 41.57929736340051,
    "comparison_scope": "different machine/runtime/warmup; not causal hardware A/B or web latency",
    "one_character_mutation_is_rejected": true
  }
}
```

Publicación deliberadamente acotada, no captura integral: se excluyen fuente del observador, logs de arranque, observaciones repetidas, partial/progress y manifiesto de modelos. La captura amplia completa de 27 archivos permanece en `/workspace/ocr-cpu-repiloto-20261101-a415b433/capture-061236.json`, 267.016 bytes, SHA256 `5d0df17ba4068c503f8c810b2f740f48e841a954ec8d0bbe1009526282757d9f`. El paquete amplio preparado localmente no se confunde con una publicación remota. Este límite no impide recomputar y contradecir el veredicto terminal con los ocho archivos publicados.

## 8. NO MEDIDO y control de salida

NO MEDIDO: precisión contra gold humano, tres repeticiones nuevas por página, comportamiento ante otros documentos o concurrencia, ausencia de impacto transitorio, costo facturado y causalidad exclusivamente CPU/GPU. No se probó una caída total de VM/disco. No se autoriza despliegue ni reemplazo del OCR actual.

Instrumento -> afirmación -> falsador: worker state/result/raw y checker -> terminó esta página -> exit distinto de cero, texto alterado o cobertura cero dan rojo; cgroup/systemd/proc -> no hay OOM ni procesos propios actuales -> eventos OOM y PID residual simulado dan rojo; comparación de UTF-8 -> mismo texto que GPU existente -> un carácter diferente da rojo. Ninguno prueba fidelidad jurídica.

QA del cierre técnico acotado: 44/45 = 97,8/100. Completitud 14/15 (ocho originales decisivos completos y replay; captura amplia local no publicada íntegra); ejecutabilidad 15/15 (verificador recuperado de Git exit0 y stdout idéntico); documentación 10/10 (alcance, tiempos, hashes, errores, exclusiones y reproducción); proceso 5/5 (positivo y nueve negativos, evidencia cruda separada del veredicto). N/A 55 puntos: producto, seguridad/DevOps de despliegue, arquitectura escalable e innovación no son el objeto de este cierre de lectura. No es una nota de calidad comercial del OCR ni aprobación externa.

Continuidad: actualizar sólo trabajos_vivos.id=22 a terminado_verificado y resultado_leido=1 tras esta lectura. El seguimiento programado de las 04:30 ART ya tiene una condición de no duplicar si el registro y Doc están cerrados; no se elimina ni se modifica el schedule en este turno.

--- METODO TITAN / PROMETEO ---
Accion delicada: NO, lectura del ensayo y bitacora/evidencia append-only
Modo aplicado: FULL
Maquina: brain-env; lectura SSH de VM Corpus
Rubrica: 44/45 -> 97.8/100, cierre tecnico acotado
N/A declarados: 55 puntos de criterios de producto/despliegue
Review externo: NO REALIZADO; mismo operador, sin auditoria independiente
Instrumento: collect.py exit0; verify_terminal_v2.py exit0 en captura completa, seleccion y replay desde Git; stdout completo y fuentes en evidencia enlazada
Artefactos: docs/agents/respuestas/2026-11-01-02-cpu-terminal-verificado-sin-relanzar.md + https://app.clickup.com/90171457413/docs/2kza6fw5-26097
