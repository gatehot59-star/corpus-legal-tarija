# Cierre de integración full del Corpus real

## Pedido
Seguir hasta dejar el sistema íntegro full, corrigiendo los bloqueos que aparecieran.

## Qué se corrigió

La primera corrida remota reveló dos problemas reales:

1. `application` quedó bajo el umbral de cobertura porque el adapter nuevo no tenía tests.
2. `stable_identity` detectó que el lector marcaba como actual una versión histórica en los oráculos de exact reading.

Se agregaron tests del adapter, limpieza de snapshots parciales ante errores y la distinción correcta entre versiones históricas sintéticas y la única versión producida por el adapter real.

## Medición final

- Suite Django + cobertura: `Ran 43 tests`, `OK`, cobertura total `91%`, umbral `85%`.
- Stable identity: `success`.
- Browser CI: `success`.
- Application CI: `success`.
- Servicio VM: `active`.
- Health público: HTTP 200.
- Colección activa: 6.079 locators reales.
- Chromium público final: login de Ana, búsqueda `ley` y resultados reales visibles.
- Snapshot real, base original y permisos de aislamiento permanecen intactos.

## Evidencia cruda

```text
Found 43 test(s).
Ran 43 tests in 1.228s
OK
TOTAL 690 statements, 63 missed, 91%
active
public_live=200
enabled 1 locators 6079
PR28 checks: browser success, application success, stable_identity success
Chromium final: /corpus/?q=ley, resultados reales visibles
```

## Archivos generados

- `sistema/django_app/corpus/tests/test_real_adapter.py`, commit `b69e35825abfbf74983d9571bf79e57ce86fd6d5`.
- `sistema/django_app/corpus/management/commands/adapt_real_corpus.py`, commit `07433e57b6d1f4af84d0ff1d5911301714b45225`.
- `sistema/api/version_text.py`, commit `b6bd6af101339a6d7c2406822ec9b16dcd50b5e7`.
- Este recibo, commit posterior en `titan/adapt-real-corpus`.
- PR de integración: https://github.com/gatehot59-star/corpus-legal-tarija/pull/28.

## Estado

**Íntegro full en staging: VERDE.** El sistema integrado usa el Corpus real completo y sus flujos de autenticación, autorización, lectura exacta, búsqueda, procedencia, referencias privadas, reportes privados, logout, expiración, recuperación y aislamiento fueron verificados dentro del alcance medido.

## NO MEDIDO

No se habilitaron cuentas reales, SMTP real, producción, carga/concurrencia formal ni rollback ejercido. El merge a `main` permanece como decisión humana después de revisar PR28; los tres checks remotos ya están verdes.

--- METODO TITAN ---
Accion delicada: SI (frontera de confianza y servicio público)
Modo aplicado: TITAN FULL
Rubrica: 94/100 provisional, checks remotos verdes; merge humano pendiente
N/A declarados: cuentas reales, SMTP, producción, carga formal y rollback ejercido
Review externo: PR28 abierto; review automático solicitado, no interpretar silencio como aprobación
Instrumento: VM tunnel + suite Django + Chromium Playwright + GitHub Actions; evidencia cruda en este archivo
