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

Merge-blocking, verifiable now (no new format/simulator required):

- [ ] `python3 -c "import ast,glob,sys; [ast.parse(open(f).read()) for f in glob.glob('bin/*.py')+glob.glob('tools/*.py')+glob.glob('libs/*.py')]"` parses clean (T1, T2).
- [ ] `2to3 -f print $(git ls-files 'bin/*.py' 'tools/*.py')` reports no changes (T2).
- [ ] `grep -rn 'os.isfile\|/opt/mojobol\|/opt/voh\|/opt/shwaasivr' bin/ libs/` returns nothing outside comments/docs (T1, T3).
- [ ] No bare `except:` in the touched files (T1): `grep -rn 'except:' libs/ bin/` is empty.
- [ ] The engine imports and initializes from a clone at an arbitrary path with only `MOJOBOL_CONFIG` set — no source edits (T3).

The stronger end-to-end acceptance ("example flow runs through the engine")
completes once the simulator (T7) exists; until then this sprint is verified by
the static/import checks above plus a manual dry-run.

## Not in this sprint

Everything format- or feature-shaped stays in **Sprint 1 — Essentials**
(`docs/sprints/sprint-01-essentials.md`): the native flow format (T4), loader
(T5), Verboice importer (T6), simulator (T7), LLM authoring (T8), and quickstart
(T9). Live-Asterisk hardening (SIP/RTP exposure, `os.system` → `subprocess`, GSM
bring-up) remains deferred to a later sprint.
