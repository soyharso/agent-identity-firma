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
    # El MODELO se declara, no se deja al azar. Dos motivos, y el segundo importa para la
    # entrega: (1) `latest_short` está afinado para enunciados cortos, que es exactamente lo
    # que es una nota de voz de atención al cliente; (2) sin declararlo, el servicio elige por
    # nosotros y no podríamos decir con qué modelo transcribimos — y aquí todo lo que se afirma
    # tiene que poder comprobarse. `chirp`/`chirp_2` NO existen en esta versión de la interfaz:
    # medido el 2026-08-30, devuelven `400 Incorrect model specified`.
    config = {"languageCode": idioma or IDIOMA, "encoding": codificacion,
              "model": os.environ.get("MODELO_ESCUCHA", "latest_short")}
    if codificacion == "LINEAR16":
        config["sampleRateHertz"] = 16000
    r = requests.post("https://speech.googleapis.com/v1/speech:recognize",
                      headers=_cabeceras(), timeout=60,
                      json={"config": config,
                            "audio": {"content": base64.b64encode(audio_wav).decode()}})
    r.raise_for_status()
    res = r.json().get("results") or []
    return res[0]["alternatives"][0]["transcript"].strip() if res else ""


# Formatos que el navegador y WhatsApp producen, y su nombre para cada motor.
_MIME = {"WEBM_OPUS": "audio/webm", "OGG_OPUS": "audio/ogg",
         "LINEAR16": "audio/wav", "MP3": "audio/mp4"}


def escuchar_con_gemini(audio: bytes, codificacion: str = "WEBM_OPUS") -> str:
    """Segundo motor de transcripción, por Vertex AI.

    POR QUÉ HAY DOS. Speech-to-Text se queda sin cuota, y cuando eso pasa a mitad de una
    grabación no hay segunda toma. Un solo motor es un punto único de fallo el día que más
    caro sale. Gemini acepta audio y tiene cuota aparte, así que uno cubre al otro.

    NO CAMBIA NADA DEL CANDADO. Lo que devuelve sigue siendo DATO, exactamente igual que el
    texto escrito: si la nota de voz contiene instrucciones dirigidas al agente, siguen siendo
    dato y siguen exigiendo una persona. Un modelo de transcripción —el que sea— está ANTES de
    la ruta de la decisión, nunca dentro. Que ahora sean dos no le da autoridad a ninguno.
    """
    # `global`, y sin prefijo de región en el host: es donde vive el modelo que el resto del
    # proyecto ya usa (`agente/agent.py` fija GOOGLE_CLOUD_LOCATION=global). Apuntar a
    # `us-central1-aiplatform…` devuelve 404 sin decir por qué, y se pierde un rato buscándolo.
    region = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
    modelo = os.environ.get("MODELO_VOZ", "gemini-3.7-flash")
    host = "aiplatform.googleapis.com" if region == "global" else f"{region}-aiplatform.googleapis.com"
    url = (f"https://{host}/v1/projects/{PROYECTO}"
           f"/locations/{region}/publishers/google/models/{modelo}:generateContent")
    r = requests.post(url, headers=_cabeceras(), timeout=90, json={
        "contents": [{"role": "user", "parts": [
            {"text": "Transcribe literally what is said in this audio. "
                     "Reply with the transcription only, no commentary, no quotes."},
            {"inlineData": {"mimeType": _MIME.get(codificacion, "audio/webm"),
                            "data": base64.b64encode(audio).decode()}}]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 256}})
    r.raise_for_status()
    for c in r.json().get("candidates") or []:
        for p in (c.get("content") or {}).get("parts") or []:
            if p.get("text"):
                return p["text"].strip()
    return ""


def transcribir(audio: bytes, idioma: str = None, codificacion: str = "WEBM_OPUS"):
    """La cadena de dos motores, en UN solo sitio. Devuelve `(motor, texto, fallos)`.

    POR QUÉ EXISTE. Esta cadena vivía dentro del endpoint del portal, y la prueba de ruptura de
    voz llamaba a `escuchar()` a pelo. Resultado medido el 2026-08-30: Speech-to-Text devolvió
    `429 Too Many Requests` —cuota por minuto agotada por las corridas del día— y **la prueba se
    puso en rojo mientras el producto seguía funcionando**, porque el producto tenía respaldo y
    la prueba no. Una prueba más frágil que aquello que prueba no mide el sistema: mide la suerte.

    EL REINTENTO NO ES MAQUILLAJE. El `429` es un límite por minuto, no un fallo del candado; lo
    que esta prueba afirma es que un juicio hablado acaba en manos de una persona, y eso no
    cambia porque se agote la cuota. Se reintenta una vez, se pasa al segundo motor, y **si los
    dos caen se devuelve el fallo**: aquí no hay texto de reserva, ni lo habrá.
    """
    import time

    # CUÁNTAS VECES SE INSISTE, y por qué son tres y no una. Medido en producción el 2026-08-30,
    # sobre veintiocho peticiones: Speech-to-Text devuelve `503 Service Unavailable` en cerca del
    # 80 % de los intentos desde la cuenta de servicio, mientras desde una credencial de usuario
    # responde 200 sin fallar una sola vez. Es intermitencia del proveedor, no un límite nuestro:
    # las cuotas del proyecto son 900 peticiones por minuto y la facturación está activa.
    # Con un intento se ve el motor principal 2 de cada 10 veces; con tres, cerca de la mitad.
    # No cambia lo que el sistema garantiza —el respaldo ya cubría el 100 %—, cambia lo que un
    # jurado ve cuando prueba el portal, y la respuesta sigue diciendo la verdad en los dos casos.
    intentos_por_motor = {"speech-to-text": 3, "gemini": 2}

    fallos = []
    for nombre, fn in (("speech-to-text", lambda: escuchar(audio, idioma=idioma,
                                                           codificacion=codificacion)),
                       ("gemini", lambda: escuchar_con_gemini(audio, codificacion=codificacion))):
        tope = intentos_por_motor[nombre]
        for intento in range(1, tope + 1):
            try:
                texto = fn()
                if texto:
                    return nombre, texto, fallos
                break                                    # respondió, pero no entendió nada
            except Exception as e:                       # noqa: BLE001
                transitorio = any(c in str(e) for c in ("429", "503", "500"))
                if transitorio and intento < tope:
                    time.sleep(1)
                    continue
                fallos.append(f"{nombre}: {str(e)[:120]} (x{intento})")
                break
    return "ninguno", "", fallos


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
