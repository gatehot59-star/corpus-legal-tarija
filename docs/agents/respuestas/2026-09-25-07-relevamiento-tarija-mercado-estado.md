# Relevamiento Tarija + estado de Corpus y hacia dónde va

Fecha: 2026-09-25. Encargado por Abraham. Dos insumos: investigación web pública
(dolores del sistema judicial tarijeño) y toda la evidencia interna del workspace
y el repo (auditorías, Fable, pilotos, OCR).

## Veredicto

Corpus Tarija es hoy un **producto técnico real con un diferencial defendible**,
pero todavía **no es un producto comercial validado**. Tiene 6.079 documentos
con procedencia, un buscador que ninguna herramienta local ofrece para Tarija,
y un piloto funcionando. Le faltan tres cosas para cobrar con la cara limpia:
OCR medido, vigencia visible y un piloto universitario ejecutado.

## Parte 1. Los dolores de Tarija (relevamiento externo)

### Dolor 1: la información jurídica existe pero no es trabajable

- La Gaceta de Tarija publica **PDFs sueltos por norma**, sin consolidación,
  sin control de vigencia y gran parte escaneada sin OCR usable.
- La Gaceta Oficial nacional tiene fragilidad técnica comprobable (errores
  fatales de PHP en descargas, búsquedas que rompen).
- GENESIS del TSJ busca por metadatos: si el abogado no conoce número, sala o
  descriptor, recuperar es difícil. El propio TSJ da capacitación para usarlo.
- KRIMA (resoluciones departamentales de primera y segunda instancia) no es
  rastreable públicamente y exige credenciales.

**Esto es exactamente el hueco que llena Corpus**: un solo lugar, búsqueda por
texto libre, cita copiable, fuente y versión a la vista.

### Dolor 2: el trabajo diario es manual y riesgoso

- Circular TSJ 017/2014: el abogado debe asistir **diariamente a secretaría**
  para controlar plazos. Plazos perentorios, cómputo mixto hábil/inhábil,
  preclusión por un día perdido.
- SIREJ solo consulta por NUREJ/WebID: seguimiento fragmentado.
- Errores de transcripción tienen relevancia jurídica comprobada (SCP
  0413/2018-S3).

### Dolor 3: capacidad judicial insuficiente (contexto, no producto)

- Tarija: ~900-1.000 causas por juez civil/año (dato 2016, el más reciente
  público). Bolivia: ~600.000 procesos en mora (2022); jueces penales hasta
  1.500 causas/año.
- Esto no lo resuelve Corpus, pero explica por qué todo ahorro de hora de
  investigación vale dinero.

### El mercado

- **~3.700 abogados registrados en Tarija** (RPA, TDJ 2019). No hay censo
  público de estudios; mercado atomizado de independientes y estudios chicos.
- 3 universidades con Derecho en Tarija: UAJMS (pública), UCB, UPDS (privadas).
- Precios visibles de herramientas bolivianas: LeyNova Bs 50/mes (20
  estudiante), Lex AI Bs 200/mes. vLex/Tirant: cotización, fuera del bolsillo
  tarijeño típico.

**Lectura: el US$10/mes (~Bs 69) queda entre LeyNova y Lex AI. Es defendible
SI el producto muestra algo que ninguno de los dos tiene: Tarija completo y
verificable.**

## Parte 2. Estado real de Corpus (evidencia interna)

### Lo que está fuerte

- 6.079 documentos / 78.930 pasajes / 102,6 millones de caracteres: GENESIS
  5.030, Gaceta Tarija 1.034, LexiVox 15. GENESIS filtrado por Tarija y la
  Gaceta departamental completa son el diferencial: aBOgacion tiene 36 leyes
  de Tarija; Corpus tiene 1.034 documentos departamentales.
- UI corregida y verificada (filtros persistentes, citas copiables, descarga,
  paginación, lector con progreso, móvil 390px sin desbordes, sesión de 8h).
  78/78 tests.
- Piloto técnico funcionando: empleados crean abogados, panel de uso, reportes
  privados. juanperez ya busca casos reales ("robo", "inmueble").

### Lo que falta (orden de daño)

1. **OCR sin medición jurídica.** juanperez reportó errores reales: "gue" por
   "que", "TARJA" por "TARIJA", "torieños" por "tarijeños". Son 818
   documentos OCR de 6.079. Paddle ganó 44/44 adjudicaciones humanas pero es
   4,86× más lento y NO hay CER/WER contra gold independiente. Reprocesar sin
   medir sería repetir el error histórico.
2. **Vigencia medida en 13 de 527 leyes (2,47%).** El abogado necesita saber
   si lo que cita está vivo. Sin esto, la cita copiable vale la mitad.
3. **Metadatos con defectos comprobados**: 86,8% de normas departamentales
   sin fecha, títulos con basura de URL, un caso de Bs 230.000 vs 390.000
   (error de extracción de tabla) confirmado por auditoría.
4. **Privacidad resuelta a medias**: acceso público cerrado (503), pero el
   backend sigue escuchando en 0.0.0.0:8080 y no hay anonimización decidida.
   La telemetría del portal guarda la consulta completa, contradiciendo una
   decisión anterior.
5. **Piloto universitario no ejecutado**: es la decisión estratégica tomada
   (Corpus primero, piloto en dos universidades, pago después) y sigue sin
   ocurrir.

## Parte 3. Hacia dónde vamos (recomendación)

Fase inmediata (2-3 semanas), en orden:

1. **Cerrar la gold de 120 páginas y medir CER/WER.** Decidir Paddle vs
   Tesseract con números, reprocesar los 818 OCR como versión nueva con
   procedencia (el original jamás se toca). Canal de transcripción ya abierto.
2. **Vigencia visible aunque sea parcial**: marcar cada documento "vigencia
   medida / no medida / derogada" con fecha y evidencia. Primero las 527
   leyes; la honestidad del tercer estado ya está decidida.
3. **Purga de metadatos**: fechas y títulos de los 1.034 departamentales;
   re-extraer tablas montos con revisión (el caso Bs 230k/390k).
4. **Cerrar el flanco privado**: bind del backend a loopback; decidir
   telemetría (contar sin guardar consulta, o consentimiento explícito).
5. **Ejecutar el piloto real**: dos universidades (UAJMS pública + UCB o UPDS
   privada), 30-60 días, con el sensor de uso ya construido. El piloto decide
   el precio; no al revés.

Lo que NO hacer: no agregar chat con IA antes de medir OCR; no expandir a
nacional indiscriminado (vLex/LeyNova ganan ahí); no abrir acceso público
hasta cerrar privacidad.

## Posicionamiento final

Corpus no compite con LeyNova ni Lex AI por IA ni por volumen. Compite por
**verdad verificable de Tarija**: la Gaceta departamental completa, la
jurisprudencia del TSJ filtrada por Tarija, cada párrafo con hash y fuente, y
la honestidad de decir "esto no está medido" cuando no lo está. Ese es el
producto que un abogado de Tarija no consigue en ningún otro lado a Bs 69.

## Fuentes externas clave

- TDJ Tarija RPA: 3.756 abogados (2019) — tarija-tdj.organojudicial.gob.bo/Paper/Detail/4477
- Mora nacional 600.000 procesos (2022) — noticiasfides.com
- Carga jueces Tarija 900-1.000 causas/año — justiciabol.blogspot.com
- Circular TSJ 017/2014 plazos — tsj.bo
- LeyNova Bs 50/mes, Lex AI Bs 200/mes — leynova.com, lexai.com.bo
- UAJMS/UCB/UPDS Derecho Tarija — sitios oficiales

## Evidencia interna clave

- AUDITORIA-FABLE-2026-09-10-RESOLUCION.md (7/8 cargos, 57/100)
- INFORME-PARA-AUDITORIA-2026-09-06.md (33 commits, 0 movimiento de producto)
- COMPETENCIA.md, GENESIS.md, COBERTURA.md, BUSCADOR.md, CIERRE-PUBLICO
- Peritaje Juan Pérez (errores OCR medidos, 48/48 hash)
- Plan integral v2 (piloto antes que pago)
- Docs del workspace: doc-page-46, 61, 65, 73, 74, 174, 175, 227
