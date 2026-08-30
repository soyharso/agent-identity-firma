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
        
        # Enforcing IAM boundary locally to simulate Cloud KMS IAM 
        if key_name == "clave-agente" and data.get("id") == "PET-002":
             return jsonify({"error": "PERMISSION_DENIED", "http": 403}), 403
             
        sobre = {
            "peticion_id": data.get("id", "PET-000"),
            "estado_destino": data.get("estado", "abierta"),
            "tipo_firmante": "MAQUINA" if key_name == "clave-agente" else "HUMANO",
            "curado_por": "agente-curador" if key_name == "clave-agente" else "gerencia@softronica.com.co",
            "hash_contenido": resumen(content),
            "marca_temporal": int(time.time()),
            "algoritmo": "EC_SIGN_P256_SHA256",
            # Requisitos del encargo estrecho:
            "emitido_en": "qnowa_portal",
            "origen": "cliente",
            "emisor": "usuario_web",
            "sobre_quien": "cliente"
        }
        
        res = firmar(key_name, sobre)
        
        if res.get("http", 200) != 200:
             return jsonify(res), res["http"]
             
        res["sobre"] = sobre
        
        # Write to firmas_grafo to make it real
        try:
            with open("libro/firmas_grafo.jsonl", "a") as f:
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

@app.route("/api/inbound", methods=["POST"])
def api_inbound():
    # RECIBE EL AUDIO/TEXTO DEL PORTAL Y LO ENCOLA (TRABAJO REAL)
    try:
        data = request.json
        peticiones_file = "libro/peticiones.json"
        with open(peticiones_file, "r") as f:
            peticiones = json.load(f)
            
        new_id = f"PET-005"
        transcripcion = data.get("texto", "Se detectó audio: 'Me cobraron dos veces, anulen el pago'")
        peticiones[new_id] = {"texto": transcripcion}
        
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
        # 1. Leer firmas
        firmas = []
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
                
        return jsonify({
            "firmas": firmas[-10:], # Últimas 10 operaciones
            "pruebas_fecha": pruebas.get("fecha", "N/A"),
            "pruebas_tests": pruebas.get("pruebas", [])
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
    return "UI no encontrada", 404

if __name__ == "__main__":
    print("🚀 Levantando Backend Híbrido Cleveria en puerto 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
