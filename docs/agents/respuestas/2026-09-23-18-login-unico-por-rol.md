# 2026-09-23 18:05 · Un solo link, destino según rol

## Pedido
Usar el mismo enlace para abogados y empleados: empleado entra a su panel; abogado entra al Corpus. El panel debe gestionar credenciales.

## Decisión de seguridad
La contraseña actual no se puede mostrar: Django solo conserva su hash. El panel conserva la operación segura: generar/reemitir una nueva contraseña y mostrarla una sola vez; la anterior queda invalidada.

## Cambio
- El middleware `corpus/tracking.py` intercepta el POST exitoso de `/corpus/login/`.
- Si el usuario tiene membership activa en `corpus-empleados` y no es `PilotAccount`, redirige a `/empleados/`.
- Si es abogado, conserva la redirección a `/corpus/`.
- El enlace del portal sigue oculto dentro de Corpus: la URL pública única de acceso es `/corpus/login/`.
- La gestión de abogados ya existente genera usuario/contraseña; reemite contraseña de forma segura y elimina accesos.

## Evidencia cruda
- Staging VM: `Found 74 test(s)` / `Ran 74 tests in 2.119s` / `OK`; servicio `active`.
- Chromium vivo, mismo link `https://corpus-tarija.abacusai.cloud/corpus/login/`:
  - Luz: `employeeSameLinkUrl=https://corpus-tarija.abacusai.cloud/empleados/`, `employeePanel=true`.
  - Abogado temporal: `lawyerSameLinkUrl=https://corpus-tarija.abacusai.cloud/corpus/`, `lawyerWorkspace=true`, `lawyerNoEmployeeText=true`.
  - Alta temporal: usuario generado y contraseña de 12 caracteres; luego cuenta eliminada desde el panel (`testAccountRemoved=true`).

## NO MEDIDO
- No se implementó mostrar contraseñas históricas en texto plano porque sería incompatible con almacenamiento seguro. La reemisión de contraseña sí queda medida y disponible.
