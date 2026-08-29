#!/usr/bin/env python3
"""KILL-TEST — una firma auténtica, presentada en el caso de al lado, sigue siendo falsa.

De los tres intentos que hace un agente con el objetivo mal puesto, este es el más plausible,
porque NO exige romper nada. No hay que falsificar una clave ni alterar un byte: basta con
copiar una aprobación humana que ya existe y presentarla en otro expediente. Un agente que
quiere bajar su cola de pendientes y ya vio a la supervisora conceder una excepción parecida
tiene todos los incentivos para reutilizarla, y ningún incentivo para notar la diferencia.

Y es el que más silenciosamente pasa, porque supera todas las demás comprobaciones:

  · la firma es criptográficamente válida — la hizo la persona, de verdad
  · el firmante está en el directorio y es del tipo correcto
  · el estado destino está dentro del alcance de esa clave
  · el hash del contenido cuadra, porque el atacante copia también el contenido

Lo único que delata el fraude es que aquella aprobación NO ERA PARA ESTE CASO. Por eso el
vínculo al expediente no puede leerse del propio sobre: lo pone quien verifica, desde el
expediente que tiene delante. Un sobre que se autocertifica no certifica nada.

Uso: python3 agente/killtest_reutilizacion.py
Sin red y sin credenciales.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.verificar_sobre import cargar_directorio, verificar  # noqa: E402

VERDE, ROJO, GRIS, FIN = "\033[32m", "\033[31m", "\033[2m", "\033[0m"


def buscar_sobre_humano(directorio):
    """El sobre real más reciente firmado por una persona, del libro del repositorio."""
    libro = pathlib.Path(__file__).resolve().parent.parent / "libro" / "firmas_grafo.jsonl"
    for linea in reversed(libro.read_text(encoding="utf-8").splitlines()):
        if not linea.strip():
            continue
        fila = json.loads(linea)
        sobre, firma = fila.get("sobre"), fila.get("firma")
        if not sobre or not firma:
            continue
        v, _ = verificar(sobre, firma, directorio=directorio)
        if v == "OK":
            return fila
    return None


def main():
    directorio = cargar_directorio()
    fila = buscar_sobre_humano(directorio)
    if fila is None:
        sys.exit("No hay ningún sobre válido en libro/firmas_grafo.jsonl con el que probar.")

    sobre, firma = fila["sobre"], fila["firma"]
    caso_real = sobre["peticion_id"]
    caso_ajeno = "PET-999"

    print(f"\n  Sobre auténtico, firmado para {caso_real}.")
    print(f"  {GRIS}Un agente lo copia entero y lo presenta en {caso_ajeno}.{FIN}\n")

    fallos = 0

    # 1 · Presentado en SU caso: debe pasar. Si esto fallara, la comprobación sería inútil
    #     por rechazarlo todo, que es la forma más fácil de aparentar seguridad.
    v, d = verificar(sobre, firma, directorio=directorio, peticion_esperada=caso_real)
    ok = v == "OK"
    fallos += not ok
    print(f"  {VERDE + '✓' + FIN if ok else ROJO + '✗' + FIN} en su propio caso  "
          f"({caso_real}) → {v}")

    # 2 · El mismo sobre, el mismo byte, presentado en otro expediente: debe caer.
    v, d = verificar(sobre, firma, directorio=directorio, peticion_esperada=caso_ajeno)
    ok = v == "CONTEXTO_AJENO"
    fallos += not ok
    print(f"  {VERDE + '✓' + FIN if ok else ROJO + '✗' + FIN} reutilizado en otro "
          f"({caso_ajeno}) → {v}")
    if ok:
        print(f"      {GRIS}firmado para {d['firmado_para']}, presentado en "
              f"{d['presentado_en']} — {d['por_que']}{FIN}")

    # 3 · Sin decir en qué expediente estamos, no se puede juzgar el contexto: la firma sigue
    #     siendo válida y el veredicto es OK. Esto NO es un agujero: es la frontera del
    #     verificador. Quien verifica tiene que aportar el caso, y por eso se dice aquí.
    v, _ = verificar(sobre, firma, directorio=directorio)
    ok = v == "OK"
    fallos += not ok
    print(f"  {VERDE + '✓' + FIN if ok else ROJO + '✗' + FIN} sin declarar caso "
          f"→ {v} {GRIS}(el vínculo lo aporta quien verifica, no el sobre){FIN}")

    print()
    if fallos:
        print(f"  {ROJO}VEREDICTO: FALLA — {fallos} comprobación(es) en rojo{FIN}\n")
        sys.exit(1)
    print(f"  {VERDE}VEREDICTO: PASA{FIN} — una aprobación humana auténtica no se puede "
          f"trasplantar a otro expediente.\n")


if __name__ == "__main__":
    main()
