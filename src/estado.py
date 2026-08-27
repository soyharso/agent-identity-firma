"""La verdad duradera del dominio. NO la sesión del motor.

La fase cero encontró la contradicción: la pausa nativa del marco vive en la sesión, y sin sesión
persistida un despertar posterior no puede reanudarla —el contenedor se apaga sin avisar y la
siguiente llamada puede caer en otra instancia—. Aquí vive lo que sí tiene que sobrevivir.

También vive aquí la marca de idempotencia, y se escribe **antes** del trabajo caro: si se
escribiera al final, dos despertares a la vez gastarían el modelo dos veces aunque solo uno
lograra firmar.
"""
import os

from google.cloud import firestore

PROYECTO = os.environ.get("GOOGLE_CLOUD_PROJECT", "ai-transf-lab-0827")
COLECCION = "peticiones"
_cliente = None


def _c():
    global _cliente
    if _cliente is None:
        _cliente = firestore.Client(project=PROYECTO)
    return _cliente


def _doc(peticion_id):
    return _c().collection(COLECCION).document(peticion_id)


def leer(peticion_id) -> dict:
    d = _doc(peticion_id).get()
    return d.to_dict() or {} if d.exists else {}


def guardar(peticion_id, **campos):
    _doc(peticion_id).set(campos, merge=True)


def reservar(peticion_id, hash_contenido) -> bool:
    """Marca atómicamente que ESTE despertar se ocupa de este par petición+texto.

    Devuelve True si la reserva es nuestra, False si otro ya la tenía. La atomicidad la da la
    transacción: comprobar y escribir por separado deja la carrera que la fase cero señaló.
    """
    doc = _doc(peticion_id)
    tx = _c().transaction()

    @firestore.transactional
    def _intentar(t):
        actual = doc.get(transaction=t).to_dict() or {}
        if actual.get("reserva_hash") == hash_contenido:
            return False                      # ya reservado para este mismo texto
        if actual.get("firma") and actual.get("hash_contenido") == hash_contenido:
            return False                      # ya firmado: no se vuelve a firmar
        t.set(doc, {"reserva_hash": hash_contenido}, merge=True)
        return True

    return _intentar(tx)


def ya_firmado(peticion_id, hash_contenido) -> bool:
    e = leer(peticion_id)
    return bool(e.get("firma")) and e.get("hash_contenido") == hash_contenido


def anotar_decision_humana(peticion_id, decision):
    """La persona decide por su propia entrada. El siguiente despertar lo consume."""
    guardar(peticion_id, decision_humana=str(decision).strip().lower(), espera_humana=False)


def pendientes_de_persona() -> list:
    q = _c().collection(COLECCION).where(filter=firestore.FieldFilter("espera_humana", "==", True))
    return [d.id for d in q.stream()]
