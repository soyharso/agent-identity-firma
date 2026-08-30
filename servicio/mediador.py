"""EL MEDIADOR: el único que puede escribir el registro, y solo con un sobre verificado.

QUÉ RESUELVE. Hasta hoy el agente tenía `roles/datastore.user` y escribía el estado él mismo. El
sobre firmado se producía, se guardaba y probaba DESPUÉS quién cerró qué — pero nada rechazaba un
cierre que llegara sin él. Era un recibo, no una puerta.

Este servicio corre con OTRA identidad —`sa-mediador`, la única con permiso de escritura sobre
Firestore— y expone exactamente dos entradas:

  · `/aplicar-cierre`  verifica el sobre CONTRA ESTA petición y solo entonces escribe. Es lo
                       único en todo el sistema que puede escribir `sobre`, `firma` y
                       `hash_contenido`.
  · `/anotar`          el trámite: reservar, apartar para una persona, anotar una decisión,
                       anotar el desenlace de una pasada que no firmó nada. Tiene PROHIBIDO
                       tocar los campos de cierre, y la prohibición se construye en
                       `src/estado.anotar_local`, campo por campo.

POR QUÉ ES UNA PUERTA Y NO UNA CONVENCIÓN. Si alguien borrara las comprobaciones de este archivo,
el agente seguiría sin poder escribir: la credencial que haría falta no la tiene su identidad.
La regla la sostiene el permiso, no el código — que es la misma regla con la que este proyecto
sostiene que el agente no puede firmar como persona.

Se despliega desde la MISMA imagen que `servicio/main.py`, con `APP_MODULO=mediador`. Lo que
cambia entre los dos servicios no es el código: es con qué identidad corren.
"""
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "ai-transf-lab-0827")

# El mediador es el que ESCRIBE: si él mismo tuviera un mediador configurado, se llamaría en
# círculo. Se borra aquí, antes de importar el almacén, para que un despliegue con la variable
# heredada por descuido no monte un bucle en vez de fallar a la vista.
os.environ.pop("MEDIADOR_URL", None)

from flask import Flask, jsonify, request                          # noqa: E402

from identidad import quien_llama                                  # noqa: E402
from src import estado                                             # noqa: E402

app = Flask(__name__)

# Quién puede pedirle una escritura. Cloud Run ya exige `roles/run.invoker` para llegar hasta
# aquí; esto es la segunda capa, y la que se puede leer en el repositorio. Vacío = no se filtra
# por identidad, que es lo que hace falta para ensayar en la máquina del operador.
PERMITIDOS = [x.strip() for x in os.environ.get("IDENTIDADES_PERMITIDAS", "").split(",")
              if x.strip()]


def _autorizado():
    quien = quien_llama()
    if PERMITIDOS and quien not in PERMITIDOS:
        return None, (jsonify({"error": "identity not authorised to write the record",
                               "error_es": "identidad no autorizada para escribir el registro",
                               "caller": quien or "(no token)"}), 403)
    return quien, None


@app.post("/aplicar-cierre")
def aplicar_cierre():
    """Un cierre. Sin sobre válido para ESTA petición, no ocurre nada."""
    quien, negado = _autorizado()
    if negado:
        return negado

    cuerpo = request.get_json(silent=True) or {}
    pid = cuerpo.get("peticion_id")
    if not pid:
        return jsonify({"error": "peticion_id is required"}), 400

    aplicado, detalle = estado.aplicar_cierre_local(
        pid, cuerpo.get("sobre"), cuerpo.get("firma"), cuerpo.get("dictamen"))
    if not aplicado:
        # 403 y no 400: no es que la petición esté mal formada, es que no está autorizada. Y el
        # registro queda exactamente como estaba, que es la frase entera de este frente.
        return jsonify({"aplicado": False, "requested_by": quien, "record_unchanged": True,
                        **detalle}), 403
    return jsonify({"aplicado": True, "requested_by": quien, **detalle})


@app.post("/anotar")
def anotar():
    """El trámite. No puede escribir una firma ni aunque se la manden."""
    quien, negado = _autorizado()
    if negado:
        return negado

    cuerpo = request.get_json(silent=True) or {}
    pid = cuerpo.get("peticion_id")
    if not pid:
        return jsonify({"error": "peticion_id is required"}), 400

    datos = cuerpo.get("datos") or {}
    if not isinstance(datos, dict):
        return jsonify({"error": "datos must be an object"}), 400

    ok, detalle = estado.anotar_local(pid, cuerpo.get("operacion"), **datos)
    return jsonify({"ok": ok, "requested_by": quien, "detalle": detalle}), (200 if ok else 400)


@app.get("/")
def salud():
    return jsonify({
        "service": "mediador",
        "writes": "the ONLY identity with roles/datastore.user",
        "endpoints": ["/aplicar-cierre", "/anotar"],
        "rule": "without a valid envelope for THIS request, nothing happens",
        "closure_fields": list(estado.CAMPOS_DE_CIERRE)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
