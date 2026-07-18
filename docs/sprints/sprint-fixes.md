# Fix Sprint — Stabilize the engine (v3.0 revival)

**Goal:** make the existing engine *run* — no crashes, Python 3 throughout, and
launchable from a fresh clone at any path — before any net-new v3.0 feature work
lands on top of it. This is the hardening pass that de-risks Sprint 1
(Essentials): the simulator (T7) and quickstart (T9) can only prove themselves
against an engine that starts and survives a call.

**Why a separate sprint:** the three tasks below are all **ADR-0006** follow-ups
(correctness + portability), carry no dependency on the new flow format, and are
each small and mechanical. Pulling them out lets the cheap-tier agents clear them
in parallel and get merged while the format/loader/simulator design (T4/T5/T7)
proceeds independently.

**Definition of done:** a fresh clone runs the example flow end-to-end through the
engine on Python 3 without raising on any of the known-bad paths, with no source
edits for local paths.

## Sprint backlog

All three are already filed; `Tn` ids match `docs/issues/v3.0-sprint-01.yml`.

| Task | Issue | ADR | Depends on | Tier | Effort |
|------|-------|-----|-----------|------|--------|
| T1 Fix runtime bugs (`os.path.isfile`, pandas dep, `stepCapture`, bare `except`) | [#1](https://github.com/arjunvenkatraman/mojobol/issues/1) | 0006 | — | Haiku | S |
| T2 Port `bin/` scripts Python 2 → 3 (+ CI parse check) | [#2](https://github.com/arjunvenkatraman/mojobol/issues/2) | 0006 | — | Haiku | S |
| T3 De-hardcode paths; config via `MOJOBOL_CONFIG` env / `--config` | [#3](https://github.com/arjunvenkatraman/mojobol/issues/3) | 0006 | — | Sonnet | M |

## Execution order & parallelism (tiered agents — ADR-0007)

The three are mutually independent — all can start at once.

- **Wave A (parallel, day 1):** T1 and T2 on **Haiku** (well-specified, mechanical
  edits); T3 on **Sonnet** (needs a small config-resolution design decision).
- **Sequencing note:** land T1 first where they touch the same file — T1 fixes
  `libs/mojobol.py` (`compresscallfile`, `updatedf`) and `libs/mojoasteriskplayer.py`;
  T2 rewrites `bin/*.py`; T3 changes path resolution in `bin/mojobol-svr.py` and
  `setupasterisk.sh`. Overlap is minimal, but if T2/T3 both touch a `bin/` script,
  merge T2 (the Py3 port) first so T3 rebases onto Py3 syntax.
- **Integration/review:** the Opus orchestrator reviews each PR and runs the
  smoke check (below) before merge. Each task ships as its own PR against the
  revival branch.

## Exit checklist

Merge-blocking, verifiable now (no new format/simulator required) — all of these
are enforced by `pytest` (`tests/`, run in CI via `.github/workflows/ci.yml`):

- [x] Every `.py` under `bin/`, `libs/`, `tools/`, `tests/` parses under Python 3
  — a stale `print x` is a SyntaxError (T2). `tests/test_static.py`.
- [x] No `os.isfile` typo and no `pandas` import/use in the engine (T1).
- [x] No bare `except:` in `bin/` or `libs/` (T1).
- [x] `stepCapture` assigns `stepresources` before use (T1).
- [x] No hardcoded `/opt/...` deployment paths in the engine entrypoints
  (`libs/mojobol.py`, `libs/mojoasteriskplayer.py`, `bin/mojobol-svr*.py`) and no
  blanket `chmod a+rwx -R /opt/mojobol` in `setupasterisk.sh` (T3).
- [x] Config resolves via CLI arg > `MOJOBOL_CONFIG` > in-repo default (T3);
  the engine builds `MojoBolResponder` against the sample flow and runs the
  call-teardown paths (`updatedf`, `compresscallfile`) without crashing
  (`tests/test_engine.py`).

Run locally with `pip install -r requirements.txt && pytest -q`.

The stronger end-to-end acceptance ("example flow runs through the engine"
interactively) completes once the simulator (T7) exists; the integration tests
here cover initialization and post-call bookkeeping in the meantime. The legacy
outbound/report scripts (`mojobol-svr-out.py`, `returncalls.py`,
`generatemenureport.py`) are ported to Py3 syntax but retain their site-specific
`/opt` paths and Asterisk CLI calls — de-hardcoding those is out of scope here.

## Not in this sprint

Everything format- or feature-shaped stays in **Sprint 1 — Essentials**
(`docs/sprints/sprint-01-essentials.md`): the native flow format (T4), loader
(T5), Verboice importer (T6), simulator (T7), LLM authoring (T8), and quickstart
(T9). Live-Asterisk hardening (SIP/RTP exposure, `os.system` → `subprocess`, GSM
bring-up) remains deferred to a later sprint.
