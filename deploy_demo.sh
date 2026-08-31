#!/bin/bash
set -euo pipefail

# Despliega cleveria-demo sirviendo app_real.py (webhook /webhook/whatsapp + UIs).
#
# NO usar `gcloud run deploy --source=.`: ese modo de build usa el Dockerfile
# de la raíz del repo (el que arma servicio/main.py), sin importar que exista
# Dockerfile.demo. Por eso el servicio terminaba sirviendo el contenedor
# equivocado (webhook daba 404). La vía correcta es construir la imagen
# aparte con Dockerfile.demo vía Cloud Build (cloudbuild.demo.yaml) y
# desplegar esa imagen.

PROJECT="ai-transf-lab-0827"
REGION="us-central1"
IMAGE="gcr.io/${PROJECT}/cleveria-demo"

echo "🚀 Verificando credenciales de aplicación (gcloud auth application-default)..."
gcloud auth application-default print-access-token >/dev/null 2>&1 || \
  echo "⚠️ Si esto falla, corre 'gcloud auth application-default login' manualmente."

echo "📦 Construyendo imagen con Dockerfile.demo (app_real.py) vía Cloud Build..."
gcloud builds submit --config cloudbuild.demo.yaml --project="${PROJECT}" .

echo "☁️  Desplegando ${IMAGE} en Cloud Run (${PROJECT}/${REGION})..."
# LA IDENTIDAD VA EXPLÍCITA, y esto no es redundancia. El 2026-08-31 se descubrió que este
# servicio corría con la CUENTA POR DEFECTO DE COMPUTE —con escritura en Firestore a nivel de
# proyecto y abierto a todo el mundo— y se le creó `sa-demo`, con cuatro permisos y NINGUNO de
# firma. Este script no la nombraba: hoy la conserva porque Cloud Run mantiene la del servicio
# existente, pero el día que alguien despliegue sobre un servicio nuevo, o que lo borre y lo
# vuelva a crear, la corrección se pierde en silencio y nadie se entera.
# Una garantía que depende de que nadie recree el servicio no es una garantía.
gcloud run deploy cleveria-demo \
  --project="${PROJECT}" \
  --region="${REGION}" \
  --image "${IMAGE}" \
  --service-account "sa-demo@${PROJECT}.iam.gserviceaccount.com" \
  --allow-unauthenticated \
  --update-env-vars="WA_VERIFY_TOKEN=cleveria-hackathon-2026"

# `--update-env-vars` Y NO `--set-env-vars`, Y ESTO COSTÓ UNA HORA DE DEPURACIÓN A CIEGAS.
# `--set-env-vars` REEMPLAZA el conjunto entero: al desplegar con una sola variable, borra
# todas las demás. Así desapareció `GOOGLE_CLIENT_ID` en cada despliegue posterior a haberlo
# configurado, y el síntoma era el peor posible — nada fallaba. El servicio arrancaba bien,
# `/api/config` respondía 200, y solo devolvía el identificador vacío, así que la pantalla se
# comportaba exactamente igual que antes de existir el login. Se buscó en la caché del
# navegador, en el código y en Google antes de mirar aquí.
# La forma de verlo es preguntarle al navegador qué recibió, no leer el código.

echo "✅ Despliegue completado. Toma la Service URL de arriba y ponla en Meta for Developers"
echo "   (endpoint del webhook: <URL>/webhook/whatsapp)."
