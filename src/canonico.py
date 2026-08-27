"""La forma exacta que se firma. UN solo sitio, y el de la norma internacional.

POR QUÉ EXISTE ESTE ARCHIVO. Había dos serializadores en el repositorio, escritos con quince
minutos de diferencia, y **no coincidían**: uno escapaba los acentos y el otro no. Con texto sin
acentos daban lo mismo, así que los kill-tests pasaban. Con un acento, la firma dejaba de
validar. Lo cazó la fase cero, no yo.

Y hay una razón más fuerte que la coherencia interna. Todo el producto se apoya en que
**cualquiera pueda rehacer la verificación**, también en otro lenguaje. Improvisar la
serialización rompe esa promesa en silencio: dos programas correctos, en dos lenguajes, firmando
bytes distintos. La norma existe para eso, y por eso se usa la norma y no una aproximación.

Dos casos medidos donde nuestra aproximación anterior divergía de la norma:
  · un número decimal:  `2.0` frente a `2`  → resumen distinto.
  · un acento:  `\\u00f3` escapado frente a los bytes crudos  → resumen distinto.
"""
import hashlib

import rfc8785


def canonico(sobre: dict) -> bytes:
    """Los bytes exactos que se firman, según RFC 8785."""
    return rfc8785.dumps(sobre)


def digest(sobre: dict) -> bytes:
    return hashlib.sha256(canonico(sobre)).digest()


def resumen_texto(texto: str) -> str:
    """El resumen del contenido curado, que viaja dentro del sobre."""
    return "sha256:" + hashlib.sha256(texto.encode("utf-8")).hexdigest()
