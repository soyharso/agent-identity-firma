#!/usr/bin/env bash
# ==============================================================================
# CLEVERIA — THE BREAK TESTS, IN ONE BLOCK
# ==============================================================================
# The video promises "break tests, green, in a block". Running them live costs
# well over two minutes, which does not fit the shot. So this script does two
# things and keeps them apart:
#
#   ./pruebas_de_ruptura.sh          run them all, record the result
#   ./pruebas_de_ruptura.sh --resumen  print the recorded result (the shot)
#
# The summary always prints WHEN the run happened and refuses to pretend it is
# fresh. Run it right before recording; show the summary on camera.
# ==============================================================================
set -uo pipefail
cd "$(dirname "$0")"

REG="libro/pruebas_de_ruptura.json"
BOLD="\033[1m"; DIM="\033[2m"; GREEN="\033[32m"; RED="\033[31m"; YELLOW="\033[33m"; CYAN="\033[36m"; RESET="\033[0m"

# name:file:what it breaks
PRUEBAS=(
  "canonical-json:agente/killtest_canonico.py:RFC 8785 byte-for-byte, accents and integers included"
  "signature-replay:agente/killtest_reutilizacion.py:a genuine human approval cannot be moved to another case"
  "act-binding:agente/killtest_acto.py:two identical rulings do not produce interchangeable envelopes"
  "channel-port:agente/killtest_puerto_canal.py:the WhatsApp channel is decoupled from signing"
  "managed-filter:agente/killtest_blindaje.py:the vendor filter misses our Spanish attack"
  "prompt-injection:agente/killtest_inyeccion.py:8 injections, 4 languages, stopped by the ceiling"
  "key-scope:agente/killtest_alcance.py:a key cannot authorize a state outside its scope"
  "fleet-identity:agente/killtest_agente_comercial.py:two agents cannot borrow each other's key"
  "voice:agente/killtest_voz.py:a spoken judgement still requires a human signature"
  "semantic-fence:agente/killtest_cerco_semantico.py:9/9 caught, 2 false positives declared"
  "durability:agente/killtest_durabilidad.py:5 steps, 5 processes, survives an abrupt kill"
  "co-signer:agente/killtest_cofirmante.py:a second model family must agree; its silence closes the door"
)

resumen() {
  if [ ! -f "$REG" ]; then
    echo -e "${RED}No hay ninguna corrida registrada. Corre primero: ./pruebas_de_ruptura.sh${RESET}"
    exit 2
  fi
  python3 - "$REG" <<'PY'
import json, sys, time
d = json.load(open(sys.argv[1], encoding="utf-8"))
edad = int(time.time() - d["epoch"])
B, DIM, G, R, Y, C, X = "\033[1m", "\033[2m", "\033[32m", "\033[31m", "\033[33m", "\033[36m", "\033[0m"
verdes = sum(1 for p in d["pruebas"] if p["ok"])
total = len(d["pruebas"])
print()
print(f"  {B}BREAK TESTS — {verdes}/{total} GREEN{X}   {DIM}run {d['fecha']} · took {d['segundos']}s{X}")
print(f"  {DIM}{'─'*72}{X}")
for p in d["pruebas"]:
    marca = f"{G}✓{X}" if p["ok"] else f"{R}✗{X}"
    print(f"  {marca} {B}{p['nombre']:<20}{X}{DIM}{p['segundos']:>6.1f}s{X}  {p['rompe']}")
print(f"  {DIM}{'─'*72}{X}")
print(f"  {DIM}Reproduce: ./pruebas_de_ruptura.sh{X}")
if edad > 3600:
    print(f"  {Y}⚠ This run is {edad//3600}h old. Run it again before recording.{X}")
print()
PY
}

[[ "${1:-}" == "--resumen" ]] && { resumen; exit 0; }

echo -e "${BOLD}Running the break tests. This takes about two minutes.${RESET}"
echo -e "${DIM}Do not record this — record the summary afterwards.${RESET}\n"

INICIO=$(date +%s)
RESULTADOS="["
PRIMERO=1
for entrada in "${PRUEBAS[@]}"; do
  IFS=':' read -r nombre archivo rompe <<< "$entrada"
  printf "  %-22s " "$nombre"
  t0=$(date +%s.%N)
  if python3 "$archivo" >/tmp/ruptura_$$.log 2>&1; then ok=true; marca="${GREEN}✓${RESET}"; else ok=false; marca="${RED}✗${RESET}"; fi
  t1=$(date +%s.%N)
  seg=$(python3 -c "print(round($t1-$t0,1))")
  echo -e "$marca ${DIM}${seg}s${RESET}"
  [ "$ok" = false ] && { echo -e "${RED}    ↳ $(tail -3 /tmp/ruptura_$$.log | tr '\n' ' ')${RESET}"; }
  [ $PRIMERO -eq 0 ] && RESULTADOS+=","
  PRIMERO=0
  RESULTADOS+=$(python3 -c "
import json,sys
print(json.dumps({'nombre':sys.argv[1],'archivo':sys.argv[2],'rompe':sys.argv[3],'ok':sys.argv[4]=='true','segundos':float(sys.argv[5])}))
" "$nombre" "$archivo" "$rompe" "$ok" "$seg")
done
RESULTADOS+="]"
rm -f /tmp/ruptura_$$.log
FIN=$(date +%s)

python3 - "$REG" "$RESULTADOS" "$((FIN-INICIO))" <<'PY'
import json, sys, time
ruta, pruebas, segundos = sys.argv[1], json.loads(sys.argv[2]), int(sys.argv[3])
json.dump({
    "_que_es": "Resultado de la ultima corrida de las pruebas de ruptura. Lo escribe pruebas_de_ruptura.sh; se muestra con --resumen. No se edita a mano.",
    "fecha": time.strftime("%Y-%m-%d %H:%M:%S %z"),
    "epoch": int(time.time()),
    "segundos": segundos,
    "pruebas": pruebas,
}, open(ruta, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY

echo
resumen
