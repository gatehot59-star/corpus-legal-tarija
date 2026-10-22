# OCR paralelo instalado, todavía no operativo

## 1. Pedido y autorización
Implementar siete tareas y montar el OCR paralelo, sin reemplazar Corpus ni pagar GPU. Confirmación del usuario recibida. No se cerraron tareas ni se hizo merge a main.

## 2. Resultado
FAIL operativo: la carga de PaddleOCR-VL-1.6 superó el límite de memoria de 5 GiB que se configuró para el sidecar. El kernel mató el worker por CONSTRAINT_MEMCG a las 19:09:13 UTC del 22-oct-2026. La extracción real no terminó. El nuevo servicio fue detenido y deshabilitado; Corpus API y Django staging siguen activos.

El límite fue una decisión de esta implementación, no un límite demostrado de la VM. No se concluye que haga falta pagar GPU. Hay que ajustar carga o presupuesto con medición antes de reintentar.

## 3. Cambios persistentes
Rama titan/ocr-vl-sidecar-20261022. Fuente del servicio en d8040a4915bc1cfcd2e5584f3a701b67bfdc5287; tests adicionales y E2E en eec11c7ddba34b6abfc705f3ee8ee84634b00f57.

Archivos: sistema/ocr_sidecar/ocr_service.py, ocr_client.py, test_ocr_service.py, test_worker_contract.py, e2e_private.py, corpus-ocr-vl.service.

VM: /opt/corpus-ocr-vl/app y runtime, root-owned sin escritura para ubuntu. Se copió el runtime experimental, se eliminó de la COPIA la dependencia heredada por .pth a /tmp copiando sus paquetes, y se verificaron los imports desde /opt. Pillow 13.0.0 sólo en el runtime nuevo. Unidad instalada en /etc/systemd/system/corpus-ocr-vl.service, ahora disabled. Sin modificación de Django, API, nginx ni bases.

## 4. Evidencia y límites
PASS local: 46 tests. trace estándar de Python: 86% de 608 líneas del servicio. Los contratos de worker usan un modelo doble explícito; no son exactitud OCR. PASS VM previo: 43 tests, pins/hashes, imports, pip check y systemd-analyze verify. Socket real 0600, directorio 0700; otro UID no pudo conectar. Sin listener TCP nuevo.

FAIL real: E2E admitió escaneado 2 páginas, híbrido 2 páginas y PDF sobre el límite. Primer worker murió cargando pesos; los tres trabajos quedaron interrupted tras reinicio. No hubo resultados completos. Logs indican modelo y pesos reales; ese hecho solo no prueba inferencia terminada.

Kernel: anon-rss 5221388 kB, file-rss 197800 kB, proceso 2248848. Evidencia cruda de diagnóstico filtrada y del safe-stop en archivo adjunto de evidencia. El archivo es un extracto explícito, no el log completo. Logs completos locales: /workspace/corpus-ocr-deploy-20261022/preflight.json, activation.log, socket-check.log, first-e2e-journal.log, restart-diagnosis.log, safe-stop.json. No se afirma que todos estén publicados en Git.

SHA256 service: ba6319aed537f601745e9d54c1156ce5ee2dd3da500581a94347fc4b64ce5e0f. Test principal: 13533ac84d32d0d49b63c2b258d554f80df15797246c33da6620f23b87a75cb7. Ambos iguales entre sandbox y fuente Git recuperada. Los archivos se transfirieron por SSH desde esa fuente.

Seguridad: OSV consultado para paquetes principales; Pillow actualizado tras avisos. NO se certificó ausencia de vulnerabilidades en toda la clausura transitiva. Revisor a4 no halló bloqueante para E2E privado bajo runtime readonly; eso no es aprobación de producción. Quedan deudas de configuración efectiva en sello, inventario de archivos adicionales y procesos del mismo UID.

## 5. Siguiente ejecución, sin repetir lo completado
Conservar fallos y originales. Leer /tmp/corpus-ocr-e2e-20261022/runner.log, submitted.json y los trabajos de /var/lib/corpus-ocr. Medir opciones de carga eficiente en los paquetes instalados y presupuesto disponible; no inferir imposibilidad por el límite elegido. Ajustar sólo el sidecar, probar y reactivar para E2E. Exigir documentos completos y controles negativos antes de declarar montado. Corpus original debe permanecer activo. Completar runbook, evidencia cruda y criterios de las siete tareas. No ampliar a MinerU/Surya, no hacer merge ni comprar GPU.

## 6. Entrega y QA
[Doc espejo](https://app.clickup.com/90171457413/docs/2kza6fw5-24237). El Doc amplía este recibo; no es un informe de éxito. QA operativo NO APROBADO por gate E2E fallido. No emitir score global verde usando cobertura como sustituto del producto.

--- METODO PROMETEO ---
Accion delicada: SI
Modo aplicado: FULL
Maquina: sandbox + brain-env + VM
Rubrica: NO APROBADO; extracción real incompleta
Review externo: a4, condiciones y deuda
Instrumento: unittest, trace, hashes, systemd, dmesg; alcance exacto arriba
Artefactos: docs/agents/respuestas/2026-10-22-03-ocr-sidecar-bloqueo-memoria.md + https://app.clickup.com/90171457413/docs/2kza6fw5-24237
