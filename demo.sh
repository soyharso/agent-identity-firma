#!/usr/bin/env bash
# La demostración, en el orden del vídeo. Cada bloque es una toma.
#
#   bash demo.sh          → las cuatro tomas seguidas, con pausas
#   bash demo.sh 3        → solo la toma 3 (la que gana)
#   bash demo.sh 3 --sin-pausa
#
# Requiere: gcloud autenticado, y estar en la raíz del repositorio.
set -uo pipefail

P=ai-transf-lab-0827
REGION=us-central1
URL=https://candado-firma-141981963817.us-central1.run.app
TOMA="${1:-todas}"
PAUSA=1; [[ "${2:-}" == "--sin-pausa" ]] && PAUSA=0

titulo() { echo; echo "════════════════════════════════════════════════════════════════"; echo "  $*"; echo "════════════════════════════════════════════════════════════════"; }
paso()   { echo; echo "▶ $*"; }
esperar(){ [ "$PAUSA" = 1 ] && { echo; read -rp "   ⏎ para seguir "; }; return 0; }
limpio() { grep -viE "FutureWarning|grpcio|warnings\.warn|check_feature|UserWarning|^\s*$"; }

# ── TOMA 1 · el defecto real ────────────────────────────────────────────────────────────
toma1() {
  titulo "SHOT 1 — the real defect this comes from"
  paso "What it is, in one line:"
  head -5 README.en.md
  paso "The sample requests — one of them is a judgement about a person:"
  python3 -c "
import json
for k,v in json.load(open('libro/peticiones.json')).items():
    if k.startswith('_'): continue
    print(f'  {k}: {v[\"texto\"][:86]}')"
  esperar
}

# ── TOMA 2 · el agente trabaja solo ─────────────────────────────────────────────────────
toma2() {
  titulo "SHOT 2 — the agent wakes on its own and decides"
  paso "Clearing the store so the run is honest:"
  python3 -c "
import sys; sys.path.insert(0,'.')
from src import estado
for p in ('PET-001','PET-002','PET-003','PET-004'): estado._doc(p).delete()
print('  store cleared')" 2>&1 | limpio

  paso "Cloud Scheduler wakes the service — no person launches it:"
  gcloud scheduler jobs run despertar-candado --location=$REGION --project=$P --quiet 2>&1 | tail -1
  echo "  waiting while it processes…"; sleep 70

  paso "What it decided, read from the store:"
  python3 -c "
import sys; sys.path.insert(0,'.')
from src import estado
for p in ('PET-001','PET-002','PET-003','PET-004'):
    e=estado.leer(p)
    print(f'  {p}: verdict={e.get(\"veredicto\",\"-\"):<10} awaiting_human={str(e.get(\"espera_humana\",\"-\")):<6} signed={\"YES\" if e.get(\"firma\") else \"no\"}')" 2>&1 | limpio
  echo
  echo "  -> verifiable evidence: the MACHINE signs."
  echo "  -> a judgement about a person: the flow STOPS."
  echo "  -> no evidence: returned unsigned."
  esperar
}

# ── TOMA 3 · la que gana ────────────────────────────────────────────────────────────────
toma3() {
  titulo "SHOT 3 — the cloud says no. THIS IS THE SHOT THAT WINS."
  TOK=$(gcloud auth print-identity-token)
  paso "THE SERVICE — running as the agent — tries BOTH keys:"
  curl -s -X POST -H "Authorization: Bearer $TOK" "$URL/intentar-suplantar" | python3 -m json.tool
  echo
  echo "  -> with ITS OWN: 200. With the HUMAN key: 403 PERMISSION_DENIED."
  echo "  -> and even if it had signed, the verifier would reject it anyway."

  paso "And if asked to sign on the person's behalf without a ready signature:"
  curl -s -X POST -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
       -d '{"peticion_id":"PET-003","decision":"descartada"}' "$URL/decidir" | python3 -m json.tool
  echo
  echo "  -> \"this service cannot sign as a human, and must not\""

  paso "And the person CAN, from THEIR machine, with THEIR key:"
  python3 src/decidir_como_persona.py PET-002 descartada 2>&1 | limpio | tail -3

  paso "The scheduler picks that signature up and closes:"
  gcloud scheduler jobs run despertar-candado --location=$REGION --project=$P --quiet 2>&1 | tail -1
  sleep 70
  python3 -c "
import sys; sys.path.insert(0,'.')
from src import estado
e=estado.leer('PET-002'); s=e.get('sobre') or {}
print(f'  PET-002 -> verdict={e.get(\"veredicto\")} · signer={s.get(\"tipo_firmante\")} · state={s.get(\"estado_destino\")}')" 2>&1 | limpio
  esperar
}

# ── TOMA 4 · cualquiera lo comprueba ────────────────────────────────────────────────────
toma4() {
  titulo "SHOT 4 — anyone can verify, and the vendor filter misses"
  paso "The verifier imports NOTHING from Google:"
  python3 -c "
import ast
t=ast.parse(open('src/verificar_sobre.py').read()); imp=set()
for n in ast.walk(t):
    if isinstance(n,ast.Import): imp|={a.name.split('.')[0] for a in n.names}
    if isinstance(n,ast.ImportFrom) and n.module: imp.add(n.module.split('.')[0])
print('  imports:', ', '.join(sorted(imp)))
print('  anything from Google? ->', 'yes' if any(i in ('google','requests') for i in imp) else 'NO')"

  paso "The kill-tests, all green:"
  for k in inyeccion alcance canonico blindaje; do
    printf "  %-12s " "$k"
    python3 agente/killtest_$k.py >/dev/null 2>&1 && echo "PASA" || echo "NO PASA"
  done

  paso "Google's own injection filter against OUR attack:"
  python3 agente/killtest_blindaje.py 2>&1 | limpio | sed -n '3,12p'
  esperar
}

# ── TOMA 5 · la prueba visual de la nube, que las reglas exigen ─────────────────────────
toma5() {
  titulo "SHOT 5 — visual proof of Google Cloud (required by the rules)"
  paso "The deployed service:"
  gcloud run services list --project=$P --region=$REGION --format='table(metadata.name,status.url)' 2>&1 | head -4
  paso "The scheduler that wakes it:"
  gcloud scheduler jobs list --location=$REGION --project=$P --format='table(name,schedule,state)' 2>&1 | head -3
  paso "THE TWO KEYS AND THEIR IAM POLICIES — the difference IS the product:"
  for K in clave-agente clave-humano; do
    echo "  ── $K"
    gcloud kms keys get-iam-policy $K --location=$REGION --keyring=firmas --project=$P 2>&1 | sed 's/^/     /' | head -6
  done
  paso "The live service URL:"
  gcloud run services describe candado-firma --region=$REGION --project=$P --format='value(status.url)' 2>&1 | tail -1
}

case "$TOMA" in
  1) toma1 ;; 2) toma2 ;; 3) toma3 ;; 4) toma4 ;; 5) toma5 ;;
  todas) toma1; toma2; toma3; toma4; toma5 ;;
  *) echo "uso: bash demo.sh [1|2|3|4|5|todas] [--sin-pausa]"; exit 1 ;;
esac

echo
echo "════════════════════════════════════════════════════════════════"
echo "  end of demo"
echo "════════════════════════════════════════════════════════════════"
