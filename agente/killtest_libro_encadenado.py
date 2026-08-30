#!/usr/bin/env python3
"""KILL-TEST — borrar una fila del libro deja de ser indetectable.

EL PROBLEMA QUE CIERRA, y estaba medido. `libro/firmas_grafo.jsonl` anotaba una fila por
operación y **ninguna apuntaba a la anterior**:

    $ python3 -c "import json; f=[json.loads(l) for l in open('libro/firmas_grafo.jsonl') if l.strip()]; print(len(f), sorted(f[0]))"
    50 ['dictamen', 'firma', 'peticion_id', 'sobre', 'ts', 'veredicto']

Cada firma cubre su propio sobre y nada más. Así que se podía **borrar una fila entera** y
las otras 49 seguían verificando: el verificador las recorría una a una, todas salían `OK`, y
del hueco no decía ni una palabra. El libro probaba que *lo que hay es auténtico*; no probaba
que *esté todo lo que hubo*. Para un libro de firmas eso es media promesa.

LO QUE SE COMPRUEBA AQUÍ, en cuatro pasos y sobre un libro de usar y tirar (este kill-test
NUNCA escribe en `libro/firmas_grafo.jsonl`):

  1. Se anexan filas con `src/libro_cadena.py` y la cadena queda íntegra.
  2. Se BORRA una fila del medio → tiene que salir `alterada`, y decir en qué línea.
  3. Se EDITA una fila sin tocar su hash → tiene que salir `alterada`.
  4. Un escritor viejo anexa sin cadena (la trampa de la CONVIVENCIA, que es el fallo que no
     comete nadie: dos escritores desplegados a medias cortan la cadena sin mala fe) → tiene
     que salir `convivencia` y NO confundirse con un borrado.

Y el paso final es de mundo real: se ejecuta **el verificador de verdad**,
`python3 src/verificar_sobre.py <libro>`, como subproceso y contra el libro con la fila
borrada, y se exige que **salga con código distinto de cero**. Que la biblioteca cace el
borrado no sirve de nada si el comando que teclea un jurado sigue diciendo que todo está bien.

LO QUE ESTO **NO** PRUEBA, dicho antes de que lo pregunte otro: la cadena da CONTINUIDAD, no
autenticidad de la cadena. Quien pueda escribir el archivo puede recalcularla entera. Lo que
prueba la autenticidad de cada decisión sigue siendo la firma ECDSA del sobre, que es otra
cosa y se comprueba en los otros kill-tests.

Uso: python3 agente/killtest_libro_encadenado.py
Sin red y sin credenciales.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src import libro_cadena  # noqa: E402

VERDE, ROJO, GRIS, FIN = "\033[32m", "\033[31m", "\033[2m", "\033[0m"

fallos = 0


def comprobar(titulo: str, res: dict, clase_esperada: str, exige_linea: int | None = None):
    """Una comprobación: la clase que salió tiene que ser la que se esperaba."""
    global fallos
    ok = res["clase"] == clase_esperada
    if ok and exige_linea is not None:
        ok = res["roto_en"] == exige_linea
    marca = f"{VERDE}✓{FIN}" if ok else f"{ROJO}✗{FIN}"
    print(f"  {marca} {titulo}")
    print(f"      {GRIS}esperaba clase={clase_esperada}"
          f"{f' línea={exige_linea}' if exige_linea is not None else ''} · "
          f"salió clase={res['clase']} línea={res['roto_en']}{FIN}")
    print(f"      {GRIS}{res['mensaje'][:140]}{FIN}")
    if not ok:
        fallos += 1


def libro_con(n: int, destino: pathlib.Path) -> list[dict]:
    """Un libro nuevo con `n` filas encadenadas, escritas por la biblioteca de verdad."""
    return [libro_cadena.anexar(destino,
                                {"ts": 1788000000 + i, "peticion_id": f"PET-{i:03d}",
                                 "dictamen": "descartada", "veredicto": "OK",
                                 "sobre": None, "firma": None})
            for i in range(1, n + 1)]


def escribir(destino: pathlib.Path, filas: list[dict]) -> None:
    """Reescribe el libro entero. Es lo que haría un atacante con acceso al archivo."""
    destino.write_text(
        "".join(json.dumps({k: v for k, v in f.items() if not str(k).startswith("_")},
                           ensure_ascii=False, sort_keys=True) + "\n" for f in filas),
        encoding="utf-8")


def main():
    print("\n  KILL-TEST — el libro encadenado: borrar una fila deja de ser indetectable\n")

    with tempfile.TemporaryDirectory() as tmp:
        destino = pathlib.Path(tmp) / "firmas_grafo.jsonl"

        # 1 — la cadena, tal como la escribe el escritor de verdad.
        libro_con(6, destino)
        comprobar("seis filas recién encadenadas: la cadena cuadra",
                  libro_cadena.verificar(destino), "integra")

        # 2 — se borra la fila 3 de 6. Nadie toca las demás.
        filas = libro_cadena.filas_crudas(destino)
        escribir(destino, filas[:2] + filas[3:])
        res_borrada = libro_cadena.verificar(destino)
        comprobar("se BORRA la fila 3 de 6 y no se toca ninguna otra",
                  res_borrada, "alterada", exige_linea=3)

        # 3 — se edita el contenido de una fila dejándole su hash viejo.
        libro_con(0, destino)
        destino.unlink(missing_ok=True)
        libro_con(6, destino)
        filas = libro_cadena.filas_crudas(destino)
        filas[3]["veredicto"] = "OK_PERO_NO"
        escribir(destino, filas)
        comprobar("se EDITA el veredicto de la fila 4 sin recalcular su hash",
                  libro_cadena.verificar(destino), "alterada", exige_linea=4)

        # 4 — la convivencia: el escritor viejo, que solo anexa, vuelve a mitad de despliegue.
        #     Es el fallo que no comete nadie, y por eso hay que distinguirlo de un borrado:
        #     se arregla migrando el escritor, no reparando el archivo.
        destino.unlink(missing_ok=True)
        libro_con(4, destino)
        with destino.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": 1788009999, "peticion_id": "PET-VIEJA",
                                 "dictamen": "descartada", "veredicto": "OK"},
                                ensure_ascii=False) + "\n")
        comprobar("un escritor SIN cadena anexa detrás: es convivencia, no un borrado",
                  libro_cadena.verificar(destino, tolerar_convivencia=True),
                  "convivencia", exige_linea=5)

        # 5 — MUNDO REAL: el comando que teclea un jurado tiene que fallar.
        print(f"\n  {GRIS}Y el verificador de verdad, como subproceso, sobre el libro "
              f"con la fila borrada:{FIN}")
        destino.unlink(missing_ok=True)
        libro_con(6, destino)
        filas = libro_cadena.filas_crudas(destino)
        escribir(destino, filas[:2] + filas[3:])
        p = subprocess.run([sys.executable, "src/verificar_sobre.py", str(destino)],
                           cwd=RAIZ, capture_output=True, text=True)
        global fallos
        real_ok = p.returncode != 0 and "ALTERADA" in p.stdout.upper()
        marca = f"{VERDE}✓{FIN}" if real_ok else f"{ROJO}✗{FIN}"
        print(f"  {marca} python3 src/verificar_sobre.py <libro con fila borrada> "
              f"→ salida {p.returncode}")
        for linea in p.stdout.strip().splitlines()[-5:]:
            print(f"      {GRIS}{linea}{FIN}")
        if not real_ok:
            fallos += 1

    print()
    if fallos:
        print(f"  {ROJO}VEREDICTO: FALLA — {fallos} comprobación(es) en rojo{FIN}\n")
        sys.exit(1)
    print(f"  {VERDE}VEREDICTO: PASA{FIN} — borrar una fila del libro ya no es "
          f"indetectable, y el verificador lo dice con su número de línea.\n")


if __name__ == "__main__":
    main()
