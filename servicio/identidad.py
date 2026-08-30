"""Quién llama, leído del token que la plataforma ya validó.

Vivía dentro de `servicio/main.py`. Sale aquí porque el mediador necesita exactamente la misma
lectura, y tener dos copias de esto es tener dos formas de equivocarse — que es el argumento con
el que este proyecto ya unificó el verificador. El comentario sobre el esquema en minúscula viaja
con la función: se pagó caro y no puede quedarse huérfano.
"""
import base64
import json

from flask import request


def quien_llama() -> str:
    """El correo del que llama, sacado del token que la plataforma YA validó.

    No se verifica la firma aquí a propósito: si la petición llegó, la plataforma comprobó el
    token. Lo que este programa añade es la autorización por identidad, que la plataforma no
    sabe hacer por ruta.
    """
    cab = request.headers.get("Authorization", "")
    # Cloud Run entrega el esquema en MINÚSCULA («bearer», no «Bearer»). Comparar distinguiendo
    # mayúsculas dejaba la identidad vacía y, con ella, la autorización abierta de par en par:
    # el programa creía que nadie se identificaba y todas las entradas contestaban lo mismo.
    if cab[:7].lower() != "bearer ":
        return ""
    try:
        carga = cab.split(" ", 1)[1].split(".")[1]
        carga += "=" * (-len(carga) % 4)
        return json.loads(base64.urlsafe_b64decode(carga)).get("email", "")
    except Exception:                                             # noqa: BLE001
        return ""
