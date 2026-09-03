# Que existe ya en Bolivia, y donde esta el hueco real

**Investigado el 2026-09-03.** La pregunta era si esto que construimos existe y si tiene alto
valor. La respuesta medida es incomoda y va escrita: **existe, hay mucho, y varios son mas
grandes que nosotros.**

## Comercial: hay competencia grande y con IA

| producto | lo que declara |
|---|---|
| **LeyNova** (`leynova.com`) | **35.000+ normas y 163.000+ extractos del TCP y TSJ.** Verificacion de cada cita contra su corpus, **control de vigencia** ("nunca cites derecho muerto"), OCR de memoriales, analisis con citas `[S#]` y lista de fuentes verificadas. Equipo boliviano, infraestructura propia. |
| **Difusion Juridica** (`difusion.com.bo`) | **163.000 resoluciones judiciales**: 47.236 del TCP, 49.406 del TSJ, 25.271 de la Corte Suprema, 7.030 del Agroambiental, 9.485 Autos de Vista, 2.300 sentencias de juzgados. Mas ~13.700 normas y doctrina. |
| **SILEG / Bolivia Legal** | **100.000+ textos** digitalizados y concordados, desde la fundacion de la Republica. **25 anos** de trabajo de compilacion. Version corporativa y en linea. |
| **Derechoteca D-Jurisprudencia** | Base de resoluciones del TCP y TSJ por suscripcion, con buscadores especializados y analisis de relaciones entre resoluciones. |
| **Lexius** (`lexius.io/bo`) | Legislacion y jurisprudencia con actualizacion diaria, busqueda con IA, alertas. |

## Oficial y gratuito

- **GENESIS** (`jurisprudencia.tsj.bo`): Autos Supremos, Sentencias y Jurisprudencia del TSJ, con arbol de jurisprudencia y app movil. **Es nuestra fuente.**
- **KRIMA** (`krima.organojudicial.gob.bo`): resoluciones de Tribunales Departamentales y Juzgados. **Fuente nueva que no estabamos usando.**
- **Buscador del TCP** (`buscador.tcpbolivia.bo`): causas y resoluciones constitucionales.

## En GitHub: hay uno con casi nuestra misma arquitectura

| proyecto | que es |
|---|---|
| **`Ansvar-Systems/Bolivian-law-mcp`** | **2.497 leyes y 25.002 provisiones en SQLite FTS5 con ranking BM25**, ~51 MB, servidor **MCP** con 8 herramientas: busqueda, `validate_citation` ("zero-hallucination check"), `check_currency` (vigente/modificada/abrogada), `format_citation`. "Zero LLM-generated content". Fuente: Bolivia Justia y LexiVox. |
| **`israelmamani/tcp-bolivia-mcp`** | MCP del **Tribunal Constitucional Plurinacional**, con diccionario juridico boliviano para expandir consultas y **referencias reproducibles por parrafo** (`tcp:{id}:{seccion}:p{n}`). |
| **`strysg/aBOgacion`** | Normativa boliviana scrapeada de **lexivox.org** y la Gaceta Oficial, en markdown por ano, con visor estatico y busqueda FlexSearch. GPLv3. |

Es sano decirlo: **la convergencia de diseno es casi total** con el primero. SQLite FTS5, BM25,
validacion de citas contra la fuente, control de vigencia, servidor para que lo consuma un
agente. Llegamos a las mismas decisiones por separado, lo que sugiere que son las correctas, y
tambien que **no son un diferencial**.

## El hueco, y es exactamente el nuestro

**TODOS declaran explicitamente que NO cubren lo departamental ni lo municipal.** No es una
suposicion: esta escrito en sus propias fuentes.

- `Bolivian-law-mcp`, README: *"Departmental and municipal regulations are not included -- this
  covers national legislation only"*.
- `Bolivian-law-mcp`, `sources.yml`, limitaciones de LexiVox: *"departmental and municipal
  ordinances (ordenanzas municipales) are not included"*.
- Su `DISCLAIMER.md`: *"Departmental regulations -- Regulatory instruments at the departmental
  level may be missing"*.

Y los comerciales cuentan **normas nacionales y jurisprudencia de tribunales nacionales**;
ninguno publicita legislacion departamental de los nueve departamentos.

**Nuestras 784 normas departamentales de Tarija 2010-2026, con texto completo, hash y URL
oficial, no estan en ninguno de estos productos.** Eso es lo que tenemos y nadie mas.

## Que significa para la estrategia

1. **El corpus nacional NO es nuestra ventaja.** Competir ahi es pelear contra 25 anos de SILEG y
   contra un equipo que ya tiene 163.000 extractos con control de vigencia. Sumar los codigos
   sigue siendo util **para completar el producto**, no para diferenciarlo.
2. **Lo departamental si es un hueco real y verificado**, y el pipeline ya generaliza a los otros
   ocho departamentos con un adaptador por gaceta.
3. **Lo municipal es el hueco siguiente**, y esta igual de vacio.
4. **KRIMA aparecio como fuente nueva**: resoluciones de Tribunales Departamentales, o sea
   jurisprudencia de Tarija de primera y segunda instancia, que GENESIS no tiene y que ningun
   competidor publicita en volumen.
5. Lo que si podemos afirmar como propio: **el corpus es abierto y verificable**. Los comerciales
   son cajas cerradas por suscripcion; aca cada documento trae su sha256 y su URL oficial, y el
   pipeline entero es auditable.

## NO MEDIDO

- **El volumen real de los comerciales.** Sus numeros son autodeclarados en su propio marketing;
  no verifique ninguno.
- **Si LeyNova o Lexius tienen algo departamental** sin publicitarlo. Habria que registrarse y
  buscar una ley de Tarija adentro.
- **Cuantos documentos tiene KRIMA para Tarija.** Es la medicion que sigue.
