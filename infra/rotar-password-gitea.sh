#!/usr/bin/env bash
# ROTACION de la password admin de Gitea, con falsador adentro.
#
# POR QUE EXISTIA EL PROBLEMA: la password vieja (mudh-brain-2026) viajo EN
# CLARO por el buzon nexus compartido (mensajes 198-200), que leen Tachi y Sol.
# Un secreto que paso por un canal compartido esta comprometido aunque nadie lo
# haya usado: la exposicion es el hecho, el uso es una hipotesis.
#
# POR QUE ESTE ARCHIVO ESTA COMMITEADO TAL COMO CORRIO, con la password vieja
# adentro: es el rastro de auditoria de QUE se roto. Esa cadena esta MUERTA y su
# 401 se midio dos veces por caminos distintos (dentro de este script y despues
# desde una medicion aparte). Un secreto muerto documentado vale mas que un
# "se roto algo" sin sujeto. La password NUEVA no esta aca y no va a estar.
#
# ROTAR SIN MEDIR ES TEATRO. Cuatro chequeos, y cada uno puede dar rojo:
#
#   1. CONTROL POSITIVO: la vieja TIENE que andar AHORA. Si no anda, no hay nada
#      que rotar y el "exito" de abajo seria un verde vacio. Aborta.
#   2. Se rota.
#   3. La VIEJA tiene que dar 401. Si sigue dando 200, la rotacion no aplico.
#   4. La NUEVA tiene que dar 200. Si no, deje el acceso roto, que es peor.
#   5. CONTROL NEGATIVO: una password INVENTADA tiene que dar 401. Sin esto, si
#      la API no autenticara nada, los 200 de arriba no probarian nada.
#
# LO QUE ESTE SCRIPT **NO** HACE, y hay que medirlo aparte: una password rotada
# NO revoca tokens de API, NI llaves SSH, NI sesiones abiertas. Si queda
# cualquiera de las tres, el acceso sigue vivo. Medido el 2026-09-16 por la API
# (con control positivo del instrumento): tokens [] y llaves []. Ver
# 2026-09-16-rotacion-gitea.md.
#
# Uso: bash rotar-password-gitea.sh '<password-nueva>'
# Codigos de salida: 0 rotada y medida - 1 no cierra (no rotada, o rota a medias)
set -uo pipefail
API="http://127.0.0.1:3000/api/v1/user"
VIEJA='mudh-brain-2026'
NUEVA="$1"

codigo() { curl -s -o /dev/null -w '%{http_code}' -m 15 -u "brain:$1" "${API}"; }

echo "=== 1. CONTROL POSITIVO: la password vieja anda AHORA?"
ANTES=$(codigo "${VIEJA}")
echo "    vieja -> HTTP ${ANTES}"
if [ "${ANTES}" != "200" ]; then
  echo "ROJO: la vieja NO da 200. O ya fue rotada, o el instrumento no mide."
  echo "      No se rota a ciegas: abortando para no romper el acceso."
  exit 1
fi

echo "=== 2. Rotando"
sudo -u git gitea admin user change-password --username brain \
     --password "${NUEVA}" --must-change-password=false \
     --config /etc/gitea/app.ini 2>&1 | tail -3

echo "=== 3. La VIEJA tiene que estar MUERTA"
DESPUES_VIEJA=$(codigo "${VIEJA}")
echo "    vieja -> HTTP ${DESPUES_VIEJA} (se espera 401)"

echo "=== 4. La NUEVA tiene que ANDAR"
DESPUES_NUEVA=$(codigo "${NUEVA}")
echo "    nueva -> HTTP ${DESPUES_NUEVA} (se espera 200)"

echo "=== 5. Y una password INVENTADA tiene que dar 401 (control negativo:"
echo "       si diera 200, la API no autentica y los 200 de arriba no valen)"
INVENTADA=$(codigo "no-es-la-clave-$RANDOM")
echo "    inventada -> HTTP ${INVENTADA} (se espera 401)"

ROJOS=0
[ "${DESPUES_VIEJA}" = "401" ] || { echo "ROJO: la vieja SIGUE VIVA"; ROJOS=1; }
[ "${DESPUES_NUEVA}" = "200" ] || { echo "ROJO: la nueva NO entra"; ROJOS=1; }
[ "${INVENTADA}" = "401" ]     || { echo "ROJO: una password inventada entra"; ROJOS=1; }

if [ "${ROJOS}" = "0" ]; then
  umask 077
  printf 'gitea admin brain\nrotada %s\n%s\n' "$(date -u +%FT%TZ)" "${NUEVA}" \
    > /home/ubuntu/.gitea-admin-brain
  chmod 600 /home/ubuntu/.gitea-admin-brain
  echo "guardada en /home/ubuntu/.gitea-admin-brain (600):"
  ls -l /home/ubuntu/.gitea-admin-brain
  echo "VERDE: rotada y medida"
else
  echo "ROJO: la rotacion no cierra"
  exit 1
fi
