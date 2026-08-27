#!/usr/bin/env python3
"""Firma humana (D-5): id_token OIDC de Google de la cuenta del operador.

OBSTÁCULO REGISTRADO al implementar: el diseño (§4) pide que el sobre humano lleve el mismo
esquema — `sub`, `estado`, `hash_contenido` — pero el id_token lo emite Google y sus claims
son fijos. No hay forma de meter `estado` ni `hash_contenido` dentro. Se anexa tal cual,
que es lo que el diseño permite, y el verificador ve un sobre sin esos campos.
"""
import argparse
import json
import pathlib
import subprocess
import time


def id_token():
    return subprocess.run(["gcloud", "auth", "print-identity-token"],
                          capture_output=True, text=True, check=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--peticion", required=True)
    ap.add_argument("--estado", required=True)
    ap.add_argument("--texto-archivo", required=True)
    ap.add_argument("--libro", default="libro/firmas.jsonl")
    args = ap.parse_args()

    pathlib.Path(args.texto_archivo).read_text()
    sobre = id_token()

    libro = pathlib.Path(args.libro)
    libro.parent.mkdir(parents=True, exist_ok=True)
    with libro.open("a") as fh:
        fh.write(json.dumps({"ts": int(time.time()),
                             "peticion_id": args.peticion,
                             "jwt": sobre}) + "\n")
    print("sobre humano anexado a", libro)


if __name__ == "__main__":
    main()
