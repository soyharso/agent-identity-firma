#!/usr/bin/env python3
r"""KILL-TEST — ninguna toma que toque la red puede terminar diciendo que no la tocó.

EL DEFECTO QUE CIERRA, y estaba en el último fotograma del vídeo. La toma 4 imprimía

    COMPLETE — verified with no network and no credentials

justo después de hacer cuatro llamadas HTTPS **autenticadas** a Model Armor, más el token de
acceso que necesita para hacerlas. La frase era cierta de la primera mitad de la toma —el
verificador RFC 8785, que no importa ni un paquete de red— y falsa de la segunda.

POR QUÉ PASÓ, que es lo que esta prueba vigila. No fue un descuido de redacción: la toma 4 era
**enteramente offline** cuando se escribió ese banner, y el comentario del código todavía lo
decía («Shots 1 and 4 only. They prove what they prove — offline»). Dejó de ser cierto el día
que se le añadió la comparación contra el filtro del proveedor, y **nada en el código obligaba
al banner a enterarse**. Una afirmación absoluta sobrevivió al cambio que la volvió falsa.

Es exactamente el fallo contra el que argumenta el proyecto entero, cometido en el fotograma
que un jurado mira más tiempo que ningún otro. Y en un vídeo que se puntúa por ser **una toma
sin editar**, la honestidad tiene que estar en la pantalla, no en una nota del manual: nadie
del jurado va a leer el manual.

QUÉ COMPRUEBA, sin necesitar red ni credenciales:

  1. Toda toma que invoque algo que llame a la red declara que lo hace — `preflight` (que marca
     la corrida como de nube) o `MIXTO` (que marca la toma como mezcla de las dos naturalezas).
  2. El banner absoluto «no network and no credentials» NO puede alcanzarse desde una toma que
     llame a la red.
  3. El número de llamadas que el banner mixto anuncia **no está escrito a mano**: se deriva de
     la lista de casos, que es donde de verdad vive. Un número tecleado sería el mismo pecado
     con otra fecha de caducidad — lo señaló el disidente que atacó el arreglo.

Búsqueda previa antes de crear este archivo: `grep -rn "banner\|COMPLETE" agente/killtest_*.py`
no devuelve ninguna prueba sobre lo que la demostración AFIRMA — las dieciséis prueban lo que el
sistema HACE. `killtest_blindaje.py` es la mitad de red de la toma 4, no su vigilante. No había
dónde anexar esto.
"""
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DEMO = RAIZ / "demo.sh"
BANNER_ABSOLUTO = "no network and no credentials"

# Lo que delata que un script sale a la red. `gcloud` cuenta: usa la credencial.
HUELLAS_DE_RED = ("requests.", "urllib", "httpx", "google.cloud", "gcloud ",
                  "print-access-token", "print-identity-token")


def cuerpo_de_toma(texto: str, n: int) -> str:
    m = re.search(rf"^toma{n}\(\)\s*\{{(.*?)^\}}", texto, re.S | re.M)
    return m.group(1) if m else ""


def scripts_invocados(cuerpo: str) -> list[str]:
    return re.findall(r"python3 ([\w/]+\.py)", cuerpo)


def toca_la_red(cuerpo: str) -> tuple[bool, list[str]]:
    """¿Esta toma sale a la red, por sí misma o por lo que invoca?"""
    razones = []
    for h in HUELLAS_DE_RED:
        if h in cuerpo:
            razones.append(f"la propia toma usa {h!r}")
    for s in scripts_invocados(cuerpo):
        ruta = RAIZ / s
        if not ruta.exists():
            continue
        texto = ruta.read_text(encoding="utf-8")
        for h in HUELLAS_DE_RED:
            if h in texto:
                razones.append(f"{s} usa {h!r}")
                break
    return bool(razones), razones


def main() -> int:
    if not DEMO.exists():
        print(f"no encuentro {DEMO}", file=sys.stderr)
        return 2
    texto = DEMO.read_text(encoding="utf-8")
    fallos, filas = [], []

    for n in range(1, 6):
        cuerpo = cuerpo_de_toma(texto, n)
        if not cuerpo:
            continue
        red, razones = toca_la_red(cuerpo)
        declara = ("preflight" in cuerpo) or ("MIXTO=1" in cuerpo)
        ok = (not red) or declara
        filas.append((n, red, declara, ok, razones[:2]))
        if not ok:
            fallos.append(
                f"la toma {n} sale a la red ({'; '.join(razones[:2])}) y NO lo declara: "
                f"puede terminar imprimiendo «{BANNER_ABSOLUTO}»")

    # El número que anuncia el banner mixto no puede estar tecleado.
    #
    # Y ojo con CÓMO se busca, porque la primera versión de esta comprobación no servía:
    # buscaba la frase en todo el archivo y la encontraba en el COMENTARIO que explica el
    # arreglo, no en el banner. Daba verde con el número tecleado — un vigilante que miraba
    # la explicación en vez de la afirmación. Lo destapó la prueba mutante, no la lectura.
    # Aquí solo cuentan las líneas que IMPRIMEN algo.
    lineas_banner = [l for l in texto.splitlines()
                     if "authenticated HTTPS calls" in l and l.lstrip().startswith("echo")]
    if not lineas_banner:
        fallos.append("no encuentro la línea que imprime el banner mixto: "
                      "si se renombró, esta prueba dejó de vigilar nada")
    for l in lineas_banner:
        if re.search(r"\b\d+ authenticated", l):
            fallos.append("el banner mixto trae el número de llamadas ESCRITO A MANO: "
                          "es el mismo pecado, con otra fecha de caducidad")
        if "LLAMADAS_RED" not in l:
            fallos.append("el número del banner no sale de LLAMADAS_RED, "
                          "que es lo único que lo ata a la lista de casos real")
    if lineas_banner and "LLAMADAS_RED=" not in texto:
        fallos.append("LLAMADAS_RED no se calcula en ninguna parte")

    print("\n  BANNER HONESTO — ¿alguna toma dice que no tocó la red, y la tocó?")
    print("  " + "-" * 74)
    for n, red, declara, ok, razones in filas:
        print(f"  {'OK ' if ok else 'FALLA'} toma {n}: "
              f"{'sale a la red' if red else 'offline':<14} "
              f"{'lo declara' if declara else 'no lo declara'}"
              + (f"   ({razones[0]})" if red and razones else ""))
    print("  " + "-" * 74)
    if fallos:
        for f in fallos:
            print(f"  ✗ {f}")
        return 1
    print("  El número de llamadas se deriva de la lista de casos, no de un literal.")
    print("  Ninguna toma puede afirmar en pantalla lo que no hizo.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
