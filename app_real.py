import os
import json
import time
from flask import Flask, request, jsonify, render_template_string, send_file

# Importar la lógica real criptográfica del repositorio
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from src.firma_kms import firmar, resumen
    from src.verificar_sobre import cargar_directorio, verificar
except ImportError:
    pass

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# ==============================================================================
# 1. WHATSAPP BUSINESS API WEBHOOK (Real Channel)
# ==============================================================================
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

# ==============================================================================
# 2. ENDPOINTS PARA LAS INTERFACES HTML (Conectando UI a KMS Real)
# ==============================================================================

@app.route("/api/firmar", methods=["POST"])
def api_firmar():
    try:
        data = request.json
        key_name = data.get("key", "clave-agente") 
        content = data.get("content", "default_content")
        
        # AVISO — este 403 lo decide esta línea, no Cloud IAM. Es un maniquí de interfaz
        # para que el tablero local tenga algo que pintar sin credenciales.
        # El 403 REAL, el que vale como evidencia, lo devuelve Cloud KMS en
        # `servicio/main.py` (/intentar-suplantar), que sí llama a las dos claves.
        # No grabar esta ruta como prueba de la frontera criptográfica.
        if key_name == "clave-agente" and data.get("id") == "PET-002":
             return jsonify({
                 "error": "PERMISSION_DENIED",
                 "_aviso": "403 de maqueta, decidido por la aplicación local. El 403 real lo da Cloud KMS en /intentar-suplantar.",
             }), 403

        sobre = {
            "peticion_id": data.get("id", "PET-000"),
            "estado_destino": data.get("estado", "abierta"),
            "tipo_firmante": "MAQUINA" if key_name == "clave-agente" else "HUMANO",
            "curado_por": "agente-curador" if key_name == "clave-agente" else "persona-operador",
            "hash_contenido": resumen(content),
            "marca_temporal": int(time.time()),
            "algoritmo": "EC_SIGN_P256_SHA256"
        }
        
        # Llamada real a Google Cloud KMS
        res = firmar(key_name, sobre)
        
        if res.get("http", 200) != 200:
             return jsonify(res), res["http"]
             
        # Add the 'sobre' object to the response for the frontend
        res["sobre"] = sobre
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

# ==============================================================================
# 3. SERVIR LAS INTERFACES 
# ==============================================================================

@app.route("/")
def index():
    html = """
    <h1>🎬 Cleveria Director's Dashboard</h1>
    <ul>
        <li><a href="/ui/unified" target="_blank">✅ ACT II: Unified Fleet Command (Curator & HITL)</a></li>
    </ul>
    <p>Webhook URL para WhatsApp Meta: <code>/webhook/whatsapp</code></p>
    """
    return render_template_string(html)

@app.route("/ui/<path:name>")
def serve_ui(name):
    base_path = os.path.dirname(os.path.abspath(__file__))
    if name == "unified":
        return send_file(os.path.join(base_path, "assets", "slides", "ui_unified_dashboard.html"))
    return "UI no encontrada", 404

if __name__ == "__main__":
    print("🚀 Levantando Backend Híbrido Cleveria en puerto 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
