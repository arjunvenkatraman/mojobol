# ADR-0006: Python 3 only, runtime bug fixes, and config via env/CLI

- Status: Accepted
- Date: 2026-07-18
- Deciders: Mojolab (Arjun Venkatraman)
- Related issues: T1, T2, T3
- Related ADRs: ADR-0005

## Context
Mojobol's engine (`libs/mojobol.py`, `libs/mojoasteriskplayer.py`) is Python 3,
but several `bin/` scripts are still Python 2 and the codebase carries a set
of confirmed defects and deployment assumptions accumulated since the last
commit in Jan 2022:
- `bin/mojobol-svr-out.py`, `bin/returncalls.py`, and
  `bin/generatemenureport.py` use Python 2 `print` statements and do not run
  under Python 3.
- `libs/mojobol.py`'s `compresscallfile` calls `os.isfile` (no such function;
  should be `os.path.isfile`), so archiving call files raises `AttributeError`.
- `libs/mojobol.py`'s `updatedf` uses `pandas`, which is imported nowhere
  (commented out at the top of the file) and is not a declared dependency;
  `bin/mojobol-svr.py` calls `updatedf` on every call, so every call crashes
  once it reaches that path.
- `libs/mojoasteriskplayer.py`'s `stepCapture` (around line 212) references
  `stepresources` before it is assigned in that method — a dead/broken code
  path.
- Paths are hard-coded throughout: `sys.path.append('/opt/mojobol/libs')` in
  `bin/` entrypoints, `MojoBolResponder("/opt/shwaasivr/voh.conf")` (and a
  `/opt/voh/voh.conf` variant) baked into the AGI entrypoint, and the config
  file location hard-coded in `bin/mojobol-svr.py`. This makes the repo
  non-runnable from any checkout other than `/opt/mojobol` and ties config to
  a single deployment.

## Decision
Standardize the whole codebase on Python 3:
- Port `bin/mojobol-svr-out.py`, `bin/returncalls.py`, and
  `bin/generatemenureport.py` to Python 3 syntax (print function, `except ... as e`,
  etc.), matching the style already used in the engine files.
- Fix the confirmed runtime bugs: `os.isfile` → `os.path.isfile`; make
  `updatedf`/pandas usage optional (either drop the call from
  `mojobol-svr.py`'s per-call path, or gate it behind an explicit
  `pandas`-available check so its absence never crashes a call); fix or
  remove the broken `stepCapture` method in `mojoasteriskplayer.py`.
- Remove hard-coded absolute paths. Library imports resolve the repo root
  relative to `__file__` instead of appending `/opt/mojobol/libs` to
  `sys.path`. Deployment configuration (workflow config path, calls
  directory, etc.) is read from a `MOJOBOL_CONFIG` environment variable or a
  `--config` CLI argument, with no built-in default pointing at `/opt/...`.

## Consequences
### Positive
- Every script in the repo runs under a single, currently-supported Python
  version; no more guessing which interpreter a given `bin/` script needs.
- The crash-on-every-call bugs (`os.isfile`, `updatedf`/pandas) are removed,
  so `mojobol-svr.py` can complete a call end-to-end.
- The repo becomes runnable from any checkout location (including the
  simulator in ADR-0005 and CI), rather than only from `/opt/mojobol`.

### Negative / Trade-offs
- Porting `bin/` scripts and de-hardcoding paths touches files with no test
  coverage; each change should be paired with a simulator run (ADR-0005)
  where possible to catch regressions.
- Removing pandas from `updatedf` may drop functionality that was intended
  but never finished; if that reporting feature is still wanted, it needs to
  be re-scoped as a separate, deliberate feature rather than silently revived.
- Config-via-env/CLI is a behavior change for any existing deployment that
  relies on the old hard-coded `/opt/...` paths; deploy docs (T9) must be
  updated in lockstep.

## Follow-up work (to be filed as issues)
- [ ] T1 — Fix `os.isfile` → `os.path.isfile` in `libs/mojobol.py` (`compresscallfile`)
- [ ] T1 — Remove or safely gate the pandas-dependent `updatedf` call in `bin/mojobol-svr.py`
- [ ] T1 — Fix or remove the broken `stepCapture` method in `libs/mojoasteriskplayer.py` (`stepresources` used before assignment)
- [ ] T2 — Port `bin/mojobol-svr-out.py` to Python 3
- [ ] T2 — Port `bin/returncalls.py` to Python 3
- [ ] T2 — Port `bin/generatemenureport.py` to Python 3
- [ ] T3 — Replace `sys.path.append('/opt/mojobol/libs')`-style imports with `__file__`-relative resolution across `bin/`
- [ ] T3 — Read deployment config from `MOJOBOL_CONFIG` env var or `--config` CLI arg instead of hard-coded `/opt/shwaasivr/voh.conf` / `/opt/voh/voh.conf` paths
