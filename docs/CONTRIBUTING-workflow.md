# Contributor workflow: ADRs → issues → TODOs

Mojobol keeps a strict, mechanical loop so that decisions turn into tracked work
and nothing actionable lives only in chat or memory (ADR-0001).

```
 significant decision ─▶ ADR in docs/adr/ ─▶ "Follow-up work" items
                                                   │
                                                   ▼
                                          GitHub issues (the tracker)
                                                   │
                                                   ▼
                                    docs/TODO.md  (a projection of issues)
```

## The rules

1. **Significant decisions get an ADR.** Copy the template from
   `docs/adr/README.md`, number it, and end it with a
   `## Follow-up work (to be filed as issues)` section.
2. **Every ADR follow-up becomes a GitHub issue.** No follow-up item is worked
   until it exists as an issue. If you have `issues:write`, file it directly;
   otherwise add it to `docs/issues/*.yml` and run `tools/file_issues.py` later.
3. **TODOs come only from issues.** `docs/TODO.md` is never hand-authored as a
   wishlist — it reflects open issues. If you want to do something, file the
   issue first.

## Why the current TODO is "provisional"

The account used to bootstrap the v3.0 revival has read-only GitHub access, so
the first wave of issues could not be created programmatically. They are checked
in at `docs/issues/v3.0-sprint-01.yml`. When a token with `issues:write` is
available:

```bash
GITHUB_TOKEN=... python3 tools/file_issues.py docs/issues/v3.0-sprint-01.yml
```

Then regenerate `docs/TODO.md` from the live tracker and drop the "provisional"
note.
