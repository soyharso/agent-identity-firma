#!/usr/bin/env python3
"""La persona decide y firma DESDE SU PROPIA MÁQUINA, con su propia credencial.

Esto no es una comodidad: es la consecuencia de que la promesa se cumpla. El servicio corre con
la identidad del agente, y esa identidad **no tiene permiso sobre la clave de la persona**. Al
intentarlo, la nube le dice que no. Así que la firma humana no puede nacer en el servidor: nace
aquí, donde está la persona, y el servicio solo la recibe y la comprueba.

Uso:
  python3 src/decidir_como_persona.py PET-002 descartada
"""
import argparse
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import requests  # noqa: E402

from src.firma_kms import CLAVE_HUMANO, firmar, resumen  # noqa: E402

SERVICIO = "https://candado-firma-141981963817.us-central1.run.app"
PETICIONES = pathlib.Path(__file__).resolve().parent.parent / "libro" / "peticiones.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("peticion_id")
    ap.add_argument("decision", choices=["cerrada", "descartada", "no"])
    ap.add_argument("--servicio", default=SERVICIO)
    args = ap.parse_args()

    texto = json.loads(PETICIONES.read_text())[args.peticion_id]["texto"]
    import time
    sobre = {"peticion_id": args.peticion_id,
             "estado_destino": args.decision,
             "tipo_firmante": "HUMANO",
             "curado_por": "humano",
             "hash_contenido": resumen(texto),
             "marca_temporal": int(time.time()),
             "algoritmo": "EC_SIGN_P256_SHA256"}

    if args.decision == "no":
        firma = None
        print("the person does NOT authorise: nothing is signed")
    else:
        r = firmar(CLAVE_HUMANO, sobre)
        if r["http"] != 200:
            print("could not sign:", r)
            return 1
        firma = r["firma"]
        print(f"signed by the person with THEIR OWN key · {firma[:32]}…")

    token = subprocess.run(["gcloud", "auth", "print-identity-token"],
                           capture_output=True, text=True, check=True).stdout.strip()
    resp = requests.post(f"{args.servicio}/decidir",
                         headers={"Authorization": f"Bearer {token}"},
                         json={"peticion_id": args.peticion_id, "decision": args.decision,
                               "sobre": sobre, "firma": firma},
                         timeout=60)
    print(f"the service replied HTTP {resp.status_code}: {resp.text[:300]}")
    return 0 if resp.ok else 1


if __name__ == "__main__":
    sys.exit(main())
