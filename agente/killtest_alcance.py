#!/usr/bin/env python3
"""KILL-TEST — el alcance por clave contra el verificador que propusieron.

La propuesta externa definía `alcance_permitido` por clave y luego NO lo usaba: su verificador
comprobaba a mano un único estado. Esto firma de verdad, con las claves de verdad, y compara los
dos veredictos caso por caso.

Si alguna fila sale ACEPTA en la columna «su verificador» y RECHAZA en la nuestra, ahí está la
diferencia entre declarar el alcance y usarlo.
"""
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.firma_kms import CLAVE_AGENTE, CLAVE_HUMANO, firmar  # noqa: E402
from src.verificar_sobre import cargar_directorio, verificar   # noqa: E402

TEXTO = "Se descarta la queja del cliente: revisando el historial, el error fue suyo."
HASH = "sha256:" + __import__("hashlib").sha256(TEXTO.encode()).hexdigest()


def su_verificador(estado_destino, tipo):
    """La política del verificador propuesto, reducida a su lógica: un solo estado a mano."""
    if estado_destino == "descartada" and tipo != "HUMANO":
        return "RECHAZA"
    return "ACEPTA"


CASOS = [
    (CLAVE_AGENTE, "MAQUINA", "descartada",          "la máquina intenta descartar"),
    (CLAVE_AGENTE, "MAQUINA", "cerrada_con_juicio",  "estado de juicio con otro nombre"),
    (CLAVE_AGENTE, "MAQUINA", "perdonada",           "otro estado de juicio cualquiera"),
    (CLAVE_AGENTE, "MAQUINA", "cerrada",             "cierre legítimo de la máquina"),
    (CLAVE_HUMANO, "HUMANO",  "descartada",          "la persona descarta: debe poder"),
]


def main():
    directorio = cargar_directorio()
    print("KILL-TEST — alcance por clave frente al verificador propuesto\n")
    print(f"  {'caso':<38} {'su verif.':<10} {'el nuestro':<22} ¿tapa el hueco?")
    print("  " + "─" * 92)

    huecos_tapados = 0
    fallos = 0
    for clave, tipo, estado_destino, desc in CASOS:
        sobre = {"peticion_id": "PET-002", "estado_destino": estado_destino,
                 "hash_contenido": HASH, "marca_temporal": int(time.time()),
                 "algoritmo": "EC_SIGN_P256_SHA256"}
        r = firmar(clave, sobre)
        if r["http"] != 200:
            print(f"  {desc:<38} no se pudo firmar: {r.get('mensaje','')[:40]}")
            fallos += 1
            continue

        v, det = verificar(sobre, r["firma"], TEXTO, directorio)
        suyo = su_verificador(estado_destino, tipo)
        nuestro = "ACEPTA" if v == "OK" else f"RECHAZA ({v})"
        tapa = suyo == "ACEPTA" and v != "OK"
        if tapa:
            huecos_tapados += 1
        legitimo = desc.startswith(("cierre legítimo", "la persona"))
        if legitimo and v != "OK":
            fallos += 1
        print(f"  {desc:<38} {suyo:<10} {nuestro:<22} {'SÍ' if tapa else ''}")

    print(f"\n  huecos que su verificador dejaba y el nuestro cierra: {huecos_tapados}")
    print(f"  casos legítimos rechazados por error: {fallos}")
    print("VEREDICTO:", "PASA" if (huecos_tapados >= 2 and fallos == 0) else "NO PASA")
    sys.exit(0 if (huecos_tapados >= 2 and fallos == 0) else 1)


if __name__ == "__main__":
    main()
