#!/usr/bin/env python3
"""Firma un sobre de curación con la identidad criptográfica del AGENTE (D-1..D-4).

Implementa el DISEÑO v1 tal como está congelado, sin corregirlo con los ataques de fase cero.
"""
import argparse
import hashlib
import json
import pathlib
import time

import google.auth
import google.auth.transport.requests
import requests

PROYECTO = "ai-transf-lab-0827"
SA = f"sa-agente-curador@{PROYECTO}.iam.gserviceaccount.com"
ENDPOINT = ("https://iamcredentials.googleapis.com/v1/"
            f"projects/-/serviceAccounts/{SA}:signJwt")


def sesion_autenticada():
    """D-1: sin clave descargada. Se usa la credencial ambiente (ADC)."""
    cred, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"])
    cred.refresh(google.auth.transport.requests.Request())
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {cred.token}"
    return s


def construir_payload(peticion, estado, texto, agent_id):
    ahora = int(time.time())
    payload = {
        "iss": SA,
        "sub": peticion,
        "iat": ahora,
        "exp": ahora + 600,                       # D-3
        "curado_por": "modelo",                   # D-3: valor fijo
        "estado": estado,
        "hash_contenido": "sha256:" + hashlib.sha256(texto.encode()).hexdigest(),
    }
    if agent_id:
        payload["agent_id"] = agent_id            # D-10
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--peticion", required=True)
    ap.add_argument("--estado", required=True)
    ap.add_argument("--texto-archivo", required=True)
    ap.add_argument("--agent-id", default="")
    ap.add_argument("--libro", default="libro/firmas.jsonl")
    ap.add_argument("--curado-por", default="modelo",
                    help="solo para el kill-test K1: intentar firmar como humano")
    args = ap.parse_args()

    texto = pathlib.Path(args.texto_archivo).read_text()
    payload = construir_payload(args.peticion, args.estado, texto, args.agent_id)
    payload["curado_por"] = args.curado_por       # K1 fuerza "humano" aquí

    s = sesion_autenticada()
    r = s.post(ENDPOINT, json={"payload": json.dumps(payload)}, timeout=30)
    print(f"HTTP {r.status_code}")
    if r.status_code != 200:
        print(r.text[:1500])
        raise SystemExit(1)
    sobre = r.json()["signedJwt"]

    libro = pathlib.Path(args.libro)
    libro.parent.mkdir(parents=True, exist_ok=True)
    with libro.open("a") as fh:                    # D-9
        fh.write(json.dumps({"ts": int(time.time()),
                             "peticion_id": args.peticion,
                             "jwt": sobre}) + "\n")
    print("sobre anexado a", libro)


if __name__ == "__main__":
    main()
