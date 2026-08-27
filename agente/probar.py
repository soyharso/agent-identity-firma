"""Prueba la puerta obligatoria: el marco de agentes de Google hablando con Gemini 3.7 Flash.

No firma nada. Solo comprueba que el dictamen sale, y con qué modelo salió.
"""
import asyncio
import sys

from google.adk.runners import InMemoryRunner
from google.genai import types

from agent import root_agent

CASOS = [
    ("PET-001", "Se cierra: el índice quedó creado y la consulta que tardaba 40 s ahora tarda "
                "0,3 s. Evidencia: salida del EXPLAIN antes y después, en el commit a1b2c3d."),
    ("PET-002", "Se cierra porque ya no parece importante."),
    ("PET-003", "Se descarta la queja del cliente: revisando el historial, el error fue suyo."),
]


async def dictaminar(runner, texto):
    sesion = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="prueba")
    partes = []
    async for ev in runner.run_async(
            user_id="prueba", session_id=sesion.id,
            new_message=types.Content(role="user", parts=[types.Part(text=texto)])):
        if ev.content and ev.content.parts:
            partes += [p.text for p in ev.content.parts if p.text]
    return "".join(partes).strip()


async def main():
    runner = InMemoryRunner(agent=root_agent, app_name="curador")
    print(f"marco: google-adk · modelo: {root_agent.model}\n")
    for pid, texto in CASOS:
        salida = await dictaminar(runner, texto)
        print(f"── {pid}\n   texto: {texto[:70]}…\n   {salida}\n")


if __name__ == "__main__":
    sys.path.insert(0, ".")
    asyncio.run(main())
