# ADR-0007: Tiered-agent delivery model for the v3.0 revival

- Status: Accepted
- Date: 2026-07-18
- Deciders: Mojolab (Arjun Venkatraman)
- Related issues: None — process ADR.
- Related ADRs: ADR-0005, ADR-0006

## Context
The v3.0 revival spans work of very different character: architectural
decisions (the `MojoPlayer` abstraction, config strategy, ADRs themselves)
that need judgment and cross-cutting awareness of the whole codebase, versus
mechanical, well-specified work (porting Py2 `print` statements to Py3,
replacing hard-coded `/opt/mojobol` paths with `__file__`-relative resolution,
drafting routine documentation) that is well-defined once scoped but doesn't
need a top-tier model to execute correctly. Running all of this work through
a single high-cost model is wasteful; running design-sensitive work through a
low-cost model risks architectural mistakes that are expensive to unwind
later (e.g. an ad hoc `MojoPlayer` interface that doesn't generalize, or a
config scheme inconsistent across scripts).

## Decision
Adopt a tiered-agent delivery process for this revival:
- **Opus (orchestrator tier)**: architecture and design decisions (this ADR
  series and any future ones), the `MojoPlayer` interface design and its
  extraction from `MojoAsteriskPlayer`, the config-loading strategy
  (`MOJOBOL_CONFIG`/`--config`), integration of parallel workstreams, and
  final review/merge of mechanical work before it lands.
- **Sonnet/Haiku (worker tier)**: mechanical, well-specified tasks dispatched
  in parallel once Opus has scoped them precisely — Python 2 to 3 ports of
  individual `bin/` scripts, search-and-replace of hard-coded paths once the
  replacement pattern is fixed, fixing the isolated bugs listed in ADR-0006
  (`os.isfile`, the `stepCapture` dead code) against an exact diff spec, and
  first drafts of documentation (quickstart guide, ADR follow-up text) for
  Opus to edit rather than write from scratch.
- Work assigned to the worker tier must come with a concrete, bounded spec
  (files touched, expected before/after, acceptance check — e.g. "runs under
  `python3 -m py_compile`" or "passes the simulator smoke test") so that
  correctness doesn't depend on the worker tier exercising architectural
  judgment.
- Opus remains responsible for reviewing worker-tier output before it is
  considered done; a worker-tier agent's own report of completion is not
  sufficient sign-off.

## Consequences
### Positive
- Lowers the cost of the bulk, mechanical portion of the revival (T2 ports,
  T3 path fixes) without lowering the quality bar on the decisions that are
  hard to reverse.
- Enables real parallelism: multiple `bin/` script ports (T2) can run
  concurrently as independent worker-tier tasks once the target pattern is
  fixed by the orchestrator.
- Keeps a single point of architectural accountability (Opus) even as
  execution fans out.

### Negative / Trade-offs
- Adds process overhead: every worker-tier task needs an explicit spec and a
  review pass, which is more upfront orchestration work than just doing it
  directly.
- Misclassifying a task (sending something design-sensitive to the worker
  tier) risks subtly wrong output that looks plausible; task classification
  itself requires judgment and is retained at the orchestrator tier.
- Depends on the orchestrator actually reviewing worker output rather than
  rubber-stamping it, which is a discipline requirement, not something this
  ADR can enforce mechanically.

## Follow-up work (to be filed as issues)
None — process ADR.
