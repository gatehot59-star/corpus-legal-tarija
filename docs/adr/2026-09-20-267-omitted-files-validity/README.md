# Actualizacion de custodia posterior al informe

El informe de alcance fue publicado primero en516aea974755b48a2a8f6a0de6cb2a4dd4967a9a y declaraba la custodia pendiente. Despues se publico `test-receipt.xz.b64` endfa18de2e0ba100abea2ebf748df2b619ab047e3. Esta nota actualiza esa parte sin reescribir la cronologia.

**Ahora SI estan commiteados:** fuente completa del instrumento y hook, seis comandos exactos con stdout/stderr completos y exit codes, control adverso del hook y cuatro diffs locales. JSON decodificado41725bytes, SHA256 `fce9674dc7899a48b000eb95835144c7015fb2fd4214764691f56da821119e1c`. Recuperado desde git y comparado BYTE A BYTE con la captura local. Los seis comandos devolvieron0 y los dos brazos produjeron los mismos111 nombres de tests con resultado ok.

**Siguen SIN publicarse completas:** las dos trazas globales de E/S, el manifiesto integral y las capturas REST de inicializacion. Persisten localmente donde indica el informe. No se puede recomputar toda la afirmacion de ausencia de accesos desde este paquete: es una observacion local con custodia parcial declarada. No se usa como recibo remoto ni se mergea por ella.

Verificacion sin ejecutar el payload: `base64 --decode test-receipt.xz.b64 | xz --decompress > test-receipt.json`, luego `sha256sum test-receipt.json`. Abrir JSON para inspeccionar `runs`, `instrument_source`, `hook_source`, `falsifier` y `diff_evidence`. No ejecutar el codigo embebido solo para verificar la custodia.

El laboratorio sigue incompleto:10 originales subidos,11 por subir y un README vacio extra en la inicializacion; main extra como default. Ningun PR experimental, ningun run al consultar, ningun merge. El permiso anterior no se vuelve a pedir; lo pendiente es resolver el desvio real de inicializacion antes de seguir escribiendo el laboratorio.
