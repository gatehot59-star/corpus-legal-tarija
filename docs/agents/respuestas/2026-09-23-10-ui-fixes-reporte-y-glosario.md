# Correcciones visuales por screenshot del usuario + reporte con glosario

## Pedido
El usuario adjuntó un screenshot de resultados y reportó:
1. Títulos con errores de presentación: badges "Resultado" y "Versión verificada" grandes o no centradas.
2. "Reportar problema" debe aparecer en todas las instancias desde el inicio.
3. El reporte debe traer un glosario para que un abogado entienda qué es "metadata", etc.

## Medición antes (staging público, sesión de Abraham, búsqueda `inmueble`)
- Cards de resultado llevaban 2 badges redundantes (`Resultado`, `Versión verificada`) que en el screenshot se ven como figuras enormes vacías.
- Títulos largos en versalitas ocupaban 4-6 líneas por card.

## Cambios
- Cards de resultado: sin badges redundantes; título a 16px/600 con corte a 3 líneas; snippet acotado; queda la nota "Fuente secundaria · Vigencia no medida".
- Reporte disponible en toda la app:
  - Workspace: nueva tarjeta "Reportar un problema" que apunta al último documento visto/referenciado (o guía al usuario si todavía no abrió ninguno).
  - Lectura: el formulario sigue y ahora viene abierto por defecto.
- Glosario en ambos formularios:
  - Extracción: el texto se ve cortado, repetido o distinto del original.
  - Metadatos: datos del documento mal puestos (título, fecha, rubro, tipo, fuente).
  - Acceso: no podés abrir algo que creés que deberías ver.
  - Otro: cualquier otra cosa.

## Medición después (mismo instrumento)
```text
resultado card: badges=0, título 16px peso 600, altura 47px, overflow=0
workspace: tarjeta Reportar un problema presente, glosario presente
lectura: formulario abierto (details[open]), 4 ítems de glosario
búsqueda móvil 390px: overflow=0
suite en VM: Ran 54 tests ... OK
servicio: active, público 200
```

## Archivos
- `workspace.html`, `views.py`, `test_ui.py` en `feat/ui-professional-polish`, desplegado a `7f01d68`.

## NO MEDIDO
- CI del PR corre en GitHub; revisar antes de mergear.
- El glosario explica categorías; no certifica exactitud jurídica de los textos.
- No se mergeó a `main`.

--- METODO TITAN ---
Accion delicada: SI (servicio staging reiniciado)
Modo aplicado: TITAN FULL
Rubrica: pendiente en PR
N/A declarados: producción, cuentas reales, SMTP y carga
Review externo: pendiente en PR; silencio no es aprobación
Instrumento: Playwright real contra staging público + suite Django 54 tests en VM; evidencia cruda arriba
