# ADR-0005: Simulator-first testing via a MojoPlayer interface

- Status: Accepted
- Date: 2026-07-18
- Deciders: Mojolab (Arjun Venkatraman)
- Related issues: T7, T9 (#8)
- Related ADRs: ADR-0006

## Context
Mojobol currently has no test harness. The only way to exercise a flow is to
place a real call through Asterisk, using `libs/mojoasteriskplayer.py`'s
`MojoAsteriskPlayer` to play prompts and capture DTMF via the AGI channel.
This makes iterating on a flow slow (requires a live PBX, a SIP endpoint, and
a human dialing in) and makes the engine effectively untestable in CI or by a
new contributor without telephony infrastructure. `libs/mojobol.py` already
separates flow/workflow data (`MojoBolWorkflow`, `MojoBolCall`) from the
player that speaks to the channel, so the coupling to Asterisk is mostly
confined to `MojoAsteriskPlayer`.

## Decision
Extract a `MojoPlayer` interface describing the operations the engine needs
from a call player (play a resource, capture digits, capture confirmation,
hang up, etc. — the same surface `MojoAsteriskPlayer` exposes today).
`MojoAsteriskPlayer` becomes one implementation of this interface. We add a
second implementation, a text/stdin-backed player, that:
- prints each prompt resource's text/name as the engine would play it,
- accepts keypresses either scripted (a DTMF string passed on the CLI) or
  typed interactively at a prompt,
- requires no Asterisk process, AGI socket, or SIP channel.

A new CLI (`bin/mojobol-simulate.py`, working name) loads a workflow via
`MojoBolWorkflow`/`MojoBolResponder` exactly as `mojobol-svr.py` does, drives
it with the text player, and prints the traversed step path and any captured
values to stdout. This becomes the primary way flows are developed and
regression-tested going forward; live-telephony hardening (real AGI edge
cases, audio format issues, channel timeouts) is explicitly deferred to a
later sprint and is not blocked on this work.

## Consequences
### Positive
- Flow authors and contributors can validate a workflow in seconds, with no
  PBX, SIP client, or phone call required.
- Scripted keypress sequences are reusable as regression tests and can run in
  CI.
- Forces a clean interface boundary between flow logic and channel I/O, which
  will also make future players (e.g. a web-based tester) cheap to add.

### Negative / Trade-offs
- The interface extraction is a refactor of `mojoasteriskplayer.py` and
  touches call sites in `bin/mojobol-svr.py`; must be done carefully to avoid
  regressing live-call behavior.
- The simulator cannot catch AGI/channel-specific defects (timing, audio
  encoding, SIP signaling) — those still require a real or emulated Asterisk
  call, which remains out of scope for this ADR.
- Some `MojoAsteriskPlayer` methods are currently broken (see ADR-0006,
  `stepCapture`'s `stepresources` bug); the interface must be defined against
  the *intended* behavior, not the current buggy implementation.

## Follow-up work (to be filed as issues)
- [ ] T7 — Define `MojoPlayer` interface and extract it from `MojoAsteriskPlayer`
- [ ] T7 — Implement text/stdin `MojoPlayer` backend (scripted + interactive modes)
- [ ] T7 — Add `bin/mojobol-simulate.py` CLI: load workflow, drive text player, print traversed path and captures
- [ ] T9 — Wire the quickstart smoke test (#8) to run against the simulator, not a live call
