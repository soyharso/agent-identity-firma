#!/usr/bin/env python3
"""KILL-TEST — al libro se le corta el final, y el ancla lo tiene que cazar.

QUÉ MATA. `agente/killtest_libro_encadenado.py` ya dice, en su propio título, lo que la cadena
no puede: *«altering or removing a row INSIDE the chain is caught; truncating the tail is
not»*. Eso NO es un defecto de implementación — una cadena de resúmenes hacia atrás no puede
detectar su propio truncamiento, porque lo que queda tras cortar el final sigue siendo una
cadena válida, solo que más corta. Esta prueba existe para que esa frase deje de ser cierta, y
para fallar en rojo el día que alguien rompa el ancla.

CÓMO ESTÁ CONSTRUIDA, y esto importa tanto como lo que prueba:

  · **Nunca toca `libro/firmas_grafo.jsonl`.** Copia el libro real a un temporal y ataca la
    copia. Igual que los dos kill-tests de libro que ya existen.
  · **Se firma con un par de claves EFÍMERO**, generado aquí y muerto al terminar. El ancla de
    verdad la firma `clave-humano` en Cloud KMS, y este proceso —que es el agente— recibe
    HTTP 403 al pedirla: ese 403 es el argumento del producto, no un obstáculo a sortear. Lo
    que esta prueba comprueba es la LÓGICA de verificación, que es independiente de qué llave
    concreta firme.
  · **Prueba también que NO grita cuando nadie ataca** (casos 1 y 9). Un ancla que da falsas
    alarmas se apaga a la semana y deja de proteger: es el modo de fallo que señaló el
    disidente del diseño, y por eso tiene su propio caso.

Cada caso deja su línea en `libro/killtest_ancla.jsonl` para que cualquiera rehaga el
veredicto sin volver a correr nada.
"""
import base64
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from cryptography.hazmat.primitives import hashes                      # noqa: E402
from cryptography.hazmat.primitives.asymmetric import ec               # noqa: E402
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed  # noqa: E402
from cryptography.hazmat.primitives.serialization import (             # noqa: E402
    Encoding, PublicFormat)

from src import ancla as A                                             # noqa: E402
from src import libro_cadena                                           # noqa: E402

LIBRO_REAL = RAIZ / "libro" / "firmas_grafo.jsonl"
REGISTRO = RAIZ / "libro" / "killtest_ancla.jsonl"


class Firmante:
    """Una llave que solo vive en este proceso. Hace de `clave-humano` sin serlo."""

    def __init__(self, dir_claves: pathlib.Path, nombre: str = A.CLAVE_ANCLA):
        self.priv = ec.generate_private_key(ec.SECP256R1())
        dir_claves.mkdir(parents=True, exist_ok=True)
        (dir_claves / f"{nombre}.pem").write_bytes(
            self.priv.public_key().public_bytes(Encoding.PEM,
                                                PublicFormat.SubjectPublicKeyInfo))

    def firma(self, sobre: dict) -> str:
        return base64.b64encode(
            self.priv.sign(hashlib.sha256(A.canonico(sobre)).digest(),
                           ec.ECDSA(Prehashed(hashes.SHA256())))).decode()


def anclar(libro, ruta_ancla, firmante: Firmante) -> dict:
    sobre = A.construir(libro, ruta_ancla)
    return A.anexar_ancla(ruta_ancla, sobre, firmante.firma(sobre))


def _filas(p) -> list[str]:
    return [l for l in pathlib.Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def _escribir(p, lineas):
    pathlib.Path(p).write_text("\n".join(lineas) + "\n", encoding="utf-8")


def caso(nombre, rompe, esperado, monta):
    """Monta el escenario en un directorio propio y compara la CLASE con la esperada."""
    with tempfile.TemporaryDirectory(prefix="killtest_ancla_") as tmp:
        tmp = pathlib.Path(tmp)
        libro = tmp / "firmas_grafo.jsonl"
        ruta_ancla = tmp / "ancla.jsonl"
        claves = tmp / "claves"
        shutil.copy(LIBRO_REAL, libro)
        firmante = Firmante(claves)
        detalle = monta(libro, ruta_ancla, firmante) or {}
        r = A.verificar(libro, ruta_ancla, dir_claves=claves)
    ok = r["clase"] == esperado
    return {"caso": nombre, "rompe": rompe, "esperado": esperado, "obtenido": r["clase"],
            "ok": ok, "mensaje": r["mensaje"], **detalle}


# --- Los escenarios ---------------------------------------------------------------------

def m_intacto(libro, ra, f):
    anclar(libro, ra, f)


def m_cortar_diez(libro, ra, f):
    anclar(libro, ra, f)
    lineas = _filas(libro)
    _escribir(libro, lineas[:-10])
    return {"filas_antes": len(lineas), "filas_despues": len(lineas) - 10}


def m_cortar_una(libro, ra, f):
    anclar(libro, ra, f)
    lineas = _filas(libro)
    _escribir(libro, lineas[:-1])


def m_borrar_prefijo(libro, ra, f):
    """Borra una de las 50 filas anteriores a la cadena: las que la cadena NO cubre."""
    anclar(libro, ra, f)
    lineas = _filas(libro)
    del lineas[10]
    _escribir(libro, lineas)


def m_alterar_envoltorio(libro, ra, f):
    """Cambia `veredicto`, que NINGUNA firma cubre. Es la fila 3 de la tabla del brief."""
    anclar(libro, ra, f)
    lineas = _filas(libro)
    fila = json.loads(lineas[-1])
    fila["veredicto"] = "OK_FALSIFICADO"
    lineas[-1] = json.dumps(fila, ensure_ascii=False, sort_keys=True)
    _escribir(libro, lineas)


def m_diputado_confundido(libro, ra, f):
    """EL ataque del disidente: truncar y hacer que la persona firme un ancla del libro corto.

    El firmante es el MISMO y la llave es la BUENA — así que la firma del ancla nueva es
    perfectamente válida. Lo que lo caza es que el ancla anterior ya está firmada diciendo que
    había más filas, y esa el escritor no la puede reescribir.
    """
    anclar(libro, ra, f)
    lineas = _filas(libro)
    _escribir(libro, lineas[:-14])
    anclar(libro, ra, f)
    return {"filas_antes": len(lineas), "filas_despues": len(lineas) - 14}


def m_ancla_rebajada(libro, ra, f):
    """Se siembra un ancla que declara MENOS filas que la anterior, sin tocar el libro.

    Este caso existe por una medición incómoda: el ataque del diputado confundido lo caza el
    CONTEO del ancla anterior antes de que la monotonía llegue a evaluarse, así que la
    comprobación de regresión se quedaba sin ejercitar — un chequeo sin prueba es código no
    probado. Aquí se la ataca de frente: el libro queda intacto (así que el conteo cuadra) y lo
    que se anexa es un ancla rebajada, construida sobre una copia recortada. Es la maniobra de
    quien prepara el terreno para truncar más tarde.
    """
    anclar(libro, ra, f)
    recorte = libro.with_name("recorte.jsonl")
    _escribir(recorte, _filas(libro)[:-14])
    sobre = A.construir(recorte, ra)
    sobre["libro"] = libro.name
    A.anexar_ancla(ra, sobre, f.firma(sobre))
    recorte.unlink()


def m_ancla_de_otra_llave(libro, ra, f):
    """El agente fabrica su propia ancla. Es lo único que el 403 hace imposible de verdad."""
    impostor = Firmante(pathlib.Path(tempfile.mkdtemp()), nombre="impostor")
    sobre = A.construir(libro, ra)
    A.anexar_ancla(ra, sobre, impostor.firma(sobre))


def m_sin_ancla(libro, ra, f):
    """Borran el archivo de anclas entero. Se exige que el verificador NO diga que todo va bien."""
    return {}


def m_borrar_anclas_y_reanclar(libro, ra, f):
    """El agujero que encontró el juez: borrar el historial de anclas ENTERO y re-anclar el
    libro ya truncado, con la llave legítima.

    Se espera `integro`, y eso NO es un aprobado: es la medición de un agujero conocido. Dentro
    del archivo, un libro truncado con un ancla nueva y válida es indistinguible de un libro
    corto legítimo recién anclado — el mismo problema del día uno, una vuelta más arriba. Lo que
    lo detecta está FUERA de este código: el historial de git, donde el ancla borrada sigue
    estando.

    HASTA DÓNDE LLEGA DE VERDAD, más estrecho de lo que parece, y lo acotó el operador: esta
    prueba firma ella misma el ancla nueva, y esa es la licencia que se toma. En el sistema real
    LA MÁQUINA NO PUEDE DAR ESE PASO. Si trunca y borra el historial, lo que queda es un libro
    SIN ancla, y eso se caza (`sin_ancla`, fallo cerrado). El agujero solo se consuma cuando
    DESPUÉS una persona firma un ancla sobre el libro ya mutilado sin darse cuenta — el humano
    como paso involuntario, que es la familia del diputado confundido. Se mide igual, porque el
    día que el anclado se automatice este escenario pasa a ser el principal.
    """
    anclar(libro, ra, f)
    lineas = _filas(libro)
    _escribir(libro, lineas[:-14])
    ra.unlink()
    anclar(libro, ra, f)
    return {"filas_antes": len(lineas), "filas_despues": len(lineas) - 14,
            "falso_negativo_declarado": True}



def m_ilegible_sustituida(libro, ra, f):
    """Una línea que no es JSON, dentro de lo anclado, cambiada por OTRA basura distinta.

    Lo encontró la fase cero ejecutando, y era un falso negativo de verdad: el lector marca la
    línea ilegible como `{"_ilegible": ..., "_crudo": ...}`, el cuerpo canónico descarta todo lo
    que empieza por `_`, y dos basuras distintas resumían igual — a `{}`. Se podía cambiar una
    por otra dentro del ancla sin que nada se enterara.
    """
    lineas = _filas(libro)
    lineas.insert(20, "esto no es json valido {{{")
    _escribir(libro, lineas)
    anclar(libro, ra, f)
    lineas[20] = "otra basura COMPLETAMENTE distinta ###???"
    _escribir(libro, lineas)


def m_reserializado(libro, ra, f):
    """Nadie ataca: alguien reescribe el archivo con las claves JSON en otro orden.

    Si el ancla gritara aquí, sería una falsa alarma — y una falsa alarma enseña al operador a
    ignorar la alarma. Este caso es la prueba del cambio que impuso el disidente: se ancla el
    cuerpo CANÓNICO, no los bytes crudos.
    """
    anclar(libro, ra, f)
    lineas = _filas(libro)
    revueltas = []
    for l in lineas:
        fila = json.loads(l)
        revueltas.append(json.dumps(dict(reversed(list(fila.items()))),
                                    ensure_ascii=False, indent=None))
    _escribir(libro, revueltas)


CASOS = [
    ("ancla-intacta", "un libro no tocado no dispara ninguna alarma", "integro", m_intacto),
    ("truncar-diez", "cortar las DIEZ últimas filas del libro", "faltan_filas", m_cortar_diez),
    ("truncar-una", "cortar UNA sola fila del final", "faltan_filas", m_cortar_una),
    ("borrar-prefijo", "borrar una de las 50 filas que la cadena no cubre", "faltan_filas",
     m_borrar_prefijo),
    ("alterar-envoltorio", "cambiar `veredicto`, que ninguna firma cubre", "alterado",
     m_alterar_envoltorio),
    ("diputado-confundido", "truncar y firmar un ancla nueva del libro corto", "faltan_filas",
     m_diputado_confundido),
    ("ancla-rebajada", "sembrar un ancla que declara menos filas que la anterior", "regresion",
     m_ancla_rebajada),
    ("ancla-impostora", "fabricar un ancla con una llave que no es la humana", "firma_invalida",
     m_ancla_de_otra_llave),
    ("sin-ancla", "borrar el archivo de anclas entero", "sin_ancla", m_sin_ancla),
    ("anclas-borradas-y-reanclado", "borrar el historial de anclas y re-anclar el libro corto "
     "— FALSO NEGATIVO declarado: lo detecta git, no el ancla", "integro",
     m_borrar_anclas_y_reanclar),
    ("ilegible-sustituida", "cambiar una línea ilegible por otra basura dentro del ancla",
     "ilegible_en_ancla", m_ilegible_sustituida),
    ("reserializado", "reescribir el JSON en otro orden SIN atacar nada", "integro",
     m_reserializado),
]


def control_ruta_directorio() -> dict:
    """Un verificador que un auditor va a correr no puede contestar con una traza de Python."""
    with tempfile.TemporaryDirectory(prefix="killtest_ancla_dir_") as tmp:
        r = A.verificar(pathlib.Path(tmp), pathlib.Path(tmp) / "ancla.jsonl")
    return {"caso": "ruta-directorio", "rompe": "pasar un directorio como ruta del libro",
            "esperado": "ruta_invalida", "obtenido": r["clase"],
            "ok": r["clase"] == "ruta_invalida" and not r["ok"], "mensaje": r["mensaje"]}


def control_la_cadena_sola_no_lo_ve() -> dict:
    """El control que da sentido a todo lo anterior: sin ancla, truncar NO se detecta.

    Si algún día esta comprobación fallara —es decir, si la cadena empezara a detectar el
    truncamiento por su cuenta— habría que revisar el diseño entero, no celebrarlo.
    """
    with tempfile.TemporaryDirectory(prefix="killtest_ancla_ctl_") as tmp:
        copia = pathlib.Path(tmp) / "firmas_grafo.jsonl"
        shutil.copy(LIBRO_REAL, copia)
        lineas = _filas(copia)
        _escribir(copia, lineas[:-10])
        r = libro_cadena.verificar(copia, tolerar_convivencia=True)
    return {"caso": "control-cadena-sola", "rompe": "la cadena SOLA ante el mismo corte",
            "esperado": "no lo detecta", "obtenido": ("no lo detecta" if r["ok"]
                                                      else f"lo detecta: {r['clase']}"),
            "ok": r["ok"], "mensaje": r["mensaje"]}


def main():
    if not LIBRO_REAL.exists():
        print(f"no encuentro {LIBRO_REAL}", file=sys.stderr)
        return 2
    t0 = time.time()
    filas = [caso(*c) for c in CASOS]
    filas.append(control_ruta_directorio())
    filas.append(control_la_cadena_sola_no_lo_ve())
    verdes = sum(1 for f in filas if f["ok"])

    corrida = {"ts": int(t0), "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
               "libro": str(LIBRO_REAL), "filas_libro": len(_filas(LIBRO_REAL)),
               "segundos": round(time.time() - t0, 2),
               "verdes": verdes, "total": len(filas), "casos": filas}
    with REGISTRO.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(corrida, ensure_ascii=False) + "\n")

    print(f"\n  ANCLA — {verdes}/{len(filas)} casos como se esperaba"
          f"   ({corrida['segundos']}s, sobre una copia de {corrida['filas_libro']} filas)")
    print("  " + "-" * 76)
    for f in filas:
        print(f"  {'OK ' if f['ok'] else 'FALLA'} {f['caso']:<22} {f['rompe']}")
        if not f["ok"]:
            print(f"      esperaba {f['esperado']!r}, obtuvo {f['obtenido']!r}")
    print("  " + "-" * 76)
    print(f"  registro: {REGISTRO.relative_to(RAIZ)}\n")
    return 0 if verdes == len(filas) else 1


if __name__ == "__main__":
    raise SystemExit(main())
