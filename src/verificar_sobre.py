#!/usr/bin/env python3
"""El verificador, con una sola compuerta: ¿está este estado en el alcance de la clave que firmó?

Función pura. No usa red, ni credenciales, ni servicios. Lee el directorio de claves y los PEM
que viajan en el repositorio, y con eso decide. Cualquiera puede correrlo y llegar al mismo
veredicto.

DE DÓNDE SALE ESTE ARCHIVO. Una propuesta externa planteó el «sobre canónico con segregación de
claves». Más de la mitad ya estaba construido. Lo que sí aportó, y es mucho, es el **directorio
con alcance por clave**. Pero su propio verificador NO lo usaba: comprobaba a mano un único
estado, y eso deja pasar cualquier otro estado de juicio. Se ejecutó su lógica y se vio.

Aquí el alcance es la única compuerta. No hay reglas por estado, ni listas de casos especiales
que envejecen: si el estado no está en el alcance de la clave, se rechaza.
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

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CLAVES = RAIZ / "claves"

# Lo que un sobre debe traer. `tipo_firmante` es OPCIONAL y, si viene, solo sirve para cazar
# incoherencias: NUNCA para conceder. La clase la decide qué clave validó, y punto.
CAMPOS = ("peticion_id", "estado_destino", "hash_contenido", "marca_temporal", "algoritmo")


# La raíz del repositorio entra en la ruta de módulos ANTES de importar `src.*`. Sin esto, el
# primer comando que el README le pide teclear a un jurado —`python3 src/verificar_sobre.py …`
# desde la raíz— moría con ModuleNotFoundError: Python pone en la ruta el directorio del script
# (`src/`), no la raíz, así que el paquete `src` no era visible desde dentro de sí mismo. El
# verificador sigue siendo puro: esto no añade ninguna dependencia, solo lo hace ejecutable
# tal como está escrito en el README.
sys.path.insert(0, str(RAIZ))

from src.canonico import canonico  # noqa: E402


def cargar_directorio(dir_claves=CLAVES) -> dict:
    d = json.loads((pathlib.Path(dir_claves) / "directorio.json").read_text())
    for nombre, e in d["claves"].items():
        e["_publica"] = load_pem_public_key(
            (pathlib.Path(dir_claves) / e["archivo_publico"]).read_bytes())
    return d["claves"]


def quien_firmo(directorio, mensaje: bytes, firma: bytes):
    """Prueba la firma contra cada clave del directorio. La que valide dice quién firmó."""
    digest = hashlib.sha256(mensaje).digest()
    for nombre, e in directorio.items():
        try:
            e["_publica"].verify(firma, digest, ec.ECDSA(Prehashed(hashes.SHA256())))
            return nombre, e
        except InvalidSignature:
            continue
    return None, None


def verificar(sobre: dict, firma_b64: str, texto_actual: str | None = None,
              directorio=None, peticion_esperada: str | None = None) -> tuple[str, dict]:
    directorio = directorio if directorio is not None else cargar_directorio()

    faltan = [c for c in CAMPOS if c not in sobre]
    if faltan:
        return "SOBRE_INCOMPLETO", {"faltan": faltan}

    try:
        firma = base64.b64decode(firma_b64)
    except Exception:                                            # noqa: BLE001
        return "FIRMA_ILEGIBLE", {}

    nombre, entrada = quien_firmo(directorio, canonico(sobre), firma)
    if nombre is None:
        return "FIRMANTE_DESCONOCIDO", {"por_que": "ninguna clave del directorio valida esta firma"}

    # Anti-reutilización: una firma auténtica, presentada en el caso de al lado, sigue siendo
    # una falsificación. Es el ataque más plausible de los tres, porque no exige romper nada:
    # basta con copiar una aprobación que ya existe. Sin esta comprobación, quien reutiliza un
    # sobre válido junto a su propio texto pasa las demás: la firma es buena, el firmante está
    # en el directorio, el contenido cuadra con el hash que él mismo copió, y el estado está en
    # alcance. Lo único que delata el fraude es que la aprobación no era PARA ESE CASO.
    #
    # `peticion_esperada` la pone quien verifica, nunca el sobre: si se leyera del propio sobre
    # la comprobación sería un espejo y no comprobaría nada.
    if peticion_esperada is not None and sobre["peticion_id"] != peticion_esperada:
        return "CONTEXTO_AJENO", {
            "firmante": nombre,
            "firmado_para": sobre["peticion_id"],
            "presentado_en": peticion_esperada,
            "por_que": "la firma es válida, pero aprobaba otro caso"}

    # Anti-obsolescencia: no se acepta un juicio sobre un texto que ya cambió.
    if texto_actual is not None:
        esperado = "sha256:" + hashlib.sha256(texto_actual.encode()).hexdigest()
        if sobre["hash_contenido"] not in (esperado, esperado.removeprefix("sha256:")):
            return "CONTENIDO_ALTERADO", {"firmante": nombre}

    # La incoherencia se caza, pero el tipo NUNCA se toma del sobre.
    if "tipo_firmante" in sobre and sobre["tipo_firmante"] != entrada["tipo"]:
        return "RECHAZADO_SUPLANTACION", {
            "firmante": nombre, "declaraba": sobre["tipo_firmante"], "es": entrada["tipo"],
            "por_que": "el sobre declara un tipo que no es el de la clave que lo firmó"}

    # LA ÚNICA COMPUERTA.
    if sobre["estado_destino"] not in entrada["alcance_permitido"]:
        return "FUERA_DE_ALCANCE", {
            "firmante": nombre, "tipo": entrada["tipo"], "estado": sobre["estado_destino"],
            "alcance": entrada["alcance_permitido"],
            "por_que": "esa clave no puede autorizar ese estado"}

    if sobre["algoritmo"] != entrada["algoritmo"]:
        return "ALGORITMO_INESPERADO", {"firmante": nombre, "dice": sobre["algoritmo"]}

    return "OK", {"firmante": nombre, "tipo": entrada["tipo"],
                  "estado": sobre["estado_destino"], "cuando": sobre["marca_temporal"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("libro", help="jsonl con {sobre, firma} por línea")
    ap.add_argument("--texto-archivo", default=None)
    ap.add_argument("--claves", default=str(CLAVES))
    args = ap.parse_args()

    texto = pathlib.Path(args.texto_archivo).read_text() if args.texto_archivo else None
    directorio = cargar_directorio(args.claves)

    malos = 0
    sin_firmar = 0
    for n, linea in enumerate(pathlib.Path(args.libro).read_text().splitlines(), 1):
        if not linea.strip():
            continue
        fila = json.loads(linea)
        # El libro registra TODAS las pasadas, también aquellas en las que no se firmó nada:
        # la que se devolvió abierta por falta de evidencia, y la que se detuvo esperando a una
        # persona. Esas filas no traen sobre ni firma, y eso NO es un defecto: es el sistema
        # negándose a firmar, que es justo lo que promete. Antes reventaban el verificador con
        # un TypeError —el primer comando que teclea un jurado—, así que ahora se declaran.
        if not fila.get("sobre") or not fila.get("firma"):
            sin_firmar += 1
            print(f"{n:>3} {fila.get('peticion_id', '?'):<10} {'SIN_FIRMA':<22} "
                  f"{{\"nota\": \"nada que verificar: no se firmó\"}}")
            continue
        v, det = verificar(fila["sobre"], fila["firma"], texto, directorio)
        if v != "OK":
            malos += 1
        print(f"{n:>3} {fila['sobre'].get('peticion_id','?'):<10} {v:<22} "
              f"{json.dumps(det, ensure_ascii=False)}")
    print(f"\nfirmas inválidas: {malos} · filas sin firma (no se firmó, y está bien): "
          f"{sin_firmar}")
    sys.exit(1 if malos else 0)


if __name__ == "__main__":
    main()
