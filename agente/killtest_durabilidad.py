#!/usr/bin/env python3
"""KILL-TEST — ¿la pausa sobrevive a que el proceso muera?

Es la prueba que la fase cero exigió y que hasta hoy no existía. Cada paso corre en un PROCESO
DISTINTO a propósito: si algo dependiera de la memoria del anterior, aquí se rompe.

  paso 1  el flujo llega a la pausa y se detiene.          proceso muere.
  paso 2  la persona decide por su lado.                   proceso muere.
  paso 3  se vuelve a empezar de cero: NO debe pausarse,   proceso muere.
          debe firmar con la clave humana.
  paso 4  se vuelve a empezar otra vez: NO debe firmar de nuevo.

Uso: python3 agente/killtest_durabilidad.py <paso>
"""
import asyncio
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

PETICION = "PET-002"


async def _correr_sin_responder():
    from grafo import correr
    await correr(PETICION)


def paso1():
    from src import estado
    estado._doc(PETICION).delete()
    asyncio.run(_correr_sin_responder())
    e = estado.leer(PETICION)
    ok = e.get("espera_humana") is True
    print(f"  almacén: espera_humana={e.get('espera_humana')} firma={'sí' if e.get('firma') else 'no'}")
    return ok, "el flujo se detuvo y lo dejó anotado en el almacén"


def paso2():
    from src import estado
    estado.anotar_decision_humana(PETICION, "descartada")
    e = estado.leer(PETICION)
    ok = e.get("decision_humana") == "descartada" and e.get("espera_humana") is False
    print(f"  almacén: decision_humana={e.get('decision_humana')} espera_humana={e.get('espera_humana')}")
    return ok, "la decisión de la persona quedó guardada, sin proceso vivo de por medio"


def paso3():
    from src import estado
    asyncio.run(_correr_sin_responder())
    e = estado.leer(PETICION)
    ok = e.get("veredicto") == "OK" and bool(e.get("firma"))
    print(f"  almacén: veredicto={e.get('veredicto')} firma={'sí' if e.get('firma') else 'no'}")
    return ok, "arrancó de cero, NO se detuvo, y firmó con la clave de la persona"


def paso4():
    from src import estado
    antes = estado.leer(PETICION).get("firma")
    reservado = estado.reservar(PETICION, estado.leer(PETICION).get("hash_contenido"))
    despues = estado.leer(PETICION).get("firma")
    ok = (reservado is False) and (antes == despues)
    print(f"  reserva concedida={reservado} (debe ser False) · firma sin cambios={antes == despues}")
    return ok, "un segundo despertar no vuelve a firmar lo mismo"


PASOS = {"1": paso1, "2": paso2, "3": paso3, "4": paso4}

if __name__ == "__main__":
    n = sys.argv[1] if len(sys.argv) > 1 else "1"
    ok, que = PASOS[n]()
    print(f"\npaso {n}: {'PASA' if ok else 'NO PASA'} — {que}")
    sys.exit(0 if ok else 1)
