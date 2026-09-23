# 2026-09-23 17:55 · Portal de empleados oculto dentro de Corpus

## Pedido
La opción de empleado no debe verse al entrar a Corpus, tampoco por empleados, y los abogados no deben conocerla desde esa interfaz.

## Cambio
- El branch `feat/ui-professional-polish` agrega una garantía server-side en `sistema/django_app/corpus/tracking.py`: las respuestas HTML de Corpus eliminan el enlace visible `Panel de empleados`.
- El portal sigue disponible únicamente por `/empleados/login/` y `/empleados/`.
- El test `test_workspace_hides_employee_portal_from_everyone` comprueba que no aparece ni para lectores ni para empleados.

## Evidencia cruda
- VM staging: `manage.py test corpus`
- Salida: `Found 72 test(s)` / `Ran 72 tests in 1.757s` / `OK`
- Servicio: `active`
- Chromium contra `https://corpus-tarija.abacusai.cloud`: empleado Luz entra a Corpus y obtiene `employeeNoPortalOption=true`; Corpus sigue funcionando (`employeeCorpusWorks=true`); login comercial no contiene `empleados` (`loginNoPortalOption=true`).
- Commit remoto: `af6984c ui: strip employee portal link from Corpus responses`.

## Estado
Bien: la opción no se ve dentro de Corpus. El portal independiente sigue operativo por su URL propia.
