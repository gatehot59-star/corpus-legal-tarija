# Los 267 omitidos: alcance de la validez y desvio real de inicializacion

## Respuesta

Los 267 archivos originales omitidos NO cambian la comparacion acotada propuesta: un PR cuyo unico cambio es `docs/ci-trigger-probe.md`, frente a un control que solo agrega un comentario a `pipeline/clean_snapshot.py`, ejecutando exclusivamente `clean-snapshot.yml`. Esta es una conclusion condicionada sobre el diseno y una equivalencia local observada, NO una medicion del disparo remoto ni una equivalencia de todo Corpus.

La reduccion SI impide extrapolar a todos los PRs documentales, a todo el CI o a todos los consumidores de Markdown. Dos de los omitidos son `sistema/DEMO-AISLADA.md` y `sistema/RECUPERACION-DEMO.md`: el filtro VIEJO los incluye explicitamente. La frase «antes ningun PR documental disparaba CI» es falsa. La hipotesis correcta es «la ruta documental del probe, fuera de la allowlist, es omitida antes y activa la suite despues».

## Fuente exacta y alcance

Corpus `645d1732bec136bcc518070db42ff93437f95fd6`: 294 archivos. Diseno original: excluir seis workflows, quedan288 archivos y4061549 bytes. Enmienda autorizada por comentario80170047155408: conservar21 archivos originales y160845 bytes. Diferencia:267 archivos y3900704 bytes. No se modificaron los21 originales en el preflight local.

Los267 se distribuyen por primer directorio: raiz12, contracts1, disparadores1, docs156, indices1, infra4, instrumentos9, mediciones50, pipeline16, sistema9, tests8. No son todos documentacion. Entre ellos hay codigo, tests de otras suites, manifiesto de datos, infraestructura e informes.

Los seis workflows excluidos previamente son censo-gaceta-tcp, genesis-historico, genesis-jurisprudencia, legal-html, ocr-masivo y provenance-v2. No cuentan dentro de los267. Este experimento nunca pretendio medir sus eventos, suites o interacciones.

No hay `.gitattributes`, `.gitmodules`, `.github/CODEOWNERS`, `CODEOWNERS`, `docs/CODEOWNERS`, `pytest.ini`, `pyproject.toml`, `setup.cfg`, `sitecustomize.py` ni `usercustomize.py` en el arbol fuente medido. El `.gitignore` omitido solo enumera __pycache__, pyc, salida, crudo, PDF y PNG; el workflow invoca archivos Python explicitamente, no descubrimiento de tests.

## Mediciones locales, no Actions

Instrumento ejecutado: `/workspace/brain-omission-audit.py`, SHA256 `cd600939443e49d62506347a8e159a2ab8b889e3d68403ff2e3fd5ac8d4ff992`. Directorio de evidencia persistente: `/workspace/brain-omission-audit-_gnke2gj`. Dos extracciones nuevas: arbol completo294 y reducido21. Se ejecutaron los tres bloques bash LITERALES del workflow, con stdout/stderr completos, en ambos arboles.

| Arbol | Bloque1 | Bloque2 | Bloque3 | Resultado |
| --- | --- | --- | --- | --- |
| Completo294 | exit0,52.037s | exit0,32.080s | exit0,27.154s |111 nombres de tests, todos ok |
| Reducido21 | exit0,50.724s | exit0,31.706s | exit0,27.536s |los mismos111 nombres y resultados |

Distribucion identica:21 clean_snapshot_sol,15 exact_http,15 access_policy,18 login_guards,10 isolated_session,18 demo_aislada,14 demo_restore. Se compararon nombres y resultados ordenados, NO solamente un conteo. No hubo skips en estas corridas. Coverage porcentual NO MEDIDO.

Un hook Python de auditoria registro `open`, `os.listdir` y `os.scandir`, heredado por subprocesos. Cada brazo produjo10623 eventos. En las trazas se observaron20 rutas versionadas: los20 archivos de runtime/tests conservados; el YAML se lee por el orquestador, fuera del proceso Python instrumentado. No se observaron aperturas de los267 omitidos ni de los seis workflows excluidos. No es un rastreador universal del sistema operativo: no cubre todos los stat ni toda E/S nativa. No se infiere ausencia en otros entornos o entradas.

Control adverso del hook: abrir README omitido, abrir version_text conservado, listar la raiz e intentar abrir un archivo inexistente. Registro los cuatro eventos; el proceso termino no-cero con FileNotFoundError. Un conjunto de eventos vacio no satisface ese control. Esta comprobacion valida discriminacion del capturador, no equivale a una prueba remota de GitHub.

Hashes de trazas originales completas, retenidas localmente:

- full-trace.jsonl: `9991fbee42056af3d4e64017de1c36bd29e62d6450bdd1de554807aa8c7a6f5d`.
- reduced-trace.jsonl: `e9886eeb56dd7abf68e12186fc4889805cd345c88206dee3e216c09186627240`.

**Custodia pendiente:** estos hashes no sustituyen a las trazas. El paquete `public-evidence.json` local contiene fuente del instrumento, comandos, stdout/stderr completos,267 rutas omitidas, controles y readback:62980 bytes SHA256 `d8a4b3a93734a0c381724f9de8504eb92c9580fc1586143bc81337b71de84699`. La proyeccion de eventos del repositorio tiene237118 bytes SHA256 `8702c288565c0588a67ef9598eb978b3058fdceed7cb66c2c4dc486666d96773`. No estan publicados completos con esta nota; no se presenta esta nota como recibo de merge ni como cumplimiento W-01 completo. Los resultados locales se informan como observados por BRAIN, con esta limitacion de verificabilidad externa explicita.

## El tamano del arbol no es el diff del PR

GitHub aplica `paths` a archivos CAMBIADOS en el diff de tres puntos, no a todos los archivos existentes. Fuente oficial consultada: https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions , seccion Git diff comparisons. No se usa un limite numerico de archivos como fundamento de esta conclusion.

Se construyeron cuatro commits locales sin historial importado. El diff documental es exactamente una ruta en ambos tamanos; el control de codigo tambien. El AST de clean_snapshot antes/despues del comentario coincide. Los267 omitidos no aparecen como267 borrados en los PRs: no existen desde sus bases comunes.

| Arbol | Probe | Base local | Head local | Diff exacto | Coincide con paths viejo |
| --- | --- | --- | --- | --- | --- |
| Completo | docs | ec950de8c15d89d634f019ceedc0793efc67e25a | d93008b113c6b16ed534f76ff5fc756a49eaa5f4 | docs/ci-trigger-probe.md | no |
| Completo | code | ec950de8c15d89d634f019ceedc0793efc67e25a | 69cdba456465fd9986eecb15a4c624fc66bc61d0 | pipeline/clean_snapshot.py | si |
| Reducido | docs | 28ca54975fb38f584785fd0e14f09e379178a36e | 6db8d4ab0feff45516562ab463df7b955b235a2a | docs/ci-trigger-probe.md | no |
| Reducido | code | 28ca54975fb38f584785fd0e14f09e379178a36e | c8359d9a4d62913bd01028bb6a03f8f0df385bd0 | pipeline/clean_snapshot.py | si |

Son objetos LOCALES; no se presentan como commits publicados ni URLs de GitHub.

## Lo que aun debe cerrar el ensayo remoto

Antes de cualquier evento: completar los21 archivos, comparar todos sus hashes, congelar bases, comprobar que old/new solo difieren en el bloque paths, comprobar diff acumulado de cada PR y activar captura externa. Mantener cuatro PRs, seis episodios maximo (opened de cuatro y synchronize de los dos documentales), controles positivos y ventanas de observacion acotadas. Ausencia sin control positivo es INCOMPLETO, no exito.

No se ensayan directivas skip, forks, conflictos, politicas de cuenta, ramas protegidas, Apps, hooks o todos los consumidores de Markdown. Se preserva la prohibicion de afirmar que Markdown es inerte. Los permisos y reglas del repo real se consultan nuevamente antes de un eventual merge.

## Hallazgo real durante esta consulta: inicializacion distinta de lo solicitado

Laboratorio creado publico, no fork, con autoInit=false: https://github.com/gatehot59-star/corpus-docs-trigger-lab . Al recuperar el estado se encontro `main` con un README.md VACIO en el commit raiz `0fa35d85569916c8525c490cfe854faee4a6fa14` (20:44:48UTC). El primer push de la rama experimental, `87ebfa88bdeb0dd2861f785e7876d06ec363f265`, es hijo de ese commit, un segundo despues. Los parametros de creacion/push no incluyeron ese README ni una rama main. La secuencia es consistente con inicializacion automatica del conector; no se inspecciono su implementacion, por lo que esa atribucion no es un hecho demostrado.

Estado recuperado: dos ramas, main y lab/docs-trigger-old-base. Default branch main. Rama experimental en `2480cbc16f7daf4cd41d018f591170e807a2e5e5`:10 originales copiados con SHA256 iguales, mas README vacio; faltan11 originales. API:0PRs y0runs al consultar. No se abrio ningun PR experimental, no se gasto ningun episodio experimental, no se toco el toggle Actions y no se mergeo PR21.

Esto no prueba que los267 omitidos invaliden el ensayo. Es OTRO desvio: conservando esa inicializacion, las bases tendrian22 archivos (21 originales+README) y el repo siete ramas totales (main+seis experimentales). Una constante identica fuera del diff no cambia por si sola la comparacion de paths, pero el laboratorio real todavia no coincide con el alcance aprobado. **Se detuvieron las escrituras del laboratorio al detectarlo.** No se borra README ni main sin autorizacion y no se amplia silenciosamente el alcance.

## Estado de entrega y errores propios

Analisis de alcance: conclusion condicionada respaldada por fuentes/diffs y observaciones locales. Experimento remoto: NO MEDIDO. Laboratorio: INCOMPLETO y con desvio de inicializacion. Custodia W-01 de la nueva comparacion: pendiente de publicacion integral. Merge: NO AUTORIZADO POR RESULTADO TODAVIA; la autorizacion humana condicional sigue vigente pero sus condiciones no se cumplieron.

Seis commits preparatorios fueron publicados con rubrica declarada parcial, no con scorecard terminado; esto es incumplimiento del requisito previo para el workflow inicial, no queda subsanado por esta nota. Tambien se reitero un intento fallido de creacion de archivo con ruta relativa que el adaptador rechazo; no afecto archivos remotos. No se agrega ninguna regla de trabajo ni se encarga la implementacion a auditores.
