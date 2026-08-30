#!/usr/bin/env python3
r"""El ancla firmada del libro: lo único que puede detectar que le cortaron el final.

QUÉ PROBLEMA CIERRA, y estaba medido antes de escribir esto. `src/libro_cadena.py` encadena
cada fila con el resumen de la anterior, y con eso caza que alteren, borren o reordenen una
fila **del medio**. Lo que NO puede cazar es su propio truncamiento:

    $ head -n 49 libro/firmas_grafo.jsonl > /tmp/copia.jsonl   # se cortan las diez últimas
    $ python3 src/libro_cadena.py /tmp/copia.jsonl
    "mensaje": "cadena íntegra: 8 filas encadenadas + 41 de prefijo declarado"

No es un defecto de implementación: **ninguna** cadena hacia atrás puede detectarlo, porque lo
que queda tras cortar el final sigue siendo una cadena perfectamente válida, solo que más
corta. Ningún arreglo dentro del archivo lo resuelve. Hace falta algo FUERA del archivo que
diga cuánto había — y que lo diga alguien que no pueda escribir el archivo.

QUIÉN FIRMA, que es la pregunta entera. No es «qué hash»: un hash lo recalcula cualquiera que
pueda escribir el libro, y entonces no hay ancla. Es **qué identidad firma el ancla y por qué
el que escribe el libro no puede usarla**. Este sistema ya tiene la respuesta montada:

  · `sa-mediador` es la ÚNICA identidad con permiso de escritura sobre el libro
    (`servicio/mediador.py`).
  · `clave-humano` en Cloud KMS le devuelve **HTTP 403 PERMISSION_DENIED** a ese mismo agente,
    por IAM, y eso está demostrado en vivo (`src/firma_kms.py`, `ENTREGA.md:53`).

Así que el ancla la firma `clave-humano`: el escritor del libro **no puede firmar lo que lo
audita**. Es el mismo 403 que ya protege cada decisión, aplicado un nivel más arriba — al
libro entero — sin ninguna pieza nueva.

POR QUÉ LAS ANCLAS SE ENCADENAN ENTRE SÍ. Este es el ataque que tumbó la primera versión del
diseño, y lo encontró un disidente de otro linaje (Kimi K3) antes de que se escribiera una
línea de código: *el 403 prueba que el agente no puede INVOCAR la llave, no que no pueda
ELEGIR LO QUE LA LLAVE FIRMA*. Si el escritor arma el sobre que la persona firma, trunca el
libro de 59 filas a 45 y presenta un ancla de 45, la persona firma un libro mutilado sin
enterarse — y el ancla lo certifica.

El arreglo no es pedirle a la persona que mire mejor: un control que depende de que alguien lea
con atención a las once de la noche no es un control. Cada ancla lleva DENTRO DE LA FIRMA el
hash del ancla anterior, y el verificador exige dos monotonías:

  1. `filas` nunca decrece entre un ancla y la siguiente.
  2. Lo que un ancla ya firmó tiene que SEGUIR SIENDO un prefijo del libro después.

Con eso, el ataque rompe solo: el ancla anterior ya está firmada diciendo 59, y esa el escritor
no la puede reescribir. La detección deja de depender de la atención humana.

QUÉ SE ANCLA, y aquí hubo un segundo cambio por el mismo ataque. La primera versión anclaba el
sha256 de los BYTES del prefijo. El disidente lo llamó fábrica de falsas alarmas, con razón: un
salto de línea distinto, un cambio de codificación o una re-serialización gritan «manipulado»
sin que nadie haya manipulado nada, y la primera falsa alarma enseña al operador a ignorar la
alarma. Se ancla el resumen de los **cuerpos canónicos** — `libro_cadena.cuerpo_firmable()`,
que ya existe y ordena las claves. Es inmune a re-serialización, y a diferencia de anclar la
secuencia de `hash` de fila (que era la propuesta del disidente) **cubre también las 50 filas
del prefijo**, que no tienen `hash`, y **los campos del envoltorio** (`dictamen`, `veredicto`,
`ts`), que ninguna firma cubre.

QUÉ CIERRA Y QUÉ NO, sin adornos:

  ✓ truncar el final del libro           — hasta el último ancla
  ✓ borrar una de las 50 filas del prefijo sin encadenar
  ✓ alterar `dictamen`, `veredicto` o `ts` — hasta el último ancla
  ✗ lo escrito DESPUÉS del último ancla: sigue siendo truncable, y el verificador lo dice
  ✗ AÑADIR filas falsas: eso no lo gobierna el ancla, lo gobierna la puerta
    (`servicio/mediador.py` + `agente/killtest_puerta.py`, 7 cierres forjados rechazados)
  ✗ un truncamiento anterior al PRIMER ancla: no hay ancla previa contra la que compararlo.
    Ventana única y de una sola vez, que se cierra emitiendo el primer ancla
  ✗ BORRAR el archivo de anclas entero: dentro del archivo eso es indistinguible del día uno,
    cuando todavía no había ancla. Lo distingue el historial de git, no la criptografía. El
    ancla no impide que la borren: convierte un ataque silencioso en uno ruidoso

Búsqueda previa antes de crear este archivo: `grep -rn 'ancla\|checkpoint\|truncam' src/
agente/` no devuelve ningún mecanismo — solo la frase de `agente/killtest_libro_encadenado.py`
que DECLARA la brecha sin cerrarla. `src/libro_cadena.py` es continuidad dentro del archivo,
que es justo lo que no alcanza. `src/verificar_kms.py` verifica sobres de decisión, no libros.
No había dónde anexar esto.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src import libro_cadena                                          # noqa: E402

CLAVE_ANCLA = "clave-humano"   # la que el agente NO alcanza: ahí está toda la seguridad
TIPO = "ancla_libro"


# --- El resumen que se firma ------------------------------------------------------------

def resumen_canonico(filas: list[dict]) -> str:
    """sha256 de los cuerpos canónicos de las filas, en orden.

    `cuerpo_firmable` ordena las claves y quita las anotaciones del lector, así que dos
    lecturas de la misma fila dan lo mismo aunque el archivo se re-serialice. Cubre TODOS los
    campos de la fila —incluidos los del envoltorio que ninguna firma cubre— y también las
    filas de prefijo, que no tienen `hash` propio.

    LAS FILAS ILEGIBLES VAN POR SU TEXTO CRUDO, y esto lo encontró la fase cero EJECUTANDO, no
    leyendo. `filas_crudas` devuelve una línea que no es JSON como `{"_ilegible": ..., "_crudo":
    ...}`, y `cuerpo_firmable` descarta TODA clave que empiece por `_` — con razón, porque son
    anotaciones que pone el lector. El efecto combinado era que dos líneas ilegibles
    completamente distintas resumían igual (a `{}`), así que dentro de lo anclado se podía
    cambiar una basura por otra basura sin que nada se enterara. Se resume el texto crudo.
    """
    h = hashlib.sha256()
    for fila in filas:
        if "_ilegible" in fila:
            h.update(("_crudo:" + str(fila.get("_crudo", ""))).encode("utf-8"))
        else:
            h.update(libro_cadena.cuerpo_firmable(fila).encode("utf-8"))
        h.update(b"\n")
    return "sha256:" + h.hexdigest()


def hash_sobre(sobre: dict) -> str:
    """El identificador de un ancla: resumen de su sobre canónico. Es lo que encadena."""
    return hashlib.sha256(canonico(sobre)).hexdigest()[:16]


def canonico(sobre: dict) -> bytes:
    """La misma serialización que firma el resto del sistema (`src/verificar_kms.canonico`)."""
    return json.dumps(sobre, sort_keys=True, separators=(",", ":")).encode()


# --- Construir --------------------------------------------------------------------------

def leer_anclas(ruta_ancla) -> list[dict]:
    ruta_ancla = pathlib.Path(ruta_ancla)
    if not ruta_ancla.exists():
        return []
    anclas = []
    for linea in ruta_ancla.read_text(encoding="utf-8").splitlines():
        if linea.strip():
            anclas.append(json.loads(linea))
    return anclas


def construir(libro, ruta_ancla) -> dict:
    """El sobre que hay que firmar para anclar el libro tal como está AHORA.

    No firma nada: construirlo es lo que puede hacer cualquiera, firmarlo es lo que no.
    """
    libro = pathlib.Path(libro)
    filas = libro_cadena.filas_crudas(libro)
    ultima = filas[-1] if filas else {}
    anclas = leer_anclas(ruta_ancla)
    return {
        "tipo": TIPO,
        "libro": libro.name,
        "filas": len(filas),
        "n_ultima": ultima.get("n"),
        "hash_ultima": str(ultima.get("hash") or ""),
        "sha256_canonico": resumen_canonico(filas),
        "ancla_previa": hash_sobre(anclas[-1]["sobre"]) if anclas else "",
        "marca_temporal": int(__import__("time").time()),
    }


def anexar_ancla(ruta_ancla, sobre: dict, firma_b64: str,
                 clave: str = CLAVE_ANCLA) -> dict:
    """Anexa el ancla firmada. NUNCA sobrescribe: cada ancla es una fila más.

    Un historial de anclas deja que el auditor verifique el libro en cualquier punto del
    pasado, y hace que borrar «el ancla» sea borrar filas visibles en el historial de git en
    vez de reemplazar un archivo.
    """
    ruta_ancla = pathlib.Path(ruta_ancla)
    ruta_ancla.parent.mkdir(parents=True, exist_ok=True)
    fila = {"sobre": sobre, "firma": firma_b64, "clave": clave,
            "hash_sobre": hash_sobre(sobre)}
    datos = (json.dumps(fila, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(str(ruta_ancla), os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o600)
    try:
        escrito = 0
        while escrito < len(datos):
            escrito += os.write(fd, datos[escrito:])
        os.fsync(fd)
    finally:
        os.close(fd)
    return fila


# --- Verificar --------------------------------------------------------------------------

def _clave_publica(dir_claves, nombre):
    from cryptography.hazmat.primitives.serialization import load_pem_public_key
    return load_pem_public_key(
        (pathlib.Path(dir_claves) / f"{nombre}.pem").read_bytes())


def _firma_valida(pub, sobre: dict, firma_b64: str) -> bool:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
    try:
        pub.verify(base64.b64decode(firma_b64),
                   hashlib.sha256(canonico(sobre)).digest(),
                   ec.ECDSA(Prehashed(hashes.SHA256())))
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


def verificar(libro, ruta_ancla, dir_claves="claves", exigir_ancla: bool = True) -> dict:
    """¿Está el libro completo hasta el último ancla? Y si no, DE QUÉ CLASE es la ruptura.

    `clase` distingue las seis cosas que si no saldrían todas como «no cuadra»:
      · `integro`      — el libro contiene, íntegro y en orden, todo lo que las anclas firman.
      · `sin_ancla`    — no hay ninguna ancla. Con `exigir_ancla` (el defecto, fail-closed) es
                         un fallo: un libro con filas y sin ancla no puede declararse completo.
                         Y hay que decirlo con su nombre: esto es indistinguible de que alguien
                         BORRARA las anclas. Lo distingue el historial de git, no este código.
      · `firma_invalida` — un ancla no la firmó `clave-humano`. Es el caso de alguien que
                         fabricó un ancla con otra llave: lo único que el 403 hace imposible.
      · `ancla_rota`   — la cadena de anclas no cuadra: falta una, o la reordenaron.
      · `regresion`    — un ancla declara MENOS filas que la anterior. Es la firma del ataque
                         del diputado confundido: truncar el libro y anclar lo que queda.
      · `faltan_filas` — el libro tiene menos filas que las que un ancla firma. Y el nombre es
                         deliberadamente ese y no «truncado»: el ancla prueba que FALTAN, no
                         DÓNDE faltaban. Cortadas del final o borradas del medio dan lo mismo
                         aquí, y decir «le cortaron el final» sería afirmar más de lo que la
                         medición sostiene. Que falten es lo que ninguna cadena podía ver.
      · `alterado`     — el libro tiene las filas, pero el prefijo anclado ya no resume igual:
                         alguien cambió algo dentro de lo anclado, envoltorio incluido.
    """
    libro = pathlib.Path(libro)
    # Una ruta que es un directorio reventaba con el traceback crudo de `read_text` (fase cero).
    # Fallaba cerrado, que es lo importante, pero un verificador que un auditor va a correr no
    # puede contestar con una traza de Python.
    for etiqueta, ruta in (("el libro", libro), ("el ancla", pathlib.Path(ruta_ancla))):
        if ruta.is_dir():
            return {"ok": False, "clase": "ruta_invalida", "libro": str(libro),
                    "ancla": str(ruta_ancla), "roto_en": None,
                    "mensaje": f"{etiqueta} apunta a un directorio, no a un archivo: {ruta}"}
    filas = libro_cadena.filas_crudas(libro)
    anclas = leer_anclas(ruta_ancla)
    res = {"ok": True, "clase": "integro", "mensaje": "", "libro": str(libro),
           "ancla": str(ruta_ancla), "filas_libro": len(filas), "anclas": len(anclas),
           "filas_ancladas": 0, "filas_fuera_del_ancla": len(filas), "roto_en": None}

    if not anclas:
        res.update(ok=not exigir_ancla, clase="sin_ancla",
                   mensaje=(f"el libro tiene {len(filas)} filas y NINGUNA ancla: no se puede "
                            f"decir que esté completo. Y esto es indistinguible de que "
                            f"alguien borrara {ruta_ancla}: lo distingue el historial de git"))
        return res

    try:
        pub = _clave_publica(dir_claves, CLAVE_ANCLA)
    except Exception as e:                                            # noqa: BLE001
        res.update(ok=False, clase="sin_ancla",
                   mensaje=f"no pude cargar la clave pública {CLAVE_ANCLA}: {e}")
        return res

    previo_hash = ""
    previo_filas = 0
    for i, a in enumerate(anclas, start=1):
        sobre = a.get("sobre") or {}

        if not _firma_valida(pub, sobre, a.get("firma", "")):
            res.update(ok=False, clase="firma_invalida", roto_en=i,
                       mensaje=(f"el ancla {i} NO la firmó {CLAVE_ANCLA}. Fabricar un ancla es "
                                f"exactamente lo que el 403 de IAM hace imposible al agente"))
            return res

        if str(sobre.get("ancla_previa", "")) != previo_hash:
            res.update(ok=False, clase="ancla_rota", roto_en=i,
                       mensaje=(f"el ancla {i} dice venir de {sobre.get('ancla_previa')!r} y la "
                                f"anterior es {previo_hash!r}: falta un ancla o las reordenaron"))
            return res

        n = int(sobre.get("filas", 0))
        if n < previo_filas:
            res.update(ok=False, clase="regresion", roto_en=i,
                       mensaje=(f"el ancla {i} firma {n} filas y la anterior firmaba "
                                f"{previo_filas}: un libro no encoge. Alguien truncó el libro "
                                f"y ancló lo que quedó"))
            return res

        if len(filas) < n:
            res.update(ok=False, clase="faltan_filas", roto_en=i, filas_ancladas=previo_filas,
                       mensaje=(f"el ancla {i} firma {n} filas y el libro tiene {len(filas)}: "
                                f"FALTAN {n - len(filas)}. Cortadas del final o borradas del "
                                f"medio: el ancla prueba que faltan, no dónde faltaban — y "
                                f"que falten es justo lo que la cadena sola no puede ver"))
            return res

        ilegibles = [f.get("_linea") for f in filas[:n] if "_ilegible" in f]
        if ilegibles:
            # Fail-closed. El resumen ya cubre estas filas por su texto crudo, así que una
            # sustitución se detectaría igual; pero una línea que no es JSON DENTRO de lo
            # anclado es de por sí una señal de daño, y decir «íntegro» sobre un libro que el
            # lector no puede leer entero sería mentir con la verdad técnica de la mano.
            res.update(ok=False, clase="ilegible_en_ancla", roto_en=ilegibles[0],
                       filas_ancladas=previo_filas,
                       mensaje=(f"dentro de lo que el ancla {i} firma hay {len(ilegibles)} "
                                f"línea(s) que no son JSON (la primera, en la "
                                f"{ilegibles[0]}): el libro no se puede declarar íntegro"))
            return res

        esperado = resumen_canonico(filas[:n])
        if esperado != sobre.get("sha256_canonico"):
            res.update(ok=False, clase="alterado", roto_en=i, filas_ancladas=previo_filas,
                       mensaje=(f"las primeras {n} filas del libro ya no resumen lo que el "
                                f"ancla {i} firmó: algo cambió dentro de lo anclado "
                                f"(el envoltorio cuenta)"))
            return res

        previo_hash = hash_sobre(sobre)
        previo_filas = n

    res["filas_ancladas"] = previo_filas
    res["filas_fuera_del_ancla"] = len(filas) - previo_filas
    res["mensaje"] = (
        f"libro completo hasta el ancla: {previo_filas} filas ancladas por {len(anclas)} "
        f"ancla(s) de {CLAVE_ANCLA}, + {res['filas_fuera_del_ancla']} fila(s) FUERA del ancla. "
        f"Lo anclado no se puede truncar sin que se note; lo de fuera del ancla, SÍ")
    return res


# --- Línea de comandos ------------------------------------------------------------------

def _uso():
    print("uso: ancla.py verificar <libro.jsonl> <ancla.jsonl> [dir_claves]\n"
          "     ancla.py construir <libro.jsonl> <ancla.jsonl>   (imprime el sobre a firmar)\n"
          "     ancla.py firmar    <libro.jsonl> <ancla.jsonl>   (pide la firma a Cloud KMS)",
          file=sys.stderr)
    raise SystemExit(2)


def main(argv):
    if len(argv) < 3:
        _uso()
    orden, libro, ruta_ancla = argv[0], argv[1], argv[2]

    if orden == "construir":
        print(json.dumps(construir(libro, ruta_ancla), ensure_ascii=False, indent=2))
        return 0

    if orden == "firmar":
        # Esto FALLA a propósito cuando lo corre el agente, y el fallo es el argumento entero
        # del producto: HTTP 403 PERMISSION_DENIED sobre `clave-humano`. Quien escribe el libro
        # no puede firmar lo que lo audita.
        from src import firma_kms
        sobre = construir(libro, ruta_ancla)
        r = firma_kms.firmar(CLAVE_ANCLA, sobre)
        if r.get("http") != 200:
            print(json.dumps({"ancla": "NO EMITIDA", **r}, ensure_ascii=False, indent=2))
            return 3
        anexar_ancla(ruta_ancla, sobre, r["firma"])
        print(json.dumps({"ancla": "emitida", "filas": sobre["filas"],
                          "hash_sobre": hash_sobre(sobre)}, ensure_ascii=False, indent=2))
        return 0

    if orden == "verificar":
        r = verificar(libro, ruta_ancla, argv[3] if len(argv) > 3 else "claves")
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0 if r["ok"] else 2

    _uso()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
