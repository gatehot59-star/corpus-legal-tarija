# 2026-09-04 · La llave SSH no es un botón de encendido, y mi sonda de endpoints se refutó sola

Abraham insiste, con razón de fondo: me dio la llave SSH, entonces por qué no la prendo. Fui a medirlo en vez de repetir el "no puedo".

## 1. Qué hace una llave SSH y qué no

La llave **autentica** contra un `sshd` que ya está escuchando. No enciende hardware. Medido contra la VM:

```
ip: 208.122.8.11
   puerto 22172  sin respuesta (errno 11)
   puerto 22     sin respuesta (errno 11)
   puerto 443    sin respuesta (errno 11)
```

`errno 11` es timeout, no "conexión rechazada". Con la máquina apagada no hay proceso que reciba la llave: es la llave correcta de una puerta que no está enchufada. Si el problema fuera de permisos vería `Permission denied (publickey)`, y eso **sí** sería mío.

## 2. El SDK oficial no tiene el método

Instalé `abacusai 1.4.111` en brain-env y lo inventarié en vez de suponer:

```
metodos totales: 645
con personal / agent_computer / computer:
   execute_chatllm_computer_streaming
   get_personalized_ranking
con start / stop / resume / wake / boot / power:
   restart_document_retriever, resume_pipeline_refresh_schedule,
   resume_refresh_policy, start_autonomous_agent, start_batch_prediction,
   start_deployment, stop_deployment
```

Hay `start_deployment` y `stop_deployment`, que son **despliegues de modelos**, no la SuperComputer. Ningún método toca la computadora personal. E-01: no confundir el sujeto por parecido de nombre.

## 3. Mi sonda de endpoints SE REFUTÓ SOLA, y por eso esto queda NO MEDIDO

Sabía que existe una familia interna de endpoints, porque `nuevo_host.sh` **la usó con éxito** el 4-sep: `addPersonalAgentComputerHostname`. Así que probé nombres hermanos contra `api.abacus.ai`, incluyendo un control negativo inventado:

```
addPersonalAgentComputerHostname   404  "Action ... not found"   <-- ESTE SÍ EXISTE
listPersonalAgentComputers         404  "Action ... not found"
startPersonalAgentComputer         404  "Action ... not found"
stopPersonalAgentComputer          404  "Action ... not found"
metodoQueNoExisteEnLaVida          404  "Action ... not found"   <-- control
```

**El endpoint que sé que funciona contesta lo mismo que uno que inventé.** O sea el instrumento no distingue existente de inexistente: `api.abacus.ai` no es el servidor que sirve esas acciones. `nuevo_host.sh` no usa una URL fija, usa el `api_base_url` que saca de la metadata interna `169.254.169.254`, y esa metadata **solo responde desde dentro de la VM**.

Conclusión metodológica: **no puedo declarar "el endpoint para prenderla no existe"**. Solo puedo declarar que desde afuera no sé ni contra qué servidor preguntar. Eso es NO MEDIDO, no rojo. Sin el control positivo habría reportado con seguridad una conclusión falsa.

## 4. Lo que sí me habilitaría a intentarlo

Dos datos que hoy no tengo, y que la VM apagada se llevó consigo:

1. La **API key** de la cuenta (`https://abacus.ai/app/profile/apikey`).
2. El **`api_base_url`** y el **`personal_agent_computer_id`**, que vivían en la metadata interna de la VM.

Con la key puedo buscar el `api_base_url` correcto y probar la familia de acciones con un control válido. Sin eso, la vía documentada por Abacus es una sola: la UI de `supercomputer.abacus.ai`.

## 5. Lo que no cambia

El despliegue sigue listo en un comando (`sistema/despliegue/despliega.sh`), probado contra la VM apagada: falla en el paso 1 con el mensaje correcto y no toca nada. Base en `/workspace/deploy/rag-abogacia-v7.db`, md5 `87b2aa0a43e2a8ad2945fa5e246a9b00`, guard VERDE 9/9.
