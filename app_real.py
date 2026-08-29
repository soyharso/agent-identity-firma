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
        # Meta Webhook Verification
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Forbidden", 403

    if request.method == "POST":
        data = request.json
        print("📥 WHATSAPP EVENT:", json.dumps(data, indent=2))
        # Aquí se procesaría el mensaje real y se mandaría a Firestore o a la cola
        # Para el hackathon, esto demuestra que el canal de entrada ES REAL.
        return "EVENT_RECEIVED", 200


# ==============================================================================
# 2. ENDPOINTS PARA LAS INTERFACES HTML (Conectando UI a KMS Real)
# ==============================================================================

@app.route("/api/firmar", methods=["POST"])
def api_firmar():
    """Conecta el botón 'Sign' del HTML con Cloud KMS real"""
    try:
        data = request.json
        key_name = data.get("key", "clave-agente") # O clave-humano
        content = data.get("content", "default_content")
        
        sobre = {
            "peticion_id": data.get("id", "PET-000"),
            "estado_destino": data.get("estado", "abierta"),
            "tipo_firmante": "MAQUINA" if key_name == "clave-agente" else "HUMANO",
            "curado_por": "agente-curador" if key_name == "clave-agente" else "gerencia@softronica.com.co",
            "hash_contenido": resumen(content),
            "marca_temporal": int(time.time()),
            "algoritmo": "EC_SIGN_P256_SHA256"
        }
        
        # Llamada real a Google Cloud KMS
        res = firmar(key_name, sobre)
        
        return jsonify(res), res.get("http", 500)
    except Exception as e:
        return jsonify({"http": 500, "error": str(e)}), 500


@app.route("/api/verificar", methods=["POST"])
def api_verificar():
    """Conecta el panel de auditoría con el verificador RFC 8785 offline"""
    try:
        data = request.json
        sobre = data.get("sobre")
        firma = data.get("firma")
        texto = data.get("texto")
        
        directorio = cargar_directorio()
        veredicto, explicacion = verificar(sobre, firma, texto, directorio)
        
        return jsonify({"veredicto": veredicto, "explicacion": explicacion}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==============================================================================
# 3. SERVIR LAS INTERFACES (Para cargarlas en OBS fácilmente)
# ==============================================================================

@app.route("/")
def index():
    html = """
    <h1>🎬 Cleveria Director's Dashboard</h1>
    <ul>
        <li><a href="/ui/whatsapp" target="_blank">1. Interfaz de Usuario (WhatsApp Web Mockup)</a></li>
        <li><a href="/ui/curador" target="_blank">2. Agente Curador (Intentos de Firma)</a></li>
        <li><a href="/ui/hitl" target="_blank">3. Cola HITL (Firma Humana Real)</a></li>
        <li><a href="/ui/auditoria" target="_blank">4. Panel de Auditoría y Verificación</a></li>
    </ul>
    <p>Webhook URL para WhatsApp Meta: <code>/webhook/whatsapp</code></p>
    """
    return render_template_string(html)

@app.route("/ui/<path:name>")
def serve_ui(name):
    # Mapear las UIs que dejaste en Downloads/Borrar (puedes moverlas al repo)
    base_path = "/home/softboy/Downloads/Borrar"
    files = {
        "whatsapp": "ui_usuario_whatsapp.html",
        "curador": "ui_curador_firma.html",
        "hitl": "ui_hitl_cola_humanos.html",
        "auditoria": "ui_auditoria_intentos.html"
    }
    
    file_name = files.get(name)
    if file_name:
        return send_file(os.path.join(base_path, file_name))
    return "UI no encontrada", 404


if __name__ == "__main__":
    print("🚀 Levantando Backend Híbrido Cleveria en puerto 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
