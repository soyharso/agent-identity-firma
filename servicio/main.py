"""El servicio: dos entradas, y ninguna que firme.

La fase cero encontró que el permiso de invocar de la plataforma es **por servicio, no por
ruta**: quien pueda llamar a una entrada puede llamar a la otra. Así que la separación entre
«el temporizador despierta» y «la persona decide» **la hace este programa**, leyendo la identidad
del token que la plataforma ya validó. Se dice así, y no como una garantía de la nube.
"""
import base64
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "ai-transf-lab-0827")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

import asyncio                                                    # noqa: E402

from flask import Flask, jsonify, request                         # noqa: E402

from src import estado                                            # noqa: E402

app = Flask(__name__)

# Quién puede hacer qué. Se lee del entorno para no tener correos en el código.
IDENTIDAD_HUMANA = os.environ.get("IDENTIDAD_HUMANA", "")
IDENTIDAD_TEMPORIZADOR = os.environ.get("IDENTIDAD_TEMPORIZADOR", "")
TOPE_POR_DESPERTAR = int(os.environ.get("TOPE_POR_DESPERTAR", "5"))


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


def _comprobar_firma_humana(sobre, firma_b64):
    """Comprueba, no confía. Y con la MISMA compuerta que el resto: el alcance de la clave.

    Antes esta función tenía su propia lógica y su propia serialización. Tener dos formas de
    comprobar lo mismo es tener dos formas de equivocarse: aquí se llama al verificador único.
    """
    from src.verificar_sobre import verificar
    return verificar(sobre, firma_b64)


def _negar(esperada, quien):
    return jsonify({"error": "identidad no autorizada para esta entrada",
                    "quien_llama": quien or "(sin token)",
                    "esperada": esperada or "(sin configurar)"}), 403


@app.post("/despertar")
def despertar():
    """Lo llama el temporizador. Procesa lo que haya pendiente, con tope."""
    quien = quien_llama()
    if IDENTIDAD_TEMPORIZADOR and quien != IDENTIDAD_TEMPORIZADOR:
        return _negar(IDENTIDAD_TEMPORIZADOR, quien)

    from agente.grafo import correr_para_servicio
    hechas = asyncio.run(correr_para_servicio(TOPE_POR_DESPERTAR))
    return jsonify({"despertado_por": quien, "procesadas": hechas})


@app.post("/decidir")
def decidir():
    """La llama la persona. NO firma: solo deja anotada su decisión."""
    quien = quien_llama()
    if IDENTIDAD_HUMANA and quien != IDENTIDAD_HUMANA:
        return _negar(IDENTIDAD_HUMANA, quien)

    cuerpo = request.get_json(silent=True) or {}
    pid = cuerpo.get("peticion_id")
    decision = str(cuerpo.get("decision", "")).strip().lower()
    if not pid or decision not in ("cerrada", "descartada", "no"):
        return jsonify({"error": "hace falta peticion_id y decision (cerrada|descartada|no)"}), 400

    # El servicio NO firma como persona: no puede, y esa es la promesa. La firma viene hecha
    # desde la máquina de quien decide, y aquí solo se COMPRUEBA contra la clave pública.
    sobre, firma = cuerpo.get("sobre"), cuerpo.get("firma")
    if decision != "no":
        if not sobre or not firma:
            return jsonify({"error": "falta el sobre firmado por la persona",
                            "nota": "este servicio no puede firmar como humano, y no debe"}), 400
        veredicto, detalle = _comprobar_firma_humana(sobre, firma)
        if veredicto != "OK":
            return jsonify({"error": "la firma no valida como humana",
                            "veredicto": veredicto, "detalle": detalle}), 400
        estado.guardar(pid, sobre=sobre, firma=firma, veredicto="OK",
                       hash_contenido=sobre.get("hash_contenido"))

    estado.anotar_decision_humana(pid, decision)
    return jsonify({"anotado": True, "peticion_id": pid, "decision": decision,
                    "por": quien, "firma_comprobada": decision != "no"})


@app.get("/estado")
def ver_estado():
    return jsonify({"esperando_persona": estado.pendientes_de_persona()})


@app.get("/quien")
def quien():
    """Diagnóstico: qué cabeceras llegan y qué identidad se lee. No devuelve el token."""
    cabs = {k: (v[:12] + "…" if k.lower() == "authorization" else v[:60])
            for k, v in request.headers.items()}
    return jsonify({"identidad_leida": quien_llama() or "(vacía)", "cabeceras": cabs})


@app.get("/")
def salud():
    return jsonify({"rutas": ["/despertar", "/decidir", "/estado"],
                    "nota": "ninguna entrada firma; la firma vive dentro del grafo"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
