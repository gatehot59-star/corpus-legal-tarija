# Causa exacta de `TargetClosed` en Chromium

Fecha: 21-sep-2026 ART. Investigación de entorno sobre la auditoría de PR24; no modifica Corpus, no mergea ni despliega.

## Veredicto

`TargetClosed` no lo causaba PR24 ni Django. Chromium se cerraba por una dependencia ambiental de fuentes: al renderizar la página, Skia intentaba inicializar Fontconfig y abortaba con:

```text
FATAL: third_party/skia/src/ports/SkFontMgr_FontConfigInterface.cpp:163
Not implemented.
process did exit ... signal=SIGTRAP
```

El log previo también decía:

```text
Fontconfig error: Cannot load default config file: File not found
```

La causa fue que el `LD_LIBRARY_PATH` usado para rescatar las bibliotecas gráficas de Chromium incluía el sysroot del navegador, pero no una instalación utilizable de Fontconfig ni un `fonts.conf`. `ldd` mostró `libglib` y varias bibliotecas ausentes en el primer arranque; el inventario confirmó que el entorno tenía `libfontconfig`, `libfreetype` y `libglib` en `/workspace/ocrenv/lib`, fuera de ese path.

## Separación de fallos

Hubo tres cierres ambientales distintos, todos manifestados por Playwright como `TargetClosed`:

1. Headless inicial: Chromium ni arrancaba, `libglib-2.0.so.0` ausente, exit 127.
2. Canal Chromium completo: `libcups.so.2` ausente, exit 127.
3. Headless después de agregar el sysroot: Chromium arrancaba, atendía GET/POST y recibía `302/200`, pero al renderizar la segunda página abortaba en Fontconfig con SIGTRAP. Este es el `TargetClosed` que parecía un fallo de la aplicación.

El segundo y tercer caso no deben mezclarse: el segundo es un loader failure; el tercero es un abort del renderer al usar fuentes.

## Control causal

Se repitió una sonda mínima sobre PR24, sin tocar el código:

- Sin Fontconfig usable: `TargetClosed`, página cerrada, browser desconectado, SIGTRAP en Skia.
- Con `LD_LIBRARY_PATH=/workspace/ocrenv/lib:<sysroot>` y `FONTCONFIG_FILE=/workspace/ocrenv/etc/fonts/fonts.conf`: página estable después del login, `browser.is_connected() = true`, sin cierre.
- Con ese entorno corregido se repitió el recorrido completo: **25 controles PASS**, incluidos login, lectura exacta, hash, procedencia, guardado, reporte escapado, logout, replay de sesión, aislamiento de usuario, móvil, recuperación de contraseña, token de un solo uso y revocación. Sin excepciones de página, sin solicitudes fuera de loopback y servidor detenido al final.

La corrección es del entorno de prueba, no del producto. No se instaló ningún paquete ni se editó configuración de Corpus. El `TargetClosed` queda explicado y reproducido causalmente.

## Qué cambia en la auditoría de PR24

La corrida anterior quedó correctamente como parcial porque no conocía la causa. Con el entorno de fuentes corregido, el E2E independiente de PR24 pasa en Chromium 153.0.8010.12. Esto **no levanta por sí solo** la revisión humana ni autoriza el merge: PR24 sigue abierto y sin review independiente.

## Evidencia

La evidencia incluye logs del crash, `ldd`, la sonda mínima, el resultado con el entorno corregido y el resultado completo de 25 controles. No contiene cuentas reales, secretos, correo real ni datos jurídicos.
