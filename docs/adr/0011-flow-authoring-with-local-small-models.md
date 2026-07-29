# ADR-0011: Flow authoring with locally-running small models

- Status: Proposed
- Date: 2026-07-29
- Deciders: Mojolab (Arjun Venkatraman) — pending sign-off
- Related issues: T17, T18, T19, T20 (amends #7)
- Related ADRs: ADR-0004 (amended by this ADR), ADR-0002, ADR-0009, ADR-0010

## Context
ADR-0004 decided that new flows are authored by conversing with **"a capable
LLM"** which emits a valid native `flow.yml` directly, replacing the Verboice
Designer GUI. That decision stands. Its *mechanism* does not: "capable" implicitly
meant a large frontier model, and the requirement now is that authoring work
against the same **locally-running set of small models** as the runtime — on a
laptop, offline.

This is not the same problem with a smaller model plugged in. Asking a quantised
1–8B model to emit a whole `flow.yml` from an open-ended brief fails in specific,
predictable ways:

- **Cross-reference incoherence.** `next:` pointers to step ids that do not
  exist, or that create unreachable branches. Long-range consistency is exactly
  what small models are worst at.
- **Id invention.** Stable, unique, collision-free ids are pure bookkeeping and
  models are bad at bookkeeping.
- **Schema drift.** A schema held in the prompt is a schema the model partially
  forgets by the end of a long document.
- **Conversational wander.** Given an open brief, small models drift, over-ask,
  and lose the thread of what has already been decided.

None of these are fixed by better prompting; the frontier-model workflow in
ADR-0004 papers over them with raw capability. The design below removes each
failure mode structurally instead, so that what remains is work small models are
genuinely good at: short, bounded, local transformations with a constrained
output space.

## Decision
Authoring is a **program that uses small models as subroutines**, not a model
that writes a document. Five mechanisms, each targeting one failure mode above:

**1. Constrained decoding — schema validity becomes structural.**
Generation is driven against `schemas/flow.schema.json` (T4) using grammar- or
JSON-Schema-constrained sampling (llama.cpp GBNF, Outlines, XGrammar). Tokens
that would violate the schema are not sampleable. A 4B model with constrained
decoding beats a far larger model prompted freeform *on validity*, because
validity stops being something the model has to remember. The grammar is
generated from the schema, so the two cannot drift.

**2. The model never emits a flow — it emits one small typed edit at a time.**
Define a flow-edit operation vocabulary — `add_play`, `add_menu`, `add_listen`,
`add_option`, `set_prompt`, `set_next`, `set_intent_phrases` — where each
operation is a small JSON object. Deterministic Python applies the operations and
**owns everything the model gets wrong**: id generation, `next` wiring,
reachability, and schema invariants. The model proposes a local change; the
program is the sole author of structure. This single decision eliminates
cross-reference incoherence and id invention outright, rather than validating for
them after the fact.

**3. A deterministic interviewer; the model as a narrow transformer.**
Python owns the conversation's control flow — which question comes next, what has
already been settled, when the flow is complete. The small model is called only
for bounded single-purpose transformations, each with a short input and a small
output space:

- rewrite an operator's rough phrasing into a natural spoken prompt;
- translate a prompt into another target language;
- propose example `phrases` for an intent (directly serving ADR-0009's
  per-language authoring burden);
- suggest menu wording that mentions both the spoken and DTMF affordance.

Small models wander when they drive and behave well as subroutines. This puts
them where they are reliable.

**4. Retrieve-and-adapt from an example library.**
Small models adapt a near-miss far better than they compose from scratch. Keep a
library of worked flows in `examples/flows/`, retrieve the closest by embedding
similarity, and use it as the starting skeleton the operations then modify.
This reuses ADR-0010's sentence encoder, so it adds no new footprint.

**5. Validate → lint → simulate → repair, with a hard human floor.**
Every candidate flow passes through, in order: JSON Schema validation → graph
lint (dangling `next`, unreachable steps, missing `store` targets, prompts that
fail to offer the DTMF fallback per ADR-0009) → a simulator dry run (T7). A
failure feeds back **one specific scoped error**, not the whole document, for a
targeted repair. Repair attempts are capped at 2–3, after which the problem is
surfaced to the human rather than retried indefinitely. Nothing auto-deploys.
This is ADR-0004's guardrail machinery, reused unchanged — the safety apparatus
built for frontier-model authoring is exactly what small-model authoring needs
more of.

**6. The authoring model is not a runtime dependency.**
It runs on a laptop at design time. The deployed edge box needs only ASR, TTS,
VAD and the intent encoder (ADR-0010). Authoring capability therefore costs
nothing in the runtime footprint, which is what keeps the platform lightweight
while still being LLM-authored.

*Noted for later, not decided here:* since the platform will have a working
speech stack, a flow could eventually be authored **by phone** — the operator
calls in, speaks the flow, and the same ASR/TTS captures it. Appealing
dogfooding, and the right long-term answer for non-technical authors in the
field, but it depends on ADR-0008/0009 landing first.

## Consequences
### Positive
- Authoring works fully offline on laptop-class hardware, with the same model
  set the runtime already requires.
- Structurally valid output: constrained decoding plus program-owned structure
  makes the two most common small-model failures impossible rather than merely
  detected.
- Degrades gracefully with model quality — a weaker model produces clumsier
  *wording*, not a broken flow, because it never controls structure.
- Operations are a natural undo/redo and audit trail, and give a GUI or a
  phone-based authoring surface something to target later.
- Directly attacks ADR-0009's per-language `phrases` burden, which is otherwise
  the most tedious part of authoring a dual-mode flow.

### Negative / Trade-offs
- Substantially more engineering than ADR-0004's "ask a model for YAML": an
  operation vocabulary, an applier, a grammar generator, an interviewer, and a
  repair loop are each real components.
- Adds a constrained-decoding dependency (llama.cpp / Outlines / XGrammar) and a
  schema→grammar generation step that must stay in sync with T13's schema
  changes.
- The deterministic interviewer is less flexible than open conversation. It will
  not handle briefs its question flow does not anticipate, and that question flow
  is itself a thing to design and maintain.
- Human review becomes **mandatory rather than advisory**. Small models produce
  awkward and occasionally wrong prompt wording, and no amount of structural
  validation catches a grammatically valid prompt that says the wrong thing.
- Two authoring paths may coexist for a while (frontier-model per ADR-0004,
  local per this ADR), which is a real maintenance cost until one is retired.

## Follow-up work (to be filed as issues)
- [ ] T17 — Schema-constrained generation harness: generate a GBNF/JSON-Schema
      grammar from `schemas/flow.schema.json` and run a local small model
      (llama.cpp or equivalent) against it. **Amends #7.**
- [ ] T18 — Define the flow-edit operation vocabulary and the deterministic
      applier that owns id generation, `next` wiring and reachability
      invariants.
- [ ] T19 — Interview-driven authoring CLI: deterministic question flow calling
      the small model for bounded transforms (phrasing, translation, intent
      `phrases`), with retrieve-and-adapt over `examples/flows/`.
- [ ] T20 — Validate/lint/simulate/repair loop with scoped error feedback, a
      capped retry budget, and a mandatory human review gate before deploy.
