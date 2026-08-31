#!/usr/bin/env python3
r"""La pista de narración, generada del MISMO plan que dirige la toma y que hace los subtítulos.

PARA QUÉ SIRVE Y PARA QUÉ NO. La voz del vídeo entregado debería ser la de la persona: los cinco
proyectos que ganaron la edición anterior narran con voz humana, y en un producto cuyo argumento
es que alguien responde de lo que firma, una voz sintética contándolo resta más de lo que ahorra.

Esta pista tiene otros dos trabajos, y los dos valen:

  1. **Ensayar.** Oír la frase con su ritmo antes de decirla, y saber cuántos segundos ocupa de
     verdad — que casi nunca son los que uno cree.
  2. **Cubrir.** Si el reloj aprieta y no hay tiempo de grabar la voz, una pista sintética
     entregada a tiempo vale más que una pista humana que no llegó.

Y una tercera cosa que solo se ve al usarla: **avisa de las frases que no caben**. Si el audio de
un momento dura más que su hueco en el plan, el problema no es la voz, es el guion — y es mejor
enterarse aquí que en la toma.

CÓMO SE MONTA CON LA IMAGEN. Genera un archivo por momento, con su segundo de inicio en el
nombre, más un `.txt` con los comandos de `ffmpeg` para pegarlos sobre el vídeo. No los ejecuta:
pegar audio sobre el metraje es una decisión de montaje, y el metraje todavía no existe.

BÚSQUEDA PREVIA antes de crear este archivo, hecha a mano porque este repositorio queda fuera del
alcance del gancho que la vigila: `ls *.py` y `grep -rln "texttospeech" --include=*.py .` devuelven
`src/voz.py` —las funciones que este guion llama— y `ensayar_narracion.py`, que hace lo contrario
(escucha a la persona y la corrige). No había nada que generara la pista.

USO:
    python3 generar_narracion.py --listar-voces      # las de gama alta que hay
    python3 generar_narracion.py --muestra           # una frase con seis voces, para elegir
    python3 generar_narracion.py --voz en-US-Studio-Q    # la pista entera
"""
import argparse
import base64
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

PLAN = RAIZ / "plan_toma.txt"
SALIDA = RAIZ / "narracion"
VOZ_DEFECTO = "en-US-Studio-Q"
FRASE_MUESTRA = ("That refusal is not our code. That is Google. "
                 "It's not that it shouldn't. It's that it can't.")
VERDE, ROJO, AMARILLO, GRIS, NEGRITA, FIN = (
    "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m")


def _voz():
    from src import voz
    return voz


def momentos():
    """(segundo, frase) de cada momento con narración, y el hueco hasta el siguiente."""
    if not PLAN.exists():
        sys.exit(f"{ROJO}No encuentro {PLAN}.{FIN}")
    todos = []
    for linea in PLAN.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        p = [x.strip() for x in linea.split("|")]
        if len(p) >= 2:
            todos.append((int(p[0]), p[4] if len(p) > 4 else ""))
    todos.sort()
    fuera = []
    for i, (seg, frase) in enumerate(todos):
        if not frase:
            continue
        fin = todos[i + 1][0] if i + 1 < len(todos) else seg + 12
        fuera.append((seg, fin - seg, frase))
    return fuera


def sintetizar(texto, nombre_voz, velocidad=0.95):
    import requests
    v = _voz()
    r = requests.post("https://texttospeech.googleapis.com/v1/text:synthesize",
                      headers=v._cabeceras(), timeout=90,
                      json={"input": {"text": texto},
                            "voice": {"languageCode": "en-US", "name": nombre_voz},
                            "audioConfig": {"audioEncoding": "MP3",
                                            "speakingRate": velocidad}})
    r.raise_for_status()
    return base64.b64decode(r.json()["audioContent"])


def duracion(mp3: pathlib.Path) -> float:
    """Segundos reales del audio. Sin esto no se puede avisar de lo que no cabe."""
    import subprocess
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "default=noprint_wrappers=1:nokey=1", str(mp3)],
                           capture_output=True, text=True, timeout=30)
        return float(r.stdout.strip())
    except Exception:                                                 # noqa: BLE001
        return 0.0


def main():
    ap = argparse.ArgumentParser(description="La pista de narración, desde el plan de la toma.")
    ap.add_argument("--voz", default=VOZ_DEFECTO)
    ap.add_argument("--velocidad", type=float, default=0.95)
    ap.add_argument("--muestra", action="store_true", help="una frase con varias voces")
    ap.add_argument("--listar-voces", action="store_true")
    a = ap.parse_args()

    if a.listar_voces:
        import requests
        r = requests.get("https://texttospeech.googleapis.com/v1/voices?languageCode=en-US",
                         headers=_voz()._cabeceras(), timeout=60)
        r.raise_for_status()
        for v in sorted(r.json().get("voices", []), key=lambda x: x["name"]):
            if any(k in v["name"] for k in ("Studio", "News", "Polyglot", "Chirp3")):
                print(f"  {v['name']:<28} {v['ssmlGender']}")
        return 0

    if a.muestra:
        SALIDA.mkdir(exist_ok=True)
        for n in ("en-US-Studio-Q", "en-US-Studio-O", "en-US-News-N",
                  "en-US-Chirp3-HD-Charon", "en-US-Chirp3-HD-Autonoe", "en-US-Polyglot-1"):
            f = SALIDA / f"muestra_{n}.mp3"
            f.write_bytes(sintetizar(FRASE_MUESTRA, n, a.velocidad))
            print(f"  {VERDE}✓{FIN} {f}")
        print(f"\n  {GRIS}Escúchalas y elige: python3 generar_narracion.py --voz <nombre>{FIN}\n")
        return 0

    ms = momentos()
    SALIDA.mkdir(exist_ok=True)
    print(f"\n{NEGRITA}PISTA DE NARRACIÓN{FIN}  {GRIS}{len(ms)} momentos · voz {a.voz}{FIN}\n")
    apretados, comandos = [], []
    for seg, hueco, frase in ms:
        f = SALIDA / f"{seg:04d}.mp3"
        f.write_bytes(sintetizar(frase, a.voz, a.velocidad))
        d = duracion(f)
        # El aviso que de verdad sirve: la frase que no cabe en su hueco. Es un problema del
        # guion, no de la voz, y es mucho más barato saberlo aquí que en la toma.
        cabe = d <= hueco
        if not cabe:
            apretados.append((seg, d, hueco, frase))
        color = VERDE if cabe else ROJO
        print(f"  {color}{seg:>4}s  {d:5.1f}s de {hueco:>3}s{FIN}  "
              f"{GRIS}{frase[:58]}{'…' if len(frase) > 58 else ''}{FIN}")
        comandos.append(f'-i {f.name} -filter_complex "[{{n}}]adelay={seg * 1000}|{seg * 1000}[a{seg}]"')

    (SALIDA / "COMO_MONTARLA.txt").write_text(
        "Cada archivo se llama con el segundo en que entra.\n\n"
        "Mezclar las pistas sobre el vídeo, conservando el sonido ambiente por debajo\n"
        "(un silencio absoluto se lee como que oculta algo):\n\n"
        "  ffmpeg -i video.mkv " +
        " ".join(f"-i {s:04d}.mp3" for s, _, _ in ms) +
        " \\\n    -filter_complex \"" +
        ";".join(f"[{i+1}]adelay={s*1000}|{s*1000}[a{i}]" for i, (s, _, _) in enumerate(ms)) +
        ";" + "".join(f"[a{i}]" for i in range(len(ms))) +
        f"[0:a]amix=inputs={len(ms)+1}:duration=first:weights='" +
        " ".join(["1"] * len(ms)) + " 0.25'[mix]\" \\\n"
        "    -map 0:v -map \"[mix]\" -c:v copy con_voz.mp4\n\n"
        "El último peso (0.25) es el ambiente original: se baja, no se elimina.\n",
        encoding="utf-8")

    if apretados:
        print(f"\n  {ROJO}{NEGRITA}{len(apretados)} frase(s) NO CABEN en su hueco:{FIN}")
        for seg, d, hueco, frase in apretados:
            print(f"    {seg:>4}s  necesita {d:.1f}s y tiene {hueco}s  {GRIS}{frase[:50]}…{FIN}")
        print(f"  {AMARILLO}Es el guion, no la voz: acorta la frase o dale más segundos al "
              f"momento en plan_toma.txt.{FIN}")
    else:
        print(f"\n  {VERDE}Todas caben en su hueco.{FIN}")
    print(f"\n  {GRIS}Cómo pegarla al vídeo: {SALIDA / 'COMO_MONTARLA.txt'}{FIN}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
