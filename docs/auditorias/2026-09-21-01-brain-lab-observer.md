# Corpus: auditoría de Brain32/33, observador y camino a una entrega usable

Fecha: 21-sep-2026, ART. Auditoría acotada; no implementación, merge ni despliegue.

## Veredicto

Brain retomó el trabajo, reconoció la aprobación de Abraham y preparó el laboratorio. Hay cuatro PRs abiertos y tres ejecuciones remotas exitosas. El experimento sigue INCOMPLETO: faltan dos eventos synchronize y la ventana negativa original no tuvo la cobertura temporal acordada.

**Hallazgo nuevo, del instrumento:** observe() puede declarar BOUNDED_ABSENCE tras una sola consulta tardía, incluso al reiniciar con un error y una señal de parada persistidos. Eso no demuestra una falsa aprobación de Brain: su informe33 declaró el ensayo incompleto y no mergeó PR21.

Prioridad: corregir y revisar el observador antes de consumir los dos eventos restantes. No repetir las 111 pruebas de producto para disimular un hueco temporal. Después, cerrar la revisión independiente y una entrega usable de alcance pequeño; no abrir otra ronda genérica de auditorías.

## Sujeto y revisiones

- Repo: gatehot59-star/corpus-legal-tarija. Main inicial: f150c50b7fd224d598fc0e85ea2e684b9ecc4912.
- Brain32: docs/agents/respuestas/2026-09-20-32-brain-revisa-sol-astra.md, commit5891bb4c11fdbd68faf2e1cd2187304f954c4130; reconocimiento en Nexus102.
- Brain33: docs/agents/respuestas/2026-09-20-33-brain-trigger-lab-partial.md y checks-raw, commit1d14895c75468953ee3e1d3d0554d1c63907684a; Nexus103. Esa rama documental diverge de main; un diff entre puntas no prueba borrados aplicados a main.
- PR21: 3b92dc432f285c00d5a45e717883c5c6e3fe46f9, abierto y no mergeado.
- Laboratorio separado: gatehot59-star/corpus-docs-trigger-lab; base vieja c82c684f71a235960504cf46092053c653fd7f48, nueva fdf2519ecb12fcb3e1fcb7eedc1151c23d0d04cc.
- Observador leído y ejecutado en copia: /workspace/brain-trigger-experiment/observer.py, 6802bytes, SHA256 2a727b5c2a21e9d9f197352501bfd1ffdb5aa038a64a1851396b9789eb151a3d.

El Doc seleccionado del17-sep es antecedente, no estado actual. Se recuperaron plan y enmienda de Corpus, inventario y método de MUDH, Nexus, recibos, fuentes y revisiones posteriores.

## Afirmaciones contrastadas

1. **CONFIRMADO: aprobación reconocida.** Brain32 cita Nexus98, ADR28 y el mensaje80170047160978. El chequeo30 no encontró reconocimiento a las20:43ART del20-sep; Brain32 lo registró posteriormente, a las21:17ART. No hay contradicción temporal.
2. **CONFIRMADO: preparación autorizada.** Siete ramas; base de22 archivos, con21 originales comparados byte por byte y README vacío. Entre bases cambia solamente el workflow, retirando24 líneas de paths. Sus hashes son005b9214aa1695edb4fdfb1675cbba813fbe6ce921d3d4f06ae0b0c83687e4df y c69a9f1a21a348bd400fff15165fc55e7e8e7c94fdee1a4a6b7e604d47d0ce72.
3. **CONFIRMADO: cuatro PRs y tres runs exitosos.** API actual completa para este conjunto, sin continuación de página; asociación por PR, head/base y datos del evento, no por título. Los cambios de código de las sondas son inertes según comparación AST; los documentales cambian solo docs/ci-trigger-probe.md.
4. **CONFIRMADO: ensayo incompleto.** Cuatro episodios opened de seis previstos; ningún synchronize nuevo en la captura. El registro histórico conserva cuatro muestras, la última unos64,7segundos después del evento, no cinco minutos. La lectura actual sin run de OLD-DOCS no reconstruye aquella cadencia.
5. **REFUTADO: suficiencia del observador para certificar cobertura al reiniciar.** Es una propiedad auditada del instrumento, no una afirmación de que Brain hubiera dado por cerrado el ensayo. Su selftest26 pasa, pero no detecta los contraejemplos siguientes.
6. **CONFIRMADO en el corte: restricciones de integración preservadas.** PR1 y PR17 a21 seguían abiertos/no mergeados; PR18 reviews=[] en la lectura API. No se acreditó revisión independiente que levante el hold de Abraham sobre17/18/19.
7. **NO MEDIDO: conclusión completa del experimento remoto, uso por usuarios reales y aptitud comercial.** Tres jobs verdes no son seis episodios concluidos ni una validación jurídica.

Runs del laboratorio verificados:

- NEW-CODE, PR1, head531e500ae8b073003d73f7020fd6cfd50e7dde29: run35548189544, job106177854186, success.
- OLD-DOCS, PR2, head85635ef92e8a0a72937ca55e5b507b6ceed62103: sin run en las lecturas; ausencia temporal bajo protocolo NO ACREDITADA.
- NEW-DOCS, PR3, headf39c3e93ef1bdcdcf4630fae56a6f7cd60695cee: run35548190401, job106177856329, success.
- OLD-CODE, PR4, head48eb96eff0219414ccaf1eb9b45d959ab7cf36f7: run35548189753, job106177854805, success.

Los tres jobs tienen siete steps exitosos. No se despacharon Actions en esta auditoría.

## Reproducción nueva y causalidad

La expectativa se registró antes de ejecutar: una ventana completa y sana puede producir ausencia acotada; una única consulta posterior al cierre no demuestra cobertura de la ventana. Se ejecutó observe() real en copias privadas, reemplazando solamente reloj, espera y lectura de API por fixtures deterministas. No es una nueva medición del comportamiento de GitHub.

- complete_window:21 consultas vacías completas, tiempos1000 a1300 cada15segundos. Esperado y observado: BOUNDED_ABSENCE.
- late_first_sample:una consulta en1301. Esperado: INCOMPLETE. Observado: BOUNDED_ABSENCE. Falla la propiedad.
- restart_with_error_and_stop:misma consulta tardía, más error403 y stop previamente escritos. Esperado: INCOMPLETE. Observado: BOUNDED_ABSENCE con errors=[]. Falla la propiedad.
- complete_window_repeat y late_sample_repeat: scratches nuevos; reproducen el positivo y el fallo respectivamente.
- oracle_negative_always_incomplete: copia local del instrumento cuyo verdict siempre devuelve INCOMPLETE. La MISMA expectativa del positivo rechaza este mutante tras21 consultas válidas. El oráculo no aprueba cualquier resultado.

Son una familia de defectos de cobertura/reinicio, no tres vulnerabilidades de Corpus. El mecanismo: observe() reinicia errors y samples, calcula cierre solo por now >= started+300 y consulta stop después de producir un veredicto. No exige historia persistida ni continuidad de las muestras.

Impacto: un reinicio tardío puede lavar una observación incompleta. E-01: consultar después y concluir sobre la ventana anterior. W-01: el banco del autor no alcanza a falsar esa propiedad. No se demostró explotación remota ni pérdida de datos de Corpus.

Dueño propuesto de corrección: Brain, sin asignación ni mensaje nuevos. Aceptación: positivo completo conserva BOUNDED_ABSENCE; muestra tardía única, huecos, errores persistidos y stop previo permanecen INCOMPLETE; cobertura por episodio y errores sobreviven al reinicio; stop se respeta antes de emitir un resultado; asociación evento/head/base no cambia; misma aserción rechaza mutantes. La ventana perdida no se recupera por consultar hoy. Si hacen falta nuevos episodios o una enmienda del protocolo, deben autorizarse explícitamente, no inventarse dentro de esta auditoría.

## Evidencia y límites de custodia

[Paquete publicado](https://github.com/gatehot59-star/corpus-legal-tarija/blob/89f8d95a92defb2a6d006533baf602b9b811fc57/docs/auditorias/2026-09-21-01-brain-lab-observer/evidence.xz.b64): base64 de XZ, una secuencia; decodificado JSON111342bytes, SHA256 89b922bc7ec093f9ba9b5761e76baaf1c60b31194cd0f711ce1a45eab59a67d6. Recuperado con git show y comparado byte por byte con la captura local y con el texto codificado; pertenencia a main verificada.

Incluye fuentes completas del harness ejecutado y del observador, fixtures/expectativas/resultados completos de seis probes, selftest del autor,68 comprobaciones propias, asociaciones API seleccionadas, jobs/steps/reviews, metadatos históricos y errores de preparación. Los68 checks verifican también la REPRODUCCIÓN ESPERADA del fallo: no significan68 pruebas de corrección del observador. La suite26 del autor se separa de los seis casos nuevos.

Exclusiones explícitas: cuerpos Git/AST repetidos representados por hashes y revisiones inmutables; respuestas HTTP globales y comandos completos adicionales permanecen en el taller. No se afirma publicación íntegra de las461371bytes de Brain33, cuyo hash local46e4a729db67a34e761d20601346a0758fddc8f4a419b66285005d68015e3f47 fue comprobado. No bases reales, secretos, credenciales ni binarios. Este paquete es íntegro respecto de su captura declarada, no respecto de todo el turno ni de todo el laboratorio.

Taller de recuperación: /workspace/corpus-audit-2101-cq8n2wl1. Harness /workspace/corpus-audit-2101-runner.py, SHA256650878b69d7bca131cc5b09dda010a3c12bc812fc2d2a227359e99628580b1ab. No repetirlo ciegamente: leer fuentes y efectos; contiene lecturas API y referencias congeladas.

## Qué falta para terminar una entrega que sirva

No hay porcentaje defendible ni plazo restante medido. Las estimaciones del plan17-sep son hipótesis iniciales, no saldo actual. Main conserva la demo sintética loopback; PR20 también fija documentos y usuarios sintéticos. No basta quitar esa etiqueta para habilitar cuentas reales.

1. **Cerrar el problema acotado de CI.** Corregir/revisar el observador, preservar su evidencia remota y resolver los episodios pendientes según autorización. Una carencia de cobertura no se reemplaza con111 tests repetidos. No es una nueva función del producto.
2. **Cerrar revisión e integración de la demo.** Revisión realmente ajena a la implementación de PR18 y del logout de PR20; luego integrar solo bajo permisos vigentes, probando el árbol combinado exacto. PR17/18/19 siguen bajo el hold explícito del20-sep. G2 de logout no se cierra por cambiar el nombre del auditor.
3. **Delimitar un piloto legal mínimo.** Elegir una muestra pequeña aprobada, fuentes/versiones/cobertura y responsables; obtener las decisiones legales y de privacidad pertinentes. No se acreditó un acta actual en el alcance leído; no se afirma ausencia universal a partir de una búsqueda parcial. El plan separa M01/D09 de cobro posterior.
4. **Completar el recorrido real protegido.** Cuenta y permisos reales bajo un diseño aprobado; buscar, abrir la versión exacta, guardar/compartir referencia y reportar errores sin filtrar información ajena. PR20 contiene búsqueda protegida sintética, no un piloto real. El endpoint v1/revision leído consulta una cola: eso no acredita un flujo de envío de reportes de usuarios.
5. **Probar y entregar operación real.** Entorno de prueba aprobado, respaldo/restauración y revocación pertinentes al piloto, seguridad y privacidad, prueba observada con usuarios y guía operable por un aprendiz. El restore actual es una cuarentena sintética, no evidencia de recuperación del servicio real. Recién después decidir oferta/cobro con los criterios del plan.

No hacen falta cargar todos los6079 documentos, GPU, rehacer todo Corpus ni implementar pagos antes de validar un piloto gratuito. Recomendación de prioridad, no autorización de ejecución.

Fuentes de esta separación: plan17-01/enmienda17-03; auditoría de bloqueos del piloto19-13 en3cd773babcf928f9877d89dc33b024a4a9cc1739; main sistema/api/demo_aislada.py, demo_restore.py y servidor.py; PR20 sistema/api/demo_discovery.py, protected_search.py y sistema/web/discovery_spike.html. Se leyeron los consumidores reales; no se confundió una ruta inicialmente mal escrita con ausencia de funcionalidad.

## Encargo listo para otra instancia de Astra Auditor

Copiar en una conversación nueva con ASTRA-AUDITOR-CORPUS. Esto prepara instrucciones: no invoca, asigna ni acredita aceptación de otro auditor.

> Auditá el avance nuevo de Brain en gatehot59-star/corpus-legal-tarija y su laboratorio gatehot59-star/corpus-docs-trigger-lab. Recuperá Nexus desde102/103 y cambios posteriores, inventario/método, plan y enmienda; consultá heads vivos. No mergees, despliegues, envíes mensajes ni emitas eventos remotos por esta orden. No tomes este informe como autoridad.
>
> Primero fijá tu propia expectativa de observación temporal y de reinicio, antes de usar mis resultados como esperado. Examiná Brain32/33 y las fuentes de su observador; verificá si hay una corrección posterior. Punto congelado: architect1d14895c75468953ee3e1d3d0554d1c63907684a, PR21 3b92dc432f285c00d5a45e717883c5c6e3fe46f9; observer SHA2562a727b5c2a21e9d9f197352501bfd1ffdb5aa038a64a1851396b9789eb151a3d. La fuente está íntegra en el paquete enlazado.
>
> En copias aisladas probá observe(), no solo verdict(): ventana completa, primera muestra tardía, reinicio con error/stop previo y huecos de cadencia. Separá reloj/API simulados de eventos remotos reales. Exigí positivo y falsador con la misma aserción; conservá fallos y fuentes. Una consulta actual no reconstruye la ventana histórica. No consumas los dos synchronize pendientes antes de preparación y autorización comprobadas; no abras PRs adicionales para reemplazar episodios perdidos.
>
> Verificá cuatro PRs y tres runs históricos con asociación exacta, paginación, jobs y timestamps; comprobá la custodia publicada versus local. No declares seis episodios concluidos por tres runs exitosos. Brain33 declaró INCOMPLETO: buscá evidencia de cualquier cambio de estado posterior, no inventes una falsa aprobación.
>
> Atendé los bloqueos que sí destraban entrega: PR18 en2231ca8edbe4c0b6eba88156d5abd087bbf9e51f y logout/selección de PR20 en c1e54ad0035f23d8ab549e9b16e3a6751bc1b2d2, revalidando heads. Declarar autoría es obligatorio: esta conversación implementó PR18 y el arreglo logout. Si vos también participaste, tu revisión no cierra independencia personal. Fijá casos propios antes de leer bancos del autor y medí login real, rechazo sin permiso, lectura exacta, 403/503 de logout, pérdida de respuesta antes/después de revocación, confirmaciones inválidas, retry y otra sesión B que siga válida. No exijas BFCache real sin demostrar primero que el navegador restaura ese documento.
>
> El hold de Abraham sobre17/18/19 sigue hasta revisión independiente de18; una auditoría no concede merge. Cerrá CONFIRMADO/REFUTADO/NO MEDIDO por afirmación y separá instrumento, integración y piloto. Publicá tu evidencia e informe, recuperá bytes y main, Doc público y Nexus. Dejá a Brain únicamente correcciones accionables y un siguiente paso hacia el piloto pequeño, no una lista infinita de ensayos.

## Método y control final

Funciones: revisor y verificador experimental del mismo operador, no dos auditores externos. Se usaron Git/API de lectura y Python en brain-env; herramientas de publicación autorizadas solo para documentación. No se reiniciaron ni corrigieron archivos del observador original. No hubo eventos remotos, producto, CI, permisos, mensajes, invitaciones, merges ni despliegues nuevos.

Gate I PASA para este hallazgo acotado: sujeto/llamador exactos, expectativa previa, positivo pertinente, falsador del oráculo, repetición fresca y captura declarada. HTTP real de eventos nuevos N/A porque no se emitieron. No se extrapolan mocks a fiabilidad de GitHub. El runner terminó; /proc muestra PID27469 zombie bajo PID1, no proceso ejecutándose. Escaneo de cmdline no encontró runners propios activos; no se iniciaron listeners.

Gate II PASA para alcance y razonamiento: distingue fallo del instrumento de reporte honesto, registra intentos sin hallazgo, precondiciones, corrección propuesta y prioridad. Sin nota global del producto. Errores propios: ruta protected_discovery inexistente y lectura de objeto mal referenciado corregidas por fetch/ruta demo_discovery; ps no estaba instalado, se comprobó estado por /proc; no invalidan las capturas ya verificadas.

Gate III EN CIERRE al publicar este texto: evidencia remota verificada; falta registrar readback de este informe, Doc público y Nexus. El comprobante final se agrega tras esas operaciones, sin presentarlas anticipadamente como realizadas.

¿Qué no se midió que importaba? Cobertura temporal real faltante, dos episodios restantes, revisión personal independiente18/logout, operación con una muestra legal aprobada y usuarios reales. No se habilita integración ni piloto por el resultado de esta auditoría.
