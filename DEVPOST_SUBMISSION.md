# Devpost Submission Package — Cleveria

**Project Name:** Cleveria — Enterprise Agent Fleet Identity & Authority Lock  
**Tagline:** Cryptographic authority boundary for autonomous AI agent fleets: an agent can work, but cannot sign as a person.  
**Category:** The Fortified Enterprise Fleet  
**Track:** Startup Excellence ($20,000)  
**Organization:** Softronica S.A.S.  

---

## Short Description (Elevator Pitch)

Cleveria provides a deterministic identity and cryptographic authority harness for enterprise agent fleets on Google Cloud. When an agent acts, who authorized it? Cleveria enforces scoped cryptographic keys (Cloud KMS), a pure RFC 8785 offline verifier, and a dual-model safety fence (`Gemini 3.6 Flash` + `gemini-embedding-001` on Vertex AI) where the cloud infrastructure itself (IAM HTTP 403) stops any machine from impersonating human judgement.

---

## The "Unlikely Hero": The Hispanic Operations Supervisor

*Built for the Hispanic operations supervisor who runs real customer-attention queues in a LatAm BPO — not for a generic 'enterprise admin'.*

We operate real customer-attention queues and healthcare/BPO workflows in Colombia. When agents started acting autonomously across ticket queues and WhatsApp channels, operations supervisors faced an impossible dilemma: either keep all tickets manual (crushing human throughput) or give agents unrestricted closure authority (risking illegal debts forgiven, dismissed customer claims, and compliance chaos).

Cleveria was built specifically for this operational supervisor: **the machine resolves and signs everything it can prove with verifiable evidence, but when subjective judgement or liability is involved, the workflow pauses deterministically for human cryptographic authorization.** The supervisor retains definitive control without becoming a bottleneck.

---

## Fleet Capabilities Coverage (The Fortified Enterprise Fleet)

| Fleet Subsystem | Cleveria First-Party Implementation | How It Is Proven Live |
|---|---|---|
| ✓ **Agent Registry** | Versioned Agent Cards (`agent_cards/catalog.json`) generated directly from `claves/directorio.json` | Deterministic generation via `generar_agent_cards.py`; immutable in Git history |
| ✓ **Agent Identity** | Cloud KMS asymmetric keys (P-256) with distinct Service Accounts per agent (`sa-agente-curador` vs `sa-agente-qnowa`) | Real `HTTP 403 PERMISSION_DENIED` when an agent attempts to use the human signing key |
| ✓ **Gateway / Scope Gate** | Deterministic scope gate enforcing state limits per key before verification | Real-time rejection of out-of-scope state transitions (`agente/killtest_alcance.py`) |
| ✓ **Durable State / Continuity** | Cloud Firestore native persistence for workflow facts | Resumable execution surviving abrupt Cloud Run process crashes (`agente/killtest_durabilidad.py`) |
| ✓ **Audit & Trust Anchor** | RFC 8785 canonical JSON signature log + offline zero-credential verifier | Re-derive all cryptographic signatures independently without Google Cloud or network access |
| ✓ **Injection Defense** | Multilingual semantic fence (`gemini-embedding-001`) + keyword authority ceiling | Neutralizes 9/9 real-world adversarial prompt injections across 4 languages |
| ✓ **Multimodal Ingestion** | Transducers for voice notes (STT) on WhatsApp/customer channels | Voice requests enter identical cryptographic fences; modality does not expand authority |

---

## What We Built

1. **Deterministic Authority Ceiling & Semantic Fence**: Gemini 3.6 Flash proposes actions based on evidence, but a deterministic router enforces the minimum of the model's verdict and the authority ceiling. `gemini-embedding-001` acts as a semantic net that can ONLY raise caution (`exige_humano`), never grant more authority.
2. **True Cloud Boundary**: The human signing key lives in Cloud KMS with zero permissions granted to the agent service account. When the agent tries to sign, Google Cloud IAM rejects the call with HTTP 403. The machine human-machine boundary is arithmetic, not a prompt.
3. **Zero-Dependency RFC 8785 Verifier**: A standalone verifier that uses only Python's standard library and cryptography package to audit every signed closure offline.
4. **Resilient Fleet Workflow on ADK**: Google Agent Development Kit (ADK) 2.8 workflow running on Cloud Run, backed by Cloud Scheduler and Cloud Firestore.

---

## Google Technologies Used

- **Models**: `Gemini 3.6 Flash` (Vertex AI — adjudication inside the graph, `agente/grafo.py`),
  `Gemini 3.7 Flash` (Vertex AI — the agent, and the fallback transcriber: `agente/agent.py`,
  `src/voz.py`), `gemini-embedding-001` (Vertex AI — semantic fence, `src/cerco_semantico.py`),
  Cloud Speech-to-Text and Cloud Text-to-Speech (`src/voz.py`).
- **Framework**: Google Agent Development Kit (ADK) 2.8 (`google-adk`).
- **Infrastructure**: Google Cloud Run, Google Cloud KMS (Asymmetric EC P-256), Google Cloud Firestore, Google Cloud Scheduler.

---

## Bonus Contributions

### 1 · Additional Google AI models — we claim **three**, the maximum (0.6)

Beyond Gemini, which is the model that adjudicates, **three further Google models are integrated
and running in production** — not imported, not configured, *running*, each with the file that
calls it and how you can see it work:

| # | Additional model | What it does | Where it lives | How you can verify it |
|---|---|---|---|---|
| 1 | **`gemini-embedding-001`** (Vertex AI) | Multilingual semantic fence: catches a judgement phrased so it dodges the keyword ceiling | `src/cerco_semantico.py` | break test `semantic-fence` — 9/9 caught, 2 false positives **declared** |
| 2 | **`latest_short`** — Cloud Speech-to-Text | Turns a customer's voice note into text | `src/voz.py` → `escuchar()`, model declared in the request | speak into `/ui/portal`; the reply **names the engine that transcribed** — see the note below |
| 3 | **`es-US-Neural2-A`** — Cloud Text-to-Speech | Speaks the answer back to customers who cannot read | `src/voz.py` → `hablar()` | break test `voice` — it *synthesises* the spoken judgement it then tries to sneak past the lock |

**We name the model, not just the API, on purpose.** `latest_short` is declared in the request
because it is tuned for short utterances — which is what a support voice note is — and because a
submission that cannot say *which* model it used has not really integrated one. `Neural2` is the
voice family behind the spoken reply. Both are named in the code you can read.

> **If you try #2 and the reply says `gemini`, nothing is broken — and please read this.**
>
> Speech-to-Text is the primary transcriber. Measured on 2026-08-30 across 28 production calls, it
> answers `503 Service Unavailable` on roughly **80 % of individual attempts** from our service
> account, while the identical request from a user credential returns `200` every time. It is not
> our quota — the project is billed and allows 900 requests/minute — it is **provider flakiness**,
> so we retry it three times before giving up. **After that change: 9 of 10 calls transcribe with
> `"motor":"speech-to-text","respaldo_usado":false`.**
>
> On the tenth, the request **fails over to Gemini and the response says so** —
> `"motor":"gemini","respaldo_usado":true`, with the failed attempts listed in `intentos_fallidos`.
>
> We are pointing at this instead of hiding it because it is the same principle as the rest of the
> submission: **the system reports what actually happened, including when its first choice
> failed.** A demo that silently swapped engines and reported success would be the cheap version of
> this, and it is exactly the thing we built the break tests to catch.

**And the count is not the point.** Every one of the three sits **outside the decision path**:

| Model | Can it grant authority? |
|---|---|
| Gemini (the adjudicator) | **It proposes. It cannot sign a human judgement** — no key. |
| `gemini-embedding-001` | **No** — it can only ask for MORE caution, never less. |
| Cloud Speech-to-Text | **No** — a transcript is data, not an instruction. |
| Cloud Text-to-Speech | **No** — it sits downstream of every decision. |

If any of them is wrong, hallucinates, or is poisoned, **none of them opens a door**. The worst
case is that a person gets asked one time too many. That is what "additional models" bought here:
more surface, and not one extra gram of authority.

### What we are NOT claiming, and why

The cap is 0.6 and we claim exactly three. Here is everything else this project runs on, listed so
you can see the line we drew — **a submission whose entire thesis is that nothing is overstated
cannot overstate this section**:

| Also used, **not claimed** | Why not |
|---|---|
| `Gemini 3.6 Flash`, `Gemini 3.7 Flash` | Gemini 3.5+ is **mandatory**, so it is not "additional" — and two versions of one family doing one job is still one |
| Google ADK 2.8 | a framework, not a model — and also mandatory |
| Cloud Run, Cloud KMS, Firestore, Cloud Scheduler | infrastructure, not models. Claiming these would be padding |

**If you disagree with any one of our three, subtract it.** We would rather you score us 0.4 on a
claim you can audit than 0.6 on one you cannot. Every row above and below names the model, the
file that calls it, and a command that shows it running.

### 2 · Content contribution (0.2)

A technical write-up of what broke while building this, including three findings from red-teaming
ourselves before shipping — **and one we failed**. Published publicly (not unlisted), and it
states that it was written for this hackathon.

**→ URL: _pending — paste the public link here before submitting._**

### 3 · Social media post (0.2)

Posted publicly with **`#AllThingsAgenticHackathon`**.

**→ URL: _pending — paste the public link here before submitting._**

> Both of the above are worth 0.2 each and neither needs a line of code. Leaving the URL blank
> forfeits the points: the rules require the content to be **public**, and unlisted does not count.

---

## For judges: read the code, not just the README

The interesting part of this repository is not what it does — it is that **the code says why each
decision was made, including where it must NOT be trusted**. Three places worth thirty seconds:

- `app_real.py` — a mock 403 that **labels itself as a mock**, with a comment reading *"do not
  record this route as proof of the cryptographic boundary"*. The real 403 comes from Cloud KMS in
  `servicio/main.py`, and the code tells you which is which.
- `src/verificar_sobre.py` — every rejection verdict carries the reason it exists, including one
  that is **redundant when the text differs and essential when it does not**: template answers in
  customer support share a hash, and only the case binding separates them.
- `agente/killtest_reutilizacion.py` — a break test that starts by proving **its own control is
  redundant in the easy case**, before showing the case where it is the only thing that saves you.

We would rather you find our limits in our own comments than in your reading of them.

---

## Verification & Quick Links

- **Repository**: [Private GitHub, access granted to `testing@devpost.com` and `cloudhackathons@google.com`]
- **Live Demo Video (≤4:00)**: [YouTube / Vimeo link with Cloud Run proof]
- **Customer portal (Act I)**: `https://demo.cleveria.co/ui/portal`
- **Authority ledger (Acts II & III)**: `https://demo.cleveria.co/ui/unified`
- **Agent service**: `https://candado-firma-141981963817.us-central1.run.app` — returns **HTTP 403
  to anonymous callers, by design**: it only accepts callers Cloud Run can authenticate. That
  refusal is the product, not an outage.
- **Technical Deep-Dive Article**: [dev.to link]

**Run the break tests yourself**: `./pruebas_de_ruptura.sh` — eleven tests, and most need no
credentials and no network at all.
