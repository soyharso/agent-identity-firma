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
