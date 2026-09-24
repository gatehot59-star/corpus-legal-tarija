# Login comercial + ventana de empleados para la prueba piloto

## Pedido
1. El login debe dejar de mostrar notas técnicas y convertirse en presentación del sistema (venderse).
2. Una segunda ventana para empleados: en la entrevista con el abogado cargan nombre, apellido y matrícula opcional; el sistema genera usuario y contraseña para entregar; la misma ventana concentra los informes de fallos de la prueba piloto.

## Qué se construyó
- `login.html` comercial: titular "La ley, lista para citar.", tres puntos de valor (todo el corpus en un solo lugar, fuentes y versiones a la vista, hecho para el trabajo diario), "Acceso exclusivo para participantes de la prueba piloto". Sin notas técnicas. La respuesta de recuperación sigue byte-uniforme (sin token en modo sent).
- `/corpus/piloto/`: ventana de empleados con alta (nombre, apellido, matrícula opcional), credenciales mostradas una sola vez, guía de presentación en 4 pasos, cuentas creadas y todos los reportes de los abogados.
- `PilotAccount` (modelo + migración 0002): guarda abogado, quien lo creó y cuándo. La contraseña nunca se guarda en claro ni en el modelo.
- `services.create_pilot`: crea usuario Django, membership del grupo del operador, grant de 30 días sobre la colección habilitada y el registro de auditoría. Username derivado del nombre (maria.suarez → marasurez si hay colisión, sufijo numérico).
- `PilotForm` y vista con presupuesto de intentos ("pilot", 10/min) como login/reset/feedback.

## Errores encontrados y corregidos en la misma sesión
1. El deploy inicial no aplicó la migración 0002 (el env del servicio solo lo lee root; el migrate corría sin env y fallaba por SECRET_KEY). La página piloto daba 503. Corregido: `migrate` como root con env cargado, servicio reiniciado, verificado.
2. Dos tests nuevos fallaban por supuestos míos: el hasher de la suite es MD5 (no pbkdf2) y el login comercial ya no dice "Sin acceso público". Tests corregidos; suite final: `Ran 59 tests ... OK`.

## Evidencia cruda (Playwright contra https://corpus-tarija.abacusai.cloud)

```text
login comercial: headline y "Acceso por invitación" presentes, sin nota técnica, 3 puntos de valor, móvil 390px overflow=0
ventana piloto: carga, título "Corpus Tarija · Prueba piloto"
alta: "Cuenta lista para entregar", usuario marasurez, contraseña 12 chars, una sola vez
login del abogado generado: /corpus/ con la mesa de lectura (302 al entrar)
overflow en la ventana: 0
suite en VM: Ran 59 tests ... OK
```

## Límites honestos
- La ventana piloto hoy la puede usar cualquier cuenta autenticada con grant (en staging: abraham). Para producción hay que separar el rol empleado del rol abogado (los abogados piloto NO deberían crear cuentas). Esto queda como deuda explícita del issue #29.
- Reportes de pilotos: se listan todos; todavía sin filtros ni exportación.
- No se mergeó a `main`; CI del PR corre en GitHub.

--- METODO TITAN ---
Accion delicada: SI (alta de cuentas reales, migración en base real)
Modo aplicado: TITAN FULL
Rubrica: pendiente en PR
N/A declarados: producción, SMTP y carga no son objeto de esta feature
Review externo: pendiente en PR; silencio no es aprobación
Instrumento: Playwright real contra el alias público + suite Django 59 tests en VM; evidencia cruda arriba
