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
    # El cuerpo se ajusta al ancho disponible en vez de fijarse: al cambiar el texto del rótulo
    # por uno más largo, el título se salía de la caja y la última palabra quedaba cortada en
    # cámara. Un rótulo recortado dice justo lo contrario de lo que el rótulo viene a decir.
    def cabe(texto, ruta, tope, maximo):
        for cuerpo in range(maximo, 8, -1):
            f = ImageFont.truetype(ruta, cuerpo)
            if d.textlength(texto, font=f) <= tope:
                return f
        return ImageFont.truetype(ruta, 9)

    disponible = ANCHO - 58 - 20
    d.text((58, 26), titulo, font=cabe(titulo, NEGRITA, disponible, 27), fill=TITULO)
    d.text((58, 63), pie, font=cabe(pie, NORMAL, disponible, 15), fill=PIE)
    im.save(destino)
    print(f"  {destino.name}  ({ANCHO}×{ALTO})  «{titulo}» · «{pie}»")


if __name__ == "__main__":
    v = sys.argv[1] if len(sys.argv) > 1 else "2"
    # POR QUÉ NO DICE «UNEDITED», que es lo que decía hasta el 2026-08-30. Lo tumbó el disidente
    # externo, y tenía razón: es una afirmación ABSOLUTA colocada sobre un vídeo cuyo envoltorio
    # —títulos, diagrama, fundidos— sí está editado. Un jurado adversarial no lee el matiz «no
    # cuts INSIDE this block»: lee la palabra grande, ve un fundido dos minutos después, y la
    # defensa se convierte en una acusación contra uno mismo. El rótulo ahora dice exactamente
    # qué cubre —este bloque— y deja de proclamar lo que no puede prometer del vídeo entero.
    rotulo(AQUI / "rotulo_toma_unica.png",
           "DEMO BLOCK — ONE CONTINUOUS TAKE",
           "no cuts within this segment · live against Google Cloud")
    rotulo(AQUI / "rotulo_toma_unica_acelerado.png",
           "DEMO BLOCK — ONE CONTINUOUS TAKE",
           f"no cuts within this segment · live · uniform {v}x playback")
