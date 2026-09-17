# TITAN FULL · Plan integral para culminar Corpus Tarija v1

17 de septiembre de 2026. Pedido de Abraham: explorar arte actual y repositorios reutilizables, fuentes bolivianas y tarijeñas, prioridades de abogados/docentes/estudiantes, capacidades y entorno; entregar el plan íntegro antes de construir.

## Veredicto: terminar una versión mantenible, no una descarga infinita

**Culminar significa permitir encontrar, verificar, guardar y compartir investigación jurídica con cobertura declarada, sin confundir historia con vigencia ni exponer datos sensibles.** El plan distingue v1 para piloto, v1 comercial y expansión permanente. No promete cada ley del país ni transforma un piloto gratuito en demanda comercial demostrada.

Precio objetivo: **US$10**; mensual por persona es supuesto de cálculo pendiente de confirmación. Primera compra y renovación son pruebas distintas. Propuesta: preservar Python/SQLite FTS5, adaptadores y frontend; añadir una sola frontera de cuentas con Django, colecciones, reportes y membresía. No importar una plataforma grande de RAG, un LMS o un gestor de expedientes.

**Planificación, no implementación:** no se fusionó PR, desplegó, instaló dependencia, cambió credenciales, contrató infraestructura, contactó instituciones ni creó un lote de tareas. Roles humanos son necesidades pendientes, no personas contratadas. La publicación del plan no autoriza esas acciones.

## 1. Estado real y trabajo que se conserva

Main leído: `b7e1066edff59782116ac770f352cc85f53402d0`. PR1 abierto: `2360f27d43fdc9a1e2a74a3f6465698918df2ad1`. Rama de paginación/decretos: `84358cc821490cd90e31cb3f049ef7e691ccc4da`. No se cotejó el servicio desplegado con esas revisiones.

| Activo | Reusar | No dar por terminado |
| --- | --- | --- |
| Main | Buscador FTS5/BM25, frontend, filtros, API, OpenAPI y manifiesto para agentes | Relevancia con usuarios, concurrencia, cuentas/membresía |
| Pipeline | OCR, variantes de citas, revisión y pruebas existentes | Fidelidad jurídica integral; un comentario no sustituye un control |
| PR1 | Alias/procedencias, censo, ingesta nacional y frontera | Integración, despliegue y seguridad del head completo |
| Rama paginación | Permalinks y extracción real de decretos/anexos | Cierre de extracción, reconciliación y publicación |
| Nacional | Manifest de15 entradas | Archivos servidos, integridad y versiones actuales |
| Seguridad documentada | Cierre público, informes posteriores de login/loopback y rotación Gitea | Estado actual de todas las rutas, sesiones y archivos |

El [manifest nacional](https://github.com/gatehot59-star/corpus-legal-tarija/blob/2360f27d43fdc9a1e2a74a3f6465698918df2ad1/indices/nacional-normas.jsonl) incluye Código de Familia1972 y no Ley603. [SILEP identifica Ley603 de19/11/2014 como Código de las Familias y del Proceso Familiar, vigente con modificaciones](http://www.silep.gob.bo/norma/13366/ley_actualizada). Conservar historia, completar régimen actual y relaciones; no vender «tenemos código de familia» como cobertura actual.

El [lector nacional](https://github.com/gatehot59-star/corpus-legal-tarija/blob/2360f27d43fdc9a1e2a74a3f6465698918df2ad1/sistema/api/fuente_nacional.py) aceptó texto sintético alterado con hash distinto en el ensayo previo: [salida cruda](https://github.com/gatehot59-star/corpus-legal-tarija/blob/b7e1066edff59782116ac770f352cc85f53402d0/mediciones/2026-09-16-20-hash-nacional.json). Es defecto de esa clase, no prueba de corrupción productiva. Los412 números de artículo atribuidos a CPE por regex no están validados jurídicamente.

La [auditoría de decretos](https://github.com/gatehot59-star/corpus-legal-tarija/blob/84358cc821490cd90e31cb3f049ef7e691ccc4da/sistema/evidencia/2026-09-04-11-el-catalogo-miente-sobre-5-decretos.md) documenta discrepancias catálogo/PDF y anexos legítimos. Recuperar ese trabajo antes de repetir descargas. Número+año no es clave única de cuerpo y anexos.

Custos sigue separado:24 checks HTTP PostgreSQL16/17 verifican su núcleo, no el corpus. Cuentas del corpus no son tenants de bufetes ni autorizan cargar expedientes. El snapshot histórico6.079 no es un inventario de hoy; no sumar pasajes, PDFs, normas, anexos y procedencias como una unidad.

## 2. Capacidades y entorno leídos y remidos

Se leyeron completos [00-ENTORNOS-Y-CAPACIDADES.md](https://github.com/gatehot59-star/mudh-mobile/blob/5dda974cc355e50d79162bfeca61540fe0ce0f21/00-ENTORNOS-Y-CAPACIDADES.md) y [CONTEXTO-ENTORNO.md](https://github.com/gatehot59-star/drosophila-fep-connectome/blob/08b3b01bc0a6c678ae09fe6adeabadfe6cd94b63/docs/agents/CONTEXTO-ENTORNO.md). No se localizó el literal `ENTORNO.MD` en búsqueda parcial; no traté el autolink como sitio externo ni afirmo que sea otro archivo. Estos son los documentos canónicos encontrados.

El contexto antiguo niega git/gcc; correcciones posteriores y medición nueva lo contradicen. No se reescribieron inventarios de otros proyectos.

**Medido17-sep03:21UTC por gateway build.run en brain-env:**2CPU, uid1000, Python3.12.14, SQLite3.46.1,117,82GiB libres, MemAvailable2632136kB. FTS5 ejecutó búsqueda positiva1/negativa0. Git/gcc/node/npm encontrados en PATH; docker/tesseract/pdftotext no, lo que no prueba imposibilidad ni ausencia fuera de PATH. Nada instalado.

| Entorno | Trabajo propuesto | Límite de evidencia |
| --- | --- | --- |
| brain-env | Recuperar trabajos, censos pequeños, parsers/tests/SQLite | Medición nueva;2CPU compartidas, no VM productiva |
| Actions hosted x64 | Build limpio, navegador, OCR por lotes autorizados | Capacidad histórica/inventario; no nuevo job ni garantía de cuota actual |
| Self-hosted | Solo con decisión explícita | Puede ser el mismo brain-env; verificar runs-on, no contarlo como otra máquina |
| Kaggle | Embeddings opcionales si benchmark los justifica | Servicio listado; GPU/sesión/cuota actuales NO MEDIDOS; fuera de ruta crítica |
| VM corpus | Servicio de snapshots y cuentas, sin OCR pesado | Capacidad/despliegue/restore actuales a medir en A01/F05 |
| Sandbox auxiliar | Validación del plan y estimaciones | Máquina distinta, sin internet; no es brain-env |

No hace falta comprar VPS/GPU para empezar. Tampoco se promete capacidad productiva sin medir. Material sensible, bases de cuentas y secretos nunca entran en logs/artifacts/repos públicos.

## 3. Prioridad tarijeña: hipótesis respaldada, no ranking inventado

No se encontró tabla pública reciente comparable de causas por materia para todo Tarija. El orden se basa en utilidad, riesgo y tareas, **no volumen estadístico de litigios**. No mezclar noticias, matrícula y cargas de2019.

| Prioridad | Necesidad | Evidencia | Decisión |
| --- | --- | --- | --- |
| Transversal | Identificar/citar/guardar fuentes | [UAJMS Derecho](https://www.uajms.edu.bo/oferta-academica/carrera-de-derecho/), [UPDS Tarija](https://www.upds.edu.bo/carrera/derecho-tarija/): investigación, TIC, LegalTech y práctica | Citas, móvil, colecciones desde piloto |
| Familia/niñez/violencia | Asistencia familiar, protección y debido proceso | [TDJ asistencia](https://tarija-tdj.organojudicial.gob.bo/Paper/Detail/10340), [TSJ siete jueces2024](https://tsj.bo/juramento-y-posesion-de-siete-jueces-con-ampliacion-de-competencias-en-materia-penal-refuerza-sistema-judicial-en-tarija/) |603/548/348 y procedimiento; privacidad antes de difundir fallos |
| Civil/propiedad | Contratos, propiedad, ejecución | [TDJ embargos](https://tarija-tdj.organojudicial.gob.bo/Paper/Detail/10356), [GAMT servicios](https://www.tarija.bo/servicios-digitales01/) | Civil/CPC y muestra local; guía de trámite no equivale a norma |
| Laboral | Despido, salarios, seguridad social, trabajo rural | [TDJ-UAJMS](https://tarija-tdj.organojudicial.gob.bo/Paper/Detail/10360), [Defensoría zafra Bermejo](https://www.defensoria.gob.bo/uploads/files/informe-defensorial-sobre-verificacion-a-la-zafra-de-la-cana-de-azucar-en-el-municipio-de-bermejo-tarija.pdf) | LGT, reglamentos necesarios y procesal laboral |
| Agrario/ambiental/autonómico | Tierra, competencia y usos del suelo | [INRA](https://www.inra.gob.bo/normativa-agraria/), [Agroambiental](https://arbol.tribunalagroambiental.bo/), [PLUS Tarija](https://www.tarija.gob.bo/gestion-transparente/planes-estrategicos?download=1291%3Aplan-de-uso-del-suelo-del-departamento-de-tarija) | Módulo pequeño desde piloto, conservando mapas/anexos |
| Especialización posterior | Tributario/frontera/hidrocarburos/minería | Fuentes §4 y currículo UPDS | Catálogo e instrumentos concretos; ampliar por consultas reales |

Antes de congelar cobertura: seis entrevistas de tareas con abogados, cuatro con docentes y seis con estudiantes, participación voluntaria. Observar última investigación, fuente, tiempo y error costoso sin pedir expedientes; datos ficticios o anonimizados. El valor es tiempo hasta verificar, no rapidez de respuesta.

## 4. Bibliotecas: alcance v1 y mapa de expansión

### Núcleo nacional:24 identidades a reconciliar

Semilla de aceptación, no declaración de vigencia consolidada ni de faltantes:

1. Constitución Política del Estado.
2. Código Civil.
3. Código Penal.
4. Código Procesal Civil, Ley439.
5. Código de Procedimiento Penal, Ley1970.
6. Código de las Familias y del Proceso Familiar, Ley603.
7. Código de Comercio.
8. Código Tributario, Ley2492.
9. Código Niña, Niño y Adolescente, Ley548.
10. Código Procesal Constitucional, Ley254.
11. Ley General del Trabajo.
12. Código Procesal del Trabajo.
13. Ley1178, administración y control gubernamentales.
14. Ley025, Órgano Judicial.
15. Ley031, autonomías.
16. Ley348, vida libre de violencia.
17. Ley1173, abreviación procesal penal.
18. Ley1715, reforma agraria.
19. Ley3545, reconducción comunitaria.
20. Ley477, avasallamiento y tráfico de tierras.
21. Ley482, gobiernos municipales.
22. Ley2341, procedimiento administrativo.
23. Ley1700, forestal.
24. Ley1333, medio ambiente.

Añadir modificatorias/reglamentarias necesarias para cada tarea de evaluación. Una ley base no acredita materia completa. Cambios de cantidad se registran con costo; historia conserva etiqueta/fecha/relación.

### Selección mínima del piloto

Propuesta a validar:24 identidades troncales,20 instrumentos departamentales/locales,30 decisiones TSJ/TCP/Agroambiental y10 lecturas propias/autorizadas. **84 unidades editoriales, no84PDFs ni total del corpus**. Anexos/reformas añaden unidades. No reducir material ya validado a84; lo pendiente queda en catálogo/cuarentena, no desaparece.

Niveles de publicación: catálogo, texto aprobado, histórico, restringido. Ningún faltante se rellena por inferencia.

| Familia | Fuentes de entrada verificadas | Adquisición y condición |
| --- | --- | --- |
| Nacional | [Gaceta avanzada](http://www.gacetaoficialdebolivia.gob.bo/normas/busquedaAvanzada), [CPE PDF](http://www.gacetaoficialdebolivia.gob.bo/app/webroot/archivos/CONSTITUCION.pdf), [SILEP](http://www.silep.gob.bo/) | HTML/PDF; SILEP ayuda con versiones, Gaceta referencia definitiva |
| Tarija legislativo/ejecutivo | [Leyes](https://www.tarija.gob.bo/gaceta-oficial/leyes-departamentales), [decretos](https://www.tarija.gob.bo/gaceta-oficial/decretos-departamentales), [estatuto](https://www.tarija.gob.bo/gaceta-oficial/estatuto-autonomico-departamental) | Recuperar extracción; cuerpo/anexos contra sello, no solo catálogo |
| Gran Chaco | [Gaceta](https://granchaco.gob.bo/gaceta/), [estatuto](https://granchaco.gob.bo/download/60/marco-legal-de-dtlc/2684/estatuto-regional-del-gran_chaco.pdf) | Separar competencias regional/municipal y fechas |
| Tarija municipal | [Decretos](https://www.tarija.bo/decretos-municipales/), [ediles](https://www.tarija.bo/decretos-ediles/), [Ley328 Concejo](https://www.concejotarija.bo/storage/files/8/LEYES%202023/Ley%20Municipal%20328.PDF) | Norma distinta de noticia/trámite; PDF semilla no acredita serie |
| Yacuiba/Villa Montes | [Ley25/2024](http://www.concejomunicipalyacuiba.gob.bo/assets/gaceta/1762530899), [índice Villa Montes](https://www.gamvm.gob.bo/leyes-municipales/) | Censo IDs/fechas, revisar OCR/anexos |
| Resto municipal | [Bermejo](https://gambermejo.gob.bo/), [referencia territorial OEP](https://web.oep.org.bo/wp-content/uploads/2021/02/Que-elegiremos-Tarija.pdf) | Matriz Tarija,Yacuiba,Villa Montes,Caraparí,Bermejo,Padcaya,Entre Ríos,San Lorenzo,El Puente,Uriondo,Yunchará. Catálogos completos no localizados para todos; buscar Concejo/Ejecutivo y solicitar con autorización |
| Ordinaria | [GENESIS](https://genesis.tsj.bo/resoluciones), [TSJ resúmenes](https://tsj.bo/tipo_publicacion/resumenes-de-jurisprudencia/) | Gestiones/salas/IDs, fallo separado de ficha; privacidad |
| Constitucional | [TCP jurisprudencia](https://jurisprudencia.tcpbolivia.bo/), [resoluciones](https://buscador.tcpbolivia.bo/) | Ratio/precedente y resolución separados |
| Agrario/ambiental | [INRA](https://www.inra.gob.bo/normativa-agraria/), [Agroambiental](https://arbol.tribunalagroambiental.bo/), [ABT](https://abt.gob.bo/index.php/institucion/marco-legal/normas-generales) | Compendio2023 no cubre todas las novedades; conservar cartografía |
| Laboral | [MTEPS SST](https://mintrabajo.gob.bo/index.php/normas-tecnicas-de-sst/), [OVT](https://ovt.mintrabajo.gob.bo/soporte/recursos/Manual%20de%20Planillas%20Mensuales.pdf) | SST/manual no son todo laboral; separar guía/norma |
| Tributario/aduanero | [SIN RND](https://www.impuestos.gob.bo/index.php/rnd-2026/), [Aduana](https://www.aduana.gob.bo/normativa-vigente), [circulares](https://www.aduana.gob.bo/NOR_circulares) | Temporalidad, reemplazos y fecha de efecto |
| Hidrocarburos/minería | [ANH](https://www.anh.gob.bo/w2019/contenido.php?s=54), [AJAM](https://www.autoridadminera.gob.bo/), [Minería](https://mineria.gob.bo/) | Selección por tarea, no expedientes/catastro como normativa |
| DDHH/internacional | [OEA Convención](https://www.oas.org/dil/esp/tratados_b-32_convencion_americana_sobre_derechos_humanos.htm), [ratificaciones Bolivia](https://www.oas.org/dil/esp/tratados_firmas_ratificaciones_estados_miembros_bolivia.htm), [OHCHR](https://tbinternet.ohchr.org/_layouts/TreatyBodyExternal/Treaty.aspx?CountryID=21&Lang=EN) | Texto, ratificación, reservas/protocolos; no inferir aplicabilidad temática |
| Doctrina | [UAJMS Tribuna](https://dicyt.uajms.edu.bo/revistas/index.php/tribuna-juridica/issue/archive), [biblioteca TSJ](https://tsj.bo/servicios-judiciales/biblioteca/), [UCB licencia](https://lawreview.ucb.edu.bo/a/copyright-policy) | Catálogo/enlaces y materiales autorizados; no CC-NC comercial por defecto |

“Todo Bolivia” se organiza como catálogo de familias/competencias y adquisición progresiva; no afirmo lectura de cada norma/portal. Registro por fuente:URL,tipo de acceso,condiciones/licencia,censo,frecuencia propuesta,última consulta,responsable. HTTP sin TLS y sitios dinámicos requieren revisión/controles, no bypass.

## 5. Arte actual: reciclar componentes, no promesas

Repositorios/licencias/metadatos/código seleccionado fueron abiertos. Licencia de software no licencia los datos. Versiones son candidatas al17-sep, no lock instalado ni certificación CVE.

| Candidato | Evidencia/licencia | Decisión |
| --- | --- | --- |
| pypdf6.19.0 | [pyproject](https://github.com/py-pdf/pypdf/blob/6.19.0/pyproject.toml), BSD | PDF nativo, no OCR; comparar con extractor existente |
| Tesseract5.5.3 | [tag](https://github.com/tesseract-ocr/tesseract/tree/5.5.3), Apache | Reusar motor como proceso, registrar traineddata/idioma |
| OCRmyPDF17.12.1 | [api.py](https://github.com/ocrmypdf/OCRmyPDF/blob/v17.12.1/src/ocrmypdf/api.py), MPL | Worker opcional, no reemplazo automático; dependencias externas separadas; Ghostscript no incondicional en v17 |
| Trafilatura2.2.0 | [pyproject](https://github.com/adbar/trafilatura/blob/v2.2.0/pyproject.toml), Apache | Comparador/fallback HTML; selector por fuente y tablas jurídicas mandan |
| Django5.2.17 LTS | [versiones](https://www.djangoproject.com/download/), [auth](https://github.com/django/django/tree/5.2.17/django/contrib/auth), BSD | Cuentas/admin/CSRF/sesiones; una frontera y adapter legacy, no login casero |
| Playwright1.63.0/axe4.13.0 | [Playwright](https://github.com/microsoft/playwright-python/tree/v1.63.0), [axe](https://github.com/dequelabs/axe-core/tree/v4.13.0), Apache/MPL | Pruebas CI y accesibilidad, no camino HTTP; revisión manual adicional |
| Cobalt9.0.1 | [AKN](https://github.com/laws-africa/cobalt/blob/v9.0.1/cobalt/akn.py), [URI](https://github.com/laws-africa/cobalt/blob/v9.0.1/cobalt/uri.py), LGPL | Modelo obra/versión/manifestación como referencia; diferir AKN completo |
| Indigo19.1.1 | [repo](https://github.com/laws-africa/indigo/tree/v19.1.1) | Referencia editorial, no plataforma importada; discordancia GPL/LGPL a aclarar |
| Docling2.128.0 | [repo](https://github.com/docling-project/docling/tree/v2.128.0), MIT código | Diferir modelos/deps/carga; ensayo si tablas complejas justifican |
| PyMuPDF1.28.2 | [repo](https://github.com/pymupdf/PyMuPDF/tree/1.28.2), AGPL/comercial | No añadir sin decidir cumplimiento/licencia; repo propio público no basta |
| aBOgacion | [repo](https://github.com/strysg/aBOgacion), [ingesta](https://github.com/strysg/aBOgacion/blob/main/obtener_gaceta.py), [metadata](https://github.com/strysg/aBOgacion/blob/main/construir_metadata.py) | Referencia raw/normalizado. README GPLv3; licencia separada de datos no confirmada. No importar sin obligaciones |
| Bolivian-law-mcp | [repo](https://github.com/Ansvar-Systems/Bolivian-law-mcp), [LICENSE](https://github.com/Ansvar-Systems/Bolivian-law-mcp/blob/dev/LICENSE), [sources](https://github.com/Ansvar-Systems/Bolivian-law-mcp/blob/dev/sources.yml) | Referencia por artículo/drift; NO base o veredicto de vigencia. Declara2497 estatutos Justia y excluye fallos/Tarija local; cifra del autor |
| LexiVox/dataset mirror | [LexiVox](https://www.lexivox.org/norms), [dataset](https://huggingface.co/datasets/endomorphosis/ipfs_bolivia_laws) | Descubrimiento/comparación, no autoridad ni licencia comercial general |

El MCP fue accesible por web aunque el conector dio404. README mezcla promesas de actualidad con historia pendiente y nombres de herramientas UE para Bolivia: no copiar sus afirmaciones de vigencia o dominio público. Su implementación completa no fue auditada.

Django6.1.1 fue observado como última oficial;5.2.17 se propone por LTS, no porque5.2.6 siga actual. PyPI devolvió OCRmyPDF17.12.1 frente a17.10.0 de una lectura anterior: se corrigió. `vulnerabilities=[]` en registry no demuestra ausencia de CVEs transitivos. Antes de integrar: registry fechado, lock exacto, hashes, SBOM, avisos oficiales y compatibilidad. No se instaló ni ejecutó código de estos terceros.

## 6. Arquitectura y contratos propuestos

### Decisiones y alternativas

1. Mantener adaptadores/FTS5 con tests legacy; rechazar reescritura de búsqueda sin beneficio medido.
2. Django como frontera única: sesión/CSRF/reset/admin; rutas legacy por wrapper. Servidor stdlib no queda expuesto por puerto alternativo. No headers del cliente como identidad/membresía.
3. Corpus snapshot readonly y base transaccional separada para usuarios/colecciones/reportes/acceso. SQLite inicial, escritor controlado/transacciones cortas/backup consistente. Migrar transaccional a PostgreSQL si concurrencia/operación fallan; no migrar FTS por gusto.
4. Original inmutable y derivados versionados: obra, versión normativa y archivo son identidades distintas. Hash original no es hash del texto ni prueba de vigencia.
5. Publicación de snapshot fuera de servicio y cambio atómico autorizado. Retirada por ID se evalúa también sobre snapshots viejos, colecciones y exportación.
6. OCR/fetch fuera de requests; límites y estados explícitos. No habilitar expedientes privados en v1.

### Árbol objetivo, no scaffold entregado

```text
pipeline/                    extracción/adaptadores existentes
  fuentes/                   manifests y políticas de adquisición
  validacion/                identidad/hash/estructura/anexos
sistema/api/                 búsqueda/procedencia y adapter de lectura
sistema/web/                 UI existente adaptada
sistema/portal/              Django settings/urls/wsgi/middleware
  cuentas/                   auth/sesiones/permisos
  colecciones/               favoritos/compartir/versiones
  reportes/                  feedback y revisión privada
  membresias/                periodos/pagos/conciliación
  publicaciones/             snapshots/restricción/retirada
tests/                       unit/integración/HTTP/navegador/mutación
tests/fixtures/              goldens sintéticos/autorizados
docs/adr/                    decisiones y alternativas
docs/agents/                 contexto/bitácora/evidencia segura
docs/operacion/              restore/incidentes/actualización/rollback
contracts/                   OpenAPI y esquemas al implementar
infra/                       proxy/servicio no-root/build/límites
.github/workflows/           CI hosted sin datos sensibles
pyproject.toml               dependencias directas seleccionadas
requirements.lock            resolución exacta y hashes probados
```

Son entregables de B01/B02/D01/F01, no archivos que se afirmen implementados aquí.

### Entidades y reglas

| Entidad | Contrato mínimo |
| --- | --- |
| Fuente |ID,órgano,jurisdicción/competencia,URL,condiciones,censo,fecha de consulta |
| Obra |ID estable,tipo,número,fecha,título,emisor; no clave por número solo |
| Versión |obra,publicación/efecto si conocidos,fecha de conocimiento,relaciones verificadas,estado y evidencia/revisor |
| Archivo/extracción |SHA original,MIME/tamaño,URL,motor/versión/idioma,hash derivado,páginas/artículos/anexos/errores |
| Publicación |snapshot,manifest,head,conjuntos/conteos,aprobador,restricciones/retirada |
| Usuario |ID,rol,estado,consentimiento; auth framework, sin secretos en logs |
| Colección |propietario,título,versiones,permisos,revocación de enlace |
| Reporte |autor según canal,categoría,UID/versión/pasaje,texto limitado,estado,responsable,historial privado |
| Membresía |usuario,periodo explícito,inicio/fin,estado pago,renovación cancelada,proveedor,idempotencia |

Vigencia `desconocida/parcial/verificada/histórica` no implica consolidación de cada artículo. Relaciones modifica/abroga/reglamenta llevan disposición/fecha/evidencia; candidato automático separado de aprobación humana.

### HTTP propuesto

A02 inventaría y B02 congela rutas existentes con goldens; no se rompe a consumidores. Nuevas mutaciones: sesión,CSRF,tamaño/permisos.

| Operación | Entrada/salida y error |
| --- | --- |
| GET búsqueda legacy |q/filtros/paginación→UID,versión,pasaje,fuente,restricción,alcance,snapshot;400 sintaxis,429 cuota |
| GET documento/procedencia legacy |UID/versión→texto permitido/fuente;404 desconocido/no visible,410 retirado solo si no filtra identidad |
| POST /cuenta/registro,/cuenta/sesion,/cuenta/salir |auth framework, cookie segura, respuesta no enumera cuentas; sin tokens en URL |
| GET/POST /api/v1/colecciones |listar propias/crear título;201,401 sin sesión |
| PATCH/DELETE /api/v1/colecciones/{id} |metadata/permisos/eliminación confirmada;404 ajena,409 versión |
| POST /api/v1/colecciones/{id}/items |UID+versión visible; duplicado idempotente, no concede permisos adicionales |
| POST /api/v1/reportes |UID/versión opcional,categoría,descripción→201 ID/estado;413 tamaño,429 abuso |
| GET /api/v1/reportes/{id} |estado/historial autorizado;404 ajeno |
| GET /api/v1/membresia |estado,periodo pagado,renovación/uso;401 |
| POST /api/v1/pagos/eventos |firma proveedor e idempotencia; duplicado200 sin doble efecto,firma inválida401 |
| POST /api/v1/membresia/cancelar-renovacion |conserva periodo abonado,200 estado resultante |
| GET /salud,/listo |liveness mínima/readiness sin secretos;503 si dependencia esencial indisponible |

JSON: tiempos ISO8601 con zona,IDs opacos,errores code/message/request_id sin trazas SQL ni consultas originales. OpenAPI/esquemas ejecutables son trabajo previo a implementar consumidores.

```text
fuente externa → fetch restringido → original cuarentena
 → extracción aislada → identidad/hash/estructura → revisión
 → snapshot aprobado → consulta readonly

navegador → TLS/proxy → Django auth/CSRF/membresía
 → permiso documental/retirada → adapter corpus → cita versionada

reporte → validación → base privada → triage
 → corrección revisada → publicación → resolución privada

proveedor pago → firma/conciliación → evento idempotente
 → periodo de acceso → consulta autorizada
```

## 7. WBS detallada:72 unidades y aceptación

Roles propuestos: E=Brain técnico; J=revisor jurídico boliviano a designar; D=docente/editor a designar; A=Abraham para decisiones/autorizaciones. No se delega a ejecutores sin créditos ni se inventa disponibilidad humana.

Horas son esfuerzo estimado, no runtime. Cada fila≤4h; lotes se repiten según fórmula. Un lote4h no representa revisión de todo el país.

| ID | Entregable y aceptación | Depende de | Rol | h |
| --- | --- | --- | --- | ---: |
| A01 | Foto segura VM/servicio/base: revisión, recursos, rutas y respaldo identificado, sin secretos | Inicio | E | 4 |
| A02 | Matriz main/PR/ramas/servicio; contratos existentes e IDs reconciliados, sin reset de árboles ajenos | A01 | E | 4 |
| A03 | Registro de fuentes, permisos y alcance publicado con exclusiones explícitas | A02 | J | 4 |
| A04 | Guion, consentimiento y tareas de entrevistas por rol; ningún expediente requerido | Inicio | D | 2 |
| A05 | Primeras cuatro entrevistas/observaciones anonimizadas, informe de tareas | A04 | D | 4 |
| A06 | Lista inicial24+20+30+10 y tareas de aceptación; huecos/dependencias normativas declarados | A03,A05 | J | 4 |
| A07 | ADR de reuso: licencias directas/transitivas y versiones candidatas contrastadas | A02 | E | 4 |
| A08 | Aprobación de alcance, roles, periodo de membresía y política de datos; acta | A06,A07 | A | 2 |
| B01 | Esquemas de identidad/procedencia/versión; tests contra número repetido/anexos | A02 | E | 4 |
| B02 | OpenAPI/goldens legacy y nuevos contratos; compatibilidad observable | B01,A07 | E | 4 |
| B03 | Fix hash nacional: alterado/ausente/malformed rechazados; control válido aceptado | B01,I05 | E | 3 |
| B04 | Extracción HTML por cuerpo legal; fixture navegación/relacionados excluidos | B03 | E | 4 |
| B05 | Comparación PDF nativo/OCR sobre10 páginas representativas, sin sustituir por intuición | A07 | E | 4 |
| B06 | Fetch seguro: límites, redirect policy, MIME, hashes, reintentos y recuperación | B01 | E | 4 |
| B07 | Recuperación decretos: IDs/anexos/fallados y ubicación real de resultados | A02 | E | 4 |
| B08 | Publicador snapshot transaccional; no-pérdida por conjuntos y rollback probado | B02,B06,B07 | E | 4 |
| C01 | Lote nacional: identidad/texto/artículos de hasta6 normas, diferencias documentadas | A06,B04 | J | 4 |
| C02 | Lote relaciones temporales de hasta6 normas; cada estado con fuente y evidencia | C01 | J | 4 |
| C03 | Lote departamental: hasta5 cuerpos/anexos con fecha/título contra documento | A06,B07 | D | 4 |
| C04 | Adaptador local piloto: censo y muestra de Tarija/Gran Chaco, sin inferir serie completa | B06,A06 | E | 4 |
| C05 | Lote jurisprudencia: hasta5 fallos, materia/fecha/fuente/privacidad revisadas | A06 | J | 4 |
| C06 | Lote agrario/laboral sectorial: hasta5 instrumentos necesarios para tareas | A06,B06 | J | 4 |
| C07 | Diez lecturas docentes: enlaces/licencias o autorización explícita; no PDFs NC comerciales | A03 | D | 4 |
| C08 | Snapshot curado con inventario de cobertura y pendientes por fuente | B08,C01,C02,C03,C04,C05,C06,C07,I06,I07 | E | 4 |
| D01 | Frontera Django en staging, lock/SBOM, legacy adapter y puertos laterales cerrados | A07,B02 | E | 4 |
| D02 | Registro/sesión/logout/CSRF probados; respuestas no enumeran cuentas | D01 | E | 4 |
| D03 | Recuperación/revocación/admin restringido; pruebas de sesiones expiradas | D02 | E | 4 |
| D04 | Favoritos y colecciones privadas; aislamiento entre dos usuarios probado | D02,B02 | E | 4 |
| D05 | Compartir colección/versiones y revocar enlace; no bypassea permisos del documento | D04 | E | 4 |
| D06 | UI lectura móvil/teclado/fuentes/cita y glosario breve; flujo completo observable | D04,C08 | E | 4 |
| D07 | Feedback dentro de resultados/documentos y cola privada; caso end-to-end | D02,B02 | E | 4 |
| D08 | Contadores mínimos, privacidad logs y cuotas por cuenta/red universitaria | D01,D07 | E | 4 |
| E01 | Corpus de evaluación60 tareas, primera tanda15 con clave profesional y versiones | A06,C08 | J | 4 |
| E02 | Unitarias de identidad/citas/hash y controles negativos; cobertura crítica reportada | B03,B04,B08 | E | 4 |
| E03 | Integración snapshot/cuentas/permisos/feedback; rollback y duplicados | D05,D07,C08 | E | 4 |
| E04 | Verificador HTTP separado fijado por hash; no importa recibos del candidato | E02,E03 | E | 4 |
| E05 | Seguridad: SSRF/XSS/traversal, archivos malformados, bypass y logs con fixtures | B06,D08 | E | 4 |
| E06 | Navegador+axe y revisión teclado/móvil manual; defectos severos cerrados | D06,D07 | E | 4 |
| E07 | Carga escalonada5/20/50 sesiones en staging; medir latencia/errores/RAM, sin producción | E03,D08 | E | 4 |
| E08 | Revisión de muestra de publicación y rutas alternativas; permiso para piloto o bloqueo | E01,E04,E05,E06,E07 | J | 4 |
| F01 | CI hosted con pins/permisos mínimos, resultados durables sin datos sensibles | E02,E04,A07 | E | 4 |
| F02 | Servicio no-root/proxy/TLS/secretos y límites documentados en staging | D01,F01 | E | 4 |
| F03 | Backup/restore consistente de corpus, cuentas, permisos, colecciones, feedback y retiro | F02,C08,D03,D05,D07,D08 | E | 4 |
| F04 | Simulacro caída/retiro documento/rollback; prohibido reabrir retirados desde snapshots viejos | F03,E08 | E | 4 |
| F05 | Inventario final VM, smoke y carga propuesta autorizada; capacidad o plan de reducción | A01,F04 | E | 4 |
| F06 | Manual usuario/editor/operación y soporte, ficha cobertura/precio/privacidad | D06,F04 | D | 4 |
| F07 | Acuerdo piloto y alta de grupos, responsables y consentimiento; no invitaciones antes | A08,E08,F06,I01,I03,I04,I08 | A | 2 |
| F08 | Decisión go/no-go y despliegue reversible autorizado; acta y smoke del head publicado | F05,F07 | A | 2 |
| G01 | Sesión de onboarding pequeña por universidad, registro de dificultades sin PII innecesaria | F08 | D | 4 |
| G02 | Primer bloque de tareas comparadas corpus/método habitual, resultados por rol | G01,E01 | D | 4 |
| G03 | Triage semanal: privacidad/bloqueantes primero; reporte con responsable y evidencia | G01 | E | 4 |
| G04 | Revisión docente de errores y aplicación normativa, acuerdo entre revisores | G02 | J | 4 |
| G05 | Corrección acotada de defecto priorizado y regresión; no expansión sin evidencia | G03,G04 | E | 4 |
| G06 | Informe piloto por rol, tarea, retorno y tiempos con denominadores | G02,G04,G05 | E | 4 |
| G07 | Oferta US$10 por periodo aprobado a activos elegibles, sin cobro automático sorpresivo | G06,A08 | A | 2 |
| G08 | Decisión sobre etapa paga según calidad, uso y capacidad, no solo encuestas | G06,G07 | A | 2 |
| H01 | Elegibilidad de banco/pasarela/NIT/facturación y tarifa real; contrato antes de integrar | A08 | A | 4 |
| H02 | Periodos de acceso y cancelación al fin abonado; estados verificables | D03,H01 | E | 4 |
| H03 | Pago en entorno de prueba/conciliación; no activar por captura de pantalla | H02 | E | 4 |
| H04 | Eventos idempotentes/desorden y restauración de periodo pagado/conciliación probados | H03,F03 | E | 4 |
| H05 | Checkout/política/recibo y autorización primera venta real acotada | H04,G08 | A | 2 |
| H06 | Medición activación/pago/soporte por rol; resultados sin datos bancarios | H05 | E | 4 |
| H07 | Medición renovación segundo periodo, bajas y margen con costos reales | H06 | E | 4 |
| H08 | Cierre comercial v1 y priorización expansión por búsquedas faltantes/reporte de valor | H07 | A | 2 |
| I01 | Primer dictamen de datos/colección y acuerdo piloto; tiempo jurídico separado | A03 | J | 4 |
| I02 | Revisión licencias software/datos elegidos, incluidas dependencias, o veto explícito | A07 | J | 4 |
| I03 | Primera revisión términos/facturación/precio/periodo/moneda y matriz de decisiones | Inicio | J | 4 |
| I04 | Reclutamiento y matriz de confirmados por rol/institución; criterio mínimo cumplido | A04,A05 | D | 4 |
| I05 | Contrato byte original/texto/manifest identificado por digest y retirada de caches | B01 | E | 4 |
| I06 | Revisión jurídica de selección local y competencia; sin confundir cotejo editorial con dictamen | C03,C04 | J | 4 |
| I07 | Revisión jurídica de diez lecturas y permisos comerciales; veto a obras sin base | C07,I02 | J | 4 |
| I08 | Calibración de cuatro lotes reales y revisión del presupuesto/capacidad antes de ampliar | B05,C01,C03,C05 | E | 4 |

### Lotes, esfuerzo y dependencias

Repeticiones presupuestadas: A05×4;C01×4;C02×4;C03×4;C05×6;C06×2;E01×4;G03/G04/G05×4. Resto×1. C07 es catálogo de diez lecturas, no diez dictámenes complejos. I01/I02/I03/I06/I07 son primeros bloques jurídicos que se repiten si no bastan. Cada nuevo lote tiene alcance/aceptación y recalcula presupuesto.

**Cómputo validado:**72 unidades,271h base,391h con lotes. E191h,J128h,D54h,A18h. Reserva30% sobre E+D=73,5h: **464,5h orientativas**, antes de más revisión legal, reformas/anexos y esperas. No es benchmark ni precio cotizado. Ninguna fila>4h, sin IDs repetidos/dependencias inexistentes/ciclos. Ciclos semanales no garantizan cerrar cualquier número de bugs.

La cantidad por lote no es productividad medida. I08 calibra tiempo por norma/página/fallo; si excede4h, dividir por capítulos/relaciones y aumentar presupuesto o reducir alcance transparentemente, nunca bajar calidad. No esconder asesoramiento legal en reserva técnica.

A04/A05,A01/A02 yA07 pueden avanzar en paralelo. B03 bloquea ingesta confiable, no entrevistas ni diseño de colecciones. C08 yD06 convergen en producto usable; no esperar todos los municipios. E08/F08 bloquean exposición; CI no sustituye revisión jurídica. H01 puede tramitarse durante preparación; H05 espera calidad/piloto/autorización. I es transversal, no una fase al final.

## 8. Calendario y primeros pasos

No fijo fecha por supuesta disponibilidad24/7 de una IA. Semanas técnicas=horas pendientes/capacidad real, ajustadas por DAG y disponibilidad humana.

Arranque: A01/A02/A04/A07; luego B01→I05→B03 con observación de usuarios en paralelo. Segunda etapa: alcance humano y flujo buscar→verificar→guardar→reportar con colección pequeña. Reestimar antes de comprometer el resto.

A20h técnicas semanales,E191h equivale a9,55 semanas de esfuerzo distribuidas entre preparación,piloto,cobro, **no fecha de lanzamiento**. J128h/D54h tienen disponibilidad distinta. La primera semana a20h puede no completar todo el arranque. Calendario con fechas después deI08 y confirmación J/D.

Piloto cuatro semanas después de gates, ampliable dos si faltan observaciones, no para ocultar fracaso. Renovación requiere terminar el siguiente periodo. Desarrollo propio no es costo cero: tiempo técnico/jurídico/editorial/soporte, almacenamiento, correo y cobro. No usar presupuestos genéricos de investigadores como cotizaciones.

## 9. Tests y gates de liberación

G0 alcance/fuentes/tareas/revisor;G1 contenido;G2 software;G3 operación;G4 piloto;G5 comercial. Cada gate puede rechazar.

| Prueba | Umbral propuesto/falsador |
| --- | --- |
| Integridad | Original pasa; byte alterado/hash ausente no autorizado/ID equivocado/anexo pisado fallan |
| Fidelidad | Citas/versión contra fuente; historia no aparece vigente. Error material pendiente bloquea tarea/colección |
| Privacidad | Cero fugas en conjunto adversarial e incidentes críticos abiertos; búsqueda/texto/API/exportación/cache/snapshot retirado |
| Autorización | Sin sesión/no miembro/ajeno/revocado no acceden; colección no concede permiso documental |
| HTTP | Verificador separado fijado; siempre200 y fallos de procedencia deben rechazarse; salida cruda |
| Rendimiento | Inicial p95≤2s búsqueda y errores<1% con20 sesiones staging;50 estrés y dataset sintético10×, no certificar población futura |
| Accesibilidad | Cero hallazgos automatizados críticos abiertos y tareas por teclado/móvil; axe no certifica WCAG solo |
| Recuperación | Propuesta RPO24h/RTO4h, pagos conciliables con proveedor; restore por hashes/conteos/permisos |
| Dependencias | Lock/SBOM/advisories/análisis de alcance; vulnerabilidad crítica explotable abierta bloquea publicación |

Objetivo≥85% líneas críticas nuevas, sin sustituir tests de permisos/contenido. Parsers aislados con límites páginas/píxeles/tamaño/tiempo. SSRF valida redirects/DNS/redes privadas, no solo URL inicial.

A10× no se promete escalabilidad SQLite: medir bloqueos,FTS,RAM,snapshots. Si transaccional falla, migrar aPostgreSQL; si búsqueda falla SLA, optimizar consulta/cache controlada antes de vector DB. OCR fuera de recursos del servicio.

## 10. Privacidad, identidad y trabajo humano después de QA

C03/D coteja metadata; I06/J aprueba competencia/selección. C07/D inventaría lecturas; I07/J verifica uso comercial. I01/I02/I03/I06/I07 son bloques iniciales, no garantía de dictamen completo en4h.

I05 define SHA original sobre bytes recibidos antes de extraer; SHA texto sobre UTF8 de derivado con algoritmo/versión. Manifest con claves ordenadas/codificación definida, objeto/URL/fecha/hash; publica digest/procedencia. Hash no es autenticidad estatal ni firma criptográfica. Versión nueva no sobreescribe originales.

Retirada porID se evalúa en cada request/exportación, invalida caches/enlaces temporales y bloquea reconstrucción desde snapshots viejos. **No puede borrar archivos ya descargados por terceros**: minimizar exportación sensible y gestionar incidente aparte.

D01 staging aislado/sin demo pública. Exposición solo trasE05/F02: HTTPS,cookies Secure/HttpOnly/SameSite apropiado,CSRF,reset con caducidad/un uso,permisos y cierre de listeners legacy. No nuevos auth/JWT ad hoc ni confianza en headers del cliente.

F03 restaura cuentas/permisos/colecciones/reportes después de existir. H04 repite con pagos/periodos y conciliación; restore no duplica ni pierde acceso abonado. Cancelar renovación conserva tiempo pagado.

Registro de reportes: ID,UID/versión/pasaje,categoría,descripción limitada,estado/responsable/historial privado. Botones Reportar error,No encontré,Sugerir yMis reportes. No adjuntar consultas/capturas/expedientes automáticamente. Reporte no reescribe fuente; corrección revisada y nueva versión. Métricas mínimas/agregadas, sin q en logs por defecto. No entrenamiento con datos de usuarios sin base/autorización.

Licencia de código y derechos de datos separados. [UCB CC BY-NC-SA](https://lawreview.ucb.edu.bo/a/copyright-policy) no autoriza uso comercial íntegro por defecto. Un sitio público o un pie derechos reservados tampoco resuelve jurídicamente cada norma. Revisión boliviana de actividad,datos,condiciones y materiales, no dictamen emitido por este plan.

## 11. Piloto en dos universidades y conversión real

Candidatas verificadas: [UAJMS](https://www.uajms.edu.bo/oferta-academica/carrera-de-derecho/) y [UPDS Tarija](https://www.upds.edu.bo/carrera/derecho-tarija/). Meta dos docentes+12 estudiantes por universidad y seis abogados:34 participantes objetivo, no convocados. Niveles inicial/intermedio/avanzado. Biblioteca común/grupos diferenciados; docente no ve historial privado de alumno.

I04 registra reclutamiento autorizado/aceptación/rol/disponibilidad sin PII pública. Para llamarlo dos universidades: ambas confirmadas, al menos un docente y ocho estudiantes en cada una. Conclusión profesional exige≥4 abogados; si faltan, piloto reducido y NO MEDIDO ese público. No sustituir participación por matrícula.

Banco60 tareas:20 exactas,20 temáticas,20 temporales/procedencia; cada persona realiza subconjunto, alternando método habitual/corpus. Claves profesionales y holdout separado de ajuste; no comparar respuestas contra las del propio sistema.

Métricas: éxito=tareas correctas/asignadas válidas con abandonadas explícitas; precisión=citas correctas/revisadas; tiempo hasta verificar; retorno; reuso de colecciones; reportes cerrados. Umbrales iniciales a acordar:≥80% éxito,≥95% citas correctas y **cero errores materiales abiertos en aceptación**,≥25% ahorro, cero incidentes críticos. El95% no autoriza5% de normas falsas: error material bloquea su escenario. Recuentos/intervalos y diferencias por rol; no extrapolar muestra aBolivia.

Oferta US$10 por periodo aprobado: biblioteca declarada,búsqueda,citas,guardados/colecciones,cambios detectados en fuentes incluidas,reportes/soporte acotado. No asesoría,IA ilimitada o todos los textos vigentes. API de volumen/licencia institucional aparte. No bajar precio estudiantil automáticamente: evaluar quién paga,alumno o institución.

[D-Lex US$95,88/año](https://www.derechoteca.com/legal-tech/d-lex-bolivia-suscripcion), [Pixi Lector Bs20/mes](https://www.pixilegal.com/planes), [LeyNova Bs50 profesional/Bs20 estudiante](https://leynova.com/) son precios publicados, no calidad auditada. US$10 mensual requiere valor local; no se reemplaza porBs69.

I03 especifica importe,periodo,moneda cobro/liquidación,tipo de cambio/momento si aplica,impuestos,cancelación,reembolso y facturación. A08 aprueba propuesta; H01 valida soporte del proveedor antes del checkout.

[Red Enlace](https://www.redenlace.com.bo/productos-y-servicios/quiero-cobrar-por-internet-en-mi-tienda-virtual) ofrece Bs/USD,checkout y recurrencia tokenizada con requisitos; hasta2,5% publicado no es costo contractual total. [SIN](https://siatinfo.impuestos.gob.bo/index.php/informacion/modalidades-facturacion/facturacion-portal-web) para validar facturación según vendedor. QR manual requiere conciliación y moneda/tipo de cambio informado; captura no prueba pago ni renovación automática.

Conversión=pagadores/activos elegibles con oferta; renovación2/pagadores1. Encuesta no sustituye pago. Medir soporte/edición por usuario. Modelo mensual supuesto: `N * (10 * (1-comision) - cargo_fijo - variable_usuario) - fijos`.100miembros=US$1000 brutos, no beneficio. Costos/contratos/impuestos no medidos.

## 12. Operación y expansión hasta cierre comercial

Monitoreo servicio/fallos de fuente diario; triage privacidad según capacidad acordada; novedades volátiles semanal; revisión editorial por lote; restore mensual y después de migración; acceso/secrets/parches con cadencia. Mostrar última consulta de fuente y última revisión jurídica de versión. Alerta de cambio no es dictamen de vigencia.

Después de v1: reconciliar toda serie departamental disponible, Gran Chaco y catálogos municipales pendientes; módulos sectoriales por búsquedas fallidas. Cada adaptador pasa identidad/no-pérdida/privacidad. Anexos/cartografía no se descartan por ser difíciles. Revisión de cobertura trimestral y decisión comercial por retención/costo, no número dePDFs.

| Riesgo | Mitigación/stop |
| --- | --- |
| Falta revisor jurídico | No publicar como validado; acordar recurso antes del gate |
| Catálogo sirve otro PDF | Identidad en cuerpo; discrepancia y cuarentena |
| Mirror parece oficial | Autoridad real/mirror/licencia y contraste emisor |
| Ruta vieja expone causa | Frontera única, tests bypass/caches/exports, retirada independiente |
| Dependencia aumenta costo/licencia | Shortlist/SBOM/spike; rechazar plataforma sin beneficio |
| Clase comparteIP | Cuota cuenta y red compartida; límite global separado |
| Scope infinito | Materias/tareas v1 congeladas; expansión por lotes |
| Gratis no convierte | Pago/renovación reales; ajustar valor/modelo con evidencia |
| OCR compite con servicio | Worker separado, límites y hosted autorizado |
| Doctrina sin derecho | Permiso/licencia porobra o enlace, revisión comercial |

Decisiones humanas:periodo/moneda,roles,alcance,permisos,acuerdos,cuota/runtime,deploy,banco/fiscal. No bloquean esta planificación; sí gates correspondientes. No se emiten órdenes a otros ejecutores ni se crean issues en lote sin confirmación.

## 13. TITAN FULL, scorecard y evidencia

Router: investigación/arquitectura/documentación sobre repo existente. Roles GITHUB/ARCHITECT/DOCS/QA; seguridad,testing,operación e innovación como requisitos de plan. BUILDER/REFACTOR/DEPLOY de software no ejecutados: pedido plan,no implementación.

QA por otra instancia, no auditoría externa contratada. Primer preflight35/45 rechazó trabajo jurídico oculto,restore,reclutamiento ysemántica de retirada. Corregidos conI01-I08/dependencias/precisiones. Segundo **41/45=91,1/100**, contenido apto condicionado a publicación/hash. La edición publicada se coteja antes del cierre.

| Criterio | Score | Evidencia |
| --- | --- | --- |
| Completitud |14/15| §4/§7/§10:72unidades y lotes humanos; productividad aún a calibrar |
| Arquitectura razonamiento |9/10| §6,DAG yrestore; escala no medida |
| Documentación |9/10| Fuentes,decisiones,gates; onboarding real futuro pendiente |
| Innovación diseño |5/5| Retirada porID,tiempo normativo/conocimiento,red compartida,holdout,cobertura por colección |
| ProcesoQA |4/5| Dos pasadas/correcciones/cómputo; no certificación producto |

| Rol | Resultado | Pasadas | Observación |
| --- | --- | --- | --- |
| GITHUB/investigación | Incorporado a rúbrica |2| Separación rama/servicio/mirror |
| ARCHITECT | Incorporado a rúbrica |2| Dependencias/semántica corregidas; contratos ejecutables futuros |
| DOCS | Incorporado a rúbrica |2| Estimaciones sin personas/fechas inventadas |
| QA |41/45,91,1/100|2| Calidad del plan, no corpus91%terminado |

N/A55:Ejecutabilidad15,Seguridad15,Testing15,DevOps10 de código nuevo. No decir OWASP cubierto o producción verde por esta rúbrica.

Evidencia nueva: entorno/FTS5 yregistry fechados,lecturas públicas,validación mecánica WBS. No nuevo test productivo ni ejecución de dependencias. Control FTS5positivo/negativo prueba esa función, no rendimiento del corpus.

Errores corregidos: Django5.2.6 histórico frente LTS5.2.17; OCRmyPDF17.10.0 frente17.12.1; literal ENTORNO.MD no localizado no significa capacidades ausentes;404 conector de tercero no impidió web y web no se llamó auditoría de todo el código.

**NO MEDIDO:** producción actual,cuota/GPU/nuevo hosted run,benchmarks terceros,CVEs transitivos completos,recursos humanos/acuerdos,exactitud global/censo total,contratos/costos/conversión. No dictamen legal ni permisos adquiridos.

Archivo canónico: `docs/agents/respuestas/2026-09-17-01-plan-integral-corpus-titan-full.md`. Evidencia de cierre: `docs/agents/evidencia/2026-09-17-01-plan-corpus-evidencia.json`. Copia documental pública en Space. Este archivo es un plan nuevo; no sobreescribe contexto operativo ni asigna72tareas reales.
