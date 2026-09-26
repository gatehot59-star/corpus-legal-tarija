# Producción endurecida + revisión del sistema de agentes de Custos Legis

Fecha: 2026-09-25 (noche). Pedido: dejar solo luz y abraham activos, pasar a
producción endurecida, y revisar el sistema de agentes de custos-legis-tarija.

## 1. Producción endurecida (hecho y verificado)

- **Modo synthetic eliminado** de `/etc/corpus-django-staging.env` (backup en
  `.bak-20260926-015705`). Ahora rigen: `SESSION_COOKIE_SECURE`,
  `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT`, HSTS 1 año.
- **SECRET_KEY real** presente (54 chars), no la sintética.
- **Usuarios activos: solo `luz` y `abraham`.** Desactivados: fixture-ana,
  fixture-ben, marasurez, lucafernndez, juanperez, pruebaportal741173,
  emp-rominabarrionuevo. (Los usuarios nuevos de mañana se crean desde el
  panel de empleados.)
- **Verificación en vivo**: servicio activo, live:200, login de luz entra al
  panel, flujo público por HTTPS OK. El `ready:301` en loopback HTTP es el
  redirect a HTTPS endurecido (correcto: nginx termina TLS, gunicorn no).
- **Privacidad**: el backend API viejo (`corpus-api`, python3 :8080) ya está
  en 127.0.0.1. El riesgo de Fable (0.0.0.0:8080) está mitigado en la
  práctica. (Custos aún lo lista como §9.11 NO MEDIDO; ver abajo.)

## 2. Sistema de agentes de Custos Legis: lo que hay de verdad

Leído el código real (backend/), no solo el ESTADO.md.

**Lo que existe y es sólido:**

- `corpus_cliente.py`: cliente HTTP del corpus (stdlib) que respeta ADR-001
  (corpus independiente, sin leer su SQLite). Tres estados de vigencia
  VIGENTE/DEROGADA/NO_MEDIDO con advertencia obligatoria en cada cita. La
  cadena de custodia (fuente_url, sha256, via_texto) viaja con la cita.
- `api.py`: API HTTP stdlib con los controles duros reales:
  - Sesiones con bearer token; sin tenant no hay degradación a "todos los
    bufetes" (levanta SinTenant, no amplía el WHERE).
  - **Gate HITL de acciones externas**: ninguna acción externa sale sin
    aprobación por matrícula sobre el sha256 EXACTO del contenido, y la
    ÚLTIMA decisión manda (un rechazo posterior revoca). El case_id es parte
    de la identidad de la decisión (None solo matchea None).
  - Búsqueda pasa por la compuerta de anonimización: jurisprudencia nunca
    como texto libre; normativa sí.
  - Sensor de uso con q_hash, no el texto de la búsqueda jurídica.
  - Logging con lista blanca (nunca query string ni tokens en logs).
  - Escucha en 127.0.0.1 por defecto (lección del 0.0.0.0 del corpus).
  - Fail-fast: no arranca sin Postgres con RLS.
- `plazos.py` (71/71) y `calendario_judicial.py` (36/36): motor de plazos por
  materia con Ley 439 art. 90 y CPP art. 130 bien modelados, con el día por
  día verificable.
- RLS forzado en Postgres (16/16 con PostgreSQL 16 real en CI).

**Lo que NO existe (declarado por el propio repo):**

- Los 6 agentes / grafo LangGraph: NO EXISTE. Es lo siguiente en la hoja.
- FastAPI/endpoints formales, scraper judicial, Qdrant, facturación: NO
  EXISTE.
- La compuerta CABLEADA en el buscador del corpus: NO (vive en custos, no en
  corpus-legal-tarija).

**Puntos de contacto entre Custos y Corpus que importan para mañana:**

1. Custos apunta a `BASE = https://150448fcc6.abacusai.cloud` (el dominio
   viejo). El acceso público ahí sigue siendo el staging; con producción
   endurecida en corpus-tarija.abacusai.cloud, el cliente de Custos debería
   apuntar al contrato autenticado correcto (hoy `/buscar` público da 503 por
   diseño desde el cierre). Cuando Custos se reactive, hay que darle una API
   key con scope (pendiente en corpus) en vez del endpoint público.
2. La filosofía de Custos (tres estados de vigencia, advertencia en la cita,
   hash con la cita) es exactamente la que el corpus ya implementa en UI. Hay
   convergencia de diseño: el corpus es la fuente de verdad; Custos es el
   consumidor que razona sobre expedientes.
3. El gate HITL de Custos es la pieza más valiosa y menos visible: es lo que
   hace que un agente externo pueda operar sin que nadie firme por error. Ese
   patrón debería ser el modelo para las API keys con scope del corpus.

## 3. Estado para la entrega de mañana

Corpus: listo para pilotos (producción endurecida, solo luz/abraham, 6.080
docs, UI y sesiones verificadas). Los usuarios nuevos se crean desde
/empleados/ mañana.

Custos: núcleo probado, no producto. El sistema de agentes propiamente dicho
(grafo) no existe todavía; lo que hay es la API con los controles duros que
harán que el grafo sea seguro cuando se construya. No empieza por el grafo
porque "es la parte divertida" y en el corpus eso costó 33 commits sin mover
el producto.
