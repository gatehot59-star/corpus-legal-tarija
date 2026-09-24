# 2026-09-23 16:30 · Portal de empleados independiente + telemetría de piloto

## Pedido
La ventana de prueba piloto debía ser independiente de Corpus: empleados entran con su
contraseña, crean/eliminan usuarios de abogados, ven credenciales emitidas, y relevan
uso (tiempo, secciones) e informes de errores.

## Entregado (rama feat/ui-professional-polish, HEAD d980667)
- Portal independiente en `/empleados/` con login propio (`/empleados/login/`), marca
  "Panel de empleados", sin fachada comercial. Los abogados reciben 403; anónimos van
  al login del portal. `/corpus/piloto/` redirige al portal.
- Gestión completa de cuentas: alta (como antes), **reemisión de contraseña** (se
  muestra una sola vez, la vieja muere), **eliminación de acceso** (cuenta inactiva,
  grants revocados, historial e informes preservados, badge "Eliminada").
- Telemetría server-side (sin JS, CSP intacta): middleware `corpus/tracking.py`
  registra eventos del abogado piloto: Ingreso, Inicio, Búsqueda (con consulta),
  Catálogo (con filtros), Lectura (con uid), Referencia guardada, Informe enviado.
  Empleados y errores no se registran. `usage_for` estima páginas, visitas (sesiones
  con gap de 30 min) y minutos.
- Migración 0004 (status en PilotAccount + PilotEvent) aplicada a la DB real de staging.
- nginx: `/empleados/` ahora proxifica al Django (antes caía en el Corpus viejo y daba
  404 JSON). Backup de la config en corpus-legal.conf.bak-*.
- TIME_ZONE de display: America/La_Paz (las horas del panel son las del abogado).

## Evidencia medida
- Suite en VM: **72 tests OK** (10 nuevos de portal: login propio, abogado rechazado,
  reemisión mata la vieja, eliminación bloquea login y preserva historial, telemetría
  por sección, agregación de sesiones, empleado no se registra, redirect legado).
- Chromium en vivo (corpus-tarija.abacusai.cloud): empleado entra al portal; crea
  `valeriarojas896107`; la abogada entra por /corpus/login/, busca "expropiación" y lee;
  la abogada recibe 403 en /empleados/; el portal muestra su actividad
  ("5 páginas · 1 min · 1 visita · Último uso 23/09 16:21 · Usó: Inicio, Ingreso,
  Búsqueda"); reemisión muestra nueva contraseña y la vieja queda bloqueada; eliminación
  muestra aviso y badge Eliminada, login posterior bloqueado; /corpus/piloto/ → 302
  /empleados/. Móvil 390px: 0 overflow en el portal.
- Cuentas de prueba del debug eliminadas desde el propio portal (prueba la función).

## Pendiente honesto
- CI del PR31: application ✅, stable_identity ✅, **browser ❌**. El script de
  aceptación no toca el portal y el viaje equivalente pasó en vivo; falta el log del
  job (esta conexión GitHub no expone logs) o reproducción local con
  tests/browser_acceptance.py (la VM no tenía .venv-browser; instalación iniciada).
- La plantilla vieja pilot.html quedó huérfana tras el redirect (limpieza menor).
- Issue #29 sigue abierto para producción real (SMTP, cuentas formales, etc.).
