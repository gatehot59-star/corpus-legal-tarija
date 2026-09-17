# En criollo: hay producto y avances, falta convertirlos en una version confiable para usuarios

17-sep-2026. Abraham pregunta dónde estamos, qué tenemos, cuánto falta y si vamos bien.

## ¿Vamos bien?

**Sí en dirección técnica; todavía no estamos para cobrar ni para abrir el piloto completo.** Ya hay trabajo funcional y defectos reproducidos/corregidos, no solo una idea. Pero pasamos bastante tiempo mejorando instrumentos y planes: el siguiente avance valioso tiene que verse en una experiencia usable, no solamente en otro número de tests.

## Qué tenemos

**Corpus:** buscador y API existentes, más una colección que Brain midió a04:30UTC con6079documentos y78930pasajes. Esa lectura es de Brain; no hice un censo nuevo ahora. Sirve como activo de investigación para personas y agentes, independiente de Custos. No equivale a6079documentos revisados jurídicamente ni todos vigentes.

**Mejora nueva del corpus:** contratos de identidad/procedencia y lector nacional endurecido. En la ejecución anterior43tests pasaron yCI fue verde. El PR3 acaba de ser consultado: sigue abierto,sin merge,headb61ac872316dba4ea5b1e04d44a3a195f32c4dfa,apilado sobrePR2. Por tanto, estas correcciones están probadas en rama, **no acreditadas en la web productiva**.

**Custos:** núcleo de API probado antes por24contratos HTTP en PostgreSQL16/17, más correctivo del falsador con9tests reejecutados en la revisión previa. No es todavía un sistema profesional completo de gestión de causas ni su progreso debe confundirse con el corpus.

## Qué falta, en orden de valor

1. Revisar e integrar los cambios del lector sin romper las rutas actuales; comprobarlos en un entorno integrado antes de autorizar producción.
2. Corregir contenido concreto ymetadatos: importe de Ley483 señalado por auditoría,fechas/autoridad,edición familiar yrelaciones de vigencia. Los fixes del lector no corrigen automáticamente esos registros.
3. Preparar una colección pequeña revisada,cuentas ypermiso gratuito,guardar/compartir investigaciones yreportar errores dentro del corpus;probar privacidad yrecuperación.
4. Observar tareas reales con docentes,estudiantes yabogados. Antes de ampliar,cotejar utilidad ytiempo de revisión humana.
5. Solo después,piloto de dos universidades yoferta US$10 porperiodo confirmado;medir compra yrenovación. Pagos,soporte yfacturación todavía requieren implementación/decisiones.

## Cuánto falta

**Falta integración,calidad editorial/jurídica yexperiencia de usuario: no es un retoque de uno o dos días.** No tengo una fecha honesta hasta medir ese primer incremento yconfirmar disponibilidad de revisor/docente.

La enmienda presupuesta323h de esfuerzo hasta piloto y417h para la ruta completa,sin reserva. **Son estimaciones del plan completo,no horas restantes medidas.** No corresponde restar43tests oalgunos commits para inventar un porcentaje. Esas horas incluyen personas distintas yno son horas de máquina. La disponibilidad jurídica puede marcar el calendario más que el código.

Mi recomendación: conservar lo construido yconcentrar el próximo tramo en **buscar → verificar → guardar → reportar**,con muestra pequeña ycontroles. No rehacer el producto ni aumentar la biblioteca antes de comprobar que ese flujo le sirve a alguien.

## Fuentes y límites

[PR3 actual](https://github.com/gatehot59-star/corpus-legal-tarija/pull/3), [fix ypruebas](https://app.clickup.com/90171457413/docs/2kza6fw5-12617), [revisión de avance](https://app.clickup.com/90171457413/docs/2kza6fw5-12597), [A01/A02 deBrain](https://app.clickup.com/90171457413/docs/2kza6fw5-12557), [plan enmendado](https://app.clickup.com/90171457413/docs/2kza6fw5-12477).

Herramienta de este turno: consulta dePR3. No se ejecutó nuevamente test,censo,despliegue ni medición comercial. Síntesis de evidencia previa con una comprobación actual deestado delPR. Escrituras solo este balance yDoc;no autorización demerge ni tareas.
