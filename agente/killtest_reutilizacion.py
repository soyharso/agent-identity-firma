#!/usr/bin/env python3
"""KILL-TEST — una aprobación auténtica, movida al expediente de al lado.

CUÁNDO IMPORTA ESTO, Y CUÁNDO NO. Hay que decirlo con precisión, porque la
primera versión de este kill-test probaba el caso fácil y se vendía como si
probara el difícil.

  · Si el texto del otro caso es DISTINTO, este control no aporta nada: el hash
    canónico ya no cuadra y `CONTENIDO_ALTERADO` rechaza el sobre solo. Quien
    diga que la reutilización «ya estaba cubierta» tiene razón en este escenario.

  · Si el texto del otro caso es EL MISMO, el hash cuadra, `CONTENIDO_ALTERADO`
    se queda mudo, y el sobre pasa entero: firma auténtica, firmante conocido,
    estado dentro de alcance, contenido que coincide. Lo único que separa un
    expediente de otro es el identificador de la petición.

Y el segundo escenario no es rebuscado: es el normal. En atención al cliente las
resoluciones son de plantilla. «Se descarta la queja del cliente: revisando el
historial, el error fue suyo» aparece idéntica en cientos de expedientes, y en
este mismo repositorio ya ocurre — el sobre firmado para PET-002 tiene el hash
del texto de PET-004, porque son la misma frase.

Un agente que quiere bajar su cola de pendientes no necesita romper nada: le
basta con reciclar una aprobación que ya existe hacia otro caso con la misma
resolución de plantilla.

TERCER ESCENARIO, y es la frontera del verificador: si quien verifica no aporta
ni el texto ni el expediente, el sobre pasa. No es un agujero escondido — es que
el contexto lo pone quien verifica, nunca el propio sobre. Un sobre que se
autocertifica no certifica nada. Se comprueba aquí para que nadie lo descubra
después.

Uso: python3 agente/killtest_reutilizacion.py
Sin red y sin credenciales.
"""
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.verificar_sobre import cargar_directorio, verificar  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
VERDE, ROJO, GRIS, FIN = "\033[32m", "\033[31m", "\033[2m", "\033[0m"


def sobre_humano_del_libro(directorio):
    """El sobre real más reciente firmado por una persona, del libro del repositorio."""
    libro = RAIZ / "libro" / "firmas_grafo.jsonl"
    for linea in reversed(libro.read_text(encoding="utf-8").splitlines()):
        if not linea.strip():
            continue
        fila = json.loads(linea)
        sobre, firma = fila.get("sobre"), fila.get("firma")
        if not sobre or not firma:
            continue
        if verificar(sobre, firma, directorio=directorio)[0] == "OK":
            return sobre, firma
    return None, None


def texto_que_casa(sobre):
    """El texto de `libro/peticiones.json` cuyo hash coincide con el del sobre.

    No se elige a mano: se busca. Así el kill-test no depende de que alguien
    recuerde qué petición llevaba qué frase.
    """
    peticiones = json.loads((RAIZ / "libro" / "peticiones.json").read_text(encoding="utf-8"))
    for pid, p in peticiones.items():
        if pid.startswith("_"):
            continue
        h = "sha256:" + hashlib.sha256(p["texto"].encode()).hexdigest()
        if sobre["hash_contenido"] in (h, h.removeprefix("sha256:")):
            return pid, p["texto"]
    return None, None


def texto_distinto(excluye_pid):
    peticiones = json.loads((RAIZ / "libro" / "peticiones.json").read_text(encoding="utf-8"))
    for pid, p in peticiones.items():
        if not pid.startswith("_") and pid != excluye_pid:
            return pid, p["texto"]
    return None, None


def main():
    directorio = cargar_directorio()
    sobre, firma = sobre_humano_del_libro(directorio)
    if sobre is None:
        sys.exit("No hay ningún sobre válido en libro/firmas_grafo.jsonl con el que probar.")

    caso_firmado = sobre["peticion_id"]
    pid_origen, texto_plantilla = texto_que_casa(sobre)
    if texto_plantilla is None:
        sys.exit("No encuentro en libro/peticiones.json el texto que este sobre firmó.")

    _, texto_otro = texto_distinto(pid_origen)

    # El expediente hermano: otra reclamación, misma resolución de plantilla. No hace
    # falta firmarlo ni inventar nada — el sobre sigue siendo el auténtico; lo único
    # que cambia es EN QUÉ EXPEDIENTE se presenta.
    caso_hermano = "PET-777"

    print(f"\n  Aprobación humana auténtica, firmada para {GRIS}{caso_firmado}{FIN}.")
    print(f"  Texto de plantilla: {GRIS}«{texto_plantilla[:56]}…»{FIN}")
    print(f"  Un agente la recicla hacia {GRIS}{caso_hermano}{FIN}, otra reclamación "
          f"con la misma resolución.\n")

    fallos = 0

    def paso(etiqueta, esperado, **kw):
        nonlocal fallos
        v, d = verificar(sobre, firma, directorio=directorio, **kw)
        ok = v == esperado
        fallos += not ok
        marca = VERDE + "✓" + FIN if ok else ROJO + "✗" + FIN
        print(f"  {marca} {etiqueta:<46} → {v}")
        return v, d

    # A · El caso fácil, el que ya estaba cubierto. Se prueba para poder decir
    #     con datos que aquí el control nuevo NO aporta nada.
    print(f"  {GRIS}A · reutilizado donde el texto es DISTINTO — ya lo cazaba el hash{FIN}")
    paso("sin declarar expediente", "CONTENIDO_ALTERADO", texto_actual=texto_otro)

    # B · El caso que justifica el control. Mismo texto, otro expediente.
    print(f"\n  {GRIS}B · reutilizado donde el texto es EL MISMO — aquí el hash es ciego{FIN}")
    v, _ = paso("sin declarar expediente", "OK", texto_actual=texto_plantilla)
    if v == "OK":
        print(f"      {ROJO}↑ pasa: firma válida, firmante conocido, hash correcto{FIN}")
    _, d = paso("declarando el expediente real", "CONTEXTO_AJENO",
                texto_actual=texto_plantilla, peticion_esperada=caso_hermano)
    if d.get("firmado_para"):
        print(f"      {GRIS}firmado para {d['firmado_para']}, presentado en "
              f"{d['presentado_en']} — {d['por_que']}{FIN}")

    # C · En su propio expediente tiene que pasar. Si no, el control sería inútil
    #     por rechazarlo todo, que es la forma más fácil de aparentar rigor.
    print(f"\n  {GRIS}C · en su propio expediente debe seguir valiendo{FIN}")
    paso("declarando su expediente", "OK", peticion_esperada=caso_firmado)

    print()
    if fallos:
        print(f"  {ROJO}VEREDICTO: FALLA — {fallos} comprobación(es) en rojo{FIN}\n")
        sys.exit(1)
    print(f"  {VERDE}VEREDICTO: PASA{FIN} — con texto de plantilla, el hash no distingue "
          f"expedientes\n  y el vínculo al caso es lo único que para el fraude.\n")


if __name__ == "__main__":
    main()
