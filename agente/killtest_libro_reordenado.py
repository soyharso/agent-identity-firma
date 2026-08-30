#!/usr/bin/env python3
"""KILL-TEST — reordenar dos filas del libro deja de ser indetectable.

POR QUÉ ES UN ATAQUE DISTINTO DEL BORRADO, y por eso tiene su propio kill-test. Al borrar una
fila desaparece contenido, y hay verificaciones que lo notarían por el conteo. Al **reordenar**
no falta nada: las mismas filas, los mismos sobres, las mismas firmas, el mismo número de
líneas. Un verificador que solo mire fila a fila da `OK` a las dos, porque cada firma sigue
cubriendo su propio sobre — y ninguna dice en qué lugar del libro iba.

Y el orden es contenido en un libro de firmas: cambia qué se decidió antes y qué después.
Poner la aprobación delante de la evidencia que la justifica, o mover una firma humana a un
momento anterior a la petición que la pedía, es reescribir la historia sin falsificar ni una
firma.

La cadena lo cierra porque cada fila declara de dónde viene: intercambiar dos filas rompe el
`prev` de las dos a la vez, así que la comprobación falla en la primera de ellas y la nombra
por su número de línea.

Aquí se comprueban tres reordenamientos distintos, sobre un libro de usar y tirar (este
kill-test NUNCA escribe en `libro/firmas_grafo.jsonl`):

  1. Intercambiar dos filas CONTIGUAS del medio.
  2. Intercambiar la primera con la última.
  3. Mover una fila al final sin borrar nada (una rotación).

Uso: python3 agente/killtest_libro_reordenado.py
Sin red y sin credenciales.
"""
import json
import pathlib
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src import libro_cadena  # noqa: E402

VERDE, ROJO, GRIS, FIN = "\033[32m", "\033[31m", "\033[2m", "\033[0m"

fallos = 0


def libro_de_seis(destino: pathlib.Path) -> None:
    destino.unlink(missing_ok=True)
    for i in range(1, 7):
        libro_cadena.anexar(destino,
                            {"ts": 1788000000 + i, "peticion_id": f"PET-{i:03d}",
                             "dictamen": "descartada", "veredicto": "OK",
                             "sobre": None, "firma": None})


def escribir(destino: pathlib.Path, filas: list[dict]) -> None:
    destino.write_text(
        "".join(json.dumps({k: v for k, v in f.items() if not str(k).startswith("_")},
                           ensure_ascii=False, sort_keys=True) + "\n" for f in filas),
        encoding="utf-8")


def ataque(titulo: str, destino: pathlib.Path, reordenar, linea_esperada: int) -> None:
    """Monta el libro, aplica el reordenamiento y exige que la cadena lo cace."""
    global fallos
    libro_de_seis(destino)
    filas = libro_cadena.filas_crudas(destino)
    escribir(destino, reordenar(list(filas)))
    res = libro_cadena.verificar(destino)
    ok = res["clase"] == "alterada" and res["roto_en"] == linea_esperada
    marca = f"{VERDE}✓{FIN}" if ok else f"{ROJO}✗{FIN}"
    print(f"  {marca} {titulo}")
    print(f"      {GRIS}esperaba clase=alterada línea={linea_esperada} · "
          f"salió clase={res['clase']} línea={res['roto_en']}{FIN}")
    print(f"      {GRIS}{res['mensaje'][:140]}{FIN}")
    if not ok:
        fallos += 1


def main():
    print("\n  KILL-TEST — el libro encadenado: reordenar dos filas deja de ser "
          "indetectable\n")
    print(f"  {GRIS}Ninguna fila se borra ni se edita. Mismas filas, mismas firmas, "
          f"mismo número de líneas: solo cambia el orden.{FIN}\n")

    with tempfile.TemporaryDirectory() as tmp:
        destino = pathlib.Path(tmp) / "firmas_grafo.jsonl"

        def contiguas(f):
            f[2], f[3] = f[3], f[2]
            return f

        def extremos(f):
            f[0], f[-1] = f[-1], f[0]
            return f

        def rotar(f):
            return f[:1] + f[2:] + f[1:2]

        # Al intercambiar las filas 3 y 4, la que ahora ocupa la línea 3 dice venir del hash
        # de la 3 y la anterior real es la 2: la cadena falla ahí, en la primera de las dos.
        ataque("se intercambian las filas 3 y 4 (contiguas, en medio del libro)",
               destino, contiguas, linea_esperada=3)
        ataque("se intercambian la primera y la última", destino, extremos, linea_esperada=1)
        ataque("se mueve la fila 2 al final sin borrar nada", destino, rotar,
               linea_esperada=2)

        # Y el control que evita que este kill-test pase por casualidad: el mismo libro SIN
        # reordenar tiene que salir íntegro. Una prueba que grita con todo no prueba nada.
        libro_de_seis(destino)
        res = libro_cadena.verificar(destino)
        global fallos
        ok = res["clase"] == "integra"
        marca = f"{VERDE}✓{FIN}" if ok else f"{ROJO}✗{FIN}"
        print(f"\n  {marca} CONTROL: el mismo libro sin tocar sale íntegro "
              f"(clase={res['clase']})")
        if not ok:
            fallos += 1

    print()
    if fallos:
        print(f"  {ROJO}VEREDICTO: FALLA — {fallos} comprobación(es) en rojo{FIN}\n")
        sys.exit(1)
    print(f"  {VERDE}VEREDICTO: PASA{FIN} — cambiar el orden del libro sin tocar ninguna "
          f"firma ya no pasa desapercibido.\n")


if __name__ == "__main__":
    main()
