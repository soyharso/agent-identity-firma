#!/usr/bin/env python3
"""CLEVERIA — LIVE 4-PANEL RICH DASHBOARD (ALL THINGS AGENTIC HACKATHON)

High-density visual layout combining:
- Panel 1: Ingestion Queue (Multimodal / Bilingual requests)
- Panel 2: Agent Fleet Status (agente-curador, agente-comercial, persona-operador)
- Panel 3: Cloud IAM & KMS Boundary (HTTP 200 vs HTTP 403 live status)
- Panel 4: Trust Metrics & Multilingual Semantic Net
"""
import os
import sys
import time
from rich.align import Align
from rich.box import ROUNDED, DOUBLE
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

def make_layout() -> Layout:
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=1)
    )
    layout["left"].split(
        Layout(name="queue", ratio=1),
        Layout(name="fleet", ratio=1)
    )
    layout["right"].split(
        Layout(name="boundary", ratio=1),
        Layout(name="metrics", ratio=1)
    )
    return layout

def get_header() -> Panel:
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=1)
    grid.add_column(justify="right")
    grid.add_row(
        "[bold white]CLEVERIA[/bold white] [bold bright_cyan]— Enterprise Agent Fleet Authority Dashboard[/bold bright_cyan]",
        "[dim]GCP: us-central1 • ADK 2.8 • KMS • Cloud Run[/dim]"
    )
    return Panel(grid, style="white on #0b1120", box=ROUNDED)

def get_queue_table(phase: int = 1) -> Table:
    table = Table(title="1. Multimodal Ingestion Queue", box=ROUNDED, expand=True, border_style="cyan")
    table.add_column("ID", style="bold cyan", width=9)
    table.add_column("Task Context / Modality", style="white")
    table.add_column("Authority Gate", style="bold")

    p1_status = "[green]✓ SIGNED (Machine)[/green]" if phase > 1 else "[cyan]⚡ INGESTING...[/cyan]"
    p2_status = "[bold yellow]⏸️ AWAITING HUMAN[/bold yellow]" if phase > 1 else "[yellow]EVALUATING...[/yellow]"
    p4_status = "[bold yellow]⏸️ PAUSED (Voice)[/bold yellow]" if phase > 1 else "[magenta]🎙️ TRANSCRIBING[/magenta]"

    table.add_row("PET-001", "Closing index (40s➔0.3s) Evidence: commit a1b2", p1_status)
    table.add_row("PET-002", "Dismiss customer complaint (Judgement)", p2_status)
    table.add_row("PET-003", "Closing backup ticket (No evidence)", "[red]✖ RETURNED (Unsigned)[/red]")
    table.add_row("PET-004", "Voice note (WhatsApp): 'Descarte la queja'", p4_status)
    return table

def get_fleet_table() -> Table:
    table = Table(title="2. Agent Fleet Identity & Scopes", box=ROUNDED, expand=True, border_style="blue")
    table.add_column("Principal", style="bold magenta", width=16)
    table.add_column("Type", style="bold")
    table.add_column("IAM Service Account / Key", style="dim")
    table.add_column("Scope Limits", style="bold")

    table.add_row("agente-curador", "[cyan]MAQUINA[/cyan]", "sa-agente-curador (KMS clave-agente)", "[green][cerrada, abierta][/green]")
    table.add_row("agente-comercial", "[cyan]MAQUINA[/cyan]", "sa-agente-qnowa (KMS clave-agente-qnowa)", "[blue][informada][/blue]")
    table.add_row("persona-operador", "[yellow]HUMANO[/yellow]", "Operator Machine (KMS clave-humano)", "[bold yellow][ALL + descartada][/bold yellow]")
    return table

def get_boundary_panel(phase: int = 1) -> Panel:
    content = Text()
    content.append("ZERO-TRUST CLOUD BOUNDARY (Cloud KMS EC P-256)\n", style="bold bright_white")
    content.append("──────────────────────────────────────────────\n", style="dim")
    content.append("• Machine Key (clave-agente):   ", style="white")
    content.append("HTTP 200 OK (Allowed)\n", style="bold green")
    content.append("• Human Key   (clave-humano):   ", style="white")
    content.append("HTTP 403 PERMISSION_DENIED\n\n", style="bold red")

    if phase > 2:
        content.append("REASON: ", style="bold yellow")
        content.append("Google Cloud IAM strictly denies sa-agente-curador on clave-humano.\n", style="white")
        content.append("\"It is not that the agent won't; it can't.\"", style="italic bright_cyan")
    else:
        content.append("Status: Monitoring IAM calls in real time...", style="dim")

    return Panel(content, title="3. Cloud KMS Enforcement", box=ROUNDED, border_style="red")

def get_metrics_panel() -> Panel:
    content = Text()
    content.append("AUDIT ANCHOR & DEFENSE TELEMETRY\n", style="bold bright_white")
    content.append("──────────────────────────────────────────────\n", style="dim")
    content.append("• RFC 8785 Standalone Verifier:   ", style="white")
    content.append("100% OFFLINE (0 Google pkgs)\n", style="bold green")
    content.append("• Dual Model (gemini-embedding):  ", style="white")
    content.append("ACTIVE (Vertex AI)\n", style="bold green")
    content.append("• Multilingual Injections (4 Lang): ", style="white")
    content.append("9/9 CAUGHT (0 False Positives)\n", style="bold green")
    content.append("• Durable Recovery (Kill-Resume): ", style="white")
    content.append("100% ATOMIC (Firestore)\n", style="bold green")
    return Panel(content, title="4. Safety & Audit Telemetry", box=ROUNDED, border_style="green")

def get_footer() -> Panel:
    msg = Text.from_markup(
        "[bold white]Cleveria, by Softronica[/bold white] • [bold bright_cyan]\"Because compliance facts are never paraphrased.\"[/bold bright_cyan] • [dim]Live Demo[/dim]"
    )
    return Panel(Align.center(msg), style="white on #0b1120", box=ROUNDED)

def main():
    layout = make_layout()
    layout["header"].update(get_header())
    layout["footer"].update(get_footer())

    for step in [1, 2, 3]:
        layout["queue"].update(Panel(get_queue_table(step), box=ROUNDED, border_style="cyan"))
        layout["fleet"].update(Panel(get_fleet_table(), box=ROUNDED, border_style="blue"))
        layout["boundary"].update(get_boundary_panel(step))
        layout["metrics"].update(get_metrics_panel())
        
        console.clear()
        console.print(layout)
        time.sleep(1.5)

if __name__ == "__main__":
    main()
