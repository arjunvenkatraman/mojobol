# ADR-0004: LLM conversational flow authoring

- Status: Accepted
- Date: 2026-07-18
- Deciders: Mojolab (Arjun Venkatraman)
- Related issues: T8
- Related ADRs: ADR-0002, ADR-0003

## Context
Historically, the only way to author a mojobol call flow was the Verboice
Designer GUI, which produced the GUID-heavy multi-file export described in
ADR-0002. ADR-0002 replaces that export with a single human-readable
`flow.yml`, and ADR-0003 confines Verboice to a one-time import path — but
neither ADR says how new flows should actually be authored going forward.
Without the Designer GUI, and without asking flow authors to hand-write YAML
against a schema from scratch, we need a concrete authoring workflow that is
at least as approachable as the GUI was, ideally more so, since flow authors
(e.g. survey designers) are frequently not developers.

## Decision
New flows are authored by describing the desired IVR in natural-language
conversation with a capable LLM, which emits a valid native `flow.yml`
(per ADR-0002) directly — the LLM replaces the Verboice Designer GUI as the
authoring surface. Concretely:
- We will ship a reusable system prompt that teaches an LLM the native flow
  schema (step types `play`/`capture`/`menu`/`record`/`playloop`, the
  `say:`/`audio:` prompt fields, `next`/`options` control flow, and the
  per-type fields such as `min_length`, `finish_on_key`, `valid_values`,
  `store`, `stop_key`, `max_seconds`) plus a short authoring guide and a set
  of worked example conversations/flows (e.g. a health-survey flow like the
  one in ADR-0002).
- A flow author converses with the LLM about the call they want (menu
  options, prompts, data to capture); the LLM asks clarifying questions as
  needed and produces `flow.yml` as its output.
- The emitted `flow.yml` is not trusted blindly: it is validated against the
  native flow schema (T4) and simulated/dry-run before being deployed to
  Asterisk, so authoring errors are caught before a live call flow breaks.
- The system prompt, guide, and examples are treated as versioned
  documentation/config, not a one-off — they get updated as the native
  format (ADR-0002) evolves.

## Consequences
### Positive
- Removes the Verboice Designer GUI as a dependency for new flow authoring,
  completing the transition started in ADR-0002/ADR-0003.
- Non-developer flow authors can describe intent conversationally instead of
  learning a GUI or hand-writing YAML.
- Because the LLM emits the same native format a human could hand-edit
  (ADR-0002), authors can always drop into the YAML directly for touch-ups
  the conversation doesn't cover.
- Validation + simulation before deployment catches malformed or
  inconsistent flows (bad `next` references, unreachable steps, missing
  `store` targets) before they reach a live caller.

### Negative / Trade-offs
- Output quality depends on the system prompt and examples staying in sync
  with the native schema; drift between them will produce invalid or
  subtly wrong flows.
- LLM-generated flows still need a human review step for tone, correctness
  of survey logic, and language/localization choices — this is not a
  fully unattended authoring pipeline.
- Validation and simulation tooling referenced here (schema validation from
  T4, plus a dry-run/simulator) do not exist yet and are a prerequisite for
  trusting LLM output in production.

## Follow-up work (to be filed as issues)
- [ ] T8 — Write the LLM conversational flow-authoring guide: reusable
      system prompt teaching the native flow schema, a short human-facing
      authoring guide, and worked example conversations/flows.
