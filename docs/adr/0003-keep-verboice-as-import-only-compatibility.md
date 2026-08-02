# ADR-0003: Keep Verboice as import-only compatibility

- Status: Accepted
- Date: 2026-07-18
- Deciders: Mojolab (Arjun Venkatraman)
- Related issues: #7, T6
- Related ADRs: ADR-0002

## Context
ADR-0002 adopts a single-file native `flow.yml` format and stops using the
InSTEDD Verboice Designer for authoring new flows. That leaves a body of
existing flows — `workflow.yml` plus GUID-named `resource*.yml` and
`localized_resource*.yml` files, such as the ones under
`samplecallflows/mojobolsamplecallflow/` — that were built in Verboice and
are still in use or worth preserving. We do not want to hand-convert these,
and we do not want to keep Verboice as a live authoring path for new work,
since that would leave two divergent formats to support indefinitely and
undercut the reason for adopting the native format in the first place.
GitHub issue #7 already tracks the need for a Verboice-to-native conversion
path for this reason.

## Decision
Verboice support is retained strictly as a one-way, one-time import path,
not as an ongoing authoring format:
- `tools/import_verboice.py` will read a legacy Verboice Designer `.zip`
  export (the `workflow.yml` + `resource*.yml` + `localized_resource*.yml`
  bundle) and emit an equivalent native `flow.yml` (per ADR-0002), resolving
  every GUID cross-reference into inline `say:`/`audio:` content on the
  corresponding step.
- No new mojobol tooling will read Verboice's multi-file format directly at
  call time; once imported, a flow is native and is maintained as native
  going forward.
- The Verboice Designer GUI itself is not part of the v3.0 authoring
  workflow (see ADR-0004) — it is only a source format the importer
  understands.
- This importer is the resolution for GitHub issue #7.

## Consequences
### Positive
- Existing Verboice flows are not lost or stranded; they get a clear,
  scripted upgrade path to the native format instead of manual rewriting.
- The engine and docs only need to support one live format (native); Verboice
  parsing logic is isolated to a single conversion tool, not spread through
  `libs/mojobol.py` / `libs/mojoasteriskplayer.py`.
- Closes out issue #7 with a concrete deliverable.

### Negative / Trade-offs
- The importer must handle every Verboice step type and quirk the old
  engine supported (`play`, `capture`, `menu`, `record`, `playloop`, and
  their GUID-based resource/localized-resource resolution), which is
  nontrivial reverse-engineering of an undocumented export format.
- Converted flows will need a manual review pass — the importer produces a
  structurally valid `flow.yml`, but inlined `say:` text pulled from
  `localized_resource*.yml` files may need cleanup, and multi-language
  Verboice exports need to be reconciled with however ADR-0002 ends up
  handling multi-language natively (tracked under T4).
- Once a flow is imported, its native and Verboice versions can drift; there
  is no round-trip or sync back to Verboice, so import is a one-way door.

## Follow-up work (to be filed as issues)
- [ ] T6 — Build `tools/import_verboice.py`: parse a Verboice `.zip` export
      (workflow + resource + localized_resource files), resolve GUID
      cross-references, and emit a native `flow.yml` per ADR-0002 (resolves
      #7).
