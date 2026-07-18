# TODO

> **This file is generated from GitHub issues — do not hand-edit.**
> Governance (ADR-0001): work is filed as an issue first; this list is a
> projection of the tracker. See `docs/CONTRIBUTING-workflow.md`.
>
> **Provisional (2026-07-18):** the revival token is read-only, so the Sprint 1
> items below are seeded from `docs/issues/v3.0-sprint-01.yml` and are **not yet
> live issues**. Once a token with `issues:write` exists, run
> `python3 tools/file_issues.py docs/issues/v3.0-sprint-01.yml` and regenerate
> this file from the tracker. Items already live on GitHub are linked.

## Open issues (live)

- **#8** — [FR] Simplified Installation Process → addressed by T9 below.
- **#7** — [FR] Add sample call flow and simple mechanism to add prompts →
  addressed by T6 below.

## Sprint 1 — Essentials (seeded, awaiting filing)

| id | Title | ADR | Status |
|----|-------|-----|--------|
| T1 | Fix runtime bugs (`os.path.isfile`, pandas, `stepCapture`) | 0006 | todo |
| T2 | Port `bin/` scripts Python 2 → Python 3 | 0006 | todo |
| T3 | De-hardcode paths; config via env var / CLI arg | 0006 | todo |
| T4 | Define native single-file flow format (schema + docs) | 0002 | todo |
| T5 | Add native-flow loader to the engine | 0002 | todo |
| T6 | Verboice zip importer (legacy → native) | 0003 | todo |
| T7 | Flow simulator / test CLI (no telephony) | 0005 | todo |
| T8 | LLM conversational flow-authoring guide + prompt | 0004 | todo |
| T9 | Quickstart deploy guide + smoke test | 0005 | todo |

Full bodies and acceptance criteria: `docs/issues/v3.0-sprint-01.yml`.
Sprint plan and execution waves: `docs/sprints/sprint-01-essentials.md`.
