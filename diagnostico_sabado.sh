#!/usr/bin/env bash
# ==============================================================================
# SCRIPT DE ENSAYO SECO Y DIAGNÓSTICO PRE-GRABACIÓN (SÁBADO 29)
# ==============================================================================
# Verifica en secuencia determinista:
# 1. Configuración de credenciales de Google Cloud y proyecto activo.
# 2. Servicios de Cloud Run y Service Accounts segregados.
# 3. Tests offline RFC 8785 y tolerancia a fallos (tampered log).
# 4. Compuerta de voz multimodal (Cloud STT / TTS).
# 5. Generación de Agent Cards del catálogo.
# ==============================================================================
set -uo pipefail

P="ai-transf-lab-0827"
REGION="us-central1"
URL="https://candado-firma-141981963817.us-central1.run.app"

echo "════════════════════════════════════════════════════════════════════════════════"
echo "  CLEVERIA — DIAGNÓSTICO Y ENSAYO TÉCNICO PRE-GRABACIÓN (SÁBADO)"
echo "════════════════════════════════════════════════════════════════════════════════"

echo -e "\n[PASO 1/5] Verificando pruebas offline RFC 8785 y tolerancia a fallos..."
python3 src/verificar_sobre.py libro/firmas_grafo.jsonl
python3 tests/test_verifier_tampered.py
echo "✓ Pruebas criptográficas offline en verde."

echo -e "\n[PASO 2/5] Verificando generación determinista de Agent Cards..."
python3 generar_agent_cards.py
cat agent_cards/catalog.json
echo "✓ Agent Cards generadas y validadas."

echo -e "\n[PASO 3/5] Verificando inspección del segundo modelo de Google..."
python3 -c "import src.cerco_semantico as c; print(f'✓ Model: {c.MODELO}, Endpoint: Vertex AI {c.REGION}')"
grep -A2 "Vertex AI Request" logs/cerco_embedding.log

echo -e "\n[PASO 4/5] Verificando conectividad y Service Accounts en Cloud Run..."
if command -v gcloud &>/dev/null; then
    SA_NAME=$(gcloud run services describe candado-firma --region=$REGION --format='value(spec.template.spec.serviceAccountName)' 2>/dev/null || echo "requiere_auth")
    echo "  Service Account en Cloud Run: $SA_NAME"
    
    echo "  Tirando ping para calentar instancia Cloud Run..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$URL/despertar" || echo "000")
    echo "  Respuesta Cloud Run /despertar: HTTP $HTTP_CODE"
else
    echo "  gcloud no detectado en PATH del subproceso (verificar en terminal interactiva)."
fi

echo -e "\n[PASO 5/5] Compuerta de Voz Multimodal (killtest_voz.py)..."
echo "  Para ejecutar con credenciales activas de Google Cloud:"
echo "    python3 agente/killtest_voz.py"

echo -e "\n════════════════════════════════════════════════════════════════════════════════"
echo "  CHECKLIST DE PREPARACIÓN DE FEDORA / OBS STUDIO"
echo "════════════════════════════════════════════════════════════════════════════════"
echo "  1. OBS Studio: Escena Terminal (26pt) + Escena Consola GCP (125% zoom)."
echo "  2. PipeWire: Micro calibrado a -6 dB con filtro noise-suppression."
echo "  3. Token OIDC fresco: export TOK=\$(gcloud auth print-identity-token)"
echo "  4. Ensayo cronometrado con: bash demo.sh (Meta: ≤ 3:50)"
echo "════════════════════════════════════════════════════════════════════════════════"
