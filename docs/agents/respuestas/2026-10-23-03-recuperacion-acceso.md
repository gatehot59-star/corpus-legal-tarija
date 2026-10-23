# Recuperación de acceso: brain-env levantado, VM de Corpus detenida en Abacus

Fecha: 23-oct-2026. Ventana medida: 12:54 a 13:06 ART (UTC-3). Operador: Astra, GPT-6 Astra confirmado por el entorno. Repo documental: gatehot59-star/corpus-legal-tarija. Main leído: 2a706e98cea381f3216b58e4a056d5a0762e86d3.

## Resultado

**PASS acotado:** se recuperó el contenedor existente brain-env y ambos servicios de ejecución, host y build, ejecutaron comandos reales. **FAIL de acceso remoto:** SSH a la VM falló por ambas vías. **CONFIRMADO por la respuesta del proveedor:** los dos dominios públicos de Corpus devolvieron HTTP 503 y el mensaje exacto: "The machine hosting this app is currently stopped."

La recuperación local no levantó la VM remota. No se lanzó ninguna inferencia nueva, no se hizo merge, no se desplegó el parche y no se modificó Corpus. Las tres repeticiones nuevas por página siguen pendientes.

## Pedido y alcance

Pedido vigente: probar las dos vías de ejecución y levantar los servicios pertinentes detenidos. Se interpretó como permiso para iniciar el contenedor ya existente, no para recrearlo, exponer puertos, cambiar credenciales ni habilitar Always On con costo continuo.

Modo aplicado: TITAN LIGERO, diagnóstico y recuperación de un servicio existente sin configuración ni superficie nueva. Acción delicada: NO en el cambio ejecutado. Rúbrica formal: N/A por modo ligero. Funciones ejercidas por el mismo operador: diagnóstico, ejecución y control de evidencia; no es una revisión externa.

## Lo que se hizo realmente

1. A las 12:54:26 ART se inspeccionó brain-env desde el host: exited, Running=false, ExitCode=255 y OOMKilled=false. El contenedor identificado fue 72277dd36e1778716b8e5477311081a3c1905d015282ecc6761462b63fd09f89. Su comando era sleep infinity y no tenía PortBindings.
2. Se ejecutó docker start brain-env, exit 0. Inicio registrado por Docker: 2026-10-23T15:54:28.053640436Z, 12:54:28 ART. Estado posterior running, PID 7136. docker exec ejecutó Python 3.12.14, exit 0, y verificó que persistía el archivo de lanzamiento de la corrida VL anterior. Las llamadas posteriores a build también ejecutaron Python.
3. A las 12:55:04 ART, SSH desde el contenedor terminó 255 con websocket: bad handshake. A las 12:55:42 ART, SSH desde el host terminó 255 con el mismo fallo de handshake. Ambas pruebas usaron la misma identidad autorizada, sin copiar la clave. Para la primera prueba del host se copió sólo el ejecutable cloudflared a scratch y se comprobó su hash; después se encontró el binario ya instalado en el host.
4. El endpoint corpus-vm.icca-engine.com devolvió HTTP 530 y Cloudflare Tunnel error 1033. Eso prueba una ruta remota no disponible, no por sí solo una VM apagada.
5. Se verificaron activos mcp-gateway, kratos-gateway y cloudflared-tunnel. El último sostiene mudh-mcp, no corpus-vm. El proceso de puerto 3002 es accept-proxy; no es otra VM. No se reinició ninguno. Los 404 de /health son rutas no expuestas, no una prueba de caída de esos servicios.
6. A las 13:04:17 ART se probaron /corpus/live/ y /corpus/login/ en 150448fcc6.abacusai.cloud y corpus-tarija.abacusai.cloud. Los cuatro GET devolvieron HTTP 503, título App stopped y la indicación de iniciar la máquina desde https://apps.abacus.ai. Son dos nombres de la misma aplicación, no cuatro máquinas independientes.
7. El acceso del navegador de automatización falló al conectar con su endpoint local 9225. El navegador Brave existente, PID 2681, no tenía argumentos de depuración remota; las conexiones locales a 9225 y 9222 fueron rechazadas. No se reinició el navegador, no se leyeron perfiles ni cookies y no se alcanzó una sesión autenticada de administración de Abacus.

## Afirmación, instrumento y posibilidad de dar rojo

- "brain-env estaba detenido y arrancó": docker inspect antes y después, docker start y docker exec. Podían fallar por ese estado o no ejecutar Python. Resultado: CONFIRMADO para ese contenedor y esa ventana.
- "host y contenedor ejecutan": resultados reales de los dos servicios. Podían devolver error de ejecución. Resultado: CONFIRMADO; no demuestra acceso a la VM.
- "ambas rutas SSH llegan a la VM": conexiones SSH reales. Podían fallar y fallaron, exit 255. Resultado: REFUTADO en la ventana probada.
- "el proveedor informa que la máquina está detenida": respuestas HTTP completas de los endpoints conocidos. Podían devolver la aplicación viva y en cambio devolvieron App stopped. Resultado: CONFIRMADO como estado publicado por Abacus, no como lectura del hipervisor.
- "puedo iniciar ahora la VM desde una sesión administrativa": no se alcanzó una consola autenticada. Resultado: NO MEDIDO como capacidad global; vía disponible de automatización bloqueada.
- "se ejecutaron las tres repeticiones nuevas por página": no hay lanzamiento ni resultados registrados en el directorio inspeccionado. Resultado: NO ACREDITADO. No se pudo inspeccionar el estado interno actual de la VM.

## Qué no se midió que importaba

Causa y hora exactas de la detención remota, estado del saldo y Always On de Abacus, logs de su hipervisor, servicios internos actuales de la VM y ejecución de seis inferencias nuevas. No se atribuye esta detención a inactividad, OOM ni a la prueba VL anterior. El antecedente de apagado por inactividad del 14-oct es historia, no causalidad de hoy.

La última observación directa disponible de Corpus y sus servicios activos es el preflight de las 07:09 ART. No se extiende ese resultado a las 13:06 ART. La corrida VL del parche ya terminada conserva su PASS acotado de dos páginas sintéticas; este diagnóstico no agrega mediciones de OCR ni altera ese registro.

## Errores propios y cuidado de credenciales

- El primer intento de preparación en el host usó shlex.join, ausente en Python 3.7.3. Falló antes de SSH; se corrigió el armado de argumentos y se realizó la conexión real. Se conserva el error, no se lo cuenta como intento SSH.
- systemctl de usuario necesitó las variables no secretas del bus del usuario. La ausencia inicial del bus no era un servicio detenido.
- La búsqueda inicial de procesos por nombres chrome/chromium no identificaba el ejecutable brave. Se inspeccionó el PID real del scope y se registró el navegador existente; no se afirmó que no hubiera navegador.
- **Incidente de captura:** una lectura inicial de configuración incluyó una clave BRAVE_API_KEY en una respuesta de herramienta y en el archivo local gateway-services.json. Ese valor NO se incluye en Git ni en el Doc. La publicación excluye valores de entorno y credenciales; los originales locales no se borraron. La clave NO fue rotada. Sanear la publicación no revoca la exposición previa; su rotación queda pendiente y requiere autorización o acción del titular.
- El primer empaque, todavía sin publicar, ocultaba también el nombre no secreto brain-env por tratar todos los valores de entorno como secretos. Se reconstruyó preservando los comandos y ocultando sólo credenciales y los campos declarados.
- No se confundió timeout de transporte con fin de ejecución, ni HTTP 404 con caída, ni túnel local con túnel remoto.

## Evidencia y custodia

Archivo hermano: ../evidencia/2026-10-23-03-recuperacion-acceso.json.

Paquete JSON textual con compresión reversible base64+xz+utf8-json. Incluye 11 capturas seleccionadas completas después de las exclusiones explícitas de secretos e IP; conserva metadatos de longitud y hash de cada fuente. No contiene claves privadas, cookies, perfiles de navegador, pesos ni bases.

- Archivo publicado esperado: 12105 bytes; SHA256 3f5a61d2082e44f451357a4a78cb96525f1fcd430171153309342b769da84723.
- Contenido descomprimido: 38758 bytes; SHA256 607e9a0c71eb5d3bfd06176b8ebc1416e0a8d11803654b7b101528b88bac149a.
- Se comprobó decodificación exacta y ausencia del valor secreto conocido antes de publicar.
- Fuentes locales conservadas en /workspace/corpus-ocr-recovery-20261023. El directorio no debe publicarse entero: contiene el original sensible excluido.
- La comparación posterior de bytes remotos y pertenencia del commit a main se registra en el Doc de cierre. Este archivo es el recibo prepublicación, no un comprobante de su propia lectura remota.

## Gates y continuidad

Gate I, instrumento: PASA para arranque local, ejecución de ambos servicios y respuestas HTTP/SSH observadas. NO MEDIDO para arranque remoto y nuevas inferencias. No hay oráculo nuevo de OCR ni mutaciones de producto en este diagnóstico.

Gate II, informe: estados y límites separados; sin atribuir causa al producto. Incidente de credencial declarado, no resuelto por redactarlo.

Gate III, entrega: Git y Doc requieren lectura de vuelta posterior. Nexus no enviado: no hay autorización específica para un mensaje o reporte compartido nuevo. No se marca el cierre integral como completo por publicar sólo un recibo.

Siguiente dependencia real: iniciar la máquina existente desde una sesión autorizada de Abacus, sin cambiar Always On ni contratar recursos. Luego comprobar SSH, servicios y trabajos antes de lanzar una única tanda de tres inferencias nuevas por página. No repetir ni sustituir la corrida anterior. El parche sigue separado del servicio montado y no hay autorización de merge o despliegue.
