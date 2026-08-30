#!/usr/bin/env python3
"""KILL-TEST — dos decisiones idénticas dejan de ser indistinguibles.

EL PROBLEMA QUE CIERRA. Un sobre que solo firma el CONTENIDO no distingue dos
decisiones iguales. Y en atención al cliente las resoluciones son de plantilla:
«se descarta la queja del cliente» resuelve cientos de expedientes con la misma
frase exacta. Mismo texto, mismo hash, mismo estado destino: dos aprobaciones
distintas producen sobres que solo se diferencian en el identificador de la
petición — y si alguien no lo comprueba, en nada.

LA SOLUCIÓN, que es del operador: firmar también EL ACTO. No solo qué se decidió,
sino cuándo se emitió, desde qué canal, quién lo emite y sobre quién se aplica.
Esos cuatro campos entran dentro de lo firmado, así que:

  · cambiarlos invalida la firma — no se pueden retocar;
  · copiarlos tal cual delata que la decisión era de otro momento o de otra persona;
  · y dos decisiones distintas difieren al menos en uno, luego sus firmas difieren.

No hace falta un contador ni una marca de un solo uso: la unicidad sale de que el
acto es único.

EL LÍMITE, dicho antes de que lo encuentre otro: el momento tiene resolución de un
segundo. Dos decisiones sobre el MISMO destinatario, MISMO origen y MISMO emisor
dentro del mismo segundo seguirían colisionando. Eso lo cierra `peticion_padre`,
que ata la decisión al expediente del que nació. Está declarado y todavía no es
obligatorio, porque lo entrega el canal de peticiones.

Uso: python3 agente/killtest_acto.py
Sin red y sin credenciales: firma con una clave efímera generada aquí mismo.
"""
import base64
import json
import pathlib
import sys
import time

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src.canonico import canonico                       # noqa: E402
from src.verificar_sobre import CAMPOS_ACTO, verificar  # noqa: E402

VERDE, ROJO, GRIS, FIN = "\033[32m", "\033[31m", "\033[2m", "\033[0m"

TEXTO_PLANTILLA = "Se descarta la queja del cliente: revisando el historial, el error fue suyo."


def directorio_efimero():
    """Un directorio de una sola clave, creado en memoria. No toca Cloud KMS ni el disco."""
    priv = ec.generate_private_key(ec.SECP256R1())
    pub = priv.public_key()
    pem = pub.public_bytes(serialization.Encoding.PEM,
                           serialization.PublicFormat.SubjectPublicKeyInfo)
    return priv, {"persona-prueba": {
        "tipo": "HUMANO",
        "alcance_permitido": ["cerrada", "descartada", "cerrada_con_juicio", "perdonada"],
        "algoritmo": "EC_SIGN_P256_SHA256",
        "_publica": serialization.load_pem_public_key(pem)}}


def firmar(priv, sobre):
    return base64.b64encode(
        priv.sign(canonico(sobre), ec.ECDSA(hashes.SHA256()))).decode()


def sobre_de(peticion, cliente, momento, origen="portal", emisor="persona-operador"):
    import hashlib
    return {"peticion_id": peticion,
            "estado_destino": "descartada",
            "hash_contenido": "sha256:" + hashlib.sha256(TEXTO_PLANTILLA.encode()).hexdigest(),
            "marca_temporal": momento,
            "emitido_en": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(momento)),
            "origen": origen,
            "emisor": emisor,
            "sobre_quien": cliente,
            "algoritmo": "EC_SIGN_P256_SHA256"}


def main():
    priv, directorio = directorio_efimero()
    ahora = int(time.time())

    # Dos reclamaciones distintas, de dos clientes distintos, resueltas con LA MISMA FRASE.
    a = sobre_de("PET-100", "cliente-A", ahora)
    b = sobre_de("PET-200", "cliente-B", ahora + 61)
    firma_a, firma_b = firmar(priv, a), firmar(priv, b)

    print(f"\n  Dos decisiones con el texto de plantilla, palabra por palabra igual.")
    print(f"  {GRIS}A: {a['peticion_id']} · {a['sobre_quien']}   "
          f"B: {b['peticion_id']} · {b['sobre_quien']}{FIN}")
    print(f"  {GRIS}Mismo hash de contenido en las dos: "
          f"{a['hash_contenido'] == b['hash_contenido']}{FIN}\n")

    fallos = 0

    def paso(etiqueta, sobre, firma, esperado, **kw):
        nonlocal fallos
        v, d = verificar(sobre, firma, directorio=directorio, **kw)
        ok = v == esperado
        fallos += not ok
        print(f"  {VERDE + '✓' + FIN if ok else ROJO + '✗' + FIN} {etiqueta:<48} → {v}")
        return d

    acto_a = {c: a[c] for c in CAMPOS_ACTO}
    acto_b = {c: b[c] for c in CAMPOS_ACTO}

    print(f"  {GRIS}El hash NO las distingue: es el mismo en las dos.{FIN}")
    paso("A, en su propio acto", a, firma_a, "OK", acto_esperado=acto_a)
    paso("B, en su propio acto", b, firma_b, "OK", acto_esperado=acto_b)

    print(f"\n  {GRIS}Reciclar la aprobación de A hacia el caso de B{FIN}")
    d = paso("la firma de A presentada como el acto de B", a, firma_a,
             "ACTO_AJENO", acto_esperado=acto_b)
    if d.get("campo"):
        print(f"      {GRIS}difiere en «{d['campo']}»: firmado con {d['firmado_con']}, "
              f"presentado con {d['presentado_con']}{FIN}")

    print(f"\n  {GRIS}Retocar el sobre para que encaje: la firma deja de valer{FIN}")
    falsificado = dict(a)
    falsificado["sobre_quien"] = "cliente-B"
    paso("A con el destinatario cambiado a mano", falsificado, firma_a,
         "FIRMANTE_DESCONOCIDO", acto_esperado=acto_b)

    print(f"\n  {GRIS}Y un sobre que no declara el acto no puede fingir que sí{FIN}")
    viejo = {k: v for k, v in a.items() if k not in CAMPOS_ACTO}
    paso("sobre sin campos de acto, exigiéndoselos", viejo, firmar(priv, viejo),
         "ACTO_INCOMPLETO", acto_esperado=acto_a)

    print()
    if fallos:
        print(f"  {ROJO}VEREDICTO: FALLA — {fallos} comprobación(es) en rojo{FIN}\n")
        sys.exit(1)
    print(f"  {VERDE}VEREDICTO: PASA{FIN} — dos resoluciones idénticas ya no producen "
          f"sobres intercambiables.\n")


if __name__ == "__main__":
    main()
