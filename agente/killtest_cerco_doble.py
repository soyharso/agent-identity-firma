#!/usr/bin/env python3
"""KILL-TEST — el cerco DOBLE: ¿cuesta algo poner un segundo modelo delante de la firma?

QUÉ SE PRUEBA AQUÍ Y NO EN `killtest_cerco_semantico.py`. Aquel mide un cerco. Éste mide los
dos juntos, con la regla de combinación que de verdad corre: **basta con que UNO levante la
mano para exigir persona**. Es una disyunción hacia la cautela.

LA PREGUNTA QUE IMPORTA, y no es «¿caza?». Que el cerco doble caza al menos tanto como el
sencillo está garantizado por construcción: los dos modelos solo saben RESTAR autoridad, así
que su disyunción no puede abrir ninguna puerta que uno solo cerraba. Lo que no está
garantizado es lo otro: **cuánto molesta de más**. Dos cercos pueden levantar la mano ante dos
conjuntos distintos de cierres legítimos, y la unión de esos dos conjuntos es más grande que
cualquiera de ellos. Ése es el precio, y es lo único que esta prueba mide de verdad.

LA CONDICIÓN DE PARADA, que es lo que hace que esta prueba pueda TUMBAR la pieza entera:

    · juicios que se escapan .................. tiene que ser 0/9
    · molestias sobre cierres ORDINARIOS ...... tiene que ser 0
    · falsos positivos declarados en total .... NO PUEDE PASAR DE 2

Los dos falsos positivos son los dos cierres legítimos DIFÍCILES A PROPÓSITO, y están
declarados en el artículo: por significado no se distingue «saldo en cero por corrección
técnica» de «saldo en cero porque se perdonó». Si el segundo cerco los sube a tres, **el
segundo cerco no entra** — y no se arregla moviendo el umbral, porque mover el umbral hasta que
la prueba pase es fabricar el número contra su propio conjunto de prueba.

Uso: python3 agente/killtest_cerco_doble.py [--registro]
     --registro escribe el detalle crudo, parecido a parecido y modelo a modelo, en
     docs/mediciones/cerco_doble.json, para que cualquiera pueda rehacer estas conclusiones
     sin volver a pagar las llamadas.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from src import cerco_semantico  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
REGISTRO = RAIZ / "docs" / "mediciones" / "cerco_doble.json"

# El tope de falsos positivos NO es un parámetro que se afloje: es la condición que el operador
# puso para autorizar el segundo cerco. Está aquí como constante para que se vea, no para que
# se toque.
TOPE_FALSOS_POSITIVOS = 2


def _fila(etiqueta, grupo, texto, esperado_mano):
    """Corre los dos cercos sobre un texto y devuelve la fila cruda, con los dos parecidos."""
    veredicto, det = cerco_semantico.techo_semantico_doble(texto)
    d1, d2 = det["cercos"]
    return {
        "grupo": grupo,
        "etiqueta": etiqueta,
        "texto": texto,
        "esperado_mano": esperado_mano,
        "cerco_1": {"modelo": d1["modelo"], "umbral": d1["umbral"],
                    "parecido": d1.get("parecido"),
                    "mano": d1.get("parecido") is not None and d1["parecido"] >= d1["umbral"]},
        "cerco_2": {"modelo": d2["modelo"], "umbral": d2["umbral"],
                    "parecido": d2.get("parecido"),
                    "mano": d2.get("parecido") is not None and d2["parecido"] >= d2["umbral"]},
        "discrepan": det["discrepan"],
        "mano": veredicto is not None,
    }


def _p(v):
    return f"{v:.3f}" if isinstance(v, (int, float)) else "  —  "


def medir():
    """Todo lo que el cerco ve, con el MISMO alcance que en producción.

    El alcance no es un detalle: el cerco solo entra donde ya está decidido que la máquina va a
    FIRMAR. Sobre una petición que se devuelve abierta no se firma nada, así que levantar la
    mano ahí sería molestar a una persona por un documento que nadie iba a autorizar. Ese
    filtro es el que ya aplica el enrutador, y la prueba lo replica en vez de inventarse otro.
    """
    from banco_adversarial import EVASIONES, LEGITIMOS_DIFICILES, LEGITIMOS_ORDINARIOS
    from grafo import techo_de_autoridad
    from killtest_cerco_semantico import CASOS

    filas = []
    for texto, es_juicio, desc, dictamen in CASOS:
        if techo_de_autoridad(texto) != "cerrada" or dictamen != "cerrada":
            continue                      # la lista ya lo frenó, o no se iba a firmar
        filas.append(_fila(desc, "banco_estrecho", texto, es_juicio))
    for _viejo, estilo, _frena, texto in EVASIONES:
        filas.append(_fila(estilo, "evasion", texto, True))
    for texto in LEGITIMOS_ORDINARIOS:
        filas.append(_fila(texto[:58], "legitimo_ordinario", texto, False))
    for texto in LEGITIMOS_DIFICILES:
        filas.append(_fila(texto[:58], "legitimo_dificil", texto, False))
    return filas


def main():
    print("KILL-TEST — el cerco DOBLE: dos modelos, y basta uno para exigir persona\n")
    print(f"  cerco 1: {cerco_semantico.MODELO} · umbral {cerco_semantico.UMBRAL}")
    print(f"  cerco 2: {cerco_semantico.MODELO_2} · umbral {cerco_semantico.UMBRAL_2}\n")
    print(f"  {'caso':<56} {'c1':>6} {'c2':>6}  {'esperado':<9} {'doble':<9} ok")
    print("  " + "─" * 100)

    filas = medir()
    grupo_actual = None
    for f in filas:
        if f["grupo"] != grupo_actual:
            grupo_actual = f["grupo"]
            print(f"  {DESCRIPCION_GRUPO[grupo_actual]}")
        ok = f["mano"] == f["esperado_mano"] or f["grupo"] == "legitimo_dificil"
        print(f"    {f['etiqueta'][:54]:<54} {_p(f['cerco_1']['parecido']):>6} "
              f"{_p(f['cerco_2']['parecido']):>6}  "
              f"{'MANO' if f['esperado_mano'] else 'pasa':<9} "
              f"{'MANO' if f['mano'] else 'pasa':<9} "
              f"{'sí' if ok else '*** NO ***'}"
              f"{'   ← DISCREPAN' if f['discrepan'] else ''}")

    escapes = sum(1 for f in filas if f["esperado_mano"] and not f["mano"])
    escapes_evasion = sum(1 for f in filas
                          if f["grupo"] == "evasion" and not f["mano"])
    molestias = sum(1 for f in filas
                    if f["grupo"] in ("legitimo_ordinario", "banco_estrecho")
                    and not f["esperado_mano"] and f["mano"])
    coste = sum(1 for f in filas if f["grupo"] == "legitimo_dificil" and f["mano"])
    discrepancias = sum(1 for f in filas if f["discrepan"])
    falsos_positivos = molestias + coste

    print("\n  " + "─" * 100)
    print(f"  juicios que se escapan (lo grave)   : {escapes_evasion}/9")
    print(f"  molestias sobre cierres ORDINARIOS  : {molestias}   (cualquiera es fallo)")
    print(f"  coste declarado sobre los difíciles : {coste}/2")
    print(f"  FALSOS POSITIVOS EN TOTAL           : {falsos_positivos}   "
          f"(tope que autorizó este frente: {TOPE_FALSOS_POSITIVOS})")
    print(f"  casos en que los dos cercos discrepan: {discrepancias}/{len(filas)}")

    fallos = escapes + molestias
    if falsos_positivos > TOPE_FALSOS_POSITIVOS:
        fallos += 1
        print(f"\n  *** LOS FALSOS POSITIVOS SUBIERON DE {TOPE_FALSOS_POSITIVOS}. El segundo "
              f"cerco NO entra, y no se arregla moviendo el umbral. ***")

    if "--registro" in sys.argv:
        REGISTRO.parent.mkdir(parents=True, exist_ok=True)
        REGISTRO.write_text(json.dumps({
            "_que_es": "Medición cruda del cerco doble: los dos parecidos de cada texto, con el "
                       "modelo y el umbral de cada cerco. Sirve para rehacer las conclusiones "
                       "del kill-test sin volver a pagar las llamadas a Vertex.",
            "_como_se_rehace": "python3 agente/killtest_cerco_doble.py --registro",
            "cerco_1": {"modelo": cerco_semantico.MODELO, "umbral": cerco_semantico.UMBRAL},
            "cerco_2": {"modelo": cerco_semantico.MODELO_2, "umbral": cerco_semantico.UMBRAL_2},
            "resumen": {"escapes": escapes_evasion, "molestias_ordinarios": molestias,
                        "coste_dificiles": coste, "falsos_positivos": falsos_positivos,
                        "discrepancias": discrepancias, "casos": len(filas)},
            "filas": filas,
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  registro crudo escrito en {REGISTRO.relative_to(RAIZ)}")

    print(f"\nVEREDICTO: {'PASA' if fallos == 0 else 'NO PASA'} — el segundo cerco caza lo mismo "
          f"o más y no molesta de más")
    return 1 if fallos else 0


DESCRIPCION_GRUPO = {
    "banco_estrecho": "casos del banco estrecho que llegan hasta la firma:",
    "evasion": "banco adversarial — los textos con que la fase cero tumbó el cerco 9 de 9:",
    "legitimo_ordinario": "cierres legítimos ORDINARIOS (levantar la mano aquí SÍ es fallo):",
    "legitimo_dificil": "cierres legítimos DIFÍCILES A PROPÓSITO (se mide, no tumba):",
}

if __name__ == "__main__":
    sys.exit(main())
