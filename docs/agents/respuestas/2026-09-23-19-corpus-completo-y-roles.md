# 2026-09-23 19:20 · Corpus completo para empleados y gestión de roles

## Pedido
El botón Abrir Corpus del modo empleado estaba llevando a una vista sin documentos. El panel debía generar más empleados y contraseñas, dar de baja cuentas y usar claves distintas: minúscula + 4 números para empleados, mayúscula + 4 números para abogados.

## Hallazgo medido
Luz tenía membership activa en `corpus-empleados`, pero **no tenía AccessGrant** sobre la colección real. La colección real estaba habilitada; por eso Corpus renderizaba `Fuentes disponibles 0` y `Rubros detectados 0`. No era un snapshot vacío: era autorización incompleta.

## Cambio
- Migración 0005 agrega `EmployeeAccount`.
- Alta de empleado: username prefijado `emp-`, clave de una minúscula + cuatro dígitos, membership y AccessGrant explícito sobre la colección real por 365 días.
- Alta de abogado: clave de una mayúscula + cuatro dígitos, membership y AccessGrant explícito por 30 días.
- Panel: generar/reemitir/dar de baja empleados y abogados. Las contraseñas no se almacenan ni se muestran históricamente; la generada se muestra una sola vez.
- Se conservaron las rutas antiguas del panel para no romper consumidores existentes.
- Bootstrap real: perfiles y grants de Abraham y Luz creados; el panel de Luz ya tiene acceso completo.

## Evidencia cruda
- Suite staging: `Found 74 test(s)` / `Ran 74 tests in 1.730s` / `OK`.
- Chromium vivo con Luz, desde el mismo login único: `sources=[Fuentes disponibles 3, Rubros detectados 11]`, `documentCards=0` en inicio porque todavía no se abrió el catálogo, y los selectores de fuentes/rubros reales aparecen cargados.
- Alta empleado viva: `employeeUser=emp-sofiaprueba`, `employeePassword=l0613`, `employeePasswordFormat=true`.
- Alta abogado viva: `lawyerUser=carlosprueba`, `lawyerPassword=R9905`, `lawyerPasswordFormat=true`.
- Ambas cuentas temporales fueron dadas de baja desde el panel: `tempAccountsRemoved=true`.
- Servicio staging: `active`.

## Estado
Bien: el empleado ya ve la colección real completa y administra ambos tipos de cuenta desde la misma ventana.
