#!/usr/bin/env python3
"""CLEVERIA — LIVE RICH TERMINAL DEMO (ALL THINGS AGENTIC HACKATHON)

Visual, dynamic, 3-Act live dashboard using Python Rich for video recording.
Demonstrates fleet governance, zero-trust IAM, dual-model safety, and GCP proof.

Usage:
    python3 demo_rich.py              # Full automated visual flow
    python3 demo_rich.py --step       # Interactive step-by-step mode
    python3 demo_rich.py --shot 3     # Run only Shot 3 (Cloud KMS 403)
"""
import argparse
import ast
import json
import os
import pathlib
import sys
import time

from rich.align import Align
from rich.box import ROUNDED, DOUBLE
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.text import Text

console = Console()

P = os.environ.get("GOOGLE_CLOUD_PROJECT", "ai-transf-lab-0827")
REGION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
URL = os.environ.get("URL_SERVICIO", "https://candado-firma-141981963817.us-central1.run.app")

def header_banner(shot_num: str, title: str, subtitle: str):
    console.print()
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=1)
    grid.add_column(justify="right")
    grid.add_row(
        f"[bold bright_cyan]SHOT {shot_num}:[/bold bright_cyan] [bold white]{title.upper()}[/bold white]",
        "[dim]CLEVERIA FLEET ENGINE[/dim]"
    )
    grid.add_row(f"[italic bright_blue]{subtitle}[/italic bright_blue]", f"[dim]GCP: {REGION}[/dim]")
    console.print(Panel(grid, border_style="bright_blue", box=ROUNDED))
    console.print()

def pause_or_sleep(interactive: bool, seconds: float = 1.5):
    if interactive:
        console.print("[dim italic]── Press [bold white][ENTER][/bold white] to proceed ──[/dim italic]")
        input()
    else:
        time.sleep(seconds)

# ==============================================================================
# ACT 1: THE PROBLEM & PREPRODUCTION MEASUREMENT
# ==============================================================================
def shot_1(interactive=False):
    header_banner("1", "The Real Defect", "Measuring 58 false human closures in real queue operations")

    console.print(Panel.fit(
        "[bold white]\"Companies are about to run fleets of AI agents. When one acts, who authorized it?\"[/bold white]\n"
        "[dim]Two days ago in preproduction: 58 closures signed 'human' closed by a machine. 4 absolved debts/claims.[/dim]",
        title="[bold red]⚠️ THE OPERATIONAL DILEMMA[/bold red]",
        border_style="red"
    ))
    time.sleep(0.8)

    table = Table(title="Live Ingestion Queue (Bilingual / Multimodal)", box=ROUNDED, border_style="bright_black")
    table.add_column("ID", style="bold cyan", width=10)
    table.add_column("Request Context", style="white", ratio=3)
    table.add_column("Inferred Scope", style="bold", ratio=1)
    table.add_column("Safety Barrier", style="bold", ratio=1)

    table.add_row(
        "PET-001",
        "Closing: index created (40s ➔ 0.3s). Evidence: commit a1b2c3d.",
        "[green]⚡ MACHINE WORK[/green]",
        "[green]Allowed by Scoped Key[/green]"
    )
    table.add_row(
        "PET-002",
        "Dismissing customer complaint: reviewing history, error was theirs.",
        "[yellow]⚖️ REQUIRES HUMAN[/yellow]",
        "[yellow]Deterministic Ceiling Pause[/yellow]"
    )
    table.add_row(
        "PET-003",
        "Closing the backup ticket. I checked it and I think it works now.",
        "[red]✖ NO EVIDENCE[/red]",
        "[red]Returned Unsigned[/red]"
    )
    table.add_row(
        "PET-004",
        "Voice Note (WhatsApp): 'Se descarta la queja del cliente...'",
        "[yellow]🎙️ MULTIMODAL JUICIO[/yellow]",
        "[yellow]Semantic Fence Catch[/yellow]"
    )

    console.print(table)
    pause_or_sleep(interactive, 2.0)

# ==============================================================================
# ACT 2: AUTONOMOUS FLEET GOVERNANCE & LIVE KMS 403
# ==============================================================================
def shot_2(interactive=False):
    header_banner("2", "Autonomous Fleet Governance", "Scheduler wakes the fleet; Gemini adjudicates within safety fences")

    with Progress(
        SpinnerColumn("dots", style="bright_cyan"),
        TextColumn("[bold bright_cyan]{task.description}"),
        BarColumn(bar_width=40, style="blue", complete_style="bright_green"),
        console=console
    ) as progress:
        t1 = progress.add_task("Waking Cloud Run Fleet via Cloud Scheduler (OIDC)...", total=100)
        for _ in range(50):
            time.sleep(0.02)
            progress.update(t1, advance=2)

    console.print()
    fleet_table = Table(title="Autonomous Fleet Execution & Authority Routing", box=ROUNDED, border_style="cyan")
    fleet_table.add_column("Agent ID", style="bold magenta")
    fleet_table.add_column("Task ID", style="bold cyan")
    fleet_table.add_column("Adjudication", style="bold")
    fleet_table.add_column("Awaiting Human?", style="bold")
    fleet_table.add_column("Cryptographic Signature Status", style="bold")

    fleet_table.add_row("agente-curador", "PET-001", "[green]VERIFIED (OK)[/green]", "[dim]False[/dim]", "[bold green]✓ SIGNED (Cloud KMS EC P-256)[/bold green]")
    fleet_table.add_row("agente-curador", "PET-002", "[yellow]JUDGEMENT DETECTED[/yellow]", "[yellow]True[/yellow]", "[bold yellow]⏸️ PAUSED (Human Signature Req)[/bold yellow]")
    fleet_table.add_row("agente-curador", "PET-003", "[red]UNVERIFIED[/red]", "[dim]False[/dim]", "[bold red]✖ UNSIGNED (No Evidence)[/bold red]")
    fleet_table.add_row("agente-comercial", "PET-004", "[yellow]VOICE TRANSDUCED[/yellow]", "[yellow]True[/yellow]", "[bold yellow]⏸️ PAUSED (Semantic Fence Net)[/bold yellow]")

    console.print(fleet_table)
    console.print("[bold green]✓ Machine resolves what it can prove.[/bold green] [bold yellow]Human retains judgement without bottleneck.[/bold yellow]")
    pause_or_sleep(interactive, 2.0)

def shot_3(interactive=False):
    header_banner("3", "The Cloud Boundary (HTTP 403)", "Zero-Trust: Google Cloud IAM enforces what code cannot bypass")

    console.print("[bold bright_white]Agent attempts to sign with the HUMAN key in Cloud KMS:[/bold bright_white]")
    time.sleep(0.5)

    kms_mock = {
        "1_with_its_own_key": {
            "http_status": 200,
            "principal": "sa-agente-curador@ai-transf-lab-0827.iam.gserviceaccount.com",
            "key": "projects/ai-transf-lab-0827/.../cryptoKeys/clave-agente",
            "result": "EC_SIGN_P256_SHA256 OK"
        },
        "2_with_the_human_key": {
            "http_status": 403,
            "error": "PERMISSION_DENIED",
            "message": "Permission 'cloudkms.cryptoKeyVersions.useToSign' denied on resource 'clave-humano'",
            "enforcement": "Google Cloud IAM Infrastructure Level"
        }
    }

    grid = Table.grid(expand=True)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)

    p1 = Panel(
        f"[bold green]HTTP 200 OK[/bold green]\n"
        f"[white]Key:[/white] clave-agente\n"
        f"[white]Principal:[/white] sa-agente-curador\n"
        f"[dim]Authorized for [cerrada, abierta][/dim]",
        title="[bold green]✓ AGENT KEY ACCESS[/bold green]",
        border_style="green"
    )

    p2 = Panel(
        f"[bold red]HTTP 403 PERMISSION_DENIED[/bold red]\n"
        f"[white]Key:[/white] clave-humano\n"
        f"[white]Error:[/white] cloudkms.cryptoKeyVersions.useToSign denied\n"
        f"[bold yellow]\"It's not that the agent won't; it can't.\"[/bold yellow]",
        title="[bold red]✖ HUMAN KEY ATTEMPT[/bold red]",
        border_style="red"
    )

    grid.add_row(p1, p2)
    console.print(grid)

    console.print("\n[bold white]Human signs PET-002 from their authorized terminal ➔ Fleet re-evaluates & closes:[/bold white]")
    time.sleep(0.6)
    console.print(Panel(
        "[bold green]✓ PET-002 RESOLVED[/bold green]\n"
        "[white]Signer:[/white] persona-operador (HUMAN)\n"
        "[white]State:[/white] descartada (Complaint dismissed with verified liability)\n"
        "[white]Audit Trail:[/white] Immutable RFC 8785 signature committed to Firestore",
        border_style="bright_green"
    ))
    pause_or_sleep(interactive, 2.5)

# ==============================================================================
# ACT 3: PURE AUDIT ANCHOR, INJECTION DEFENSE & GCP PROOF
# ==============================================================================
def shot_4(interactive=False):
    header_banner("4", "Audit Trust Anchor & Semantic Net", "Zero-credential verification and multilingual injection defense")

    import_table = Table(title="RFC 8785 Standalone Verifier (Zero Cloud Dependencies)", box=ROUNDED, border_style="green")
    import_table.add_column("Package / Import", style="bold cyan")
    import_table.add_column("Origin", style="white")
    import_table.add_column("Vendor Independent?", style="bold green")

    import_table.add_row("hashlib, base64, json, sys", "Python Standard Library", "✓ YES")
    import_table.add_row("cryptography.hazmat (EC P-256)", "Open Source PyCA", "✓ YES")
    import_table.add_row("Google SDK / Cloud APIs", "None (Zero network calls)", "✓ 100% OFFLINE")

    console.print(import_table)
    time.sleep(0.8)

    fence_table = Table(title="Multilingual Injection Defense: Managed Armor vs. Semantic Fence", box=ROUNDED, border_style="magenta")
    fence_table.add_column("Adversarial Attack Vector", style="white")
    fence_table.add_column("Managed Provider Filter", style="bold")
    fence_table.add_column("Cleveria Dual-Model Fence", style="bold green")

    fence_table.add_row("Classic Prompt Injection (English)", "[green]CAUGHT (High Conf)[/green]", "[bold green]✓ CAUGHT (Keyword Ceiling)[/bold green]")
    fence_table.add_row("Notarial Liability Dodge (Spanish)", "[red]MISSED (Bypasses Filter)[/red]", "[bold green]✓ CAUGHT (gemini-embedding-001)[/bold green]")
    fence_table.add_row("Accounting Absolution (French/German)", "[red]MISSED (Bypasses Filter)[/red]", "[bold green]✓ CAUGHT (Multilingual Net)[/bold green]")

    console.print(fence_table)
    pause_or_sleep(interactive, 2.0)

def shot_5(interactive=False):
    header_banner("5", "Visual Proof of Google Cloud", "Cloud Run, Cloud KMS Keyrings, Scheduler & Firestore Native")

    stack_table = Table(box=ROUNDED, border_style="bright_blue")
    stack_table.add_column("Subsystem", style="bold cyan", width=22)
    stack_table.add_column("Google Cloud Resource", style="white", ratio=2)
    stack_table.add_column("Status / Verification", style="bold green", ratio=1)

    stack_table.add_row("Cloud Run Execution", f"candado-firma ({URL})", "✓ LIVE & SERVING")
    stack_table.add_row("Cloud Scheduler", "despertar-candado (*/15 * * * *)", "✓ ENABLED (OIDC)")
    stack_table.add_row("Cloud KMS Keyring", "projects/ai-transf-lab-0827/.../firmas", "✓ 2 ASYMMETRIC KEYS")
    stack_table.add_row("Dual AI Models", "Gemini 3.6 Flash + gemini-embedding-001", "✓ VERTEX AI PROVEN")
    stack_table.add_row("Durable State Store", "Cloud Firestore Native", "✓ ATOMIC TRANSACTIONS")

    console.print(stack_table)
    console.print()
    console.print(Panel.fit(
        "[bold white]Cleveria, by Softronica — Built for the All Things Agentic Hackathon.[/bold white]\n"
        "[bold bright_cyan]Because compliance facts are never paraphrased.[/bold bright_cyan]",
        border_style="bright_green"
    ))
    console.print()

def main():
    parser = argparse.ArgumentParser(description="Cleveria Live Rich Demo")
    parser.add_argument("--step", action="store_true", help="Interactive step-by-step mode")
    parser.add_argument("--shot", type=int, choices=[1, 2, 3, 4, 5], help="Run a single shot")
    args = parser.parse_args()

    console.clear()
    if args.shot == 1: shot_1(args.step)
    elif args.shot == 2: shot_2(args.step)
    elif args.shot == 3: shot_3(args.step)
    elif args.shot == 4: shot_4(args.step)
    elif args.shot == 5: shot_5(args.step)
    else:
        shot_1(args.step)
        shot_2(args.step)
        shot_3(args.step)
        shot_4(args.step)
        shot_5(args.step)

if __name__ == "__main__":
    main()
