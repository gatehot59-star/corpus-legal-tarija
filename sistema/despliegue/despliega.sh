#!/bin/bash
# despliega.sh - sube la base nueva a la VM y verifica desde AFUERA.
#
# Se corre desde brain-env cuando la SuperComputer ya esta prendida. La VM no se
# puede prender desde aca: el arranque es la UI (supercomputer.abacus.ai) y el
# registro del hostname usa la metadata interna 169.254.169.254, que solo responde
# DESDE la VM. Medido: con la VM apagada los puertos 22172, 22 y 443 no contestan,
# y el hostname devuelve 404 de Cloudflare, o sea la ruta se solto.
#
# Uso:  bash despliega.sh
set -u

SSH_OPTS="-4 -i /workspace/.ssh-abacus/id_ed25519 -o StrictHostKeyChecking=no
          -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o ConnectTimeout=25"
DEST="ubuntu@150448fcc6.ssh4.abacusai.cloud"
PUERTO=22172
LOCAL="/workspace/deploy/rag-abogacia-v7.db"
REMOTO="/home/ubuntu/rag-abogacia-v7.db"
HOST_PUB="corpus-tarija.abacusai.cloud"

echo "=== 1. la VM contesta? ==="
if ! ssh $SSH_OPTS -p $PUERTO "$DEST" 'echo VIVA' 2>/dev/null | grep -q VIVA; then
  echo "ROJO: la VM no responde. Prenderla en https://supercomputer.abacus.ai"
  exit 1
fi

echo "=== 2. md5 local ==="
MD5_LOCAL=$(md5sum "$LOCAL" | cut -d' ' -f1)
echo "   $MD5_LOCAL"

echo "=== 3. parar el servicio antes de reemplazar la base ==="
ssh $SSH_OPTS -p $PUERTO "$DEST" 'sudo systemctl stop corpus-api'

echo "=== 4. respaldo en la VM y subida ==="
ssh $SSH_OPTS -p $PUERTO "$DEST" "cp -a $REMOTO ${REMOTO}.antes-del-deploy-$(date +%Y%m%d-%H%M) 2>/dev/null; true"
scp $SSH_OPTS -P $PUERTO -q "$LOCAL" "$DEST:$REMOTO"

echo "=== 5. md5 EN LA VM: tiene que ser el mismo ==="
MD5_REMOTO=$(ssh $SSH_OPTS -p $PUERTO "$DEST" "md5sum $REMOTO" | cut -d' ' -f1)
echo "   $MD5_REMOTO"
if [ "$MD5_LOCAL" != "$MD5_REMOTO" ]; then
  echo "ROJO: la base llego distinta. No se levanta el servicio."
  exit 1
fi

echo "=== 6. levantar servicios ==="
ssh $SSH_OPTS -p $PUERTO "$DEST" 'sudo systemctl start corpus-api; sudo systemctl start nginx; sleep 3; systemctl is-active corpus-api nginx'

echo "=== 7. re-registrar el hostname (la ruta se solto con el apagado) ==="
ssh $SSH_OPTS -p $PUERTO "$DEST" "bash /home/ubuntu/nuevo_host.sh $HOST_PUB" 2>&1 | tail -12

echo "=== 8. VERIFICACION DESDE AFUERA, no desde la VM ==="
sleep 25
for ruta in / /estado /estado-del-corpus; do
  printf '   %-20s -> %s\n' "$ruta" "$(curl -s -o /dev/null -w '%{http_code}' --max-time 25 "https://$HOST_PUB$ruta")"
done
echo "   /buscar?q=vendimia -> $(curl -s --max-time 25 "https://$HOST_PUB/buscar?q=vendimia" | head -c 160)"
echo
echo "si las rutas dan 200, el buscador esta publico en https://$HOST_PUB"
