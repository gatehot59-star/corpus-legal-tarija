# Auditoría independiente de PR24 en copia nueva

Fecha: 21-sep-2026 ART. Alcance: PR24 únicamente, sin merge, despliegue, datos reales ni cambios en el repositorio remoto.

## Sujeto exacto

- PR24: `0da5c5f046af88941fe9900829c37d727a8c09ce`
- Base PR23: `777ca6374989ac042ddf7cb8275a7e3c7bdf7da2`
- Main al iniciar: `5bb33ffa9d2cb01eada1a6650cc38b6629287d98`
- PR24 sigue abierto, no mergeado, con un check `application` exitoso y reviews vacías.

Se usó una copia nueva del repositorio y un entorno virtual nuevo para las dependencias Django del PR. El diff PR23→PR24 tiene exactamente cuatro archivos: dos recibos documentales, el cambio de `SECURE_REFERRER_POLICY` de `no-referrer` a `same-origin`, y una regresión de login.

## Resultado

**No encontré un defecto nuevo en el cambio de PR24 dentro del alcance medido. El arreglo conserva CSRF y mantiene rechazados `Origin: null` y orígenes externos.**

La aceptación independiente queda **PARCIAL**, no cerrada como aprobación de merge: el recorrido Chromium completo en la copia nueva volvió a terminar en `TargetClosed` después del primer control HTTP, igual que el límite ya declarado por Brain. Por eso no presento el recorrido de navegador del recibo de PR24 como una medición propia.

## Pruebas nuevas

1. `manage.py check`: pasa.
2. `makemigrations --check --dry-run`: pasa, sin cambios.
3. Suite fresca de PR24: **39 tests, exit0**, 5,649 segundos.
4. Cobertura fresca: **93%** de la aplicación, excluyendo tests y migraciones.
5. Matriz HTTP con Django `Client(enforce_csrf_checks=True)` sobre la copia:

   - same-origin explícito: `302`
   - `Origin: null`: `403`
   - origen externo: `403`
   - sin `Origin`: `302`

6. Falsador de configuración: revertir `same-origin` a `no-referrer` hace fallar la nueva regresión antes del login.
7. Falsador de seguridad: quitar `CsrfViewMiddleware` hace fallar la prueba porque desaparece la cookie CSRF. El banco sí distingue el arreglo de una desactivación de CSRF.
8. Diff check: sin errores de whitespace.
9. Chromium real en la copia nueva: anonimato `403` correcto; luego `TargetClosed` antes de completar login/DOM. No se atribuye a PR24 sin aislarlo; queda como NO MEDIDO en esta corrida.

## Cadena causal

El cambio productivo es una sola línea de configuración. La regresión comprueba explícitamente que la política es `same-origin`, que un `Origin: null` sigue siendo rechazado y que un origen del sitio puede iniciar sesión con CSRF activo. Los dos mutantes relevantes fueron rechazados. La prueba HTTP no reemplaza al navegador: solo valida el contrato del servidor.

No se auditaron carga 10x, TLS/proxy productivo, cuentas reales, correo real, accesibilidad completa ni revisión humana independiente. Tampoco se tocó PR22, PR23, PR18, PR20, PR21 ni el laboratorio de CI.

## Veredicto y siguiente paso

- **CONFIRMADO:** PR24 contiene el cambio acotado declarado; CI verde; suite y cobertura frescas; CSRF y rechazo de orígenes peligrosos preservados.
- **CONFIRMADO:** los falsadores de revertir la política y quitar CSRF producen rojo.
- **NO MEDIDO:** recorrido Chromium completo independiente en esta copia, por `TargetClosed`.
- **NO AUTORIZADO:** merge o despliegue.

Siguiente paso correcto: revisión humana/externa del PR24 y resolver la causa del `TargetClosed` o conseguir una corrida de navegador reproducible en un entorno controlado. No hace falta otra arquitectura ni otra auditoría general.

Evidencia: `evidence.json` en la carpeta hermana, con heads, diff, comandos, resultados, mutantes y límite del navegador.
