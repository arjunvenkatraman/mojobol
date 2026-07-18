# Design memo: GUID-free native format, prompt reuse, and multi-language

- Status: Proposal (feeds T4/T6, and edits to ADR-0002/ADR-0003)
- Author: Mojolab (design pass on v3.0 native format)
- Related: ADR-0002, ADR-0003, `docs/issues/v3.0-sprint-01.yml` (T4, T6)

## 1. Do we need GUIDs anywhere in v3?

**No.** Not in the flow file, not in the engine's in-memory model, and not
exposed to the LLM at any point.

GUIDs in Verboice exist to solve one problem: three separate files
(`workflow.yml`, `resource*.yml`, `localized_resource*.yml`) need a
join key because they're physically separate. That's a consequence of
Verboice's Designer serializing an object graph to disk, not a requirement
of the problem itself ("play this prompt, in this language, possibly from
several places"). In a single `flow.yml`, the join key can just be a
readable string — a step id or a prompt name — because everything lives in
one YAML document and YAML anchors/keys already give us referencing for
free. There is nothing a GUID buys us here that a human-chosen name
doesn't buy more cheaply (readability, diffability, grep-ability, and zero
chance of an LLM emitting a plausible-looking-but-wrong 36-char token).

The two real capabilities GUIDs happened to provide — **prompt reuse**
(§2.3) and **multi-language** (§2.2) — are addressed below with named,
readable keys instead. `import_verboice.py` (§4) is the one place a GUID
is ever read, and it never leaves that tool.

## 2. Recommended format

### 2.0 Full worked example

```yaml
name: health-survey
languages: [en, hi]
default_language: en

prompts:
  welcome:
    say:
      en: "Welcome to the health survey. Press 1 to continue."
      hi: "स्वास्थ्य सर्वेक्षण में आपका स्वागत है। जारी रखने के लिए 1 दबाएं।"
  invalid_input:
    say:
      en: "Sorry, that wasn't a valid choice."
      hi: "क्षमा करें, यह मान्य विकल्प नहीं था।"
  ask_menu:
    audio:
      en: prompts/ask_menu-en.wav
      hi: prompts/ask_menu-hi.wav
  goodbye:
    say: "Thanks for calling. Goodbye."   # single-language shortcut, see 2.1

steps:
  - id: welcome
    type: play
    prompt: welcome
    next: menu

  - id: menu
    type: menu
    prompt: ask_menu
    invalid_prompt: invalid_input
    timeout: 5
    attempts: 3
    options:
      "1": record_feedback
      "2": goodbye

  - id: record_feedback
    type: record
    say: "Please leave your feedback after the beep."
    stop_key: "1"
    max_seconds: 30
    store: feedback_audio
    next: goodbye

  - id: goodbye
    type: play
    prompt: goodbye
```

Two prompt-referencing styles appear side by side on purpose: `record_feedback`
uses inline `say:` (the common case — a one-off prompt used once), while
`welcome`, `menu`, and `goodbye` use `prompt: <name>` to pull from the
`prompts:` table (reused and/or multi-language content). Both are legal on
any step that plays or reads a prompt (`play`, `menu`'s `prompt`/
`invalid_prompt`, `capture`'s instruction text, `record`'s explanation
text); the engine treats "inline `say`/`audio`" and "`prompt: name`
looked up in the table" as two ways of arriving at the same resolved
value (§3).

### 2.1 Inline `say:` for the simple/common case

Most steps in a real flow play a prompt exactly once, in one language.
For that case, `say: "<text>"` directly on the step (as ADR-0002 already
specifies) stays the recommended default — no indirection, no table entry,
the wording sits right next to the step that speaks it. This is the
95% case and should stay the path of least resistance for both a human
and an LLM drafting a flow turn-by-turn.

### 2.2 Multi-language: recommendation

Three options were considered:

| Option | Sketch | Verdict |
|---|---|---|
| **A. `say:` as a `{lang: text}` map** inline per step | `say: {en: "Hi", hi: "नमस्ते"}` | Good for one-off prompts in >1 language; doesn't solve reuse |
| **B. Top-level `prompts:` table**, keyed by readable name, holding per-language `say`/`audio`; steps reference via `prompt: <name>` | shown in §2.0 | **Recommended** |
| **C. One flow file per language** (`flow.en.yml`, `flow.hi.yml`) | fully duplicated flows | Rejected |

**Recommendation: B, a top-level `prompts:` table with `prompt: <name>`
references — but allow inline `say:` (option A's shape) to *also* accept a
language map when a prompt is genuinely one-off but still needs several
languages.** Concretely:

- `say: "text"` → single-language shortcut (uses `default_language` or the
  flow's sole `languages` entry).
- `say: {en: "...", hi: "..."}` inline → multi-language, one-off, not reused.
- `prompts:` + `prompt: <name>` → multi-language *and/or* reused (the two
  problems the GUID scheme solved are both instances of "give the prompt a
  name and point at it from more than one place").

Why B over C (one file per language): a per-language flow file duplicates
the entire step graph — every `next` pointer, every menu option, every
`store` key — for content that differs only in wording. Two divergent
`next` graphs are exactly the class of bug GUID cross-referencing already
caused (structural drift between copies that are supposed to stay in
sync). It also doubles the LLM's authoring surface for zero structural
benefit: the conversation that produces the flow already knows all target
languages at once. Per-language files are appropriate output artifacts for
Asterisk deployment (files on disk per locale) but wrong as the *authoring*
representation.

Why B over pure A (always inline maps): once a prompt is reused (§2.3) an
inline map has nowhere to live without repeating itself at every use site.
A `prompts:` table gives reuse and multi-language the same mechanism, so
authors (human or LLM) only learn one indirection concept, not two.

### 2.3 Prompt reuse: recommendation

**Support a named `prompts:` table; do not rely on copy-paste
duplication for reused prompts.** Flows are small (the sample flow has
6 steps, 9 resources), so duplicating a two-line `say:` string is
harmless in isolation — but "harmless duplication" is exactly the
mismatch risk ADR-0002 is trying to retire: two copies of the same
"invalid input" prompt inevitably drift once someone edits one and not
the other. A `prompts:` table with a readable key (`invalid_input`,
`ask_menu`) costs nothing to add and removes the drift risk entirely.
Recommendation in one line: **inline `say:` when a prompt is used once;
`prompts:` + `prompt: name` as soon as a prompt is used more than once or
needs more than one language** — and an LLM authoring a flow should default
to the table the moment it notices it's about to write the same wording
twice (e.g., a shared "that wasn't valid, try again" line across a `capture`
and a `menu`).

### 2.4 Recorded audio alongside/instead of TTS text

Same table, same step-level fields, just a different key — `audio:` in
place of `say:`, both inline and inside `prompts:`:

```yaml
prompts:
  ask_menu:
    audio:
      en: prompts/ask_menu-en.wav
      hi: prompts/ask_menu-hi.wav

steps:
  - id: outro
    type: play
    audio: prompts/outro.wav     # inline, single-language, one-off
    next: null
```

A prompt entry may carry `say`, `audio`, or both per language (mirroring
Verboice's `TextLocalizedResource` vs. `ExternalAudio`/`recorded_audio`
distinction); if both are present, `audio` wins for that language (a
human-recorded file is assumed better than TTS when someone bothered to
record one). Paths are relative to the flow file's directory, same as
Verboice's `recorded_audio` today.

## 3. Engine impact

`executeStep`'s dispatch (`if step['type']=='play' / 'capture' / 'menu' /
'record' / 'playloop'`) does not change at all — it's the resource
resolution feeding `getAudioFile` that changes. The GUID hop
(`step['resource']['guid']` → `getStepResourceByGuid` →
`MojoBolWorkflowResource` → `getLocalizedResources(language=...)` → pick
`.rtype`) collapses into one lookup against the flow's own `prompts:`
table plus the step's own inline fields.

Sketch of `load_flow(path)` (new loader for T5, alongside the existing
`MojoBolWorkflow`):

```python
def load_flow(path):
    with open(path) as f:
        flow = yaml.safe_load(f)
    prompts = flow.get("prompts", {})
    default_lang = flow.get("default_language", flow.get("languages", ["en"])[0])

    def resolve_prompt(step, key="prompt", say_key="say", audio_key="audio"):
        """Return {'kind': 'audio'|'say', 'value': str} for the *current*
        runtime language, given a step that has either `prompt: name`,
        inline `say:`, or inline `audio:` under the given field names."""
        if key in step:
            entry = prompts[step[key]]
        else:
            entry = step  # inline say/audio live directly on the step
        for kind, field in (("audio", audio_key), ("say", say_key)):
            if field in entry:
                val = entry[field]
                if isinstance(val, dict):     # {lang: text/path}
                    val = val.get(current_language, val.get(default_lang))
                return {"kind": kind, "value": val}
        raise ValueError(f"step has no {say_key}/{audio_key}/{key}")
```

This returns a `(kind, value)` pair — `("say", "Welcome...")` or
`("audio", "prompts/welcome-en.wav")` — which is exactly the two branches
`getAudioFile` already has (`rtype == 'ExternalAudio'` → play the file
path directly; `rtype == 'TextLocalizedResource'` → espeak→sox). A thin
`getAudioFile` rewrite takes this pair directly instead of a
`MojoBolWorkflowResource`/`getLocalizedResources()` object, but keeps the
same two code paths (file path vs. espeak/sox synth) verbatim. `next`
pointers, `options` maps, `min_length`/`max_length`/`store`/`stop_key`/
`max_seconds`/`attempts` all read straight off the step dict exactly as
they do today — only the four resource-lookup call sites in `executeStep`
(`play`, `capture`'s instructions/invalid, `menu`'s
explanation/options/invalid, `record`'s explanation/confirmation) swap
their GUID resolution for a call to `resolve_prompt`. `MojoBolWorkflow`'s
`getStepByID`/root-step/`while next` loop in `MojoBolResponder.parse_workflow`
is unaffected — `load_flow` just needs to produce a `.steps` list and a
`getStepByID` lookup with the same shape.

## 4. Verboice importer: keep as Sprint-1 essential, but only as a tool concern

Recommendation: **keep `tools/import_verboice.py` in Sprint 1 (T6 stays
essential, not deferred)**, for one concrete reason independent of whether
Verboice-the-GUI is still used: the only existing flow content mojobol has
— including `samplecallflows/mojobolsamplecallflow/` used for T7's
simulator and T9's smoke test — is in Verboice's format. Without the
importer, Sprint 1 has no real flow to exercise the new loader (T5) or the
simulator (T7) against; the "example flow" ADR-0002/T4 promise would have
to be hand-authored from scratch instead of migrated, which is more work,
not less, for exactly the flow everyone already has on disk.

What changes is *why* it's essential: not "because Verboice is a live
authoring path" (ADR-0003 already forecloses that) but "because it's the
one-time bulk-conversion path for content that predates v3.0, needed to
seed the very first native example/test flow." That framing should be
made explicit in ADR-0003 (see §5) so nobody reads "importer stays" as
"Verboice GUI stays relevant."

The GUID→readable-id mapping the importer performs (turning `resource
0a69cfd7-....yml`'s `name: DemoPlayAMessage` plus its
`localized_resource ...-en-....yml` siblings into `prompts: { message: {
say: { en: "A message" } } }`) is a **pure tool concern**: the importer
reads GUIDs, resolves them, and picks/derives a readable key (from the
Verboice resource's own `name:` field, slugified, with numeric suffixing
on collision — e.g. two resources both named "Message" become `message`
and `message_2`). The LLM is never involved in this step and never sees a
GUID; it only ever sees the importer's output `flow.yml`, indistinguishable
from one it would have authored itself. Concretely the importer should:
group Verboice steps by their `resource`/`instructions_resource`/
`invalid_resource`/`explanation_resource`/`options_resource`/
`confirmation_resource` GUIDs, deduplicate resources that are referenced
from more than one step into a single `prompts:` entry (this is where
Verboice's incidental reuse, if any, becomes explicit reuse in the new
format), and fold each resource's `localized_resource` files into that
entry's per-language `say`/`audio` map, keyed by each localized resource's
`language:` field.

## 5. Concrete change list (for the orchestrator to apply)

**ADR-0002** (`docs/adr/0002-adopt-single-file-native-flow-format.md`):
- In "Decision," replace the current single-sentence prompt-content bullet
  with the two-tier model: inline `say:`/`audio:` (per-step, optionally a
  `{lang: ...}` map) for one-off prompts, plus an optional top-level
  `prompts:` table + per-step `prompt: <name>` for reused and/or
  multi-language prompts. Add `languages:`/`default_language:` as
  flow-level fields.
- In "Consequences → Negative," replace the "multi-language flows need a
  documented convention (tracked under T4)" bullet with a pointer to this
  memo's resolution (§2.2) rather than leaving it open.
- Update the "Follow-up work" T4 line to reference this memo as the format
  spec's multi-language/reuse basis.

**ADR-0003** (`docs/adr/0003-keep-verboice-as-import-only-compatibility.md`):
- In "Consequences → Negative," replace the open-ended "multi-language
  Verboice exports need to be reconciled with however ADR-0002 ends up
  handling multi-language natively (tracked under T4)" bullet with the
  concrete mapping from §4: each Verboice `resource` (deduplicated across
  steps that share a GUID) becomes one `prompts:` entry; each of its
  `localized_resource` siblings becomes one language key in that entry's
  `say`/`audio` map.
- Add a sentence to "Decision" making explicit that GUID→readable-name
  resolution (via the Verboice resource's `name:` field, slugified) is
  internal to `import_verboice.py` and never surfaces to the LLM authoring
  path (ADR-0004) — this forecloses any reading of T6 as reviving Verboice
  as a live/ongoing format.
- Reframe why the importer is Sprint-1-essential (see §4): it's needed to
  produce the first real native example/test flow (T4's worked example,
  T7's simulator fixture, T9's smoke test) from existing content, not
  because Verboice authoring continues.

**`docs/issues/v3.0-sprint-01.yml`:**
- **T4** body: add explicit acceptance sub-bullets for multi-language and
  reuse: "the example flow includes at least one `prompts:` entry used
  from two steps, and at least one prompt with two languages, both
  validating against the schema." Add a schema note: `schemas/flow.schema.json`
  needs a `prompts` object type (map of prompt-name → `{say, audio}`, each
  of which is either a string or a map of language → string) distinct from
  but structurally identical to the inline per-step `say`/`audio` fields.
- **T6**: keep as-is in Sprint 1 (do not move to "optional/later" — see
  §4 rationale). Add a sub-bullet: "resources referenced by more than one
  Verboice step are deduplicated into a single `prompts:` entry rather than
  duplicated per step" and "prompt names are derived from each Verboice
  resource's `name:` field (slugified, de-duplicated on collision), never
  from its `guid:`." Update the `adr:` field's implicit scope note (via
  ADR-0003 edit above) so the issue reads as "seed data for T4/T7/T9," not
  as ongoing Verboice support.

## Summary

No GUIDs anywhere in v3 — not in the flow file, not in the engine, not in
front of the LLM. Reuse and multi-language are both solved by the same
mechanism: an optional top-level `prompts:` table keyed by a readable name,
referenced from steps via `prompt: <name>`, sitting alongside (not
replacing) inline `say:`/`audio:` for the common one-off case. Multi-language
is a `{lang: text}` map on `say`/`audio`, not a map of flow files —
one flow, several languages, one step graph. The Verboice importer (T6)
stays a Sprint-1 essential, but purely as a one-time seed/migration tool
for the one real flow the repo has; its GUID handling is entirely internal
tooling the LLM never touches.
