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
  titulo "TOMA 1 — el defecto real del que sale todo"
  paso "El componente y su promesa, en una línea:"
  head -5 README.en.md
  paso "El texto de las peticiones de ejemplo — una de ellas es un juicio sobre una persona:"
  python3 -c "
import json
for k,v in json.load(open('libro/peticiones.json')).items():
    print(f'  {k}: {v[\"texto\"][:88]}')"
  esperar
}

# ── TOMA 2 · el agente trabaja solo ─────────────────────────────────────────────────────
toma2() {
  titulo "TOMA 2 — el agente despierta solo y decide"
  paso "Limpiar el almacén para que la corrida sea honesta:"
  python3 -c "
import sys; sys.path.insert(0,'.')
from src import estado
for p in ('PET-001','PET-002','PET-003'): estado._doc(p).delete()
print('  almacén limpio')" 2>&1 | limpio

  paso "El temporizador de la nube despierta al servicio (no lo lanza una persona):"
  gcloud scheduler jobs run despertar-candado --location=$REGION --project=$P --quiet 2>&1 | tail -1
  echo "  esperando a que procese…"; sleep 70

  paso "Lo que decidió, leído del almacén:"
  python3 -c "
import sys; sys.path.insert(0,'.')
from src import estado
for p in ('PET-001','PET-002','PET-003'):
    e=estado.leer(p)
    print(f'  {p}: veredicto={e.get(\"veredicto\",\"-\"):<10} espera_persona={str(e.get(\"espera_humana\",\"-\")):<6} firma={\"SÍ\" if e.get(\"firma\") else \"no\"}')" 2>&1 | limpio
  echo
  echo "  → evidencia comprobable: la MÁQUINA firma."
  echo "  → un juicio sobre una persona: el flujo SE DETIENE."
  echo "  → sin evidencia: se devuelve sin firma."
  esperar
}

# ── TOMA 3 · la que gana ────────────────────────────────────────────────────────────────
toma3() {
  titulo "TOMA 3 — la nube le dice que no. ESTA ES LA TOMA QUE GANA."
  TOK=$(gcloud auth print-identity-token)
  paso "EL SERVICIO —que corre como el agente— intenta firmar con las DOS claves:"
  curl -s -X POST -H "Authorization: Bearer $TOK" "$URL/intentar-suplantar" | python3 -m json.tool
  echo
  echo "  → con la SUYA: 200. Con la de la PERSONA: 403 PERMISSION_DENIED."
  echo "  → y aunque hubiera firmado, el verificador la rechazaría igual."

  paso "Y si se le pide que firme por la persona sin traer la firma hecha:"
  curl -s -X POST -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
       -d '{"peticion_id":"PET-003","decision":"descartada"}' "$URL/decidir" | python3 -m json.tool
  echo
  echo "  → «este servicio no puede firmar como humano, y no debe»"

  paso "Y la persona SÍ puede, desde SU máquina, con SU clave:"
  python3 src/decidir_como_persona.py PET-002 descartada 2>&1 | limpio | tail -3

  paso "El temporizador recoge esa firma y cierra:"
  gcloud scheduler jobs run despertar-candado --location=$REGION --project=$P --quiet 2>&1 | tail -1
  sleep 70
  python3 -c "
import sys; sys.path.insert(0,'.')
from src import estado
e=estado.leer('PET-002'); s=e.get('sobre') or {}
print(f'  PET-002 → veredicto={e.get(\"veredicto\")} · firmante={s.get(\"tipo_firmante\")} · estado={s.get(\"estado_destino\")}')" 2>&1 | limpio
  esperar
}

# ── TOMA 4 · cualquiera lo comprueba ────────────────────────────────────────────────────
toma4() {
  titulo "TOMA 4 — cualquiera lo verifica, y el filtro del fabricante falla"
  paso "El verificador NO importa nada de Google:"
  python3 -c "
import ast
t=ast.parse(open('src/verificar_sobre.py').read()); imp=set()
for n in ast.walk(t):
    if isinstance(n,ast.Import): imp|={a.name.split('.')[0] for a in n.names}
    if isinstance(n,ast.ImportFrom) and n.module: imp.add(n.module.split('.')[0])
print('  importa:', ', '.join(sorted(imp)))
print('  ¿algo de Google? →', 'sí' if any(i in ('google','requests') for i in imp) else 'NO')"

  paso "Las cinco pruebas, en verde:"
  for k in inyeccion alcance canonico blindaje; do
    printf "  %-12s " "$k"
    python3 agente/killtest_$k.py >/dev/null 2>&1 && echo "PASA" || echo "NO PASA"
  done

  paso "El filtro de inyección de Google contra NUESTRO ataque:"
  python3 agente/killtest_blindaje.py 2>&1 | limpio | sed -n '3,12p'
  esperar
}

# ── TOMA 5 · la prueba visual de la nube, que las reglas exigen ─────────────────────────
toma5() {
  titulo "TOMA 5 — prueba visual de Google Cloud (obligatoria por las reglas)"
  paso "El servicio desplegado:"
  gcloud run services list --project=$P --region=$REGION --format='table(metadata.name,status.url)' 2>&1 | head -4
  paso "El temporizador que lo despierta:"
  gcloud scheduler jobs list --location=$REGION --project=$P --format='table(name,schedule,state)' 2>&1 | head -3
  paso "LAS DOS CLAVES Y SUS PERMISOS — la diferencia ES el producto:"
  for K in clave-agente clave-humano; do
    echo "  ── $K"
    gcloud kms keys get-iam-policy $K --location=$REGION --keyring=firmas --project=$P 2>&1 | sed 's/^/     /' | head -6
  done
  paso "El agente en el catálogo de agentes de Google:"
  gcloud run services describe candado-firma --region=$REGION --project=$P --format='value(status.url)' 2>&1 | tail -1
}

case "$TOMA" in
  1) toma1 ;; 2) toma2 ;; 3) toma3 ;; 4) toma4 ;; 5) toma5 ;;
  todas) toma1; toma2; toma3; toma4; toma5 ;;
  *) echo "uso: bash demo.sh [1|2|3|4|5|todas] [--sin-pausa]"; exit 1 ;;
esac

echo
echo "════════════════════════════════════════════════════════════════"
echo "  fin de la demostración"
echo "════════════════════════════════════════════════════════════════"
