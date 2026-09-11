# mojobol — development guidelines

## What this project is

**mojoबोल** is an IVR (interactive voice response) platform that runs telephone
call flows on top of Asterisk. `libs/mojobol.py` reads a server config and a
call flow and walks its steps; `libs/mojoasteriskplayer.py` (`MojoAsteriskPlayer`)
plays prompts and captures DTMF over Asterisk's AGI channel. Prompts are either
pre-recorded audio or synthesized with espeak. `bin/mojobol-svr.py` is the AGI
entrypoint Asterisk invokes when a call arrives.

Call flows today are **Verboice Designer exports** — a `workflow.yml` plus
GUID-named `resource*.yml` and `localized_resource*.yml` files (see
`samplecallflows/mojobolsamplecallflow/`). The step types the engine dispatches
on are `play`, `capture`, `menu`, `record` and `playloop`.

The repo is part-way through a **v3.0 revival**, recorded in
`docs/decisions/`. What has landed: the Python 3 port, the known runtime bug
fixes, config resolution via `--config` / `MOJOBOL_CONFIG`, a pytest suite and
CI (ADR-006). What is *decided but not yet built*: the single-file native
`flow.yml` format (ADR-002), its loader, the Verboice → native importer
(ADR-003), LLM-assisted flow authoring (ADR-004), and the telephony-free
simulator (ADR-005). Read the ADRs before assuming a capability exists.

## Repository layout

```
mojobol/
├── CLAUDE.md                    # This file
├── README.md                    # Overview + Docker and manual install
├── INSTALL.md                   # Manual install instructions
├── INSTALLATION                 # Older plain-text copy of the same
├── Dockerfile, docker-compose.yml
├── installmojoboldeps.sh        # apt/easy_install deps; clones livingdata + mojomailman into /opt
├── setupasterisk.sh             # copies conf/ into /etc/asterisk, links bin/ into agi-bin
├── requirements.txt             # PyYAML, pytz, pytest
├── pytest.ini                   # testpaths = tests
├── bin/                         # entrypoints (run by Asterisk or by cron)
│   ├── mojobol-svr.py           # AGI entrypoint: run a flow for an incoming call
│   ├── mojobol-svr-dev.py       # near-identical dev copy of the above
│   ├── mojobol-svr-out.py       # outbound calling from a CSV (legacy, /opt paths)
│   ├── returncalls.py           # legacy call-back script
│   ├── generatemenureport.py    # legacy menu report
│   └── mojobolmailer.py         # mails call output (needs external MojoMail)
├── libs/
│   ├── mojobol.py               # MojoBolResponder / MojoBolWorkflow / MojoBolCall,
│   │                            #   resolve_config_path(), post-call bookkeeping
│   ├── mojoasteriskplayer.py    # MojoAsteriskPlayer: AGI playback + DTMF capture
│   └── mojobolmailer.py
├── conf/
│   ├── sampleserver.conf        # template server config (the in-repo default)
│   ├── extensions.conf          # sample Asterisk dialplan (callback context)
│   ├── sip.conf                 # sample SIP peers / gateway config
│   └── call.skel                # Asterisk call-file skeleton
├── samplecallflows/             # Verboice export used by the tests
├── tools/
│   ├── file_issues.py           # files docs/issues/*.yml into the GitHub tracker
│   ├── emailmojobolcalls.py     # legacy mail helpers (/opt paths)
│   ├── mojobolmailharness.py
│   └── updatepermissions.sh
├── docs/
│   ├── CONTRIBUTING-workflow.md # the ADR → issue → TODO loop
│   ├── TODO.md                  # GENERATED from GitHub issues — do not hand-edit
│   ├── decisions/               # ADRs — read before changing core approach
│   │   ├── README.md            # index, governance rule, ADR template
│   │   ├── ADR-001-record-architecture-decisions.md
│   │   ├── ADR-002-adopt-single-file-native-flow-format.md
│   │   ├── ADR-003-keep-verboice-as-import-only-compatibility.md
│   │   ├── ADR-004-llm-conversational-flow-authoring.md
│   │   ├── ADR-005-simulator-first-testing.md
│   │   ├── ADR-006-python3-only-and-config-via-env.md
│   │   └── ADR-007-tiered-agent-delivery.md
│   ├── design/native-format-and-guids.md
│   ├── issues/v3.0-sprint-01.yml  # issue bodies, source of record for the tracker
│   └── sprints/                 # sprint-01-essentials.md, sprint-fixes.md
├── tasks/
│   ├── todo.md                  # local work record (see "Work tracking")
│   └── lessons.md               # dated discoveries and gotchas
├── tests/                       # pytest — conftest, test_config, test_engine, test_static
├── images/                      # screenshots used by README
├── logs/                        # checked-in sample log
└── livingdata/, mojomailman/    # bare gitlinks with no .gitmodules (see tasks/todo.md)
```

## Conventions

- **Write an ADR for any non-obvious design or scope decision.** ADRs live in
  `docs/decisions/` as `ADR-NNN-kebab-title.md`; the index, governance rule and
  template are in `docs/decisions/README.md`. Numbers are sequential and
  three-digit zero-padded.
- **Issue-first workflow (ADR-001).** Every actionable item that comes out of an
  ADR goes in that ADR's `## Follow-up work` section and is filed as a GitHub
  issue before it is worked. See `docs/CONTRIBUTING-workflow.md`.
- Track local work in `tasks/todo.md`; record gotchas in `tasks/lessons.md`.
- **Python 3 only (ADR-006).** No Python 2 syntax anywhere.
- **No hardcoded deployment paths in the engine.** Library imports resolve the
  repo root from `__file__`. Config comes from `--config`, else the
  `MOJOBOL_CONFIG` env var, else the in-repo `conf/sampleserver.conf`
  (`mojobol.resolve_config_path`). The legacy outbound/report scripts in `bin/`
  and `tools/` still carry site-specific `/opt` paths — de-hardcoding those is
  explicitly out of scope (`docs/sprints/sprint-fixes.md`).
- **Dependencies stay in `requirements.txt`** (PyYAML, pytz, pytest). pandas was
  deliberately removed (ADR-006) — do not reintroduce it.
- **Match the surrounding style.** The engine files are tab-indented and use
  `from module import *`. Fix what you are changing; do not reformat whole files.
- **Run the tests.** `pip install -r requirements.txt && pytest -q`.
  `tests/test_static.py` is a guard suite: it fails on Python 2 syntax, a bare
  `except:`, the `os.isfile` typo, or a re-introduced hardcoded `/opt` path in
  the engine entrypoints. CI (`.github/workflows/ci.yml`) runs `pytest -q` on
  Python 3.11 for every push and PR.

## Work tracking

Two files, deliberately different in kind:

- **`docs/TODO.md` is machine-generated** from the GitHub issue tracker and
  carries a "do not hand-edit" banner. Its seed source of record is
  `docs/issues/*.yml`, filed with `tools/file_issues.py`. Under ADR-001 nothing
  reaches this list without being an issue first.
- **`tasks/todo.md` is the conventional local record** — hand-maintained,
  cross-linking to the ADRs, sprint docs and `docs/TODO.md` rather than
  duplicating the generated table. It is where shipped work, near-term intent
  and watch items live, including items too small or too local to be issues.

Edit `docs/issues/*.yml` (or the tracker) to change what `docs/TODO.md` will say;
edit `tasks/todo.md` directly.

## Git workflow

- Conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, `test:`.
- A `prepare-commit-msg` hook (in `.git/hooks/`) appends `Coding-Agent:` and
  `Model:` trailers so history records which agent or human produced a commit.
- **Do not change file modes.** This repo has already had one commit strip the
  executable bit off `bin/` scripts and another restore it. Check
  `git diff --summary` for `mode change` lines before committing.
- Do not commit secrets. `conf/sampleserver.conf` ships blank
  `[MojoMailer]` credentials — keep real ones out of the repo.
