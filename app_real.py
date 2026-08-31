import datetime
import os
import json
import time
import uuid
from flask import Flask, request, jsonify, render_template_string, send_file

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from src.firma_kms import firmar, resumen
    from src.verificar_sobre import cargar_directorio, verificar
except ImportError:
    pass

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Rutas absolutas. Con rutas relativas el servicio escribía donde estuviera el directorio de
# trabajo: en local coincide con el repositorio, en Cloud Run no tiene por qué, y el libro
# acababa en otro sitio o el proceso moría por no encontrarlo.
RAIZ = os.path.dirname(os.path.abspath(__file__))
LIBRO = os.path.join(RAIZ, "libro")
FIRMAS = os.path.join(LIBRO, "firmas_grafo.jsonl")
PETICIONES = os.path.join(LIBRO, "peticiones.json")
RUPTURA = os.path.join(LIBRO, "pruebas_de_ruptura.json")

VERIFY_TOKEN = os.getenv("WA_VERIFY_TOKEN", "cleveria-hackathon-2026")

@app.route("/webhook/whatsapp", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Forbidden", 403

    if request.method == "POST":
        data = request.json
        print("📥 WHATSAPP EVENT:", json.dumps(data, indent=2))
        return "EVENT_RECEIVED", 200

@app.route("/api/firmar", methods=["POST"])
def api_firmar():
    try:
        data = request.json
        key_name = data.get("key", "clave-agente") 
        content = data.get("content", "default_content")
        
        # AVISO — este 403 lo decide esta línea, no Cloud IAM. Es un maniquí de interfaz para
        # que el tablero tenga algo que pintar sin credenciales. El 403 REAL, el único que
        # vale como evidencia, lo devuelve Cloud KMS en `servicio/main.py`
        # (/intentar-suplantar), que sí llama a las dos claves.
        # NO GRABAR ESTA RUTA COMO PRUEBA DE LA FRONTERA CRIPTOGRÁFICA.
        if key_name == "clave-agente" and data.get("id") == "PET-002":
             return jsonify({
                 "error": "PERMISSION_DENIED", "http": 403,
                 "_aviso": "403 de maqueta, decidido por la aplicación local. El 403 real lo da Cloud KMS en /intentar-suplantar.",
             }), 403

        # Campos de ACTO. Van dentro de lo firmado y su razón de ser es que dos decisiones
        # distintas produzcan sobres distintos aunque el texto sea el mismo. Por eso NO pueden
        # ser constantes: si todos los sobres del portal declaran el mismo instante y el mismo
        # destinatario, la unicidad que estos campos compran se pierde entera.
        ahora = time.time()
        sobre = {
            "peticion_id": data.get("id", "PET-000"),
            "estado_destino": data.get("estado", "abierta"),
            "tipo_firmante": "MAQUINA" if key_name == "clave-agente" else "HUMANO",
            "curado_por": "agente-curador" if key_name == "clave-agente" else "persona-operador",
            "hash_contenido": resumen(content),
            "marca_temporal": int(ahora),
            "algoritmo": "EC_SIGN_P256_SHA256",
            "emitido_en": datetime.datetime.fromtimestamp(
                ahora, datetime.timezone.utc).isoformat(timespec="seconds"),
            "origen": data.get("origen", "portal"),
            "emisor": "agente-curador" if key_name == "clave-agente" else "persona-operador",
            "sobre_quien": data.get("sobre_quien", "sin_declarar"),
        }
        if data.get("peticion_padre"):
            sobre["peticion_padre"] = data["peticion_padre"]
        
        res = firmar(key_name, sobre)
        
        if res.get("http", 200) != 200:
             return jsonify(res), res["http"]
             
        res["sobre"] = sobre
        
        # Al libro duradero, no al disco del contenedor: el panel de auditoría lee de ahí y
        # el sistema de ficheros de Cloud Run desaparece con la instancia.
        try:
            from src import libro_demo
            libro_demo.anotar_firma({
                "ts": int(time.time()),
                "peticion_id": sobre["peticion_id"],
                "dictamen": sobre["estado_destino"],
                "veredicto": "OK",
                "sobre": sobre,
                "firma": res.get("firma"),
            })
        except Exception:                                        # noqa: BLE001
            pass
            
        return jsonify(res), 200
    except Exception as e:
        return jsonify({"http": 500, "error": str(e)}), 500

@app.route("/api/verificar", methods=["POST"])
def api_verificar():
    try:
        data = request.json
        directorio = cargar_directorio()
        veredicto, explicacion = verificar(data.get("sobre"), data.get("firma"), data.get("texto"), directorio)
        return jsonify({"veredicto": veredicto, "explicacion": explicacion}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/transcribir", methods=["POST"])
def api_transcribir():
    """Audio del micrófono del navegador -> texto, con Speech-to-Text de verdad.

    El portal enseñaba una transcripción escrita a mano: el cliente decía una cosa y en
    pantalla salía otra. En un producto cuya tesis es que la evidencia se prueba y no se
    declara, esa era la mentira más cara del demo. Aquí no hay texto de reserva: si la
    transcripción falla, se dice que falló.
    """
    try:
        from src.voz import transcribir
    except Exception as e:                                       # noqa: BLE001
        return jsonify({"error": "transcripcion_no_disponible", "detalle": str(e)}), 503

    audio = request.files.get("audio")
    if audio is None:
        return jsonify({"error": "no llegó audio"}), 400

    # El navegador graba en WEBM/OPUS salvo Safari, que usa MP4. Declarar el formato
    # equivocado no da error: da una transcripción que no se parece a lo que se dijo.
    tipo = (audio.mimetype or "").lower()
    if "webm" in tipo:
        codificacion = "WEBM_OPUS"
    elif "ogg" in tipo:
        codificacion = "OGG_OPUS"          # notas de voz de WhatsApp
    elif "wav" in tipo or "x-wav" in tipo:
        codificacion = "LINEAR16"          # lo que produce Text-to-Speech, útil para ensayar
    elif "mp4" in tipo or "m4a" in tipo or "aac" in tipo:
        codificacion = "MP3"               # Safari graba en MP4/AAC
    else:
        codificacion = "WEBM_OPUS"         # el caso normal del navegador
    idioma = request.form.get("idioma", "es-CO")

    datos = audio.read()

    # Dos motores con reintento, y el segundo no es adorno: Speech-to-Text se quedó sin cuota en
    # mitad de las pruebas de hoy, y eso mismo pasando durante una grabación no tiene segunda
    # toma. La cadena vive en `src.voz` para que la prueba de ruptura recorra ESTE mismo camino
    # y no uno más frágil.
    motor, texto, fallos = transcribir(datos, idioma=idioma, codificacion=codificacion)

    if not texto:
        return jsonify({"error": "no_se_entendio",
                        "mensaje": "No se entendió el audio. Vuelve a intentarlo.",
                        "intentos": fallos}), 422 if not fallos else 502
    return jsonify({"texto": texto, "idioma": idioma,
                    "codificacion": codificacion, "motor": motor,
                    "respaldo_usado": motor != "speech-to-text",
                    "intentos_fallidos": fallos}), 200


@app.route("/api/inbound", methods=["POST"])
def api_inbound():
    """La petición del cliente entra en la cola. Es el turno que el agente atenderá."""
    try:
        data = request.json or {}
        transcripcion = (data.get("texto") or "").strip()
        if not transcripcion:
            return jsonify({"error": "sin texto: el portal no inventa lo que dijo el cliente"}), 400

        from src import libro_demo
        pid, fila = libro_demo.nueva_peticion(
            transcripcion,
            de=data.get("de", "cliente-portal"),
            origen=data.get("origen", "portal"),
            padre=data.get("peticion_padre"))

        return jsonify({
            "status": "success",
            "id": pid,
            "transcription": transcripcion,
            "estado": "esperando decision humana",
            "duradero": libro_demo.disponible(),
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/auditoria_datos", methods=["GET"])
def api_auditoria_datos():
    """Todo lo que el panel pinta sale de aquí, y todo es real.

    Devuelve el libro entero de operaciones, la cola de peticiones y el resultado de la última
    corrida de pruebas. El panel agrupa; este endpoint no decide qué se ve.
    """
    try:
        from src import libro_demo
        pruebas = {}
        try:
            with open(RUPTURA, "r", encoding="utf-8") as f:
                pruebas = json.load(f)
        except Exception:                                        # noqa: BLE001
            pass

        return jsonify({
            "firmas": libro_demo.firmas(),
            "peticiones": libro_demo.peticiones(),
            "pruebas_fecha": pruebas.get("fecha", "sin corrida registrada"),
            "pruebas_tests": pruebas.get("pruebas", []),
            "pruebas_segundos": pruebas.get("segundos"),
            "duradero": libro_demo.disponible(),
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    """La puerta de `demo.cleveria.co`.

    Esta página se ve antes que ninguna otra, y hasta hoy era una lista sin formato con la
    palabra «ACT I» encima. Un jurado que llega por el enlace de la inscripción no sabe qué son
    los actos ni le importan: quiere saber qué va a ver y por qué le debería interesar. Se
    reescribe con la misma marca oscura del libro de autoridad, y cada puerta dice lo que
    demuestra, no en qué orden se rodó.
    """
    html = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cleveria — Live demo</title>
<link href="https://fonts.googleapis.com/css2?family=Chivo:wght@700;900&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
<style>
:root{--navy:#06111F;--harbor:#0B2940;--cyan:#27E6D2;--agent:#4B6BFF;--violet:#8D72FF;
      --ice:#E9FFFB;--slate:#93A8B8;--linea:rgba(147,168,184,.18)}
*{box-sizing:border-box}
body{margin:0;background:var(--navy);color:var(--ice);
     font:16px/1.6 Inter,system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased}
.env{max-width:880px;margin:0 auto;padding:64px 26px 72px}
.marca{display:flex;align-items:center;gap:11px;font-family:Chivo,sans-serif;font-weight:900;
       font-size:1.15rem;letter-spacing:-.02em;color:var(--ice);text-decoration:none}
.nudo{width:26px;height:26px;flex:none}
h1{font-family:Chivo,sans-serif;font-weight:900;letter-spacing:-.028em;line-height:1.06;
   font-size:clamp(2rem,5vw,3.1rem);margin:38px 0 14px;text-wrap:balance}
.entrada{color:var(--slate);font-size:1.06rem;max-width:60ch;margin:0 0 40px}
.puertas{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(310px,1fr))}
a.puerta{display:block;text-decoration:none;color:inherit;background:var(--harbor);
         border:1px solid var(--linea);border-radius:15px;padding:22px 22px 20px;
         transition:border-color .18s,transform .18s}
a.puerta:hover,a.puerta:focus-visible{border-color:var(--cyan);transform:translateY(-2px)}
.puerta h2{font-family:Chivo,sans-serif;font-weight:700;font-size:1.16rem;margin:0 0 7px;
           letter-spacing:-.01em}
.puerta p{margin:0;color:var(--slate);font-size:14px;line-height:1.5}
.puerta .prueba{display:block;margin-top:13px;padding-top:11px;border-top:1px solid var(--linea);
                font:400 12px JetBrains Mono,monospace;color:var(--cyan)}
.pie{margin-top:44px;padding-top:22px;border-top:1px solid var(--linea);
     color:var(--slate);font-size:13.5px;line-height:1.6}
.pie b{color:var(--ice);font-weight:600}
</style></head><body>
<div class="env">
  <a class="marca" href="/">
    <svg class="nudo" viewBox="0 0 100 100" fill="none" aria-hidden="true">
      <path d="M50 8 82 26v36L50 80 18 62V26z" stroke="#27E6D2" stroke-width="6"/>
      <path d="M50 26 68 36v20L50 66 32 56V36z" stroke="#8D72FF" stroke-width="6"/>
    </svg>
    Cleveria
  </a>

  <h1>An agent can close your cases.<br>It cannot sign as a person.</h1>
  <p class="entrada">Two live screens, running on Google Cloud. The first is what a customer
     sees; the second is what the people who answer them see. Both read the same ledger, and
     nothing on either page is staged.</p>

  <div class="puertas">
    <a class="puerta" href="/ui/portal">
      <h2>The customer's channel</h2>
      <p>A support portal that takes a real voice note, transcribes it and files the case.
         Speak into it and watch the request appear in the queue.</p>
      <span class="prueba">the request enters here</span>
    </a>
    <a class="puerta" href="/ui/unified">
      <h2>The authority ledger</h2>
      <p>Every case with who proposed it, who approved it, and every attempt that was refused —
         plus the ten break tests, with the time each one took.</p>
      <span class="prueba">the decision is proved here</span>
    </a>
  </div>

  <p class="pie"><b>Why two screens and not one.</b> The customer's channel is deliberately
     ordinary: any company could have one. What is not ordinary is that the program answering it
     has no key to commit the company. The refusal is the product, and it lives on the second
     screen.</p>
</div>
</body></html>"""
    return render_template_string(html)

@app.route("/ui/<path:name>")
def serve_ui(name):
    base_path = os.path.dirname(os.path.abspath(__file__))
    if name == "unified":
        return send_file(os.path.join(base_path, "assets", "slides", "ui_unified_dashboard.html"))
    elif name == "portal":
        return send_file(os.path.join(base_path, "assets", "slides", "ui_portal_cliente.html"))
    elif name == "bandeja":
        return send_file(os.path.join(base_path, "assets", "slides", "ui_bandeja_humana.html"))
    # Marca: Qnowa da la cara al cliente en el portal, Cleveria gobierna por dentro.
    marca = {"qnowa-logo.svg": (("assets", "qnowa", "qnowa-logo.svg"), "image/svg+xml"),
             "qnowa-mark.svg": (("assets", "qnowa", "qnowa-mark.svg"), "image/svg+xml"),
             "cleveria-mark.svg": (("assets", "cleveria-mark.svg"), "image/svg+xml"),
             # El logotipo sellado por el operador. Dos versiones: la de tinta para fondo
             # claro y la de hielo para el panel oscuro. Un logotipo oscuro sobre fondo
             # oscuro no se ve, y en cámara eso se nota más que cualquier otra cosa.
             "cleveria-logo.png": (("assets", "cleveria-logo.png"), "image/png"),
             "cleveria-logo-dark.png": (("assets", "cleveria-logo-dark.png"), "image/png"),
             "cleveria-logo.svg": (("assets", "cleveria-logo.svg"), "image/svg+xml")}
    if name in marca:
        ruta, mime = marca[name]
        return send_file(os.path.join(base_path, *ruta), mimetype=mime)
    return "UI no encontrada", 404

if __name__ == "__main__":
    print("🚀 Levantando Backend Híbrido Cleveria en puerto 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
