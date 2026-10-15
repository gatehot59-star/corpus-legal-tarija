# REA sí analizó una biblioteca OCR real de ABBYY; precisión e integración siguen sin medir

Fecha: 2026-10-15. Operador: BRAIN, GPT-6 Astra. Pedido: «hazlo», después de proponer analizar el ejecutable de ABBYY FineReader con REA/Ghidra sin su código fuente.

## Resultado

**Se descargó la distribución oficial, se extrajeron componentes sin instalar y REA/Ghidra descompiló una función interna de reconocimiento de una DLL nativa x64.** No se analizó sólo el instalador. La función examinada prepara entradas y llama a la red de NeoML. Esto es un resultado de ingeniería inversa acotado, **no** un OCR reconstruido ni una demostración de que ABBYY sea el mejor para Corpus.

No se ejecutó el instalador ni las DLL de ABBYY, no se activó una prueba, no se aceptaron condiciones mediante formularios, no se ingresaron credenciales, no se eludieron licencias y no se modificó Corpus.

## Origen y sujeto exacto

La [página oficial de prueba](https://pdf.abbyy.com/finereader-pdf/trial/) devolvió un enlace directo a `downloads.abbyy.com`. No hizo falta enviar el formulario que describe la página de soporte. Se usó el enlace presente en el HTML recibido, no un espejo ni una URL adivinada. El parámetro temporal de la descarga no se publica aquí.

Distribución: `ABBYY_FineReader_PDF_Trial_Corporate_x64_16.26.6.6004.exe`.

| Sujeto | Bytes | SHA-256 |
|---|---:|---|
| Distribución oficial completa | 1887164688 | 2cbc106e0495cff540950b269f6f3f633157349665e0d72a4cebd512e2550534 |
| MSI, extraído como datos | 37957632 | 50370c3f28fc3f26653f2031195ccee011d1739989df625a6fe27773ccc02809 |
| Bin.cab | 1486771330 | 82871b14faeb71ff720021169d81d9a1a6751605379e14e9584d56722b7b5a57 |
| FR.cab | 966817841 | 6572d4db6ff6719d4940883be52816842f53e3e49c107a9ec62e7998c14798b4 |
| Recognizer.dll | 644408 | 4bd41420ed52bddba3211f6b380d5c964655a03eba2094270bd5b16d8f9a48cb |
| endtoendrecognition.dll | 161080 | a68dd7a907f78d2f942a586539f2c5a17336c09fefdf00ef2b3b6dc600185375 |

El ejecutable exterior es un autoextraíble RAR con envoltorio PE32, no el motor OCR x64. El archivo RAR es sólido. Se leyó su índice por rangos verificando CRC de cabeceras: 180 registros, incluyendo cabeceras y directorios, no 180 componentes OCR. Se obtuvieron 1.618.982 bytes por rangos para ese índice.

La descarga completa, con cuatro conexiones y verificación de continuidad de segmentos, terminó sin errores en 454,858 segundos, antes del límite fijado de 600. Se calculó el SHA-256 del archivo completo. La extracción de los tres contenedores seleccionados terminó con exit 0 y tamaños coincidentes con el índice.

Los hashes son mediciones propias, no una comparación contra hashes publicados por ABBYY. El paquete contiene certificados PKCS#7, entre ellos uno con sujeto ABBYY Development, Inc. **No se verificó la firma Authenticode, la cadena de confianza ni su sello de tiempo.** La fecha de vencimiento de un certificado por sí sola no se usa aquí para aceptar o rechazar una firma histórica.

## Máquinas y herramientas realmente usadas

- brain-env, alcanzado por MUDH Gateway `build`: Linux x86-64, 2 CPU reportadas por Python, 83,48 GiB libres al inicio y 2.569.384 kB de memoria disponible. Se usaron requests, lector PE `pefile 2024.8.26`, 7-Zip 26.04, REA 6.4.0 y Ghidra 12.1.4 con JDK 21.
- El sandbox de ClickUp se midió aparte: 4 CPU, 20,12 GiB libres, 7-Zip disponible y sin acceso a internet. No se lo confundió con brain-env y no se usó para ejecutar ABBYY.
- 7-Zip se descargó desde el enlace de la [página oficial](https://www.7-zip.org/download.html) a la publicación `ip7z/7zip` 26.04. SHA-256 del tar: `fc0327ba27e89bd086cf426dff17d77de582953cdbbc10a6576540a06853ffcd`.
- Herramientas auxiliares en una carpeta aislada; no se reemplazaron paquetes del sistema ni la instalación de REA.
- REA usó HOME separado, proveedor Ghidra explícito, snapshot propio, heap headless de 1024M, un procesador activo para Java y prioridad reducida. Cada comando tuvo un límite de 350 segundos, con terminación diferida de 8 segundos.
- No se arrancaron Actions, Kaggle, Windows, Wine ni máquinas de Abacus. La ausencia medida de Wine en brain-env y el sandbox no se convierte en una afirmación sobre todas las máquinas posibles.

## PASS: identificación y análisis estático

### Recognizer.dll

El recurso de versión declara `OCR/ICR Components Manager`, producto `ABBYY OCR Technology`, versión `16.3.1353.0`, arquitectura PE x64. El paquete comercial y esta biblioteca tienen versiones distintas; no se confunden.

Se inventariaron importaciones de `FineObj.dll`, `LangInfoUnicode.dll`, `NeoML.dll`, `FineFormats.dll`, `AbbyyZlib.dll` y bibliotecas Windows. La exportación `__FineObjUsed` por sí sola no se interpretó como una API de OCR independiente. Esta DLL tuvo inventario PE, **no** descompilación completa.

### endtoendrecognition.dll

El recurso declara `E2ERec`, versión `16.3.1353.0 (private)`, PE x64. `private` es texto del recurso de compilación, no una cuenta privada accedida. Su tabla PE contiene 175 exportaciones, incluyendo métodos con nombres C++ de reconocimiento, vocabulario y conversión a texto. El inventario independiente identificó dependencias de `NeoML.dll`, `NeoMathEngine.dll`, `ExtraNeoML.Dnn.dll` y `FineObj.dll`.

REA inspect terminó con exit 0, `ok:true`, y el SHA-256 del sujeto coincide con el del archivo extraído. Ghidra inventarió **533 procedimientos y 469 cadenas**. Son elementos detectados, no 533 funciones comprendidas o validadas.

- Inicio: `2026-10-15T05:12:04.183549+00:00`.
- Fin: `2026-10-15T05:13:24.462474+00:00`.
- Tiempo del wrapper: 80,278 s.
- Evidencia: `ev_3c23f2003db93bffdee78ca872bc8ddccf3e67f7f42d5886fda14c750af4cee9`.

### Función de reconocimiento realmente descompilada

Se seleccionó una dirección derivada de la exportación PE del propio archivo, no el punto de entrada del instalador:

`E2EUtils::CEndToEndRecognitionNetwork::doRecognize`, dirección `0x180006890`, ordinal 157.

REA decompile terminó con exit 0 y `ok:true`; Ghidra devolvió pseudocódigo con cuerpo analizable. El resultado permite observar esta secuencia estática: comprobar la validez del wrapper neuronal, preparar los blobs de entrada, rellenarlos, obtener la red y llamar a `NeoML::CDnn::RunOnce`.

No se publica el cuerpo íntegro del pseudocódigo propietario. Se conserva la salida completa localmente con su hash. El pseudocódigo es una reconstrucción de Ghidra, **no** el fuente original y **no** una prueba de ejecución o exactitud semántica completa.

- Inicio: `2026-10-15T05:14:00.166081+00:00`.
- Fin: `2026-10-15T05:15:05.656901+00:00`.
- Tiempo del wrapper: 65,490 s.
- Evidencia: `ev_63171ad8b013b9d8a853fc4f032c5f6f0b1ab56854ceceec3c4339dd690797ad`.

La llamada de transporte venció antes de devolver el resultado, pero la ejecución se recuperó del registro ya escrito, **sin relanzarla**. Sus stdout y stderr completos se conservaron antes de resumir.

## Qué aporta para Corpus

El paquete separa ejecutables, bibliotecas y datos. El índice de Bin.cab contiene, entre otros, `ocr.zmd` (183.028.211 bytes), `Spanish.lm` (64.340.808 bytes) y archivos para análisis de tablas, columnas y tipos de contenido. **Nombre y tamaño no equivalen a haber recuperado o entendido sus modelos.** No se decodificaron esos formatos ni se incorporaron sus datos a Corpus.

La llamada efectiva a NeoML es más fuerte que una coincidencia de nombre de DLL. Además, el [README público de NeoML](https://github.com/neoml-lib/neoml/blob/bad7a93f7b51637c1cd04e1c5fdad25e11045353/README.md) declara uso por ABBYY para OCR y otras tareas, y licencia Apache 2.0 para ese proyecto abierto. **Eso no hace abierta ni relicencia la DLL comercial, ExtraNeoML, los modelos o FineReader.** Tampoco se verificó paridad de versión entre la biblioteca comercial y el repositorio abierto. Sólo se leyó documentación pública, no la implementación del módulo propietario analizado.

Recomendación: usar esta arquitectura como información de diseño, no elegir por marketing ni confundir descompilar con obtener un OCR listo. Para decidir el mejor OCR de Corpus todavía hace falta un banco fijo de páginas escaneadas con transcripción independiente, preservación de números/artículos/negaciones, CER/WER, tiempo y costo, y una comparación bajo las mismas condiciones. Esa comparación **no se ejecutó** en este turno.

El defecto previo de texto duplicado en una página HTML de Corpus no queda atribuido al OCR ni corregido por este trabajo.

## FAIL, incidencias y NO MEDIDO

- Hubo varias llamadas interrumpidas antes de ejecutarse; se verificó el estado antes de repetir. No se contabilizan como fallos de ABBYY.
- El prefijo incompleto de 8 MiB produjo en 7-Zip exit 2, fin inesperado y advertencia de checksum, como corresponde a un archivo truncado. No se lo trató como distribución completa ni como motor.
- La extracción de FR.cab informó datos al final del contenedor. Se conserva la advertencia; no se transformó en acusación de corrupción. La extracción seleccionada terminó con exit 0 y los dos archivos materializados tienen los tamaños esperados.
- `pefile` conservó tres advertencias sobre UNWIND_INFO en Recognizer.dll; no hubo esas advertencias en endtoendrecognition.dll.
- Calidad OCR, CER, WER, precisión en castellano jurídico, comparación con Tesseract/PaddleOCR, ejecución Windows, modelos recuperados, compatibilidad Linux, licencia comercial e integración: **NO MEDIDOS**.
- No hubo banco ciego ni evaluador independiente. No se afirma «el mejor OCR», producto reconstruido, clon o producción lista.

## Custodia y alcance de la entrega

Carpeta de trabajo: `/workspace/abbyy-rea-20261015-80j6swlt`. Puntero: `/workspace/abbyy-rea-current.txt`. Capturas y metadatos completos permanecen ahí; el instalador, DLL, CAB y pseudocódigo propietario no se commitean. Los scripts de índice, descarga, extracción, inventario PE y captura REA fueron efectivamente ejecutados; se conserva su hash en `evidence-manifest.json`.

| Evidencia local | Bytes | SHA-256 |
|---|---:|---|
| rar-index.json | 58908 | 10daacd6cc59916371d82dbbceb246118c2cc12e988b7134261c60cfec829871 |
| download-status.json | 22580 | 0ae519f316d2d15044ea4d9fd316aebfd62b5b16d5c9abd2844adad8b23e8d1d |
| extraction.json | 1265 | dca70ba8019560b8a388ba645d34dd9ca949d982b2dac3efbe1bd813689592c3 |
| pe-inventory.json | 68179 | 05d75c4e9ae9a9266d13b44bb176d33bb748bef3e7505ad064a5afe38e659c01 |
| rea-inspect.stdout | 3083 | 0cd9dc7eab4bd26a1e5c4e37d2f3a238ce6fcd417ce27921470326e7478cf570 |
| rea-decompile.stdout | 5848 | 19984040e88ee064b9572d4278252eb9c99bd66edd27d6ab342e523cb32c8cb4 |

La publicación contiene hechos, interpretación y referencias a custodia, no el material propietario completo. Los trabajos de descarga y extracción finalizaron; inspect y decompile tienen registros de salida 0. No se dejaron ensayos OCR ejecutándose. No hubo PR, merge, modificación de producción ni cambio de cuentas.

---
Método TITAN: análisis estático acotado de un binario ajeno, no reconstrucción ni evaluación jurídica. Instrumento capaz de rechazar: cabeceras CRC, rangos HTTP, continuidad/tamaño de descarga y rechazo real del prefijo truncado; eso no valida precisión OCR. Rúbrica de producto/merge: N/A. Veredicto de superioridad: NO EMITIDO.
