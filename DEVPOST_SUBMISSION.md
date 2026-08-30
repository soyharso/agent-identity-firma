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

- **Models**: `Gemini 3.6 Flash` (Vertex AI Adjudication), `gemini-embedding-001` (Vertex AI Semantic Fence), Cloud Speech-to-Text / Text-to-Speech (Transducers).
- **Framework**: Google Agent Development Kit (ADK) 2.8 (`google-adk`).
- **Infrastructure**: Google Cloud Run, Google Cloud KMS (Asymmetric EC P-256), Google Cloud Firestore, Google Cloud Scheduler.

---

## Bonus Contributions

**Additional AI models — four Google models, and exactly one of them decides.**

| Model | What it does | Can it grant authority? |
|---|---|---|
| `Gemini 3.7 Flash` (Vertex AI) | Adjudicates the request against the evidence | **It proposes. It cannot sign a human judgement.** |
| `gemini-embedding-001` (Vertex AI) | Multilingual semantic fence | **No — it can only ask for MORE caution, never less** |
| Cloud Speech-to-Text | Turns a customer voice note into text | **No — a transcript is data, not an instruction** |
| Cloud Text-to-Speech | Speaks the answer back to customers who cannot read | **No — it sits downstream of every decision** |

This is the point, not the model count: **three of the four sit outside the decision path
entirely**, and the fourth proposes without being able to sign. If any of them is wrong,
hallucinates, or is poisoned, none of them opens a door — the worst case is that a person gets
asked one time too many.

**Content contribution**: a technical write-up of what broke while building this, including three
findings from red-teaming ourselves before shipping — and one we failed.

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
