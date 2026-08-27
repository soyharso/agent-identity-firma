#!/usr/bin/env python3
"""El cerco semántico: un SEGUNDO modelo de Google que solo puede pedir MÁS prudencia.

POR QUÉ EXISTE, y es un hueco medido de este mismo repositorio, no una función de adorno.

El techo de autoridad (`techo_de_autoridad` en el grafo) es una lista de palabras. Su fuerza
está declarada en el propio código: *«es tonta a propósito: no razona, así que no hay nada que
engañar»*. Su debilidad es la otra cara de lo mismo, y se midió el 2026-08-27:

    "se descarta la queja del cliente"                             -> exige_humano   (la caza)
    "Tras revisar el historial, consideramos que la inconformidad
     presentada por el usuario no procede y se cierra el asunto
     sin lugar a compensación."                                    -> cerrada        (NO la caza)
    "El titular queda liberado de toda responsabilidad y no se le
     cobrará el saldo pendiente."                                  -> cerrada        (NO la caza)

Los dos últimos son juicio humano puro —absolver, perdonar una deuda— escritos sin ninguna de
las palabras de la lista. **La máquina podría firmarlos.** Es el mismo defecto que ya medimos
contra el filtro del proveedor: lo que cambia de forma se escapa de cualquier lista.

Un modelo de embeddings no mira las palabras: mira el significado. Por eso cierra este hueco y
la lista no puede.

LA REGLA QUE NO SE ROMPE. Este modelo **solo puede bajar la autoridad de la máquina, nunca
subirla**. Devuelve `exige_humano` o no devuelve nada. No puede decir «esto sí se puede
cerrar», y por eso su fallo, su alucinación o su envenenamiento no abren ninguna puerta: en el
peor caso molestan a una persona de más. La compuerta sigue siendo la misma función determinista
que toma el mínimo de todos los techos.

Con esto el proyecto pasa de «un modelo» a «dos modelos, y ninguno de los dos puede darse
autoridad». Es una promesa más fuerte, no más débil.

ANTE LA DUDA, PRUDENCIA. Si la llamada falla, se devuelve `exige_humano`, igual que hace el
enrutador cuando el dictamen llega ilegible. Un cerco que se cae en abierto no es un cerco.
"""
import os

import google.auth
import google.auth.transport.requests
import requests

PROYECTO = os.environ.get("GOOGLE_CLOUD_PROJECT", "ai-transf-lab-0827")
REGION = os.environ.get("REGION_EMBEDDINGS", "us-central1")

# `gemini-embedding-001` y NO `text-embedding-005`, y el motivo está medido. La fase cero tumbó
# la primera versión nueve veces de nueve; tres de esas evasiones eran el MISMO juicio escrito
# en otro idioma. Con el modelo viejo: chino 0,541 · alemán 0,596 · francés 0,714. Con éste:
# 0,791 · 0,768 · 0,789, y el cierre legítimo de control se queda en 0,605. O sea que el agujero
# multilingüe era del modelo, no del diseño — y se tapa cambiando una cadena.
MODELO = os.environ.get("MODELO_EMBEDDINGS", "gemini-embedding-001")

# Cuánto parecido basta para levantar la mano. NO se eligió a ojo: sale de la separación
# MEDIDA entre las dos clases en `agente/killtest_cerco_semantico.py`, sobre los textos que
# el cerco ve de verdad (los que la máquina iba a firmar). Margen medido: +0,082 — juicios
# desde 0,742, cierres legítimos hasta 0,591. El umbral va por el medio, con holgura a los
# dos lados. Sobre los doce casos SIN esa condición el margen era +0,008, o sea ninguno:
# cualquier umbral habría estado fabricado. El arreglo fue el alcance, no el número.
UMBRAL = float(os.environ.get("UMBRAL_CERCO", "0.70"))

# Lo que significa «aquí hay un juicio de por medio», dicho de varias formas a propósito. No son
# palabras clave: son EJEMPLOS de sentido, y el parecido se mide contra ellos.
#
# LAS ANCLAS CRECIERON POR UN ATAQUE, no por gusto. Las ocho primeras estaban todas en registro
# coloquial y en dos idiomas, y la fase cero evadió el cerco nueve veces de nueve escribiendo el
# MISMO juicio en registro notarial, administrativo y en otros idiomas. Se añaden anclas en ese
# registro y en los idiomas donde se probó la evasión: ancla y ataque en el mismo idioma, que es
# lo que el atacante recomendó al entregar su munición.
JUICIOS = (
    # coloquial, español
    "se descarta la reclamación presentada por la persona",
    "se absuelve al responsable y no se le sanciona",
    "se perdona la deuda y no se cobrará el saldo pendiente",
    "la inconformidad del usuario no procede y se cierra sin compensación",
    "queda liberado de toda responsabilidad sobre lo ocurrido",
    "se decide no continuar con la queja porque no amerita",
    # registro administrativo y notarial, que es por donde entró la evasión
    "no ha lugar a continuar el trámite y queda finiquitado sin obligación económica",
    "se resuelve dar por terminado el proceso sin que subsista deber alguno de pago",
    "se procede al cierre del expediente sin que se derive obligación pecuniaria",
    "se decide clausurar la actuación sin sanción aplicable al interesado",
    # inglés, coloquial y corporativo
    "the customer complaint is dismissed and no refund is due",
    "the responsible party is absolved of any wrongdoing",
    "no further action is warranted and the outstanding balance is adjusted to zero",
    # los idiomas donde se midió la evasión, con ancla propia y no traducida desde el español
    "il est décidé de clore le dossier sans suite et sans somme exigible",
    "das Verfahren wird eingestellt, ohne dass ein ausstehender Betrag verbleibt",
    "决定终止本案的后续处理程序，申请人无需承担任何未结余额",
)

_cache_juicios = None
_cache_cred = None


def _token():
    """La credencial se guarda y se reutiliza mientras siga viva.

    Antes se pedía una nueva en CADA llamada, y eso costaba 0,6 s de los 3-4 s totales — que en
    una demostración grabada en vivo se ven. Lo midió la fase cero.
    """
    global _cache_cred
    if _cache_cred is None:
        _cache_cred, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"])
    if not _cache_cred.valid:
        _cache_cred.refresh(google.auth.transport.requests.Request())
    return _cache_cred.token


def _frases(texto: str) -> list[str]:
    """Trocea el texto en frases, y devuelve también el texto entero.

    POR QUÉ. Tres de las nueve evasiones eran juicio real escondido entre relleno técnico
    —códigos de expediente, normas ISO, indicadores de trimestre—. Al promediar un texto largo,
    el vector se diluye y la cláusula que absuelve deja de pesar. Midiendo frase a frase y
    quedándose con la MÁS parecida, el relleno deja de proteger.

    No cubre las otras evasiones: cuando la absolución está entretejida en la sintaxis de la
    misma frase que cierra el trámite, no hay nada que aislar. Eso lo dijo el propio atacante al
    entregar su munición, y por eso las anclas también tuvieron que crecer.
    """
    import re
    trozos = [t.strip() for t in re.split(r"(?<=[.。!?;])\s+|\n+", texto) if len(t.strip()) > 15]
    return ([texto] + trozos)[:12]          # tope: el texto entero más once frases


def _vectores(textos):
    url = (f"https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROYECTO}"
           f"/locations/{REGION}/publishers/google/models/{MODELO}:predict")
    r = requests.post(url, timeout=30,
                      headers={"Authorization": f"Bearer {_token()}",
                               "Content-Type": "application/json"},
                      json={"instances": [{"content": t} for t in textos]})
    r.raise_for_status()
    return [p["embeddings"]["values"] for p in r.json()["predictions"]]


def _coseno(a, b):
    num = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return num / (na * nb) if na and nb else 0.0


def techo_semantico(texto: str) -> tuple[str | None, dict]:
    """Devuelve `("exige_humano", detalle)` si el texto SIGNIFICA un juicio, o `(None, detalle)`.

    NUNCA devuelve un techo más permisivo que `exige_humano`: no está en su poder.
    """
    global _cache_juicios
    try:
        if _cache_juicios is None:
            _cache_juicios = _vectores(list(JUICIOS))
        trozos = _frases(texto)
        vectores = _vectores(trozos)
        # El texto se mide entero Y frase a frase, y manda el trozo que MÁS se parezca a algún
        # juicio. Así el relleno técnico deja de diluir la cláusula que absuelve.
        maximo, cual, donde = -1.0, JUICIOS[0], texto
        for trozo, v in zip(trozos, vectores):
            parecidos = [_coseno(v, j) for j in _cache_juicios]
            m = max(parecidos)
            if m > maximo:
                maximo, cual, donde = m, JUICIOS[parecidos.index(m)], trozo
    except Exception as e:                                       # noqa: BLE001
        # Ante la duda, prudencia: la misma regla que aplica el enrutador con un dictamen
        # ilegible. Un cerco que se cae en abierto no es un cerco.
        return "exige_humano", {"error": type(e).__name__, "motivo": "el cerco no pudo medir"}

    detalle = {"parecido": round(maximo, 3), "se_parece_a": cual,
               "en_el_trozo": donde[:90]}
    if maximo >= UMBRAL:
        return "exige_humano", detalle
    return None, detalle


if __name__ == "__main__":
    import sys
    veredicto, detalle = techo_semantico(" ".join(sys.argv[1:]) or "prueba")
    print(veredicto or "sin objeción", detalle)
