# TODO

> **This file is generated from GitHub issues — do not hand-edit.**
> Governance (ADR-0001): work is filed as an issue first; this list is a
> projection of the tracker. See `docs/CONTRIBUTING-workflow.md`.
>
> **Live (2026-07-29):** Sprint 1 is filed as #1–#9 (labels `v3.0`,
> `sprint-1`); Sprint 2 as #11–#23 (labels `v3.0`, `sprint-2`). Seed sources of
> record are `docs/issues/v3.0-sprint-01.yml` and `docs/issues/v3.0-sprint-02.yml`,
> re-filable via `tools/file_issues.py`.

## Sprint 1 — Essentials (live)

| id | Issue | Title | ADR | Status |
|----|-------|-------|-----|--------|
| T1 | [#1](https://github.com/arjunvenkatraman/mojobol/issues/1) | Fix runtime bugs (`os.path.isfile`, pandas, `stepCapture`) | 0006 | todo |
| T2 | [#2](https://github.com/arjunvenkatraman/mojobol/issues/2) | Port `bin/` scripts Python 2 → Python 3 | 0006 | todo |
| T3 | [#3](https://github.com/arjunvenkatraman/mojobol/issues/3) | De-hardcode paths; config via env var / CLI arg | 0006 | todo |
| T4 | [#4](https://github.com/arjunvenkatraman/mojobol/issues/4) | Define native single-file flow format (schema + docs) | 0002 | **blocked by #11** |
| T5 | [#5](https://github.com/arjunvenkatraman/mojobol/issues/5) | Add native-flow loader to the engine | 0002 | todo |
| T6 | [#6](https://github.com/arjunvenkatraman/mojobol/issues/6) | Verboice zip importer (legacy → native) | 0003 | todo |
| T7 | [#8](https://github.com/arjunvenkatraman/mojobol/issues/8) | Flow simulator / test CLI (no telephony) | 0005 | **blocked by #12** |
| T8 | [#7](https://github.com/arjunvenkatraman/mojobol/issues/7) | LLM conversational flow-authoring guide + prompt | 0004 | amended by #20 |
| T9 | [#9](https://github.com/arjunvenkatraman/mojobol/issues/9) | Quickstart deploy guide + smoke test | 0005 | todo |

Full bodies and acceptance criteria: `docs/issues/v3.0-sprint-01.yml`.
Sprint plan and execution waves: `docs/sprints/sprint-01-essentials.md`.

## Sprint 2 — Live voice on the edge (live)

> **Sequencing:** #11 and #12 come first. Both amend in-flight Sprint 1 work
> and are cheap now, expensive later — #11 gates #4 (and therefore T5, T6, T7,
> T8), and #12 must land before the `MojoPlayer` extraction in #8 freezes into
> a blocking, DTMF-only shape.

| id | Issue | Title | ADR | Depends on | Status |
|----|-------|-------|-----|-----------|--------|
| T13 | [#11](https://github.com/arjunvenkatraman/mojobol/issues/11) | Extend flow schema for voice (`listen`, `barge_in`, intent `phrases`) | 0009 | — | todo |
| T10 | [#12](https://github.com/arjunvenkatraman/mojobol/issues/12) | Define async, cancellable `MojoPlayer` interface | 0008 | — | todo |
| T15 | [#13](https://github.com/arjunvenkatraman/mojobol/issues/13) | Pluggable speech engines; espeak → Piper TTS | 0010 | — | todo |
| T21 | [#14](https://github.com/arjunvenkatraman/mojobol/issues/14) | Remove mail/batch/outbound/reporting subsystems | 0012 | — | **in review** |
| T12 | [#15](https://github.com/arjunvenkatraman/mojobol/issues/15) | Minimal PJSIP + AudioSocket dialplan + SIP/RTP exposure | 0008 | — | todo |
| T16 | [#16](https://github.com/arjunvenkatraman/mojobol/issues/16) | Benchmark edge speech models on target hardware | 0010 | #13 | todo |
| T11 | [#17](https://github.com/arjunvenkatraman/mojobol/issues/17) | AudioSocket player + asyncio per-call driver | 0008 | #12 | todo |
| T14 | [#18](https://github.com/arjunvenkatraman/mojobol/issues/18) | Dual-mode input resolution + tiered intent matching | 0009 | #11, #17 | todo |
| T22 | [#19](https://github.com/arjunvenkatraman/mojobol/issues/19) | SQLite capture store + export; drop `calllog` symlink | 0012 | — | todo |
| T17 | [#20](https://github.com/arjunvenkatraman/mojobol/issues/20) | Schema-constrained generation harness (local small models) | 0011 | #11 | todo |
| T18 | [#21](https://github.com/arjunvenkatraman/mojobol/issues/21) | Flow-edit operation vocabulary + deterministic applier | 0011 | #11 | todo |
| T19 | [#22](https://github.com/arjunvenkatraman/mojobol/issues/22) | Interview-driven authoring CLI + retrieve-and-adapt | 0011 | #20, #21 | todo |
| T20 | [#23](https://github.com/arjunvenkatraman/mojobol/issues/23) | Validate/lint/simulate/repair loop + human gate | 0011 | #21 | todo |

Full bodies and acceptance criteria: `docs/issues/v3.0-sprint-02.yml`.
Sprint plan, execution waves and risks: `docs/sprints/sprint-02-live-voice.md`.
