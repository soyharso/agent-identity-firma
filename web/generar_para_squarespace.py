#!/usr/bin/env python3
"""Convierte la página de cleveria.co en un bloque que se pueda pegar dentro de Squarespace.

POR QUÉ HACE FALTA CONVERTIRLA, y no basta con copiar y pegar. La página original es un documento
completo: define estilos sobre `body`, sobre `*` y sobre las etiquetas de encabezado. Pegada tal
cual en un bloque de código de Squarespace, **esos estilos se aplican a la plantilla entera** —
la cabecera, el pie y cualquier otra página que comparta la hoja de estilos— y el resultado no es
la página que se revisó: es la plantilla rota.

QUÉ HACE ESTE GUION, que son tres cosas y ninguna es cosmética:

  1. **Encapsula**: mete todo dentro de `<div id="cleveria-home">` y antepone ese identificador a
     cada regla de estilo, de modo que ninguna se escape al resto del sitio. `body{…}` pasa a ser
     `#cleveria-home{…}`, y `*{box-sizing}` pasa a `#cleveria-home *{…}`.
  2. **Neutraliza el formulario propio.** En Squarespace el envío lo hace su bloque de formulario,
     no el nuestro: dejar un formulario que llama a un endpoint inexistente sería exactamente el
     formulario que finge, que es lo que la página vino a evitar. Se sustituye por un aviso
     visible para el operador y un enlace de correo que SÍ funciona mientras tanto.
  3. **Deja marcado dónde va el bloque nativo**, con un comentario que se ve al editar.

    python3 web/generar_para_squarespace.py
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "assets" / "web" / "cleveria-home.html"
DESTINO = RAIZ / "assets" / "web" / "cleveria-home-squarespace.html"
CAJA = "#cleveria-home"


def encapsular(css: str) -> str:
    """Antepone el contenedor a cada selector, sin tocar lo que va dentro de una @regla."""
    fuera = []
    for bloque in re.split(r"(@[a-zA-Z-]+[^{]*\{)", css):
        if bloque.startswith("@"):
            fuera.append(bloque)
            continue
        def prefijo(m):
            sels = []
            for s in m.group(1).split(","):
                s = s.strip()
                if not s:
                    continue
                if s in ("body", "html"):
                    sels.append(CAJA)
                elif s == "*":
                    sels.append(f"{CAJA} *")
                elif s.startswith(":root"):
                    sels.append(CAJA)
                elif s.startswith(("from", "to")) or re.fullmatch(r"\d+%", s):
                    sels.append(s)                      # fotograma de animación: no se toca
                else:
                    sels.append(f"{CAJA} {s}")
            return ", ".join(sels) + " {"
        fuera.append(re.sub(r"([^{}@]+)\{", prefijo, bloque))
    return "".join(fuera)


AVISO_FORMULARIO = """
      <div style="border:1px dashed rgba(39,230,210,.5);border-radius:12px;padding:22px;
                  text-align:left;background:rgba(11,41,64,.6)">
        <!-- ══════════════════════════════════════════════════════════════════════════ -->
        <!--  AQUÍ VA EL BLOQUE DE FORMULARIO DE SQUARESPACE.                           -->
        <!--  Añade un bloque «Form» justo debajo de este bloque de código y borra este -->
        <!--  recuadro. Configúralo para que las respuestas lleguen a info@cleveria.co. -->
        <!--  Campos: nombre, empresa, correo, teléfono, qué necesita, detalle.         -->
        <!-- ══════════════════════════════════════════════════════════════════════════ -->
        <p style="margin:0 0 10px;font-weight:600">¿Hablamos?</p>
        <p style="margin:0;color:#93A8B8;font-size:15px">
          Cuéntenos su caso a
          <a href="mailto:info@cleveria.co?subject=Cleveria" style="color:#27E6D2">info@cleveria.co</a>
          y le respondemos el mismo día hábil.
        </p>
      </div>
"""


def main() -> None:
    h = ORIGEN.read_text(encoding="utf-8")

    estilos = re.search(r"<style>(.*?)</style>", h, re.S)
    cuerpo = h[estilos.end():] if estilos else h
    css = encapsular(estilos.group(1)) if estilos else ""

    # Fuera el formulario propio y su guion: en Squarespace envía el bloque nativo.
    cuerpo = re.sub(r"<form class=\"form\".*?</form>", AVISO_FORMULARIO, cuerpo, flags=re.S)
    cuerpo = re.sub(r"<script>.*?</script>", "", cuerpo, flags=re.S)
    # Y fuera la línea del correo duplicada, que ahora vive dentro del aviso.
    cuerpo = re.sub(r"<p class=\"alternativa\">.*?</p>", "", cuerpo, flags=re.S)

    fuentes = "\n".join(re.findall(r"<link[^>]*fonts\.(?:googleapis|gstatic)[^>]*>", h))

    DESTINO.write_text(
        "<!-- Cleveria — bloque para pegar en un bloque de código de Squarespace.\n"
        "     Generado por web/generar_para_squarespace.py — no editar a mano, regenerar.\n"
        "     Todo va encapsulado en #cleveria-home para no tocar la plantilla del sitio. -->\n"
        f"{fuentes}\n<style>\n{css}\n</style>\n"
        f'<div id="cleveria-home">\n{cuerpo}\n</div>\n', encoding="utf-8")

    print(f"  escrito: {DESTINO.relative_to(RAIZ)}  ({DESTINO.stat().st_size} bytes)")
    print(f"  reglas encapsuladas bajo {CAJA} · formulario propio retirado · guion retirado")


if __name__ == "__main__":
    main()
