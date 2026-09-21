# Corpus: adopción de Django aprobada, aplicación aún por implementar

## Autoridad y estado

21-sep-2026 07:52 ART. Abraham confirmó approve_corpus_django_architecture en comentario80170047177003: adoptar Django para cuentas, permisos, reportes privados y recuperación, reutilizando módulos existentes; mantener revisiones independientes, sin despliegue de producción, datos reales, autorización general de merge ni escritura masiva. Este ADR registra esa decisión, no pide volver a aprobar Django.

Base leída y rama creada desde main5bb33ffa9d2cb01eada1a6650cc38b6629287d98. Entrega presente: tres archivos nuevos, este ADR, contracts/corpus_django.py y sistema/django_app/README.md. No cambia código ejecutado, rutas legacy, bases, configuración de despliegue o PRs abiertos. No está mergeado ni certificado por CI.

Precedentes leídos: docs/adr/2026-09-17-identidad-procedencia-v2.md; enmienda03 del17sep; diagnóstico13 del19sep; explicación02 del21sep; Nexus104/105 y mensaje214. Las revisiones18/logout siguen pendientes: mensaje214 leido0 no acredita inicio. El fallo del observadorCI no es dependencia funcional del producto.

## 1. Árbol y responsabilidades

Árbol completo propuesto del lote siguiente: sistema/django_app/README.md de esta rama. Incluye32 archivos de implementación, pruebas, migración, dos templates, contenedor, workflow y evidencia. Es un lote pendiente de confirmación, no32 archivos ya creados. Los tres archivos de esta entrega no son un lote fraccionado de implementación: materializan exclusivamente la decisión arquitectónica que se aprobó.

Raíces: contracts/ contiene DTOs e interfaces; sistema/django_app/config/ contiene settings/rutas/WSGI; corpus/ contiene dominio y adaptadores; corpus/migrations/ conserva evolución de esquema; corpus/management/commands/ contiene fixture y recuperación offline; corpus/templates/ contiene UI server-rendered; corpus/tests/ contiene pruebas causales; .github/workflows/ contiene CI separado; docs/agents/ conserva recibos. El árbol se materializará con implementación real, no con archivos vacíos para simular avance.

## 2. Decisiones técnicas

Django5.2 LTS con pin5.2.17, verificado hoy en https://www.djangoproject.com/download/ y https://pypi.org/pypi/Django/5.2.17/json. Python3.12.14 medido en brain-env, compatible con requires_python>=3.10. Django no estaba instalado; no se declara ejecución de Django en este ADR. Wheel no yanked SHA256 f04fb3b36ee119e1af4fa1d397d5fd6cf12700f49321e84d4f4c642c5b1973db. La página oficial sitúa soporte extendido5.2 hasta abril2028. Se elige LTS frente a6.1 por estabilidad del horizonte, no por falta de features.

Aviso oficial leído https://www.djangoproject.com/weblog/2026/aug/04/security-releases/:5.2.17 corrige CVE-2026-15307,15337,15830,15920. No equivale a auditoría total de dependencias. Al implementar, resolver y fijar también asgiref/sqlparse y revisar sus avisos; no inventar versiones. La aplicación no requiere GeoDjango ni admin expuesto. PBKDF2 de Django inicialmente evita agregar librería criptográfica externa; nunca contraseña literal para cuentas reales.

Monolito Django server-rendered, cookies de sesión opacas y servidor como dueño de sesión, CSRF activo, logout porPOST, SameSite=Lax y HttpOnly. Secure por defecto en perfil no-test, DEBUG=False, ALLOWED_HOSTS explícito, ningún proxy confiado por defecto. No JWT ni bearer persistido en navegador. Renombrar fixture-ana o adaptar isolated_login a usuarios reales fue descartado: rompe deliberadamente el límite de la demo y duplica funciones que Django ya mantiene.

Reutilizar sistema/api/version_text.py sin editar: SQLite snapshot inmutable abierto mode=ro, cierre de conexión explícito, hash de texto y versión exacta. No llama servidor.py ni expone /api/v1/. Su soporte actual es extracción secundaria LexiVox; otras fuentes fallan cerradas, no se etiqueta como oficial. Importar ese lector no integra ni legitima PR1.

Reutilización de políticas: preservar las invariantes de access_policy.py y sus fixtures negativos, portar la decisión a consultas ORM vinculadas al usuario/sesión Django. NO encadenar dos sesiones ni copiar tokens de los fixtures. Reutilización de PR20: contrato consulta acotada, autorización antes del texto y pruebas de aislamiento; no adoptar su catálogo máximo8 ni máximo4096 caracteres como motor real. El archivo dePR20 está en rama no integrada y su revisión no se da por cerrada.

Persistencia inicial de pruebas: SQLite temporal para datos operativos y otro archivo inmutable para corpus. No adoptar SQLite como garantía de carga productiva: la contención de escrituras y recuperación se miden en staging; PostgreSQL se considera si hay contención. Índices sobre grant(user,collection,valid_until), membership(user,group), locator(collection,uid,version), reference(owner,locator), feedback(owner,created_at). Búsqueda mínima: catálogo autorizado acotado antes de lectura; con10x documentos el escaneo crece linealmente. Limitar páginas, texto total leído y tiempo; rechazar exceso explícitamente, sin truncar silenciosamente resultados. La colección real/tamaño aún no fue aprobada y no se promete rendimiento10x. Un índice FTS por colección se añade solo con prueba de aislamiento y benchmark que lo justifique.

Guardado es referencia privada persistida, no texto exportado. No compartir enlaces públicos ni reproducir texto retirado desde un historial. Reportes privados no crean issues públicos, emails, mensajes ni adjuntos. Recuperación de cuentas usa primitives de Django y respuesta uniforme; envío real de correo y dominio exigen configuración aprobada, backend de pruebas solo captura en memoria.

## 3. Contratos

contracts/corpus_django.py compila y expone nueve DTOs inmutables, siete errores públicos y seis métodos deCorpusApplication. Son interfaces abstractas: NotImplementedError identifica un contrato, NO un servicio ejecutable ni placeholders de implementación. El artefacto presente se califica como arquitectura/contrato, nunca como sistema terminado.

Esquema objetivo: User deDjango; Membership(user,group,enabled) único; Collection(UUID,enabled,approval_evidence,snapshot_digest); DocumentLocator(collection,uid,version_sha256,withdrawn_at) único; AccessGrant(UUID,user,group,collection,origin,valid_from,valid_until,revoked_at,issued_by,evidence_id), valid_until>valid_from; PolicyState(revision,session_epoch,quarantined); SavedReference(UUID,owner,locator,created_at) único porowner/locator; PrivateFeedback(UUID,owner,locator,category,description,status,created_at). FK y restricciones en migración, no solamente clean(). Cambios de política y epoch se transaccionan. UTC consciente de zona; inicio inclusivo, fin exclusivo; grupo/colección/usuario activos; no bypass de contenido por is_staff o superuser.

Rutas nuevas bajo /corpus/, sin reemplazar APIv1/v2. GET login entrega formulario; POST login valida CSRF y presupuesto de intentos persistido, rota sesión. POST logout invalida sesión del servidor; expiración/reset invalida credenciales previas conforme a authDjango y epoch. GET búsqueda q1..128 caracteres/256bytes, offset canónico>=0, limit1..20; rechazar parámetros repetidos/desconocidos y exceder tope de cuerpo. GET lectura exige collectionUUID+uid1..200+SHA256 completo,start>=0,limit1..10000. POST guardar/reporte exige esos mismos locators y autorización fresca. Report category in(extraction,metadata,access,other), description1..2000 caracteres, texto plano escapado, sin adjuntos ni documentos completos. Respuesta reporte contiene solo UUID, fechaUTC, statusreceived. Referencias y reportes consultables solo por propietario; revisión de reportes requiere permiso operativo específico, sin privilegios sobre texto legal.

Una decisión authorize es local a la petición, nunca token reutilizable. Buscar filtra antes de abrir textos/snippets. Leer, guardar y reportar vuelven a autorizar. Habilitación se decide desde datos del servidor, jamásX-User/X-Collection. Lectura sin login:403/redirect de UI sin datos; recurso inexistente o prohibido indistinguibles; fallo operativo503 genérico; hash incorrecto no devuelve texto. Cache-Control:no-store y no logs de query/texto/credenciales.

Recuperación: backup atómico y validado por digest, destino nuevo no sobrescrito, purge de sesiones y quarantine persistente. El contrato publicado cubre restore_quarantined, no reapertura. La reapertura es un gate operativo separado: reconciliar con política actual independiente del backup, comprobar revision/epoch y retiradas, ejecutar smoke de usuario autorizado/denegado, acta explícita antes de admitir servicio. Si falta política actual, permanecer cerrado. No prometer recuperación completa cuando solo se implementó cuarentena; el lote siguiente debe documentar y probar ambos estados sin abrir un listener real.

## 4. Flujos y fronteras

Navegador no confiable -> Django CSRF/login/session -> principal servidor -> permiso ORM actual -> locator autorizado -> lector existente SQLiteRO/hash -> template escapado/no-store -> usuario.

Consulta -> sesión incluso si catálogo vacío -> filtrar grants+grupo+colección+retirada -> leer solo versiones autorizadas -> búsqueda acotada -> resultados autorizados -> nueva autorización al seguir página.

Guardar/reportarPOST -> CSRF -> principal -> permiso actual -> transacción de propiedad -> recibo privado. Nunca GitHub/ClickUp como almacén del texto privado.

Operador offline -> backup identificado y hash -> destino nuevo en cuarentena -> descartar sesiones -> política actual/epoch fuera del backup -> pruebas negativas de revocación -> decisión de reapertura aparte. Ninguna restauración arranca servicio por su cuenta.

## 5. Riesgos y mitigaciones verificables

Doble autorización incompatible: reemplazar solo la envoltura auth, no el lector; comparar matrices de invariantes. Snapshot cambiado durante lectura: digest y localización pinneados, permisos filesystemRO; fallo cerrado ante cambio. Catálogo grande: presupuesto duro y benchmark, nunca declarar búsqueda completa truncada. Revocación concurrente: snapshot transaccional por petición, siguiente petición siempre reconsulta; no prometer retirar bytes ya enviados. Feedback sensible: dueño y reviewer explícitos, escape, límites, no logs ni exportación pública. Backup viejo: epoch y política actuales independientes o no reabrir. CSRF y cache lateral: Django middleware y pruebas con enforce_csrf_checks, no confiar en cliente normal que omiteCSRF. Fixtures superan su scope: provisioning solo entorno de prueba explícito; no generar cuentas reales ni secretos fuera defixtures.

## Supuestos y aceptación del siguiente lote

Se construye una aplicación apta para identidades no ficticias, pero TODA ejecución de este lote usa usuarios y documentos sintéticos. No migrar tablaslegacy ni baseslive. No pagos, catálogo nacional completo, despliegue ni contacto institucional. Una decisión de arquitectura no es aprobación jurídica de datos, ni licencia, ni gateF08. El lote de32 archivos necesita confirmación única; no reiterar esta aprobación deDjango. Tests exigidos: login/CSRF/logout/reset, cuenta sin grant, grant futuro/vencido/revocado, grupo/colección ajenos, retirada tras página1, propiedad referencias/reportes, metadata/snippets filtrados, integridad, restore viejo y recorrido buscar-verificar-guardar-reportar. Positive controls e inyección causal deben impedir falso verde; evidencia íntegra sin datos reales. Compilar contratos no satisface ninguno de esos tests de aplicación.

## Evidencia cruda de contratos

Primer intento py_compile/import: exit1, SyntaxError línea6 '+from __future__ import annotations'. El transporte local deapply_patch conservó signos+ al inicio. No se publicó ese archivo. Se retiró exactamente un prefijo+ por línea para la fuente que se envía aGit; se verificará el SHA remoto.

Salida completa del segundo verificador, exit0:
```json
{
  "command": "compile(normalized_source, contracts/corpus_django.py, exec); exec; structural assertions",
  "exit": 0,
  "sha256": "49c4eaa175ab65d6f74c491d6a3be8a95bc1bc719495c1ae9200f27779af76ac",
  "bytes": 4910,
  "methods": ["authorize", "list_references", "read", "report_error", "save_reference", "search"],
  "checks": "import, six interfaces, seven error codes, nine immutable DTOs, public method docstrings",
  "scope": "contracts only; no runtime/security/CI claim",
  "prior_failure": "local patch transport retained + prefixes; initial compile SyntaxError, not published"
}
```

Reproducción sin requerirDjango: python3 -m py_compile contracts/corpus_django.py; importar con importlib y comprobar CorpusApplication.__abstractmethods__, len(ErrorCode)==7 y los nueve __dataclass_params__.frozen. No es validación de tipos con mypy ni tests de autenticación. No se instaló ningún runtime ni se consumieron eventosCI del laboratorio.

## QA de esta entrega, no del producto

Arquitectura41/45=91.11: completitud13/15 (secciones1-5; reapertura aún sin interfaz final), razonamiento9/10 (decisiones y límites10x sin benchmark), documentación10/10 (tree/contratos/scope), innovación4/5 (reutilización sin doble sesión y privacidad por propiedad; no mejora implementada deproducto), proceso5/5 (fuente/refs/registro y fallos). N/A55: ejecutabilidad15,seguridad15,testing15,DevOps10 deproducto. Contratos43/45=95.56: completitud14/15 (seis fronteras app y restore; reapertura no definida), ejecutabilidad15/15 (compile/import exit0), documentación9/10 (DTOs/Protocol explícitos; no schema ORM aún), proceso5/5 (salida y SHA). N/A55:seguridad15,testing15,arquitectura10,DevOps10,innovación5. Scores son autoevaluación, no revisión independiente ni permiso de merge. Estado: decisión registrada y contrato compilado EN RAMA; aplicación NO IMPLEMENTADA en esta entrega.
