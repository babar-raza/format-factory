---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same target type/class + same 5-part Analysis Framework produce the same 4 dimension ratings; read-only end to end"
loc_budget: "0 lines of executable code (prompt-driven checklist only; no bundled script)"
test_path: "N/A (prompt-spec skill, no executable code) — verification is the manual scan proof recorded under TC-EXT-017-02"
external_skill_origin: true
external_skill_source: anthropics/claude-code
external_skill_commit: 988b3e56432775c09bba903ba22522b97cd0f2fb
external_skill_license: Apache-2.0
risk_level: LOW
created-by: TC-EXT-017-02
product_track: governance
---

# /type-design-analyzer

Read-only reviewer that rates how well a type/class expresses and enforces
its own invariants. Never modifies the reviewed target; produces a ratings +
findings report only.

## Attribution

This skill adapts the 5-part Analysis Framework, the 4 numeric rating
dimensions, and the named anti-pattern list from the `type-design-analyzer`
skill in Anthropic's `claude-code` PR Review Toolkit
(`anthropics/claude-code`, Apache-2.0), commit
`988b3e56432775c09bba903ba22522b97cd0f2fb`. The framework, the 1-10 rating
scale, and the anti-pattern names are carried over near-verbatim from the
upstream skill; the FF-specific finding-routing rule (any dimension rated
≤4/10 hands off to `/found-issue-ownership`) is original to this repository.
License: Apache-2.0 — attribution preserved per license terms; no upstream
code is executed, only its documented methodology is adapted into prose.
Cleared by `/skill-scanner` per TC-EXT-012's mandatory gating rule.

## Purpose

A type that does not enforce its own invariants is only as safe as every
caller's discipline — and callers are not reliably disciplined. This skill
gives a structured, repeatable way to rate a type's actual invariant
enforcement (not its documented intent) so weak type designs are caught as
findings rather than discovered as production bugs once a caller violates an
assumption the type never actually enforced.

## When to Use

- Reviewing any diff or file that introduces or modifies a class,
  dataclass, struct, or other type intended to carry an invariant (a Table
  cell that must always have a valid row/column, a codec model that must
  never be constructed in a partially-initialized state, etc.).
- Before closing a taskcard whose scope added or changed a domain/object
  model type under `src/**`.
- On request, against any existing type, as an ad hoc audit.

## Analysis Framework (the real 5-part framework, adapted)

1. **Identify Invariants.** Enumerate every invariant the type is supposed
   to maintain — the developer's intended guarantees, whether or not they
   are currently enforced in code. Distinguish invariants from mere
   documentation comments describing intent.
2. **Rate Encapsulation (1-10).** How well are the type's internal fields
   protected from direct, uncontrolled external mutation? A `10` means
   internal state can only change through methods that preserve invariants;
   a `1` means all fields are public and mutable with no protection at all.
3. **Rate Invariant Expression (1-10).** How clearly does the type's own
   structure (field types, constructor signature, method signatures)
   communicate its invariants to a reader who has not read any external
   documentation? A `10` means the invariant is obvious from the type
   signature alone; a `1` means the invariant exists only in a comment or
   nowhere at all.
4. **Rate Invariant Usefulness (1-10).** Do the identified invariants
   actually prevent real bugs, or are they trivial/vacuous constraints that
   provide little practical safety? A `10` means the invariant closes off a
   class of real failure; a `1` means the invariant is decorative.
5. **Rate Invariant Enforcement (1-10).** Are the invariants enforced at
   every mutation point (construction and every subsequent mutator), or only
   in some paths? A `10` means every path that could violate the invariant
   is guarded; a `1` means enforcement is inconsistent, bypassable, or
   documentation-only.

## Named Anti-Patterns

- **Anemic domain models** — types that are pure data bags with no behavior
  or invariant enforcement of their own; all validation lives elsewhere.
- **Types exposing mutable internals** — returning a mutable reference to
  internal state (e.g. a list/dict field) lets callers bypass every mutator
  method's invariant checks.
- **Invariants enforced only via documentation** — a docstring or comment
  says "must be non-negative" but no code path actually checks it.
- **Types with too many responsibilities** — a type conflating unrelated
  invariants (e.g. serialization format AND business validation AND caching
  state) makes every invariant harder to verify in isolation.
- **Missing validation at construction** — a type that can be constructed
  in an invalid state, with validation deferred (or never performed) until
  first use.
- **Inconsistent enforcement across mutators** — one setter validates its
  input, a sibling setter on the same field does not.

## Output Format

```
## Type Design Analysis: [Type Name]

### Invariants Identified
- <invariant 1>
- <invariant 2>
...

### Ratings (1-10)
- Encapsulation: <N>/10
- Invariant Expression: <N>/10
- Invariant Usefulness: <N>/10
- Invariant Enforcement: <N>/10

### Strengths
- <what the type does well>

### Concerns
- <anti-patterns identified, with file:line references>

### Recommended Improvements
- <concrete, actionable changes>
```

## Finding Routing

- **Any dimension rated ≤4/10** — hand off to `/found-issue-ownership`
  (Step 1 — Capture). A rating this low indicates the invariant is
  effectively unenforced or unexpressed, which is a correctness risk for
  every current and future caller, not a stylistic nit.
- **All 4 dimensions rated ≥5/10** — logged inline in the review output
  only; recommended improvements may still be noted without a mandatory
  hand-off.

## Allowed Paths

- The file(s)/diff under review — read only
- `.claude/commands/type-design-analyzer.md` (this file, its own reference
  framework)
- No report file is written by default — findings are recorded inline in the
  invoking taskcard's evidence

## Forbidden Paths

- **This skill never writes to the reviewed target, or to any other file.**
  It is read-only end to end: no edits to source, tests, configuration, or
  documentation under review.
- `src/**`, `tests/**` — read only, for the purpose of locating and rating
  type definitions; never mutated by this skill
- `.supervisor/skill-registry.yaml`, `registry/found-issue-register.yaml` —
  never written directly; ≤4/10 hand-off goes through
  `/found-issue-ownership`, not a direct write from this skill

## Constraints

- Read-only in all 5 framework steps. No writes, no external network calls,
  no hooks executed.
- All 4 dimensions must be rated for every type reviewed — a partial rating
  (e.g. 3 of 4 dimensions) is an incomplete review, not a valid output.

## Idempotency Contract

Given the same target type's content and the same 5-part Analysis Framework
(this file), the review produces the same invariants list and the same 4
numeric ratings. No randomness; no time-dependent output.

## Governance Note

Per TC-EXT-012 (external-skill-import plan) and TC-EXT-017 (5 read-only
reviewer imports), this skill was cleared by `/skill-scanner` before
registration. It is a pure prompt/methodology spec: no bundled script, no
automated file operations, no hooks, and no external network calls of its
own.
