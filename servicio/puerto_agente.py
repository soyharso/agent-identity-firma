#!/usr/bin/env python3
"""El candado aplicado al agente que HABLA CON CLIENTES, sin tocar su transporte.

QUÉ RESUELVE, y es un bloqueante que ese producto declaró por sí mismo antes de que existiera
este componente: un agente que conversa con clientes reales no puede comprometer a la empresa
—cotizar, descontar, prometer, escribir en el ERP— sin la firma de una persona. Hasta hoy eso
dependía de que el modelo se portara bien, que es justo lo que esta casa dejó de aceptar el 26
de agosto.

CÓMO ENCAJA. El canal de WhatsApp de la casa (`qnowa-wa-channel`) expone un puerto de agente:
un protocolo con un solo método, `responder(ctx) -> AgentReply`, que mantiene aislado el cerebro
del transporte. Esta clase implementa ESE MISMO puerto y envuelve a cualquier otro agente. Se
enchufa sin tocar una línea del gateway de mensajería, y sin ella el canal sigue funcionando
igual: es aditiva.

LA REGLA, y es la misma de todo el proyecto: la clave decide, no el código. El agente comercial
tiene alcance `["informada"]` en `claves/directorio.json`. Informar lo firma él. Cualquier cosa
que comprometa a la empresa queda FUERA DE SU ALCANCE, y el verificador la rechaza aunque el
modelo esté convencido de lo contrario, aunque lo hayan envenenado, y aunque alguien cambie el
código de esta clase — porque la clave que haría falta no la tiene el servicio.

LO QUE ESTO NO ES, dicho antes de que lo pregunte nadie: el canal de WhatsApp NO está corriendo
con esto. Aquí se demuestra que el puerto encaja y que el alcance por clave gobierna sus
respuestas, con el contrato copiado fiel del canal. Enchufarlo en producción es un despliegue de
ese otro repositorio y no se ha hecho.
"""
import sys
import pathlib
from dataclasses import dataclass, field

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.firma_kms import firmar, resumen                      # noqa: E402
from src.verificar_sobre import cargar_directorio, verificar   # noqa: E402

CLAVE_COMERCIAL = "clave-agente-qnowa"

# Las categorías con que el propio canal marca una respuesta que compromete. Vienen de su
# contrato (`gate_hint`), no las inventa este archivo: cotizar, dar precio, prometer algo, o
# escribir en el sistema de la empresa.
COMPROMETEN = {"quote", "price", "promise", "erp_write"}


# ── el contrato del canal, copiado fiel para que enchufar sea copiar y pegar ──────────────

@dataclass(slots=True)
class AgentContext:
    tenant_slug: str
    wa_id: str
    nombre_perfil: str | None
    tipo: str
    texto: str | None


@dataclass(slots=True)
class AgentReply:
    texto: str | None
    handoff: bool = False                      # escalar a una persona
    gate_hint: str | None = None               # 'quote'|'price'|'promise'|'erp_write'
    erp_intent: object | None = None           # escritura declarativa al ERP
    sobre: dict | None = field(default=None)   # AÑADIDO: la constancia firmada
    firma: str | None = field(default=None)


class CandadoDeFirma:
    """Envuelve a cualquier agente del canal y firma —o se niega a firmar— su respuesta."""

    def __init__(self, agente, directorio=None):
        self._agente = agente
        self._directorio = directorio if directorio is not None else cargar_directorio()

    async def responder(self, ctx: AgentContext) -> AgentReply:
        r = await self._agente.responder(ctx)

        compromete = bool(r.gate_hint in COMPROMETEN or r.erp_intent is not None)
        if compromete:
            # NO se intenta firmar y fallar: se para antes, y se dice por qué. El agente
            # comercial no tiene ninguna clave capaz de autorizar un compromiso, así que
            # intentarlo solo produciría un rechazo más abajo y una respuesta ya enviada.
            r.handoff = True
            r.texto = (
                "Con gusto te ayudo, y esto en concreto lo confirma una persona del equipo: "
                "voy a pasarle tu solicitud ahora mismo."
            )
            r.sobre, r.firma = None, None
            return r

        if not r.texto:
            return r                            # nada que decir, nada que firmar

        # Informar SÍ lo puede firmar el agente: queda constancia atribuible de qué dijo, a
        # quién y cuándo, y cualquiera puede comprobarla con la clave pública, sin credenciales.
        import time
        sobre = {"peticion_id": f"{ctx.tenant_slug}:{ctx.wa_id}",
                 "estado_destino": "informada",
                 "tipo_firmante": "MAQUINA",
                 "curado_por": "agente-comercial",
                 "hash_contenido": resumen(r.texto),
                 "marca_temporal": int(time.time()),
                 "algoritmo": "EC_SIGN_P256_SHA256"}
        res = firmar(CLAVE_COMERCIAL, sobre)
        if res["http"] != 200:
            # Si no se puede dejar constancia, no se habla. Ante la duda, prudencia — la misma
            # regla que el resto del sistema.
            r.handoff = True
            r.texto = "Te paso con una persona del equipo para atenderte."
            return r

        veredicto, _ = verificar(sobre, res["firma"], r.texto, self._directorio)
        if veredicto != "OK":
            r.handoff, r.texto = True, "Te paso con una persona del equipo para atenderte."
            return r

        r.sobre, r.firma = sobre, res["firma"]
        return r
