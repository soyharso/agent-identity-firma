# Judge presentation package

## Positioning decision

**Product identity:** Cleveria.ai — the agent identity harness.  
**Proof scenario:** QNOWA — the operational workflow where the defect was measured.  
**Operator disclosure:** Softronica.co — owner/operator of the originating system.

This is not a three-brand co-marketing video. The judge should remember one technical idea:

> **Cleveria makes the human boundary cryptographic: the agent can work, but it cannot sign as a person.**

QNOWA appears only when it gives the claim a concrete operational setting. Softronica appears in
the final credits and submission disclosure, not in the hook, title card, or repeated lower thirds.
This preserves the blind-test advantage: evidence first, thesis after proof, no advertising signal.

## Why this beats the alternatives

| Option | Strength | Risk | Decision |
|---|---|---|---|
| Softronica.co as lead | Established corporate legitimacy | Reads as a company pitch; judges may expect a commercial product and production claims | Disclosure only |
| QNOWA as lead | Concrete BPO/workflow context | The channel is not fully wired to this lock; risks implying a live integration | Demonstration context only |
| Cleveria.ai as lead | Names the novel technical artifact and supports the architecture prize | Must explain it in one sentence | **Use** |
| Neutral project name | Maximizes apparent independence | Loses the harness/product identity and operator provenance | Backup only |

## Four-minute cut

The video must be in English or have burned-in English subtitles. It should be one continuous
screen recording with no decorative montage and no claim that the agents are in production.

| Time | Visual | Spoken purpose |
|---|---|---|
| 0:00–0:12 | Ledger: 58 machine-attributed closures; 4 dismissed; small `PREPRODUCTION` label | Establish a measured defect, not a slogan |
| 0:12–0:38 | Cleveria.ai title card, then the flow begins | Explain that the fix is a boundary, not a better prompt |
| 0:38–1:18 | Cloud Scheduler, Firestore, and three request outcomes | Prove useful autonomous work and the human stop |
| 1:18–2:08 | Live terminal attempt against the human KMS key | Show the decisive HTTP 403 |
| 2:08–2:42 | Human-machine handoff and offline verifier | Prove attribution and independent verification |
| 2:42–3:24 | Adversarial tests, including Spanish Model Armor miss and semantic fence catch | Show measured limits and compensating controls |
| 3:24–3:48 | Cloud Run/KMS/Firestore console | Satisfy Google Cloud proof visibly |
| 3:48–4:00 | Final card with the thesis, repo URL, and disclosure | Close after evidence, not before it |

## Opening and closing copy

### Opening

> “Fifty-eight records said human although a machine had closed them. Four were dismissals. We
> found the defect in preproduction, where it belongs: before a customer could be affected.”

Do not say “we gave an agent a human signature”, “it lied”, “it absolved itself”, or “it can
close tasks all day”. The blind jury read those as sensational or promotional.

### Closing

> “The machine does the work it can prove. The person keeps the judgement. Cleveria turns that
> boundary into IAM, keys, and a verifier anyone can run.”

Then show the disclosure in small but readable text:

> “Cleveria.ai harness. QNOWA operational scenario. Built and operated by Softronica.co.”

## Visual system

- Background: near-black `#0B1020`; text: off-white `#F8FAFC`.
- Machine path: Google blue `#4285F4`.
- Human pause: amber `#F9AB00`.
- Verified result: green `#34A853`.
- Denied capability: red `#EA4335`, used only for the 403.
- Typeface: Inter, Arial, or DejaVu Sans; minimum 28 px for terminal output and 32 px for labels.
- Logo treatment: one monochrome Cleveria wordmark on the opening and closing cards only.
- No stock robot, shield, handshake, server-room, or smiling-business imagery.

The strongest “image” is the actual evidence: the IAM policy, the 403, the Firestore state
change, and the verifier output. Use a clean architecture diagram from the README as a single
animated build: scheduler → agent → deterministic ceiling → pause/sign → verify.

## Animation rules

Use restrained motion in the editor of choice (Kdenlive, Shotcut, DaVinci Resolve, or OpenShot):

1. Reveal one node at a time along the real execution path.
2. Freeze the frame for at least 2 seconds when `403 PERMISSION_DENIED` appears.
3. Animate the human key as unreachable: a red boundary around it, not a cartoon lock.
4. When the agent pauses, stop the animation completely; the absence of motion communicates the
   stop better than an effect.
5. Use hard cuts between terminal evidence and cloud console. Do not use wipes, zoom bursts, or
   glitch transitions.

## Audio

Use a quiet, instrumental bed only if it does not compete with terminal audio or narration:

- 70–78 BPM, no vocals, no lyrics, no dramatic risers.
- Keep music around -30 dB under speech; duck it completely during the 403 and verifier output.
- A single low, short tonal hit may mark the denied request; never use a “hacking” sound.
- Prefer a CC0 or self-recorded track and retain its license/source in the submission notes.
- The safest version is **no music**, clean narration, keyboard sound, and the audible pause after
  the 403. Silence is part of the proof.

## Capture and subtitle toolchain

Already available and tested locally:

- GNOME Shell native recorder: `Ctrl+Alt+Shift+R`.
- `ffmpeg` 8.1.2 for burned subtitles.
- local `whisper` for timing/transcription; write the English `.srt` manually from the script.
- LibreOffice for a PDF slide deck if a static architecture handout is needed.

Do not install `mcp-video`: the documented package is a 443-byte stub, not a recorder. Do not add
an unverified npm package to the capture path.

For the final render on this machine, use `libopenh264`, not `libx264`:

```bash
ffmpeg -i recording.webm \
  -vf "subtitles=subs_en.srt:force_style='FontName=DejaVu Sans,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=40'" \
  -c:v libopenh264 -c:a aac video_final.mp4
```

## Submission page strategy

Use the same ordering as the video:

1. One-sentence problem and measured 58/4 result.
2. One-sentence Cleveria solution.
3. Architecture and Google services.
4. Exact guaranteed-versus-mitigated table.
5. Reproduction commands and hosted demo.
6. Disclosure of QNOWA and Softronica.

The article title remains the measured, non-promotional version:

> **Fifty-eight machine closures wore a human signature. We found them in preproduction.**

## Evidence and decision rule

The available blind measurement is stronger than an unverified “winner style” claim: three
independent model jurors with rotated order unanimously preferred the evidence-led video opening,
while the slogan-led opening was last for two jurors. Therefore, do not optimize for cinematic
polish at the expense of causal proof. Run one final blind check on the complete first 30 seconds
after recording; change only if at least two of three jurors independently identify the same
confusion or promotional signal.
