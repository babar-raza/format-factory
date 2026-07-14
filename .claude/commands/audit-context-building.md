---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same target module/system + same 3-phase methodology produce the same context artifact (module map, per-function analyses, trust boundary map); the numeric thresholds (>=3 invariants/function, >=5 assumptions/function, >=3 risk considerations per external interaction) are fixed minimums, not randomized"
loc_budget: "0 lines of executable code (prompt-driven checklist only; no bundled script)"
test_path: "N/A (prompt-spec skill, no executable code) — verification is the manual scan proof recorded under TC-EXT-025-05"
external_skill_origin: true
external_skill_source: trailofbits/skills
external_skill_commit: cfe5d7b1619e47fb5b38b7e2561dad7e5f1e89af
external_skill_license: CC-BY-SA-4.0
risk_level: LOW
created-by: TC-EXT-025-02
product_track: governance
---

# /audit-context-building

Pure context-building reviewer — explicitly does **NOT** identify
vulnerabilities, propose fixes, generate proof-of-concept exploits, or assign
severity ratings (a non-goal preserved verbatim from upstream). Builds a
structured, citation-backed understanding of a target module or system —
entrypoints, actors, storage, invariants, trust boundaries — for a separate
vulnerability-hunting skill (`sharp-edges`, `agent-owasp-compliance`) or a
human reviewer to reason about afterward. Tools: Read, Grep, Glob (+
Bash/Task only at a command-invocation layer, per upstream — never used by
this skill to mutate anything).

## Attribution

<!--
This skill's methodology (Phase 1 Initial Orientation, Phase 2
Ultra-Granular Function Analysis with its Purpose/Inputs & Assumptions/
Outputs & Effects/Block-by-Block structure and the Cross-Function & External
Flow Analysis Case A/Case B split, Phase 3 Global System Understanding, the
numeric thresholds [minimum 3 invariants/function, minimum 5
assumptions/function, minimum 3 risk considerations per external
interaction], and the anti-hallucination citation rules) is adapted from the
`audit-context-building` skill in `trailofbits/skills`, commit
`cfe5d7b1619e47fb5b38b7e2561dad7e5f1e89af`. Author, per the upstream skill's
own conventions: Trail of Bits. Licensed CC-BY-SA-4.0
(https://creativecommons.org/licenses/by-sa/4.0/).

CC-BY-SA-4.0 share-alike notice: this file is itself a derivative work of
the cited upstream skill's documented methodology (prose adaptation only —
no upstream code, script, or asset is vendored or executed). Per the
license's ShareAlike term, this derivative file
(`.claude/commands/audit-context-building.md`) is distributed under the same
CC-BY-SA-4.0 terms as the original. Any further redistribution of this
specific file must preserve this attribution notice and the CC-BY-SA-4.0
license grant. This share-alike obligation applies only to this file's
adapted methodology text — it does not relicense any other file in this
repository, all of which remain under this repository's own license terms.
-->

This skill adapts the 3-phase methodology, the numeric thresholds, and the
anti-hallucination citation rules from Trail of Bits' `audit-context-building`
skill (`trailofbits/skills`, CC-BY-SA-4.0), commit
`cfe5d7b1619e47fb5b38b7e2561dad7e5f1e89af`. The phase names, the Case A/Case
B external-flow split, and the threshold minimums are carried over
near-verbatim from the upstream skill; the FF-specific primary-target scope
(`tools/supervisor/` + `tools/governance/`, below) is original to this
repository. Cleared by `/skill-scanner` per TC-EXT-012's mandatory gating
rule.

## Purpose

FF's own Gate 8 threat-model process (`docs/governance/security.md`)
explicitly scopes itself, in its own `## Scope` section, to:
`prototypes/by-format/`, `src/python/{format}/` (Python FOSS product),
`src/net/{format}/` (.NET product and commercial-tier), and
`tools/validation/`. It does not name `tools/supervisor/` or
`tools/governance/` anywhere in that scope — the high-privilege
autonomous-execution codebase that runs the entire supervisor loop, writes
every governance registry, and can commit/push on the repository's behalf is
outside Gate 8's stated coverage entirely. This skill's primary target is
explicitly `tools/supervisor/` and `tools/governance/` — **not** the
already-covered `src/python/{format}/` parsers, which remain Gate 8's job.

## Non-Goal (verbatim from upstream)

This skill does **NOT**: identify vulnerabilities, propose fixes, generate
proof-of-concept exploits, or assign severity ratings. Its only output is a
structured factual map of what the target code does — for a separate
vulnerability-hunting skill (or a human) to reason about afterward.

## When to Use

- Before applying `sharp-edges` or `agent-owasp-compliance` against
  `tools/supervisor/` or `tools/governance/` — this skill builds the factual
  context those reviewers reason over, rather than each reviewer
  re-deriving module structure from scratch.
- Whenever a change to `tools/supervisor/` or `tools/governance/` needs a
  ground-truth map of entrypoints, actors, and trust boundaries before any
  security or correctness judgment is made about it.
- On request, as a standalone context-building pass over any target module.

## The 3 Phases

### Phase 1 — Initial Orientation

Map the target's modules, entrypoints, actors, and storage **"without
assuming behavior"** — derive structure from what the code actually imports,
exposes, and calls, never from filenames or naming conventions alone (a
function named `validate_input` is not assumed to validate correctly, or at
all, until its body is read).

### Phase 2 — Ultra-Granular Function Analysis

Per function, in this order:

1. **Purpose** — what the function is for, derived from its body.
2. **Inputs & Assumptions** — every parameter, its expected shape, and every
   assumption the function's body makes about it (minimum **5 assumptions
   per function**).
3. **Outputs & Effects** — return value(s) and every side effect (file
   writes, registry mutations, subprocess/network calls).
4. **Block-by-Block** — a walkthrough of the function body in order,
   citing line numbers for every claim.

**Cross-Function & External Flow Analysis** — for every call the function
makes:

- **Case A — "internal, jump in."** The callee is in-repo code under the
  same trust boundary: trace its own body with the same rigor as the caller.
- **Case B — "true external/black box, treat as adversarial."** The callee
  crosses into a third-party package, a subprocess, or a network call: do
  not assume its internals; treat its output as untrusted, and document at
  least **3 risk considerations** for that external interaction.

**Numeric thresholds (minimums, not caps):** at least 3 invariants
documented per function; at least 5 assumptions documented per function; at
least 3 risk considerations documented for every external interaction.

### Phase 3 — Global System Understanding

Reconstruct state and invariants across the whole target, and map its trust
boundaries — where data crosses from a lower-trust actor (an external
package, a subprocess, an unauthenticated caller) to a higher-trust one (the
supervisor loop itself, a governance registry writer).

## Anti-Hallucination Rules (verbatim-adapted)

- **Cite line numbers for every claim** — "function `X` at `file:line` does
  `Y`" — never assert behavior without a citation to the actual code.
- **No naming-based inference** — a function's name is a hint, never
  evidence; its documented Purpose/Inputs/Outputs/Effects must trace to its
  actual body.

## Primary Target for This Repository (TC-EXT-025-02 scope)

`tools/supervisor/**` and `tools/governance/**` — explicitly, not
`src/python/{format}/`, which is already covered by Gate 8's existing
threat-model scope per `docs/governance/security.md`'s `## Scope` section.

## Steps

1. **Phase 1** across the target directory tree (`tools/supervisor/**` and/or
   `tools/governance/**`, per the invoking request's scope).
2. **Phase 2** per function in scope, applying the Case A/Case B split and
   the numeric thresholds.
3. **Phase 3** global reconstruction — state/invariants and trust-boundary
   map across the whole target.
4. **Package the output** as a context artifact (module map, per-function
   analyses, trust-boundary map) — no vulnerability claims, no severity, no
   fixes — for downstream consumption by `sharp-edges`,
   `agent-owasp-compliance`, or `/found-issue-ownership`.

## Allowed Paths

- Read, Grep, Glob (+ Bash/Task only to invoke this skill itself — never to
  mutate the target) — `tools/supervisor/**`, `tools/governance/**` (primary
  target, read only)
- `docs/governance/security.md` (read only — the Gate 8 scope-boundary
  citation that justifies this skill's primary-target scope)
- No dedicated report file is written by default — the context artifact is
  recorded inline in the invoking taskcard's evidence; a persisted copy under
  `reports/context-building/<target>.md` is optional, at the invoking task's
  discretion, never a default write

## Forbidden Paths

- **No vulnerability identification, fix proposal, PoC generation, or
  severity assignment** — enforced by this skill's own Non-Goal, not merely
  a path restriction.
- `src/**`, `tests/**` — read only, never mutated by this skill.
- `.supervisor/skill-registry.yaml`, `.supervisor/policies.yaml`,
  `registry/found-issue-register.yaml` — never written by this skill; any
  finding that looks like a real vulnerability is handed off to
  `/found-issue-ownership` or a vulnerability-hunting reviewer skill, not
  recorded as this skill's own disposition.

## Constraints

- Read-only in all 3 phases via Read/Grep/Glob; Bash/Task are used only to
  invoke this skill, never to mutate the target or write findings.
- Enforces its own Non-Goal at every phase: no vulnerability claim, fix
  suggestion, PoC, or severity rating is ever emitted by this skill.

## Idempotency Contract

Given the same target module/system content and the same 3-phase methodology
(this file), the review produces the same module map, the same per-function
analyses (meeting the same threshold minimums), and the same trust-boundary
map. No randomness; no time-dependent output.

## Governance Note

Per TC-EXT-012 (external-skill-import plan) and TC-EXT-025 (this import),
this skill was cleared by `/skill-scanner` before registration. Its
CC-BY-SA-4.0 share-alike attribution is recorded above in both prose and an
HTML comment, per TC-EXT-001-02's precedent for CC-BY-SA-4.0 imports. Its
primary target scope (`tools/supervisor/` + `tools/governance/`) closes the
exact coverage gap identified against Gate 8's own stated `## Scope` in
`docs/governance/security.md`.
