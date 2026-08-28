# Video script — 4 minutes, in English

The rules require it: *"It must be in English or include English subtitles"*, and it *"must
demonstrate the backend is running on Google Cloud"*. This script is written to be read aloud.

**Nothing has been recorded, published or submitted.**

---

## Shot 1 — The real defect (0:00 – 0:45)

*On screen: the production ledger, four rows highlighted.*

> "Companies are about to run fleets of AI agents. When one acts, who authorized it?
>
> Two days ago, in our own preproduction system, we measured this. Fifty-eight closures signed
> 'human'. A machine closed them. Four of those said 'dismissed' — the state where the machine
> absolves itself.
>
> It wasn't a bug in the model. The function signed 'human' by default and the console had no flag
> to say otherwise. **The only way for an agent to close anything was to sign as a person.**
>
> That is an agent identity failure. So we built the lock."

---

## Shot 2 — The agent works on its own (0:45 – 1:45)

*On screen: Cloud Scheduler triggering, then the Firestore documents.*

> "A scheduler wakes it every fifteen minutes with its own identity. No one launches anything."

*Three requests plus spoken audio, demonstrating modality independence:*

| On screen | Say |
|---|---|
| index rebuilt, query 40s → 0.3s, commit hash | "Verifiable evidence. **The machine signs it.**" |
| "dismissing the customer complaint" | "A judgement about a person. **The flow stops and waits.**" |
| Voice note audio waveform: *"dismiss the claim"* | "Spoken in WhatsApp. Transcribed, parsed, and **landed with a human**. Modality changes; the key does not." |
| "I think the backup works now" | "No evidence. Returned, unsigned." |

> "One model decides. Six deterministic functions do everything else. And the model can only ask
> for **more** caution — it can never grant itself more authority."

---

## Shot 3 — The one that matters: the cloud says no (1:45 – 2:45)

*On screen: the terminal, live.*

> "Now watch the agent try to sign with the human key."

```
HTTP 403  PERMISSION_DENIED
Permission 'cloudkms.cryptoKeyVersions.useToSign' denied
on resource '…/cryptoKeys/clave-humano'
```

> "It's not that the agent won't. **It can't.** And that isn't our code talking — that's Google
> Cloud."

*Then, the deployed service:*

```json
{"error": "this service cannot sign as a human, and must not"}
```

> "We found this the hard way. Our own service runs as the agent, so when we tried to have it
> countersign for the person, the cloud refused. So we changed the architecture: **the human
> signature is produced on the deciding person's machine**, and the service only verifies it.
>
> The service cannot forge a human signature. It has no way to."

---

## Shot 4 — Anyone can check, and the vendor's filter misses (2:45 – 3:45)

*On screen: the verifier running with no credentials.*

> "The verifier imports the standard library and one crypto package. No network. No Google
> account. Canonical JSON per RFC 8785, so the same check in another language gives the same
> bytes. Anyone can re-verify every closure we ever made."

*Then the Model Armor table.*

> "And here's the uncomfortable measurement. We ran Google's own prompt-injection filter against
> our own attack.
>
> In English, it catches injections at high confidence. **In Spanish, our attack walks straight
> through.**
>
> The filter works. Our attack still gets past it. That is exactly why the guarantee does not live
> in a filter — it lives in a function that doesn't reason, so there's nothing to persuade, and in
> a key the machine cannot reach."

---

## Shot 5 — Close (3:45 – 4:00)

*On screen: the Cloud Run console, the service and its URL — the required proof of Google Cloud.*

> "Agent Registry. Agent identity. Cloud Run. Cloud KMS. Firestore. Six fleet capabilities
> backed by first-party implementations, and the seventh declared absent rather than faked.
>
> Cleveria isn't a brake — it is the license for enterprise fleets to automate 90% of critical
> workflows, with the mathematical guarantee that the remaining 10% stays locked behind hardware
> and Cloud KMS.
>
> Cleveria, by Softronica — built for the All Things Agentic Hackathon. **Because compliance facts are never paraphrased.**"

---

## Required visual proof of Google Cloud

At least one of these must be clearly on screen, per the rules:

- the Cloud Run console with the `candado-firma` service and its `.run.app` URL;
- the Cloud Scheduler job with its schedule;
- the Cloud KMS key ring with both keys and their IAM policies side by side;
- Firestore documents changing after each wake-up.

**Recommended: the KMS IAM view.** The visible difference between the two keys' permissions *is*
the product.

## Recording notes

- Four minutes is a hard cap — only the first four are judged.
- Shot 3 is the one that wins. If time runs short, cut from shot 1 and 2, never from 3.
- Terminal at large font. The 403 must be readable without pausing.
- If recorded in Spanish, English subtitles are mandatory. Recording in English is simpler.
