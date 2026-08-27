"""El agente firma el cierre de una tarea, y no puede firmar como persona.

Corre en Cloud Run con el service account del agente adjunto. No hay ninguna clave en disco:
la identidad la da el servidor de metadatos, y la clave privada nunca sale del servicio de
claves de Google.
"""
import base64
import hashlib
import json
import os

import google.auth
import google.auth.transport.requests
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

PROYECTO = os.environ.get("PROYECTO", "ai-transf-lab-0827")
REGION = os.environ.get("REGION", "us-central1")
LLAVERO = "firmas"
BASE = ("https://cloudkms.googleapis.com/v1/projects/{p}/locations/{r}"
        "/keyRings/{a}/cryptoKeys/{k}/cryptoKeyVersions/1")


def sesion():
    cred, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"])
    cred.refresh(google.auth.transport.requests.Request())
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {cred.token}"
    return s


def quien_soy():
    """El servidor de metadatos: la prueba de que el proceso ES el service account."""
    try:
        r = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/"
            "service-accounts/default/email",
            headers={"Metadata-Flavor": "Google"}, timeout=5)
        return r.text
    except Exception as e:                                   # noqa: BLE001
        return f"sin metadatos: {e}"


def canonico(sobre):
    """La forma exacta que se firma. El verificador la recalcula igual o no valida."""
    return json.dumps(sobre, sort_keys=True, separators=(",", ":")).encode()


def firmar(s, clave, sobre):
    digest = hashlib.sha256(canonico(sobre)).digest()
    url = BASE.format(p=PROYECTO, r=REGION, a=LLAVERO, k=clave) + ":asymmetricSign"
    r = s.post(url, json={"digest": {"sha256": base64.b64encode(digest).decode()}},
               timeout=30)
    cuerpo = r.json()
    if r.ok:
        return {"clave": clave, "http": 200, "firma": cuerpo["signature"]}
    return {"clave": clave, "http": r.status_code,
            "error": cuerpo.get("error", {}).get("status"),
            "mensaje": cuerpo.get("error", {}).get("message", "")[:250]}


def sobre_de(peticion, estado, texto, curado_por):
    return {"peticion_id": peticion, "estado": estado, "curado_por": curado_por,
            "hash_contenido": "sha256:" + hashlib.sha256(texto.encode()).hexdigest()}


@app.get("/firmar")
def cerrar_peticion():
    """El agente cierra una tarea y la firma con SU clave."""
    p = request.args.get("peticion", "PET-001")
    estado = request.args.get("estado", "cerrada")
    texto = request.args.get("texto", "cierre de prueba")
    sobre = sobre_de(p, estado, texto, "modelo")
    return jsonify({"identidad_del_proceso": quien_soy(), "sobre": sobre,
                    "resultado": firmar(sesion(), "clave-agente", sobre)})


@app.get("/suplantar")
def intentar_suplantar():
    """El agente intenta firmar como persona. Esto tiene que fallar, y ese fallo es la prueba."""
    sobre = sobre_de("PET-001", "descartada", "me absuelvo a mi mismo", "humano")
    s = sesion()
    return jsonify({
        "identidad_del_proceso": quien_soy(),
        "sobre_que_intenta_colar": sobre,
        "con_la_clave_de_la_persona": firmar(s, "clave-humano", sobre),
        "con_su_propia_clave": firmar(s, "clave-agente", sobre),
        "nota": ("aunque logre firmar el sobre con SU clave, el verificador lo rechaza: "
                 "una firma de la clave del agente no puede declararse humana"),
    })


@app.get("/")
def salud():
    return jsonify({"identidad_del_proceso": quien_soy(),
                    "rutas": ["/firmar", "/suplantar"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
