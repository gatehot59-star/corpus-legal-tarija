# Piloto CPU con límites defendibles

Estado: EN CURSO, no resultado final. Corte observado: 2026-11-01 05:27:53 UTC, 02:27:53 ART.

Doc público en el workspace: [Piloto CPU rehecho](https://app.clickup.com/90171457413/docs/2kza6fw5-26097), ruta Space > Doc. El contenido principal de este recibo está en ese Doc; aquí se agrega evidencia seleccionada verbatim.

## 1. Pedido

«Rehacé el piloto CPU con límites defendibles».

Una nueva ejecución de la primera página pública de Ley 524, con el mismo PNG congelado y el PaddleOCR-VL-1.6 instalado. Cambio de rol declarado: de auditor a ejecutor. No se modificaron el producto, unidades instaladas, PR33 ni el intento fallido del 31 de octubre. No se repitieron GPU/API ni se contrató un servicio.

[Protocolo sellado antes del lanzamiento](https://github.com/gatehot59-star/corpus-legal-tarija/blob/c0c3320add61ebdabdf7e3c25d4eea9e6db23972/docs/agents/evidencia/2026-11-01-cpu-repiloto-a415b433-protocolo.json).

## 2. Herramientas, máquina y alcance de escrituras

GitHub MCP para bitácora y evidencia, gateway build/python en brain-env y SSH verificado por Cloudflare hacia la VM Corpus. Python 3.12.3 del sistema para el observador; runtime OCR ya instalado, sin instalar paquetes ni modificar sus pins. Nexus conserva el trabajo vivo 22, autor brain. ClickUp contiene el Doc espejo.

Escrituras experimentales sólo en `/home/ubuntu/ocr-cpu-repiloto-20261101-a415b433`, unidades transitorias propias y `/workspace/ocr-cpu-repiloto-20261101-a415b433` en el taller. Sin nuevos listeners TCP, credenciales, permisos de producción, merges ni releases. Hay consumo de CPU/RAM/swap de la VM existente; costo facturado NO MEDIDO.

## 3. Contrato y decisiones antes de ejecutar

La medición previa encontró 2 vCPU, 7.183.008 KiB de RAM disponible (6,85 GiB), casi 4 GiB de swap libre y 40,3 GB de disco libre. No había otro worker OCR activo y la cola instalada estaba vacía. PSI no está expuesto por este kernel y no se usó como requisito.

- RAM máxima: 6 GiB. Swap máxima: 3 GiB.
- CPUQuota 100%, presupuesto equivalente a una CPU lógica, con un thread de inferencia y Nice 10.
- Es el perfil efectivamente instalado. Se rechaza repetir el perfil de 5 GiB con OOM documentado. Estar instalado no garantiza completar esta prueba.
- Timeout de trabajo 7.200 s, propio del worker. Límite exterior del servicio 7.500 s; observador 7.560 s.
- Una admisión, una página, cero reintentos. No aumentar recursos durante la corrida para forzar un verde.
- Inicio condicionado a RAM disponible >=6,5 GiB, swap libre >=3,5 GiB y disco libre >=2 GiB.

Arquitectura acotada: PNG congelado -> cliente instalado -> socket privado -> cola nueva -> worker instalado -> raw/partial/result. Un observador fuera del cgroup OCR consulta systemd, cgroup y archivos y escribe su propio final.json. No se crea infraestructura de producto ni se propone escalar esta VM a diez corridas: concurrencia autorizada uno.

El observador tiene 128 MiB, swap cero y CPUQuota 10%. systemd enlaza la vida de la unidad OCR a la del observador. Un finalizador intenta guardar una interrupción si el observador termina sin recibo. No es una garantía frente a pérdida de la VM o del disco.

Guardas, sólo sobre el ensayo: RAM disponible <512 MiB, o <768 MiB durante 30 s; swap libre <512 MiB; disco libre <1 GiB; otro worker OCR o cola instalada activa; pérdida de readiness; cambio de PID/reinicios/inicio/estado de servicios observados. Muestreo aproximado cada 10 s. No son una reserva física ni una prueba de ausencia de impacto transitorio.

## 4. Qué se midió

- 18/18 controles sintéticos en taller y 18/18 en VM. Son los mismos 18 casos en dos entornos, no 36 pruebas independientes.
- Fuente del observador y protocolo iguales byte a byte en taller/VM. Protocolo en Git con objeto de contenido `f3b052397c66dd768be82263fcfc8b3aa7bd71d0`, coincidente con el blob calculado sobre el local.
- systemd confirmó 6.442.450.944 bytes RAM, 3.221.225.472 bytes swap y CPUQuotaPerSecUSec=1s antes de la admisión.
- Trabajo admitido el 1-nov a las 05:19:39 UTC. A las 05:27:53 llevaba 493,45 s observado, en extracción. Superó carga y calentamiento. No es tiempo final de inferencia.
- Pico de RAM observado 6 GiB. En el corte: 5.275.369.472 bytes del cgroup; 2.022.854.656 bytes de RAM disponible del host y 3.183.235.072 bytes de swap libre.
- OCR y observador estuvieron activos en cgroups diferentes. No se relanzó por un error de lectura del canal.

Conclusión derivada: la nueva configuración superó la etapa donde murió el intento anterior. Todavía no prueba terminación, velocidad final, fidelidad ni viabilidad web. El tiempo de GPU de 39,33 s pertenece a la corrida GPU ya recuperada, no a un nuevo A/B causal.

## 5. Evidencia seleccionada verbatim

Esta selección publica la salida íntegra del selftest de la VM, el archivo de límites y el último estado observado. La captura extendida, fuentes y demás logs siguen locales mientras la ejecución está abierta. No se presenta esta selección como publicación completa del experimento.

Comando de selftest: `/usr/bin/python3 /home/ubuntu/ocr-cpu-repiloto-20261101-a415b433/cpu_pilot.py selftest`. Exit 0; stderr vacío. stdout:

```json
{"tests": [{"case": "complete_positive", "expected": "completed", "observed": "completed", "pass": true}, {"case": "running_positive", "expected": null, "observed": null, "pass": true}, {"case": "stale_running_dead", "expected": "service_exit", "observed": "service_exit", "pass": true}, {"case": "oom_over_running", "expected": "oom", "observed": "oom", "pass": true}, {"case": "cgroup_oom_over_reported_timeout", "expected": "oom", "observed": "oom", "pass": true}, {"case": "deadline", "expected": "deadline", "observed": "deadline", "pass": true}, {"case": "empty_text", "expected": [false, "empty_text"], "observed": [false, "empty_text"], "pass": true}, {"case": "text_hash", "expected": [false, "text_hash"], "observed": [false, "text_hash"], "pass": true}, {"case": "page_coverage", "expected": [false, "page_coverage"], "observed": [false, "page_coverage"], "pass": true}, {"case": "input_hash", "expected": [false, "input_hash"], "observed": [false, "input_hash"], "pass": true}, {"case": "assembled_text", "expected": [false, "assembled_text"], "observed": [false, "assembled_text"], "pass": true}, {"case": "nonzero_exit", "expected": "invalid_result", "observed": "invalid_result", "pass": true}, {"case": "guard_positive", "expected": null, "observed": null, "pass": true}, {"case": "low_ram", "expected": "host_ram_emergency", "observed": "host_ram_emergency", "pass": true}, {"case": "sustained_ram", "expected": "host_ram_sustained", "observed": "host_ram_sustained", "pass": true}, {"case": "transient_ram", "expected": null, "observed": null, "pass": true}, {"case": "swap", "expected": "host_swap_reserve", "observed": "host_swap_reserve", "pass": true}, {"case": "other_worker", "expected": "production_ocr_active", "observed": "production_ocr_active", "pass": true}], "passed": 18, "total": 18}
```

`limits.json` íntegro:

```json
{"exit": 0, "stderr": "", "units": {"corpus-ocr-repilot-a415b433.service": {"RuntimeMaxUSec": "2h 5min", "MainPID": "1798591", "Result": "success", "NRestarts": "0", "ExecMainStartTimestamp": "Sun 2026-11-01 05:19:36 UTC", "ExecMainStatus": "0", "ControlGroup": "/system.slice/corpus-ocr-repilot-a415b433.service", "MemoryCurrent": "1121153024", "MemoryPeak": "1123065856", "CPUUsageNSec": "2218542000", "CPUQuotaPerSecUSec": "1s", "MemoryMax": "6442450944", "MemorySwapMax": "3221225472", "Id": "corpus-ocr-repilot-a415b433.service", "LoadState": "loaded", "ActiveState": "active", "SubState": "running"}}}
```

`observer-status.json` del corte íntegro:

```json
{"utc": "2026-11-01T05:27:53.320760+00:00", "elapsed_seconds": 493.45249762304593, "job": "4eb6c147c31d45b3b57c8a95669e8ac5", "observed_job_status": "running", "phase": "extraction", "service": {"RuntimeMaxUSec": "2h 5min", "MainPID": "1798591", "Result": "success", "NRestarts": "0", "ExecMainStartTimestamp": "Sun 2026-11-01 05:19:36 UTC", "ExecMainStatus": "0", "ControlGroup": "/system.slice/corpus-ocr-repilot-a415b433.service", "MemoryCurrent": "5275369472", "MemoryPeak": "6442450944", "CPUUsageNSec": "349320340000", "CPUQuotaPerSecUSec": "1s", "MemoryMax": "6442450944", "MemorySwapMax": "3221225472", "Id": "corpus-ocr-repilot-a415b433.service", "LoadState": "loaded", "ActiveState": "active", "SubState": "running"}, "mem_available": 2022854656, "swap_free": 3183235072}
```

El campo systemd Result=success en un servicio todavía activo no equivale a OCR terminado. Aquí se conserva junto al estado y PID, no se usa como veredicto final.

## 6. Archivos y continuidad

Entrada SHA256: `669c89a75a4e3ad2ecc567f03a13e50c2552265b3baf4e4f547e362acbb9c3c4`.
Código instalado SHA256: `ba6319aed537f601745e9d54c1156ce5ee2dd3da500581a94347fc4b64ce5e0f`.
Observador ejecutado SHA256: `544f4acf0564246cfe34d5bf14b346aa1204df6d56f73fed0e882e9366359f00`.

VM: `/home/ubuntu/ocr-cpu-repiloto-20261101-a415b433`.
Taller: `/workspace/ocr-cpu-repiloto-20261101-a415b433`.
Unidad: `corpus-ocr-repilot-a415b433.service`.
Observador: `corpus-ocr-watch-a415b433.service`.
Trabajo: `4eb6c147c31d45b3b57c8a95669e8ac5`.
Nexus: `trabajos_vivos.id=22`, autor brain. No relanzar.

Fuentes ejecutadas: `cpu_pilot.py`, `collect.py`, `preflight_vm.py`. Capturas: `preflight.json`, `selftest-workshop.json`, `vm-preparation.json`, `observer-launch-receipt.json`, `capture-052353.json`, `capture-052753.json` y lecturas intermedias. En VM: protocolo, lanzamiento, límites, observaciones, estado y carpeta del único job. Inputs/modelos/binarios no se commitean.

Sobre reversible ya preparado localmente: `evidence-selected-inicio.json`, XZ+base64, 101.288 bytes decodificados, SHA256 `da7cc151b71057fbb6d59f3ec5edeac5ecf309697294cf6ea3070bd57e935286`. Contiene la captura seleccionada hasta 05:23:53, no el resultado final. Publicación extendida y lectura terminal PENDIENTES.

## 7. Errores propios y límites

El primer sondeo asumió PSI existente; se corrigió como interfaz opcional. La primera lectura del log del nuevo observador falló por permisos del archivo abierto por systemd. El lanzamiento había sido exitoso: se inspeccionó antes de volver a leer, sin repetirlo. Hubo llamadas de transporte sin ejecución; se verificó que no dejaron captura antes de reintentar lecturas.

NO MEDIDO: resultado final CPU, fidelidad jurídica, repetibilidad de tres ejecuciones, costo facturado y ausencia de impacto transitorio. Una ejecución es exploratoria. El observador y sus pruebas son del mismo operador: no constituyen revisión externa. No se ensayó una caída total de VM/disco.

## 8. Criterio de cierre

Leer final.json contra systemd/cgroup. Si hay salida: una página no vacía, exit 0, hashes de entrada/código/texto, reconstrucción de texto crudo, tiempos separados de preparación/carga/calentamiento/extracción. Si falla: conservar causa y tiempos, sin relanzar. Confirmar que no quedan procesos propios y observar producción sin atribuir ausencia absoluta de impacto. Publicar evidencia final, actualizar Doc y cerrar el registro propio de Nexus sólo después de leer el resultado.

Preparación del instrumento: 42/45 = 93,3/100. Completitud 15 (fuente completa ejecutada), ejecutabilidad 13 (selftests 18/18 en dos entornos; integración entonces pendiente), documentación 9 (contrato y límites; cierre pendiente), proceso 5 (hashes y capturas). N/A 55 puntos de criterios de producto. La nota no aprueba el resultado. Entrega de resultados INCOMPLETA mientras la corrida siga abierta.

--- METODO TITAN / PROMETEO ---
Accion delicada: NO, ensayo aislado autorizado y bitacora append-only
Modo aplicado: FULL
Maquina: brain-env y VM Corpus por SSH
Rubrica: preparacion 42/45 -> 93.3/100; resultado final NO MEDIDO
N/A declarados: 55 puntos, instrumento de diagnostico y no producto desplegado
Review externo: pendiente; no aprobado por silencio
Instrumento: selftest exit 0, 18/18 en taller y VM; systemd/cgroup y captura viva; evidencia seleccionada integra arriba, captura extendida local declarada
Artefactos: este archivo + https://app.clickup.com/90171457413/docs/2kza6fw5-26097
