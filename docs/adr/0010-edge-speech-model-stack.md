# ADR-0010: Edge-hosted small-model speech stack

- Status: Proposed
- Date: 2026-07-29
- Deciders: Mojolab (Arjun Venkatraman) — pending sign-off
- Related issues: T15, T16
- Related ADRs: ADR-0002 (amended by this ADR), ADR-0008, ADR-0009, ADR-0011

## Context
Speech has to run **on the box that answers the phone** — an edge node or a
laptop-class server — with no call-time network dependency. That is not a
preference; it is what makes the platform deployable where it is actually used:
intermittent or absent connectivity, no cloud egress budget, and health/
agriculture data that should not leave the district. It also caps per-call cost
at electricity.

Today the only model in the system is `espeak`, shelled out per utterance in
`getAudioFile`:

```python
os.system("espeak -s 100 -w %s.wav '%s'" % (tempfilename, text))
os.system("sox %s.wav -r 8000 -c 1 %s.wav" % (...))
```

Formant synthesis, regenerated on every call with no caching, hardcoded into the
resource resolver, and — per ADR-0002 — the native flow format currently plans to
keep it. There is no ASR at all.

Two constraints shape every choice below. **Latency**: telephony conversation
stops feeling live past roughly 800 ms mouth-to-ear, which is a budget spread
across four stages, not a single model's inference time. **Footprint**: a laptop
serving several concurrent calls cannot hold a separate multi-gigabyte model per
call.

## Decision

**1. Speech is pluggable, not hardcoded.** Define `ASREngine`, `TTSEngine` and
`VAD` interfaces, resolved per deployment from config. This amends ADR-0002: the
flow format must not name espeak; a step says `say:` and optionally hints
`voice:`/`engine:` (ADR-0009), and the configured engine renders it. The
`tts = espeak` key already sitting unread in `conf/sampleserver.conf` becomes the
real selector.

**2. Default model profile** — all local, all at call time, no network:

| Stage | Default | Approx. footprint |
|---|---|---|
| VAD / endpointing | silero-vad (ONNX) | ~2 MB |
| ASR (English) | Moonshine tiny → base | ~27 MB → ~190 MB int8 |
| ASR (Indic) | AI4Bharat IndicConformer 600M multilingual | ~600 MB–1.2 GB |
| TTS | Piper (ONNX), one voice per language | ~20–60 MB per voice |
| Intent embeddings (ADR-0009) | small multilingual sentence encoder | ~100 MB |

Moonshine is chosen for English over Whisper specifically because it was built
for streaming with minimal revision of already-emitted tokens, and because its
inference cost scales with utterance length rather than padding every input to a
fixed 30-second window — both of which matter more than headline WER on short
telephony turns. Piper replaces espeak because it is ONNX, fast on CPU, and
already telephony-appropriate at 8 kHz.

**3. Model files are fetched, never vendored.** A `tools/fetch_models.py` pulls
and checksums into a gitignored `models/` directory. Nothing model-sized enters
git.

**4. Models are shared across calls behind a bounded worker pool.** One instance
per model per process, not per call. The pool bound is the admission-control knob
for concurrency, and calls beyond it are rejected at answer time rather than
degrading every call in flight.

**5. Budgets are targets to be measured, not assumed.** Recorded here so T16 has
something to falsify:

- *Latency*, mouth-to-ear under 800 ms: VAD endpoint 150–250 ms, ASR finalize
  100–200 ms, dialog 100–300 ms, TTS first-audio 100–200 ms. This only closes if
  every stage streams — in particular, the first TTS audio must leave before the
  last dialog token is generated.
- *Footprint*: under ~1 GB resident for an English deployment, ~2 GB for Indic.
- *Concurrency*: 2–4 concurrent calls on a 4-core laptop.

**6. The published benchmark numbers behind these picks are treated as
unverified.** They come substantially from vendor and secondary sources. T16
benchmarks the candidates on target hardware with real call audio before any
default is locked in.

**7. Narrowband is acknowledged as a real accuracy cost.** 8 kHz μ-law measurably
hurts WER. Prefer G.722/Opus wideband wherever the gateway negotiates it; where
it does not, close the gap by fine-tuning on 8 kHz telephony audio rather than by
swapping in a bigger model.

**8. The existing recordings are a fine-tuning corpus.** Every `record` step
since 2015 has been accumulating real audio in the target languages, over the
exact channel conditions, accents and code-switching this platform faces. That is
the asset that lets small local models beat general-purpose cloud ASR on *this*
traffic, and it is the strongest technical argument for the edge stack beyond
offline operation.

## Consequences
### Positive
- Works with no connectivity; no per-call cost; no caller audio leaves the box.
- Replacing espeak with Piper is a large, immediate quality gain that needs no
  architectural change, because `say:` already abstracts text from rendering.
- Pluggable engines let a deployment trade footprint against accuracy — a tiny
  English box and a heavier Indic box run the same code.
- Fine-tuning on the local corpus is a durable advantage a cloud API cannot
  match on this traffic.

### Negative / Trade-offs
- **Indic ASR is the main technical risk.** IndicConformer at 600M is an order of
  magnitude heavier than Moonshine, and streaming it in real time on a laptop CPU
  is not established. Mitigations (quantisation, a smaller distilled model, an
  optional GPU, or accepting higher latency) are all compromises; T16 must
  determine which is needed before committing.
- espeak's near-zero footprint is genuinely lost; Piper is better but bigger, and
  every added model narrows the minimum viable hardware.
- Model licences differ and must be checked individually — Apache-2.0 is common
  but not universal, and some checkpoints carry dataset restrictions.
- A `models/` fetch step makes first-run setup slower and needs network *once*,
  which is awkward for a genuinely air-gapped install (needs a documented
  sneakernet path).
- More moving parts than `os.system("espeak")`: ONNX runtimes, resampling, and a
  worker pool are all new operational surface on a box that may have no
  on-site engineer.

## Follow-up work (to be filed as issues)
- [ ] T15 — Define `ASREngine`/`TTSEngine`/`VAD` interfaces; implement the Piper
      TTS backend with a prompt cache keyed on `(text, voice, lang)` and retire
      the inline espeak/sox `os.system` calls from `getAudioFile`. **Amends
      ADR-0002** — the flow format must not name a TTS engine.
- [ ] T16 — Benchmark candidate ASR/TTS/VAD models on target edge hardware for
      latency, resident footprint, concurrent-call ceiling and WER on real
      recorded call audio; lock in the default profile from measurements, and
      settle the Indic-realtime question specifically.
