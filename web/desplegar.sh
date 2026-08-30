#!/bin/bash
set -euo pipefail

# Despliega el servicio que recibe el formulario de cleveria.co.
#
# POR QUÉ EXISTE ESTE ARCHIVO Y NO SE DESPLIEGA A MANO. Dos veces en la misma tarde, actualizar
# la clave del correo con `--set-env-vars` **borró el usuario**, porque esa opción REEMPLAZA todas
# las variables en vez de añadir una. El servicio se quedó apuntando al buzón equivocado y el
# envío falló sin que nadie supiera por qué. Un comando escrito una vez y guardado no comete ese
# error; uno tecleado a las once de la noche, sí.
#
# LA CLAVE NO VA EN UNA VARIABLE. Va montada desde Secret Manager, por tres motivos que se notan
# el día que hay un problema:
#   · una variable de entorno la ve cualquiera que pueda describir el servicio, y sale entera en
#     los volcados de configuración;
#   · un secreto se ROTA sin volver a desplegar: se añade una versión nueva y ya;
#   · y su lectura queda registrada, así que se puede responder a «¿quién la usó y cuándo?».
#
#   Uso:  bash web/desplegar.sh
#   Antes, UNA vez, el operador sube la clave (nunca un agente):
#     printf '%s' '<clave de aplicación>' | gcloud secrets versions add smtp-clave-cleveria-web \
#       --project=cleveria-495203 --data-file=-

# El guion SE SITÚA SOLO, y no es una cortesía. `--source .` toma el directorio actual, así que
# lanzarlo desde la raíz del repositorio construía el Dockerfile de la raíz —el del candado— y
# dejaba `cleveria-web` sirviendo el servicio equivocado. Pasó, y es el mismo error que ya había
# costado un despliegue por la mañana: un guion que depende de dónde lo llamen no es un guion.
cd "$(dirname "${BASH_SOURCE[0]}")"

PROYECTO="cleveria-495203"
REGION="us-central1"
SERVICIO="cleveria-web"
SECRETO="smtp-clave-cleveria-web"
BUZON="${BUZON_SALIENTE:-softronica@gmail.com}"   # de dónde SALE el aviso
DESTINO="${CORREO_DESTINO:-info@cleveria.co}"     # a dónde LLEGA

echo "▸ Comprobando que el secreto tenga una versión…"
if ! gcloud secrets versions list "$SECRETO" --project="$PROYECTO" --limit=1 --format='value(name)' 2>/dev/null | grep -q .; then
  echo "  ✖ El secreto '$SECRETO' existe pero está VACÍO." >&2
  echo "    Súbele la clave (esto lo hace el operador, no un agente):" >&2
  echo "      printf '%s' '<clave>' | gcloud secrets versions add $SECRETO --project=$PROYECTO --data-file=-" >&2
  exit 1
fi

echo "▸ Desplegando $SERVICIO…"
# La CUENTA con la que corre el servicio, y por qué no es la de por defecto. La cuenta de
# cómputo por defecto de un proyecto trae `roles/editor`: puede crear y BORRAR secretos, tocar
# Firestore entero, desplegar servicios. Este proceso solo necesita dos cosas — escribir en una
# colección y leer una clave —, y encima está abierto a internet. Un servicio público con
# `editor` en un proyecto que además guarda las llaves de `git-crypt` es una puerta que no hace
# falta dejar abierta. Esta cuenta tiene `datastore.user` y acceso a UN secreto. Nada más.
CUENTA="sa-cleveria-web@${PROYECTO}.iam.gserviceaccount.com"

gcloud run deploy "$SERVICIO" \
  --source . \
  --region "$REGION" \
  --project "$PROYECTO" \
  --allow-unauthenticated \
  --quiet \
  --service-account="$CUENTA" \
  --set-env-vars="SMTP_USUARIO=${BUZON},CORREO_DESTINO=${DESTINO}" \
  --set-secrets="/secretos/smtp-clave=${SECRETO}:latest"

echo "▸ Comprobando de dónde lee la clave…"
URL="$(gcloud run services describe "$SERVICIO" --region "$REGION" --project "$PROYECTO" --format='value(status.url)')"
curl -s "${URL}/salud"; echo

echo "▸ Listo. Para comprobar el envío de punta a punta, desde la web pública:"
echo "   curl -s -X POST https://cleveria.co/api/contacto -H 'Content-Type: application/json' \\"
echo "     -d '{\"nombre\":\"prueba\",\"correo\":\"tu@correo\",\"detalle\":\"prueba\"}'"
echo "   Si responde \"avisado\": true, el aviso salió."
