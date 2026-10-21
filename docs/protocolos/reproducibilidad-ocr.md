# Estándar de reproducibilidad OCR

Versión 1.0. Adoptado por pedido de Abraham el 21 de octubre de 2026. Aplicar a futuras verificaciones de repetibilidad y reproducibilidad del OCR de Corpus. Es un protocolo operativo, no una certificación de exactitud ni una autorización automática para ejecutar, publicar datos o desplegar cambios.

Fuente del método: [ensayo verificado de las dos páginas atípicas](https://github.com/gatehot59-star/corpus-legal-tarija/commit/12d79957d3682fb33d265caf5d0cb878788269b9). Se conserva ese resultado como evidencia histórica; sus tiempos no se copian como resultados de trabajos futuros.

## Regla principal

Una conclusión sólo vale para lo que el instrumento podía contradecir. Separar siempre:

- **Repetibilidad del texto:** si las lecturas de una misma entrada son exactamente iguales.
- **Estabilidad temporal observada:** cuánto varían los tiempos en las condiciones medidas.
- **Reproducibilidad entre sesiones o entornos:** requiere ejecutar las sesiones o entornos que se afirman, no contarlos como si fueran repeticiones dentro de una sesión.
- **Exactitud:** requiere una referencia independiente y declarar si es humana o IA.
- **Causa de la demora:** requiere instrumentación o una intervención controlada que la ponga a prueba.

Que un texto se repita no prueba que sea correcto. Que un proceso termine con exit 0 no prueba ninguna de esas propiedades por sí solo.

## 1. Fijar el sujeto y el protocolo antes de medir

Identificar cada documento y página original, su motivo de selección, la referencia temporal previa y el criterio que se quiere comprobar. Congelar las imágenes y su manifiesto con SHA256, dimensiones y resolución; no recortar, corregir ni reducir resolución durante una prueba de repetibilidad.

Fijar revisiones y hashes de pesos, configuración del pipeline, semilla, dispositivo, hilos, batch, límites de tokens y calentamiento. Registrar el entorno y las versiones realmente resueltas, incluidas las transitivas, y compararlas contra la referencia antes de declarar equivalencia. No actualizar dependencias sólo porque haya una versión más reciente: eso cambia el experimento.

Sellar orden de ejecución, número de repeticiones, timeouts y presupuesto antes de inferir. Si se necesita un PASS/FAIL de latencia, fijar antes la tolerancia y su justificación; sin tolerancia previa, entregar estadísticas descriptivas, no inventar un umbral después de ver los tiempos.

## 2. Repetir de verdad

Mínimo diagnóstico para el perfil OCR: **tres inferencias nuevas por página**, además de la lectura original cuando exista. Tres no garantizan potencia estadística ni generalización; aumentar o cambiar el diseño cuando la afirmación lo requiera.

En el ensayo de referencia se usó una sesión nueva, una carga del modelo, un calentamiento sintético y orden **A,B,B,A,A,B**, con tres lecturas de cada una de dos páginas. Es un orden explícito reproducible, no una prueba de que todos los efectos de orden están eliminados.

Cada repetición debe ejecutar el OCR sobre la imagen; reutilizar una predicción o copiar el archivo anterior no cuenta. Registrar un ID distinto por inferencia y mantener el vínculo con la página original. Mantener el gold y las salidas anteriores fuera de la inferencia.

Distinguir una sola sesión con tres repeticiones de tres sesiones independientes. Si no se reproduce el historial de páginas anteriores, decirlo. Seleccionar páginas por haber sido extremas tampoco representa al corpus completo.

## 3. Medir sin mezclar etapas

Separar preparación e instalación, carga, calentamiento, inferencia por página y tiempo continuo del lote. Para inferencia GPU, sincronizar el dispositivo alrededor del tramo medido y verificar uso real de GPU, no sólo la solicitud de acelerador.

Guardar tiempo monotónico y marcas UTC, con hora local explícita al informar. Conservar todos los tiempos individuales y su orden. Reportar media, mediana, mínimo, máximo, rango, desvío estándar muestral y diferencia respecto del original; no esconder casos lentos detrás de un promedio.

Conservar intentos fallidos, errores y timeouts. Un fallo parcial no es la duración exitosa del lote. Un timeout de transporte no autoriza relanzar: primero comprobar el proceso y los recibos existentes.

## 4. Comparar texto exacto

Comparar directamente los **bytes UTF-8 de los textos completos**, sin strip, normalización Unicode, compactación de espacios, corrección ortográfica, cambio de mayúsculas ni eliminación de saltos. Guardar también SHA256, caracteres y bytes, pero no sustituir igualdad directa por una puntuación de similitud.

Comparar todos los pares dentro de las repeticiones de cada página y cada repetición contra su original. Tres lecturas nuevas más una original producen seis pares por página. No comparar páginas distintas como si debieran contener el mismo texto.

Si hay diferencias, conservar ambos textos y localizar las diferencias sin modificar los originales. Si se desea además una comparación normalizada, etiquetarla como secundaria: nunca reemplaza el resultado exacto.

Comparar separadamente los JSON crudos cuando existan. Diferencias de metadatos o rutas pueden hacer distintos los JSON sin hacer distinto el texto; no confundir los dos veredictos ni borrar esos campos en silencio.

## 5. Probar el instrumento y la integridad

El comparador debe aceptar un control idéntico y detectar cambios de un carácter, un espacio, LF frente a CRLF, forma Unicode y una negación eliminada. Los controles artificiales no cuentan como resultados OCR.

Verificar cobertura de IDs, orden sellado, hashes de entradas y salidas, correspondencia entre bloques y texto, longitudes, tiempos positivos, ausencia de solapamientos cuando la ejecución es serial, coherencia de agregados, finalización y exit observado. Elegir controles negativos capaces de detectar exactamente el fallo que la comprobación pretende descartar.

Declarar por afirmación: instrumento, si podía dar rojo y resultado. Usar **PASS**, **FAIL**, **EN CURSO** o **NO MEDIDO** con alcance explícito. Un estado RUNNING no prueba progreso de inferencia; un archivo descargado no prueba que esté verificado.

## 6. Conservar evidencia que permita contradecir el resultado

Guardar las transcripciones completas, tiempos, comandos y exits, configuración, hashes, errores y recibos necesarios para recomputar el resultado. Mantener evidencia cruda separada del informe derivado. Si cajas, logs íntegros o archivos grandes quedan fuera de Git, identificar dónde están y qué parte sí quedó publicada; un hash solo no permite recomputar texto ausente.

Publicar el resultado sustancial en una rama de trabajo de Git y en un Doc de ClickUp, respetando permisos y privacidad de los documentos fuente. No commitear secretos, pesos ni binarios derivados. No mezclar una medición con un merge o despliegue no autorizado.

Leer de vuelta lo publicado, cotejarlo con los archivos fuente y recalcular igualdad y estadísticas. Registrar operador e instrumentos; no llamar auditoría externa a una comprobación del mismo operador.

El seguimiento desatendido puede recoger archivos sin enviar avisos: sólo prometer notificación si existe un mecanismo configurado para hacerlo. Si el trabajo sigue en curso, dejar un checkpoint honesto, no un veredicto anticipado.

## 7. Cierre mínimo

El informe debe permitir responder: qué páginas y hashes se probaron; cuántas inferencias y sesiones; qué entorno coincidió o cambió; qué pares de texto fueron iguales o distintos; cuánto tardó cada lectura; qué controles se ejecutaron; dónde está la evidencia; qué no se midió.

En el chat: dos o tres frases con el resultado, el límite principal y enlaces a Git y Doc. No presentar adopción de este estándar como una nueva ejecución exitosa.

## Caso de referencia, no objetivo futuro

El ensayo de octubre procesó dos páginas, tres veces cada una. Las seis lecturas coincidieron exactamente entre sí por página y con sus originales: doce pares iguales, cero distintos. Las medias nuevas fueron 155.350597 y 168.136592 segundos; la exactitud y la causa interna de la demora quedaron NO MEDIDAS. La prueba de tres repeticiones se hizo en una sola sesión GPU nueva, distinta de la sesión del lote original.

[Informe y evidencia completos del caso de referencia](https://github.com/gatehot59-star/corpus-legal-tarija/commit/12d79957d3682fb33d265caf5d0cb878788269b9).

No se creó una nueva corrida, un sistema de notificación ni una política de aprobación automática al adoptar este documento.
