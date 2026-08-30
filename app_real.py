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
        
        # Write to firmas_grafo to make it real
        try:
            with open(FIRMAS, "a") as f:
                log_entry = {
                    "ts": int(time.time()),
                    "peticion_id": sobre["peticion_id"],
                    "dictamen": sobre["estado_destino"],
                    "veredicto": "OK",
                    "sobre": sobre,
                    "firma": res.get("firma")
                }
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
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
        from src.voz import escuchar, escuchar_con_gemini
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
    motor, texto, fallos = "speech-to-text", "", []

    # Dos motores, y el segundo no es adorno: Speech-to-Text se quedó sin cuota en mitad de
    # las pruebas de hoy, y eso mismo pasando durante una grabación no tiene segunda toma.
    for nombre, fn in (("speech-to-text", lambda: escuchar(datos, idioma=idioma,
                                                           codificacion=codificacion)),
                       ("gemini", lambda: escuchar_con_gemini(datos, codificacion=codificacion))):
        try:
            texto = fn()
            if texto:
                motor = nombre
                break
        except Exception as e:                                   # noqa: BLE001
            fallos.append(f"{nombre}: {str(e)[:120]}")

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
    # RECIBE EL AUDIO/TEXTO DEL PORTAL Y LO ENCOLA (TRABAJO REAL)
    try:
        data = request.json
        peticiones_file = PETICIONES
        with open(peticiones_file, "r") as f:
            peticiones = json.load(f)
            
        # Un identificador por petición. Con un valor fijo, cada envío pisaba al anterior y
        # dos clientes distintos acababan en el mismo expediente — justo lo contrario de lo
        # que este producto promete.
        n = 1 + max((int(k.split("-")[1]) for k in peticiones if k.startswith("PET-")), default=0)
        new_id = f"PET-{n:03d}"
        transcripcion = data.get("texto", "").strip()
        if not transcripcion:
            return jsonify({"error": "sin texto: el portal no inventa lo que dijo el cliente"}), 400
        peticiones[new_id] = {
            "texto": transcripcion,
            "de": data.get("de", "cliente-portal"),
            "origen": "portal",
            "recibido_en": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        }
        
        with open(peticiones_file, "w") as f:
            json.dump(peticiones, f, indent=2, ensure_ascii=False)
            
        return jsonify({
            "status": "success", 
            "id": new_id, 
            "transcription": transcripcion,
            "estado": "esperando decision humana"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/auditoria_datos", methods=["GET"])
def api_auditoria_datos():
    # LEE LOS DATOS REALES (NO MOCKS) PARA EL TABLERO
    try:
        # 1. Leer firmas (TODAS, el frontend agrupa)
        firmas = []
        import os, json
        if os.path.exists("libro/firmas_grafo.jsonl"):
            with open("libro/firmas_grafo.jsonl", "r") as f:
                for line in f:
                    if line.strip():
                        firmas.append(json.loads(line))
        
        # 2. Leer pruebas de ruptura
        pruebas = {}
        if os.path.exists("libro/pruebas_de_ruptura.json"):
            with open("libro/pruebas_de_ruptura.json", "r") as f:
                pruebas = json.load(f)
                
        # 3. Leer peticiones para contexto
        peticiones = {}
        if os.path.exists("libro/peticiones.json"):
            with open("libro/peticiones.json", "r") as f:
                peticiones = json.load(f)
                
        return jsonify({
            "firmas": firmas,
            "pruebas_fecha": pruebas.get("fecha", "N/A"),
            "pruebas_tests": pruebas.get("pruebas", []),
            "peticiones": peticiones
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    html = """
    <h1>🎬 Cleveria Director's Dashboard</h1>
    <ul>
        <li><a href="/ui/portal" target="_blank">✅ ACT I: Portal Cliente Multimodal</a></li>
        <li><a href="/ui/unified" target="_blank">✅ ACT II & III: Unified Fleet Command (Curador, HITL, Auditoría)</a></li>
    </ul>
    """
    return render_template_string(html)

@app.route("/ui/<path:name>")
def serve_ui(name):
    base_path = os.path.dirname(os.path.abspath(__file__))
    if name == "unified":
        return send_file(os.path.join(base_path, "assets", "slides", "ui_unified_dashboard.html"))
    elif name == "portal":
        return send_file(os.path.join(base_path, "assets", "slides", "ui_portal_cliente.html"))
    # Marca: Qnowa da la cara al cliente en el portal, Cleveria gobierna por dentro.
    marca = {"qnowa-logo.svg": ("assets", "qnowa", "qnowa-logo.svg"),
             "qnowa-mark.svg": ("assets", "qnowa", "qnowa-mark.svg"),
             "cleveria-logo.svg": ("assets", "cleveria-logo.svg"),
             "cleveria-mark.svg": ("assets", "cleveria-mark.svg")}
    if name in marca:
        return send_file(os.path.join(base_path, *marca[name]), mimetype="image/svg+xml")
    return "UI no encontrada", 404

if __name__ == "__main__":
    print("🚀 Levantando Backend Híbrido Cleveria en puerto 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
