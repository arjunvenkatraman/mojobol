# Architecture Decision Records (ADRs)

This directory records the significant architectural decisions for Mojobol,
starting with the **v3.0 revival**. We use lightweight
[Nygard-style](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
ADRs.

## Why ADRs

Mojobol stalled in 2022. Reviving it means making a handful of load-bearing
decisions (flow format, authoring tooling, testing strategy, cleanup scope).
Recording them keeps the "why" from evaporating and gives new contributors a
map of the reasoning.

## Governance rule: ADRs → issues → TODOs

This project follows one strict rule for tracking work:

1. **Every actionable item that emerges from an ADR is filed as a GitHub issue.**
   Each ADR ends with a `## Follow-up work (to be filed as issues)` section. Those
   checkboxes are the source list.
2. **The TODO list is sourced only from filed issues** — never hand-authored.
   `docs/TODO.md` is a projection of the repository's open issues, not a
   free-floating wishlist. If something should be done, it is an issue first.

This means: ADR → follow-up items → GitHub issues → `docs/TODO.md`. Nothing
skips a step. See `docs/CONTRIBUTING-workflow.md` for the day-to-day loop.

> **Note (2026-07):** the first wave of follow-ups (Sprint 1) is filed as
> `arjunvenkatraman/mojobol` #1–#9. Their bodies are kept in `docs/issues/` as
> the source of record and can be re-filed/synced with `tools/file_issues.py`;
> `docs/TODO.md` is a projection of those live issues.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-adopt-single-file-native-flow-format.md) | Adopt a single-file native flow format | Accepted |
| [0003](0003-keep-verboice-as-import-only-compatibility.md) | Keep Verboice as import-only compatibility | Accepted |
| [0004](0004-llm-conversational-flow-authoring.md) | LLM conversational flow authoring | Accepted (mechanism amended by 0011) |
| [0005](0005-simulator-first-testing.md) | Simulator-first testing | Accepted (interface amended by 0008) |
| [0006](0006-python3-only-and-config-via-env.md) | Python 3 only; config via env/CLI | Accepted |
| [0007](0007-tiered-agent-delivery.md) | Tiered-agent delivery | Accepted |
| [0008](0008-streaming-media-path-and-async-player.md) | Streaming media path via AudioSocket; async MojoPlayer | Proposed |
| [0009](0009-dual-mode-dtmf-and-voice-input.md) | Dual-mode input — DTMF *and* speech | Proposed |
| [0010](0010-edge-speech-model-stack.md) | Edge-hosted small-model speech stack | Proposed |
| [0011](0011-flow-authoring-with-local-small-models.md) | Flow authoring with local small models | Proposed |
| [0012](0012-narrow-scope-to-telephony-and-capture.md) | Narrow scope to telephony + data capture | Proposed |

### The live-voice wave (0008–0012)

ADRs 0001–0007 revive mojobol as a **turn-based DTMF IVR**. ADRs 0008–0012 take
it to **live voice conversation on edge hardware**, while keeping DTMF as a
first-class input rather than replacing it. They are `Proposed` pending
sign-off. Two of them are deliberately timed to land *before* in-flight Sprint 1
work freezes an interface:

- **ADR-0008 amends ADR-0005** — `MojoPlayer` must be async and cancellable, or
  barge-in has nowhere to live and the extraction has to happen twice (#8 is in
  flight).
- **ADR-0009 amends ADR-0002** — the flow schema needs `listen`, `barge_in` and
  intent `phrases` before it freezes, because T5, T6, T7 and T8 all depend on
  #4.

## Writing a new ADR

Copy the template below into `NNNN-short-title.md` (next number), fill it in,
open a PR, and add its follow-up items to `docs/issues/` (or file them directly
when you have write access).

```
# ADR-NNNN: <Title>

- Status: Proposed | Accepted | Superseded by ADR-XXXX
- Date: YYYY-MM-DD
- Deciders: <names>
- Related issues: <#N ...>
- Related ADRs: <ADR-XXXX ...>

## Context
## Decision
## Consequences
### Positive
### Negative / Trade-offs

## Follow-up work (to be filed as issues)
- [ ] T<n> — <short imperative title>
```
