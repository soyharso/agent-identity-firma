#!/usr/bin/env python3
"""La portada y el cierre del vídeo, con el logotipo sellado por el operador.

POR QUÉ EXISTE. Las dos imágenes se hicieron a mano el 2026-08-30 y su generador no quedó en el
repositorio — exactamente el mismo agujero que `generar_rotulos.py` documenta para el rótulo, y
que se pagó igual: al cambiar el logotipo no había de dónde partir. Ahora sí lo hay, y el
logotipo se lee del archivo sellado en vez de estar dibujado dentro de la imagen.

Búsqueda previa (C1): `grep -rln portada --include='*.py'` no devolvía ningún generador —solo
`app_real.py` y el panel, que hablan de otra cosa—, y en `assets/slides/` el único generador es
`generar_rotulos.py`, que hace los rótulos superpuestos y no las tarjetas de 1920×1080. No
había nada que ampliar, así que esto nace al lado de aquél y con su misma forma.

QUÉ CAMBIA RESPECTO DE LAS IMÁGENES VIEJAS: el logotipo. Las de agosto llevaban el trazo
anterior, dibujado a mano dentro del PNG. Estas pegan `assets/cleveria-logo-dark.png`, que es la
versión de tinta clara del logotipo que el operador selló, la misma que sirve el servicio en
`/ui/cleveria-logo-dark.png`. Si el logotipo vuelve a cambiar, se cambia el archivo y se vuelve
a correr esto: no hay que redibujar nada.

    python3 assets/slides/generar_portada_y_cierre.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
LOGO = AQUI.parent / "cleveria-logo-dark.png"
ANCHO, ALTO = 1920, 1080

# La paleta de la marca, la misma que el panel de autoridad y el portal.
NAVY = (6, 17, 31)
HALO = (13, 30, 52)              # el óvalo de fondo, apenas más claro que el navy
ICE = (233, 255, 251)
CYAN = (39, 230, 210)
SLATE = (147, 168, 184)

NEGRITA = "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf"
NORMAL = "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf"


def lienzo() -> Image.Image:
    """El fondo: navy y un óvalo difuso que levanta el centro. Sin él la tarjeta es un rectángulo
    negro y el logotipo flota sin sitio."""
    im = Image.new("RGB", (ANCHO, ALTO), NAVY)
    halo = Image.new("RGB", (ANCHO, ALTO), NAVY)
    ImageDraw.Draw(halo).ellipse([-160, -300, ANCHO + 160, ALTO + 300], fill=HALO)
    return Image.blend(im, halo.filter(ImageFilter.GaussianBlur(120)), 0.9)


def centrado(d, y, texto, fuente, color):
    ancho = d.textlength(texto, font=fuente)
    d.text(((ANCHO - ancho) / 2, y), texto, font=fuente, fill=color)


def pega_logo(im, y, alto):
    """El logotipo sellado, a la altura pedida y centrado. Se lee del archivo: no se redibuja."""
    logo = Image.open(LOGO).convert("RGBA")
    ancho = round(logo.width * alto / logo.height)
    logo = logo.resize((ancho, alto), Image.LANCZOS)
    im.paste(logo, ((ANCHO - ancho) // 2, y), logo)


def rotulo_esquina(d, texto):
    """El aviso de los primeros ocho segundos, arriba a la izquierda.

    NO ES DECORACIÓN. Sobre la portada se narra «contamos cincuenta y ocho cierres firmados como
    humano», y esos 58 son del sistema de PREPRODUCCIÓN del equipo, que tiene datos de clientes y
    no es publicable: no hay ninguna pantalla de esta demostración que los pruebe. Sin el rótulo,
    una imagen de marca debajo de esa frase se lee como si la estuviera demostrando. El rótulo
    dice, en el mismo cuadro, que el dato viene de otro sitio.
    """
    f = ImageFont.truetype(NORMAL, 26)
    ancho = d.textlength(texto, font=f)
    d.rounded_rectangle([64, 60, 64 + ancho + 40, 118], radius=10,
                        fill=(11, 41, 64), outline=(39, 230, 210, 120), width=1)
    d.text((84, 76), texto, font=f, fill=SLATE)


def portada(destino: Path):
    im = lienzo()
    d = ImageDraw.Draw(im)
    rotulo_esquina(d, "preproduction system — not this demo")
    pega_logo(im, 200, 205)
    centrado(d, 510, "An agent can work.", ImageFont.truetype(NEGRITA, 74), ICE)
    centrado(d, 605, "It cannot sign as a person.", ImageFont.truetype(NEGRITA, 74), CYAN)
    d.line([(760, 720), (1160, 720)], fill=CYAN, width=2)
    centrado(d, 765, "Cryptographic authority boundaries for enterprise agent fleets",
             ImageFont.truetype(NORMAL, 33), SLATE)
    centrado(d, 828, "Softronica  ·  Google Cloud  ·  All Things Agentic 2026",
             ImageFont.truetype(NORMAL, 29), SLATE)
    im.save(destino)
    print(f"  {destino.name}  ({ANCHO}×{ALTO})  logotipo: {LOGO.name}")


def cierre(destino: Path):
    """El cierre DICE LO QUE LA VOZ DICE, y hasta hoy no.

    La tarjeta llevaba la tesis larga —«Agents sign their own operational evidence…»— mientras la
    narración del segundo 227 remata con otra frase: «It's not that it shouldn't. It's that it
    can't.» Leer una cosa y oír otra en los últimos diez segundos reparte la atención justo donde
    el vídeo se juega el recuerdo. Manda el guion: la frase narrada es el titular, y la tesis baja
    a la línea de apoyo, que es su sitio.
    """
    im = lienzo()
    d = ImageDraw.Draw(im)
    grande = ImageFont.truetype(NEGRITA, 82)
    centrado(d, 330, "It's not that it shouldn't.", grande, ICE)
    centrado(d, 440, "It's that it can't.", grande, CYAN)
    apoyo = ImageFont.truetype(NORMAL, 34)
    centrado(d, 620, "Agents sign their own operational evidence.", apoyo, SLATE)
    centrado(d, 668, "Humans alone sign human judgement. Neither can rewrite the other.",
             apoyo, SLATE)
    pega_logo(im, 800, 95)
    im.save(destino)
    print(f"  {destino.name}  ({ANCHO}×{ALTO})  logotipo: {LOGO.name}")


if __name__ == "__main__":
    print("\nPortada y cierre, con el logotipo sellado:")
    portada(AQUI / "portada.png")
    cierre(AQUI / "cierre.png")
    print()
