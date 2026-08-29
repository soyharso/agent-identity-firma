#!/usr/bin/env python3
"""The opening shot: the measured defect this project came out of.

Seconds 0-10 of the demo video. It reads `libro/defecto_medido.json` and prints
the count, its date, its scope and where it was measured. Nothing here is
invented at run time and nothing is queried live: the measurement happened once,
on 2026-08-26, in our own preproduction system, and this only reads the record
of it. That is why every line carries its source.

    python3 apertura.py            # the shot
    python3 apertura.py --fuente   # the record behind it, verbatim

No credentials, no network, no Google packages.
"""
import json
import os
import sys

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libro", "defecto_medido.json")

BOLD, DIM, RED, GREEN, WHITE, RESET = "\033[1m", "\033[2m", "\033[31m", "\033[32m", "\033[97m", "\033[0m"


def cargar():
    try:
        with open(RUTA, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit(f"No encuentro el registro de la medición: {RUTA}")


def main():
    d = cargar()

    if "--fuente" in sys.argv:
        print(json.dumps(d, indent=2, ensure_ascii=False))
        return

    ancho = 78
    print()
    print(f"{DIM}{'─' * ancho}{RESET}")
    print(f"  {DIM}{d['sistema']} · measured {d['fecha']} · {d['entorno']}{RESET}")
    print(f"{DIM}{'─' * ancho}{RESET}")
    print()
    for c in d["conteos"]:
        print(f"  {BOLD}{RED if c['color_rojo'] else GREEN}{c['valor']:>4}{RESET}  "
              f"{BOLD}{WHITE}{c['etiqueta']}{RESET}")
        print(f"        {DIM}{c['significa']}{RESET}")
        print()
    print(f"{DIM}{'─' * ancho}{RESET}")
    print(f"  {DIM}Source: {d['fuente']}{RESET}")
    print(f"  {DIM}Run `python3 apertura.py --fuente` for the full record.{RESET}")
    print(f"{DIM}{'─' * ancho}{RESET}")
    print()


if __name__ == "__main__":
    main()
