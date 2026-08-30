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
    return jsonify({"error": "identity not authorised for this endpoint",
                    "error_es": "identidad no autorizada para esta entrada",
                    "caller": quien or "(no token)",
                    "expected": esperada or "(not configured)"}), 403


@app.post("/despertar")
def despertar():
    """Lo llama el temporizador. Procesa lo que haya pendiente, con tope."""
    quien = quien_llama()
    if IDENTIDAD_TEMPORIZADOR and quien != IDENTIDAD_TEMPORIZADOR:
        return _negar(IDENTIDAD_TEMPORIZADOR, quien)

    from agente.grafo import correr_para_servicio
    hechas = asyncio.run(correr_para_servicio(TOPE_POR_DESPERTAR))
    return jsonify({"woken_by": quien, "processed": hechas})


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
        return jsonify({"error": "peticion_id and decision are required "
                                 "(cerrada|descartada|no)"}), 400

    # El servicio NO firma como persona: no puede, y esa es la promesa. La firma viene hecha
    # desde la máquina de quien decide, y aquí solo se COMPRUEBA contra la clave pública.
    sobre, firma = cuerpo.get("sobre"), cuerpo.get("firma")
    if decision != "no":
        if not sobre or not firma:
            return jsonify({
                "error": "the human-signed envelope is missing",
                "note": "this service cannot sign as a human, and must not",
                "note_es": "este servicio no puede firmar como humano, y no debe"}), 400
        veredicto, detalle = _comprobar_firma_humana(sobre, firma)
        if veredicto != "OK":
            return jsonify({"error": "the signature does not validate as human",
                            "verdict": veredicto, "detail": detalle}), 400
        estado.guardar(pid, sobre=sobre, firma=firma, veredicto="OK",
                       hash_contenido=sobre.get("hash_contenido"))

    estado.anotar_decision_humana(pid, decision)
    # `by` sale en pantalla durante la demostración, y el vídeo es público. Lo que importa aquí
    # no es QUIÉN es la persona, sino que fue UNA PERSONA y que el servicio pudo comprobarlo.
    # Se devuelve el dominio: dice lo mismo sin poner un correo personal en cámara. La identidad
    # completa sigue dentro del sobre firmado, que es donde tiene que estar para auditar.
    dominio = str(quien).split("@")[-1] if "@" in str(quien) else quien
    return jsonify({"recorded": True, "request_id": pid, "decision": decision,
                    "by": f"a person at {dominio}", "signature_verified": decision != "no"})


@app.post("/intentar-suplantar")
def intentar_suplantar():
    """La demostración: el servicio INTENTA firmar como persona, delante de quien mire.

    No es una simulación ni un mensaje preparado: se llama de verdad al servicio de claves con la
    clave de la persona, y se devuelve lo que la nube conteste. Si algún día contestara 200,
    querría decir que la garantía se rompió, y esta ruta lo enseñaría igual.
    """
    quien = quien_llama()
    if IDENTIDAD_HUMANA and quien not in (IDENTIDAD_HUMANA, IDENTIDAD_TEMPORIZADOR):
        return _negar(IDENTIDAD_HUMANA, quien)

    from src.firma_kms import CLAVE_AGENTE, CLAVE_HUMANO, firmar
    sobre = {"peticion_id": "DEMO", "estado_destino": "descartada",
             "tipo_firmante": "HUMANO", "hash_contenido": "sha256:demo",
             "marca_temporal": 0, "algoritmo": "EC_SIGN_P256_SHA256"}
    con_la_suya = firmar(CLAVE_AGENTE, sobre)
    con_la_humana = firmar(CLAVE_HUMANO, sobre)
    return jsonify({
        "this_service_runs_as": "sa-agente-curador — the AGENT's identity",
        "1_with_its_own_key": {"http": con_la_suya.get("http"),
                               "signature": (con_la_suya.get("firma") or "")[:44] or None},
        "2_with_the_human_key": {"http": con_la_humana.get("http"),
                                 "error": con_la_humana.get("error"),
                                 "message": con_la_humana.get("mensaje")},
        "3_and_even_if_it_had_signed": ("the verifier would reject it anyway: the state "
                                        "'descartada' is outside the scope of the machine key"),
    })


@app.get("/estado")
def ver_estado():
    return jsonify({"awaiting_a_human": estado.pendientes_de_persona()})


@app.get("/quien")
def quien():
    """Diagnóstico: qué cabeceras llegan y qué identidad se lee. No devuelve el token."""
    cabs = {k: (v[:12] + "…" if k.lower() == "authorization" else v[:60])
            for k, v in request.headers.items()}
    return jsonify({"identidad_leida": quien_llama() or "(vacía)", "cabeceras": cabs})


@app.get("/")
def salud():
    return jsonify({"endpoints": ["/despertar", "/decidir", "/estado",
                                 "/intentar-suplantar"],
                    "note": "no endpoint signs; signing lives inside the graph"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
