# ABBYY para Corpus: hay una ruta Linux; REA localizó la serialización y el dato latino, no generó un motor

15 de octubre de 2026. Pedido: «busca donde correr abby o mejor aplica rea a abby y genera el motor ocr para corpus». Operador: BRAIN / GPT-6 Astra.

## Resultado directo

**La ruta más razonable es FineReader Engine para Linux en la VM Ubuntu de Corpus, con el SDK y una licencia de evaluación o runtime adecuada.** No hace falta Windows para ese producto. La máquina es candidata, no una instalación verificada: hay dependencias y requisitos de memoria temporal pendientes.

**También apliqué REA de nuevo** sobre una función de serialización de `endtoendrecognition.dll`, y extraje como datos el archivo `EndToEnd.Printed.Latin.dmd`, de 17.505.527 bytes, del instalador que ya teníamos. La función delega la serialización de la red en `CDnnWrapper`, importado desde `ExtraNeoML.Dnn.dll`. La DLL aislada y el dato latino no constituyen un OCR independiente listo para Corpus.

**No generé un nuevo motor OCR, no reconocí páginas con ABBYY ni modifiqué Corpus.** La reconstrucción funcional, la compatibilidad del dato con otro runtime y su calidad siguen NO MEDIDAS. El resultado útil de este turno es un destino concreto, sus brechas y un mapa binario más preciso, no un clon ficticio.

## Dónde ejecutarlo

| Ruta | Evidencia actual | Qué falta |
|---|---|---|
| FineReader Engine 12 Linux en la VM de Corpus | Ubuntu 24.04.4, x86-64/SSE2, glibc 2.39, compilador C++, unos 6,67 GiB de RAM disponible y 25,258 GiB libres en el filesystem de /tmp; Ubuntu 24.04 está en la lista oficial | Paquete SDK Linux y licencia; revisar libpcre.so.3, swap, tmpfs y dependencias completas; ejecución real |
| ABBYY Cloud OCR SDK | Servicio REST/HTTPS independiente del sistema operativo, documentado por ABBYY | Cuenta/aplicación y credencial autorizadas; condiciones/costo; consentimiento para procesamiento externo. No se subió documento alguno |
| GitHub Actions Windows | GitHub publica runners windows-2022/2025 x64; estándar público: 4 CPU, 16 GB, 14 GB y sin cargo de minutos | Job real no ejecutado; licencia ABBYY y compatibilidad de ejecución desatendida no verificadas; tocar workflow requiere autorización |
| FineReader PDF de escritorio descargado | Distribución Windows x64 ya preservada | No es el SDK Linux. Su CLI necesita usuario conectado; guardar archivos por CLI requiere licencia Extended CLI. No es un backend de servidor listo |

No contrataría una VM Windows antes de resolver el producto y la licencia: tener Windows no resuelve el derecho de uso ni la interfaz de automatización. Wine tampoco es una compatibilidad probada en este ensayo.

### Brechas concretas de la VM Linux

La documentación oficial solicita SSE/SSE2, glibc >=2.17, 2,5 GB para biblioteca y RAM recomendada de 3,5 GB para una página o 4 GB para varias. La VM cumple esos valores medidos al momento de la consulta.

Pero también publica `4 GB + 1 GB × núcleos` para swap y tmpfs: para dos núcleos, 6 GB. La VM tiene aproximadamente 4 GiB de swap. Se midieron `/dev/shm` de 3,886 GiB y `/tmp` en ext4; **no se identificó un tmpfs específico de ABBYY**. Debe revisarse la ubicación/configuración que use el SDK, no asumir que /dev/shm representa toda necesidad temporal.

El resolver de bibliotecas no localizó `libpcre.so.3`. Eso no es un barrido exhaustivo del disco ni demuestra ausencia de una copia privada; sí impide afirmar que la dependencia publicada está resuelta. No se instaló paquete alguno ni se aumentó swap.

### Otros entornos medidos

El mismo probe corrió en brain-env y en el host. brain-env: Debian 13, glibc 2.41, dos CPU, unos 2,60 GiB disponibles; g++ no localizado, libpcre no localizada y /dev/shm de 64 MiB. El host: Huayra 5, glibc 2.28, unos 2,58 GiB disponibles; g++ y libpcre presentes. Host y brain-env comparten máquina física, no son dos reservas independientes de RAM.

En ninguno de los tres entornos se encontró Wine, FineReader, FREngine, QEMU, VirtualBox o virsh en PATH ni las carpetas ABBYY habituales inspeccionadas. **El alcance es PATH y esas rutas, no “no existe Windows en ninguna parte”.** Actions Windows es una opción documentada, no una máquina que se haya medido hoy. No se inspeccionaron credenciales ni cuentas privadas para inventariar licencias.

## Qué hizo REA esta vez

Se leyó el contexto vivo del repo, el informe ABBYY anterior y el inventario de entornos; se re-midieron las capacidades relevantes. Main estaba en `c273c659ee90f2259f540cb14c576d6a16dcfb40`. Se consultaron los cinco PR abiertos de Corpus, sin modificarlos.

Sujeto: `endtoendrecognition.dll`, 161.080 bytes, PE x64, SHA-256 `a68dd7a907f78d2f942a586539f2c5a17336c09fefdf00ef2b3b6dc600185375`.

Función nueva: `E2EUtils::CEndToEndRecognitionNetwork::Serialize`, ordinal 127, dirección `0x1800067b0`, obtenida de la tabla de exportaciones del propio PE. No se volvió a presentar la función anterior `doRecognize` como trabajo nuevo.

Comando ejecutado con el wrapper existente:

```sh
python3 /workspace/abbyy-rea-20261015-80j6swlt/rea_capture.py decompile /workspace/abbyy-rea-20261015-80j6swlt/modules/endtoendrecognition.dll rea-serialize-network-1123 0x1800067b0
```

El wrapper invocó REA/Ghidra con timeout de 350 s, nice 10, heap 1024M y un procesador activo para Java. Inicio 14:31:04 UTC (11:31:04 ART), fin 14:34:13 UTC; **exit 0, 189,068 s, ok:true**. Ghidra 12.1.4. El hash del sujeto y la dirección del resultado coinciden con lo solicitado.

Lectura estática: serializa versión y reconocedor base, obtiene un motor matemático CPU de un hilo bajo una condición del archivo, delega el bloque de red en `CDnnWrapper::Serialize` y ajusta parámetros de lote/salidas. La tabla de importaciones independiente sitúa `CDnnWrapper::Serialize` en **ExtraNeoML.Dnn.dll**, no en la DLL analizada ni como una función autónoma reconstruida.

Esto permite localizar la dependencia. **No demuestra el significado completo de la condición de deserialización, la compatibilidad ABI con otro runtime ni que el OCR pueda ejecutarse en Linux copiando esta DLL.** El pseudocódigo es salida de Ghidra, no código fuente original ni motor compilado.

## El archivo latino existe, pero no está ejecutado

Se extrajeron como datos dos miembros del CAB, sin ejecutar instalador, DLL ni modelo:

| Archivo | Bytes | SHA-256 |
|---|---:|---|
| EndToEnd.Printed.Latin.dmd | 17505527 | `4161d78419a517c03b564f43ad17079cf9fedb94ac7ffbe4c5a027ff82798fe2` |
| endtoendmodelsdescription.bin | 25723 | `c2a60f6961c14d6731387b592bc9412129c933e62bb0ce8862aa3e348cb894e3` |

El inventario también conserva `ocr.zmd` y `Spanish.lm`, pero no se extrajeron en esta corrida. El archivo latino contiene identificadores estáticos de las familias E2EUtils/NeoML; no se deserializó, convirtió a ONNX ni ejecutó. Encontrar un nombre o un archivo de datos no prueba haber recuperado pesos utilizables con un motor propio.

La extracción terminó exit 0 con advertencia de datos al final del CAB. El stdout de 7-Zip informa `Files: 135`; el directorio materializado contiene **exactamente los dos archivos enumerados**, medidos uno a uno. No se convierte el contador del extractor en 135 archivos recuperados. La advertencia se conserva sin declarar falsamente corrupción ni integridad criptográfica del proveedor.

No se publicaron DLL, pesos, instaladores ni pseudocódigo propietario. La ingeniería inversa aporta información de interoperabilidad; por sí sola no concede licencia de redistribución ni convierte el motor comercial en uno propio.

## Qué desbloquea la ejecución real

Para la opción recomendada faltan **el paquete Linux de FineReader Engine y una licencia válida de evaluación/desarrollo/runtime para el uso correspondiente**. La página pública consultada conduce a solicitud de demo, no entregó un SDK Linux directamente. En licencia online, ABBYY documenta Customer Project ID, archivo de token y contraseña. No se pidió al usuario pegarlos en chat ni se buscó una forma de saltarse esa autorización.

Con ese material se puede evaluar una instalación aislada y correr el mismo banco, preservando originales. Primero una página, luego banco completo; la disponibilidad del runtime y la licencia son el bloqueo real antes de esa ejecución. No se promete que el SDK supere Tesseract/Paddle: todavía faltan las transcripciones independientes de los escaneos reales.

Si el objetivo es un OCR de Corpus sin dependencia comercial, la alternativa es una implementación propia con componentes abiertos y pruebas reales, **no rebautizar estas DLL o sus modelos como nuestros**. Ese cambio de alcance se deja a decisión del usuario; no se sustituyó silenciosamente ABBYY por otra cosa.

## Estados e instrumento que puede contradecirlos

- **PASS de diagnóstico:** probe ejecutado en tres entornos, producto Linux oficialmente documentado, nueva descompilación de la dirección exacta y extracción de los dos datos con hashes.
- **BRECHAS:** SDK/licencia no aportados, dependencia pcre sin resolver, requisitos swap/tmpfs pendientes y automatización del FineReader de escritorio no habilitada/verificada.
- **NO MEDIDO:** OCR ABBYY, CER/WER, carga funcional del dato latino, motor reconstruido, superioridad, distribución comercial, Actions Windows en esta cuenta e integración en Corpus.

El probe puede rechazar compatibilidad básica de OS/CPU/memoria, pero no probar que ABBYY arranca. REA puede fallar al descompilar, pero su exit 0 no puede demostrar que se reconoció una página. Extraer el dato puede fallar, pero su hash no prueba utilidad de los pesos. No se emitió un verde de producto.

## Evidencia, incidencias y cierre

[Probe ejecutado](../evidencia/2026-10-15-08-abbyy-probe.py) y [mediciones publicadas](../evidencia/2026-10-15-08-abbyy-runtime.json). El JSON conserva stdout/stderr completos de los probes y extracción, tabla PE relevante y recibo de ejecución REA. El pseudocódigo completo queda local, hash `6a5667792d741b3dd571448d77c86a4e509018aac8db8af33a2a26d3b7c3eefc`; se publica la lista derivada de llamadas, no ese cuerpo. Por tanto la interpretación estática completa requiere el binario autorizado y repetir la descompilación o acceder a la custodia; no se finge publicación íntegra.

Custodia nueva: `/workspace/abbyy-runtime-20261015`; REA y paquete previo: `/workspace/abbyy-rea-20261015-80j6swlt`. SHA-256 del JSON publicado: `d09b2369ec9c94a6e12ac68a24eeb4e3b5b2889b507200b42117cb05d76ff4da`.

Incidencias: una lectura y tres intentos de preparar un lote no llegaron a escribir por timeout de la cola de herramientas; se verificó ausencia antes de repetir. Se ejecutó finalmente **una** función nueva por la vía directa. Su transporte venció mientras el proceso seguía; se recuperó el resultado, sin duplicar la corrida. La segunda función prevista no se ejecutó ni se contabiliza. No se omitió una salida negativa de ABBYY: no hubo reconocimiento ABBYY.

Al cierre, la DLL conserva su hash y no queda proceso identificado de esta corrida. Sin instalación, cuenta, pago, activación, subida de documentos, cambios a producción, workflow o main.

--- METODO TITAN ---
Accion delicada: NO
Modo aplicado: TITAN LIGERO
Rubrica: N/A (diagnóstico acotado, no entrega de un motor)
Review externo: no pedido; mismo operador, no auditoría independiente
Instrumento: probe Python, pefile, 7-Zip y REA/Ghidra; evidencia de ejecución separada de interpretación; binarios no publicados.

## Fuentes oficiales consultadas en vivo

- [ABBYY: requisitos de FineReader Engine Windows/Linux](https://docs.abbyy.com/fine-reader/engine/specifications/system-requirements).
- [ABBYY: SDK y solicitud de demo](https://www.abbyy.com/ocr-sdk/?purpose=trial).
- [ABBYY: instalación Linux](https://docs.abbyy.com/fine-reader/engine/distribution/distribution-linux/installing-the-library-linux/installing-the-library-in-automatic-mode).
- [ABBYY: licencia online y parámetros de inicialización](https://docs.abbyy.com/fine-reader/engine/licensing/online-licensing).
- [ABBYY: CLI de escritorio, usuario conectado y Extended CLI](https://pdf.abbyy.com/how-to/convert-compare-pdfs-with-cli/).
- [ABBYY: Cloud OCR SDK, procesamiento externo en Azure](https://support.abbyy.com/hc/en-us/articles/360013466039-Cloud-OCR-SDK-Specifications).
- [GitHub: runners Windows estándar](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).

No se tomó el marketing de precisión como resultado experimental.
