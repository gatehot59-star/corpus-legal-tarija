# OCR: un importe alterado y dos lineas omitidas, confirmados visualmente

Fecha: 22 de octubre de 2026, ART. Operador: GPT-6 Astra.

## Resultado e impacto

**REFUTADO: el texto fue copiado a la perfeccion.** En la pagina 2 de la Ley Departamental 151/2016, articulo 5.I, el escaneo indica un capital de **veinte millones de bolivianos**. PaddleOCR-VL-1.6 produjo literalmente:

> I. El (FOPEDT) estará financiado con un capital inicial de Bs20.000.000.000.0

El original tiene la parte entera `20.000.000` y la aclaracion inequívoca `(Bolivianos veinte millones 00/100)`. El OCR agrego un grupo de ceros. No interpreto su cadena mal formada como un importe monetario valido ni baso el hallazgo en distinguir las letras o/los ceros del grafismo de centavos.

Ademas, omitio estas dos lineas visibles, que explicitan el monto y el origen de los recursos:

> (Bolivianos veinte millones 00/100) provenientes de las Regalías que percibe
> el Departamento por concepto de explotación de Hidrocarburos.

Es una discrepancia de contenido juridico, no un mero cambio de espacios. El mismo bloque defectuoso esta en la salida original del lote de cien paginas y en las tres repeticiones de esa pagina. Repetir exactamente una salida no la convierte en correcta.

![Articulo 5.I del escaneo, recorte para cotejo](https://t90171457413.p.clickup-attachments.com/t90171457413/0d5c324d-c73e-505e-ba73-7521d66cfd88/ley151-articulo5-cotejo.png)

## Sujeto, fuentes y alcance real

Repositorio: `gatehot59-star/corpus-legal-tarija`. Rama documental: `audit/2026-10-15-prueba-viva-corpus`. Head anterior a esta publicacion: `d2ef8bafc09a433fc87ab0df8e54bed12edba8ad`. Main consultado: `c273c659ee90f2259f540cb14c576d6a16dcfb40`.

Entradas: los PNG congelados de p037 y p092, extraidos del banco de cien paginas y cotejados con sus hashes. No se corrieron nuevas inferencias, no se edito el gold del banco reservado y no se modifico producto, main, configuracion, credenciales ni datos de produccion.

- **p092:** Ley Departamental 151/2016, pagina 2. PNG 2550 x 3513, SHA256 `88d9fdddf68205f68d69ab1324bfd00dd406e7ac07b42abf91894950432ba539`. Inspeccion visual decisiva: articulo 5.I, caja original `[410, 1580, 2320, 1810]`.
- **p037:** Resolucion R.A. N° 216/2012-2013, pagina 1. PNG 2555 x 3946, SHA256 `6c7da29c3fc8057035eab6c2c4e5f3b0e8a5fe1727e3c79e95a06853e2512685`. Se vio la pagina completa en una vista de lectura. Son reconocibles el numero de resolucion, el titulo y la referencia a YPFB. Los sellos y firmas degradados no permiten aqui fijar una transcripcion exacta de todos los nombres. No se declara esta pagina perfecta ni se inventa un nombre correcto.

![Vista completa de p037 usada para lectura](https://t90171457413.p.clickup-attachments.com/t90171457413/3bbcefdf-1320-5295-ba0f-9812682015e6/resolucion216-cotejo.png)

**Cobertura:** dos fuentes recuperadas y verificadas; una vista completa de p037 y el articulo 5.I de p092 efectivamente vistos. No es una transcripcion exhaustiva de ambas paginas ni una evaluacion de las cien. La vista completa preparada de p092 no se incorpora como evidencia de lectura: preparar o transferir datos no equivale a verlos. Un contraejemplo claro basta para refutar la afirmacion de perfeccion; no basta para calcular una tasa global de error.

## Instrumento y controles

La expectativa se leyo en los pixeles, no en otro OCR. La revision es **IA, no humana y no ciega**: Astra ya conocia la salida candidata. No se presenta como auditoria externa.

El recorte p092 conserva la resolucion espacial del original, convertido a gris y binarizado a umbral 155 para visualizarlo. PNG transferido: 9234 bytes, SHA256 `ad3b61c8443180dfa3d08271a550f66dbac636ca7fa2ed05694fd40a097d3812`. El sandbox verifico ese hash antes de abrir la imagen. La vista p037 se redujo a 1280 x 1977 y se binarizo con el mismo umbral; TIFF/XZ transferido: 21172 bytes, SHA256 `2a097580ee36db5160de97aafa07c736253000c111d38a4f046eb922c25efe75`; los pixeles decodificados se comprobaron con SHA256 `02861efe446e6165faca4135717b777e4d9caf2bd7c2ddab2eb5edf8eb4e43de`.

Despues de leer el recorte se fijaron tres frases visibles y se buscaron en los bloques originales p092, p092-r2, p092-r3 y p092-r6. Faltan las tres en los cuatro bloques. El bloque ya es defectuoso en el JSON crudo, no solamente en este informe. El instrumento de presencia paso con las tres frases y detecto la supresion intencional de una de ellas. Esto valida el chequeo de presencia, no certifica por si mismo la lectura visual ni la exactitud del documento entero.

El recibo JSON adjunto conserva el codigo ejecutado, los inputs positivo/negativo y sus resultados, los cuatro bloques completos capturados, sus hashes y la fecha. La captura declarada es esos bloques, no todos los logs, pesos o cajas del experimento. Los JSON completos del motor permanecen en las salidas conservadas de Kaggle y brain-env.

## Afirmaciones y limites

- **CONFIRMADO:** el articulo 5.I contiene dos lineas legibles ausentes de los cuatro bloques OCR inspeccionados.
- **CONFIRMADO:** el monto emitido contiene un grupo adicional de ceros respecto de la parte entera visible y contradice la aclaracion escrita en letras.
- **REFUTADO:** igualdad entre repeticiones demuestra copia perfecta.
- **NO MEDIDO:** CER/WER de estas dos paginas, exactitud de las cien, exactitud completa de nombres/sellos y causa interna concreta del fallo o de la lentitud.
- **NO REALIZADO:** correccion del OCR, integracion, merge o despliegue.

La mejora medida anteriormente en cinco paginas frente a Tesseract sigue siendo un resultado de ese banco y su referencia IA. No se convierte en garantia de ausencia de errores juridicos fuera del banco. No usar este OCR como transcriptor juridico sin cotejar importes y contenido sensible con la fuente.

## Incidencias propias y custodia

El navegador no conecto y un primer transporte grande de imagen quedo truncado. La via que permitio ver los dos archivos citados fue una transferencia acotada con hash y apertura efectiva en el sandbox. Tres intentos posteriores de copiar un recorte adicional del sello de p037 se rechazaron por payload incompleto, hash distinto o padding; no se genero evidencia visual nueva desde esos bytes ni se atribuyo ese fallo al OCR. No se afirma haber visto ese recorte adicional.

La revalidacion HTTP de la URL publica de p037 devolvio 403; la de p092 no se intento despues de ese rechazo. Esto no invalida los PNG congelados verificados ni los adjuntos efectivamente vistos, pero las URLs de origen no se presentan como actualmente accesibles.

## Control final

Modo: TITAN LIGERO, revision acotada, rubrica formal N/A. Funciones ejercidas por un mismo operador: revisor visual, verificador de presencia y control documental.

**Gate I:** PASA para identidad de entradas, transferencia de las dos vistas efectivamente abiertas y chequeo de presencia con positivo/negativo. Lectura visual IA con las transformaciones y limites declarados. N/A una nueva corrida del motor o repeticion GPU: se inspeccionan salidas historicas preservadas.

**Gate II:** PASA para el contraejemplo acotado y su impacto. No hay certificacion de pagina completa, CER nuevo, perfeccion ni causalidad interna.

**Gate III formal:** INCOMPLETA respecto del protocolo amplio que exige main y Nexus. Esta entrega no autoriza merge ni mensajes. Informe y evidencia se publican en rama de auditoria; el cierre de esta respuesta incluye lectura remota y Doc de ClickUp, sin extender permisos.

Que no se midio que importaba: una referencia completa de cada pagina, los sellos ilegibles y el error juridico a escala del corpus. Nada de eso impide reconocer ahora el error monetario visible.
