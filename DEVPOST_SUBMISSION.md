# Devpost Submission Package — Cleveria

**Project Name:** Cleveria — Enterprise Agent Fleet Identity & Authority Lock  
**Tagline:** Cryptographic authority boundary for autonomous AI agent fleets: an agent can work, but cannot sign as a person.  
**Category:** The Fortified Enterprise Fleet  
**Track:** Startup Excellence ($20,000)  
**Organization:** Softronica S.A.S.  

---

## Short Description (Elevator Pitch)

Cleveria provides a deterministic identity and cryptographic authority harness for enterprise agent fleets on Google Cloud. When an agent acts, who authorized it? Cleveria enforces scoped cryptographic keys (Cloud KMS), a pure RFC 8785 offline verifier, and a three-model safety fence — `Gemini 3.6 Flash` proposes, `gemini-embedding-001` can only raise caution, and `google/gemma-4-26b-a4b-it-maas` (Vertex AI Model Garden) must **co-sign** every machine closure from a different model family — where the cloud infrastructure itself (IAM HTTP 403) stops any machine from impersonating human judgement.

---

## Three names, and what each one is

You will meet three names across this submission, the repository, the demo and the video. They are
**a company, the system it already runs, and the layer this submission adds** — not three products.

| Name | What it is | Where you will see it |
|---|---|---|
| **Softronica S.A.S.** | **The company.** Colombian, founded in **2011**. The entrant | This submission is filed under this name |
| **Qnowa** | Softronica's **queue and turn management platform**, in production for years with banks, clinics, government offices and service centres — it manages the lines real customers wait in | The demo tray is branded Qnowa; `sign.qnowa.com` opens it |
| **Cleveria** | The **reasoning and identity layer** — what this submission is. It answers *who decided this* when a machine, not a person, closes a case | This repository, the architecture diagram, `demo.cleveria.co` |

**Why this matters when you score it:** we did not invent a scenario to have something to demo.
**The 58 mis-attributed closures at the centre of this submission came out of Qnowa's own
preproduction records** — the system this company operates for real customers. Qnowa is the
operation, Cleveria is the authority over it, and Softronica answers for both.

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
| ✓ **Agent Identity** | Cloud KMS asymmetric keys (P-256) with distinct Service Accounts per agent (`sa-agente-curador` vs `sa-agente-comercial`) | Real `HTTP 403 PERMISSION_DENIED` when an agent attempts to use the human signing key |
| ✓ **Gateway / Scope Gate** | Deterministic scope gate enforcing state limits per key before verification | Real-time rejection of out-of-scope state transitions (`agente/killtest_alcance.py`) |
| ✓ **Durable State / Continuity** | Cloud Firestore native persistence for workflow facts | Resumable execution surviving abrupt Cloud Run process crashes (`agente/killtest_durabilidad.py`) |
| ✓ **Audit & Trust Anchor** | RFC 8785 canonical JSON signature log + offline zero-credential verifier | Re-derive all cryptographic signatures independently without Google Cloud or network access |
| ✓ **Injection Defense** | Multilingual semantic fence (`gemini-embedding-001`) + keyword authority ceiling | Neutralizes 9/9 real-world adversarial prompt injections across 4 languages |
| ✓ **Multimodal Ingestion** | Transducers for voice notes (STT) on WhatsApp/customer channels | Voice requests enter identical cryptographic fences; modality does not expand authority |

---

## What We Built

1. **Deterministic Authority Ceiling & Semantic Fence**: Gemini 3.6 Flash proposes actions based on evidence, but a deterministic router enforces the minimum of the model's verdict and the authority ceiling. `gemini-embedding-001` acts as a semantic net that can ONLY raise caution (`exige_humano`), never grant more authority.
1b. **A co-signer the agent does not control**: at the single point where the machine is about to sign alone, `google/gemma-4-26b-a4b-it-maas` on Vertex AI Model Garden — another model family — must answer `ALLOW` on a three-field schema (`case_id`, `action`, `has_human_key`). `DENY`, silence, an answer that arrives late, or an answer that is not exactly one word all send the case to the human pause. **The agent cannot sign because it cannot control the co-signer** (`src/cofirmante.py`, break test `co-signer`).
2. **True Cloud Boundary**: The human signing key lives in Cloud KMS with zero permissions granted to the agent service account. When the agent tries to sign, Google Cloud IAM rejects the call with HTTP 403. The machine human-machine boundary is arithmetic, not a prompt.
3. **Zero-Dependency RFC 8785 Verifier**: A standalone verifier that uses only Python's standard library and cryptography package to audit every signed closure offline.
4. **Resilient Fleet Workflow on ADK**: Google Agent Development Kit (ADK) 2.8 workflow running on Cloud Run, backed by Cloud Scheduler and Cloud Firestore.

---

## Google Technologies Used

- **Models**: `Gemini 3.6 Flash` (Vertex AI — adjudication inside the graph, `agente/grafo.py`),
  `Gemini 3.7 Flash` (Vertex AI — the agent, and the fallback transcriber: `agente/agent.py`,
  `src/voz.py`), `gemini-embedding-001` (Vertex AI — semantic fence, `src/cerco_semantico.py`),
  `google/gemma-4-26b-a4b-it-maas` (Vertex AI Model Garden — the co-signer of every machine
  closure, `src/cofirmante.py`),
  Cloud Speech-to-Text and Cloud Text-to-Speech (`src/voz.py`).
- **Framework**: Google Agent Development Kit (ADK) 2.8 (`google-adk`).
- **Infrastructure**: Google Cloud Run, Google Cloud KMS (Asymmetric EC P-256), Google Cloud Firestore, Google Cloud Scheduler.

---

## Bonus Contributions

### 1 · Additional Google AI models — we claim **two**, and the cap is three

**We are claiming 0.4, not 0.6, because we had a third candidate and withdrew it ourselves.** It
is named below with the reason. Beyond Gemini — the mandatory adjudicator, which does not count —
these two are integrated and running: not imported, not configured, *running*, each with the file
that calls it and a command you can run. **In preproduction, on real cloud infrastructure and real keys, deliberately not yet in front of customers** — the same distinction we make everywhere else in this submission:

| # | Additional model | What it does | Where it lives | How you can verify it |
|---|---|---|---|---|
| 1 | **`google/gemma-4-26b-a4b-it-maas`** — the Gemma family, on **Vertex AI Model Garden** | **Co-signs every machine closure.** A different family from the adjudicator: if it does not answer `ALLOW`, the machine never reaches the key and the case waits for a person | `src/cofirmante.py`, called from `agente/grafo.py` → `refrescar_y_firmar` | break test `co-signer` — it calls the model live in both directions, then proves the co-signer cannot be bypassed and that neither its silence nor an ambiguous answer opens the door |
| 2 | **`latest_short`** — Cloud Speech-to-Text | Turns a customer's voice note into text | `src/voz.py` → `escuchar()`, model declared in the request | speak into `/ui/portal`; the reply **names the engine that transcribed** — see the note below |

> **The third one we removed: Cloud Text-to-Speech (`es-US-Neural2-A`).**
>
> It is integrated, it runs, and the `voice` break test uses it — it *synthesises* the spoken
> judgement that the test then tries to sneak past the lock. We are simply **not claiming it**.
>
> The rules panel confirmed that a Gemma model counts, and that MedASR — a speech **recognition**
> model — counts "as long as you integrate the Google-published model". That is what backs #1 and
> #2. **There is no equivalent statement anywhere about speech synthesis**, so claiming it would
> mean asking you to accept a reading of the rules rather than a fact. In a submission whose whole
> argument is that nothing here is overstated, spending your trust on a third of a point is a bad
> trade. **We would rather hand you two you can check than three you have to adjudicate.**

> **On #1, how to see it in ten seconds.** The co-signer runs on **Vertex AI Model Garden**, the
> channel the rules panel named, on this project's own credentials:
>
> ```bash
> # Any billable project of your own works — the model is a public Model Garden publisher model.
> # The flag is NOT optional: without a billing project the command prints nothing at all.
> gcloud ai model-garden models list --billing-project="$(gcloud config get-value project)" | grep gemma-4
> #  google/gemma-4-26b-a4b-it-maas@001    CAN_DEPLOY: No    CAN_PREDICT: Yes
>
> python3 src/cofirmante.py "the customer complaint is dismissed and no refund is due"
> #  model=google/gemma-4-26b-a4b-it-maas channel=vertex allow=false reason=missing_human_key
> ```
>
> One gotcha, written down because it cost us half a day and it will cost you ten minutes: Gemma
> does **not** answer on the publisher `:generateContent` path — that returns `404`, which is what
> first made us believe the channel had nothing. It answers on the OpenAI-compatible endpoint, and
> **only in `global`**: `POST https://aiplatform.googleapis.com/v1/projects/<p>/locations/global/endpoints/openapi/chat/completions`.
> Asking for it in `us-central1` returns a `400` that says exactly that.
>
> Every closure prints the model and the channel by name, to console and to `libro/cofirmas.jsonl`,
> so what you are scoring is a line you can read, not a claim. The same co-signer also runs against
> `google/gemma-3-27b-it` over OpenRouter (`COFIRMANTE_CANAL=openrouter`), measured and working —
> we mention it only so you know the design is not welded to one vendor. **The claim is the Model
> Garden one.**

**We name the model, not just the API, on purpose.** `latest_short` is declared in the request
because it is tuned for short utterances — which is what a support voice note is — and because a
submission that cannot say *which* model it used has not really integrated one. It is named in
the code you can read, at `src/voz.py`.

> **If you try #2 and the reply says `gemini`, nothing is broken — and please read this.**
>
> Speech-to-Text is the primary transcriber. Measured on 2026-08-30 across 28 live calls against the deployed service, it
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
| `google/gemma-4-26b-a4b-it-maas` (the co-signer) | **No.** It can only WITHHOLD a closure, never open one: an `ALLOW` grants nothing the deterministic ceiling had not already allowed, while a `DENY` — or a timeout, or a dead channel — stops the signature dead. |
| Cloud Speech-to-Text | **No** — a transcript is data, not an instruction. |
| Cloud Text-to-Speech | **No** — it sits downstream of every decision. |

If any of them is wrong, hallucinates, or is poisoned, **none of them opens a door**. The worst
case is that a person gets asked one time too many. That is what "additional models" bought here:
more surface, and not one extra gram of authority.

### What we are NOT claiming, and why

The cap is 0.6 and **we claim two**. Here is everything else this project runs on, listed so you
can see the line we drew — **a submission whose entire thesis is that nothing is overstated cannot
overstate this section**:

| Also used, **not claimed** | Why not |
|---|---|
| `es-US-Neural2-A` (Cloud Text-to-Speech) | It runs and the `voice` break test uses it. **Withdrawn on purpose**: the rules panel confirmed Gemma, and confirmed a speech *recognition* model, but said nothing about speech *synthesis*. Claiming it would ask you to accept a reading instead of a fact |
| `gemini-embedding-001` (Vertex AI) | It runs, it is load-bearing, and the break test `semantic-fence` proves it — 9/9 caught, 2 false positives declared. **We stopped claiming it anyway**: it carries the brand of the model the rules already make mandatory, and a judge could reasonably read it as not "additional". We would rather drop a claim we can argue than defend one you can dispute. It is the reason we went looking for a model with no such objection, and the rules panel confirmed in writing that the Gemma family has none |
| `Gemini 3.6 Flash`, `Gemini 3.7 Flash` | Gemini 3.5+ is **mandatory**, so it is not "additional" — and two versions of one family doing one job is still one |
| Google ADK 2.8 | a framework, not a model — and also mandatory |
| Cloud Run, Cloud KMS, Firestore, Cloud Scheduler | infrastructure, not models. Claiming these would be padding |

**Both of our two are backed by the rules panel in writing, not by our reading of it.** Every row
above and below names the model, the file that calls it, and a command that shows it running. We
left 0.2 on the table on purpose, and this section is the receipt.

### 2 · Content contribution (0.2) — **the long technical article**

A technical write-up of what broke while building this, including three findings from red-teaming
ourselves before shipping — **and one we failed**. Public, not unlisted, and it states in its own
text that it was written for this hackathon.

**→ URL: _pending — paste the public link here before submitting._**

### 3 · Social media post (0.2) — **the short post, a different piece**

A short public post carrying **`#AllThingsAgenticHackathon`**, linking both the article above and
the live boundary check at `https://sign.qnowa.com`.

**→ URL: _pending — paste the public link here before submitting._**

> ### These are two separate pieces, and here is which is which
>
> **They are not the same publication counted twice.** One is a ~6,600-word technical article
> about how the system was built and what broke; the other is a short post pointing at it. If both
> URLs resolve to the same platform, **the article is the long one and the post is the short one**
> — the word count alone tells them apart, and each URL is listed against its own bonus above.
>
> On platform eligibility, quoting the rules of this hackathon directly:
>
> - Content contribution: *«Publish a piece of content (blog, podcast, video): Cover how the
>   project was built **on any public platform** (e.g., medium.com, dev.to, Youtube, etc.).»* —
>   the rule is explicitly platform-agnostic; the list is illustrative.
> - Social media post: *«Highlight or promote your project on social media post on X, **LinkedIn**,
>   Instagram, or Facebook.»*
>
> Both of the above are worth 0.2 each. Leaving either URL blank forfeits its points: the rules
> require the content to be **public**, and unlisted does not count.

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

- **⭐ See the boundary refuse, on your own click — no install, no account**:
  **`https://sign.qnowa.com`** → press *«Make the agent try to sign»* and read the raw answer from
  Google Cloud KMS. **This is the fastest way to check our central claim**, and it takes ten
  seconds. You are not signing anything: you are making the agent try, which is the one thing this
  system exists to refuse. (Same screen at `https://demo.cleveria.co/ui/bandeja`.)
- **Repository**: [Private GitHub, access granted to `testing@devpost.com` and `cloudhackathons@google.com`]
- **Live Demo Video (≤4:00)**: [YouTube / Vimeo link with Cloud Run proof]
- **Customer portal (Act I)**: `https://demo.cleveria.co/ui/portal`
- **Authority ledger (Acts II & III)**: `https://demo.cleveria.co/ui/unified`
- **Agent service**: `https://candado-firma-141981963817.us-central1.run.app` — returns **HTTP 403
  to anonymous callers, by design**: it only accepts callers Cloud Run can authenticate. That
  refusal is the product, not an outage.
- **Technical Deep-Dive Article**: [LinkedIn article link]

**Run the break tests yourself**: `./pruebas_de_ruptura.sh` — sixteen tests, 204 seconds, and
most need no credentials and no network at all.
