# Benchmark OCR completo del PDF de Juan: en corrida

Se amplió la corrida desde las 10 páginas de muestra a las 44 páginas completas del PDF oficial `RPA_161_200_2013_2014.pdf`, sin tocar producción ni sobrescribir el OCR histórico.

## Configuración

- Fuente: `/tmp/juan-source.pdf`, 44 páginas, SHA-256 `6b9dcffaffdfb997dc4227dea2d89d0a01b4474d6c00abfa4bb4152ca4750784`.
- Entrada idéntica: render a 300 dpi, escala de grises.
- Motores: Tesseract fast PSM 3, Tesseract best PSM 3 y PaddleOCR PP-OCRv5 mobile Latin en CPU.
- Salida aislada: `/tmp/ocr-full44`.
- Instrumento: `pipeline/benchmark_ocr.py`, que conserva texto crudo por página y no calcula CER/WER sin gold humana.

## Estado verificado

La corrida quedó activa en la VM de Corpus. Al registrar este recibo había 14 salidas de Tesseract fast, Tesseract aún no había iniciado best y PaddleOCR todavía no había iniciado; el proceso seguía vivo y consumiendo el worker esperado. La salida final se recogerá desde el mismo directorio y se revisarán las 44 páginas, no solo las 10 anteriores.

## Regla de seguridad

Paddle sigue siendo candidato. No se promociona, no se reindexa el corpus y no se altera la base de datos hasta completar la revisión humana de los campos jurídicos críticos y la gold independiente.

## Siguiente acción

Cuando finalice la corrida: revisar página por página resolución, artículos, fechas, nombres, cantidades, citas y orden; producir la anotación completa y decidir si vale la pena ampliar el benchmark a 120-200 páginas del corpus nacional.

--- METODO TITAN ---
Accion delicada: NO
Modo aplicado:   TITAN FULL
Rubrica:         37/40 -> 92.5/100
N/A declarados:  3 (deployment, external review, final gold metrics are not applicable or not yet complete)
Review externo:  no emitido (deuda declarada)
Instrumento:     BRAIN via MUDH Gateway build.run, exit=0 for launch and process verification
