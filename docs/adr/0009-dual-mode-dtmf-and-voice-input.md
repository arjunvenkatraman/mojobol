# ADR-0009: Dual-mode input — every interactive step accepts DTMF *and* speech

- Status: Proposed
- Date: 2026-07-29
- Deciders: Mojolab (Arjun Venkatraman) — pending sign-off
- Related issues: T13, T14 (amends #4)
- Related ADRs: ADR-0002 (amended by this ADR), ADR-0008, ADR-0010

## Context
Every input in mojobol today is a keypress. `executeStep` dispatches `capture`
and `menu` to AGI's `GET DATA` and compares the resulting digit string against
`valid_values` or an `options` list. The `record` step captures caller audio but
only ever writes it to disk — it is never transcribed.

We want live voice conversation, but **not at the cost of DTMF.** In the
deployments this platform actually serves — rural Indian telephony over GSM
ATAs and narrowband SIP trunks — speech recognition degrades on exactly the
inputs that are most common: background noise, wide accent variation,
code-switching mid-sentence, and 8 kHz narrowband audio (ADR-0010). DTMF is
unglamorous and nearly always works. A voice-only IVR would be a regression in
reliability even as it improved in feel.

So voice must be **additive**: a second way to answer the same question, with
DTMF as a floor the caller can always fall back to — including automatically,
when recognition is not working on that call.

This ADR is also time-sensitive with respect to **ADR-0002 / issue #4**. The
native flow format is specified as supporting `play`, `capture`, `menu`,
`record`, `playloop`, with prompts as `say:` or `audio:`. Nothing in that schema
can express "listen for speech", "these phrasings mean this option", or "this
prompt may be interrupted". #4 is still `todo` and **T5, T6, T7 and T8 all depend
on it**, so a schema that forecloses voice would have to be versioned a second
time and would drag four downstream deliverables with it. Extending the schema
before it freezes is much cheaper than extending it after.

## Decision

**1. Every interactive step accepts both modalities concurrently.** A single
`listen()` (ADR-0008) is armed for DTMF and speech at the same time; whichever
resolves first wins, and the loser is discarded. Authors do not write two flows,
and do not choose a modality per step.

**2. Extend the native flow schema** (amending ADR-0002) with the minimum needed:

- `barge_in: true|false` on any step that speaks. Default `false`, preserving
  today's play-to-completion behaviour; conversational flows opt in.
- `menu` options gain an `intent` name and a list of example `phrases`
  alongside the existing DTMF `number`.
- a new `listen` step type for open-ended or slot-filling capture, with
  `intents:` and/or a `store:` target for free-form transcription.
- `say:` gains optional `voice:` / `engine:` hints, so a flow can pin a
  specific TTS voice without the format hardcoding espeak (ADR-0010).

```yaml
- id: main_menu
  type: menu
  say: "For crop prices, say prices or press 1. For weather, say weather or press 2."
  barge_in: true
  options:
    - number: "1"
      intent: prices
      phrases: ["prices", "rate", "bhav", "daam", "crop price"]
      next: crop_prices
    - number: "2"
      intent: weather
      phrases: ["weather", "rain", "mausam", "baarish"]
      next: weather_today
  on_no_match:
    say: "Sorry, I did not catch that."
    max_attempts: 3
    then: dtmf_only          # degrade, do not hang up
```

The author writes the intent and its phrasings once; the engine derives both the
speech path and the DTMF path from the same declaration.

**3. A deterministic fallback ladder, guaranteed by the engine.** On repeated
speech no-match the engine escalates without the flow author having to write it:

1. reprompt as authored;
2. reprompt with DTMF-only wording ("press 1 for prices");
3. after `max_attempts`, latch to DTMF-only for the remainder of the step.

Recognition failure therefore degrades to today's working behaviour rather than
dead-ending the call. Flows may override the ladder but get it by default.

**4. Intent resolution is tiered, cheapest first**, and configurable per
deployment:

| Tier | Mechanism | Cost |
|---|---|---|
| 1 | exact / fuzzy keyword match of the transcript against `phrases` | negligible |
| 2 | embedding similarity against `phrases` (default) | ~ms, ~100 MB model |
| 3 | small-LLM classification, output constrained to the intent labels | optional |

Tier 2 is the default: it handles paraphrase and multilingual phrasing, is fast
enough to stay inside the latency budget, and keeps the runtime footprint small.
Tier 3 is opt-in for flows that need it. A match below the configured confidence
threshold is treated as a no-match and enters the ladder above — **an
LLM is not required at runtime for a working voice flow.**

**5. `record` steps may optionally transcribe.** The audio file remains the
record of truth; a transcript becomes an additional captured field (ADR-0012).
This is how the existing corpus of recordings starts producing structured data.

## Consequences
### Positive
- Reliability floor is preserved: any call that would work today still works,
  because DTMF is always armed and the engine degrades to it automatically.
- One authored flow serves both modalities, so there is no dual maintenance and
  no per-step modality decision for the author.
- Extending the schema before #4 freezes avoids a second format version and
  avoids reworking T5, T6, T7 and T8.
- No runtime LLM dependency in the default configuration, which keeps the edge
  footprint small (ADR-0010).

### Negative / Trade-offs
- Prompts must offer both affordances ("say prices or press 1"), which makes
  them longer and slightly more stilted than pure conversational wording. Good
  barge-in mitigates this; it does not remove it.
- Two concurrent input paths roughly double the input test surface, including
  the race where DTMF and speech arrive nearly simultaneously — the engine needs
  an explicit, tested precedence rule (DTMF wins, as the higher-confidence
  signal).
- `phrases` must be authored per language per intent, which is real authoring
  burden — and the main thing ADR-0011's tooling needs to help with.
- The embedding model is a new runtime dependency and footprint item, even in the
  default no-LLM configuration.
- Speech introduces a whole class of failure that DTMF does not have
  (mis-recognition producing a *confident wrong* branch); the confidence
  threshold is a tuning parameter with no universally right value, and mis-set
  it silently routes callers wrongly.

## Follow-up work (to be filed as issues)
- [ ] T13 — Extend the native flow schema and `schemas/flow.schema.json` with
      `barge_in`, `menu` option `intent`/`phrases`, the `listen` step type, and
      `say:` `voice:`/`engine:` hints; document them in `docs/flow-format.md`.
      **Amends #4** — land these before the schema freezes.
- [ ] T14 — Implement dual-mode input resolution in the engine: concurrent
      DTMF + speech arming with a tested precedence rule, the tiered intent
      matcher (keyword / embedding / optional constrained LLM) behind a
      configurable confidence threshold, and the deterministic no-match
      fallback ladder.
