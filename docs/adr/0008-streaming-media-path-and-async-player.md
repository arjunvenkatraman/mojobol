# ADR-0008: Streaming media path via AudioSocket, and an async MojoPlayer

- Status: Proposed
- Date: 2026-07-29
- Deciders: Mojolab (Arjun Venkatraman) — pending sign-off
- Related issues: T10, T11, T12 (amends #8)
- Related ADRs: ADR-0005 (amended by this ADR), ADR-0009, ADR-0010

## Context
Mojobol talks to Asterisk over AGI. `libs/mojoasteriskplayer.py` writes AGI
commands to stdout and blocks on `readline()`: `STREAM FILE` to play a prompt,
`GET DATA` to collect DTMF, `RECORD FILE` to capture audio. `libs/mojobol.py`'s
`parse_workflow` walks the flow one step at a time, with a `time.sleep(1)`
between every step.

**AGI is a turn-based control channel, not a media path.** This is the load-bearing
constraint for everything below:

- `STREAM FILE` plays a file to completion. It can be interrupted only by a
  DTMF escape digit, never by the caller speaking.
- `RECORD FILE` records to completion and *then* returns, so audio is only
  available as a finished file — there is no incremental access to it.
- There is no bidirectional audio stream at all.

Consequently, streaming ASR is impossible (no audio arrives until the caller
stops talking) and barge-in is impossible (nothing can interrupt playback but a
keypress). Barge-in is not a nice-to-have: without it, a caller must listen to
every prompt to its end, which is the single biggest reason IVR feels dead
rather than conversational.

This ADR is also time-sensitive with respect to **ADR-0005**. That ADR extracts a
`MojoPlayer` interface, and scopes it as *"play a resource, capture digits,
capture confirmation, hang up"* — the surface `MojoAsteriskPlayer` exposes today.
That shape is blocking and DTMF-only, and a streaming voice player **cannot
implement it**:

- a blocking `play()` has no way to be interrupted, so barge-in has nowhere to live;
- `capture_digits() -> str` has nowhere to put a partial transcript, a
  confidence score, or timing;
- nothing in the interface can express *"the caller started speaking while we
  were still talking"*, which is the central event in a live conversation.

ADR-0005 anticipates that a clean boundary makes "future players cheap to add".
That only holds if the boundary is not itself shaped by AGI's blocking
semantics. T7/#8 is in the current sprint, so this is the cheapest moment to fix
it — and it gets more expensive every week that downstream work builds on the
blocking shape.

## Decision

**1. Asterisk is demoted to a SIP/PSTN gateway.** It answers the call and hands
the media to mojobol. No flow logic, no prompt playback, no digit collection in
the dialplan. All existing gateway configuration (SIP trunk, GSM ATA) stays
valid and useful; only the AGI hand-off changes.

**2. Media travels over AudioSocket.** Asterisk's AudioSocket carries a
bidirectional audio stream to mojobol over TCP as `type(1) + length(2, BE) +
payload` frames — with distinct frame types for audio (signed linear 16-bit,
8 kHz mono), DTMF, hangup/terminate, and the channel UUID. DTMF arriving as its
own frame type on the same connection is what lets ADR-0009's dual-mode input
work over a single transport. (Exact type constants must be verified against the
Asterisk version in use.)

*Alternative considered:* ARI + External Media, which carries audio over RTP/UDP.
UDP avoids TCP head-of-line blocking, but it costs a WebSocket control channel
plus a separately-managed RTP stream and a much larger Asterisk surface area.
For a single-box edge deployment where Asterisk and mojobol share a host (so the
TCP hop is loopback), AudioSocket's simplicity wins. Revisit if we ever split
the media plane onto a different machine.

**3. `MojoPlayer` is defined as asynchronous and cancellable**, against the
*intended* behaviour rather than today's AGI behaviour:

```python
class MojoPlayer(Protocol):
    async def say(self, prompt: Prompt, *, barge_in: bool) -> SayResult: ...
    async def listen(self, spec: InputSpec) -> InputEvent: ...
    async def record(self, spec: RecordSpec) -> RecordResult: ...
    async def hangup(self) -> None: ...
```

- `say()` is cancellable. When `barge_in=True` and the caller starts speaking,
  the pending playback is cancelled and `SayResult` reports that it was
  interrupted and where.
- `listen()` returns a tagged `InputEvent` — a DTMF press, a recognised
  utterance (with transcript, confidence, timing), or a timeout — rather than a
  bare digit string. ADR-0009 defines how a single `listen()` accepts both.
- Nothing in the interface assumes a file on disk, an AGI channel, or a
  keypad.

**4. Three implementations of that one interface**, so the simulator and the live
path never diverge:

| Implementation | Purpose |
|---|---|
| `AudioSocketPlayer` | live calls (this ADR) |
| `TextPlayer` | ADR-0005's simulator: prompts to stdout, scripted/typed input |
| `AudioFilePlayer` | feed recorded audio in, capture audio out — ASR/TTS regression in CI, no PBX |

The text player implements the async interface just as easily as a blocking one,
so ADR-0005's deliverable does not get harder — only differently shaped.

**5. The legacy AGI player is retained during transition**, selected by the
existing `playertype` config key (`playertype = agi` vs `audiosocket`), and
wired to a *separate* dialplan extension. This is what allows the new engine to
be A/B'd against the old one on real traffic before the old one is removed.

**6. The `time.sleep(1)` in `parse_workflow` goes.** A full second of dead air
between every step is incompatible with the latency budget in ADR-0010.

## Consequences
### Positive
- Barge-in and streaming ASR become *possible* — neither can be built on AGI at
  any level of effort, so this is the unlock, not an optimisation.
- One interface serves the simulator, CI regression, and live telephony, so
  flows are developed without a PBX and still exercise the real dialog code.
- The latency budget in ADR-0010 becomes achievable, because every stage can
  overlap instead of running to completion in sequence.
- Defining the interface once, now, avoids extracting `MojoPlayer` twice.

### Negative / Trade-offs
- The call driver becomes asyncio. This is a genuine rewrite of the loop in
  `parse_workflow` and of `mojoasteriskplayer.py`'s I/O, not a refactor.
- AudioSocket is TCP: a stall shows up as latency rather than as loss, so the
  agent needs its own jitter/pacing discipline on the playout side.
- Requires AudioSocket support in the deployed Asterisk (`res_audiosocket` /
  `chan_audiosocket`), which is a deployment prerequisite the current apt-based
  Dockerfile does not verify.
- Concurrency stops being free: models must be shared across calls behind a
  bounded pool (ADR-0010), and the per-call global `calllog` symlink in
  `MojoBolCall` — removed then recreated on every call — actively breaks with
  more than one call in flight (ADR-0012).
- Running two players during transition means two live code paths to keep
  working, with the associated risk that the legacy one quietly rots.

## Follow-up work (to be filed as issues)
- [ ] T10 — Define the async, cancellable `MojoPlayer` interface (`say`/`listen`/
      `record`/`hangup`, `InputEvent` union, `SayResult` with interruption
      position). **Amends #8** — the interface must land in this shape, not the
      blocking DTMF shape ADR-0005 originally described.
- [ ] T11 — Implement `AudioSocketPlayer` and the asyncio per-call driver:
      frame codec, 8k↔16k resampling, playout pacing, cancellable playback,
      DTMF frames; remove the `time.sleep(1)` from `parse_workflow`.
- [ ] T12 — Minimal PJSIP config + dialplan that answers and hands the channel
      to AudioSocket; replace the 74 KB deprecated `chan_sip` `conf/sip.conf`;
      expose SIP 5060/UDP and the RTP range in the container (see #9).
