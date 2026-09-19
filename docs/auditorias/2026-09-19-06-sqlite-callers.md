# SQLite: 169 omisiones de cierre explicito, 10 sitios exactos

19-sep-2026 ART. Pedido: Trace the remaining SQLite leaks to their exact callers. Diagnostico solamente, sin correccion, merge, CI nuevo ni despliegue. Operador/revisor: Brain. Observador: instrumento anterior de Astra, recuperado literalmente; no equivale a una nueva revision externa.

## Sujeto y resultado

Repo gatehot59-star/corpus-legal-tarija, main congelado 1f4f87da4f99ba2d1e88d288fd994d4d40ce49f8. Cuatro suites restantes del handoff: clean_snapshot_sol, access_policy, login_guards e isolated_session. PR17 sigue abierto en 3eedba5460495bb1c329e0cd87d8305fd0e9e00a; su correccion HTTP no esta en este main. HTTP se excluyo expresamente del nuevo conteo porque ya tiene arreglo en PR17. No se dice que main tenga cero pendientes HTTP.

CONFIRMADO: 169 aperturas observadas no reciben close explicito, en 10 callsites de cuatro archivos de tests. Ninguna de esas 169 pilas termina en un opener de producto. Esto NO certifica ausencia global de fugas productivas: solo atribuye las observadas en este recorrido. El observador mantiene referencias fuertes deliberadamente; mide omision de close, no recursos sobrevivientes a la salida de un proceso.

## Corridas nuevas, no conteos heredados

<table><tr><th>Suite</th><th>Tests</th><th>Abiertas</th><th>Cerradas</th><th>Sin close</th><th>Procesos con captura</th></tr><tr><td>clean_snapshot_sol</td><td>21</td><td>47</td><td>45</td><td>2</td><td>25</td></tr><tr><td>access_policy</td><td>15</td><td>172</td><td>109</td><td>63</td><td>1</td></tr><tr><td>login_guards</td><td>18</td><td>157</td><td>88</td><td>69</td><td>1</td></tr><tr><td>isolated_session</td><td>10</td><td>123</td><td>88</td><td>35</td><td>1</td></tr><tr><td>Total de estas corridas</td><td>64</td><td>499</td><td>330</td><td>169</td><td>28</td></tr></table>

Las cuatro suites funcionales salieron 0: 21 en 6.143s, 15 en 4.762s, 18 en 21.006s y 10 en 13.948s. No se sumaron otra vez los 12 tests heredados de login. El criterio separado assert unclosed == 0 sale 1 en las cuatro. Un verde funcional no detecta esta deuda.

## Matriz de callsites: lineas en la revision congelada

Prefijo de todos los archivos: tests/. Cada fila es un sitio unico, no un bug distinto por cada invocacion.

<table><tr><th>Archivo:linea</th><th>Funcion que abre</th><th>Suite y ocurrencias</th></tr><tr><td>test_clean_snapshot.py:43</td><td>CleanCopyTests.test_full_copy_keeps_ids_and_archives_old_text</td><td>clean_snapshot_sol: 1, heredado</td></tr><tr><td>test_clean_snapshot_sol.py:50</td><td>InputTests.test_exact_repeated_text_after_real_build</td><td>clean_snapshot_sol: 1</td></tr><tr><td>test_access_policy.py:34</td><td>AccessTests.setUp, store</td><td>access_policy: 15</td></tr><tr><td>test_access_policy.py:43</td><td>AccessTests.setUp, candidate</td><td>access_policy: 15</td></tr><tr><td>test_access_policy.py:62</td><td>AccessTests.sql</td><td>access_policy: 33</td></tr><tr><td>test_isolated_login.py:41</td><td>LoginTests.setUp, store</td><td>login_guards: 18; isolated_session: 10</td></tr><tr><td>test_isolated_login.py:50</td><td>LoginTests.setUp, candidate</td><td>login_guards: 18; isolated_session: 10</td></tr><tr><td>test_isolated_login.py:67</td><td>LoginTests.sql</td><td>login_guards: 15; isolated_session: 13</td></tr><tr><td>test_isolated_login.py:71</td><td>LoginTests.count</td><td>login_guards: 17; isolated_session: 2</td></tr><tr><td>test_isolated_login.py:108</td><td>test_login_is_not_a_grant_and_token_reads_only_after_explicit_fixture_grant</td><td>login_guards: 1</td></tr></table>

Los 104 de guards+session vienen de cinco sitios en test_isolated_login.py. GuardTests hereda LoginTests. SessionTests no hereda sus tests: presta sql/count/grant y llama base.LoginTests.setUp desde test_isolated_session.py:21. Por eso corregir el archivo de logout o copiar cierres en cada suite consumidora seria apuntar al sujeto equivocado.

AccessTests.sql: 19 aperturas vienen de test_each_persisted_gate_denies_independently:118; siete de test_schema_requires_valid_intervals_origin_and_evidence:205, incluso cuando execute levanta IntegrityError; las otras siete son revocacion de grant:132, sesion:137, withdrawal:142, headers:152, paid/pilot:162 y :164, y store failure:168. Esas excepciones hacen rollback pero no close.

La evidencia incluye caller_chains con cada cadena de archivos/lineas/funciones y frecuencia, ademas de TODOS los unclosed_stacks originales. Las llamadas grant pasan por LoginTests.grant:90 y terminan en sql:67; no abren una conexion adicional en grant.

## Controles y limites del instrumento

Se recupero resource_followup.instrument de la evidencia Astra de 420667 bytes, SHA256 e4e3c3f266c91d628fdcb2be55a319aebd80700c7b42a408d71273e128f5b273, comprobado antes de extraerlo. sitecustomize intercepta sqlite3.connect y usa una subclase que marca close despues de ejecutarlo. Se leyo el uso de connect en fixtures y rutas consumidas; no se encontro factory alternativo ni alias dbapi2 en esos callsites. No se afirma interceptar cualquier extension SQLite del repositorio.

Positivo propio: una conexion cerrada, 1/1/0. Negativo deliberado: misma apertura sin close, 1/0/1. Repeticion positiva nueva: 1/1/0. Mismo criterio assert unclosed == 0 produce 0/1/0. Son controles del observador, no un fix aplicado a los 10 sitios.

Las 24 aperturas de hijos del CLI de snapshot cerraron todas; el padre registro 23/21/2. VersionTests.setUp usa addCleanup(self.c.close); SessionTests.revoked usa closing. CleanCopyTests.setUp llama corpus.cerrar() y despues corpus.con.close(): cerrar por si solo hace commits/optimize, pero el fixture si completa close. Ninguno de esos caminos explica las omisiones atribuidas.

Se ejecutaron suites seriales, cada una con timeout 240s, en archive nuevo; datos ficticios, sin bases vivas. Capturas guardan argv/cwd, exit, stdout/stderr completos, PID, conteos y pilas. Los 31 PID observados, incluyendo los tres controles, estaban ausentes al empaquetar. Los tests HTTP cierran servidor/hilo y verifican join; no se hizo un inventario de puertos de toda la maquina ni se cerraron recursos ajenos.

## Errores propios preservados

Primer archivo preparado tenia prefijos + por transporte de AddFile: py_compile lo rechazo antes de transferirlo. Se materializo limpio, compilo y se verifico SHA antes de ejecutar.

Primer supervisor asumio UN JSON de observacion por suite. clean_snapshot_sol genera 24 hijos y el instrumento produjo correctamente 25 archivos; fallo esa asercion del supervisor, no el producto. Se preservan fuente, log y recursos de ese intento. Su stdout no se habia persistido antes de la asercion: NO se presenta como captura completa. Se corrigio solo el supervisor para capturar antes de validar, incluir todos los PID y sumar; se repitio en un scratch nuevo. Las cuatro corridas definitivas SI conservan stdout/stderr completos. No se oculto ese error como fuga ni se cambio producto para acomodar el banco.

## Reparacion propuesta, no ejecutada

Los diez sitios usan with sqlite3.connect(...) as db, que maneja transaccion pero no cierra. El cambio acotado seria with closing(sqlite3.connect(...)) as db, db: junto con import closing en los cuatro archivos. El contexto interior conserva commit/rollback y el exterior cierra aun con excepcion. Alternativa equivalente: try/finally con close y transaccion conservada.

Aceptacion de un futuro arreglo: mismo observador, 169 a 0 en estas suites; 64 tests conservados; inverso de cada grupo vuelve rojo por close; excepcion transaccional mantiene rollback; regresion integrada 111 si corresponde al mismo head. Esa reduccion NO fue ejecutada aqui. No se modificaron tests, producto o workflows; no se hizo merge de PR17 ni PR1. Un futuro guard CI es trabajo separado, no existe por publicar este diagnostico.

## Evidencia y reproduccion

Archivo hermano: docs/auditorias/2026-09-19-06-sqlite-callers/evidence.json. Wrapper xz+base64 de JSON de 398797 bytes, SHA256 2622590d9ce2c68d4403161b24cf0a7ebdcefe108a7d96cc2ef2de04eabbc832. Fuentes del candidato ya estan en Git en la revision congelada; tracked_source_verification guarda paths/hashes comparados con git show. Se omite solo esa duplicacion y el inventario grep amplio, no capturas ni pilas. supervisor, observer y packager_source contienen los instrumentos completos ejecutados. No tokens, bases ni credenciales reales capturados.

```python
import base64, hashlib, json, lzma
from pathlib import Path
w = json.loads(Path('docs/auditorias/2026-09-19-06-sqlite-callers/evidence.json').read_text())
raw = lzma.decompress(base64.b64decode(w['payload'], validate=True))
assert len(raw) == w['uncompressed_bytes']
assert hashlib.sha256(raw).hexdigest() == w['sha256']
e = json.loads(raw)
assert sum(r['count'] for r in e['matrix']) == 169
assert len({(r['file'], r['line']) for r in e['matrix']}) == 10
```

Para repetir: archive del SHA indicado, guardar observer como sitecustomize.py en directorio propio; para cada suite ejecutar python3 tests/test_<suite>.py con PYTHONPATH a ese directorio y AUDIT_RESOURCE_DIR nuevo. Leer todos los JSON por PID, no solo el padre. supervisor registra el comando exacto usado.

## Gate final y alcance

Modo TITAN LIGERO, diagnostico acotado. Roles de revisor, verificador y control final del mismo operador; no tres revisores independientes. Rubrica numerica N/A; no acciones delicadas ni certificado de producto.

Gate I PASA para la atribucion acotada: control positivo/negativo, sujeto fijo, cadenas completas, suma por PID, repeticion del error instrumental en scratch nuevo. FALLA la propiedad close del candidato en las cuatro suites. Gate II PASA: causa en fixtures separada de producto y errores propios preservados. Gate III al publicar: pendientes recuperacion byte-identica de este commit, Doc publico y registro Nexus; se comprueban antes del cierre de chat, no se suponen ya hechos en este archivo.

CONFIRMADO: 169 omisiones explicitas en diez sitios, todas en tests de este recorrido. REFUTADO: que el verde de 64 tests demuestre close, o que las 35 de session nazcan en logout. NO MEDIDO: fugas de un servicio productivo, consumo RSS sostenido, rutas no ejecutadas, integridad juridica, TLS, restauracion productiva y piloto. Esta entrega no avanza ni declara terminados esos objetivos del plan.
