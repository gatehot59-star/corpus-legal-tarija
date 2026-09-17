# PR6 se puede saltear con cierres cruzados: Chromium conserva el ancestro que el extractor borra

17-sep-2026. Abraham pidió intentar bypass con markup malformado. Prueba adversarial **de mi propio fix**, no auditoría independiente. PR6 abierto, head452a75678d5e8160ee62dd8829f9b85fb6f4a072, módulo pipeline/legal_html.py SHA256867444ece1574270d97c6dfbd2fee3674a82711563d8dc9b0e6db1d9312ea1e0. No cambié código ni PR, no merge/deploy ni corpus real.

## Veredicto

**Bypass confirmado de la selección de ancestros: tres HTML sintéticos son aceptados por PR6 mientras Chromium los conserva bajo hidden o dentro de template.** Los29tests del head siguen pasando. La evidencia es una discrepancia real de parsing, no solo una interpretación mía de las etiquetas.

No demuestra XSS, acceso a información ajena ni corrupción de las tres fuentes reales revisadas antes. PR6 ya excluía ser un parserHTML5 completo: esa limitación era honesta, pero su recuperación permisiva de cierres externos permite precisamente el contexto oculto que intentaba rechazar. El remedio acotado puede ser rechazar ambigüedad, no implementar un navegador.

## Inputs y resultado

Cuerpo común exacto:

```html
<div id="normTxtId"><h1>Ley sintetica 1</h1><p>No pagar 390000.</p></div>
```

Para cada input, el SHA esperado se calculó sobre esos mismos bytes yel título fue Ley sintetica 1. No se intentó falsificar elhash ni untítulo incorrecto; estas comprobaciones no resuelven la diferencia deárbol.

| Caso | Envoltorio antes/después del cuerpo | PR6 | Chromium DOMParser text/html |
| --- | --- | --- | --- |
| visible | ninguno | acepta | cuerpo en documento,sin ancestrohidden |
| hidden_balanced | `<div hidden>` / `</div>` | rechaza | cuerpo bajoDIVhidden |
| cross_table | `<div hidden><table></div>` / `</table></div>` | **acepta** | cuerpo todavía bajoDIVhidden;table reubicada como hermana |
| cross_template | `<div hidden><template></div>` / `</template></div>` | **acepta** | objetivo dentrotemplate.content,no enárboldocumentoprincipal |
| closed_hidden_sibling | `<div hidden>otro</div>` / nada | acepta | cuerpo sinancestrohidden |
| cross_object | `<div hidden><object></div>` / `</object></div>` | **acepta** | cuerpo dentroOBJECT,bajoDIVhidden |

Los tres casos aceptados indebidamente emiten:

```text
Ley sintetica 1
No pagar 390000.
```

## Causa exacta

En `LegalParser.handle_endtag`, fuera del cuerpo, se busca hacia atrás cualquier ancestro delmismo nombre yse ejecuta:

```python
if self.ancestors[index][0] == tag:
    del self.ancestors[index:]
    break
```

Con pila `[div(hidden), table]`, el `</div>` elimina **ambos**, aunque no cerraba elúltimo elemento abierto. Al llegar anormTxtId, ya no hay ancestros ocultos que revisar. El mismo mecanismo descarta template uobject.

Chromium aplica reglas de alcance yrecuperación HTML distintas: ignora ointerpreta ese cierre sin liberar alobjetivo delcontexto hidden/template. El instrumento midió suárbol, no lo dedujo delstring. Los controles visible,hiddenbalanceado yhermanocerrado descartan uncomparador quesiempre marque oculto ounextractor quesiempreacepte.

## Pruebas y comparador

1. Descarga exacta delmódulo porheadPR6, hasharriba,importación sin modificar.
2. Seiscasos sintéticos ejecutados enbrain-env con `extract(raw,sha256(raw),title)`.
3. Mismosseisstrings analizados con `new DOMParser().parseFromString(html,'text/html')` en HeadlessChrome140.0.0.0 porgatewayplaywright. Documentosdesconectados enabout:blank; no ejecución descripts,nopeticionesexternas,ningún dato real.
4. Inspección `querySelector('#normTxtId')`, ancestros `[hidden]`, contenido de `template.content` yserializaciónbody íntegra.
5. Banco publicado `python3 tests/test_legal_html.py`:29tests,0.459s,OK,exit0. No hubo nuevoCI ni cambio delproducto.

No se evaluó geometría depíxeles,estilos externos ni todaslasreglasHTML5. La confirmación es estructuraHTMLdelnavegador yatributohidden explícito/inactividadtemplate. No extrapolar acomportamientoCSSuniversal.

## Cambio recomendado, no aplicado

Antes deseleccionar normTxtId, un cierre externo que cruce elementos abiertos debería producir rechazo explícito envezde borrar elcontexto. Agregar fixtures paratable/template/object ycontroleshermanos/visible. Conservar elestado decontextoinactivo hastacierre inequívoco. Probar otrosescapes porrecuperación delparser concomparadorHTML5 yreverificar lastresfuentesreales paraevitar rechazo nointencional.

Esto no garantiza eliminar toda divergenciaHTML5; es una corrección puntual medible. Si se decide tolerancia general deHTMLmalformado,hace falta definir modelo deparsing compatible, no acumular excepciones de texto. No sanitizar ni renderizar HTML como solución alproblemade selección.

## Evidencia y límites

Companion JSON conserva los6inputs exactos,resultadosPR6 ysalidaDOMParser conárboles/ancestros. Los resultadosPython originales en `/workspace/pr6-malformed-20260917/extractor.json`; banco completo enbaseline.json. La evidencia publicada separa logs completos decasos/browser delresumen delbanco29tests.

NO MEDIDO: fuentesreales nuevas,producción,explotación remota,rendimientofuzzingmasivo,CSS/renderingcompleto,otrosnavegadores. No se cambia elfix durante un pedido deataque. No hay firma independiente deoperador; sí comparadorChromiumexterno alparser ysalidarecomputable.

TITANFULL,QAinforme41/45:completitud14/15 (seiscasos,noexhaustivo),razonamiento9/10 (DOMnoequivale apíxeles),documentación9/10 (inputs/salidas/comandos),aporte5/5 (diferencialparser),proceso4/5 (autoataquedeclarado). N/A55deproducto. No se usa nota paraaprob arPR6: **requiere corrección antes de considerar cerrado elrechazo deancestros malformados.**

Archivos: docs/auditorias/2026-09-17-11-pr6-cierres-cruzados.md y docs/auditorias/2026-09-17-11-pr6-cierres-cruzados.json.
