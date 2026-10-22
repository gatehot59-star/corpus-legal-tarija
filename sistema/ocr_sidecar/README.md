# Corpus OCR: servicio paralelo privado

No reemplaza Corpus, no modifica bases, no reindexa y no abre puerto TCP. Estado de aceptación: consultar el último recibo de E2E, no inferirlo de systemctl active. Todos los resultados son `requires_review` y `fidelity_certified:false`.

## Ejecución instalada

VM, usuario ubuntu autorizado por SO_PEERCRED y permisos Unix. Python `/opt/corpus-ocr-vl/runtime/venv/bin/python`, cliente `/opt/corpus-ocr-vl/app/ocr_client.py`, socket `/run/corpus-ocr/ocr.sock`. Desde SSH autorizado:

```sh
/opt/corpus-ocr-vl/runtime/venv/bin/python /opt/corpus-ocr-vl/app/ocr_client.py --ready
/opt/corpus-ocr-vl/runtime/venv/bin/python /opt/corpus-ocr-vl/app/ocr_client.py --input documento.pdf --mode auto
/opt/corpus-ocr-vl/runtime/venv/bin/python /opt/corpus-ocr-vl/app/ocr_client.py --job IDENTIFICADOR_DEVUELTO
```

`--wait 7200` espera al resultado; sin wait devuelve la admisión. Admitido no significa completado. `/ready` acredita lanzamiento, no modelo residente. CPU, un trabajo por vez, cuatro pendientes. Máximos: 20 MiB, cuatro páginas, 24 megapíxeles por imagen, 7200 segundos por trabajo, 64 directorios. Los terminales vencidos se limpian al admitir otro trabajo luego de 24 h. Copiar resultados necesarios antes de esa retención.

Modos: `ocr` fuerza imágenes; `txt` exige capa nativa utilizable en cada página; `auto` decide página por página mediante heurística, no mediante certificación. Se conserva texto nativo cuando se lee y salida OCR en bloques; tablas conservan su markup. Consumidores deben tratar contenido como no confiable y escaparlo antes de renderizar HTML. No se evalúa JavaScript del documento.

## Runtime

PaddleOCR3.7.0, PaddleX3.7.2, Paddle3.3.1, Pillow13.0.0. Modelo VL revisión c5630abae1d940eafe0697512a0325494b02ab42 y layout 241f8bdfc77a7c7bee915a5057aaee58c235a8d3. Hashes completos en runtime/models.json, verificados por job. Los archivos de /opt son root-owned. No editar en caliente. No depender de /tmp: se verificó importación desde el nuevo venv.

`memory.conf` es un drop-in de systemd. Límite 6 GiB RAM y 3 GiB swap dentro de una VM de aproximadamente 7.77 GiB RAM y 4 GiB swap. No es una promesa de throughput ni un permiso para aumentar la concurrencia. CPUQuota100%, nice10. El intento inicial de5GiB falló con OOM; aumentar solamente swap no resolvió la carga. `low_cpu_mem_usage=True` falló con KeyError de gate_proj en esta combinación de versiones: queda desactivado explícitamente mediante CORPUS_OCR_LOW_MEMORY=0. No promoverlo por pasar el test de forwarding.

## Operación y rollback

La unidad es `corpus-ocr-vl.service`. Para retirar sólo el sidecar, un operador autorizado puede detener/deshabilitar esa unidad. Corpus conserva su API, Django staging, Tesseract, índices y bases. No borrar runtime, fuentes o evidencia como parte de un rollback. Para reanudar, verificar primero modelos/pins y la memoria disponible, luego iniciar sólo esa unidad. Es una operación administrativa, no una ruta de la API.

## Verificación

```sh
python -m unittest -v test_ocr_service test_worker_contract test_low_memory
python ocr_service.py verify --runtime /opt/corpus-ocr-vl/runtime
python e2e_private.py --root DIRECTORIO_NUEVO
```

La última orden crea dos PDF sintéticos y un control de cinco páginas, los envía al servicio REAL y verifica orden, método, negación y monto. No es un gold humano, no mide CER/WER ni exactitud general. El fixture de Ley151 detecta el error conocido mediante fragmentos; no corrige automáticamente ningún texto productivo. Reproducibilidad requiere un protocolo separado con tres lecturas nuevas por página.

## Licencias y comparadores

Paddle código/pesos Apache2 según auditoría22-oct. Separar siempre licencia de motor, pesos y dependencias; esta entrega no concede elegibilidad comercial de terceros. No se instaló MinerU ni Surya. No se sostiene la afirmación de menor error por combinar tres motores sin banco pareado. El ejemplo correcto de motor es `PaddleOCRVL(pipeline_version='v1.6', ...)`, no PaddleOCR general. La implementación serializa cada página y cada bloque, no resultado[0] de un documento completo.

Referencias de cifras y licencias: docs/auditorias/2026-10-22-02-propuesta-ocr-implementacion.md en la rama de auditoría, commit b9a7d4154bd5d6ea69a746834bb9a2db8536f316. Paddle96.34 corresponde a tabla OmniDocBench v1.6_full observada22-oct, no a precisión de Corpus; paper96.33 discrepante. No es #1 en esa tabla. Los84idiomas MinerU y92.56 del Paddle base no fueron revalidados. GLM códigoApache/modeloMIT; Surya y MinerU requieren leer condiciones específicas. No inferir licencias uniformes de sus metadatos.

## Deudas conocidas

El supervisor actual etiqueta cualquier salida SIGKILL(-9) como timeout, aunque pueda provenir de OOM. Consultar dmesg/cgroup para distinguirlos; no interpretar ese rótulo como evidencia de7200segundos vencidos. El directorio de estado comparte confianza con procesos del mismo UID. El sello verifica modelos/configuración de admisión, no toda la clausura del runtime. Código y paquetes de sólo lectura son parte del requisito de despliegue. No se certifica cero vulnerabilidades transitivas.
