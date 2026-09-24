# Separación de roles: empleado vs abogado piloto

## Pedido
Separar el rol empleado del rol abogado: la ventana de prueba piloto es solo para empleados; el abogado piloto lee el corpus y nada más.

## Qué se construyó
- Grupo `corpus-empleados` (migración 0003, idempotente). Las membresías las asigna un operador; en staging Abraham quedó empleado.
- `access.is_employee` / `require_employee`: solo miembros habilitados del grupo. Un abogado piloto queda fuera **aunque alguien lo agregue al grupo** (el registro PilotAccount lo excluye). Staff/superuser sigue sin ser bypass.
- `/corpus/piloto/` ahora exige el rol empleado.
- El enlace "Prueba piloto" en la mesa de lectura solo aparece para empleados.

## Error encontrado y corregido en la misma sesión
El primer test de denegación agregaba al abogado al grupo a mano, pero `create_pilot` ya le había dado esa membresía: IntegrityError por la constraint única. El test ahora verifica la denegación con el login real de la cuenta creada, que es la prueba que importa.

## Evidencia cruda (Playwright contra https://corpus-tarija.abacusai.cloud)

```text
empleado (abraham): workspace con enlace "Prueba piloto", /corpus/piloto/ carga ("Alta de abogado")
alta desde la ventana: usuaria lucafernndez, contraseña 12 chars, mostrada una sola vez
abogada (sesión real con esa contraseña): /corpus/ carga y NO ve el enlace; /corpus/piloto/ => 403
suite en VM: Ran 62 tests ... OK
migración 0003 aplicada en la base real; servicio active; alias 200
```

## Límites honestos
- Los reportes que ven los empleados incluyen los de todos los usuarios; eso es el punto del relevamiento, pero en producción conviene filtrar por período y exportar. Sigue en deuda.
- El alta de nuevos empleados hoy es por consola (operador); una consola web de roles queda pendiente en issue #29.
- No se mergeó a `main`; CI del PR corre en GitHub.

--- METODO TITAN ---
Accion delicada: SI (frontera de autorización, migración y alta en base real)
Modo aplicado: TITAN FULL
Rubrica: pendiente en PR
N/A declarados: producción, SMTP y carga no son objeto de esta feature
Review externo: pendiente en PR; silencio no es aprobación
Instrumento: Playwright real contra el alias público + suite Django 62 tests en VM; evidencia cruda arriba
