#!/usr/bin/env python3
"""KILL-TEST — la serialización, que es donde la promesa se rompe en silencio.

Todo el producto se apoya en que cualquiera pueda rehacer la verificación, también en otro
lenguaje. Si el que firma y el que verifica no producen los mismos bytes, dos programas
correctos llegan a veredictos distintos y **nadie se entera hasta que un acento lo destapa**.

Aquí estuvo el fallo: dos serializadores escritos con quince minutos de diferencia, uno
escapando los acentos y el otro no. Con texto en inglés daban lo mismo. Esta prueba existe para
que no vuelva a pasar.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.canonico import canonico                    # noqa: E402
from src.firma_kms import canonico as canonico_firma  # noqa: E402
from src.verificar_sobre import canonico as canonico_verifica  # noqa: E402

# Los dos casos donde una aproximación casera diverge de la norma, medidos por la fase cero.
CASOS = [
    ("un acento", {"motivo": "revisión", "peticion_id": "PET-1"}),
    ("un número decimal", {"cantidad": 2.0, "peticion_id": "PET-1"}),
    ("los dos a la vez", {"motivo": "sanción", "cantidad": 3.0, "peticion_id": "PET-2"}),
    ("orden de las claves al revés", {"z": 1, "a": 2, "m": 3}),
    ("solo texto sencillo", {"peticion_id": "PET-3", "estado_destino": "cerrada"}),
]


def main():
    print("KILL-TEST — el que firma y el que verifica producen los MISMOS bytes\n")
    fallos = 0
    for nombre, sobre in CASOS:
        a, b, c = canonico_firma(sobre), canonico_verifica(sobre), canonico(sobre)
        ok = a == b == c
        if not ok:
            fallos += 1
        print(f"  {'ok  ' if ok else 'FALLA'} {nombre:<32} {a.decode()[:56]}")
        if not ok:
            print(f"        firma   : {a}")
            print(f"        verifica: {b}")

    # Y la prueba de que la norma hace lo que promete: sin escapes y sin decimales de adorno.
    bytes_acento = canonico({"m": "revisión"})
    bytes_decimal = canonico({"n": 2.0})
    print()
    print(f"  el acento viaja crudo, sin escapar : {bytes_acento!r}")
    print(f"  el decimal entero se normaliza     : {bytes_decimal!r}")
    if b"\\u00f3" in bytes_acento:
        print("  FALLA: el acento salió escapado, no es la norma")
        fallos += 1
    if b"2.0" in bytes_decimal:
        print("  FALLA: el decimal no se normalizó, no es la norma")
        fallos += 1

    print(f"\nfallos: {fallos}")
    print("VEREDICTO:", "PASA — una sola serialización, y es la de la norma"
          if fallos == 0 else "NO PASA — hay más de una forma de firmar lo mismo")
    sys.exit(0 if fallos == 0 else 1)


if __name__ == "__main__":
    main()
