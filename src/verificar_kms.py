#!/usr/bin/env python3
"""Verifica sobres firmados sin confiar en lo que el sobre dice de sí mismo.

Lo único que necesita son las dos claves PÚBLICAS. No usa credenciales de Google, no llama a
ninguna interfaz: cualquiera puede correr esto y llegar al mismo veredicto.

La clase de firmante NO la declara el sobre: la decide QUÉ CLAVE valida la firma.
"""
import argparse
import base64
import hashlib
import json
import pathlib
import sys

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives.serialization import load_pem_public_key

CLASES = {"clave-agente": "modelo", "clave-humano": "humano"}
ESTADOS_SOLO_HUMANO = {"descartada", "cerrada_con_juicio"}


def canonico(sobre):
    return json.dumps(sobre, sort_keys=True, separators=(",", ":")).encode()


def cargar_claves(dir_claves):
    claves = {}
    for nombre in CLASES:
        ruta = pathlib.Path(dir_claves) / f"{nombre}.pem"
        claves[nombre] = load_pem_public_key(ruta.read_bytes())
    return claves


def quien_firmo(claves, mensaje, firma):
    """Prueba la firma contra cada clave pública. La que valide dice quién firmó."""
    digest = hashlib.sha256(mensaje).digest()
    for nombre, pub in claves.items():
        try:
            pub.verify(firma, digest,
                       ec.ECDSA(Prehashed(hashes.SHA256())))
            return nombre
        except InvalidSignature:
            continue
    return None


def veredicto(claves, fila, texto_original=None):
    sobre = fila["sobre"]
    try:
        firma = base64.b64decode(fila["firma"])
    except Exception:                                        # noqa: BLE001
        return "FIRMA_ILEGIBLE", {}

    clave = quien_firmo(claves, canonico(sobre), firma)
    if clave is None:
        return "FIRMA_INVALIDA", {"por_que": "ninguna clave conocida valida esta firma"}

    clase = CLASES[clave]

    # El texto se comprueba aquí, y por eso el verificador lo recibe. Es el hallazgo que
    # la fase cero del diseño v1 dio por seguro: sin el texto, este veredicto es inalcanzable.
    if texto_original is not None:
        esperado = "sha256:" + hashlib.sha256(texto_original.encode()).hexdigest()
        if sobre.get("hash_contenido") != esperado:
            return "CONTENIDO_ALTERADO", {"clase": clase}

    if clase == "modelo" and sobre.get("curado_por") != "modelo":
        return "RECHAZADO_SUPLANTACION", {
            "clase": clase, "declaraba": sobre.get("curado_por"),
            "por_que": "firmado con la clave del agente, pero se declara humano"}

    if sobre.get("estado") in ESTADOS_SOLO_HUMANO and clase != "humano":
        return "RECHAZADO_SUPLANTACION", {
            "clase": clase, "estado": sobre.get("estado"),
            "por_que": "ese estado solo lo puede declarar una persona"}

    return "OK", {"clase": clase, "clave": clave, "estado": sobre.get("estado")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("libro", help="jsonl con una línea por sobre: {sobre, firma}")
    ap.add_argument("--claves", default="claves")
    ap.add_argument("--texto-archivo", default=None,
                    help="el texto curado, para comprobar que el sobre no miente sobre él")
    args = ap.parse_args()

    texto = pathlib.Path(args.texto_archivo).read_text() if args.texto_archivo else None
    claves = cargar_claves(args.claves)

    malos = 0
    for n, linea in enumerate(pathlib.Path(args.libro).read_text().splitlines(), 1):
        if not linea.strip():
            continue
        fila = json.loads(linea)
        v, det = veredicto(claves, fila, texto)
        if v != "OK":
            malos += 1
        pid = fila.get("sobre", {}).get("peticion_id", "?")
        print(f"{n:>3} {pid:<10} {v:<24} {json.dumps(det, ensure_ascii=False)}")
    sys.exit(1 if malos else 0)


if __name__ == "__main__":
    main()
