# PR20: todos los enlaces directos del pase verificados

## Resultado y alcance

CONFIRMADO: 26 apariciones, 18 destinos únicos, todos resueltos al objeto y revisión previstos. Población completa: 13 enlaces del archivo canónico, 7 del Doc público y 6 del mensaje Nexus214. Son enlaces directos; no una recursión por todos los informes enlazados. Las rutas de evidencia escritas como texto no se cuentan como hipervínculos.

Captura GitHub: 20-sep-2026, 16:01:32 a 16:02:48 UTC (13:01 a 13:02 ART). Main inicial 8b8eabf4018331ef5052402dc1e5d1505fb802c7. PR20 sigue abierto y sin merge, head ca503377760a8dcd7965689a2853420785a83d94, base31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05. No se modificaron el pase, el producto, el PR ni el mensaje.

Fuentes de inventario: [pase canónico](https://github.com/gatehot59-star/corpus-legal-tarija/blob/92c833d13fe24e7bdb756e4cfc451678c6034e09/docs/agents/respuestas/2026-09-20-10-logout-review-handoff.md), [Doc público](https://app.clickup.com/90171457413/docs/2kza6fw5-13877), su [página](https://app.clickup.com/90171457413/docs/2kza6fw5-13877/2kza6fw5-16137), mensaje Nexus214 leído por su servicio. Markdown Git extraído mecánicamente; los siete href del Doc y seis URL del mensaje se cotejaron y transcribieron desde sus lecturas completas. Sin targets omitidos ni fallidos.

## Matriz exhaustiva de destinos

Prefijo GitHub en todas las rutas Git: https://github.com/gatehot59-star/corpus-legal-tarija/ . H = ca503377760a8dcd7965689a2853420785a83d94; F = 92c833d13fe24e7bdb756e4cfc451678c6034e09. Los 16 destinos GitHub devolvieron HTTP200 sin cambiar la URL de destino.

| # | Destino | Revisión/identidad comprobada |
| --- | --- | --- |
| 1 | pull/20 | Head H, base31dff1ed; abierto, no mergeado. URL mutable, verificada en esta captura. |
| 2 | compare/a8aeb301f8840caa547e48730a46e1b9406927bc...cc2ca30760c486cad3154c619a20f94cf75cc691 | Base y merge-base a8aeb301; último commit cc2ca307. Exactamente HTML y banco Chromium: el diff es el arreglo, no toda la pila del PR. |
| 3 | blob/H/sistema/web/discovery_spike.html | 13870 bytes; igual al HTML de cc2ca307. |
| 4 | blob/H/sistema/api/isolated_session.py | 3526 bytes; igual al de cc2ca307. |
| 5 | blob/H/sistema/api/demo_discovery.py | 13482 bytes; igual al de cc2ca307. |
| 6 | blob/H/tests/browser_discovery.cjs | 16114 bytes; banco actual, no el de 59 comprobaciones. |
| 7 | blob/H/.github/workflows/clean-snapshot.yml | 4288 bytes; workflow que ejecuta el banco, igual al de cc2ca307. |
| 8 | blob/F/docs/agents/respuestas/2026-09-20-02-logout-retry.md | 7950 bytes; idéntico al publicado en620994f76be2bdfacfad86680102bedd515a8871; sujeto cc2ca307. |
| 9 | blob/F/docs/auditorias/2026-09-20-03-pr20-logout-fix-audit.md | 10561 bytes; idéntico a f3440c16f6d3b65937c66fc44a89774cc6e69cb8; sujeto cc2ca307. |
| 10 | blob/F/docs/auditorias/2026-09-20-04-delayed-logout-navigation.md | 8613 bytes; idéntico a ee97fa4a9b9a2f73af6815ad0babd28c049ad2ff; sujeto cc2ca307. |
| 11 | blob/F/docs/auditorias/2026-09-20-05-bfcache-pending-logout.md | 7774 bytes; idéntico a d76ec10c365e568bd890c1fdea43a399ef350a36; sujeto cc2ca307. |
| 12 | blob/F/docs/agents/respuestas/2026-09-20-09-selection-ci.md | 6087 bytes; idéntico a4a30db151e5f367850b2b7627c4d5b487c29eb78; sujeto H. |
| 13 | actions/runs/35515778571/job/106091355198 | Job pertenece al run indicado; ambos tienen head H; success; workflow clean-snapshot.yml. No se descargó stdout de Actions. |
| 14 | blob/F/docs/agents/respuestas/2026-09-20-10-logout-review-handoff.md | 10408 bytes; archivo previsto, igual al main consultado. |
| 15 | blob/fea377f66b806543b91bf76bd2db84a6ccfd6d81/docs/agents/respuestas/2026-09-20-10-logout-review-handoff/custody.json | 1936 bytes; custodia de ese informe, no otra entrega. |
| 16 | blob/29f393570c72cc65dd43747af6ffb18f3745de88/docs/auditorias/2026-09-20-11-audit-astra-brain.md | 12399 bytes; contraauditoría histórica correcta. Las erratas que enumera se corrigieron después: no confundir historia con bugs aún abiertos. |
| 17 | https://app.clickup.com/90171457413/docs/2kza6fw5-13877 | Doc view:2kza6fw5-13877, título PR20: pase focalizado de logout para revisión por otro autor. |
| 18 | https://app.clickup.com/90171457413/docs/2kza6fw5-13877/2kza6fw5-16137 | Página doc:2kza6fw5-16137; parent view:2kza6fw5-13877, mismo pase y head H. |

Los 13 blobs se recuperaron también por raw.githubusercontent.com y se compararon byte por byte con los objetos Git de sus refs. Los ocho blobs documentales coinciden además con main al consultar. Los cinco enlaces relativos del pase heredan F al abrir el permalink: no saltan silenciosamente a main; abrir el pase desde main sí los vuelve móviles, aunque hoy sus bytes coinciden.

ClickUp no ofrece aquí un permalink a una revisión inmutable: sus dos enlaces resuelven el Doc y su página actuales, con el head correcto escrito y el permalink Git correcto. No afirmar que el Doc quedó congelado por tener un enlace válido.

## Instrumento, controles y error propio

HTTP real desde brain-env, API pública GitHub para PR/compare/run/job, objetos Git obtenidos por fetch explícito, y conectores ClickUp/Nexus para esas fuentes. La identidad de revisión se comprueba además del estado HTTP. No se inició un runner CI ni Chromium.

Control positivo: el HTML H recuperado tiene SHA256 69eba91fcf88b5c0547e263276cfc1a9f0da2703b91a1601397e8fffb0b5efdb. Control adverso: HTML anterior a8aeb301 devuelve200 pero SHA d8fd920aed755de18cbbc29c8ad791547fb82004f8e1c1d729e5cfad834de7c4: la comparación discrimina revisión vieja. Ruta deliberadamente inexistente en H devuelve404. No son defectos de producto.

Error auxiliar conservado: el selector inicial buscaba '-09-' para distinguir el informe09, pero también coincidía con septiembre en todos los nombres. Indicó falsamente que02-05 no nombraban el sujeto esperado. La igualdad de bytes nunca falló. Corregido mediante nombre de archivo exacto:02-05 nombran cc2ca307,09 nombra ca503377. No se modificó ningún enlace para obtener el resultado. Preparación local: prefijos '+' del transporte normalizados antes de compilar; ajuste de ruta API antes de ejecutar. El verificador terminó exit0.

## Evidencia y límites

Paquete hermano `2026-09-20-13-handoff-links/evidence.xz.b64`: base64 de xz, JSON decodificado56331bytes, SHA256 94a8171aaa03e51355beb1e3079ba536d2243650823dd05710df836b4cdb729c. Conserva resultados estructurados completos por destino,26ocurrencias,18targets,fuente ejecutada,stdout/stderr completos,control de orígenes inicial/corregido y recibo de observaciones ClickUp. Excluye cuerpos HTML y objetos API completos; no se llama captura íntegra de todo HTTP. Los PENDING_CONNECTOR del runner se resuelven por el recibo ClickUp separado, no por simular HTTP sobre sus URLs.

Qué no se midió que importaba: no se probó de nuevo logout, ni acceso anónimo a ClickUp, ni todos los enlaces recursivos de los informes citados. Validar estas rutas no cierra G2 ni equivale a review externo. Los textos 'no enviado' del pase reflejan su creación; Nexus214 acredita un envío posterior, no una revisión terminada. Ninguno de esos matices es una revisión equivocada en el enlace.

Modo TITAN LIGERO. Gate I PASA para comprobación documental por HTTP/Git y controles; pruebas nuevas de producto N/A. Gate II PASA con población explícita, distinción histórico/actual, error propio y límites. Gate III se completa con readback remoto del informe/evidencia, pertenencia a main, Doc público leído y continuidad Nexus. Rúbrica numérica N/A. Sin modificaciones del material revisado, mensajes, asignaciones, merge ni despliegue.
