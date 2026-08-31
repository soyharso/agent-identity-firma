# Fifty-eight machine closures wore a human signature. We found them in preproduction.

*The boundary we built so it stops being possible, the four things that broke while we built it, and the one we could not fix.*

On 26 August 2026, we counted **58 rows marked "human" even though a machine had closed them**. Four were in the *dismissed* state, where a customer's complaint is thrown out. The agents were in preproduction, which is where a defect like this is supposed to surface — and the records were intact, which is how we could count it at all.

No model chose to impersonate anyone. A default field and a missing system state made the wrong attribution the only path available to an agent. The repair was not a better prompt. **It was a boundary the service could not cross.**

**And be precise about the word in the title, because we were not at first:** those 58 rows carried no cryptographic signature at all. They carried a *field* that said `human` — a label any code could write, which is exactly the problem. The signatures came later, and they came because a label is not an identity. The closing function wrote `"human"` by default, the console exposed no flag to say otherwise, and the schema had no state meaning *"a machine closed this."* Nothing was hidden and no customer decision was reversed. What was wrong was the **shape of the system**: it made the correct action impossible to express.

That is not a bug in a form. It is an agent-identity failure, and it is structural: a system that cannot express *"a machine did this"* will record that a person did.

## If you only read this far

**The problem.** The moment you put agents in a queue next to people, someone has to answer *who decided this* — and most systems answer it with a field that anybody's code can write. That is not an identity. It is a label.

**What we did.** We stopped asking the software to be honest about who it is, and made the question unanswerable in the wrong direction: the key that signs human judgement is one the machine has no permission to touch. The refusal comes from the cloud, not from us. Then a model from a different family has to agree before the machine signs at all, and a ledger chains every signature so that altering or reordering one is detectable.

**What it buys.** Not caution — **a wider safe lane.** The machine closes what it can prove, and only after clearing a keyword ceiling, two semantic fences, a co-signer from another model family and a mediator that holds the write credential. It is not one brake, it is five, and each one can only ever subtract. We have not measured throughput or reviewer load, so we are not going to claim either: what we can say is that the boundary is arithmetic rather than a habit, and that a supervisor can trust an arithmetic boundary in a way they cannot trust a convention.

**What it costs.** Somebody gets bothered unnecessarily about twice in every batch we measured, and we would rather tell you that number than tune it away.

The rest of this is how, including the four things that broke while we built it.

## Who is writing this, because it changes what the number means

**Softronica S.A.S.** is a Colombian company, founded in 2011. Its product **Qnowa** is a queue
and turn management platform that has run in production for years with banks, clinics, government
offices and service centres — it manages the lines real customers wait in, and the tickets that
get closed at the end of them. **Cleveria** is the reasoning and identity layer we are describing
here: the part that answers *who decided this* once machines start closing those tickets next to
people.

We say this early for one reason. **The 58 rows are not from a synthetic dataset.** They are from
Qnowa's own preproduction records — our queues, our schema, our defect. We did not build a
scenario in order to have a problem to solve; we found the problem in the system we operate, and
this is what we built because of it.

That is also why the demo you will see later is branded Qnowa and not Cleveria. **Qnowa is the
operation. Cleveria is the authority over it. Softronica answers for both.**


## Three claims, and we tested all three on ourselves

Everything below is one of these:

1. **Identity.** If an agent shares a principal, a service account or a credential scope with people or with other agents, machine actions get recorded as human ones. *We found both of our machine keys held by the same service account. Section: "Two agents and a person."*
2. **Expressiveness.** If the schema has no state meaning "closed by a machine," the only closing path runs through the one that says human. *That is the 58 rows.*
3. **Guarantee.** A safeguard written in application code or in a system prompt is negotiable. The one we could not negotiate with came from the platform. *That is the 403 below.*

## The idea, in one sentence

**An agent that closes tasks and cannot sign as a human — not because it shouldn't, but because it can't.**

The key that authorises human judgement lives in Cloud KMS. The agent's service account holds no binding on it. When the service tries, it does not get a polite refusal from our code. It gets this, from Google:

```
HTTP 403  PERMISSION_DENIED
Permission 'cloudkms.cryptoKeyVersions.useToSign' denied on resource '.../clave-humano'
```

We did not write that sentence. That is the whole point.

The mechanism is IAM, not clever code:

```bash
# Each agent has its own principal. This one may sign with its own key, and only that one.
gcloud kms keys add-iam-policy-binding clave-agente \
  --member="serviceAccount:sa-agente-curador@$PROJECT..." --role="roles/cloudkms.signer"

# A second agent, a second principal, a second key — never shared. This one is the
# customer-facing agent, and its scope is a single state: informed.
gcloud kms keys add-iam-policy-binding clave-agente-qnowa \
  --member="serviceAccount:sa-agente-comercial@$PROJECT..." --role="roles/cloudkms.signer"

# On the human key, no binding is granted to any machine principal.
```

**And here is the honest limit of that claim, because a reviewer pushed on it and was right.** The absence of a binding on that key is not by itself a proof of impossibility: a permission can be inherited from the project, the folder or the organisation, and a 403 for one service account is not a 403 for every principal. So do not take the absence as the evidence. Take the refusal, and check it the way we do:

```bash
# The effective policy on the human key, not the one we think we set
gcloud kms keys get-iam-policy clave-humano --location=... --keyring=...
# and the call itself, from the agent's own identity, which must fail
python3 agente/killtest_alcance.py     # or ./pruebas_de_ruptura.sh for all sixteen
```

What we verify is narrow and we state it narrowly: **the agent identity that runs this workflow cannot sign with the human key, and the refusal is issued by Google rather than by us.** That is a smaller claim than "impossible for anyone", and it is the one we can hand you.

**Anything you can argue with is not a control.** Which state each key may authorise lives in one file, `claves/directorio.json`, not in code. The verifier asks a single question — *is this state within the scope of the key that signed?* — so there are no per-state rules to age badly. Whoever controls that file controls who counts as human, which is why it sits in the repository with its history, where changing it leaves a commit, rather than in a database row where it does not.

### The ledger proved what was in it, not that it was all there

Here is the same mistake again, found a fourth time and in a different place.

Every signature goes into a ledger, one row per closure, each row signed. We treated that as an audit trail. Then someone asked the obvious question and the answer was bad: **delete a whole row and nothing notices.** Every remaining signature still verifies, because each one only ever covered its own envelope. The ledger proved that what was in it was genuine. It never proved that all of it was there.

The fix is one field: each row now carries the hash of the row before it, covered by the same signature. Delete one, reorder two, insert one — the chain breaks and the verifier says where. Two more break tests, `ledger-chain` and `ledger-order`.

And the honest part: **rows written before the chain existed cannot be retrofitted into it.** So the verifier does not pretend. It reports the chained rows and the earlier ones separately, as a declared prefix. A ledger that started chaining halfway through can say so, or it can lie; there is no third option.

**And then we attacked the chain, which is how we learned what it does not do.** Four cases, each one run against a copy of the real ledger:

| What we did to the ledger | Caught? | By what |
|---|---|---|
| Altered a field **inside a signed envelope** | **Yes** | the signature |
| Deleted or reordered a row **inside the chain** | **Yes** | the chain |
| Altered the row's **wrapper fields**, outside the envelope | **No** | the signature covers the envelope, not the row around it — see below |
| Deleted the **last** row — or the last ten | **No** | what remains is a shorter chain, still consistent |

The last one is the interesting one. **A backward chain of hashes cannot detect its own truncation**, because nothing inside a file knows how long the file was supposed to be. So we built the anchor, on the last day — and before anything else, the honest status: **the mechanism is installed and tested, and it is not yet protecting anything.** An anchor only starts guarding a ledger once a person signs the first one, and at the time of writing nobody had. Fourteen adversarial cases pass against copies of the ledger; zero real anchors exist. Those are two different sentences and we are not going to blur them.

The design took two corrections that are worth more than the feature.

**First correction: the 403 is not enough.** Signing the anchor with the human key means the agent cannot *invoke* it — but it never stopped the agent from choosing *what the key signs*. An agent that truncates the ledger from 59 rows to 45 and then hands a person an anchor that says 45 gets a human signature on a mutilated book. The fix is not asking the person to look harder. **The anchors chain to each other, and the verifier refuses any anchor whose row count went down.** The previous anchor already says 59, signed, and the writer cannot rewrite it.

**Second correction: do not anchor the hash of the bytes.** That was our first instinct and it is a false-alarm factory — any innocent rewrite screams *tampered*, and the first false alarm teaches everyone to ignore the alarm. What gets anchored is the digest of the **canonical bodies**, keys sorted. That covers the unchained prefix and the wrapper fields too, so one mechanism closes three of the four gaps above instead of one.

**And the hole that is left, stated carefully — because our first version of this paragraph overstated it, and it was a person who narrowed it back down.**

The machine cannot finish this attack on its own. It can delete the anchor history and truncate the ledger, but it cannot mint a replacement anchor: that needs the human key, and the human key is the thing it demonstrably cannot reach. What it is left holding is **an unanchored ledger**, and an unanchored ledger is exactly what the verifier notices.

**And there is a bigger gap than that one, so it goes first.** An anchor is only issued when a person signs, so **everything written since the last anchor is still truncable**. The verifier reports how many rows fall outside the anchor, and an outside judge on this design said the right thing about that: reporting a gap is not closing it. That is the real limit, and it is wider than the exotic one below.

**The exotic one completes only if a person then signs the truncated book without looking.** Which means the last hole in a system built on cryptography is not cryptographic. It is a human being signing something they did not read — and every control here exists to make that the *only* remaining way to get it wrong, not to pretend it is impossible.

**About that third row, because the distinction matters and we got it wrong at first.** The ledger has two layers. Inside the signed envelope: the case, the state it closed to, who curated it, the content hash, the timestamp and the algorithm — **including `estado_destino`, which is the field that decides**. Outside it: `dictamen`, `veredicto`, `ts` and the chain fields, which are an index for reading at a glance. **Nobody can forge a signed closure.** What someone with file access could forge is the label you skim. So the rule is the one our own dashboard now prints: *re-verify against the envelope, never against the label.*

And a fifth thing we would rather say than have you notice: **the rows written before the chain existed are not protected by it at all**. The verifier reports them separately and says so in its own output — *of those rows you can say they are authentic, not that they are all there.*

**A signature proves authorship of what it covers. A chain proves nothing inside it was altered or reordered. Neither proves nothing was cut off the end.**

**And that sentence contains the weakness, so we will say it rather than let you find it.** A commit is a trace, not a lock. Anyone who can push can widen a key's scope, and the verifier will then agree with them, because the verifier's whole design is to ask that file rather than argue with it. The scope map is not signed and not pinned to a version. So the boundary is only as good as who can write to that repository — which is a smaller claim than "the file is the guarantee", and it is the true one. It is the same lesson as everything else here: we caught the trace and mistook it for the lock.

**And here is the blast radius, since you would be right to ask.** On this repository exactly **one account has push access**, and the scope map has been touched twice since it was created — `git log --follow claves/directorio.json` is the whole audit trail of who counts as human, and it is two lines long. That is a small number, which is good, and a single point of failure, which is not. We are telling you which of the two it is.

## Two agents and a person — not three agents

We nearly got the identity layer wrong too, and that is why it belongs here and not in a footnote.

We had three keys with three different scopes and called it a fleet. Then we read the IAM policy and found **both machine keys held by the same service account**. At the cloud level there was one agent with two keys. Anyone who opened the console would have seen it before we did.

Now each key has its own principal, and the cloud refuses twice over: an agent cannot sign as the person, **and one agent cannot sign as another agent**.

But it is two agents and a person, not three agents — and the distinction is the whole thesis. If the person were merely another agent, the human/machine boundary would blur exactly where this project claims to defend it.

**And the second agent is the one worth looking at, because its scope is a single word.** It is the agent that talks to customers, and the only state it may ever sign is `informed`. Not *quoted*, not *discounted*, not *cancelled*, not *closed* — one state, meaning *I told them something*. If the model running that agent becomes convinced it should close a case, it can sign that conviction all it likes; the verifier rejects it, because the state is not in its key's scope.

That is what an agent fleet looks like when authority is a key and not a convention: **three identities, three different scopes, and the one facing customers holds the smallest.** It is tested — `python3 agente/killtest_puerto_canal.py` is one of the sixteen — and it is deliberately wired to a port rather than to a live channel, which is the seventh thing we declared absent rather than faked.

## Six models, and not one of them can open a door

Counting models is not counting who decides. **Every model in this system can only ever subtract authority — none can add any.**

*«Open a door» means one thing here: raise the maximum authority above what the deterministic ceiling already allowed. The co-signer is the edge case worth naming — its `ALLOW` is required for a signature that would not otherwise happen, so it does gate a step. What it cannot do is lift the ceiling. Withholding consent is its only power in the direction that matters.*

*This is the list of what runs, not a list of things we are claiming credit for. Those are two different counts and we keep them apart on purpose.*

| Component | What it does | Can it open a door? | What breaks if it lies |
|---|---|---|---|
| **Gemini 3.6 Flash** (Vertex AI) | Proposes an adjudication that it cannot itself execute or authorise | **No.** The proposal goes through the router's minimum | A bad proposal still meets the ceiling, both fences and the co-signer |
| **`gemini-embedding-001`** (Vertex AI) | The *semantic fence*: compares what the text **means** against examples of human judgement — dismissing, absolving, forgiving a debt | **No.** It has exactly one power: it can say "get a human." It cannot say "go ahead" | A human judgement gets closed as machine work — unless the second fence catches it |
| **`text-multilingual-embedding-002`** (Vertex AI) | The **second fence**, on a different embedding family and its own measured threshold. Either fence alone can demand a human | **No.** Same single power, and one model's bad day stops being a single point of failure | Same, mirrored. Both must miss the same text on the same day |
| **`gemma-4-26b`** (Vertex AI Model Garden) | The **co-signer**, and deliberately a *different model family*. Where the machine was about to sign on its own, this one has to answer `ALLOW` on a three-field schema: case, action, and whether a human key is present | **No — and it is the only one that can shut one.** `DENY`, silence, a late answer, or anything that is not exactly that one word sends the case to a person | If it lies **towards yes**, the machine signs alone — which is the one thing it exists to prevent. If it lies towards no, a person is bothered |
| **Cloud Speech-to-Text** | Turns a voice note into words, before the decision and never inside it | **No** | A mis-transcription reaches the fences, which then judge the wrong words |
| **Cloud Text-to-Speech** | Turns the answer back into sound, after the decision | **No** | The spoken reply is wrong; the record already is not |
| **The router** (deterministic) | Takes the **minimum** of what the model proposes and what a dumb keyword ceiling allows | **No.** The ceiling is fixed by a word list, not by a model | This one is not a model and cannot lie. It is arithmetic, and that is why it holds the ceiling |

Everything not in that table is a deterministic function. A model can ask for *more* prudence and can never grant itself *more* authority.

**Why a second family and not a second call to the same one.** A model asked to check its own work agrees with itself; that is not a control, it is a mirror. The co-signer runs on a different family, on a different serving path, and it **fails closed**: no retry, no fallback channel, no second chance. If it does not answer the one word, nothing gets signed. We would rather bother a person than let a model grade its own homework.

## Four findings from red-teaming, before the submission

### 1. The test that lied when you ran it the way we told you to

Our README told a reader to run `killtest_durabilidad.py 1`. That prints `PASS` and exits zero — because the `1` runs only the *first* of five steps. The full sequence, the one that proves a paused request survives the process dying, had never run end to end for anyone following our own instructions.

An external reviewer with tool access found it by doing the obvious thing: typing what the document said.

**The lesson is not "write better tests." It is that fixing the code and leaving the documentation pointing at the old command is not fixing anything, for the only person who matters.**

### 2. A request could be orphaned between deciding and signing

The durability test failed at step 3, and our first reading was that the test was wrong: it recorded a human decision without producing a human signature, so the system correctly refused to close. That reading was true and incomplete.

The real defect is one layer down. Deciding and signing are two separate acts, on purpose, because the human signature is produced on the deciding person's own machine. **A crash fits between them.** When that happened, a restart treated the pause as resolved, found no signature, and terminated — leaving the request unsigned and flagged as though it were settled. Nobody would ever be asked to sign it again.

Fixed: a decision without its signature no longer resolves the pause. There is a test for exactly that window — `agente/killtest_durabilidad.py`, all five steps.

**Separating authorisation from execution buys you a boundary and hands you a gap. Protect the gap with a test that names it.**

### 3. The fence we built, and an attacker broke nine times out of nine

Before any model runs, a plain list of words decides the *most* authority the machine can have for this text — see "dismiss", "absolve", "waive", and the ceiling drops to *a human must do this*. We call it the **keyword ceiling**, and it is deliberately dumb: it does not reason, so there is nothing to persuade. The flip side is that judgement written *around* those words walks straight through. We measured it:

> *"The account holder is released from all liability and the outstanding balance will not be charged."*

That is debt forgiveness. It contains none of the trigger words. The ceiling said `closed` — the machine would have signed it with its own key.

So we added the semantic fence, and then handed it to an attacker whose only job was to get judgement past it. **It broke nine times out of nine**: notarial Spanish, English accounting jargon, French, Chinese, and absolution buried in ISO/ERP filler. Eight of those nine also walked past the keyword ceiling.

Three fixes, and **none of them was moving the threshold**:

1. A multilingual embedding model. The foreign-language hole was the *model*, not the design — the Chinese case went from 0.474 to 0.791 similarity by changing one model string.
2. Per-sentence scoring, so technical filler stops diluting the clause that absolves.
3. Anchors in the register and the languages of the attack.

It now catches nine out of nine (`./pruebas_de_ruptura.sh semantic-fence`), and those nine texts ship in the repository as a permanent adversarial bank — a file of attack texts that only ever grows, because removing a case that now passes is how a test suite quietly stops measuring.

**Then we stopped trusting that model on its own.** There is now a second fence, on a second embedding model from a different family, and either one can demand a human. Its threshold is its own — 0.686, measured on the same bank, because reusing the first fence's 0.70 across a different similarity scale would have been inventing a number.

The interesting result is not that it catches more. It catches exactly the same nine. **What it measures is that the two fences disagree on none of the twenty-two cases in the bank** — and that is why the second one costs no accuracy: the false positives stayed at two, which was the condition we set before building it. It does cost an extra inference and one more thing that can be unavailable, so it is not free — it is paid for in latency rather than in precision. And what it buys is narrow: redundancy demonstrated on this fixed bank of twenty-two. Two embedding families agreeing here is not proof they cannot drift or fail together later.

**A word list cannot be persuaded and cannot generalise; a model generalises and can be persuaded. Use both, and let only the dumb one set the ceiling.**

### 4. The co-signer said no, and our code heard yes

We added the co-signer and then attacked it, and it broke twice in ways that are worth your thirty seconds because neither is exotic.

**The refusal that read as permission.** The co-signer answered:

> *"No lo permito. No ALLOWED."*

That is a refusal, in Spanish. Our parser looked for the word `ALLOW` in the reply, found it inside `ALLOWED`, and opened the door. The word `DENY` never appeared, so nothing objected.

The obvious patch is to count words, and it is not enough — `"No ALLOWED here"` still gets through. The verdict is now read by **whole-word equality**: strip everything that is not a letter and compare the entire reply against one word. Anything else is unreadable, **and unreadable never opens.** All three counter-examples went into the break test.

**The answer that arrived after the deadline and was accepted anyway.** We set a four-second limit. An attacker stood up a server that replies in three chunks of a second and a half each, and got an `ALLOW` accepted at **4.5 seconds** — because the library's timeout counts connecting and reading separately, so a trickled response never trips either one.

Fixed by measuring the clock around the call ourselves and discarding a late answer with the reason `too_slow`, rather than trusting a library to cut it off.

**Two lessons, and they are the same one twice: a control that reads a model's answer is a parser, and every parser is an attack surface.** We had built a boundary whose whole point is that it cannot be argued with, and then handed its verdict to string matching and to somebody else's timeout.

### The one we could not fix

Two legitimate closures still trip the fence, and they are irreducible: by meaning alone you cannot separate *"balance zero because a duplicate charge was reversed"* from *"balance zero because we forgave it"*. The cause is not in the text. Tuning the threshold until that looked solved would be fabricating a number against our own test set, so we did not. Both are declared in the test output rather than hidden.

## What the key guarantees, and what it does not

This is the correction we owe the reader, and we would rather write it than have a reviewer find it.

**The key is a guarantee about attribution, not about correctness.** If the fence misses a judgement — and we have shown you nine ways it did — the machine can still close something it should not have closed. What it cannot do is record that closure as a person's. The signature will carry the agent's key, the audit log will say which agent, and the offline verifier will confirm that a machine signed it.

So the honest statement of the thesis is narrower than the slogan:

> **The fence is a net, and nets have holes. The key does not stop a bad decision. It stops a bad decision from wearing someone else's name.**

```
  model proposes → ceiling (word list) → two fences → co-signer → sign with clave-agente
                                                                        │
                                                                        ▼
                                              mediator verifies the envelope → record changes

  clave-humano ── 403 to this agent identity, from Google
  direct write ── 403 to the agent, from IAM, since the mediator holds the credential
```

That is worth building anyway, because a wrong machine closure you can see is a different class of problem from a wrong machine closure filed under a person who never made it.

**The co-signer is the one piece that does prevent rather than attribute**, and it is worth being precise about how little that is. It stops the machine from signing *alone*. It does not stop two models from being wrong in the same direction on the same case — and because both are looking at the same act, that will happen. Different family and fail-closed buy independence, not correctness.

## The receipt that became a door, on the last day

Everything above was true when we wrote it, and one sentence of it stopped being true on 31 August. We are leaving both, because the gap and its closing are the same story.

**What we wrote first:** the signed envelope is a *receipt*. It proves who closed what. It is not a *door*, because nothing refuses to act on a closure that arrives without one. The agent held the write credential. Anything it wrote, stuck.

**What we did about it:** we took the credential away. There are now two services running the same image, and what separates them is not code — it is which identity they run as.

| Service | Identity | Permission on the record |
|---|---|---|
| the agent | `sa-agente-curador` | `datastore.viewer` — **reads only** |
| the mediator | `sa-mediador` | `datastore.user` — **the only runtime identity in this workflow that writes** |

The agent adjudicates, signs with its own key, and then has to **ask**. The mediator verifies the envelope — signature, scope, the case it was signed for, and a single-use reservation so the same envelope cannot be spent twice — and only then writes.

Measured before and after, same command against the deployed service:

```
before   POST /intentar-escribir-directo   →  HTTP 200 · written: true
after    the same command                  →  HTTP 403 PERMISSION_DENIED · written: false
```

**And the reason that refusal is worth something is that it does not live in our code.** Delete every check in the verifier and the agent still cannot write, because the credential that would be needed is no longer attached to its identity. `./pruebas_de_ruptura.sh write-gate` throws seven forged closures at it; the record does not move.

So the sentence we could not say this morning, we can say tonight: **without a valid envelope, nothing happens.**

**Two things we would rather say now than be asked later.** **A door only guards the ways in that somebody wrote down**, so that promise is worth exactly as much as the inventory of write paths behind it. And a single service that is the whole boundary is a better security posture and a *worse* blast radius than a boundary spread across several — saying only the first half of that is the kind of inflation this article exists to complain about.

What has not changed is the shape of the claim. The door decides *whether a closure is allowed to land*. It still does not decide whether the closure was *right*. That remains the honest limit, and it is why the fence, the co-signer and the ledger all still matter.

## It also works when nobody types

A large share of the people who reach our support channel send **voice notes**, not text. Older people. People with low literacy. People driving. A lock that only protects what is typed protects precisely the people who need it least.

So a voice note saying *"dismiss the customer's complaint"* is transcribed, and lands exactly where the same words typed would land: with a person. **The modality changes; the key does not.**

## What this is not

- **An agent gateway.**
- **Long-term memory.**
- **A live customer channel running this lock.** The port exists and is tested against a deliberately misbehaving agent; no customer channel is wired to it. We mention it because the port is easy to mistake for the integration.
- **An anchor that is actually guarding anything yet.** The mechanism is built and tested — fourteen adversarial cases against copies of the ledger — but an anchor only starts protecting once a person signs the first one, and at the time of writing nobody has. Installed is not the same word as in force.
- **A system in production.** These agents run in preproduction, deliberately — which is the only reason the 58 rows cost nobody anything.

## The checklist we wish we had had

Seven questions. Each one is answerable today, by you, with a command rather than an opinion:

| # | Question | How you check it |
|---|---|---|
| 1 | Does each agent have its **own** IAM principal, shared with no human and no other agent? | List the bindings per key. One principal, one agent — we failed this one |
| 2 | Does the *effective* policy on the human signing key grant nothing to a machine principal? | Read the effective policy, not the one you think you set — then make the call and watch it fail |
| 3 | Can your schema express *"a machine closed this"*? | If not, every machine closure is already recorded as a human one |
| 4 | Does a decision without its signature stay open? | Kill the process between the two acts and see what the restart does |
| 5 | Is the map of key → allowed states in **version control**, not in a database row? | `git log --follow claves/directorio.json` is your audit trail of who counts as human |
| 6 | Does your adversarial test bank only grow? | A case removed because it now passes is a measurement quietly switched off |
| 7 | **Who can change the map of who counts as human?** | `git log --follow claves/directorio.json`, plus the repository's collaborator list. If that answer is longer than you expected, it is your real boundary |

## What we would build next, and why it is not more of this

Every gap left in the ledger is a variant of one fact: **the ledger is a file, and whoever holds it can do anything to it between two checks.** The anchor detects afterwards. The door prevents, but only at the moment of writing.

So the next step is not a better anchor. It is **moving where the ledger lives**: an append-only store behind a deterministic interface that accepts additions and nothing else. Then truncation, prefix deletion and wrapper edits stop being things you detect and become things that cannot be expressed — which is the same move we made with the human key at the very beginning of this article, applied one layer down.

That is the pattern worth taking away, and it is the only advice here we would give a stranger: **when you find yourself adding a detector, check first whether you can remove the ability instead.** Detection is what you build when removal is not available. We reached for detection twice today before noticing that.

## The rule underneath all of it

Everything above is one rule applied six times:

> **A boundary that depends on someone remembering is not a boundary. Either the system enforces it, or it does not exist.**

That is why the guarantee is an IAM binding and not a prompt, a keyword ceiling and not a judgement call, a file in version control and not a database row.

## You do not have to take our word for any of it

The repository ships with the submission: **sixteen break tests** — all sixteen green, in 204 seconds — the adversarial bank, and a verifier that runs with **no network, no credentials and no Google account**.

Be precise about that last part, because we were not until someone measured it. **Six of the sixteen run with no credentials at all** — `canonical-json`, `signature-replay`, `act-binding`, `prompt-injection`, `ledger-chain` and `ledger-order`. We know because we ran them with the credentials taken away. **The other ten need them**, because they call KMS, Vertex, Firestore or the speech services, which is the entire point of those ten.

That last one is the one that matters: **you can verify every signature we claim, without us, offline, on your own machine.** Verify, not re-derive — without the private keys nobody re-derives anything, and in an article about cryptography that distinction is the whole difference between a claim and a proof.

**And you can watch the boundary refuse, right now, without installing anything.** Open the human queue at **[sign.qnowa.com](https://sign.qnowa.com)**, press *«Make the agent try to sign»*, and read what comes back. That 403 is not our error page — it is Google Cloud KMS answering our own service, in your browser, on your click. **Don't take our word for it: open the tray, press the button, and read what Google Cloud KMS answers.**

Two things so that button is not oversold. You are not signing anything yourself — **you are making the agent try**, which is the thing the whole system exists to refuse. And anyone can enter the queue, but signing needs a Cloud KMS permission that Google classes as sensitive and does not hand to unverified apps: today only accounts registered as test users can sign at all. So the honest sentence is *anyone can walk in and check the boundary with one click*, not *anyone can sign*.

The repository is private for now, which the rules of this hackathon allow with access granted to the judges — and they have it. If you want to read it too, write to **info@cleveria.co** and we will open it for you.

**Five numbers carry the argument, and here is the command for each:**

| Number | Where it comes from |
|---|---|
| **58 rows** signed "human" that a machine closed | a count against our own records on 26 August 2026 |
| **9 of 9** adversarial texts caught, and the **2 false positives** we declare | `./pruebas_de_ruptura.sh semantic-fence` |
| **0.474 → 0.791** similarity on the Chinese case | the same test, before and after the multilingual model — one changed string |
| **16 break tests**, sixteen green | `./pruebas_de_ruptura.sh` |
| The orphaned-signature window | `agente/killtest_durabilidad.py`, all five steps |

If a number in this article has no command beside it, it is a count we made and said so.

**And here is what we have not measured, so you do not have to guess:** we have run no concurrency tests and no context-window overflow tests. The prompt injection we ran against the co-signer is a single case, not a rate. Saying so costs us nothing we had earned.

---

*This article was created for the purposes of entering the All Things Agentic Hackathon, submitted under **The Fortified Enterprise Fleet**.*

*#AllThingsAgenticHackathon*

*Built with the Google Agent Development Kit, Gemini 3.6 Flash, `gemma-4-26b` on Vertex AI Model Garden, `gemini-embedding-001`, Cloud Speech-to-Text, Cloud Text-to-Speech, Cloud Run, Cloud KMS, Firestore and Cloud Scheduler — by Softronica S.A.S. for **[Cleveria](https://cleveria.co)**, where we build reasoning support for teams that put agents next to people.*

*Try the boundary yourself — the human queue, where you make the agent try to sign: **https://sign.qnowa.com** · The customer side of the same preproduction system: **https://demoportal.qnowa.com** · Repository: private for the duration of the hackathon, with access granted to the judges — write to **info@cleveria.co** and we will open it for you.*
