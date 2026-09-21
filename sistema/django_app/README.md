# Corpus Django: arquitectura aprobada, implementación pendiente

Decisión vinculante de esta rama: docs/adr/2026-09-21-corpus-django.md. Contratos: contracts/corpus_django.py. Este directorio NO contiene todavía una aplicación que se pueda arrancar. No ejecutar comandos de producción ni interpretar el árbol proyectado como archivos existentes.

## Lote propuesto de32 archivos

31 archivos nuevos y actualización de este README; ninguna eliminación. La confirmación habilitará construir/probar/publicar el lote en rama, abrir un PR y ejecutar suCI sintético. No habilita merge, despliegue, datos reales, rotación de credenciales ni eludir revisiones pendientes. Un Doc de cierre y continuidadNexus acompañan la entrega.

```text
sistema/django_app/
  requirements.txt                         # Django5.2.17 y transitivas fijadas tras verificación
  manage.py                                # CLI Django; no listener automático
  config/
    __init__.py                            # identidad de paquete de configuración
    settings.py                            # entornos aislados, cookies, CSRF, límites y secretos por entorno
    urls.py                                # solo rutas /corpus/, sin APIlegacy
    wsgi.py                                # entrada WSGI sin arrancar servidor
  corpus/
    __init__.py                            # identidad de paquete del dominio
    apps.py                                # configuración de app
    models.py                              # colección, grants, locators, referencias, reportes y policy state
    access.py                              # decisión ORM actual sin bypass de staff
    reader.py                              # adaptador RO al version_text existente
    services.py                            # búsqueda, referencias, reportes y recuperación
    forms.py                               # límites, validación de entrada y recuperación de cuenta
    views.py                               # sesión, CSRF, respuestas sin filtraciones ni cache
    urls.py                                # rutas internas con métodos explícitos
    migrations/
      __init__.py                          # paquete de migraciones
      0001_initial.py                      # esquema y restricciones iniciales
    management/
      __init__.py                          # paquete de comandos offline
      commands/
        __init__.py                        # descubrimiento Django de comandos
        provision_fixture.py               # usuarios/corpus sintéticos solo con opt-in
        recover_snapshot.py                # restauración cerrada y reconciliación explícita
    templates/corpus/
      login.html                           # autenticación accesible, CSRF y errores genéricos
      workspace.html                       # buscar, verificar, guardar y reportar privadamente
    tests/
      __init__.py                          # paquete de suite
      test_access.py                       # controles positivos/negativos auth, permisos, CSRF y revocación
      test_workflow.py                     # recorrido HTTP real, propiedad, búsqueda y privacidad
      test_recovery.py                     # integridad, backup viejo, cuarentena y política actual
  Dockerfile                               # build no-root, sin secretos, sin deploy
  README.md                                # quickstart probado, límites y runbook
.github/workflows/corpus-django.yml         # compilación/tests sintéticos, pin porSHA, permiso read
 docs/agents/respuestas/2026-09-21-django-delivery.md # reporte, errores, QA y deuda
 docs/agents/evidencia/2026-09-21-django-delivery.json # comandos, exit codes y salidas crudas
```

Los dos renglones docs/ son rutas desde raíz (el espacio visual no forma parte del nombre). Total29 rutas en sistema/django_app, un workflow y dos archivos de entrega=32. Este README ya existe; las otras31 son nuevas dentro del lote.

## Reutilización y no interferencia

Mantener intactos sistema/api/version_text.py, access_policy.py, isolated_login.py, los lanzadores de demo y los workflows actuales. No hacer cherry-pick implícito dePR18/20 para evadir sus revisiones. El lector ya integrado se reutiliza; las invariantes de permiso y los criterios del buscador dePR20 informan pruebas nuevas. La aplicación Django tendrá sesión propia y no consumirá credenciales de la demo.

## Definición de terminado del lote

Migraciones en SQLite temporal desde cero, Django checks, compilación, pruebas negativas y recorrido sintético completo. No guardar contraseñas ni cuerpo legal en referencias/logs, no exponer reportes privados enGit. Todos los comandos y fallos quedan en evidencia. Si no se demuestra reapertura segura con política actual, declarar recuperación incompleta, no sustituirla con un recibo de cuarentena. Rendimiento, TLS final, aprobaciones de muestra y apertura institucional se aceptan aparte, no se inventan a partir de tests locales.
