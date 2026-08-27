"""Firma con las claves gestionadas: la del agente y la de la persona.

La clave privada nunca sale del servicio de claves de Google. Aquí solo se pide la firma.
Quién puede pedir cuál lo decide un permiso sobre el recurso, no este código.
"""
import base64
import hashlib
import json

import google.auth
import google.auth.transport.requests
import requests

PROYECTO = "ai-transf-lab-0827"
REGION = "us-central1"
LLAVERO = "firmas"
CLAVE_AGENTE = "clave-agente"
CLAVE_HUMANO = "clave-humano"

_BASE = ("https://cloudkms.googleapis.com/v1/projects/{p}/locations/{r}"
         "/keyRings/{a}/cryptoKeys/{k}/cryptoKeyVersions/1")


def canonico(sobre: dict) -> bytes:
    """La forma exacta que se firma. El verificador la recalcula igual o no valida."""
    return json.dumps(sobre, sort_keys=True, separators=(",", ":")).encode()


def resumen(texto: str) -> str:
    return "sha256:" + hashlib.sha256(texto.encode()).hexdigest()


def _sesion():
    cred, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"])
    cred.refresh(google.auth.transport.requests.Request())
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {cred.token}"
    # El proyecto al que se le cobra la cuota. Sin esto, la credencial del operador usa SU
    # proyecto por defecto —que puede ser cualquiera y no tener esta interfaz habilitada— y la
    # llamada muere con un 403 que parece de permisos y en realidad es de proyecto equivocado.
    s.headers["x-goog-user-project"] = PROYECTO
    return s


def firmar(clave: str, sobre: dict) -> dict:
    """Pide la firma. Devuelve el resultado crudo, incluido el fallo: el 403 es un dato."""
    digest = hashlib.sha256(canonico(sobre)).digest()
    url = _BASE.format(p=PROYECTO, r=REGION, a=LLAVERO, k=clave) + ":asymmetricSign"
    r = _sesion().post(url, json={"digest": {"sha256": base64.b64encode(digest).decode()}},
                       timeout=30)
    cuerpo = r.json()
    if r.ok:
        return {"clave": clave, "http": 200, "firma": cuerpo["signature"]}
    return {"clave": clave, "http": r.status_code,
            "error": cuerpo.get("error", {}).get("status"),
            "mensaje": cuerpo.get("error", {}).get("message", "")[:220]}
