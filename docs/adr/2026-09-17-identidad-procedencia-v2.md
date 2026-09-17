# B01/I05: contratos aislados de identidad y procedencia

Estado: propuesta implementada y probada en rama; NO integrada en producción.
Plan: enmienda 3b6cb6d85a012e8a277668fa8c12515236b91c27. Sin migración ni cambio de rutas públicas.

## Árbol y responsabilidad
contracts/provenance_v2.py: valores inmutables de obra, edición, fecha y extracción; validación y bytes del manifiesto.
tests/test_provenance_v2.py: regresiones sintéticas sin base o credenciales.
tests/check_provenance_mutations.py: tres sabotajes aislados contra los tests sin modificar.
.github/workflows/provenance-v2.yml: candidato de CI hosted con permiso de lectura.

## Decisiones
Preservar UID legacy: no recalcular identificadores existentes. Work.work_id y Version.version_id son UUID canónicos asignados una vez, no derivados de número/año ni del texto. Relación legacy y persistencia se definirán en B02; no se migran aquí. Un UUID válido no acredita existencia ni unicidad en una base: lo exigirá el repositorio transaccional.

Authority y Method son enums independientes. HTML no implica oficial, OCR no implica secundario. LegalStatus.UNKNOWN por defecto. La referencia de revisión se exige para estados evaluados, pero su UUID no prueba firma humana; verificar existencia, alcance y aprobación en integración. No se presenta una revisión sintáctica como dictamen.

Original y texto UTF-8 tienen digests separados, completos, sin prefijos ni fallback cuando falta hash. Se verifica el byte recibido. El perfil corpus-manifest-v1 fija orden de registros/claves, escape ASCII y LF. No es RFC8785, firma, autenticidad estatal ni prueba de fidelidad del OCR. Alternative sources/annexes se preservan como registros distintos; duplicado exacto da error.

## Contratos y flujo
Metadata explícita -> Work/Version/DatedEvidence/Extraction -> errores ContractError o valor válido.
Bytes originales y texto -> Extraction.verify -> dos hashes verificados + UTF-8 estricto.
Tupla de extracciones -> manifest_bytes -> bytes deterministas con perfil.
No acceso a red, no escritura de archivo/base dentro de estos contratos. require_url comprueba sintaxis, NO SSRF; B06 deberá verificar DNS, redirects, IP y tamaño. No usar esta función como autorización de descarga.

## Riesgos y límites
Memoria O(n) y ordenamiento O(n log n) del manifiesto; sin benchmark a10x. No es motor de búsqueda, auth o publicador; no recibe HTTP. Estructura física de anexos, cantidades legales, fuente auténtica, privacidad y revisión humana no se infieren del hash. Depende de B02 y gates de adopción antes de servirlo. No prueba que el defecto del lector nacional del PR1 esté corregido: B03 sigue abierto.

## Verificación
python3 tests/test_provenance_v2.py
python3 tests/check_provenance_mutations.py
23 tests válidos; 3 mutantes compilables rechazados. Se controlan original alterado, hash incompleto y prefijo compartido, texto alterado, URL con credenciales, estados sin revisión, fechas imposibles, metadatos inválidos, autoridad independiente, anexos y duplicados. Las comparaciones son sintéticas: no medir producción con estos verdes.
