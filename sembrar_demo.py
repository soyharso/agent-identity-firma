#!/usr/bin/env python3
"""Siembra una cola de atención coherente para la demostración.

EL PROBLEMA QUE RESUELVE. El libro que se venía enseñando era el libro del DESARROLLO: cada vez
que alguien corría la demo o un kill-test, se anotaba otra operación sobre el mismo caso. El
resultado, medido: PET-002 con veintisiete operaciones, veinte de ellas con el hash idéntico
porque era el mismo texto una y otra vez. En pantalla parecían veintisiete intentos distintos y
no eran nada: eran la misma prueba repetida durante dos días.

Eso no se arregla en el panel. El panel pintaba fielmente lo que había; lo que estaba mal era lo
que había. Un libro de demostración tiene que contar UNA historia, y esa historia es la cola de
atención de Qnowa: peticiones que entran por un canal, un agente que despacha las que puede
probar con evidencia, y una persona que responde por las que comprometen a alguien.

QUÉ SIEMBRA, y por qué cada caso está:

  · uno que el agente cierra solo, porque hay evidencia objetiva que cualquiera puede rehacer;
  · uno que se para y espera a una persona, porque decidir sobre una reclamación es un juicio;
  · uno donde el agente INTENTA cerrar de todas formas y se le rechaza — el argumento del vídeo;
  · uno que nace de otro, para que se vea el expediente padre;
  · y uno que sigue esperando, porque una cola real nunca está vacía.

Nada de esto es decorado: cada operación se firma de verdad y queda en el mismo libro que el
verificador comprueba. Lo que se siembra es el CASO, no la evidencia.

    python3 sembrar_demo.py            # siembra
    python3 sembrar_demo.py --borrar   # deja la cola vacía

Sin argumentos no borra nada de lo que ya haya: añade.
"""
import sys
import time

sys.path.insert(0, __file__.rsplit("/", 1)[0])

from src import libro_demo  # noqa: E402

VERDE, ROJO, GRIS, FIN = "\033[32m", "\033[31m", "\033[2m", "\033[0m"

# La cola. Textos en inglés porque el vídeo se narra en inglés.
COLA = [
    {"texto": "The index was rebuilt: the report that took 40 s now takes 0.3 s. Ticket can be closed.",
     "de": "ops-monitor", "canal": "system",
     "guion": [("agente-curador", "cerrada", "MAQUINA", "evidence anyone can re-derive")]},

    {"texto": "I was charged twice for the same invoice. I want an immediate refund.",
     "de": "cliente-4471", "canal": "portal",
     "guion": [("agente-curador", "exige_humano", "MAQUINA", "money and liability: stops"),
               ("persona-operador", "cerrada_con_juicio", "HUMANO", "supervisor grants the refund")]},

    {"texto": "Dismissing the customer complaint: reviewing the history, the error was theirs.",
     "de": "cliente-8802", "canal": "portal",
     "guion": [("agente-curador", "exige_humano", "MAQUINA", "a judgement about a person"),
               ("agente-curador", "RECHAZADO", "MAQUINA", "the agent tries to close it anyway"),
               ("persona-operador", "descartada", "HUMANO", "the person decides, and signs")]},

    {"texto": "Following up on the double charge: please confirm the refund reached my account.",
     "de": "cliente-4471", "canal": "portal", "padre_de": 1,
     "guion": [("agente-curador", "cerrada", "MAQUINA", "verifiable against the payment log")]},

    {"texto": "My subscription was cancelled without notice and I want it reinstated today.",
     "de": "cliente-1290", "canal": "portal",
     "guion": []},
]


def borrar():
    c = libro_demo._c()
    if c is None:
        sys.exit("Sin Firestore no hay nada que borrar aquí.")
    n = 0
    for col in (libro_demo.COL_PETICIONES, libro_demo.COL_FIRMAS):
        for d in c.collection(col).stream():
            d.reference.delete()
            n += 1
    print(f"{VERDE}Borradas {n} entradas de la cola de demostración.{FIN}")


def main():
    if "--borrar" in sys.argv:
        borrar()
        return

    if not libro_demo.disponible():
        print(f"{ROJO}Firestore no disponible: se sembrará en fichero y no sobrevivirá "
              f"al reinicio del contenedor.{FIN}")

    try:
        from src.firma_kms import firmar, resumen
    except Exception as e:                                       # noqa: BLE001
        sys.exit(f"No puedo firmar: {e}")

    base = int(time.time()) - 900          # la cola empieza hace quince minutos
    ids = []

    for i, caso in enumerate(COLA):
        padre = ids[caso["padre_de"]] if "padre_de" in caso else None
        pid, _ = libro_demo.nueva_peticion(caso["texto"], de=caso["de"],
                                           origen=caso["canal"], padre=padre)
        ids.append(pid)
        marca = f"{GRIS}↳ from {padre}{FIN}" if padre else ""
        print(f"\n  {pid}  {caso['texto'][:62]}…  {marca}")

        for j, (quien, estado, tipo, porque) in enumerate(caso["guion"]):
            momento = base + i * 120 + j * 35
            clave = "clave-agente" if tipo == "MAQUINA" else "clave-humano"
            rechazo = estado == "RECHAZADO"

            sobre = {"peticion_id": pid,
                     "estado_destino": "descartada" if rechazo else estado,
                     "tipo_firmante": tipo,
                     "curado_por": quien,
                     "hash_contenido": resumen(caso["texto"]),
                     "marca_temporal": momento,
                     "emitido_en": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(momento)),
                     "origen": caso["canal"],
                     "emisor": quien,
                     "sobre_quien": caso["de"],
                     "algoritmo": "EC_SIGN_P256_SHA256"}
            if padre:
                sobre["peticion_padre"] = padre

            if rechazo:
                # El agente pide firmar un juicio con la clave que no le corresponde. Cloud KMS
                # rechaza por IAM: no se firma nada, y el intento queda anotado. Que el rechazo
                # figure en el libro es la mitad del argumento — lo otro sería esconderlo.
                r = firmar("clave-humano", sobre)
                veredicto = "FUERA_DE_ALCANCE" if r.get("http") == 200 else "PERMISSION_DENIED"
                libro_demo.anotar_firma({"ts": momento, "peticion_id": pid,
                                         "dictamen": "intento_de_firma",
                                         "veredicto": veredicto, "sobre": sobre, "firma": None})
                print(f"     {ROJO}✗ {veredicto:<20}{FIN} {GRIS}{porque}{FIN}")
                continue

            r = firmar(clave, sobre)
            if r.get("http") != 200:
                print(f"     {ROJO}✗ no se pudo firmar: {str(r)[:70]}{FIN}")
                continue
            libro_demo.anotar_firma({"ts": momento, "peticion_id": pid,
                                     "dictamen": estado, "veredicto": "OK",
                                     "sobre": sobre, "firma": r.get("firma")})
            print(f"     {VERDE}✓ {estado:<20}{FIN} {GRIS}{quien} — {porque}{FIN}")

    print(f"\n{VERDE}Cola sembrada.{FIN} {GRIS}Míra la en /ui/unified{FIN}\n")


if __name__ == "__main__":
    main()
