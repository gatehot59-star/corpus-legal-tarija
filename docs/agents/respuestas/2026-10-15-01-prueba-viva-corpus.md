# Corpus probado por dentro: acceso y búsquedas funcionan; texto y paginación tienen fallas

Fecha: 15 de octubre de 2026. Operador: BRAIN, GPT-6 Astra.
Pedido de Abraham: «PUES PRUEBA», referido a entrar, buscar y leer en Corpus.

## Veredicto acotado

**Sí se pudo usar Corpus por dentro. No está todo verde.** Se inició sesión con la cuenta sintética existente, se hicieron búsquedas reales, se abrió el Código Procesal Civil y se siguió su lectura. Se verificó el enlace a LexiVox y se descargó un tramo del texto. Hay tres hallazgos reproducibles: un fragmento duplicado y roto en el texto, numeración incoherente del lector y etiquetas de resaltado mostradas literalmente.

Esta es una prueba funcional acotada, no la comparación ciega de diez casos contra RuleX, ni una auditoría integral de seguridad o corrección jurídica.

## Sujeto, acceso e instrumento

- Aplicación probada: https://corpus-tarija.abacusai.cloud/corpus/login/
- Búsqueda y lectura: https://corpus-tarija.abacusai.cloud/corpus/
- Repositorio main consultado: `c273c659ee90f2259f540cb14c576d6a16dcfb40`. **La revisión exacta desplegada no se identificó independientemente.** No se atribuyen las fallas automáticamente a main ni a un PR.
- Se leyeron los recibos de servicio y jornada pública del 23 de septiembre, el provisionador de fixtures y los PR abiertos. Estos recibos orientaron el acceso, pero no se usaron como prueba del estado actual.
- Cuenta: `fixture-ana`, sintética, ya documentada y existente. No se creó, reinició ni modificó ninguna cuenta. La contraseña del fixture no se copia en este informe.
- Máquinas y herramientas: Chromium del servicio Playwright y Python/requests desde brain-env mediante MUDH Gateway, servicio build. No se arrancaron Actions, Kaggle ni máquinas de Abacus.
- Navegador: ingreso real a las 04:33:50 UTC, búsqueda mediante el formulario y clic en el resultado. HTTP: 04:36:09 a 04:36:20 UTC y comprobaciones correctivas de 04:37:50 a 04:37:54 UTC. En Argentina corresponden a las 01:33 a 01:37 del 15 de octubre.
- Se conservaron capturas completas antes de resumir; el manifiesto local fue verificado contra los bytes guardados. Evidencia seleccionada: [registro y custodia](../evidencia/2026-10-15-01-prueba-viva-corpus.md).

## PASS: qué funcionó y qué significa

| Prueba | Observación medida | Alcance |
|---|---|---|
| Ingreso del fixture | El formulario llevó a `/corpus/` y mostró la mesa de lectura | Acceso de esa cuenta, no alta ni recuperación de clientes |
| «Código Procesal Civil» | 3 resultados visibles, página 1 de 1; apareció la Ley 439 | Recuperación del documento conocido, no exhaustividad del corpus |
| «asistencia familiar» | 7 resultados visibles, página 1 de 1 | La búsqueda devolvió documentos; relevancia jurídica completa no adjudicada |
| Filtros por fuente | Con `ley`, la primera página de cada una de las tres fuentes mostró 10 resultados y todos conservaron la etiqueta de la fuente seleccionada | Se verificaron los resultados visibles, no todas las páginas ni colecciones |
| Lectura de Ley 439 | HTTP 200; 10.000 caracteres visibles; versión y fuente presentes | Primer tramo de una versión identificada |
| Continuar lectura | El enlace real abrió los caracteres 10.000 a 20.000 y conservó la versión | El recorrido funciona; el contador visible está mal |
| Fuente enlazada | LexiVox respondió 200 y corresponde al Código Procesal Civil | Fuente secundaria accesible, no certificación de vigencia |
| Descarga | 10.000 caracteres, idénticos al primer tramo mostrado | **No se estableció una descarga completa de los 396.295 caracteres declarados** |
| Consulta inexistente | Cero resultados y mensaje explícito de ausencia | El buscador no devolvió documentos para ese control |
| Acceso anónimo | La lectura protegida volvió al login sin mostrar el texto | Un control negativo, no una auditoría de todos los permisos |
| Versión inexistente | Una versión deliberadamente inexistente devolvió 403 y ningún cuerpo de lectura | El lector rechazó ese identificador |
| Cierre de sesión | Después del logout, repetir la lectura volvió al login | Se verificó el cierre de las sesiones HTTP usadas |

El panel ofreció GENESIS del TSJ, Gaceta de Tarija y LexiVox. La presencia de las tres etiquetas no demuestra cobertura completa ni una ingesta reciente.

## FAIL: tres hallazgos confirmados

### F01. Fragmento duplicado y roto en el Código Procesal Civil

En el artículo 1, el lector contiene el fragmento `Gratuidad. El pde la causa` seguido de parte del párrafo anterior y después vuelve a empezar `Gratuidad. El proceso civil es gratuito`.

En los primeros 10.000 caracteres del lector, `Gratuidad.` aparece dos veces. En la respuesta completa de la página de LexiVox enlazada aparece una vez, con el párrafo normal. Los extractos de ambos lados se preservan en la evidencia.

**Es un defecto visible de fidelidad textual, no una mera cuestión de diseño.** No se determinó si su origen está en la extracción, la composición del snapshot u otra etapa. No se comparó contra el archivo histórico original de la Gaceta ni se certificó todo el documento.

### F02. El lector numera mal las páginas

La primera pantalla dice `Página 1 de 100` y `Caracteres 0 a 10000 de 396295`. El enlace dice `Seguir leyendo página 2`; al pulsarlo, el cuerpo avanza correctamente a 10.000-20.000, pero el título dice `Página 3 de 100` y ofrece `Seguir leyendo página 4`.

Con intervalos de 10.000 caracteres, 396.295 requieren 40 tramos, no 100. El problema confirmado es la numeración/total mostrado; **no** que el enlace real falle.

### F03. El resaltado aparece como HTML literal

Los fragmentos de resultados muestran cadenas como `<mark>Código Procesal Civil</mark>` al usuario. En la respuesta analizada no había elementos `mark` renderizados. No se probó inyección de código ni se atribuye una vulnerabilidad de ese tipo.

## Dos falsos fallos del primer comprobador, retirados expresamente

1. El control de consulta inexistente esperaba el mensaje antiguo `Sin resultados autorizados para esta consulta`. La interfaz actual dice `Sin resultados para esta consulta.` y devuelve cero tarjetas. **No es un fallo de Corpus.** El control corregido rechaza una tarjeta inyectada en una copia local y un estado HTTP 500.
2. El comprobador resolvió un enlace relativo de sólo query contra el dominio raíz, no contra la URL del documento. Eso produjo un 401 ajeno al recorrido real. **No es un fallo de la paginación de Corpus.** Chromium y la comprobación corregida llegaron al tramo siguiente con HTTP 200.

El registro inicial se conserva intacto y la corrección está separada. No se suman estos dos falsos fallos a los tres hallazgos del producto.

## NO MEDIDO y límites

No se midieron cobertura/exhaustividad, vigencia normativa, calidad jurídica general, concurrencia, cuentas reales, recuperación, aislamiento completo entre usuarios, descarga completa, ni superioridad sobre RuleX. La interfaz misma advierte `Fuente secundaria. Vigencia jurídica no medida.`

No hubo evaluador ciego ni banco sellado. El operador seleccionó y ejecutó las pruebas. La consulta a LexiVox es un contraste externo limitado, no una adjudicación jurídica independiente. Las dos vías de acceso a Corpus no equivalen a dos implementaciones independientes.

Que siga funcionando una cuenta sintética documentada públicamente permite esta prueba; no demuestra que el servicio esté preparado para cuentas y datos de clientes reales.

## Limpieza y entrega

Se cerraron las sesiones HTTP con logout y se cerró la sesión del navegador a las 04:38:28 UTC. Se cerró sólo la pestaña creada para la prueba; Mindrift y la pestaña preexistente de Corpus quedaron intactas. No quedaron procesos de prueba al fondo.

No se modificaron código, despliegue, cuentas, fuentes, referencias guardadas ni reportes privados. El uso normal de login, lectura y logout puede generar el estado de sesión y los registros operativos propios de la aplicación.

La entrega se limita a dos archivos de documentación en una rama nueva; no hay PR, merge ni corrección de producción.

---
Acción delicada: NO para este recorrido funcional de lectura con fixture existente. Método: TITAN, prueba acotada con controles negativos y correcciones del instrumento declaradas. Rúbrica de código/merge: N/A, no se entrega código. Veredicto global de producción: NO EMITIDO.
