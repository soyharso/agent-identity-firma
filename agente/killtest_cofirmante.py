#!/usr/bin/env python3
"""KILL-TEST — ¿se puede cerrar un caso SIN el cofirmante?

Esta prueba existe para fallar si el cofirmante es un adorno. Un segundo modelo que se puede
saltar, o que al caerse deja pasar el cierre, no protege nada: solo engorda el reclamo. Así que
la prueba no comprueba que el modelo responda —eso es lo fácil—, comprueba las cuatro maneras de
saltárselo:

  1. **Que no coincida y aun así se firme.** Con el cofirmante devolviendo `DENY`, la máquina no
     puede llegar a la clave. Se sustituye `firmar` por una función que revienta: si la ruta de
     firma la llama, la prueba muere. Ese es el punto exacto donde un refactor futuro rompería
     la promesa sin que nadie se entere.
  2. **Que se caiga y el silencio valga por un sí.** Con el canal apuntando a un sitio muerto y
     el tiempo límite en milisegundos, el resultado tiene que ser `DENY` con `no_response`.
  3. **Que la negativa muera en silencio.** La lección más cara de este repositorio: una ruta sin
     arista NO revienta, el flujo se apaga sin llegar al verificador. Así que se comprueba que la
     ruta `cofirma_denegada` existe en el grafo Y que lleva a la pausa humana.
  4. **Que el rastro no nombre al modelo.** El responsable del concurso pidió VER la integración,
     no creerla: sin la línea con el identificador del modelo no hay nada que enseñar.

Y una quinta, que no es de ruptura sino de honestidad: se llama al modelo DE VERDAD, dos veces,
en las dos direcciones. Si `google/gemma-3-27b-it` no está disponible, esta prueba se pone roja
y el reclamo del DEVPOST deja de ser cierto. Es a propósito: preferimos enterarnos aquí.

Uso: python3 agente/killtest_cofirmante.py
"""
import importlib
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

fallos = []


def comprobar(ok, titulo, detalle=""):
    print(f"  {'✓' if ok else '✗'} {titulo}" + (f"  {detalle}" if detalle else ""))
    if not ok:
        fallos.append(titulo)


class Ctx:
    """Lo mínimo que el nodo de firma toca: un estado y una ruta."""

    def __init__(self, **estado):
        self.state = dict(estado)
        self.route = None


# ── 1 · el modelo, de verdad, en las dos direcciones ───────────────────────────────────
print("\n1 · EL COFIRMANTE RESPONDE, Y DISTINGUE (llamada real)")
from src import cofirmante  # noqa: E402

permitido_juicio, det_juicio = cofirmante.cofirmar(
    "KT-JUICIO", "the customer complaint is dismissed and no refund is due",
    has_human_key=False)
comprobar(permitido_juicio is False, "un juicio sin llave humana se DENIEGA",
          cofirmante.linea_de_registro(det_juicio))

permitido_cierre, det_cierre = cofirmante.cofirmar(
    "KT-CIERRE",
    "close the case: commit 4f3a2b1 attached with the fix deployed and the test suite green",
    has_human_key=False)
comprobar(permitido_cierre is True, "un cierre con evidencia comprobable se PERMITE",
          cofirmante.linea_de_registro(det_cierre))
comprobar(det_juicio.get("segundos", 99) <= cofirmante.TIEMPO_LIMITE,
          f"responde dentro del límite de {cofirmante.TIEMPO_LIMITE:g} s",
          f"{det_juicio.get('segundos')} s")

# ── 4 · el rastro nombra al modelo ─────────────────────────────────────────────────────
print("\n2 · EL RASTRO NOMBRA AL MODELO")
linea = cofirmante.linea_de_registro(det_juicio)
comprobar(cofirmante.MODELO in linea and "allow=" in linea and "reason=" in linea,
          "la línea de registro trae modelo, veredicto y motivo", linea)
comprobar("missing_human_key" == det_juicio.get("reason"),
          "el motivo de la negativa es el que se reclama", det_juicio.get("reason"))

# ── 2 · el fallo cerrado ───────────────────────────────────────────────────────────────
print("\n3 · SI NO RESPONDE, NO SE CIERRA (fallo cerrado)")
os.environ["COFIRMANTE_ENDPOINT"] = "https://127.0.0.1:9/no-existe"
os.environ["COFIRMANTE_TIMEOUT"] = "0.05"
importlib.reload(cofirmante)
permitido_caido, det_caido = cofirmante.cofirmar("KT-CAIDO", "anything at all", False)
comprobar(permitido_caido is False, "el canal caído devuelve DENY, no un permiso",
          det_caido.get("reason"))
comprobar(det_caido.get("reason") == "no_response",
          "y lo dice por su nombre, con el error del canal",
          str(det_caido.get("error"))[:60])
del os.environ["COFIRMANTE_ENDPOINT"], os.environ["COFIRMANTE_TIMEOUT"]
importlib.reload(cofirmante)

# ── 3 · no se puede firmar sin cofirma, y la negativa no muere en silencio ─────────────
print("\n4 · SIN COFIRMA NO SE LLEGA A LA CLAVE")
from agente import grafo  # noqa: E402


def _firmar_prohibido(*a, **k):
    raise AssertionError("SE LLAMÓ A LA CLAVE SIN COFIRMA — la promesa está rota")


grafo.firmar = _firmar_prohibido
grafo._releer = lambda ctx: ctx.state.__setitem__("hash_actual", "sha256:x") or True
grafo.cofirmar = lambda cid, accion, has_human_key: (
    False, {"modelo": cofirmante.MODELO, "allow": False, "reason": "missing_human_key"})

ctx = Ctx(peticion_id="KT-001", texto="the complaint is dismissed",
          hash_al_dictaminar="sha256:x")
salida = grafo.refrescar_y_firmar(ctx)
comprobar(ctx.state.get("sobre") is None, "no se construyó ningún sobre firmado")
comprobar(ctx.route == "cofirma_denegada", "la ruta sale por la negativa", str(ctx.route))
comprobar("SIN COFIRMA" in salida, "y lo dice en voz alta", salida[:60])

# La arista se comprueba sobre la declaración del grafo, que es lo que el motor lee: si alguien
# borra el destino, la negativa se queda sin salida y el flujo muere en silencio (lección 1).
fuente_grafo = pathlib.Path(grafo.__file__).read_text(encoding="utf-8")
comprobar('"cofirma_denegada": n_pausa' in fuente_grafo,
          "la ruta de la negativa lleva a la PAUSA HUMANA, no al vacío")

# ── veredicto ──────────────────────────────────────────────────────────────────────────
print()
if fallos:
    print(f"✗ KILL-TEST ROJO — {len(fallos)} fallo(s): " + "; ".join(fallos))
    sys.exit(1)
print("✓ KILL-TEST VERDE — el cofirmante no se puede saltar, y su silencio no abre nada")
