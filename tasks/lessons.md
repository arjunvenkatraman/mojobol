# Lessons learned

## 2026-07-18 — What four years without tests hid

- **Every call crashed at teardown.** `libs/mojobol.py`'s `compresscallfile`
  called `os.isfile` (no such function — it is `os.path.isfile`), and `updatedf`
  used `pandas`, which was commented out at the top of the file and was never a
  declared dependency. `bin/mojobol-svr.py` calls `updatedf` on every call, so
  the post-call path raised on every single call. Neither bug is subtle; both
  survived since Jan 2022 purely because there was no way to run the engine
  without a live PBX and a phone.
- **`stepCapture` referenced `stepresources` before assigning it** — a dead code
  path in `libs/mojoasteriskplayer.py`. When extracting the `MojoPlayer`
  interface (ADR-005), define it against the *intended* behaviour, not the
  current implementation.
- **Static guards are cheap and catch the whole class.** `tests/test_static.py`
  AST-parses every `.py` under `bin/`, `libs/`, `tools/`, `tests/` and asserts on
  Python 2 syntax, bare `except:`, `os.isfile`, and hardcoded `/opt` paths in the
  engine entrypoints. That needs no telephony and would have caught all three
  bugs above.

## 2026-07-18 — The Verboice export format is a serialization, not a document

- A single flow is a *directory*: `workflow.yml` plus one `resource*.yml` and one
  `localized_resource*.yml` per prompt, cross-referenced by GUIDs whose filenames
  are the GUIDs. Nothing next to a step tells you what it says; understanding a
  flow means hopping between files.
- **There is no schema validation anywhere in the engine.** A mistyped GUID does
  not fail at load time — it fails mid-call. That property is the main argument
  for ADR-002's single-file native format and for validating before deploy.
- The engine's step vocabulary (`play`, `capture`, `menu`, `record`, `playloop`)
  is the stable part. Keeping it lets the native format land as a new loader
  rather than a rewrite of `executeStep`.

## 2026-07-18 — Issue-first tracking needs the tooling to exist first

- The automation token available during the revival was read-only, so the first
  wave of issues had to be written into `docs/issues/v3.0-sprint-01.yml` and
  filed later. Keeping issue bodies in-repo turned out to be the right default
  anyway — they are reviewable and re-filable.
- **`tools/file_issues.py` de-duplicates on the exact issue title**, so a title
  edited in the YAML after filing will create a *second* issue rather than
  update the first. Treat titles as the key.
- `docs/TODO.md` is the projection, not the source. There is still no
  `tools/gen_todo.py`, so regenerating it is the one manual step in an otherwise
  mechanical ADR → issue → TODO loop.

## 2026-08-27 — Mode-only diffs are invisible

- A permissions commit (`4defe6d`) flipped a batch of scripts from 755 to 644
  and broke the `bin/` entrypoints Asterisk executes; it took a follow-up commit
  (`1989597`, PR #24) to restore them. Mode changes show up as a one-line
  `mode change` in `git diff --summary` and as nothing at all in a normal diff
  view, so they get waved through in review.
- Before committing anything in this repo, run `git diff --summary | grep -i mode`
  and expect it to be empty unless the exec bit is the actual point of the change.

## 2026-09-10 — ADR renames reach further than the ADR directory

- Moving `docs/adr/NNNN-*.md` to `docs/decisions/ADR-NNN-*.md` required edits in
  places that do not look like documentation: the `adr:` metadata field and issue
  bodies in `docs/issues/v3.0-sprint-01.yml`, a bare-number `ADR` column in both
  sprint tables, and two source comments in `libs/mojobol.py`. `git grep` for the
  path, the `ADR-NNNN` form *and* the bare number before declaring a rename done.
- `docs/TODO.md` is deliberately left carrying the old `ADR-0001` / `0006` forms:
  it is generated and marked "do not hand-edit". Fixing the *source*
  (`docs/issues/*.yml`) is what makes the next regeneration correct — editing the
  projection by hand would just desync it from the tracker.
