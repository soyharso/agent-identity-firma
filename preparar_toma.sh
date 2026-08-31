#!/usr/bin/env bash
# ==============================================================================
# PREPARAR LA TOMA — un comando en vez de ocho, y ninguno se olvida
# ==============================================================================
# QUÉ HACE. Deja la máquina lista para grabar: audio, cola, OBS y servicio. Lo que puede
# arreglar, lo arregla; lo que no, lo dice en rojo y para. Al final imprime los CINCO momentos
# en los que la persona hace algo, que es lo único que hay que llevar en la cabeza.
#
# BÚSQUEDA PREVIA (C1). `ls *.sh` da cuatro: `demo.sh` (las tomas), `deploy_demo.sh` (el
# despliegue), `pruebas_de_ruptura.sh` (las dieciséis pruebas) y `diagnostico_sabado.sh`. Este
# último es el más parecido y NO sirve: comprueba el PRODUCTO —verificador, agent cards, voz,
# cuentas de servicio— y no toca nada del entorno de grabación. No mira OBS, ni el audio, ni la
# hora de llegada de la cola, ni el portal desplegado, que es justo lo que se olvida y lo que
# cuesta una toma. Además tarda minutos porque corre pruebas. Se deja como está.
#
#   bash preparar_toma.sh            # prepara y comprueba
#   bash preparar_toma.sh --soltar   # al terminar de grabar: devuelve el micrófono a su sitio
# ==============================================================================
set -uo pipefail

RAIZ="$(cd "$(dirname "$0")" && pwd)"
cd "$RAIZ"
VERDE="\033[32m"; ROJO="\033[31m"; AMARILLO="\033[33m"; GRIS="\033[2m"; NEGRITA="\033[1m"; FIN="\033[0m"
FALLOS=0

ok()   { echo -e "  ${VERDE}✓${FIN} $*"; }
mal()  { echo -e "  ${ROJO}✗${FIN} $*"; FALLOS=$((FALLOS+1)); }
avisa(){ echo -e "  ${AMARILLO}!${FIN} $*"; }
paso() { echo -e "\n${NEGRITA}$*${FIN}"; }

# ── --soltar · deshacer lo único que cambia fuera de este repositorio ─────────
# El sumidero virtual se queda puesto como micrófono por defecto de la máquina. Si no se suelta,
# el micrófono del portátil sigue desviado después de grabar y la siguiente videollamada no oye
# a nadie. Por eso el desmontaje es un comando y no una nota en un documento.
if [ "${1:-}" = "--soltar" ]; then
  pactl unload-module module-null-sink 2>/dev/null && echo -e "${VERDE}Sumidero soltado.${FIN}" \
    || echo -e "${AMARILLO}No había sumidero que soltar.${FIN}"
  pactl set-default-source alsa_input.pci-0000_03_00.6.analog-stereo 2>/dev/null \
    && echo -e "${VERDE}Micrófono devuelto al de la máquina.${FIN}"
  exit 0
fi

echo -e "\n${NEGRITA}PREPARAR LA TOMA${FIN} ${GRIS}· $(date '+%H:%M:%S')${FIN}"

paso "1 · Google Cloud"
if gcloud auth print-identity-token >/dev/null 2>&1; then
  ok "identificador de sesión vivo ${GRIS}(dura UNA HORA: si la toma se retrasa, renueva)${FIN}"
else
  mal "identificador caducado. Corre:  gcloud auth login"
fi

paso "2 · Audio — la voz de la clienta entra por cable, no por el aire"
# Medido el 2026-08-31: por altavoz+micrófono, Speech-to-Text devuelve «sin habla reconocible»,
# y al subir la ganancia transcribe una frase que nadie dijo. Por el sumidero, palabra por palabra.
if pactl list short sinks | grep -q cliente_sim; then
  ok "sumidero cliente_sim ya montado"
else
  pactl load-module module-null-sink sink_name=cliente_sim \
        sink_properties=device.description=ClienteSimulado >/dev/null 2>&1 \
    && ok "sumidero cliente_sim montado" || mal "no pude montar el sumidero"
fi
pactl set-default-source cliente_sim.monitor >/dev/null 2>&1 \
  && ok "micrófono por defecto = cliente_sim.monitor ${GRIS}(el navegador oirá la nota)${FIN}" \
  || mal "no pude poner el micrófono por defecto"
[ -f narracion/cliente_simulado.wav ] \
  && ok "nota de voz de la clienta lista ${GRIS}($(soxi -D narracion/cliente_simulado.wav 2>/dev/null | cut -c1-4) s)${FIN}" \
  || mal "falta narracion/cliente_simulado.wav — regenérala con generar_narracion.py"

paso "3 · La cola, con hora de llegada de hoy"
python3 sembrar_demo.py --solo-horas 2>&1 | grep -E "sellada|Sin Firestore" \
  || mal "no pude sellar la hora de la cola"

paso "4 · El servicio desplegado"
CFG=$(curl -s --max-time 15 https://demo.cleveria.co/api/config || echo "")
echo "$CFG" | grep -q '"google_client_id":"[^"]' \
  && ok "login de Google vivo" \
  || mal "google_client_id VACÍO: el despliegue lo borró. La bandeja no podrá firmar"
# A LA PÁGINA SE LE MIRA EN UNA VARIABLE, NO POR TUBERÍA. Con `set -o pipefail`, un
# `curl | grep -q` devuelve el fallo de curl —que muere por SIGPIPE cuando grep encuentra y
# sale— y la comprobación daba ROJO sobre un panel que estaba bien. Un chequeo que miente en
# rojo se desactiva a los dos días, y entonces ya no comprueba nada.
PANEL=$(curl -s --max-time 15 https://demo.cleveria.co/ui/unified || echo "")
case "$PANEL" in
  *sinatender*) ok "el panel desplegado lleva el latido de la tarjeta sin atender" ;;
  *)            mal "el panel desplegado es el viejo: falta desplegar" ;;
esac

paso "4-bis · Calentamiento — que nadie pague el arranque en frío en cámara"
# Los dos servicios corren en Cloud Run SIN instancias mínimas: tras unos quince minutos sin
# tráfico el contenedor se apaga, y la primera petición de la toma paga el arranque delante de la
# cámara. Esa espera no se puede cortar sin romper el criterio de «toma sin editar». Así que se
# golpean todas las puertas que el vídeo va a abrir, y se enseña el tiempo: la segunda pasada
# tiene que bajar. Si sigue alta, el servicio no está caliente y no es momento de grabar.
CANDADO="https://candado-firma-141981963817.us-central1.run.app"
TOK=$(gcloud auth print-identity-token 2>/dev/null || echo "")
calienta() {  # calienta <etiqueta> <url> [cabecera]
  local t1 t2
  t1=$(curl -s -o /dev/null -w '%{time_total}' --max-time 60 ${3:+-H "$3"} "$2" 2>/dev/null || echo "-")
  t2=$(curl -s -o /dev/null -w '%{time_total}' --max-time 60 ${3:+-H "$3"} "$2" 2>/dev/null || echo "-")
  if [ "$t2" = "-" ]; then
    mal "$1 no responde"
  else
    local frio caliente
    frio=$(printf '%.1f' "$t1"); caliente=$(printf '%.2f' "$t2")
    if awk "BEGIN{exit !($t2 < 1.5)}"; then
      ok "$1 caliente ${GRIS}(1ª ${frio}s → 2ª ${caliente}s)${FIN}"
    else
      avisa "$1 TODAVÍA LENTO ${GRIS}(1ª ${frio}s → 2ª ${caliente}s)${FIN} — repite antes de grabar"
    fi
  fi
}
calienta "portal    " "https://demo.cleveria.co/ui/portal"
calienta "panel     " "https://demo.cleveria.co/api/auditoria_datos"
calienta "bandeja   " "https://demo.cleveria.co/ui/bandeja"
if [ -n "$TOK" ]; then
  calienta "servicio  " "$CANDADO/quien" "Authorization: Bearer $TOK"
else
  avisa "sin identificador de sesión no puedo calentar el servicio del candado"
fi
avisa "el calor dura ~15 min sin tráfico: ensaya y graba SEGUIDO"

paso "5 · OBS"
python3 - <<'PY'
import json, pathlib, sys
try:
    import obsws_python as obs
except ImportError:
    sys.exit("  \033[31m✗\033[0m falta la librería:  pip install --user obsws-python")
cfg = pathlib.Path.home() / ".var/app/com.obsproject.Studio/config/obs-studio/plugin_config/obs-websocket/config.json"
if not cfg.exists():
    sys.exit("  \033[31m✗\033[0m no encuentro la configuración del servidor de OBS")
c = json.loads(cfg.read_text())
try:
    cl = obs.ReqClient(host="localhost", port=c["server_port"], password=c["server_password"], timeout=5)
except Exception as e:
    sys.exit(f"  \033[31m✗\033[0m OBS cerrado o servidor apagado: {e}")
print("  \033[32m✓\033[0m conectado a OBS")

escenas = [s["sceneName"] for s in cl.get_scene_list().scenes]
faltan = [e for e in ("1 · Portada", "2 · Portal del cliente", "3 · Demostración",
                      "4 · Libro de autoridad", "5 · Consola de Google Cloud",
                      "6 · Arquitectura", "7 · Cierre", "8 · Bandeja humana")
          if e not in escenas]
if faltan:
    print(f"  \033[31m✗\033[0m faltan escenas: {faltan}. ¿La colección activa es Cleveria_Hackathon?")
else:
    print(f"  \033[32m✓\033[0m las ocho escenas están")

# 1920x1080 y no otra cosa: las tarjetas son de ese tamaño y a 1200 de alto salen con bandas.
v = cl.get_video_settings()
if (v.base_width, v.base_height, v.output_width, v.output_height) != (1920, 1080, 1920, 1080):
    cl.set_video_settings(numerator=30, denominator=1, base_width=1920, base_height=1080,
                          out_width=1920, out_height=1080)
    print("  \033[32m✓\033[0m lienzo corregido a 1920×1080 a 30 fps")
else:
    print("  \033[32m✓\033[0m lienzo 1920×1080 a 30 fps")

# OBS guarda la imagen en memoria: cambiar el PNG en disco NO se ve hasta que se relee. Quitar y
# poner la visibilidad tampoco basta. Se fuerza vaciando la ruta y volviéndola a poner.
import time
raiz = pathlib.Path(__file__).resolve().parent if "__file__" in dir() else pathlib.Path.cwd()
for nombre, ruta in (("Portada", "assets/slides/portada.png"), ("Cierre", "assets/slides/cierre.png")):
    try:
        abs_ = str(pathlib.Path.cwd() / ruta)
        cl.set_input_settings(nombre, {"file": ""}, True)
        time.sleep(0.3)
        cl.set_input_settings(nombre, {"file": abs_}, True)
        print(f"  \033[32m✓\033[0m {nombre.lower()} releída del disco")
    except Exception as e:
        print(f"  \033[33m!\033[0m no pude releer {nombre}: {e}")

if cl.get_record_status().output_active:
    print("  \033[33m!\033[0m OBS YA ESTÁ GRABANDO. Párala antes de dirigir la toma.")
cl.set_current_program_scene("1 · Portada")
print("  \033[32m✓\033[0m escena inicial: 1 · Portada")
PY
[ $? -ne 0 ] && FALLOS=$((FALLOS+1))

paso "6 · El reloj"
MIN=$(date +%M); RESTO=$((10#$MIN % 15))
if [ "$RESTO" -ge 1 ] && [ "$RESTO" -le 11 ]; then
  ok "minuto :$(printf %02d $RESTO) del cuarto — ventana buena, adelante"
else
  avisa "minuto :$(printf %02d $RESTO) del cuarto. El despertador de la nube corre en :00 :15 :30 :45"
  avisa "espera a que pase y arranca entre el :01 y el :11"
fi

echo
if [ "$FALLOS" -eq 0 ]; then
  echo -e "${VERDE}${NEGRITA}TODO LISTO.${FIN}"
else
  echo -e "${ROJO}${NEGRITA}$FALLOS cosa(s) sin resolver. Arréglalas antes de grabar.${FIN}"
fi

cat <<'GUIA'

┌──────────────────────────────────────────────────────────────────────────────┐
│  LO QUE TIENES QUE HACER TÚ. Todo lo demás lo lanza el director.             │
├──────────────────────────────────────────────────────────────────────────────┤
│  ANTES                                                                       │
│   · Portal abierto en el navegador y en INGLÉS (botón EN arriba a la derecha)│
│   · Panel y bandeja en sus pestañas                                          │
│   · Una terminal a la vista con:   tail -f logs/escena.log                   │
│     (ahí escupen los comandos: la terminal del director NO sale en cámara)   │
├──────────────────────────────────────────────────────────────────────────────┤
│  DURANTE — cinco momentos, ni uno más                                        │
│   0:30  pulsas el micrófono del portal (una vez). No hables.                 │
│   0:40  vuelves a pulsarlo para enviar la nota                               │
│   1:55  te callas siete segundos con el 403 en pantalla                      │
│   2:12  pulsas Refrescar en el panel                                         │
│   2:33  abres el caso de la clienta (marco de puerta) y pulsas Firmar        │
├──────────────────────────────────────────────────────────────────────────────┤
│  ARRANCAR                                                                    │
│   Ensayo sin grabar:  python3 dirigir_grabacion.py --plan plan_toma.txt --ensayo
│   Toma buena:         python3 dirigir_grabacion.py --plan plan_toma.txt      │
│   El vídeo sale sin voz: la narración y la nota se mezclan después           │
│   (narracion/COMO_MONTARLA.txt).                                             │
├──────────────────────────────────────────────────────────────────────────────┤
│  AL TERMINAR                                                                 │
│   bash preparar_toma.sh --soltar     ← devuelve el micrófono de la máquina   │
└──────────────────────────────────────────────────────────────────────────────┘
GUIA
