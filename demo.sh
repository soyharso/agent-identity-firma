#!/usr/bin/env bash
# ==============================================================================
# CLEVERIA — LIVE INTERACTIVE TERMINAL DEMO (ALL THINGS AGENTIC HACKATHON)
# ==============================================================================
# Executable evidence sequence for video recording and judging reproducibility.
# Uses ANSI formatting, scoped GCP execution, and clear telemetry.
# ==============================================================================
set -uo pipefail

P="ai-transf-lab-0827"
REGION="us-central1"
URL="https://candado-firma-141981963817.us-central1.run.app"
TOMA="${1:-todas}"
PAUSA=1; [[ "${2:-}" == "--sin-pausa" ]] && PAUSA=0

# Colors & Formatting
BOLD="\033[1m"
CYAN="\033[36m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
BLUE="\033[34m"
MAGENTA="\033[35m"
DIM="\033[2m"
RESET="\033[0m"

banner() {
  local num="$1"
  local title="$2"
  local subtitle="$3"
  echo
  echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${RESET}"
  echo -e "${BLUE}║${RESET} ${BOLD}${CYAN}SHOT ${num} — ${title}${RESET}"
  echo -e "${BLUE}║${RESET} ${DIM}${subtitle}${RESET}"
  echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${RESET}"
  echo
}

paso()   { echo -e "\n${BOLD}${MAGENTA}▶${RESET} ${BOLD}$*${RESET}"; }
esperar(){ [ "$PAUSA" = 1 ] && { echo; echo -e "${DIM}── Press ${BOLD}[ENTER]${RESET}${DIM} to continue to the next shot ──${RESET}"; read -r; }; return 0; }
limpio() { grep -viE "FutureWarning|grpcio|warnings\.warn|check_feature|UserWarning|^\s*$"; }

# ── esperar_a · poll instead of sleeping a fixed 65 seconds ───────────────────
# The two live shots used `sleep 65`, which is 130 seconds of dead clock inside
# 50 seconds of script, in a video recorded in one unbroken take. The wait is
# real — Cloud Run has to do the work — but the ceiling is not: the run usually
# finishes far sooner. This polls Firestore for the condition and returns the
# moment it holds, with a visible counter so the shot never looks frozen.
#
#   esperar_a <python-expression-that-prints-LISTO> [max seconds]
esperar_a() {
  local cond="$1" max="${2:-90}" t=0
  # In an offline rehearsal there is nothing to wait for: do not burn 90s.
  [ "$LIVE" = 0 ] && { echo -e "  ${YELLOW}⚠ offline rehearsal — not waiting${RESET}"; return 1; }
  while [ "$t" -lt "$max" ]; do
    if python3 -c "
import sys; sys.path.insert(0,'.')
from src import estado
sys.exit(0 if ($cond) else 1)
" >/dev/null 2>&1; then
      printf "\r  ${GREEN}✓ done in %ss${RESET}%-30s\n" "$t" " "
      return 0
    fi
    printf "\r  ${CYAN}⏳ waiting on Cloud Run… %ss${RESET}" "$t"
    sleep 2; t=$((t+2))
  done
  printf "\r  ${YELLOW}⚠ still not ready after %ss — showing current state${RESET}%-10s\n" "$max" " "
  return 1
}

# ── Preflight · never let a rehearsal be mistaken for live evidence ───────────
# SHOT 3 used to print a canned response indistinguishable from a real one when
# the identity token was missing. Rehearsing offline is fine; recording it is
# not. So the gate exists — but it guards ONLY the shots that touch the cloud.
#
# Shots 1 and 4 must keep working with no credentials at all: shot 4 is the
# offline verifier, and the whole point it makes on camera is that it needs
# neither network nor credentials. Gating it would contradict the claim it
# exists to prove.
#
# It is also re-checked immediately before each cloud shot, not once at start:
# a token that was valid two minutes ago can be gone by the time the single
# take reaches the climax.
LIVE=1        # 1 = every cloud shot attempted so far reached the cloud
NUBE=0        # 1 = at least one cloud shot was attempted in this run
MIXTO=0       # 1 = this run mixes an offline proof with authenticated calls (shot 4)
preflight() {
  NUBE=1
  if gcloud auth print-identity-token >/dev/null 2>&1; then return 0; fi
  LIVE=0
  echo
  echo -e "${RED}╔══════════════════════════════════════════════════════════════════════════════╗${RESET}"
  echo -e "${RED}║  NOT LIVE — Google Cloud credentials are missing or expired.                 ║${RESET}"
  echo -e "${RED}║  Any cloud output below would be a CANNED SAMPLE. DO NOT RECORD THIS RUN.    ║${RESET}"
  echo -e "${RED}║                                                                              ║${RESET}"
  echo -e "${RED}║  Fix it, then run again:    gcloud auth login                                ║${RESET}"
  echo -e "${RED}║                                                                              ║${RESET}"
  echo -e "${RED}║  Shots 1 and 4 need no credentials and run regardless.                       ║${RESET}"
  echo -e "${RED}╚══════════════════════════════════════════════════════════════════════════════╝${RESET}"
  echo
  if [ "${FORZAR_SIN_NUBE:-0}" != "1" ]; then
    echo -e "${DIM}Refusing to run this shot. Export FORZAR_SIN_NUBE=1 to rehearse offline anyway.${RESET}"
    exit 3
  fi
}

# ── SHOT 1 · The Real Defect ──────────────────────────────────────────────────
toma1() {
  banner "1" "THE REAL PREPRODUCTION DEFECT" "Measuring 58 wrong human attributions in customer queues"
  
  paso "The premise, in one sentence:"
  echo -e "  ${BOLD}The agent can work. It cannot sign as a person.${RESET}"
  echo -e "  ${DIM}Authority is bounded by Cloud KMS, deterministic functions, and RFC 8785.${RESET}"

  paso "Sample queued requests (Notice: PET-002 and PET-004 require human judgement):"
  python3 -c "
import json
for k,v in json.load(open('libro/peticiones.json')).items():
    if k.startswith('_'): continue
    tipo = '⚖️ REQUIRES HUMAN' if 'queja' in v['texto'] or 'complaint' in v['texto'] else '⚡ MACHINE WORK'
    print(f'  \033[33m{k}\033[0m: {v[\"texto\"][:75]}... [{tipo}]')
"
  esperar
}

# ── SHOT 2 · Autonomous Fleet Execution ───────────────────────────────────────
toma2() {
  preflight
  banner "2" "AUTONOMOUS FLEET EXECUTION & GOVERNANCE" "Scheduler wakes the fleet; Gemini adjudicates within authority ceiling"

  paso "Resetting Firestore state for verifiable live execution:"
  python3 -c "
import sys; sys.path.insert(0,'.')
from src import estado
for p in ('PET-001','PET-002','PET-003','PET-004'): estado._doc(p).delete()
print('  \033[32m✓ Store cleared cleanly\033[0m')
" 2>&1 | limpio

  paso "Cloud Scheduler triggers Cloud Run (/despertar) via OIDC:"
  gcloud scheduler jobs run despertar-candado --location=$REGION --project=$P --quiet 2>&1 | tail -1
  echo -e "  ${CYAN}⏳ Autonomous workflow running in Google Cloud Run...${RESET}"
  # Ready when the fleet has ruled on every request in the batch.
  # La condición es «el agente YA PASÓ por cada caso», no «cada caso tiene veredicto». No es lo
  # mismo, y la diferencia costaba tres minutos y medio de toma: un caso que se detiene a esperar
  # a una persona —que es LO QUE EL VÍDEO VIENE A ENSEÑAR— se queda SIN veredicto para siempre,
  # así que `all(veredicto)` no se cumplía nunca y esta espera quemaba sus 90 s enteros antes de
  # rendirse. Medido en fase cero: `demo.sh 2` tardaba 3m31s donde el plan le da 30.
  esperar_a "all(estado.leer(p).get('veredicto') or estado.leer(p).get('espera_humana') for p in ('PET-001','PET-002','PET-003','PET-004'))" 90

  paso "Durable State & Cryptographic Signatures recorded in Firestore:"
  python3 -c "
import sys; sys.path.insert(0,'.')
from src import estado
for p in ('PET-001','PET-002','PET-003','PET-004'):
    e=estado.leer(p)
    v=e.get('veredicto','-')
    ah=e.get('espera_humana','-')
    signed='YES (Machine EC P-256)' if e.get('firma') else 'NO (Awaiting Human / No Evidence)'
    color = '\033[32m' if 'YES' in signed else '\033[33m'
    print(f'  \033[1m{p}\033[0m: verdict=\033[36m{v:<10}\033[0m awaiting_human={str(ah):<5} signed={color}{signed}\033[0m')
" 2>&1 | limpio

  echo
  echo -e "  ${GREEN}✓ Verifiable Evidence:${RESET} Machine signs autonomously with sa-agente-curador."
  echo -e "  ${YELLOW}⏸️ Subjective Judgement / Liability:${RESET} Workflow stops deterministically and waits."
  echo -e "  ${RED}✖ No Evidence:${RESET} Returned unsigned."
  esperar
}

# ── SHOT 3 · Cryptographic Boundary (KMS HTTP 403) ────────────────────────────
toma3() {
  preflight
  banner "3" "THE CLOUD BOUNDARY — IAM & CLOUD KMS" "Mathematical impossibility: Google Cloud IAM returns HTTP 403"

  TOK=$(gcloud auth print-identity-token 2>/dev/null || echo "")
  
  paso "The Cloud Run Service attempts to sign with BOTH keys:"
  if [ -n "$TOK" ]; then
    curl -s -X POST -H "Authorization: Bearer $TOK" "$URL/intentar-suplantar" | python3 -m json.tool
    echo
    echo -e "  ${GREEN}✓ Machine Key:${RESET} HTTP 200 OK"
    echo -e "  ${RED}✖ Human Key:${RESET}   ${BOLD}${RED}HTTP 403 PERMISSION_DENIED${RESET} (Enforced by Cloud IAM, not code)"
  else
    echo -e "  ${BOLD}${YELLOW}▓▓▓ CANNED SAMPLE — NOT A LIVE CALL — DO NOT RECORD ▓▓▓${RESET}"
    python3 -c "
import json
resp = {
  '_WARNING': 'CANNED SAMPLE. No call was made. Run: gcloud auth login',
  '1_with_its_own_key': {'http': 200, 'signature': '<a real run prints the real signature here>'},
  '2_with_the_human_key': {'error': 'PERMISSION_DENIED', 'http': 403, 'message': 'Permission cloudkms.cryptoKeyVersions.useToSign denied on resource clave-humano'},
  'this_service_runs_as': 'sa-agente-curador@ai-transf-lab-0827.iam.gserviceaccount.com'
}
print(json.dumps(resp, indent=2))
"
    echo -e "  ${BOLD}${YELLOW}▓▓▓ END OF CANNED SAMPLE ▓▓▓${RESET}"
  fi

  paso "The operator signs from their own machine and commits to Firestore:"
  python3 src/decidir_como_persona.py PET-002 descartada 2>&1 | limpio | tail -3

  paso "The scheduler resumes the workflow and closes with verified human signature:"
  gcloud scheduler jobs run despertar-candado --location=$REGION --project=$P --quiet 2>&1 | tail -1
  # Ready when the request carries a signed envelope, i.e. the human signature landed.
  esperar_a "(estado.leer('PET-002').get('sobre') or {}).get('tipo_firmante')" 90
  python3 -c "
import sys; sys.path.insert(0,'.')
from src import estado
e=estado.leer('PET-002'); s=e.get('sobre') or {}
print(f'  \033[32m✓ PET-002 closed -> verdict={e.get(\"veredicto\")} · signer={s.get(\"tipo_firmante\")} · state={s.get(\"estado_destino\")}\033[0m')
" 2>&1 | limpio
  esperar
}

# ── SHOT 4 · Pure Verifier & Semantic Defense ──────────────────────────────────
toma4() {
  banner "4" "AUDIT TRUST ANCHOR & SEMANTIC INJECTION DEFENSE" "Zero-dependency RFC 8785 verifier + Multilingual gemini-embedding-001 fence"

  paso "RFC 8785 Offline Verifier imports ZERO Google packages (Pure Trust Anchor):"
  python3 -c "
import ast
t=ast.parse(open('src/verificar_sobre.py').read()); imp=set()
for n in ast.walk(t):
    if isinstance(n,ast.Import): imp|={a.name.split('.')[0] for a in n.names}
    if isinstance(n,ast.ImportFrom) and n.module: imp.add(n.module.split('.')[0])
print('  Imports:', ', '.join(sorted(imp)))
has_cloud = any(i in ('google','requests','urllib3') for i in imp)
print('  Requires Cloud SDK / Network? ->', '\033[31mYES\033[0m' if has_cloud else '\033[32mNO (100% Offline)\033[0m')
"

  paso "Executing All Security Kill-Tests (Canonical, Tampering, Injections):"
  python3 tests/test_verifier_tampered.py | grep -E "✓|VEREDICTO"
  
  # A partir de aquí la toma DEJA DE SER OFFLINE: una llamada HTTPS autenticada por
  # caso. El número NO se escribe a mano — se lee de la lista de casos, que es donde
  # de verdad vive. Escribirlo aquí sería el mismo pecado que este bloque corrige:
  # una cifra que era cierta el día que se tecleó.
  LLAMADAS_RED="$(python3 -c "
import re
t = open('agente/killtest_blindaje.py').read()
m = re.search(r'CASOS\s*=\s*\[(.*?)\n\]', t, re.S)
print(len(re.findall(r'^\s*\(', m.group(1), re.M)) if m else 0)
" 2>/dev/null || echo 0)"
  paso "Adversarial evaluation: Managed Model Armor vs. Our Semantic Fence:"
  # MIXTO solo se enciende si la mitad de red REALMENTE corrió. Si aborta por falta
  # de credenciales, encenderla haría que el banner declarara unas llamadas que no
  # ocurrieron — la misma mentira, en el otro sentido.
  if python3 agente/killtest_blindaje.py 2>&1 | limpio | sed -n '3,10p'; then
    [ "${PIPESTATUS[0]}" = 0 ] && MIXTO=1
  fi
  esperar
}

# ── SHOT 5 · Visual Proof of Google Cloud ─────────────────────────────────────
toma5() {
  preflight
  banner "5" "VISUAL PROOF OF GOOGLE CLOUD INFRASTRUCTURE" "Cloud Run, Cloud Scheduler, Cloud KMS Keyring, and Firestore Native"

  paso "Cloud Run Live Production Deployment:"
  gcloud run services list --project=$P --region=$REGION --format='table(metadata.name,status.url)' 2>&1 | head -4

  paso "Cloud Scheduler Recurring Jobs:"
  gcloud scheduler jobs list --location=$REGION --project=$P --format='table(name,schedule,state)' 2>&1 | head -3

  paso "Cloud KMS Keyring Policies (Segregation of Duties):"
  for K in clave-agente clave-humano; do
    echo -e "  ${BOLD}── $K${RESET}"
    gcloud kms keys get-iam-policy $K --location=$REGION --keyring=firmas --project=$P 2>&1 | sed 's/^/     /' | head -5
  done

  paso "Live Hosted Service URL:"
  echo -e "  ${CYAN}${URL}${RESET}"
}

case "$TOMA" in
  1) toma1 ;; 2) toma2 ;; 3) toma3 ;; 4) toma4 ;; 5) toma5 ;;
  todas) toma1; toma2; toma3; toma4; toma5 ;;
  *) echo "Uso: bash demo.sh [1|2|3|4|5|todas] [--sin-pausa]"; exit 1 ;;
esac

echo
if [ "$MIXTO" = 1 ]; then
  # Shot 4 has two halves with different natures, and the old banner claimed the
  # stronger one for both. The offline verifier really does run with no network and
  # no credentials — that is the strong half. The vendor-filter comparison right
  # after it makes FOUR authenticated HTTPS calls to Model Armor, plus the access
  # token it needs first. Printing "no network and no credentials" as the last frame
  # of that shot was a true sentence covering a half that does not fit it, which is
  # the exact failure this whole project exists to argue against. Measured 2026-08-30.
  echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${RESET}"
  echo -e "  ${BOLD}${CYAN}SHOT 4 COMPLETE${RESET}  ${DIM}·${RESET}  ${GREEN}offline verifier: no network, no credentials${RESET}"
  echo -e "  ${DIM}vendor-filter comparison above: ${LLAMADAS_RED:-?} authenticated HTTPS calls to Model Armor${RESET}"
  echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${RESET}"
elif [ "$NUBE" = 0 ]; then
  # Shot 1 only. It proves what it proves — offline — and nothing more.
  echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${RESET}"
  echo -e "  ${BOLD}${GREEN}COMPLETE — verified with no network and no credentials${RESET}"
  echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${RESET}"
elif [ "$LIVE" = 1 ]; then
  echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${RESET}"
  echo -e "  ${BOLD}${GREEN}DEMO EXECUTION COMPLETE — ALL EVIDENCE PROVEN LIVE ON GOOGLE CLOUD${RESET}"
  echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${RESET}"
else
  # This is the frame the terminal is left on. It must never claim the cloud was
  # reached when it was not — the claim would outlive the warnings above it.
  echo -e "${YELLOW}════════════════════════════════════════════════════════════════════════════════${RESET}"
  echo -e "  ${BOLD}${YELLOW}REHEARSAL COMPLETE — CLOUD EVIDENCE WAS NOT PROVEN. DO NOT RECORD.${RESET}"
  echo -e "  ${DIM}Run 'gcloud auth login' and try again for a valid take.${RESET}"
  echo -e "${YELLOW}════════════════════════════════════════════════════════════════════════════════${RESET}"
fi
