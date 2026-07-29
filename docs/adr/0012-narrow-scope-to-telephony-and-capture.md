# ADR-0012: Narrow scope to telephony interaction and data capture

- Status: Proposed
- Date: 2026-07-29
- Deciders: Mojolab (Arjun Venkatraman) — pending sign-off
- Related issues: T21, T22
- Related ADRs: ADR-0008, ADR-0010

## Context
mojobol accumulated a set of subsystems across its 2015–2022 deployments that are
not telephony and not data capture:

- `libs/mojobolmailer.py`, `bin/mojobolmailer.py`, `tools/emailmojobolcalls.py`,
  `tools/mojobolmailharness.py` — emailing call artefacts;
- `MojoBolCall.compresscallfile()` — zipping each call directory into a `maildir`
  for that mailer;
- `bin/mojobol-svr-out.py` — a CSV-driven outbound dialer that polls
  `asterisk -rx 'sip show channels'`, greps for a hardcoded IP, and drops call
  files via `os.system("cp ...")` / `perl -p -i -e`;
- `bin/returncalls.py` — the same pattern for callbacks, against a different
  hardcoded IP;
- `bin/generatemenureport.py` — batch CSV reporting over the per-call YAML files;
- `conf/call.skel`, the `[MojoMailer]` config section, and a dangling
  `mojomailman` git submodule pointer with no `.gitmodules` entry;
- `installmojoboldeps.sh` pulling in MySQL, PHP5, Apache2 and a GUI text editor.

All of it is deployment-specific batch glue. None of it is tested. Several parts
interpolate phone numbers straight into shell commands. Two of the scripts still
carried `/opt/voh` paths that ADR-0006 removed everywhere else, and the
`livingdata` CSV library they import is a separate repo that has to be cloned
into `/opt` by hand.

Meanwhile the thing they exist to serve — capturing what callers actually said and
pressed — is spread across three mechanisms that do not agree: per-call
`menuresponsefile-*.yml` files appended mid-call, a single global
`mojobol_data.csv` rewritten in full on every call, and the zip-and-email path.

Keeping this while adding a streaming voice stack (ADR-0008) means maintaining two
eras of the platform at once, on a box that is supposed to be lightweight enough
to run on a laptop.

## Decision

**1. In scope, and nothing else:** answer and handle a call, run a flow, capture
the data. Everything listed above is removed rather than ported.

**2. Data capture consolidates on SQLite** — one file per deployment, via the
stdlib `sqlite3`, in WAL mode so concurrent calls can write. It replaces all
three current mechanisms: the per-call YAML response files, the global CSV
rewrite, and the zip/mail delivery. Schema covers calls, turns and captured
values; recorded audio stays on disk as a file referenced by its row. A
`tools/export.py` emits CSV/JSONL for anyone who wants the old spreadsheet
workflow.

SQLite is the right answer specifically for this deployment shape: zero
dependencies, zero administration, a single file to copy off a field box, and
transactional integrity across concurrent calls — which the current
read-modify-write CSV does not have.

**3. The global `calllog` symlink goes.** `MojoBolCall.__init__` currently
`os.remove`s and re-`os.symlink`s a single shared `calllog` path on every call.
That assumes exactly one call at a time and is an outright concurrency bug the
moment ADR-0008's engine serves two. Per-call log files stay; the shared symlink
does not.

**4. Outbound calling is not "deleted pending revival."** If campaign dialing is
wanted again, it is re-scoped deliberately as a feature with its own ADR — not
resurrected from these scripts, whose polling-and-shell-out approach should not
survive into v3.0 in any form.

## Consequences
### Positive
- Removes ~300 lines of untested, deployment-specific code and, with it, the
  shell-interpolation of phone numbers.
- One capture mechanism with a real schema, instead of three that disagree;
  captured data becomes queryable rather than needing a batch job to assemble.
- Drops MySQL, PHP, Apache, the `livingdata` clone and the dangling
  `mojomailman` submodule from setup, which is most of what made the install
  heavy.
- Fixes a live concurrency bug (the shared symlink) that would otherwise surface
  as confusing cross-talk between simultaneous calls.

### Negative / Trade-offs
- **Outbound campaign dialing was a real capability** for some deployments, and
  this removes it with no replacement. That is a genuine loss of function, not
  just cleanup, and should be a conscious decision rather than a side effect.
- Automatic delivery of recordings by email disappears; operators who relied on
  "the zip arrives in my inbox" have to pull or export instead.
- SQLite means existing `menuresponsefile-*.yml` and `mojobol_data.csv` data
  needs a one-time migration, or is left behind in the old format.
- Anyone running the deleted report scripts in production loses them at upgrade;
  the export command has to actually cover those use cases or this is a
  regression.

## Follow-up work (to be filed as issues)
- [ ] T21 — Remove the mail, batch, outbound and reporting subsystems: the files,
      the `[MojoMailer]` config section, `compresscallfile`, the `mojomailman`
      submodule pointer, and the MySQL/PHP/Apache/clone steps in
      `installmojoboldeps.sh`.
- [ ] T22 — SQLite capture store (calls, turns, captured values; WAL mode) with
      `tools/export.py` for CSV/JSONL; retire the per-call YAML response files
      and the global CSV; remove the shared `calllog` symlink from
      `MojoBolCall`.
