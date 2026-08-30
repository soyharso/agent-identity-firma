"""La verdad duradera del dominio. NO la sesión del motor.

La fase cero encontró la contradicción: la pausa nativa del marco vive en la sesión, y sin sesión
persistida un despertar posterior no puede reanudarla —el contenedor se apaga sin avisar y la
siguiente llamada puede caer en otra instancia—. Aquí vive lo que sí tiene que sobrevivir.

También vive aquí la marca de idempotencia, y se escribe **antes** del trabajo caro: si se
escribiera al final, dos despertares a la vez gastarían el modelo dos veces aunque solo uno
lograra firmar.

LA PUERTA (2026-08-30). Hasta hoy el sobre firmado era un RECIBO: se producía, se guardaba y
probaba después quién cerró qué, pero nada rechazaba un cierre que llegara sin él. Ahora hay un
solo camino hacia los campos que llevan credencial —`sobre`, `firma`, `hash_contenido`— y ese
camino es `aplicar_cierre`, que verifica primero y escribe después. Todo lo demás —reservas,
banderas de espera, el veredicto de una pasada que NO firmó nada— entra por `anotar`, que tiene
prohibido tocar esos tres campos.

Y la puerta no la sostiene este archivo, que cualquiera puede editar: la sostiene el permiso.
En la nube, `MEDIADOR_URL` manda las escrituras a otro servicio, que corre con OTRA identidad
—la única con `roles/datastore.user`—. Si alguien borrara estas comprobaciones, el agente
seguiría sin poder escribir, porque la credencial que haría falta no la tiene.
"""
import os

from google.cloud import firestore

PROYECTO = os.environ.get("GOOGLE_CLOUD_PROJECT", "ai-transf-lab-0827")

# La colección es la de siempre salvo que se pida otra. La variable existe porque el 2026-08-30
# se midió esto: tres frentes de la misma flota corrían `killtest_durabilidad.py` sobre el MISMO
# documento `PET-002` de la MISMA base a la vez, y el temporizador de la nube lo reescribía cada
# quince minutos por su cuenta. El paso 5 salía rojo sin que nadie hubiera roto nada. El valor
# por defecto NO cambia: la demostración y el servicio siguen escribiendo donde escribían.
COLECCION = os.environ.get("COLECCION_PETICIONES", "peticiones")
_cliente = None

# A dónde van las escrituras cuando este proceso NO es el que tiene la credencial. Vacío = este
# proceso escribe él mismo (es el mediador, o es una prueba corriendo con la credencial del
# operador). Con valor = este proceso pide, no escribe.
MEDIADOR = os.environ.get("MEDIADOR_URL", "").rstrip("/")

# Los campos que llevan credencial. Solo `aplicar_cierre` los escribe, y solo tras verificar.
# `anotar` los rechaza aunque se los pidan: es lo que hace que una operación de trámite no
# pueda colar una firma por la puerta de atrás.
CAMPOS_DE_CIERRE = ("sobre", "firma", "hash_contenido", "cierre_aplicado")


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
    """Escritura cruda. NO la use el agente: no pasa por la puerta.

    Queda para el propio mediador, para las semillas de la demostración y para las pruebas que
    corren con la credencial del operador. Si hay mediador configurado, este proceso no es quien
    escribe, y llamar aquí es un error de programación que vale más ver que tragarse.
    """
    if MEDIADOR:
        raise RuntimeError(
            "guardar() directo con MEDIADOR_URL puesto: este proceso no escribe el registro. "
            "Usa aplicar_cierre() para un cierre o anotar() para un trámite.")
    _doc(peticion_id).set(campos, merge=True)


# ── el camino hacia el mediador ────────────────────────────────────────────────────────

def _identidad_para(destino: str) -> str:
    """Un token de identidad para el mediador. En la nube lo da el servidor de metadatos; en la
    máquina del operador lo da `gcloud`. Las dos formas producen lo mismo: un OIDC cuyo público
    es el mediador, que es lo que Cloud Run comprueba antes de dejar entrar la petición."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2 import id_token
        return id_token.fetch_id_token(Request(), destino)
    except Exception:                                             # noqa: BLE001
        import subprocess
        return subprocess.run(["gcloud", "auth", "print-identity-token"],
                              capture_output=True, text=True, check=True).stdout.strip()


def _pedir(ruta: str, cuerpo: dict) -> tuple[int, dict]:
    import requests
    r = requests.post(f"{MEDIADOR}{ruta}", json=cuerpo, timeout=60,
                      headers={"Authorization": f"Bearer {_identidad_para(MEDIADOR)}"})
    try:
        return r.status_code, r.json()
    except Exception:                                             # noqa: BLE001
        return r.status_code, {"texto": r.text[:300]}


# ── LA PUERTA: el único camino hacia los campos que llevan credencial ──────────────────

def _huella(firma: str) -> str:
    import hashlib
    return "sha256:" + hashlib.sha256(str(firma).encode()).hexdigest()


def reservar_cierre(peticion_id, huella) -> bool:
    """La reserva de un solo uso DE LA PUERTA, con el mismo patrón transaccional que `reservar`.

    POR QUÉ NO ES `reservar` A SECAS, que es lo que pedía el encargo: `reserva_hash` ya la tiene
    puesta el despertar antes de llamar al modelo (`grafo.correr_para_servicio`), así que
    pedírsela otra vez aquí devolvería False en el PRIMER cierre legítimo. Medido, no supuesto:
    la comprobación está en `agente/killtest_puerta.py`. Es el mismo mecanismo, no un contador
    nuevo, y la marca es la huella de la FIRMA: dos sobres distintos no comparten huella.
    """
    doc = _doc(peticion_id)
    tx = _c().transaction()

    @firestore.transactional
    def _intentar(t):
        actual = doc.get(transaction=t).to_dict() or {}
        if actual.get("cierre_aplicado") == huella:
            return False                      # este mismo sobre ya se aplicó
        t.set(doc, {"cierre_aplicado": huella}, merge=True)
        return True

    return _intentar(tx)


def aplicar_cierre_local(peticion_id, sobre, firma, dictamen=None) -> tuple[bool, dict]:
    """Verificar y SOLO ENTONCES escribir. Es el simétrico de lo que `/decidir` hacía para el
    lado humano, aplicado también al lado máquina y con la comprobación que allí faltaba.

    `peticion_esperada` la pone quien verifica —aquí, el mediador—, nunca el sobre. Sin eso, una
    aprobación auténtica del caso de al lado pasaba entera: firma buena, firmante conocido, hash
    coherente consigo mismo y estado en alcance. Lo único que la delata es que no era PARA ESTE
    CASO, y esa comprobación no se estaba haciendo en el camino de escritura.
    """
    from src.verificar_sobre import verificar

    if not isinstance(sobre, dict) or not firma:
        return False, {"rechazo": "SIN_SOBRE",
                       "por_que": "un cierre sin sobre firmado no cambia el registro"}

    veredicto, detalle = verificar(sobre, firma, peticion_esperada=peticion_id)
    if veredicto != "OK":
        return False, {"rechazo": veredicto, "detalle": detalle,
                       "por_que": "el sobre no verifica contra esta petición"}

    huella = _huella(firma)
    primera_vez = reservar_cierre(peticion_id, huella)

    campos = {"veredicto": "OK", "espera_humana": False}
    if dictamen is not None:
        campos["dictamen"] = dictamen
    if primera_vez:
        # Los campos con credencial se escriben UNA vez, en la primera presentación del sobre.
        campos.update({"sobre": sobre, "firma": firma,
                       "hash_contenido": sobre.get("hash_contenido")})
    _doc(peticion_id).set(campos, merge=True)

    return True, {"aplicado": True, "sobre_escrito": primera_vez,
                  "firmante": detalle.get("firmante"),
                  "estado": sobre.get("estado_destino"),
                  "nota": None if primera_vez else
                  "el mismo sobre ya estaba aplicado: no se reescribió la firma"}


def aplicar_cierre(peticion_id, sobre, firma, dictamen=None) -> tuple[bool, dict]:
    """La misma puerta, esté quien esté al otro lado: aquí mismo, o el mediador por la red."""
    if not MEDIADOR:
        return aplicar_cierre_local(peticion_id, sobre, firma, dictamen)
    codigo, cuerpo = _pedir("/aplicar-cierre", {"peticion_id": peticion_id, "sobre": sobre,
                                                "firma": firma, "dictamen": dictamen})
    return (codigo == 200 and cuerpo.get("aplicado") is True), cuerpo


# ── TRÁMITE: todo lo que NO es un cierre, y que por eso no puede escribir una firma ────

_OPERACIONES = ("reservar", "apartar", "decision", "resultado", "soltar")


def anotar_local(peticion_id, operacion, **datos) -> tuple[bool, dict]:
    """Las escrituras de trámite. Ninguna puede tocar `CAMPOS_DE_CIERRE`, y eso no depende de
    quien llame: se construye aquí el diccionario entero, campo por campo."""
    if operacion not in _OPERACIONES:
        return False, {"rechazo": "OPERACION_DESCONOCIDA", "operacion": str(operacion)[:40]}

    if operacion == "reservar":
        return True, {"concedida": reservar(peticion_id, datos.get("hash_contenido"))}

    if operacion == "apartar":
        # Espera a una persona. La reserva se suelta EN LA MISMA escritura: si se dejara puesta,
        # el siguiente despertar se saltaría la petición para siempre.
        campos = {"espera_humana": True,
                  "texto": datos.get("texto"),
                  "hash_al_dictaminar": datos.get("hash_al_dictaminar"),
                  "reserva_hash": firestore.DELETE_FIELD}
    elif operacion == "decision":
        campos = {"decision_humana": str(datos.get("decision", "")).strip().lower(),
                  "espera_humana": False,
                  "reserva_hash": firestore.DELETE_FIELD}
    elif operacion == "resultado":
        # La pasada terminó SIN firmar nada: devuelta abierta, sin cofirma, sin firma humana.
        # Se anota el desenlace, y ni una letra de credencial.
        campos = {"veredicto": datos.get("veredicto"),
                  "dictamen": datos.get("dictamen"),
                  "espera_humana": False}
    else:                                                          # soltar
        campos = {"reserva_hash": firestore.DELETE_FIELD}

    fugados = [c for c in campos if c in CAMPOS_DE_CIERRE]
    if fugados:                                                    # cinturón: no debería ocurrir
        return False, {"rechazo": "CAMPO_DE_CIERRE_EN_TRAMITE", "campos": fugados}

    _doc(peticion_id).set(campos, merge=True)
    return True, {"anotado": operacion}


def anotar(peticion_id, operacion, **datos) -> tuple[bool, dict]:
    if not MEDIADOR:
        return anotar_local(peticion_id, operacion, **datos)
    codigo, cuerpo = _pedir("/anotar", {"peticion_id": peticion_id, "operacion": operacion,
                                        "datos": datos})
    return (codigo == 200 and cuerpo.get("ok") is True), cuerpo.get("detalle", cuerpo)


def reservar(peticion_id, hash_contenido) -> bool:
    """Marca atómicamente que ESTE despertar se ocupa de este par petición+texto.

    Devuelve True si la reserva es nuestra, False si otro ya la tenía. La atomicidad la da la
    transacción: comprobar y escribir por separado deja la carrera que la fase cero señaló.
    """
    if MEDIADOR:
        _, det = anotar(peticion_id, "reservar", hash_contenido=hash_contenido)
        return bool(det.get("concedida"))

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


def soltar_reserva(peticion_id):
    """La reserva dice «alguien se está ocupando», no «ya está hecho».

    Si el flujo termina esperando a una persona, el trabajo NO está hecho: dejar la reserva
    puesta bloquea su propia continuación, y el siguiente despertar se salta la petición para
    siempre. Lo descubrí corriendo el ciclo entero, no leyéndolo.
    """
    anotar(peticion_id, "soltar")


def apartar_para_persona(peticion_id, texto, hash_al_dictaminar):
    """La petición queda esperando a una persona, y la reserva se suelta en el mismo acto."""
    anotar(peticion_id, "apartar", texto=texto, hash_al_dictaminar=hash_al_dictaminar)


def anotar_resultado(peticion_id, veredicto, dictamen=None):
    """La pasada terminó sin firmar nada. Se anota el desenlace; la firma no se toca."""
    anotar(peticion_id, "resultado", veredicto=veredicto, dictamen=dictamen)


def anotar_decision_humana(peticion_id, decision):
    """La persona decide por su propia entrada. El siguiente despertar lo consume."""
    anotar(peticion_id, "decision", decision=decision)


def pendientes_de_persona() -> list:
    q = _c().collection(COLECCION).where(filter=firestore.FieldFilter("espera_humana", "==", True))
    return [d.id for d in q.stream()]
