# Auditoría de Brain: PR17 y atribución de las omisiones SQLite

19-sep-2026 ART. Encargo: auditar el trabajo posterior al cierre52. Sin permiso de merge inferido de firmas anteriores. Sujeto: PR17 y diagnóstico06 de callers, no repetir auditoría productiva PR14/16. Funciones de revisor/verificador/control final del mismo operador; no tres auditores independientes.

## Veredicto

**PR17 corrige el cierre explícito del fixture HTTP, sin nuevo reparo en lo probado. El diagnóstico de169omisiones restantes se reproduce exactamente.** No significa que toda la deuda esté corregida ni demuestra fugas productivas. PR17 sigue abierto/sin merge y con la misma cabeza al terminar.

Revisiones: base de diagnóstico1f4f87da4f99ba2d1e88d288fd994d4d40ce49f8; cabeza PR17 3eedba5460495bb1c329e0cd87d8305fd0e9e00a, base del PR9175f7bb12df5d0cd46c15b7c4e358e111d106c2. Main observado al iniciarad4fa3daaa5395f0269e4d47286d292b17ad6486. Diferencia del PR: sólo tests/test_exact_http.py,4inserciones/3eliminaciones, import closing y tres contextos. Assertions funcionales, producto y workflow sin cambios.

Leídos Docs de Brain05/06, Nexus53/54, diff y archivo completo. Capturas originales recuperadas de Git, base64estricto+xz y longitud/hash comprobados:89251bytes SHA d5ca21c389dc28afb44cf41dce4a045cc3d8c95747988c1214ac054bc69eb6c4 y398797bytes SHA2622590d9ce2c68d4403161b24cf0a7ebdcefe108a7d96cc2ef2de04eabbc832. Se utilizó la versión corregida ad4fa3d, no el wrapper inválido0d31ef9. Brain declaró el stdout inicial no preservado de su supervisor fallido; no lo tratamos como evidencia íntegra ni invalida las corridas definitivas.

## Medición propia sobre revisiones congeladas

Observador publicado de Astra reutilizado literalmente, inspeccionado antes: retiene conexiones, registra close exitoso, argv y stack en cada proceso. No es un contador nuevo ni mide RSS o supervivencia tras terminar. Tiene límites para custom factory/otras vías de conexión; no se convierte en certificación global. Controles ejecutados: cerrado1/1/0 y abierto deliberado1/0/1. Mismo criterio separado assert unclosed==0 devuelve0y1.

HTTP antes:41abiertas/24cerradas/17pendientes; HTTP PR17:41/41/0; mutante propio quitando SOLAMENTE el primer closing de setUp:41/26/15. Los15tests HTTP pasan en las tres corridas; el criterio de cierre falla antes y en el mutante y pasa en PR17. Esto prueba que el verde funcional no protege esta propiedad. Mutante sólo en scratch, nunca en producto.

Rastreo serial independiente de la captura de Brain, sobre la misma base:

- clean_snapshot_sol:21tests,47abiertas/45cerradas/2pendientes; incluye24hijos que cierran24/24.
- access_policy:15tests,172/109/63.
- login_guards:18tests,157/88/69.
- isolated_session:10tests,123/88/35.

Las64pruebas funcionales pasan; las cuatro suites fallan el criterio de cero omisiones. Recalculadas todas las pilas y agrupadas por última llamada del repo: matriz idéntica a Brain,169eventos en10sitios de4archivos. Se preserva la matriz y cada stack completo en la evidencia propia, no sólo el total.

Sitios únicos: test_clean_snapshot.py:43; test_clean_snapshot_sol.py:50; test_access_policy.py:34,43,62; test_isolated_login.py:41,50,67,71,108. Las35de sesión son métodos prestados del fixture LoginTests, no aperturas de logout. Los17HTTP no se suman dentro de169: PR17 los corrige sólo en su rama, todavía no en main.

## Prueba nueva: excepción dentro de los tres callers reales

No me limité al ejemplo genérico closing+transacción de Brain. Instrumento propio exception_probe.py carga HTTPTests real del PR y sustituye la conexión sólo durante el caller examinado por una subclase que lanza una excepción DESPUÉS de ejecutar el INSERT/UPDATE real.

En setUp, test_historical_exact_version_survives_current_change y test_tampered_text_never_returned: se observó la excepción inyectada, la conexión ya no admite SELECT1 (ProgrammingError de conexión cerrada) y un lector independiente comprueba rollback:0filas de documentos en setup, sha anterior en cambio de versión y texto original en alteración. Los tres pasan,exit0. Cleanups reales ejecutados en finally, listeners/hilos cerrados por el fixture.

Mismo instrumento sobre el mutante sin closing de setUp:exit1 por AssertionError connection usable. El positivo y el falso cierre se distinguen por usabilidad real de SQLite, no por repetir la bandera audit_closed del observador. Ésta es la verificación propia adicional y su falsador causal. No se modificó la fuente del producto ni del PR.

Compilación posterior: python3 -m py_compile tests/test_exact_http.py sobre cabeza PR17,exit0,stdout/stderr vacíos. No se relanzaron111tests completos: en este turno se ejecutaron15HTTP en tres variantes,64casos del rastreo y controles/inyección separados. No inflar a109tests únicos ni atribuir a esta auditoría los111del autor.

## CI, prioridades y alcance

API de PR17: check105914625233 completed/success, job https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35449708876/job/105914625233 . Hilos de review vacíos al consultar; silencio no equivale a aprobación. No Actions nuevos ni lectura de stdout remoto completo. CI funcional no incluye el contador; Brain lo declaró correctamente. Recomendación: convertir el criterio en guard repetible al corregir el resto, con control positivo/negativo y cobertura explícita de hijos, sin venderlo como chequeo global.

Lo entregado cumple el arreglo puntual y el diagnóstico pedido, no el handoff entero. Los169faltantes no están corregidos. La matriz buscar/verificar/guardar/reportar continúa pendiente. Prioridad siguiente: cierre quirúrgico de esos diez sitios preservando transacciones y medición169a0, sin reabrir arquitectura productiva; luego avanzar al recorrido útil. No repetir otra auditoría completa sin delta. Son recomendaciones, no implementación, asignación ni autorización de merge.

## Custodia y reproducción

Evidencia propia en docs/auditorias/2026-09-19-07-auditoria-brain-pr17/evidence.xz.b64, commit661350ee6d505715eac99352aac26b00109eacfe. Un único archivo,10732bytesASCII, sin concatenación histórica. Decodificar base64estricto y lzma.decompress:374739bytes JSON, SHA2569d58c918471c53fec0a658a56224eca6966d3eeb3224a48cdb8b2f4fa8254c12. Recuperado de Git, reconstruido y comparado BYTEPORBYTE contra original: idéntico.

Incluye comandos,retornos,stdout/stderr completos de9corridas del observador,9evaluaciones del criterio,fuentes del observador/supervisor,matriz y stacks completos,instrumento propio de excepciones y resultado positivo/mutante. Sin bases vivas,credenciales,Authorization,imágenes SQLite ni valores privados. Los33PID de las corridas observadas estaban ausentes al cierre. No se afirmó escaneo independiente de todos los puertos ni medición de memoria productiva; HTTP usa cleanup con shutdown,server_close y join comprobado.

Para reproducir: extraer base/head indicados en carpetas nuevas; guardar observer como sitecustomize.py y fijar PYTHONPATH/AUDIT_RESOURCE_DIR por corrida; ejecutar commands guardados y comparar criterio separado. Leer supervisor antes de usarlo: contiene directorio de esta captura, sustituir sólo rutas propias. exception.source se guarda como script y recibe path al repo; su mutante revierte sólo el primer contexto descrito en mutant. No ejecutar sobre árboles ajenos.

Gate I PASA acotado: baseline,negativos,atribución y prueba física de excepción. La propiedad de cierre de las cuatro suites restantes FALLA, distinta del éxito de la auditoría. Gate II PASA: causalidad/límites y pendientes separados. Gate III al publicar: evidencia ya recuperada idéntica; este informe,Doc público y Nexus se verifican antes del chat. No puntaje de producción, TLS, crash,legal,piloto,restauración o RSS. Sin merge,despliegue,correcciones de producto ni cambios en PR1/17.
