#!/usr/bin/env python3
"""La cadena de continuidad del libro de firmas: cada fila lleva el resumen de la anterior.

QUÉ PROBLEMA CIERRA, y es uno que el paquete de entrega tenía abierto y medido. Hasta hoy
`libro/firmas_grafo.jsonl` anotaba una fila por operación y **ninguna apuntaba a la anterior**:

    $ python3 -c "import json; f=[json.loads(l) for l in open('libro/firmas_grafo.jsonl') if l.strip()]; print(len(f), sorted(f[0]))"
    50 ['dictamen', 'firma', 'peticion_id', 'sobre', 'ts', 'veredicto']

Se podía borrar una fila entera y las otras 49 seguían verificando, porque cada firma solo
cubre su propio sobre. El libro probaba que **lo que hay es auténtico**; no probaba que
**esté todo lo que hubo**. Con la cadena, el verificador puede decir una frase que antes no
podía: *el libro está completo*.

DE DÓNDE SALE. Esto NO se diseñó aquí: es un port de `tools/cierre/libro_cadena.py` del
repositorio `cleveria-dominios`, que lleva funcionando sobre libros vivos y trae pagados
varios errores que aquí no hay que volver a cometer. Se conservan sus garantías y sus
comentarios de por qué. Búsqueda previa antes de crear este archivo: `grep -rn 'flock\\|LOCK_EX\\|
hashlib' src/ agente/` no devuelve ningún candado ni ningún encadenamiento; `src/canonico.py`
es JSON canónico RFC 8785 para FIRMAR un sobre, que es otra cosa (autenticidad de una
decisión, no continuidad de un libro); `src/libro_demo.py` anexaba sin candado ni cadena. No
había dónde anexar esto.

ÚNICA ADAPTACIÓN RESPECTO DEL ORIGINAL. Allá el libro es un *directorio*
(`<dir>/narrativa.jsonl` + `<dir>/ultimo.json` + `<dir>/.lock`). Aquí el libro es **un archivo
suelto** cuya ruta está publicada en el README, en `REVISION_JURADO.md` y en tres kill-tests,
así que no se mueve ni se renombra: la biblioteca toma **ruta de archivo** y deriva sus
auxiliares al lado (`<archivo>.lock`, `<archivo>.ultimo.json`, `<archivo>.parcial.<pid>`).

QUÉ GARANTIZA, que es lo único que cuenta:

1. Nadie escribe a la vez — candado exclusivo (`flock`) tomado ANTES de leer la cabeza y
   soltado DESPUÉS de escribir. Leer el hash previo y escribir la fila TIENEN que ocurrir bajo
   el mismo candado: si se leyera fuera, dos escritores leerían el mismo `prev` y los dos
   creerían ser el siguiente.
2. Nadie escribe media línea — la fila se compone entera en memoria y sale en UNA sola llamada
   `write(2)` terminada en salto de línea. Un proceso muerto a mitad deja el archivo íntegro.
3. El candado no cuelga el proceso y TAMPOCO degrada a escribir sin candado. Si no se consigue
   dentro del presupuesto, la fila va a `<archivo>.parcial.<pid>.jsonl` —uno por escritor— y
   **nunca entra en la cadena**, así que la cadena no se bifurca y la fila no se pierde.
4. El archivo es la fuente de verdad; la cache es solo velocidad. Bajo candado se comprueba que
   el hash cacheado ES el de la última línea; si no, se recalcula leyendo el archivo.

QUÉ **NO** GARANTIZA, y hay que decirlo con su nombre: esto da **continuidad**, no
autenticidad de la cadena. Detecta que alguien borró, reordenó o alteró una fila. NO impide
que quien pueda escribir el archivo recalcule la cadena entera y reescriba la cache: para eso
haría falta un secreto que la cadena no tiene. Por eso `prev` va cubierto por `hash`, y no se
le llama "firma": la firma ECDSA del sobre sigue siendo la que prueba autenticidad de cada
decisión, y esas dos cosas son distintas a propósito.

ALCANCE, declarado en vez de fingido: la cadena cubre **el archivo**. `src/libro_demo.py`
escribe en Firestore cuando hay credenciales, y `flock` no sirve entre instancias de Cloud
Run. Firestore queda FUERA de la cadena en esta versión, y el verificador lo dice.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import time
from pathlib import Path

PRESUPUESTO_S = 10.0  # tope de espera por el candado antes de desviar a parcial
ESPERA_S = 0.02       # entre reintentos del candado


def _lock(ruta: Path) -> Path:
    return ruta.with_name(ruta.name + ".lock")


def _cache(ruta: Path) -> Path:
    return ruta.with_name(ruta.name + ".ultimo.json")


def _parcial(ruta: Path) -> Path:
    return ruta.with_name(f"{ruta.name}.parcial.{os.getpid()}.jsonl")


# --- La cadena --------------------------------------------------------------------------

def cuerpo_firmable(fila: dict) -> str:
    """El cuerpo que se resume: la fila sin su propio `hash`, con las claves ORDENADAS.

    Las claves ordenadas no son cosmética: sin ellas dos ejecuciones dan resúmenes distintos
    para la misma fila y la cadena se rompe sola. El `hash` se excluye porque no puede
    resumirse a sí mismo.

    Y se excluye TODO lo que empieza por `_`: son anotaciones que ponen los lectores al cargar
    la fila (`_linea`, `_archivo`), no contenido del libro. Sin esta exclusión el verificador
    resumía la fila CON la anotación que él mismo acababa de añadir y daba por alterada una
    fila recién escrita.
    """
    return json.dumps({k: v for k, v in fila.items()
                       if k != "hash" and not str(k).startswith("_")},
                      ensure_ascii=False, sort_keys=True)


def hash_de(prev: str, fila: dict) -> str:
    return hashlib.sha256((prev + cuerpo_firmable(fila)).encode("utf-8")).hexdigest()[:16]


# --- Lectura ----------------------------------------------------------------------------

def filas_crudas(ruta: Path) -> list[dict]:
    """Las filas del archivo, cada una con su número de línea real en `_linea`.

    Una línea ilegible NO se descarta en silencio: se devuelve como `{"_ilegible": ...}` para
    que el verificador la nombre. Descartarla sería perder exactamente el caso que la cadena
    viene a detectar.
    """
    ruta = Path(ruta)
    if not ruta.exists():
        return []
    filas = []
    for i, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), start=1):
        if not linea.strip():
            continue
        try:
            fila = json.loads(linea)
            if not isinstance(fila, dict):
                raise ValueError("la fila no es un objeto")
        except Exception as e:                                   # noqa: BLE001
            fila = {"_ilegible": str(e), "_crudo": linea[:200]}
        fila["_linea"] = i
        filas.append(fila)
    return filas


def _cabeza(ruta: Path) -> tuple[int, str]:
    """(n de la última fila, hash de la última fila) — llamar SIEMPRE bajo candado.

    Usa la cache solo si coincide con la última línea real del archivo. El archivo manda.
    """
    filas = filas_crudas(ruta)
    if not filas:
        return 0, ""
    ultima = filas[-1]
    n = int(ultima.get("n") or len(filas))
    h = str(ultima.get("hash") or "")
    cache = _cache(ruta)
    if cache.exists():
        try:
            c = json.loads(cache.read_text(encoding="utf-8"))
            if c.get("hash") != h or int(c.get("n", -1)) != n:
                # La cache miente (proceso muerto entre escribir y actualizarla, o alguien la
                # tocó). Se reescribe con lo que dice el archivo, que es la fuente de verdad.
                cache.write_text(json.dumps({"n": n, "hash": h}), encoding="utf-8")
        except Exception:                                        # noqa: BLE001
            cache.write_text(json.dumps({"n": n, "hash": h}), encoding="utf-8")
    return n, h


# --- Escritura --------------------------------------------------------------------------

def _escribe_de_una_vez(ruta: Path, linea: str) -> None:
    """Anexa la línea con UN solo `write(2)`, no con el `write` con buffer de Python.

    `f.write` puede dividirse en varios `write(2)` si la línea es grande; un lector concurrente
    ve media línea y un corte deja el archivo truncado. Aquí se baja al descriptor. El candado
    ya serializa a los ESCRITORES; esto protege al LECTOR, que lee sin candado a propósito para
    no frenar a nadie.

    El modo 0o600 solo aplica al archivo que NO existe: sobre el libro ya versionado el modo no
    cambia (medido en fase cero: archivo existente se queda en -rw-r--r--).
    """
    datos = linea.encode("utf-8")
    fd = os.open(str(ruta), os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o600)
    try:
        escrito = 0
        while escrito < len(datos):
            escrito += os.write(fd, datos[escrito:])
        os.fsync(fd)
    finally:
        os.close(fd)


def _a_parcial(ruta: Path, fila: dict) -> dict:
    """No se consiguió el candado: la fila se guarda SIN entrar en la cadena.

    Un archivo por escritor, así que no hay carrera posible. Se marca fuera de cadena para que
    quien lea el libro no la cuente como encadenada.
    """
    fila = dict(fila)
    fila["fuera_de_cadena"] = True
    fila["motivo_fuera"] = "candado no adquirido dentro del presupuesto"
    _escribe_de_una_vez(_parcial(ruta),
                        json.dumps(fila, ensure_ascii=False, sort_keys=True) + "\n")
    return fila


def anexar(ruta, fila: dict, presupuesto_s: float = PRESUPUESTO_S) -> dict:
    """Anexa una fila a la cadena del archivo. Devuelve la fila escrita (con `n`, `prev`, `hash`).

    Si no consigue el candado dentro del presupuesto, devuelve la fila con
    `fuera_de_cadena: True` — nunca escribe sin candado en la cadena principal.
    """
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    inicio = time.monotonic()
    fd = os.open(str(_lock(ruta)), os.O_CREAT | os.O_RDWR, 0o600)
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() - inicio >= presupuesto_s:
                    return _a_parcial(ruta, fila)
                time.sleep(ESPERA_S)
        # --- sección crítica: leer cabeza y escribir son inseparables ---
        n, prev = _cabeza(ruta)
        cuerpo = {k: v for k, v in fila.items()
                  if not str(k).startswith("_") and k != "hash"}
        cuerpo["n"] = n + 1
        cuerpo["prev"] = prev
        cuerpo["hash"] = hash_de(prev, cuerpo)
        _escribe_de_una_vez(ruta,
                            json.dumps(cuerpo, ensure_ascii=False, sort_keys=True) + "\n")
        try:
            _cache(ruta).write_text(
                json.dumps({"n": cuerpo["n"], "hash": cuerpo["hash"]}), encoding="utf-8")
        except Exception:                                        # noqa: BLE001
            pass   # la cache es velocidad, no verdad: si no se puede escribir, no importa
        return cuerpo
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


# --- Verificación -----------------------------------------------------------------------

def verificar(ruta, tolerar_convivencia: bool = False) -> dict:
    """Recorre la cadena y dice si cuadra, y si no, EN QUÉ LÍNEA se rompió y DE QUÉ CLASE.

    Regla de génesis: las filas anteriores a la primera que trae `hash` se tratan como
    **prefijo declarado** — se cuentan y se dicen, pero no se les exige cadena. Sin esta regla
    el verificador rechazaría el libro entero, porque este libro tiene 50 filas escritas antes
    de que la cadena existiera. Un libro que empieza a encadenar a mitad NO PUEDE declarar
    completo lo anterior, y eso se declara en vez de fingirse.

    `clase` distingue las cinco cosas que si no saldrían todas como «no cuadra»:
      · `integra`      — cuadra.
      · `convivencia`  — la cadena empezó y después hay filas SIN hash. Es un escritor viejo
                         suelto (un despliegue a medias), no un incidente: se arregla
                         migrando el escritor, no reparando el archivo.
      · `alterada`     — una fila encadenada no resume lo que dice, o su `prev` no cuadra.
                         Esto SÍ es lo que la cadena existe para detectar: borrado, reordenado
                         o edición de una fila.
      · `ilegible`     — una línea que no es JSON.
      · `ausente`      — no hay archivo. Antes esto devolvía «cadena íntegra» y salida cero, y
                         es grave por dónde está: el OK de este verificador es la llave de
                         leer el libro. Cero filas CON archivo presente es legítimo (libro
                         recién creado); cero filas PORQUE NO HAY archivo, no.
    """
    ruta = Path(ruta)
    filas = filas_crudas(ruta)
    res = {"ok": True, "roto_en": None, "mensaje": "", "prefijo": 0, "encadenadas": 0,
           "total": len(filas), "ruta": str(ruta), "clase": "integra",
           "prefijo_tardio": 0, "tramos": 0}

    if not ruta.exists():
        res.update(ok=False, clase="ausente",
                   mensaje=f"no encontré el libro en {ruta}: no hay nada que verificar, "
                           f"y eso NO es una cadena íntegra")
        return res

    prev = ""
    empezo = False
    for fila in filas:
        linea = fila.get("_linea")
        if "_ilegible" in fila:
            res.update(ok=False, clase="ilegible", roto_en=linea,
                       mensaje=f"la línea {linea} no es JSON legible: {fila['_ilegible']}")
            return res
        if not empezo:
            if "hash" not in fila:
                res["prefijo"] += 1
                continue
            empezo = True          # desde aquí se exige cadena
            res["tramos"] += 1
        if "hash" not in fila:
            if tolerar_convivencia:
                res["clase"] = "convivencia"
                res["prefijo_tardio"] += 1
                res["roto_en"] = res["roto_en"] or linea
                prev, empezo = "", False
                continue
            res.update(ok=False, clase="convivencia", roto_en=linea,
                       mensaje=f"la fila n={fila.get('n')} (línea {linea}) no trae hash y la "
                               f"cadena ya había empezado")
            return res
        if str(fila.get("prev", "")) != prev:
            res.update(ok=False, clase="alterada", roto_en=linea,
                       mensaje=f"la fila n={fila.get('n')} (línea {linea}) dice venir de "
                               f"prev={fila.get('prev')!r} y la anterior es {prev!r}: la "
                               f"cadena está cortada, reordenada o bifurcada ahí")
            return res
        esperado = hash_de(prev, fila)
        if esperado != fila["hash"]:
            res.update(ok=False, clase="alterada", roto_en=linea,
                       mensaje=f"la fila n={fila.get('n')} (línea {linea}) fue ALTERADA: su "
                               f"contenido resume {esperado} y la fila dice {fila['hash']}")
            return res
        prev = fila["hash"]
        res["encadenadas"] += 1

    if res["clase"] == "convivencia":
        res["mensaje"] = (
            f"CONVIVENCIA DE ESCRITORES: {res['encadenadas']} filas encadenadas en "
            f"{res['tramos']} tramo(s) + {res['prefijo']} de prefijo + "
            f"{res['prefijo_tardio']} fila(s) escritas por un escritor SIN cadena después de "
            f"que la cadena empezara (primera en la línea {res['roto_en']}). Ningún tramo está "
            f"alterado. Esto se arregla migrando el escritor, no reparando el archivo")
        return res
    res["mensaje"] = (f"cadena íntegra: {res['encadenadas']} filas encadenadas"
                      f" + {res['prefijo']} de prefijo declarado (anteriores a la cadena)")
    return res


def parciales(ruta) -> list[dict]:
    """Las filas que no pudieron entrar en la cadena, ordenadas por marca de tiempo."""
    ruta = Path(ruta)
    filas: list[dict] = []
    for p in sorted(ruta.parent.glob(f"{ruta.name}.parcial.*.jsonl")):
        for fila in filas_crudas(p):
            fila["_archivo"] = p.name
            filas.append(fila)
    return sorted(filas, key=lambda f: str(f.get("ts", "")))


if __name__ == "__main__":
    import sys
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if len(args) != len(sys.argv[1:]) or len(args) != 1:
        # Invocarlo con `--dir <ruta>` hacía que `sys.argv[1]` fuera la cadena literal
        # `--dir`, y el verificador aprobaba esa "ruta" inexistente.
        print("uso: libro_cadena.py <archivo del libro .jsonl>", file=sys.stderr)
        raise SystemExit(2)
    r = verificar(Path(args[0]), tolerar_convivencia=True)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    raise SystemExit(0 if r["ok"] else 2)
