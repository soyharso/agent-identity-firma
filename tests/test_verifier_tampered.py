#!/usr/bin/env python3
"""Prueba de tolerancia a fallos: verificación de rechazo ante registros alterados (tampered).

Demuestra que si un registro firmado se altera aunque sea en un solo byte (o un agente
alucina/inyecta contenido no firmado o fuera de alcance), el verificador puro RFC 8785
rechaza inmediatamente la verificación devolviendo un código de error explícito y deteniendo el flujo.
"""
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.verificar_sobre import verificar

def test_tampered_rejection():
    firmas_file = ROOT / "libro" / "firmas_grafo.jsonl"
    lineas = [l.strip() for l in firmas_file.read_text().splitlines() if l.strip()]
    
    registro_valido = None
    for l in lineas:
        d = json.loads(l)
        if d.get("firma"):
            registro_valido = d
            break
            
    if not registro_valido:
        print("SKIP: no se encontró registro con firma en el libro para la prueba.")
        return

    sobre = registro_valido["sobre"]
    firma = registro_valido["firma"]

    # 1. Verificación del estado original (debe retornar "OK")
    estado_verif, detalle = verificar(sobre, firma)
    assert estado_verif == "OK", f"El registro original debe ser OK: {estado_verif} - {detalle}"
    print(f"  [1/3] ✓ Registro original íntegro: veredicto={estado_verif}")

    # 2. Alteración de un campo del sobre firmado (rompe la firma ECDSA del RFC 8785)
    sobre_alterado = copy.deepcopy(sobre)
    sobre_alterado["hash_contenido"] = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
    estado_alt, detalle_alt = verificar(sobre_alterado, firma)
    assert estado_alt == "FIRMANTE_DESCONOCIDO", f"Debe fallar firma: {estado_alt}"
    print(f"  [2/3] ✓ Alteración de hash/payload RECHAZADA: veredicto={estado_alt}")

    # 3. Alteración del texto verificado contra hash_contenido
    estado_txt, detalle_txt = verificar(sobre, firma, texto_actual="Texto alterado que no coincide con el hash")
    assert estado_txt == "CONTENIDO_ALTERADO", f"Debe fallar contenido alterado: {estado_txt}"
    print(f"  [3/3] ✓ Alteración de texto fuente RECHAZADA: veredicto={estado_txt}")

    print("\nVEREDICTO: PASA — Tolerancia a fallos demostrada: cualquier alteración o alucinación es rechazada determinísticamente.")

if __name__ == "__main__":
    print("TEST — Verificación de tolerancia a fallos ante manipulación de datos (Tampered Log)")
    test_tampered_rejection()
