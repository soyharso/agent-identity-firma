#!/usr/bin/env python3
"""Verifica los sobres del libro (D-6, D-7, D-9), sin confiar en lo que el sobre dice de sí.

Implementa el DISEÑO v1 tal como está congelado: la superficie recibe SOLO el .jsonl.
"""
import argparse
import json
import pathlib
import sys

import jwt
import requests
from cryptography import x509
from cryptography.hazmat.backends import default_backend

JWKS_HUMANO = "https://www.googleapis.com/oauth2/v3/certs"
X509_SA = "https://www.googleapis.com/robot/v1/metadata/x509/{email}"

ESTADOS_SOLO_HUMANO = {"descartada", "cerrada_con_juicio"}   # D-7


def clave_publica(iss, kid):
    """D-6: la clase de emisor la impone de dónde viene la clave, no el sobre."""
    if iss == "https://accounts.google.com":
        jwks = requests.get(JWKS_HUMANO, timeout=15).json()
        for k in jwks["keys"]:
            if k["kid"] == kid:
                return "humano", jwt.PyJWK(k).key
        return "humano", None
    if iss.endswith(".iam.gserviceaccount.com"):
        certs = requests.get(X509_SA.format(email=iss), timeout=15).json()
        pem = certs.get(kid)
        if not pem:
            return "agente", None
        return "agente", x509.load_pem_x509_certificate(
            pem.encode(), default_backend()).public_key()
    return "desconocido", None


def veredicto(sobre):
    try:
        cab = jwt.get_unverified_header(sobre)
        crudo = jwt.decode(sobre, options={"verify_signature": False})
    except Exception as e:
        return "FIRMA_INVALIDA", {"error": f"sobre ilegible: {e}"}

    iss = crudo.get("iss", "")
    clase, clave = clave_publica(iss, cab.get("kid"))
    if clase == "desconocido":
        return "EMISOR_DESCONOCIDO", {"iss": iss}
    if clave is None:
        return "FIRMA_INVALIDA", {"error": "no hay clave pública para ese kid", "iss": iss}

    try:
        datos = jwt.decode(sobre, clave, algorithms=["RS256"],
                           options={"verify_aud": False, "verify_exp": False})
    except Exception as e:
        return "FIRMA_INVALIDA", {"error": str(e)}

    # D-7: política de rol cableada
    curado_por = datos.get("curado_por")
    estado = datos.get("estado")
    if clase == "agente" and curado_por != "modelo":
        return "RECHAZADO_SUPLANTACION", {"clase": clase, "curado_por": curado_por}
    if estado in ESTADOS_SOLO_HUMANO and clase != "humano":
        return "RECHAZADO_SUPLANTACION", {"clase": clase, "estado": estado}
    return "OK", {"clase": clase, "curado_por": curado_por, "estado": estado,
                  "hash_contenido": datos.get("hash_contenido"),
                  "agent_id": datos.get("agent_id")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("libro")
    args = ap.parse_args()
    malos = 0
    for n, linea in enumerate(pathlib.Path(args.libro).read_text().splitlines(), 1):
        if not linea.strip():
            continue
        fila = json.loads(linea)
        v, det = veredicto(fila["jwt"])
        if v != "OK":
            malos += 1
        print(f"{n:>3} {fila.get('peticion_id'):<10} {v:<24} {json.dumps(det, ensure_ascii=False)}")
    sys.exit(1 if malos else 0)


if __name__ == "__main__":
    main()
