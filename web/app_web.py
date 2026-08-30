#!/usr/bin/env python3
"""La web de cleveria.co, y el formulario que de verdad recibe.

POR QUÉ ES UN SERVICIO APARTE del demo del concurso. Son dos públicos distintos: `demo.cleveria.co`
le habla a un jurado que viene a comprobar una tesis, y `cleveria.co` le habla a una empresa que
no sabe nada del concurso. Mezclarlos haría que una caída del demo tumbara la web de la casa, y
que un despliegue de la web tocara lo que el jurado está mirando. Se despliegan por separado a
propósito.

EL FORMULARIO NO FINGE, y esto es deliberado. Un lector sin contexto leyó la versión anterior
—que abría el programa de correo del visitante— como desconfianza: «es extraño tener un
formulario web que no envía nada». Pero lo contrario es peor: un formulario que dice «enviado» y
pierde el mensaje en silencio. Así que aquí:

  1. El mensaje se GUARDA primero, en Firestore. Si esto falla, el visitante ve que falló.
  2. El correo se intenta después, y solo si hay credencial configurada.
  3. La respuesta dice LA VERDAD de lo que pasó: guardado, y si se avisó o no.

Es la misma regla que gobierna el resto de la casa: se informa de lo que ocurrió, incluida la
parte que no salió.
"""
import os
import re
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

from flask import Flask, jsonify, request, send_file

app = Flask(__name__)
AQUI = Path(__file__).resolve().parent
DESTINO = os.environ.get("CORREO_DESTINO", "info@cleveria.co")

# Límites: un formulario público sin tope es una invitación a llenar la base de basura.
TOPES = {"nombre": 120, "empresa": 160, "correo": 200, "telefono": 40,
         "asunto": 200, "detalle": 4000}
CORREO_VALIDO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _guardar(datos: dict) -> str:
    """Firestore. Devuelve el identificador, o levanta si no se pudo guardar."""
    from google.cloud import firestore                      # import tardío: arranque más rápido
    cliente = firestore.Client()
    ref = cliente.collection("contactos_web").document()
    ref.set({**datos, "recibido_en": datetime.now(timezone.utc).isoformat()})
    return ref.id


def _avisar(datos: dict, ident: str) -> bool:
    """Correo al buzón de la casa. Devuelve si se envió; NUNCA levanta.

    Va detrás de dos variables de entorno a propósito. Mientras no estén, el mensaje se guarda
    igual y la respuesta lo dice: es mejor un aviso pendiente que un envío inventado.
    """
    usuario = os.environ.get("SMTP_USUARIO")
    clave = os.environ.get("SMTP_CLAVE")
    if not (usuario and clave):
        return False
    try:
        # El servidor se DEDUCE del correo, y no se deja a que alguien recuerde otra variable.
        # Costó una prueba: el buzón que se configuró es de Yahoo y aquí estaba puesto Gmail por
        # defecto, así que el envío fallaba en silencio mientras la respuesta decía —con razón—
        # que no había avisado. Un valor por defecto que solo acierta con un proveedor es una
        # trampa esperando: quien configura el correo no tiene por qué saber qué servidor toca.
        dominio = usuario.rsplit("@", 1)[-1].lower()
        SERVIDORES = {
            "yahoo.com": "smtp.mail.yahoo.com", "yahoo.com.mx": "smtp.mail.yahoo.com",
            "yahoo.es": "smtp.mail.yahoo.com", "ymail.com": "smtp.mail.yahoo.com",
            "gmail.com": "smtp.gmail.com", "googlemail.com": "smtp.gmail.com",
            "outlook.com": "smtp-mail.outlook.com", "hotmail.com": "smtp-mail.outlook.com",
            "live.com": "smtp-mail.outlook.com",
        }
        # Un dominio propio con correo de Google —el caso de esta casa— también sale por Gmail.
        host = os.environ.get("SMTP_HOST") or SERVIDORES.get(dominio, "smtp.gmail.com")
        m = EmailMessage()
        m["Subject"] = f"cleveria.co — {datos.get('empresa') or datos.get('nombre') or 'contacto'}"
        m["From"] = usuario
        m["To"] = DESTINO
        m["Reply-To"] = datos.get("correo") or usuario
        m.set_content("\n".join(f"{k}: {v}" for k, v in datos.items()) + f"\n\nid: {ident}")
        with smtplib.SMTP_SSL(host, int(os.environ.get("SMTP_PUERTO", "465")), timeout=15) as s:
            s.login(usuario, clave)
            s.send_message(m)
        return True
    except Exception as e:                                   # noqa: BLE001
        # Se registra el motivo, SIN la credencial: un aviso que falla en silencio es un aviso
        # que nadie arregla. El visitante no ve esto — a él se le dice que quedó guardado.
        print(f"aviso no enviado · servidor={host} · motivo={str(e)[:160]}", flush=True)
        return False


@app.route("/api/contacto", methods=["POST"])
def api_contacto():
    d = request.get_json(silent=True) or request.form or {}
    datos = {k: str(d.get(k, "")).strip()[:t] for k, t in TOPES.items()}

    if not datos["nombre"]:
        return jsonify({"error": "falta_nombre", "mensaje": "Necesitamos su nombre."}), 400
    if not CORREO_VALIDO.match(datos["correo"]):
        return jsonify({"error": "correo_invalido",
                        "mensaje": "Ese correo no parece válido; sin él no podemos responderle."}), 400

    try:
        ident = _guardar(datos)
    except Exception as e:                                   # noqa: BLE001
        # Se dice que falló. La alternativa —un «gracias» sobre un mensaje perdido— es la mentira
        # que este formulario existe para no contar.
        return jsonify({"error": "no_se_pudo_guardar", "detalle": str(e)[:120],
                        "mensaje": f"No pudimos guardar su mensaje. Escríbanos a {DESTINO}."}), 503

    avisado = _avisar(datos, ident)
    return jsonify({"ok": True, "id": ident, "avisado": avisado,
                    "mensaje": "Recibido. Le respondemos el mismo día hábil."}), 200


@app.route("/")
def home():
    """La página la sirve Firebase Hosting, no este servicio.

    Se deja la ruta por una razón práctica: si algún día el reenvío de Hosting se cae, quien
    llegue aquí debe entender qué es esto en vez de encontrarse un error sin explicación.
    """
    pagina = AQUI / "cleveria-home.html"
    if pagina.exists():
        return send_file(pagina)
    return jsonify({"servicio": "cleveria-web",
                    "para": "recibir el formulario de contacto de cleveria.co",
                    "endpoints": ["/api/contacto", "/salud"],
                    "la_pagina": "la sirve Firebase Hosting"}), 200


@app.route("/salud")
def salud():
    """Estado del servicio, **sin exponer ni la cuenta ni la clave**.

    Devuelve el DOMINIO del buzón y el servidor deducido, que es justo lo que hace falta para
    ver por qué un aviso no sale: si la clave es de un proveedor y la cuenta de otro, aquí se
    ve en una línea. La cuenta completa y la clave no salen de aquí nunca.
    """
    usuario = os.environ.get("SMTP_USUARIO") or ""
    dominio = usuario.rsplit("@", 1)[-1].lower() if "@" in usuario else None
    return jsonify({
        "ok": True,
        "correo_configurado": bool(usuario and os.environ.get("SMTP_CLAVE")),
        "buzon_dominio": dominio,
        "servidor_deducido": os.environ.get("SMTP_HOST") or (
            {"yahoo.com": "smtp.mail.yahoo.com", "yahoo.com.mx": "smtp.mail.yahoo.com",
             "yahoo.es": "smtp.mail.yahoo.com", "ymail.com": "smtp.mail.yahoo.com",
             "gmail.com": "smtp.gmail.com", "googlemail.com": "smtp.gmail.com",
             "outlook.com": "smtp-mail.outlook.com", "hotmail.com": "smtp-mail.outlook.com",
             "live.com": "smtp-mail.outlook.com"}.get(dominio, "smtp.gmail.com")
            if dominio else None),
        "destino": DESTINO,
    }), 200
