# VM de Corpus recuperada: acceso por host y contenedor confirmado

23-oct-2026, comprobación a las 13:54 ART (UTC-3). Pedido: REVISA DE NUEVO. Operador: Astra. Repo leído y actualizado por fetch: gatehot59-star/corpus-legal-tarija, main cc151168cf8d1908225ab8723fedb0e0ed7e8367.

## Resultado nuevo, no reinterpretación del anterior

PASS acotado de conectividad: SSH desde host y contenedor terminó exit 0 y ambos alcanzaron la misma VM. Los dos /corpus/live/ públicos devolvieron HTTP 200 con cuerpo exacto ok. /corpus/login/ devolvió HTTP 200 y el formulario Corpus Tarija · Acceso, con campos de usuario y contraseña.

A las 13:54:39 ART, la VM informó uptime de 83,25 segundos. Los servicios corpus-ocr-vl, corpus-api, corpus-django-staging, cloudflared-corpus y nginx estaban loaded, active/running, con NRestarts=0 y ExecMainStatus=0. ActiveEnterTimestamp: 13:53:17 ART. Se observó el arranque; esta revisión no lo ejecutó y no identifica quién lo inició.

brain-env seguía running con su inicio anterior de las 12:54:28 ART. No hubo docker start, restart, despliegue, merge, cambio de configuración ni rotación de credenciales en esta revisión.

## Lecturas de continuidad

La VM conservaba /home/ubuntu/ocr-pr33-vl-20261023-w30qwx_f, la carpeta de la corrida terminada de dos páginas. El directorio local de repeticiones seguía conteniendo sólo preflight.json y protocol-read.md. La lista de unidades corpus-ocr mostraba sólo el servicio productivo.

Las tres inferencias nuevas por página siguen pendientes. No se lanzó ninguna en esta revisión. El chequeo no enumera todos los procesos ni todo el disco remoto y no certifica ausencia global de trabajos; antes de una tanda nueva corresponde comprobar los trabajos y procesos exactos, el parche y los hashes del fixture/runtime.

MemAvailable observado: 7341584 kB; SwapTotal y SwapFree: 4194300 kB; espacio disponible en /home/ubuntu: 40622428160 bytes. Son recursos actuales, no una garantía de memoria o duración para la próxima corrida.

## Afirmación e instrumento

- Acceso desde ambas vías: procesos SSH reales, exit 0, salida hostname vm y estado systemd. Podían rechazar la conexión, como hicieron en la revisión anterior; PASS ahora.
- Corpus responde públicamente: GET reales con código 200 y cuerpos guardados. Podían devolver App stopped; PASS en esta ventana.
- Servicio OCR activo: systemctl show sobre corpus-ocr-vl.service, active/running. Podía devolver inactive/failed; PASS de estado, no de exactitud OCR.
- Login funcional completo: sólo se leyó el formulario, sin iniciar sesión; NO MEDIDO.
- OCR exacto o repetible en seis lecturas nuevas: no hubo inferencia nueva; NO MEDIDO.
- Causa de la detención anterior, actor que arrancó la VM y permanencia futura: NO MEDIDOS. No se atribuye el incidente a inactividad ni a memoria.

El resultado de las 13:54 no borra la captura de las 13:04, cuando Abacus devolvía App stopped. Son ventanas distintas.

## Evidencia y exclusiones

Archivo: ../evidencia/2026-10-23-04-vm-acceso-recuperado.json. JSON textual con paquete reversible base64+xz+utf8-json: 2 capturas completas, una de host y otra de contenedor/HTTP, más los controles derivados separados de sus fuentes.

Paquete: 7544 bytes, SHA256 0aa09800c28253c080c0752704dab9879592947bf1c48bdcd5bd35d26f560f8a.
Contenido descomprimido: 17426 bytes, SHA256 09bbd2b5f14c7caf434549f7c7be937d53ca14a12b406bf4c47b38f9f4dfe530.

Se conservan comandos remotos, exits, stdout y stderr completos. Los valores CSRF del HTML se excluyeron antes de guardar; se verificó cada campo con un parser HTML. No se guardaron cookies, claves privadas ni configuración con secretos. No se reprodujo la clave expuesta en la revisión anterior; esa exposición no se resuelve por recuperar la VM.

Se comprobó la decodificación exacta del paquete antes de publicar. La comparación de bytes recuperados de Git y la lectura de vuelta del Doc son pasos posteriores de entrega; este archivo no se usa como prueba de su propia publicación.

## Método y alcance de cierre

TITAN LIGERO, reconsulta de estado de sólo lectura. Acción delicada: NO. Rúbrica formal N/A. Instrumentos: SSH, HTTP, Docker inspect y systemctl. Evidencia cruda y conclusiones separadas. Sin revisión externa nueva y sin orden o reporte enviado a Nexus.

Se cierra la reconsulta de acceso, no la tarea experimental de las repeticiones ni el despliegue del parche. No se cambia ningún estado de tarea en ClickUp.
