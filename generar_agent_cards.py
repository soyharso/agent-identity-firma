#!/usr/bin/env python3
"""Genera Agent Cards en YAML y JSON desde claves/directorio.json.

B1 del errata 2026-08-28: el catálogo se genera desde el directorio de claves,
no se escribe a mano. Así no puede derivar de la verdad.

Uso:
    python3 generar_agent_cards.py                  # escribe en agent_cards/
    python3 generar_agent_cards.py --dry-run        # imprime a stdout
"""
import argparse
import json
import pathlib
import sys
import datetime

ROOT = pathlib.Path(__file__).resolve().parent
DIRECTORIO = ROOT / "claves" / "directorio.json"
SALIDA = ROOT / "agent_cards"

# Campos obligatorios del rubro (respuesta oficial Devpost Manager):
# owner, propósito/purpose, alcance/scope, estado/status
PLANTILLA_YAML = """\
# Agent Card — generada desde claves/directorio.json v{version}
# Fecha de generación: {fecha}
# NO editar a mano: editar claves/directorio.json y regenerar.
agent_card_version: "1.0"
generated_from: "claves/directorio.json"
directory_version: {version}
generated_at: "{fecha}"

name: "{nombre}"
owner: "{owner}"
type: "{tipo}"

purpose: >
  {proposito}

scope:
  authorized_states: {alcance}
  cannot_authorize: {no_puede}

identity:
  algorithm: "{algoritmo}"
  kms_resource: "{recurso_kms}"
  public_key_file: "claves/{clave_publica}"

status: "{estado}"

# Lo que este agente NO puede hacer (declarado explícitamente):
# - Autorizar estados fuera de authorized_states
# - Firmar con la clave de otro agente o de la persona
# - Ampliar su propio alcance en tiempo de ejecución
"""


def todos_los_estados():
    """El universo de estados del sistema, para calcular el complemento."""
    return [
        "abierta", "cerrada", "descartada", "cerrada_con_juicio",
        "perdonada", "informada", "cotizada", "descuento_aprobado",
        "cancelada", "exige_humano",
    ]


def generar_card(nombre: str, datos: dict, version: int) -> dict:
    alcance = datos["alcance_permitido"]
    no_puede = [e for e in todos_los_estados() if e not in alcance]
    fecha = datetime.date.today().isoformat()

    card = {
        "agent_card_version": "1.0",
        "generated_from": "claves/directorio.json",
        "directory_version": version,
        "generated_at": fecha,
        "name": nombre,
        "owner": "Softronica SAS",
        "type": datos["tipo"],
        "purpose": datos["nota"],
        "scope": {
            "authorized_states": alcance,
            "cannot_authorize": no_puede,
        },
        "identity": {
            "algorithm": datos["algoritmo"],
            "kms_resource": datos["recurso_gestionado"],
            "public_key_file": f"claves/{datos['archivo_publico']}",
        },
        "status": "active",
    }

    yaml_txt = PLANTILLA_YAML.format(
        version=version,
        fecha=fecha,
        nombre=nombre,
        owner="Softronica SAS",
        tipo=datos["tipo"],
        proposito=datos["nota"],
        alcance=json.dumps(alcance, ensure_ascii=False),
        no_puede=json.dumps(no_puede, ensure_ascii=False),
        algoritmo=datos["algoritmo"],
        recurso_kms=datos["recurso_gestionado"],
        clave_publica=datos["archivo_publico"],
        estado="active",
    )

    return card, yaml_txt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Imprime a stdout sin escribir archivos")
    args = parser.parse_args()

    directorio = json.loads(DIRECTORIO.read_text())
    version = directorio["version"]
    claves = directorio["claves"]

    if not args.dry_run:
        SALIDA.mkdir(exist_ok=True)

    # Índice del catálogo
    catalogo = {
        "catalog_version": version,
        "generated_at": datetime.date.today().isoformat(),
        "generated_from": "claves/directorio.json",
        "agents": [],
    }

    for nombre, datos in claves.items():
        if datos["tipo"] == "HUMANO":
            # La persona NO es un agente; se incluye en el directorio para
            # declarar explícitamente qué estados requieren firma humana.
            print(f"  [persona] {nombre} — incluida en catálogo como principal, no como agente")

        card, yaml_txt = generar_card(nombre, datos, version)
        catalogo["agents"].append({
            "name": nombre,
            "type": datos["tipo"],
            "card_file": f"agent_cards/{nombre}.json",
        })

        if args.dry_run:
            print(f"\n{'='*60}")
            print(f"AGENT CARD: {nombre}")
            print('='*60)
            print(yaml_txt)
        else:
            (SALIDA / f"{nombre}.yaml").write_text(yaml_txt)
            (SALIDA / f"{nombre}.json").write_text(
                json.dumps(card, indent=2, ensure_ascii=False))
            print(f"  ✓ agent_cards/{nombre}.yaml + .json")

    # Índice del catálogo
    if args.dry_run:
        print("\n=== CATALOG INDEX ===")
        print(json.dumps(catalogo, indent=2, ensure_ascii=False))
    else:
        (SALIDA / "catalog.json").write_text(
            json.dumps(catalogo, indent=2, ensure_ascii=False))
        print(f"  ✓ agent_cards/catalog.json")
        print(f"\nAgent Cards generadas desde directorio v{version}")
        print(f"Para regenerar: python3 generar_agent_cards.py")


if __name__ == "__main__":
    main()
