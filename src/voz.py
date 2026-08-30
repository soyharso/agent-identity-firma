#!/usr/bin/env python3
"""La misma garantía, entrando por voz — porque mucha gente no escribe.

POR QUÉ EXISTE, y no es por sumar modelos. En el canal de esta casa, una parte grande de los
clientes manda **notas de voz**, no texto: gente mayor, gente con poca alfabetización, gente que
va conduciendo, gente que sencillamente escribe despacio. Si el candado solo protege lo que llega
escrito, protege a los clientes que menos lo necesitan.

Lo que se demuestra aquí es que **la garantía no depende del canal de entrada**. Una nota de voz
que dice «se descarta la queja del cliente» acaba exactamente donde acaba el mismo texto escrito:
en manos de una persona, porque la máquina no tiene la llave para firmarlo. La modalidad cambia;
el techo de autoridad y el alcance por clave, no.

DOS MODELOS DE GOOGLE MÁS, y los dos hacen algo:
  · Speech-to-Text convierte la nota de voz en texto, que es lo que el techo sabe leer.
  · Text-to-Speech devuelve la respuesta hablada, para quien no puede leerla.

NINGUNO DE LOS DOS DECIDE NADA. La transcripción es DATO, igual que el texto escrito: si la nota
de voz contiene instrucciones dirigidas al agente, siguen siendo dato y siguen siendo señal de
que hace falta una persona. Un modelo de voz que se equivoque o al que alguien envenene no puede
ampliar la autoridad de nadie, porque no está en la ruta de la decisión: está antes.
"""
import base64
import os

import google.auth
import google.auth.transport.requests
import requests

PROYECTO = os.environ.get("GOOGLE_CLOUD_PROJECT", "ai-transf-lab-0827")
IDIOMA = os.environ.get("IDIOMA_VOZ", "es-CO")
VOZ = os.environ.get("VOZ_SALIDA", "es-US-Neural2-A")

_cred = None


def _token():
    global _cred
    if _cred is None:
        _cred, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"])
    if not _cred.valid:
        _cred.refresh(google.auth.transport.requests.Request())
    return _cred.token


def _cabeceras():
    return {"Authorization": f"Bearer {_token()}",
            "Content-Type": "application/json",
            "x-goog-user-project": PROYECTO}


def escuchar(audio_wav: bytes, idioma: str = None, codificacion: str = "LINEAR16") -> str:
    """Nota de voz -> texto. Lo que devuelve es DATO, nunca una orden.

    `codificacion` existe porque el audio no siempre llega del mismo sitio. Una nota de voz de
    WhatsApp llega en OGG_OPUS y el micrófono de un navegador en WEBM_OPUS; declarar LINEAR16
    para cualquiera de los dos devuelve o silencio o una transcripción que no se parece a lo
    que se dijo — que es exactamente el fallo que se vio en el portal. Los formatos comprimidos
    llevan la frecuencia dentro, así que no se le manda: mandarla equivocada es otra forma de
    obtener basura.
    """
    config = {"languageCode": idioma or IDIOMA, "encoding": codificacion}
    if codificacion == "LINEAR16":
        config["sampleRateHertz"] = 16000
    r = requests.post("https://speech.googleapis.com/v1/speech:recognize",
                      headers=_cabeceras(), timeout=60,
                      json={"config": config,
                            "audio": {"content": base64.b64encode(audio_wav).decode()}})
    r.raise_for_status()
    res = r.json().get("results") or []
    return res[0]["alternatives"][0]["transcript"].strip() if res else ""


def hablar(texto: str, voz: str = None) -> bytes:
    """Texto -> audio. Para quien no puede leer la respuesta en pantalla."""
    r = requests.post("https://texttospeech.googleapis.com/v1/text:synthesize",
                      headers=_cabeceras(), timeout=60,
                      json={"input": {"text": texto},
                            "voice": {"languageCode": "es-US", "name": voz or VOZ},
                            "audioConfig": {"audioEncoding": "LINEAR16",
                                            "sampleRateHertz": 16000}})
    r.raise_for_status()
    return base64.b64decode(r.json()["audioContent"])


if __name__ == "__main__":
    import sys
    frase = " ".join(sys.argv[1:]) or "Se descarta la queja del cliente."
    wav = hablar(frase)
    print(f"audio: {len(wav)} bytes · transcrito de vuelta: «{escuchar(wav)}»")
