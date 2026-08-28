# Storyboard and asset checklist

## Assets to prepare

| Asset | Source | On-screen treatment |
|---|---|---|
| Defect ledger | Existing measured record | Highlight 58 and 4; watermark `PREPRODUCTION` |
| Architecture diagram | `README.en.md` Mermaid diagram | Export a clean SVG/PNG; reveal nodes in execution order |
| KMS IAM comparison | Google Cloud Console | Agent key permission visible; human key absence visible |
| 403 output | Live terminal command | Monospace, 36 px minimum, no scrolling during the key line |
| Firestore state | Cloud Console | Show before/after document IDs without customer PII |
| Offline verifier | `src/verificar_sobre.py` | Show command and `OK` output with network disabled if practical |
| Adversarial results | Kill-tests | Show counts, not a wall of logs |
| Brand card | Self-created text card | Cleveria.ai only; operator disclosure at end |

## Shot instructions

### 1. Defect

Frame only the ledger and terminal. No logo. The first spoken sentence must arrive before any
title animation. Keep the `PREPRODUCTION` label visible whenever the ledger is shown.

### 2. Action

Show the scheduler wake-up and the three outcomes in a compact split screen:

- evidence-backed closure → machine signature;
- judgement request → paused for human;
- unsupported assertion → unsigned.

Use arrows and labels, not animated mascots.

### 3. Boundary

This is the hero shot. Type or execute the real request, show the Cloud KMS 403, then hold the
frame. Immediately show the human signing on the human machine and the service verifying the
already-produced signature. Do not cover the error with a logo or music hit.

### 4. Independent proof

Run the verifier, then show one adversarial case and the resulting semantic-fence decision. The
Spanish Model Armor miss is a credibility beat: show it as a limitation followed by the
compensating control.

### 5. Close

Show the Cloud Run service and KMS console for the required Google Cloud proof. End on:

> “The machine does the work it can prove. The person keeps the judgement.”

Below it, show the repository URL and the three-part disclosure for two seconds.

## Recording checklist

- English narration recorded or accurate English subtitles burned in.
- No credentials, tokens, private customer data, or unrelated browser tabs visible.
- Terminal font at least 28 px; browser zoom at least 125%.
- Cloud Console project and service names consistent with the README.
- No claim that QNOWA’s WhatsApp channel is fully integrated with the lock.
- No claim that the agents are in production.
- Three complete takes timed under four minutes.
- Choose by blind review of the first 30 seconds, not by personal preference.
