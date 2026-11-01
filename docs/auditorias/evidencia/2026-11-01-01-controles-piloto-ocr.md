# Evidencia decisiva y controles del piloto OCR

Esta es una selección explícita, no el paquete ampliado completo. No se truncan las piezas pequeñas incluidas abajo. Se excluyen del presente archivo: las fuentes completas del runner y del primer verificador, el JSON OCR completo, logs de instalación y el bloque ampliado del kernel. Se conservaron en la captura de 179.702 bytes, SHA256 5227f193d7d4cf29b4f59a046123e5448ef58fb6030ebe6822ac151ff10034ac, todavía sin publicar íntegramente en Git. No se presenta esta selección como sustituto de esa publicación pendiente.

Fuentes persistentes: [kernel Kaggle nuevo, versión 1](https://www.kaggle.com/code/abrahammendieta/corpus-ocr-piloto-20261031-1805), [servicio instalado, bytes verificados](https://github.com/gatehot59-star/corpus-legal-tarija/blob/5a108c028792b409974b00ebe04be5e1215f9029/sistema/ocr_sidecar/ocr_service.py), [README y antecedente de OOM](https://github.com/gatehot59-star/corpus-legal-tarija/blob/5a108c028792b409974b00ebe04be5e1215f9029/sistema/ocr_sidecar/README.md).

## 1. CPU: estado del sistema frente al JSON

Bloque completo del servicio piloto obtenido por systemctl show. La consulta original también incluyó los tres servicios instalados; aquí se selecciona el bloque del piloto, no toda la salida de aquella consulta.

```text
RuntimeMaxUSec=45min
MainPID=0
Result=oom-kill
NRestarts=0
ExecMainStartTimestamp=Sat 2026-10-31 18:06:32 UTC
ExecMainExitTimestamp=Sat 2026-10-31 18:08:55 UTC
ExecMainCode=2
ExecMainStatus=15
MemoryPeak=18198528
CPUUsageNSec=57552822000
CPUQuotaPerSecUSec=500ms
MemoryMax=5368709120
MemorySwapMax=1073741824
Id=corpus-ocr-pilot-41fe1113.service
LoadState=loaded
ActiveState=failed
SubState=failed
ActiveEnterTimestamp=Sat 2026-10-31 18:06:32 UTC
InactiveEnterTimestamp=Sat 2026-10-31 18:08:56 UTC
```

Exit de la consulta: 0; stderr vacío. No se usa MemoryPeak=18198528 para estimar el pico del worker: ese dato no describe el proceso muerto. El evento del kernel es el testigo pertinente.

Archivos del trabajo:

```json
{"status":"running","updated_utc":"2026-10-31T18:07:53.601192+00:00"}
```

```json
{"phase":"loading","expected_pages":1,"completed_pages":0}
```

La serialización de esos dos objetos fue compactada para lectura; sus archivos originales tienen SHA256 570d6c0c8d27182f7a5ecc528bfe544f5edbd38f3218a080e800dbd6b755bb5e y 33db59f930a162fa2434bf44933f197d7fa7a92135b71c936c71c31c15a849b0. No hubo result.json en el inventario del trabajo. No se encontró proceso del piloto; sí se encontró el servidor instalado, PID738, como control positivo de presencia.

Fragmento seleccionado por contenido de dmesg --ctime, exit0, stderr vacío. No es el dmesg entero:

```text
[Sat Oct 31 18:08:48 2026] python invoked oom-killer: gfp_mask=0x100cca(GFP_HIGHUSER_MOVABLE), order=0, oom_score_adj=0
[Sat Oct 31 18:08:48 2026] Memory cgroup stats for /system.slice/corpus-ocr-pilot-41fe1113.service:
[Sat Oct 31 18:08:48 2026] [1664401]  2000 1664401    46226     2893      129     2764         0   126976     3808             0 python
[Sat Oct 31 18:08:48 2026] oom-kill:constraint=CONSTRAINT_MEMCG,nodemask=(null),cpuset=corpus-ocr-pilot-41fe1113.service,mems_allowed=0,oom_memcg=/system.slice/corpus-ocr-pilot-41fe1113.service,task_memcg=/system.slice/corpus-ocr-pilot-41fe1113.service,task=python,pid=1664946,uid=2000
[Sat Oct 31 18:08:48 2026] Memory cgroup out of memory: Killed process 1664946 (python) total-vm:7668344kB, anon-rss:5219900kB, file-rss:18564kB, shmem-rss:0kB, UID:2000 pgtables:13584kB oom_score_adj:0
```

Una segunda captura seleccionó TODAS las114líneas del segundo18:08:48, sin filtro por palabras. Dos líneas de ese bloque:

```text
[Sat Oct 31 18:08:48 2026] memory: usage 5242880kB, limit 5242880kB, failcnt 13559
[Sat Oct 31 18:08:48 2026] swap: usage 1048576kB, limit 1048576kB, failcnt 878719
```

El journal no tenía archivos; no se interpreta su salida vacía como ausencia de OOM.

Antecedente exacto del README, línea23:

> `memory.conf` es un drop-in de systemd. Límite 6 GiB RAM y 3 GiB swap dentro de una VM de aproximadamente 7.77 GiB RAM y 4 GiB swap. No es una promesa de throughput ni un permiso para aumentar la concurrencia. CPUQuota100%, nice10. El intento inicial de5GiB falló con OOM; aumentar solamente swap no resolvió la carga. `low_cpu_mem_usage=True` falló con KeyError de gate_proj en esta combinación de versiones: queda desactivado explícitamente mediante CORPUS_OCR_LOW_MEMORY=0. No promoverlo por pasar el test de forwarding.

## 2. Muestra y reencodificación

Entrada original CPU/GPU: 4.443.312 bytes, 2520x3888 RGB, SHA256 669c89a75a4e3ad2ecc567f03a13e50c2552265b3baf4e4f547e362acbb9c3c4.

PNG interno CPU: 4.791.899 bytes, SHA256 9529d770216bf90bcf7ad6e23769c1069f54291d357941736f178cdde161a331. Igual tamaño, modo y SHA256 de bytes RGB en ambos: 7e71fb47a5464b0ad49ecd5d6f6f2b867e36492b8524b2a37887216e00d5a870. La lectura adicional de ambos archivos finalizó exit0 el1-nov04:21:28UTC. Se cerraron explícitamente las imágenes convertidas.

## 3. GPU: archivos pequeños completos

Contenido de timings.json:

```json
[
  {
    "id": "h01-p001",
    "seconds": 39.33163505399989,
    "characters": 2845,
    "blocks": 16,
    "raw_sha256": "260943a380eca8a1f01bdf46ce6cd9b24b8744158410e39d0cd217b336b7feae",
    "rss_peak_kib": 3449464
  }
]
```

Contenido de loaded.json:

```json
{
  "loaded_utc": "2026-10-31T18:22:19.124301+00:00",
  "load_seconds": 5.815086786999927,
  "parameter_places": [
    "Place(gpu:0)"
  ]
}
```

Contenido de status.json:

```json
{
  "phase": "completed",
  "completed_utc": "2026-10-31T18:23:01.016351+00:00",
  "completed_pages": 1,
  "metrics_pending_external_scoring": true
}
```

Contenido de inference-receipt.json:

```json
{
  "command": [
    "/tmp/corpus-vl16-env/bin/python",
    "-u",
    "/tmp/corpus-vl16-runner.py"
  ],
  "started_utc": "2026-10-31T18:22:03.872457+00:00",
  "timeout_seconds": 9600,
  "exit": 0,
  "seconds": 60.0567167050001,
  "ended_utc": "2026-10-31T18:23:03.929189+00:00"
}
```

Contenido de bootstrap-started.json:

```json
{
  "started_utc": "2026-10-31T18:15:29.108097+00:00",
  "python": "3.13.15 (main, Aug  6 2026, 11:06:22) [GCC 13.3.0]",
  "reference_text_uploaded": false
}
```

Contenido de bootstrap-completed.json:

```json
{"utc": "2026-10-31T18:23:03.929568+00:00", "metrics_pending_external_scoring": true}
```

Timestamp del recibo de push:2026-10-31T18:06:02.418654+00:00. Diferencia hasta bootstrap completo:1021.510914s. Diferencia hasta inicio del bootstrap:566.689443s. Bootstrap:454.821471s. No se presenta ninguna como latencia de una web o cola pura: hay relojes distintos y etapas de preparación.

La fuente descargada de Kaggle coincidió byte a byte con la enviada: SHA25645e21541e97a7e4ca0103f7f35bf7bd2e815bea33ff7fa03402c78a04ac1aff9. El log incluye el sello del runner cb225c31f9883cd18829633d7fcf210372db7a3d207592b3f11c789a0c6b7521 y RUN_COMPLETED. El crudo leído fue de21.401bytes. Su igualdad con el crudo histórico no prueba por sí misma contaminación ni exactitud.

## 4. API: fallos reales, sin inventar causa

Primera solicitud: inicio2026-10-31T18:05:16.155442+00:00, final18:06:25.098747UTC, total68.94324391300324s. Upload/submit/event HTTP200. El cuerpo SSE contiene cuatro heartbeats y termina con event:error/data:null. HTTP200 fue transporte, no éxito OCR.

Segundo intento: inicio2026-10-31T18:07:29.672116+00:00, final18:07:34.576394UTC, total4.904236527974717s. También termina en error sin salida OCR. Ambos recibos registraron not_completed. La causa upstream queda NO MEDIDA.

Fuente del detector: external_run.py, SHA256 e7edf884ac0d26a991bd086cbf0b29f51831cbeaea647cf39e664e23613bd47c. Expresión exacta extraída del AST y evaluada por el primer verificador:

```python
'completed' if 'event: complete' in r.text else 'not_completed'
```

La [fuente pública de la demo](https://huggingface.co/spaces/PaddlePaddle/PaddleOCR-VL-1.6_Online_Demo/blob/main/app.py) se recuperó además en revisión78b275c880a6bf69cbc48f5484e0ee37da57c717, SHA256 c74737c28ea97b674e5007ddcc29ff82c798cb6cf0ac2517f9a2045eba1764c5. El contrato observado devuelve Markdown, HTML y texto crudo; una finalización de transporte sin texto no satisface la salida OCR buscada.

## 5. Control reducido ejecutado, no arreglo de producto

Guardar el siguiente bloque como public_controls.py y ejecutar python3 public_controls.py. No usa red, GPU ni Paddle.

```python
#!/usr/bin/env python3
"""Audit-only controls. No network, OCR, services, credentials or product writes.
Before execution: valid OCR completion must pass; error/null/empty must fail.
The candidate expression is copied verbatim from external_run.py, SHA256
 e7edf884ac0d26a991bd086cbf0b29f51831cbeaea647cf39e664e23613bd47c.
This reduced test does not claim to rerun Paddle or validate every Gradio shape.
"""
import json, types

def candidate(payload):
    r = types.SimpleNamespace(text=payload)
    return 'completed' if 'event: complete' in r.text else 'not_completed'

def require_live(state, service):
    assert state['status']=='running' and service['ActiveState']=='active' and service['MainPID']!='0', 'JSON running does not prove live execution'

def main():
    cases = [
      ('positive_text', 'event: complete\ndata: ["Texto OCR de control", "<p>Texto OCR de control</p>", "Texto OCR de control"]\n\n', 'completed'),
      ('negative_error', 'event: error\ndata: null\n\n', 'not_completed'),
      ('null_output', 'event: complete\ndata: [null, null, null]\n\n', 'not_completed'),
      ('empty_output', 'event: complete\ndata: ["(Empty result)", "<p>No visualization available.</p>", ""]\n\n', 'not_completed')]
    rows = []
    for name, payload, expected in cases:
        observed=candidate(payload)
        rows.append({'case':name, 'input':payload, 'expected':expected, 'observed':observed, 'passes_ocr_success_contract':observed==expected})
    assert rows[0]['passes_ocr_success_contract'] and rows[1]['passes_ocr_success_contract']
    state={'status':'running'}
    positive={'ActiveState':'active','MainPID':'123'}
    mutant={'ActiveState':'failed','MainPID':'0'}
    require_live(state, positive)
    try:
        require_live(state, mutant)
    except AssertionError as err:
        state_control={'positive_passed':True,'mutant_rejected':True,'assertion':str(err)}
    else:
        raise AssertionError('state guard cannot reject a dead service')
    print(json.dumps({'external_cases':rows,'external_contract_violations':sum(not r['passes_ocr_success_contract'] for r in rows),'state_guard':state_control,'scope':'local synthetic controls; no live OCR'},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
```

Dos ejecuciones en carpetas temporales distintas, 2026-11-01T04:33:17.091455+00:00 y04:33:17.150349+00:00: exit0, stderr vacío, stdout idéntico. Salida completa común:

```json
{
  "external_cases": [
    {
      "case": "positive_text",
      "input": "event: complete\ndata: [\"Texto OCR de control\", \"<p>Texto OCR de control</p>\", \"Texto OCR de control\"]\n\n",
      "expected": "completed",
      "observed": "completed",
      "passes_ocr_success_contract": true
    },
    {
      "case": "negative_error",
      "input": "event: error\ndata: null\n\n",
      "expected": "not_completed",
      "observed": "not_completed",
      "passes_ocr_success_contract": true
    },
    {
      "case": "null_output",
      "input": "event: complete\ndata: [null, null, null]\n\n",
      "expected": "not_completed",
      "observed": "completed",
      "passes_ocr_success_contract": false
    },
    {
      "case": "empty_output",
      "input": "event: complete\ndata: [\"(Empty result)\", \"<p>No visualization available.</p>\", \"\"]\n\n",
      "expected": "not_completed",
      "observed": "completed",
      "passes_ocr_success_contract": false
    }
  ],
  "external_contract_violations": 2,
  "state_guard": {
    "positive_passed": true,
    "mutant_rejected": true,
    "assertion": "JSON running does not prove live execution"
  },
  "scope": "local synthetic controls; no live OCR"
}
```

Exit0 significa que el explorador de auditoría terminó y publicó los casos. No significa que el detector haya satisfecho el contrato: los dos false lo refutan. El fallo fue reproducido en respuestas sintéticas, no observado como falso éxito del proveedor.

## 6. Límites del expediente

La selección sirve para comprobar OOM, presupuesto, estado inconsistente, tiempos declarados por la corrida nueva y el falso éxito del detector. No reproduce aquí la inferencia completa ni certifica el texto legal. El informe distingue esa validación local de la publicación ampliada todavía pendiente. No se tocaron producción, trabajos previos ni servicios para facilitar los controles.
