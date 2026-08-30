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
RAIZ = pathlib.Path(__file__).resolve().parent.parent


def _peticion_texto():
    import json
    return json.loads((RAIZ / "libro" / "peticiones.json").read_text())[PETICION]["texto"]


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
    """La persona decide Y FIRMA, que son la misma cosa en esta arquitectura.

    ESTE PASO ESTABA MAL Y HACÍA FALLAR AL PASO 3. Llamaba a `anotar_decision_humana`, que
    guarda la decisión pero NO produce firma. Y sin firma de la persona el paso 3 no puede
    dar OK, porque el servicio corre con la identidad del agente y tiene prohibido fabricar
    una firma humana —que es justo la promesa del proyecto—. O sea: el producto se comportaba
    bien y la prueba simulaba media persona. Ahora simula la persona entera, igual que
    `src/decidir_como_persona.py`: firma con la clave humana desde la máquina de quien decide,
    y solo se guarda si el verificador puro la valida.

    ADAPTADO 2026-08-30 (puerta mediadora). Antes escribía el registro él mismo con
    `estado.guardar`, que es exactamente el camino que este frente cerró: el paso simulaba a la
    persona pero se saltaba la comprobación que ahora hace la entrada `/decidir`. Ya no hay dos
    formas de escribir un cierre — hay una, `estado.aplicar_cierre`, y esta prueba pasa por
    ella. La verificación no desaparece: se hace DENTRO de la puerta, con `peticion_esperada`,
    que es más de lo que este paso comprobaba antes.
    """
    import time

    from src import estado
    from src.firma_kms import CLAVE_HUMANO, firmar, resumen

    texto = _peticion_texto()
    sobre = {"peticion_id": PETICION, "estado_destino": "descartada",
             "tipo_firmante": "HUMANO", "curado_por": "humano",
             "hash_contenido": resumen(texto), "marca_temporal": int(time.time()),
             "algoritmo": "EC_SIGN_P256_SHA256"}
    r = firmar(CLAVE_HUMANO, sobre)
    if r["http"] != 200:
        print(f"  la persona no pudo firmar: {r}")
        return False, "la persona no pudo firmar con su propia clave"

    aplicado, detalle = estado.aplicar_cierre(PETICION, sobre, r["firma"])
    if not aplicado:
        print(f"  la puerta rechazó la firma de la persona: {detalle}")
        return False, "la firma de la persona no pasó la puerta"

    estado.anotar_decision_humana(PETICION, "descartada")
    e = estado.leer(PETICION)
    ok = (e.get("decision_humana") == "descartada" and e.get("espera_humana") is False
          and bool(e.get("firma")))
    print(f"  almacén: decision_humana={e.get('decision_humana')} "
          f"espera_humana={e.get('espera_humana')} firma={'sí' if e.get('firma') else 'no'}")
    return ok, "la persona decidió y firmó con SU clave, sin proceso vivo de por medio"


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


def paso5():
    """El hueco que encontró un disidente externo: morir ENTRE decidir y firmar.

    Decidir y firmar son dos actos separados a propósito, porque la firma humana nace en la
    máquina de quien decide y no en el servidor. Entre uno y otro cabe una caída. Antes, al
    reiniciar, el flujo daba la pausa por resuelta y terminaba en SIN_FIRMA con
    `espera_humana=False`: la petición quedaba huérfana con pinta de resuelta, y nadie volvía
    a pedir esa firma nunca. Ahora debe VOLVER A PAUSARSE.
    """
    from src import estado
    estado._doc(PETICION).delete()
    asyncio.run(_correr_sin_responder())              # llega a la pausa
    estado.anotar_decision_humana(PETICION, "descartada")   # decide… y aquí muere el proceso
    asyncio.run(_correr_sin_responder())              # se vuelve a empezar de cero
    e = estado.leer(PETICION)
    ok = e.get("espera_humana") is True and not e.get("firma")
    print(f"  almacén: espera_humana={e.get('espera_humana')} "
          f"veredicto={e.get('veredicto')} firma={'sí' if e.get('firma') else 'no'}")
    return ok, "decidido sin firmar, el reinicio VUELVE a pedir la firma en vez de abandonarla"


PASOS = {"1": paso1, "2": paso2, "3": paso3, "4": paso4, "5": paso5}


def _correr_los_cuatro():
    """Sin argumento se corren LOS CUATRO, cada uno en su propio proceso.

    Antes, sin argumento, corría solo el paso 1 y cantaba PASA. Eso hacía que la frase «los
    cinco kill-tests en verde» fuera cierta a medias sin que nadie lo notara: la prueba
    entera solo se veía si alguien sabía pasarle el número. Un jurado no lo sabe, y esa es
    exactamente la persona a la que hay que no mentirle.
    """
    import subprocess
    todo_ok = True
    for n in ("1", "2", "3", "4", "5"):
        print(f"\n{'═' * 60}\npaso {n}\n{'═' * 60}", flush=True)
        r = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), n])
        todo_ok = todo_ok and r.returncode == 0
    print(f"\n{'═' * 60}")
    print(f"DURABILIDAD: {'PASA' if todo_ok else 'NO PASA'} — los cinco pasos, "
          f"cada uno en un proceso distinto")
    return todo_ok


if __name__ == "__main__":
    if len(sys.argv) > 1:
        n = sys.argv[1]
        ok, que = PASOS[n]()
        print(f"\npaso {n}: {'PASA' if ok else 'NO PASA'} — {que}")
        sys.exit(0 if ok else 1)
    sys.exit(0 if _correr_los_cuatro() else 1)
