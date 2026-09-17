# PR6: ancestros ocultos/inactivos rechazados sin cambiar el resultado de tres fuentes reales

Pedido de Abraham: arreglar manejo de ancestros ocultos dePR5 con regresiones. Implementación propia autorizada,no auditoría independiente. [PR6](https://github.com/gatehot59-star/corpus-legal-tarija/pull/6),rama titan/fix-b04-hidden-ancestors apilada sobrePR5. Baseee8e5c24bc3dff91d03149928e87c30a88fd56c5,código74a6e8d3e99cee8e35476c720a87d253baaa038b. No cambia la rama deBrain,manifiestos,UID,texto vivo,producción ni permisos. Sinmerge/deploy.

## Qué cambia

`pipeline/legal_html.py` rastrea ancestros externos antes de abrirdiv#normTxtId. Rechaza contexto conhidden,aria-hidden=true normalizado,display:none/visibility:hidden explícitos einert; también template,noscript,textarea,title yatributos duplicados. Usa el mismo predicado de atributos para raíz,descendientes yancestros. Inert/aria-hidden no se presentan como idénticos a invisibilidad visual: se rechazan conservadoramente como contexto no apto sin revisión.

Los hermanos ya cerrados yelementos void no contaminan el cuerpo siguiente. Profundidad de contexto limitada a128. Etiquetas no-void autocerradas fuera delcuerpo se rechazan por ambigüedad HTML/XHTML; aceptar <section hidden/> como hermano vacío podía ignorar elcontexto que un navegadorHTML mantendría abierto. No se intenta adivinar estilos calculados.

## Regresiones

`tests/test_legal_html.py` pasa de20a29métodos. Nuevos: ancestro oculto en varias formas; contexto inactivo; ancestros visibles preservan text/HTML; hermanos hidden/template cerrados; sibling void; nonvoid autocerrado ambiguo; atributos duplicados;profundidad exterior;CLI rechazada no crea destino ni altera fuente.

Mismo test publicado contra ambos módulos:

```text
new python3 tests/test_legal_html.py
Ran 29 tests in 0.481s
OK
exit0

old python3 tests/test_legal_html.py
Ran 29 tests in 0.505s
FAILED (failures=12)
exit1
```

Los12son fallos de aserción incluyendo subtests,no12métodos. Los controles visibles/hermanos cerrados pasan también conelviejo. Se mantiene elbanco anterior de4mutaciones:baseline0,mutantesrechazados. No se inventa independencia jurídica a partir del parser.

## Tres HTML reales: mismo input yresultado completo idéntico

Se reutilizaron los bytes fijados en la revisión inmediata anterior, no una descarga distinta para cada brazo. Candidato publicado yextractorPR5 corrieron sobre los mismos bytes. Resultado completo Python igual,incluyendo texto,HTML,hashes,estructura yspan; no solo igualdad de largos.

| Fuente | SHA256 original | Caracteres | Resultado completo igual | Flujo no blanco con BeautifulSoup |
| --- | --- | ---: | --- | --- |
| Familia histórico |d91e5f640046f408a7f0870d6f71cd86b9b01429f0d1e8c141eda47b698a06ff|195893|sí|sí|
| Comercio |ea76821146aa9b5697c950bb511200bd61fc208820d72b4c8547287ce4b6cc42|693914|sí|sí|
| CPE2009 |c6f3d32f52c5f21dc54263f4ec99d677ac14bd4d8df2e9271502202fd8b31f74|263357|sí|sí|

Fuentes: [Familia](https://www.lexivox.org/norms/BO-COD-DL10426.xhtml),[Comercio](https://www.lexivox.org/norms/BO-COD-DL14379.xhtml),[CPE](https://www.lexivox.org/norms/BO-CPE-20090207.xhtml). Título observado para medir preservación,no verificación externa deidentidad/aplicabilidad. BeautifulSoupcomparador auxiliar ya disponible,no dependencia delproducto.

## CI ycompatibilidad

[CI preservation del código](https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35223341537/job/105208647231):completed/success,12:49:37Z–12:49:43Z. Workflowlegal-html.yml heredado ya incluye ambos paths yejecuta tests/mutantes. No se cambióworkflow,dependencia,contratoJSON ni guard deoverwrite. Copilot solicitado;hastaque emita review no es aprobación.

## Límites yriesgo de adopción

Es un extractor delperfil observado,no unparserHTML5 denavegador,unmotorCSS/JS niunXSSsanitizer. No resuelve classes/stylesheets/mediaqueries,reglasCSS que anulen ancestros,layout orecuperación completa deHTMLmalformado. Algunos contextos reciben rechazo conservador aunque pudieran usarse tras revisión. ElHTMLoriginal sigue sin sanitizar,safe_to_render_html=false. No presentar elfix como garantía universal de visibilidad.

La condición de salida exige revisión de otras plantillas si dejan de ser aceptadas. No se cambian hashes reales ni relabelan manifests para tolerar nuevo texto. No tocócorrectivosOCR,Ley483,vigencia,auth/membresía ni publicación.

## Custodia yQA

Fuente publicada descargada por revisión exacta antes de medir. Companion `docs/agents/evidencia/2026-09-17-10-hidden-ancestors.json` contieneJSONcompleto de logs nuevo/viejo/mutantes ycomparación real, comprimido sin pérdida. SHA256 de los bytes descomprimidos384f0bfcf91ba4f293fea6900f7141eec7f6637b0b805a5442e1e69db1cf3920. Cotejar retornodesdeGit antes delcierre. Local `/workspace/sol-fix-hidden-20260917/published-results.json`.

La primera fixture tuvo comillas transportadas incorrectamente:SyntaxError,se corrigió antesdepublicar,no se contó comoprueba. Otro primer planteo aceptaba nonvoidautocerrado como hermano,se endureció antesdelcommitpara evitar interpretación insegura. Erroresregistrados,no presentados comofallas delentorno.

Rúbrica módulo82/90=91,1/100:Completitud14,Ejecutabilidad15,Seguridad13,Testing14,Arquitectura9,Documentación9,Innovación4,Proceso4;DevOps10N/A. Descuentos por no medir cobertura formal,modeloHTML5/CSSfuera decontrato yreviewexterna pendiente. No aprobaciónintegral deproducto ni porcentajeavance.

NO MEDIDO:completitudlegal,otrasfuentes,CSS/navegadorcompleto,coverageformal,performance10x,producción/merge. Builder/Security/Tester actuaron sobre cambioacotado delmismo ejecutor,no auditoríaindependiente. La entrega está enPR para revisión;no se firmó release.
