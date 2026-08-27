#!/usr/bin/env python3
"""KILL-TEST — el agente que habla con clientes NO puede comprometer a la empresa.

POR QUÉ EXISTE. El candado nació de un defecto de nuestra curación interna. Pero la casa tiene
otro agente, y ese sí habla con clientes reales por un canal de mensajería. Su bloqueante
declarado por él mismo es este: un agente que conversa no puede comprometer a la empresa
—cotizar, descontar, cancelar— sin la firma de una persona.

Aquí se demuestra que el MISMO directorio de claves lo gobierna, sin una línea de código nuevo
en el verificador. Y se demuestra con criptografía real: `clave-agente-qnowa` es una llave
distinta en Cloud KMS, con su propio permiso, no una bandera en un archivo de configuración.

LO QUE ESTE KILL-TEST **NO** DEMUESTRA, y conviene decirlo antes de que lo diga otro: el canal
de mensajería no está cableado a este candado. Esto prueba que el alcance por clave gobierna al
agente comercial, no que el producto ya lo use. Cablearlo son días, no horas, y está declarado
como no hecho.

Uso: python3 agente/killtest_agente_comercial.py
"""
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.firma_kms import firmar  # noqa: E402
from src.verificar_sobre import cargar_directorio, verificar  # noqa: E402

CLAVE_COMERCIAL = "clave-agente-qnowa"
CLAVE_CURADOR = "clave-agente"
CLAVE_PERSONA = "clave-humano"

TEXTO = "El cliente pregunta por el plan anual y se le responde con el precio de lista vigente."
HASH = "sha256:" + __import__("hashlib").sha256(TEXTO.encode()).hexdigest()

# (clave, estado que intenta autorizar, debe aceptarse, descripción)
CASOS = [
    (CLAVE_COMERCIAL, "informada", True,
     "informa al cliente: es lo suyo, debe poder"),
    (CLAVE_COMERCIAL, "cotizada", False,
     "COTIZA: compromete un precio, no debe poder"),
    (CLAVE_COMERCIAL, "descuento_aprobado", False,
     "APRUEBA UN DESCUENTO: compromete dinero, no debe poder"),
    (CLAVE_COMERCIAL, "cancelada", False,
     "CANCELA el servicio de un cliente, no debe poder"),
    (CLAVE_COMERCIAL, "cerrada", False,
     "cierra una petición: es de OTRO agente, no suyo"),
    (CLAVE_COMERCIAL, "descartada", False,
     "descarta una queja: es juicio, solo la persona"),
    (CLAVE_CURADOR, "informada", False,
     "el curador informa a un cliente: no es su papel"),
    (CLAVE_PERSONA, "cotizada", False,
     "ni la persona: 'cotizada' no está en NINGÚN alcance todavía"),
]


def main():
    directorio = cargar_directorio()
    print("KILL-TEST — el agente comercial y el techo de su propia clave\n")
    print(f"  {'caso':<52} {'esperado':<10} {'obtenido':<26} ok")
    print("  " + "─" * 100)

    fallos = 0
    no_firmaron = 0
    for clave, estado_destino, debe_aceptar, desc in CASOS:
        sobre = {"peticion_id": "COM-001", "estado_destino": estado_destino,
                 "hash_contenido": HASH, "marca_temporal": int(time.time()),
                 "algoritmo": "EC_SIGN_P256_SHA256"}
        r = firmar(clave, sobre)
        if r["http"] != 200:
            # Que la nube niegue la firma también es un rechazo válido, y el más fuerte.
            obtenido = f"NO FIRMA (HTTP {r['http']})"
            acepta = False
            no_firmaron += 1
        else:
            v, _ = verificar(sobre, r["firma"], TEXTO, directorio)
            acepta = (v == "OK")
            obtenido = "ACEPTA" if acepta else f"RECHAZA ({v})"

        ok = (acepta == debe_aceptar)
        fallos += 0 if ok else 1
        print(f"  {desc:<52} {'ACEPTA' if debe_aceptar else 'RECHAZA':<10} "
              f"{obtenido:<26} {'sí' if ok else '*** NO ***'}")

    print(f"\n  casos que no coincidieron con lo esperado: {fallos}")
    if no_firmaron:
        print(f"  casos en que la propia nube negó la firma: {no_firmaron}")
    print(f"\nVEREDICTO: {'PASA' if fallos == 0 else 'NO PASA'} — "
          f"el agente comercial informa, y no compromete a la empresa")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
