"""El servicio: dos entradas, y ninguna que firme.

La fase cero encontró que el permiso de invocar de la plataforma es **por servicio, no por
ruta**: quien pueda llamar a una entrada puede llamar a la otra. Así que la separación entre
«el temporizador despierta» y «la persona decide» **la hace este programa**, leyendo la identidad
del token que la plataforma ya validó. Se dice así, y no como una garantía de la nube.
"""
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "ai-transf-lab-0827")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

import asyncio                                                    # noqa: E402

from flask import Flask, jsonify, request                         # noqa: E402

from identidad import quien_llama                                 # noqa: E402
from src import estado                                            # noqa: E402

app = Flask(__name__)

# Quién puede hacer qué. Se lee del entorno para no tener correos en el código.
IDENTIDAD_HUMANA = os.environ.get("IDENTIDAD_HUMANA", "")
IDENTIDAD_TEMPORIZADOR = os.environ.get("IDENTIDAD_TEMPORIZADOR", "")
TOPE_POR_DESPERTAR = int(os.environ.get("TOPE_POR_DESPERTAR", "5"))


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
    #
    # LA COMPROBACIÓN YA NO SE HACE AQUÍ, y no es un descuido: se hace en la puerta, que es lo
    # único que puede escribir. Antes esta entrada verificaba por su cuenta y luego escribía —y
    # verificaba SIN `peticion_esperada`, así que una aprobación auténtica del caso de al lado
    # entraba entera: firma buena, firmante conocido, hash coherente consigo mismo y estado en
    # alcance. `estado.aplicar_cierre` verifica CONTRA ESTA petición. El agujero era real y se
    # reproduce en `agente/killtest_puerta.py`.
    sobre, firma = cuerpo.get("sobre"), cuerpo.get("firma")
    if decision != "no":
        if not sobre or not firma:
            return jsonify({
                "error": "the human-signed envelope is missing",
                "note": "this service cannot sign as a human, and must not",
                "note_es": "este servicio no puede firmar como humano, y no debe"}), 400
        aplicado, detalle = estado.aplicar_cierre(pid, sobre, firma)
        if not aplicado:
            return jsonify({"error": "the envelope was not accepted for this request",
                            "error_es": "el sobre no fue aceptado para esta petición",
                            "record_unchanged": True, "gate": detalle}), 400

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


@app.post("/intentar-escribir-directo")
def intentar_escribir_directo():
    """La demostración de la PUERTA: el agente intenta escribir el registro sin pasar por nadie.

    Hermana de `/intentar-suplantar`, y por el mismo motivo: no es una simulación ni un mensaje
    preparado. Este servicio corre con la identidad del agente, y aquí se llama a la interfaz de
    Firestore A PELO —sin `src.estado`, sin mediador, sin verificador— y se devuelve lo que la
    nube conteste. Si algún día contestara 200, querría decir que la puerta es decorativa, y esta
    ruta lo enseñaría igual.

    Escribe sobre el documento que se le pase, y por defecto sobre uno de usar y tirar: si la
    nube dijera que sí, que el destrozo sea el mínimo.
    """
    quien = quien_llama()
    if IDENTIDAD_HUMANA and quien not in (IDENTIDAD_HUMANA, IDENTIDAD_TEMPORIZADOR):
        return _negar(IDENTIDAD_HUMANA, quien)

    import google.auth
    import google.auth.transport.requests
    import requests

    cuerpo = request.get_json(silent=True) or {}
    pid = str(cuerpo.get("peticion_id") or "PET-INTENTO-DIRECTO")

    cred, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    cred.refresh(google.auth.transport.requests.Request())
    url = (f"https://firestore.googleapis.com/v1/projects/{estado.PROYECTO}"
           f"/databases/(default)/documents/{estado.COLECCION}/{pid}"
           "?updateMask.fieldPaths=veredicto&updateMask.fieldPaths=firma")
    r = requests.patch(url, headers={"Authorization": f"Bearer {cred.token}"}, timeout=30,
                       json={"fields": {"veredicto": {"stringValue": "OK"},
                                        "firma": {"stringValue": "written-without-an-envelope"}}})
    detalle = {}
    try:
        detalle = r.json().get("error", {})
    except Exception:                                             # noqa: BLE001
        pass

    return jsonify({
        "this_service_runs_as": "sa-agente-curador — the AGENT's identity",
        "attempted": "a direct Firestore write, bypassing the mediator and the verifier",
        "target": pid,
        "http": r.status_code,
        "status": detalle.get("status"),
        "message": (detalle.get("message") or "")[:220],
        "written": r.ok,
        "note": ("the gate is not this code: the agent has no write permission on the record. "
                 "Only the mediator does, and the mediator asks for a verified envelope first"),
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
                                 "/intentar-suplantar", "/intentar-escribir-directo"],
                    "note": "no endpoint signs; signing lives inside the graph"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
