# Sprint 1 — Essentials (v3.0 revival)

**Goal:** a newcomer can go from a clone to a **working basic call flow** fast —
author a flow (by hand, by LLM, or imported from Verboice), **test it without a
PBX**, and read one honest path to going live. Live-telephony hardening is
explicitly out of scope for this sprint.

**Definition of done for the sprint:** `docs/quickstart.md` takes a new user to a
correctly simulated example call flow, and the engine no longer crashes on the
known bugs.

## Sprint backlog

Every task below is an ADR follow-up and is filed as an issue. The `Tn` ids match
`docs/issues/v3.0-sprint-01.yml`. Nothing here is worked without a corresponding
issue (see `docs/CONTRIBUTING-workflow.md`).

| Task | Issue | ADR | Depends on | Tier |
|------|-------|-----|-----------|------|
| T1 Fix runtime bugs (`os.path.isfile`, pandas, `stepCapture`) | #1 | 0006 | — | Haiku |
| T2 Port `bin/` scripts Py2 → Py3 | #2 | 0006 | — | Haiku |
| T3 De-hardcode paths; config via env/CLI | #3 | 0006 | — | Sonnet |
| T4 Native single-file flow format (schema + docs) | #4 | 0002 | — | Sonnet |
| T5 Native-flow loader in the engine | #5 | 0002 | T4 | Sonnet |
| T6 Verboice zip importer | #6 | 0003 | T4 | Sonnet |
| T7 Flow simulator / test CLI (no telephony) | #8 | 0005 | T5 | Sonnet |
| T8 LLM authoring guide + system prompt + examples | #7 | 0004 | T4 | Sonnet |
| T9 Quickstart deploy guide + smoke test | #9 | 0005 | T7 | Sonnet |

Issue bodies and acceptance criteria live in `docs/issues/v3.0-sprint-01.yml`.

## Execution order & parallelism (tiered agents — ADR-0007)

The Opus orchestrator owns architecture, integration, and review. Cheaper
Sonnet/Haiku agents do the well-specified mechanical work in parallel. Suggested
waves:

- **Wave A (parallel, independent):** T1, T2 (Haiku) · T3, T4 (Sonnet).
- **Wave B (after T4):** T5, T6, T8 (Sonnet, parallel).
- **Wave C (after T5):** T7 (Sonnet), then T9 (Sonnet) once T7 lands.
- **Integration/review:** Opus wires the `MojoPlayer` abstraction (T5/T7 seam),
  reviews each PR, and runs the simulator smoke test before merge.

## Out of scope (later sprints)
- Live Asterisk hardening: SIP/RTP port exposure, GSM ATA bring-up, container
  networking, `os.system` → `subprocess` with argument lists, multi-tenant paths.
- Speech recognition, session variables/branching beyond static `next`,
  external API/DB calls from a flow, SMS fallback.
- `tools/gen_todo.py` to regenerate `docs/TODO.md` from live issues.
