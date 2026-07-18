# ADR-0001: Record architecture decisions

- Status: Accepted
- Date: 2026-07-18
- Deciders: Mojolab (Arjun Venkatraman)
- Related issues: —
- Related ADRs: —

## Context

Mojobol is a small but real IVR execution engine that was last touched in
January 2022. The v3.0 revival changes several load-bearing things at once — the
flow format, how flows are authored, how they are tested, and a sweep of code
cleanup. Decisions of this kind tend to be made in chat and then lost, leaving
future contributors to reverse-engineer intent from the diff.

We also want a disciplined way to turn decisions into tracked work rather than
letting "we should also…" items scatter across commit messages and memory.

## Decision

We will keep Architecture Decision Records in `docs/adr/`, one Markdown file per
decision, numbered sequentially, using the Nygard-lite template documented in
`docs/adr/README.md`.

We adopt one governance rule for the whole project:

- Every actionable item that emerges from an ADR is captured in that ADR's
  **Follow-up work** section and filed as a **GitHub issue**.
- **`docs/TODO.md` is generated only from filed issues** — it is never a
  hand-authored wishlist. Work is an issue first, a TODO line second.

## Consequences

### Positive
- The "why" behind v3.0 is durable and reviewable in-repo.
- There is a single, mechanical path from decision → issue → TODO, so nothing
  actionable lives only in someone's head.
- New contributors can read `docs/adr/` top-to-bottom to understand the design.

### Negative / Trade-offs
- Small overhead: each significant decision needs a short write-up, and each
  ADR follow-up must be mirrored as an issue.
- The issue-sourced TODO needs tooling (`tools/file_issues.py`, and a future
  `tools/gen_todo.py`) to stay honest; until GitHub write access is granted the
  first batch is seeded manually and marked provisional.

## Follow-up work (to be filed as issues)
- None — this is a process ADR. Its output is the governance rule itself,
  which the other ADRs' follow-up sections implement.
