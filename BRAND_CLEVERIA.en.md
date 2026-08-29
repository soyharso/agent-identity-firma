# Cleveria.ai visual system

## Brand idea

**Cleveria is the boundary that holds.** The mark is a geometric `C` that stops before a
verified green node. The gap is intentional: an agent can approach a capability, but only the
right authority can cross the boundary.

The identity should feel like a precise developer tool, not a security vendor or a chatbot.

## Logo usage

- Primary lockup: `assets/cleveria-logo.svg` on `#0B1020`.
- App/favicon mark: `assets/cleveria-mark.svg`.
- Clear space: at least the height of the green node on every side.
- Minimum lockup width: 180 px digital, 35 mm print.
- Use the SVG source; do not redraw, stretch, add shadows, or place it over busy screenshots.
- The green node is a verification signal, not a generic “success” decoration.
- On a light background, place the primary lockup inside a dark rectangle rather than changing
  the blue/green relationships.

## Color tokens (Updated Palette)

| Token | Hex | Use |
|---|---|---|
| `obsidian-navy` | `#06111F` | Fondo principal y sensación de confianza. |
| `deep-harbor` | `#0B2940` | Superficies, bloques y contraste profundo. |
| `electric-cyan` | `#27E6D2` | Firma criptográfica y señal primaria. |
| `agent-blue` | `#4B6BFF` | Acciones y conexiones entre inteligencias. |
| `trust-violet` | `#8D72FF` | Consejo multiagente y capa secundaria. |
| `ice` | `#E9FFFB` | Texto principal y máxima claridad. |
| `slate` | `#93A8B8` | Metadatos y texto secundario. |
| `signal-coral` | `#FF6B6B` | Alertas y excepciones puntuales. |

**Combinaciones recomendadas:**
- **Base segura:** Obsidian Navy + Ice
- **Señal verificada:** Obsidian Navy + Electric Cyan
- **Consejo multiagente:** Deep Harbor + Agent Blue + Trust Violet

*(Nota: Reemplaza o complementa los tokens heredados anteriores)*

## Typography

- Primary: **Inter** (`600` for headings, `400` for body).
- Fallback: `Arial, sans-serif`.
- Code: **JetBrains Mono** or `DejaVu Sans Mono`.
- Presentation title: 44–56 px.
- Slide body: 26–30 px.
- Terminal evidence: 28–36 px.
- Line height: 1.2 for headings, 1.45 for body.

Never use all caps for the thesis. Use small uppercase labels only for metadata such as
`PREPRODUCTION`, `LIVE IAM`, and `OFFLINE VERIFIER`.

## Presentation template

### Cover

Dark background, logo top-left, one sentence only:

> **The agent can work. It cannot sign as a person.**

Small footer: `Cleveria.ai · Agent identity harness`.

### Evidence slide

Left: a large number (`58`, `4`) in white. Right: the measured explanation. A blue vertical rule
separates fact from interpretation. Keep `PREPRODUCTION` visible as a small amber label.

### Architecture slide

Use the README Mermaid architecture as the canonical source. Build in this order:

1. scheduler and agent in blue;
2. deterministic authority ceiling in white;
3. pause/human handoff in amber;
4. signature verification in green;
5. human-key denial as a red edge labelled `403`.

### Proof slide

The only large red element is:

```text
403 PERMISSION_DENIED
```

Below it, in white:

> **Not “the agent refuses.” The service account has no capability.**

### Limits slide

Two columns: `GUARANTEED` in green and `MITIGATED` in amber. Never show a checkmark beside
Model Armor as though it were an absolute guarantee.

### Closing slide

Logo, thesis, repository URL, and disclosure:

> `Cleveria.ai harness · QNOWA operational scenario · Built and operated by Softronica.co`

The disclosure is intentionally present but visually subordinate to the technical artifact.

## Motion and image direction

- Use diagrams, console evidence, ledger rows, and terminal output as the imagery.
- Animate paths linearly at 250–450 ms; never bounce or overshoot.
- Freeze on the 403 for two seconds.
- Stop all animation at the human handoff.
- Avoid stock imagery, 3D server rooms, robot faces, padlocks, shields, and “AI magic” particles.
- If a background texture is needed, use a faint grid at 4% opacity, never a circuit-board photo.

## Audio direction

The default is clean narration with no music. If a bed is required, use a quiet CC0/self-recorded
instrumental at 70–78 BPM, ducked below -30 dB under speech and muted at the 403 and verifier.
No lyrics, vocals, dramatic risers, glitch sounds, or “hacking” effects.
