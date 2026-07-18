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

> **Note (2026-07):** the automation account used during the revival has
> read-only GitHub access, so the first wave of issues could not be filed
> programmatically. Their ready-to-file bodies live in `docs/issues/` and can be
> created with `tools/file_issues.py` once a token with `issues:write` is
> available. Until then, `docs/TODO.md` is seeded from those same bodies and
> marked provisional.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-adopt-single-file-native-flow-format.md) | Adopt a single-file native flow format | Accepted |
| [0003](0003-keep-verboice-as-import-only-compatibility.md) | Keep Verboice as import-only compatibility | Accepted |
| [0004](0004-llm-conversational-flow-authoring.md) | LLM conversational flow authoring | Accepted |
| [0005](0005-simulator-first-testing.md) | Simulator-first testing | Accepted |
| [0006](0006-python3-only-and-config-via-env.md) | Python 3 only; config via env/CLI | Accepted |
| [0007](0007-tiered-agent-delivery.md) | Tiered-agent delivery | Accepted |

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
