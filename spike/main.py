"""Spike: ¿puede el agente firmar con SU clave y ser rechazado con la de la persona?

Corre dentro de Cloud Run con el service account del agente adjunto. No hay ninguna clave en
disco: la identidad la da el servidor de metadatos.
"""
import hashlib
import json
import os

import google.auth
import google.auth.transport.requests
import requests
from flask import Flask, jsonify

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
    """El servidor de metadatos, que es la prueba de que el proceso ES el service account."""
    try:
        r = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/"
            "service-accounts/default/email",
            headers={"Metadata-Flavor": "Google"}, timeout=5)
        return r.text
    except Exception as e:                                   # noqa: BLE001
        return f"sin metadatos: {e}"


def intentar_firma(s, clave, sobre):
    """Pide a Google que firme el resumen del sobre con esa clave. Devuelve el crudo."""
    digest = hashlib.sha256(json.dumps(sobre, sort_keys=True).encode()).digest()
    url = BASE.format(p=PROYECTO, r=REGION, a=LLAVERO, k=clave) + ":asymmetricSign"
    import base64
    r = s.post(url, json={"digest": {"sha256": base64.b64encode(digest).decode()}},
               timeout=30)
    cuerpo = r.json()
    return {"clave": clave, "http": r.status_code,
            "firma": (cuerpo.get("signature") or "")[:40] + "…" if r.ok else None,
            "error": None if r.ok else cuerpo.get("error", {}).get("status"),
            "mensaje": None if r.ok else cuerpo.get("error", {}).get("message", "")[:200]}


@app.get("/")
def spike():
    sobre = {"peticion_id": "PET-001", "estado": "cerrada", "curado_por": "modelo",
             "hash_contenido": "sha256:" + hashlib.sha256(b"cierre de prueba").hexdigest()}
    s = sesion()
    return jsonify({
        "identidad_del_proceso": quien_soy(),
        "sobre": sobre,
        "con_su_propia_clave": intentar_firma(s, "clave-agente", sobre),
        "con_la_clave_de_la_persona": intentar_firma(s, "clave-humano", sobre),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
