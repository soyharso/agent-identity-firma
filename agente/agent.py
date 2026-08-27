"""El agente curador: dictamina si un cierre puede firmarlo una máquina o exige una persona.

Marco: Google Agent Development Kit. Modelo: Gemini 3.7 Flash por Vertex.

El dictamen NO es la firma. El agente puede proponer que un cierre es de máquina, pero si
dictamina que hace falta criterio humano, no tiene forma de firmarlo: la clave que sirve para eso
está fuera de su alcance, y el verificador rechaza cualquier sobre suyo que lo declare.
"""
import os

from google.adk.agents import Agent

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "ai-transf-lab-0827")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

MODELO = "gemini-3.7-flash"

INSTRUCCION = """Eres el curador de un libro de peticiones. Recibes el texto con el que alguien
cerró una petición y dictaminas UNA de estas tres cosas, y nada más:

- `cerrada`: el texto justifica el cierre con evidencia comprobable. Una máquina puede firmarlo.
- `abierta`: falta evidencia. No se cierra; se devuelve pidiendo lo que falta.
- `exige_humano`: el cierre implica un juicio —descartar, absolver, perdonar, decidir que algo no
  importa— o afecta a una persona. Una máquina NO puede firmar esto.

Ante la duda, `exige_humano`. Es más barato molestar a una persona que dejar que la máquina se
absuelva a sí misma.

Responde en dos líneas y nada más:
DICTAMEN: <cerrada|abierta|exige_humano>
PORQUE: <una frase, máximo 25 palabras>
"""

root_agent = Agent(
    name="curador",
    model=MODELO,
    description="Dictamina si el cierre de una petición lo puede firmar una máquina.",
    instruction=INSTRUCCION,
)
