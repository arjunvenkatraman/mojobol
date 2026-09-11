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
| [ADR-001](ADR-001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [ADR-002](ADR-002-adopt-single-file-native-flow-format.md) | Adopt a single-file native flow format | Accepted |
| [ADR-003](ADR-003-keep-verboice-as-import-only-compatibility.md) | Keep Verboice as import-only compatibility | Accepted |
| [ADR-004](ADR-004-llm-conversational-flow-authoring.md) | LLM conversational flow authoring | Accepted |
| [ADR-005](ADR-005-simulator-first-testing.md) | Simulator-first testing | Accepted |
| [ADR-006](ADR-006-python3-only-and-config-via-env.md) | Python 3 only; config via env/CLI | Accepted |
| [ADR-007](ADR-007-tiered-agent-delivery.md) | Tiered-agent delivery | Accepted |

## Writing a new ADR

File names follow the `/xpal-src` workspace convention:
`ADR-NNN-kebab-title.md`, where `NNN` is the next number, zero-padded to three
digits. (These records lived in `docs/adr/` as `NNNN-kebab-title.md` until the
move to `docs/decisions/`; the numbers were preserved, only re-padded.)

Copy the template below into `ADR-NNN-short-title.md` (next number), fill it in,
open a PR, and add its follow-up items to `docs/issues/` (or file them directly
when you have write access).

```
# ADR-NNN: <Title>

- Status: Proposed | Accepted | Superseded by ADR-XXX
- Date: YYYY-MM-DD
- Deciders: <names>
- Related issues: <#N ...>
- Related ADRs: <ADR-XXX ...>

## Context
## Decision
## Consequences
### Positive
### Negative / Trade-offs

## Follow-up work (to be filed as issues)
- [ ] T<n> — <short imperative title>
```
