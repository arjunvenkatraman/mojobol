# Sprint 2 — Live voice on the edge (v3.0 revival)

**Goal:** mojobol answers a call and holds a **live conversation** — the caller
can speak, interrupt, *or* press a key — with every model running on the box that
answers the phone. DTMF remains a first-class input and the automatic fallback,
not a legacy path.

**Definition of done for the sprint:** a call to the box can be completed
entirely by speaking (with barge-in working), entirely by keypress, or by a mix
of the two; no model call leaves the host; and the captured data lands in one
place.

## Sequencing warning — two tasks unblock in-flight Sprint 1 work

**T13 and T10 should be scheduled before the rest of this sprint, and before the
Sprint 1 tasks they touch land.** Both are cheap now and expensive later:

- **T13 (flow schema)** — #4 is still `todo`, and **T5, T6, T7 and T8 all depend
  on it**. A schema without `listen`/`barge_in`/`phrases` has to be versioned a
  second time, dragging four downstream deliverables with it.
- **T10 (async `MojoPlayer`)** — #8 is *in flight*. If the interface lands
  blocking and DTMF-shaped, barge-in has nowhere to live and the extraction is
  done twice.

## Sprint backlog

Per ADR-0001 governance, each task below is an ADR follow-up filed as an issue.

| Task | ADR | Depends on | Tier |
|------|-----|-----------|------|
| T13 Extend flow schema: `listen`, `barge_in`, intent `phrases`, `voice:` | 0009 | — | Opus |
| T10 Async, cancellable `MojoPlayer` interface | 0008 | — | Opus |
| T15 `ASREngine`/`TTSEngine`/`VAD` interfaces; espeak → Piper | 0010 | — | Sonnet |
| T21 Remove mail/batch/outbound subsystems | 0012 | — | Sonnet |
| T12 Minimal PJSIP + dialplan + container SIP/RTP exposure | 0008 | — | Sonnet |
| T16 Benchmark edge models on target hardware | 0010 | T15 | Sonnet |
| T11 `AudioSocketPlayer` + asyncio per-call driver | 0008 | T10 | Opus + Sonnet |
| T14 Dual-mode input resolution + tiered intent matcher + fallback ladder | 0009 | T13, T11 | Sonnet |
| T22 SQLite capture store + export; drop the `calllog` symlink | 0012 | — | Sonnet |
| T17 Schema-constrained generation harness | 0011 | T13 | Sonnet |
| T18 Flow-edit operation vocabulary + deterministic applier | 0011 | T13 | Opus |
| T19 Interview-driven authoring CLI + retrieve-and-adapt | 0011 | T17, T18 | Sonnet |
| T20 Validate/lint/simulate/repair loop with human gate | 0011 | T18 | Sonnet |

## Execution order & parallelism (tiered agents — ADR-0007)

- **Wave 0 (do first, unblocks Sprint 1):** T13 and T10 — both Opus, both
  interface-defining, both gating other people's work.
- **Wave A (parallel, independent of Wave 0):** T15 (the Piper swap is the
  cheapest perceptible win in the sprint and needs no architecture change),
  T21, T12, T22.
- **Wave B (after Wave 0):** T11 (async driver), T16 (benchmarks, after T15's
  interfaces exist).
- **Wave C (after T11 + T13):** T14 — dual-mode input is where the sprint's goal
  actually becomes true.
- **Wave D (authoring, after T13):** T17 and T18 in parallel, then T19 and T20.
- **Integration/review:** Opus owns the `MojoPlayer` shape (T10/T11), the schema
  (T13), and the operation-applier invariants (T18), and reviews worker output
  before merge — a worker's own report of completion is not sign-off (ADR-0007).

## Risks

- **Indic ASR realtime on laptop CPU is unproven** (ADR-0010). T16 must settle it
  early, because the answer may force quantisation, a distilled model, or a GPU
  requirement — all of which change the deployment story.
- **Barge-in quality, not WER, is what callers will judge.** Endpointing that
  cuts people off mid-sentence feels worse than slightly wrong transcription.
  Budget tuning time for VAD thresholds against real recorded calls.
- **Mis-recognition can route a caller confidently wrong**, which DTMF never
  does. The ADR-0009 confidence threshold is the mitigation and has no
  universally correct value.
- **Two players live at once** during the AGI → AudioSocket transition
  (ADR-0008), with the usual risk that the legacy path rots untested.

## Out of scope (later sprints)

- Runtime LLM dialog — free-form conversation with tool calls, beyond the tiered
  intent matching in ADR-0009. Needs its own ADR; the deterministic flow spine
  stays authoritative for now.
- Authoring a flow **by phone** (ADR-0011 notes it; depends on this sprint
  landing first).
- Outbound/campaign dialing, deliberately dropped in ADR-0012 and to be
  re-scoped as a new feature if wanted.
- Fine-tuning models on the recorded-call corpus (ADR-0010 §8) — the corpus is
  an asset, but exploiting it is its own workstream.
- Multi-tenancy: several flows/servers on one box.
