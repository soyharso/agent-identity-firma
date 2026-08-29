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
gcloud run deploy cleveria-demo \
  --project="${PROJECT}" \
  --region="${REGION}" \
  --image "${IMAGE}" \
  --allow-unauthenticated \
  --set-env-vars="WA_VERIFY_TOKEN=cleveria-hackathon-2026"

echo "✅ Despliegue completado. Toma la Service URL de arriba y ponla en Meta for Developers"
echo "   (endpoint del webhook: <URL>/webhook/whatsapp)."
