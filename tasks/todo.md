# mojobol — tasks

Local, hand-maintained work record. **This is not the issue tracker.**
`docs/TODO.md` is machine-generated from the GitHub issues (seeded from
`docs/issues/*.yml` via `tools/file_issues.py`) and carries a "do not hand-edit"
banner — under ADR-001 work is filed as an issue first and that file is only a
projection of the tracker. This file cross-links to it rather than duplicating
the generated table, and additionally holds shipped history, watch items, and
items too small or too local to be issues.

- Generated issue projection: [`docs/TODO.md`](../docs/TODO.md)
- Tracker: https://github.com/arjunvenkatraman/mojobol/issues
- Decisions: [`docs/decisions/`](../docs/decisions/) · Sprint plans: [`docs/sprints/`](../docs/sprints/)

## Shipped

- [x] v3.0 revival decision set — ADR-001 … ADR-007 in `docs/decisions/`, plus
      the ADR → issue → TODO governance rule (`docs/CONTRIBUTING-workflow.md`)
- [x] Sprint 1 backlog filed as issues #1–#9; bodies kept in
      `docs/issues/v3.0-sprint-01.yml`; plan in `docs/sprints/sprint-01-essentials.md`
- [x] Design memo on the GUID-free native flow format —
      `docs/design/native-format-and-guids.md` (feeds T4/T6)
- [x] **Fix Sprint** (`docs/sprints/sprint-fixes.md`, ADR-006):
  - [x] T1 — runtime bug fixes: `os.isfile` → `os.path.isfile` in
        `compresscallfile`, pandas removed from `updatedf` (now stdlib `csv`),
        `stepCapture`'s use-before-assignment fixed, bare `except:` removed ([#1](https://github.com/arjunvenkatraman/mojobol/issues/1))
  - [x] T2 — `bin/` and `tools/` scripts ported to Python 3 ([#2](https://github.com/arjunvenkatraman/mojobol/issues/2))
  - [x] T3 — de-hardcoded engine paths; config resolves CLI arg >
        `MOJOBOL_CONFIG` > in-repo `conf/sampleserver.conf` ([#3](https://github.com/arjunvenkatraman/mojobol/issues/3))
  - [x] Validation suite (`tests/`) + CI on Python 3.11 (`.github/workflows/ci.yml`)
- [x] Restored the executable bit on `bin/` scripts after a permissions commit
      stripped it (#24)
- [x] `/xpal-src` project conventions — `CLAUDE.md`, ADRs moved from `docs/adr/`
      to `docs/decisions/` as `ADR-NNN-kebab-title.md`, `tasks/todo.md` +
      `tasks/lessons.md`

## Upcoming

Sprint 1 — Essentials; all filed, see `docs/sprints/sprint-01-essentials.md`
for waves and dependencies.

- [ ] T4 — define the native single-file `flow.yml` format: schema, per-type
      fields, multi-language convention, authoring docs (ADR-002, [#4](https://github.com/arjunvenkatraman/mojobol/issues/4))
- [ ] T5 — native-flow loader in `libs/mojobol.py`, feeding the same in-memory
      step structure `executeStep` already consumes (ADR-002, [#5](https://github.com/arjunvenkatraman/mojobol/issues/5); needs T4)
- [ ] T6 — `tools/import_verboice.py`: one-way Verboice `.zip` → native
      `flow.yml`, resolving GUID cross-references (ADR-003, [#6](https://github.com/arjunvenkatraman/mojobol/issues/6); needs T4)
- [ ] T7 — extract a `MojoPlayer` interface from `MojoAsteriskPlayer`, add a
      text/stdin player and `bin/mojobol-simulate.py` (ADR-005, [#8](https://github.com/arjunvenkatraman/mojobol/issues/8); needs T5)
- [ ] T8 — LLM conversational flow-authoring guide, system prompt and worked
      examples (ADR-004, [#7](https://github.com/arjunvenkatraman/mojobol/issues/7); needs T4)
- [ ] T9 — `docs/quickstart.md` deploy guide + smoke test run against the
      simulator rather than a live call (ADR-005, [#9](https://github.com/arjunvenkatraman/mojobol/issues/9); needs T7)

Not filed as issues (local, small):

- [ ] `tools/gen_todo.py` — regenerate `docs/TODO.md` from the live tracker;
      today the projection is refreshed by hand, which is the one manual step in
      an otherwise mechanical loop (listed as out of scope in
      `docs/sprints/sprint-01-essentials.md`)
- [ ] Decide the fate of `bin/mojobol-svr-dev.py` — it differs from
      `bin/mojobol-svr.py` only by a missing trailing newline

## Known issues / watch items

- **`livingdata/` and `mojomailman/` are bare gitlinks with no `.gitmodules`.**
  `git submodule status` errors out on a fresh clone. They correspond to the
  `mojolab/livingdata` and `mojolab/mojomailman` repos that
  `installmojoboldeps.sh` clones into `/opt`; either register them properly or
  remove the gitlinks.
- **File-mode churn.** Commit `4defe6d` flipped scripts from 755 to 644 and
  `1989597` restored the `bin/` ones; `setupasterisk.sh` and
  `installmojoboldeps.sh` are invoked as `sh <script>` in the docs, so a lost
  exec bit is easy to miss. Check `git diff --summary` for `mode change` before
  committing.
- **Legacy `/opt` paths remain outside the engine.** `bin/mojobol-svr-out.py`,
  `bin/returncalls.py`, `bin/generatemenureport.py`, `bin/mojobolmailer.py`,
  `libs/mojobolmailer.py`, `tools/emailmojobolcalls.py`,
  `tools/mojobolmailharness.py` and `setupasterisk.sh` still hardcode
  `/opt/mojobol`, `/opt/voh` and friends. Deliberately out of scope for the Fix
  Sprint; only the engine entrypoints are guarded by `tests/test_static.py`.
- **No live-telephony test coverage.** The suite covers static guards, config
  resolution and post-call bookkeeping only; anything AGI/SIP/audio-encoding
  shaped still needs a real call until T7 lands.
- **Verboice is the only runnable flow format** until T5 ships, and the
  mailer-dependent scripts need the external MojoMail package to import at all.
- **`tools/updatepermissions.sh` runs `chmod a+rwx -R /opt`** — very broad, and
  the same blanket-chmod pattern T3 removed from `setupasterisk.sh`.
- **Duplicate install docs.** `README.md`, `INSTALL.md` and `INSTALLATION` carry
  three overlapping copies of the install instructions, all still pointing at
  the old GitLab remote and Python 2 packages.
