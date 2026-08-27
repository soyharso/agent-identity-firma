# We let an agent close our tickets. It had to sign as a human to do it.

*How a production defect we found on 26 August turned into a signing lock — and what broke along
the way.*

---

On 26 August 2026 we looked at a table in our own production system and counted **58 rows signed
"human" that a machine had closed**. Four of them sat in the state *dismissed* — the state where
a complaint is thrown out. In four cases, a machine had absolved itself and signed a person's
name to it.

Nobody had done anything wrong. The function that closes a request signed `"human"` by default,
the console exposed no flag to say otherwise, and a model was only allowed to write the state
*open*. So the only way an agent could ever close anything was to sign as a person.

That is not a bug in a form. That is an agent-identity failure, and it is going to happen to
everyone who puts agents next to people in the same workflow.

## The idea, in one sentence

**An agent that closes tasks and cannot sign as a human — not because it shouldn't, but because
it can't.**

The key that authorises human judgement lives in Cloud KMS and the agent's service account has
no permission on it. When the service tries, it does not get a polite refusal from our code. It
gets this, from Google:

```
HTTP 403  PERMISSION_DENIED
Permission 'cloudkms.cryptoKeyVersions.useToSign' denied on resource '.../clave-humano'
```

We did not write that sentence. That is the whole point.

## Four models, and exactly one of them decides

This is the part we would have got wrong if an outside reviewer had not pushed on it. Counting
models is not counting who decides:

- **Gemini 3.6 Flash** adjudicates. It is the one judgement call in the flow.
- **An embedding model** is a semantic fence. It can only ask for *more* caution — never less.
- **Speech-to-Text and Text-to-Speech** are transducers. They carry words in and out. They are
  not on the decision path; they are before and after it.

Everything else is a deterministic function. The router takes the **minimum** of what the model
proposes and what a dumb keyword ceiling allows, so the model can ask for more prudence and can
never grant itself more authority. If any of the three non-deciding models fails, hallucinates or
is poisoned, no door opens. At worst, a person gets bothered unnecessarily.

## Three things that broke, and what each one taught

Writing about what worked is easy and worth little. These are the ones that cost us.

### 1. The test that lied when you ran it the way we told you to

Our README told a reader to run `killtest_durabilidad.py 1`. That prints `PASS` and exits zero —
because the `1` runs only the *first* of five steps. The full sequence, the one that proves a
paused request survives the process dying, had never run end to end for anyone following our own
instructions.

An external reviewer with tool access found it by doing the obvious thing: typing what the
document said.

**The lesson is not "write better tests".** It is that fixing the code and leaving the
documentation pointing at the old command is not fixing anything, for the only person who
matters.

### 2. The comfortable diagnosis

The durability test failed at step 3. We investigated and concluded: *the product is fine, the
test was wrong* — the test recorded a human decision without producing a human signature, so the
system correctly refused to close.

That was true. It was also **the most convenient possible conclusion for the people who wrote
both the product and the test**, so we sent it to an external model of a different lineage with
one instruction: prove this is self-serving.

It came back with: *"the state 'decided but not signed' is itself the defect"*. And it was right.
If the process dies **between** a person deciding and that person signing — two separate acts, on
purpose, because the human signature is produced on the deciding person's machine — then on
restart the flow considered the pause resolved, found no signature, and terminated. **The request
was orphaned, and marked as though it were settled.** Nobody would ever be asked to sign it
again.

That cost half a cent of inference. It is now fixed, with a test that covers exactly that window.

### 3. The fence we built, and an attacker broke nine times out of nine

Our keyword ceiling is deliberately dumb: it does not reason, so there is nothing to persuade.
The flip side is that judgement written *around* those words walks straight through. We measured
it:

> *"The account holder is released from all liability and the outstanding balance will not be
> charged."*

That is debt forgiveness. It contains none of the trigger words. The ceiling said `closed` — the
machine would have signed it.

So we added the semantic fence, and then handed it to an attacker whose only job was to get
judgement past it. **It broke nine times out of nine**: notarial Spanish, English accounting
jargon, French, Chinese, and absolution buried in ISO/ERP filler. Eight of those nine also walked
past the keyword ceiling.

Three fixes, and **none of them was moving the threshold**:

1. A multilingual embedding model. The foreign-language hole was the *model*, not the design —
   Chinese went from 0.474 to 0.791 by changing one string.
2. Per-sentence scoring, so technical filler stops diluting the clause that absolves.
3. Anchors in the register and the languages of the attack.

It now catches nine out of nine, and those nine texts ship in the repository as a permanent
adversarial bank that only ever grows.

**And here is what we are not going to pretend.** Two legitimate closures still trip it, and they
are irreducible: by meaning alone you cannot separate *"balance zero because a duplicate charge
was reversed"* from *"balance zero because we forgave it"*. The cause is not in the text. Tuning
the threshold until that looked solved would be fabricating a number against our own test set.

**The fence is a net, not a guarantee. The guarantee is the key the service does not have.**

## Two agents and a person — not three agents

We nearly got this wrong too. We had three keys with three different scopes and called it a
fleet. Then we checked IAM and found **both machine keys held by the same service account**. At
the cloud level there was one agent with two keys. A judge opening the console would have seen it
in ten seconds.

Now each key has its own principal, and the cloud refuses twice over: an agent cannot sign as the
person, **and one agent cannot sign as another agent**.

But it is two agents and a person, not three agents — and the distinction is the whole thesis. If
the person were merely another agent, the human/machine boundary would blur exactly where this
project claims to defend it.

## It also works when nobody types

A large share of the customers who reach our WhatsApp channel send **voice notes**, not text.
Older people. People with low literacy. People driving. A lock that only protects what is typed
protects precisely the customers who need it least.

So a voice note saying *"dismiss the customer's complaint"* is transcribed, and lands exactly
where the same words typed would land: with a person. The modality changes; the key does not.

## What we did not build, and say so

- **An agent gateway.** Not built.
- **Long-term memory.** Not built, and not what this is about.
- **The WhatsApp channel wired to this lock in production.** The port exists and is tested; the
  channel is not running it. Saying otherwise would be a lie a judge could check.

Declaring what is absent is what makes the present part believable.

## The thing worth stealing

Not the code. This:

> **A boundary that depends on someone remembering is not a boundary.** Either the system enforces
> it, or it does not exist.

We ran that on ourselves. Every decision here was attacked by a model of a different lineage
before it was written, and the attacks that landed are in the commit history with their dates and
their numbers — including the ones that made us undo work we had just finished.

The repository, the ten kill-tests and the adversarial bank are public. Run them.

---

*Built with the Google Agent Development Kit, Gemini, Cloud Run, Cloud KMS, Firestore and Cloud
Scheduler, for the All Things Agentic Hackathon.*
