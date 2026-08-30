#!/usr/bin/env python3
"""Los rótulos que van superpuestos sobre la demostración, y por qué son dos.

POR QUÉ EXISTE ESTE ARCHIVO. El rótulo original se hizo a mano y su generador no quedó en el
repositorio: cuando hubo que cambiar el texto, no había de dónde partir. Ahora sí.

POR QUÉ SON DOS Y NO UNO, que es lo que de verdad importa. Las reglas del concurso puntúan
«unedited, live execution». Preguntado en el foro si se puede acelerar la grabación entera para
no pasarse de cuatro minutos, el organizador respondió que **una aceleración uniforme de una
ejecución real —sin cortes, sin empalmes, sin añadir ni quitar nada— se interpreta normalmente
como «sin editar», pero recortar o unir clips no**; y recomendó dejar la ejecución continua y
**avisar en pantalla si se aceleró**.

De ahí salen los dos rótulos:

  · `rotulo_toma_unica.png`           — para la toma que va a 1×, tal como se grabó.
  · `rotulo_toma_unica_acelerado.png` — para la toma acelerada uniformemente, que DICE que lo está.

Usar el primero sobre metraje acelerado sería afirmar algo que no es cierto sobre la única parte
del vídeo cuyo valor entero es que se puede creer. Es el error más caro posible aquí.

    python3 assets/slides/generar_rotulos.py [velocidad]     # velocidad: 2 por defecto
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
ANCHO, ALTO = 640, 100
FONDO = (11, 41, 64, 235)        # Deep Harbor, casi opaco
BORDE = (39, 230, 210, 190)      # Electric Cyan
TITULO = (233, 255, 251, 255)    # Ice
PIE = (147, 168, 184, 255)       # Slate

NEGRITA = "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf"
NORMAL = "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf"


def rotulo(destino: Path, titulo: str, pie: str) -> None:
    im = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([2, 2, ANCHO - 3, ALTO - 3], radius=14, fill=FONDO, outline=BORDE, width=2)
    # El punto de grabación: lo mismo que enseña cualquier cámara, y se lee sin idioma.
    d.ellipse([26, 42, 42, 58], fill=BORDE)
    d.text((58, 26), titulo, font=ImageFont.truetype(NEGRITA, 27), fill=TITULO)
    d.text((58, 63), pie, font=ImageFont.truetype(NORMAL, 15), fill=PIE)
    im.save(destino)
    print(f"  {destino.name}  ({ANCHO}×{ALTO})  «{titulo}» · «{pie}»")


if __name__ == "__main__":
    v = sys.argv[1] if len(sys.argv) > 1 else "2"
    rotulo(AQUI / "rotulo_toma_unica.png",
           "UNEDITED — SINGLE TAKE",
           "live against Google Cloud · no cuts inside this block")
    rotulo(AQUI / "rotulo_toma_unica_acelerado.png",
           "UNEDITED — SINGLE TAKE",
           f"live against Google Cloud · no cuts · uniform {v}x playback")
