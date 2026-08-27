"""El candado de firma, como grafo: un agente, seis funciones y una pausa.

Corregido con la fase cero ejecutada del 2026-08-27, que tumbó tres supuestos:

  1. Una ruta sin arista NO revienta: el flujo muere en silencio. Por eso cada bifurcación
     lleva DEFAULT_ROUTE.
  2. `rerun_on_resume` solo aplica al nodo que se interrumpió, no a los de aguas arriba. Por eso
     la relectura va DESPUÉS de la pausa, no antes: así se ejecuta sola en cada reanudación.
  3. Un esquema rígido sobre la salida del agente convierte una respuesta mala del modelo en una
     excepción que mata el flujo entero. Por eso `dictaminar` devuelve texto libre y `enrutar`
     lo parsea con tolerancia.
"""
import asyncio
import json
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "ai-transf-lab-0827")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

from google.adk.agents import Agent                                    # noqa: E402
from google.adk.apps import App, ResumabilityConfig                    # noqa: E402
from google.adk.events.request_input import RequestInput               # noqa: E402
from google.adk.runners import InMemoryRunner                          # noqa: E402
from google.adk.workflow import DEFAULT_ROUTE, START, FunctionNode, Workflow  # noqa: E402
from google.genai import types                                         # noqa: E402

from src.firma_kms import CLAVE_AGENTE, CLAVE_HUMANO, firmar, resumen  # noqa: E402

# 3.6-flash y no 3.7: las dos cumplen la regla del concurso (3.5 o superior), pero la ultima
# esta congestionada y devuelve 429. Medido hoy, y avisado en el propio taller de Google.
MODELO = os.environ.get("MODELO_GEMINI", "gemini-3.6-flash")
LIBRO = pathlib.Path(__file__).resolve().parent.parent / "libro"
PETICIONES = LIBRO / "peticiones.json"
FIRMAS = LIBRO / "firmas_grafo.jsonl"

ESTADOS_SOLO_HUMANO = {"exige_humano"}


# ── funciones: todo lo determinista ────────────────────────────────────────────────────

def _peticion(pid):
    return json.loads(PETICIONES.read_text())[pid]


def cargar_peticion(ctx):
    """Lee el texto y su estado actual. Deja en el estado lo que otros nodos necesitarán:
    la fase cero confirmó que el dato NO viaja más allá del vecino inmediato."""
    pid = ctx.state.get("peticion_id", "PET-001")
    p = _peticion(pid)
    ctx.state["peticion_id"] = pid
    ctx.state["texto"] = p["texto"]
    ctx.state["hash_al_dictaminar"] = resumen(p["texto"])
    return p["texto"]


def enrutar(ctx, node_input):
    """DETERMINISTA. Lee el dictamen como texto y decide. Nunca decide el modelo.

    Si el dictamen llega ilegible, la ruta es `exige_humano`: ante la duda, molesta a una
    persona. Es más barato que dejar que la máquina se absuelva."""
    crudo = str(node_input or "")
    dictamen = "ilegible"
    for linea in crudo.splitlines():
        if "DICTAMEN:" in linea.upper():
            valor = linea.split(":", 1)[1].strip().lower().split()[0]
            if valor in ("cerrada", "abierta", "exige_humano"):
                dictamen = valor
            break
    ctx.state["dictamen"] = dictamen
    ctx.route = {"cerrada": "modelo", "abierta": "abierta"}.get(dictamen, "exige_humano")
    return dictamen


def _sobre(ctx, curado_por, estado):
    return {"peticion_id": ctx.state["peticion_id"], "estado": estado,
            "curado_por": curado_por, "hash_contenido": ctx.state["hash_actual"]}


def _releer(ctx):
    """Relee la petición y recalcula el resumen. Es el anti-obsolescencia: no se firma un
    juicio sobre un texto que ya cambió."""
    p = _peticion(ctx.state["peticion_id"])
    ctx.state["hash_actual"] = resumen(p["texto"])
    return ctx.state["hash_actual"] == ctx.state["hash_al_dictaminar"]


def refrescar_y_firmar(ctx):
    """La máquina firma con SU clave. Antes, relee."""
    if not _releer(ctx):
        ctx.state["motivo"] = "el texto cambió después del dictamen"
        ctx.route = "rehacer"
        return "TEXTO_CAMBIADO"
    sobre = _sobre(ctx, "modelo", "cerrada")
    r = firmar(CLAVE_AGENTE, sobre)
    ctx.state["sobre"] = sobre
    ctx.state["resultado_firma"] = r
    ctx.route = DEFAULT_ROUTE
    return f"firmado por la máquina: http {r['http']}"


def pausa_humana(ctx):
    """El flujo se DETIENE aquí. No es un aviso: es un nodo que no continúa sin la persona."""
    respuesta = (ctx.resume_inputs or {}).get("firma_humana")
    if respuesta is None:
        return RequestInput(
            interrupt_id="firma_humana",
            message=(f"La petición {ctx.state['peticion_id']} exige criterio humano. "
                     f"Texto: {ctx.state['texto'][:120]}\n"
                     f"Responde 'descartada', 'cerrada' o 'no'."))
    # La respuesta llega como texto o como diccionario según cómo se reanude. Se aceptan las dos.
    if isinstance(respuesta, dict):
        respuesta = respuesta.get("result", respuesta)
    ctx.state["decision_humana"] = str(respuesta).strip().lower()
    return ctx.state["decision_humana"]


def firmar_humano(ctx):
    """Va DESPUÉS de la pausa a propósito: así se relee sola en cada reanudación, sin depender
    de una bandera que la fase cero demostró que no alcanza a los nodos de aguas arriba."""
    decision = ctx.state.get("decision_humana", "no")
    if decision not in ("descartada", "cerrada"):
        ctx.state["resultado_firma"] = {"http": 0, "error": "la persona no autorizó"}
        ctx.state["sobre"] = None
        return "sin firma: la persona no autorizó"
    _releer(ctx)
    sobre = _sobre(ctx, "humano", decision)
    r = firmar(CLAVE_HUMANO, sobre)
    ctx.state["sobre"] = sobre
    ctx.state["resultado_firma"] = r
    return f"firmado por la persona: http {r['http']}"


def ruta_imprevista(ctx, node_input):
    """El guardián de la ruta que nadie previó.

    La fase cero comprobó que una ruta sin arista NO revienta: el flujo muere en silencio y
    nunca llega al verificador. Este nodo existe para que eso sea imposible. Y como el motor
    prohíbe dos aristas iguales, el guardián no puede ser el mismo nodo que la pausa: tiene que
    ser suyo, y de paso deja rastro de la anomalía."""
    ctx.state["ruta_imprevista"] = str(node_input)[:80]
    return "ruta imprevista: se trata como si exigiera una persona"


def devolver(ctx):
    ctx.state["sobre"] = None
    ctx.state["resultado_firma"] = {"http": 0, "error": "sin evidencia, se devuelve abierta"}
    return "devuelta abierta"


def verificar(ctx):
    """La regla dura. Ninguna ruta llega al registro sin pasar por aquí."""
    sobre = ctx.state.get("sobre")
    r = ctx.state.get("resultado_firma") or {}
    if not sobre or r.get("http") != 200:
        v = "SIN_FIRMA"
    elif r["clave"] == CLAVE_AGENTE and sobre["curado_por"] != "modelo":
        v = "RECHAZADO_SUPLANTACION"
    elif sobre["estado"] in ("descartada",) and r["clave"] != CLAVE_HUMANO:
        v = "RECHAZADO_SUPLANTACION"
    else:
        v = "OK"
    ctx.state["veredicto"] = v
    return v


def registrar(ctx):
    fila = {"ts": int(time.time()), "peticion_id": ctx.state["peticion_id"],
            "dictamen": ctx.state.get("dictamen"), "veredicto": ctx.state["veredicto"],
            "sobre": ctx.state.get("sobre"),
            "firma": (ctx.state.get("resultado_firma") or {}).get("firma")}
    FIRMAS.parent.mkdir(parents=True, exist_ok=True)
    with FIRMAS.open("a") as fh:
        fh.write(json.dumps(fila, ensure_ascii=False) + "\n")
    return f"{ctx.state['peticion_id']} → {ctx.state['veredicto']}"


# ── el único agente del flujo ──────────────────────────────────────────────────────────

dictaminar = Agent(
    name="dictaminar",
    model=MODELO,
    description="Dictamina si el cierre de una petición lo puede firmar una máquina.",
    instruction=(
        "Recibes el texto con el que alguien cerró una petición. Dictamina UNA cosa:\n"
        "- `cerrada`: el texto justifica el cierre con evidencia comprobable.\n"
        "- `abierta`: falta evidencia.\n"
        "- `exige_humano`: implica un juicio (descartar, absolver, perdonar) o afecta a una "
        "persona.\n"
        "Ante la duda, `exige_humano`.\n"
        "Responde exactamente dos líneas:\nDICTAMEN: <valor>\nPORQUE: <una frase>"),
)


# ── el grafo ───────────────────────────────────────────────────────────────────────────

n_cargar = FunctionNode(func=cargar_peticion, name="cargar_peticion")
n_enrutar = FunctionNode(func=enrutar, name="enrutar")
n_firmar_maquina = FunctionNode(func=refrescar_y_firmar, name="refrescar_y_firmar")
n_pausa = FunctionNode(func=pausa_humana, name="pausa_humana", rerun_on_resume=True)
n_firmar_persona = FunctionNode(func=firmar_humano, name="firmar_humano")
n_imprevisto = FunctionNode(func=ruta_imprevista, name="ruta_imprevista")
n_devolver = FunctionNode(func=devolver, name="devolver")
n_verificar = FunctionNode(func=verificar, name="verificar")
n_registrar = FunctionNode(func=registrar, name="registrar")

grafo = Workflow(
    name="candado_de_firma",
    edges=[
        (START, n_cargar, dictaminar, n_enrutar),
        # DEFAULT_ROUTE es obligatorio: sin él una ruta imprevista mata el flujo EN SILENCIO.
        (n_enrutar, {"modelo": n_firmar_maquina,
                     "exige_humano": n_pausa,
                     "abierta": n_devolver,
                     DEFAULT_ROUTE: n_imprevisto}),
        # ciclo: si el texto cambió entre el dictamen y la firma, se vuelve a dictaminar.
        (n_firmar_maquina, {"rehacer": dictaminar, DEFAULT_ROUTE: n_verificar}),
        (n_imprevisto, n_pausa),
        (n_pausa, n_firmar_persona, n_verificar),
        (n_devolver, n_verificar),
        (n_verificar, n_registrar),
    ],
)

app = App(name="candado", root_agent=grafo,
          resumability_config=ResumabilityConfig(is_resumable=True))


async def correr(peticion_id, respuesta_humana=None):
    runner = InMemoryRunner(app=app)
    sesion = await runner.session_service.create_session(
        app_name="candado", user_id="operador", state={"peticion_id": peticion_id})
    print(f"\n═══ {peticion_id} ═══")
    pausado = False
    async for ev in runner.run_async(
            user_id="operador", session_id=sesion.id,
            new_message=types.Content(role="user", parts=[types.Part(text=peticion_id)])):
        for p in (ev.content.parts if ev.content else []):
            if p.text:
                print(f"  · {p.text.strip()[:150]}")
            if getattr(p, "function_call", None) and p.function_call.name == "adk_request_input":
                pausado = True
                print("  ⏸  EL FLUJO SE DETUVO — espera a una persona")

    if pausado and respuesta_humana is not None:
        from google.adk.workflow.utils._workflow_hitl_utils import create_request_input_response
        parte = create_request_input_response("firma_humana", {"result": respuesta_humana})
        print(f"  ▶  la persona responde: {respuesta_humana}")
        async for ev in runner.run_async(
                user_id="operador", session_id=sesion.id,
                new_message=types.Content(role="user", parts=[parte])):
            for p in (ev.content.parts if ev.content else []):
                if p.text:
                    print(f"  · {p.text.strip()[:150]}")


async def main():
    await correr("PET-001")                          # evidencia dura → la máquina firma
    await correr("PET-002", respuesta_humana="descartada")   # juicio → pausa y firma humana
    await correr("PET-003")                          # sin evidencia → se devuelve abierta


if __name__ == "__main__":
    asyncio.run(main())
