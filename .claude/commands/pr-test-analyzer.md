---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same target diff + same behavioral-coverage checklist produce the same criticality-rated gaps; read-only end to end"
loc_budget: "0 lines of executable code (prompt-driven checklist only; no bundled script)"
test_path: "N/A (prompt-spec skill, no executable code) — verification is the manual scan proof recorded under TC-EXT-017-04"
external_skill_origin: true
external_skill_source: anthropics/claude-code
external_skill_commit: 988b3e56432775c09bba903ba22522b97cd0f2fb
external_skill_license: Apache-2.0
risk_level: LOW
created-by: TC-EXT-017-04
product_track: governance
---

# /pr-test-analyzer

Read-only reviewer that assesses test coverage by behavior, not by line
count. Never writes tests itself; produces a criticality-rated gap report
only.

## Attribution

This skill adapts the behavioral-coverage focus and the 1-10 criticality
rating rubric from the `pr-test-analyzer` skill in Anthropic's `claude-code`
PR Review Toolkit (`anthropics/claude-code`, Apache-2.0), commit
`988b3e56432775c09bba903ba22522b97cd0f2fb`. The rubric bands and the gap
categories are carried over near-verbatim from the upstream skill; the
FF-specific finding-routing rule (findings rated 8-10 hand off to
`/found-issue-ownership`) is original to this repository. License:
Apache-2.0 — attribution preserved per license terms; no upstream code is
executed, only its documented methodology is adapted into prose. Cleared by
`/skill-scanner` per TC-EXT-012's mandatory gating rule.

## Purpose

A change can show 100% line coverage while never exercising the one error
path, boundary condition, or concurrent-access scenario that actually causes
production incidents. This skill shifts the review question from "is this
line executed by some test?" to "is this *behavior* — including its failure
modes — actually verified?", and rates each gap by how much it matters
rather than treating all missing coverage as equally urgent.

## When to Use

- Reviewing any diff that adds or changes production behavior, to assess
  whether the accompanying tests actually exercise that behavior's edge
  cases and failure modes.
- Before closing a taskcard under `/product-source-task`, `/add-python-api`,
  or `/add-dotnet-api` whose scope claims test coverage for new logic.
- On request, against any existing test suite for a target module, as an ad
  hoc audit.

## Focus: Behavioral Coverage, Not Line Coverage

Line/branch coverage percentages measure execution, not verification. A line
can execute inside a test with no assertion that would catch it being wrong.
This skill looks specifically for:

- **Untested error-handling paths** — the exception/error branch exists in
  the code but no test ever triggers it and checks the resulting behavior.
- **Missing edge-case/boundary coverage** — zero, empty, None/null, maximum,
  minimum, and off-by-one boundary values around the behavior under test.
- **Uncovered critical business-logic branches** — a conditional that
  changes real outcomes (pricing, permissions, data integrity) with only one
  of its branches ever exercised.
- **Absent negative test cases** — tests that confirm valid input succeeds,
  but no test that confirms invalid input is correctly rejected.
- **Missing async/concurrent-behavior tests** — race conditions, ordering
  guarantees, or cancellation/timeout paths left entirely unverified when
  the code under test is async or concurrent.

## Criticality Rubric (1-10, adapted verbatim)

For every suggested test, rate it:

- **9-10 — Critical**: gap could plausibly lead to data loss, a security
  bypass, or a system failure if it goes uncaught.
- **7-8 — Important**: gap is in business-logic behavior that materially
  affects correctness, though not catastrophically.
- **5-6 — Edge Cases**: gap is a boundary/edge condition worth covering but
  unlikely to be hit in typical usage.
- **3-4 — Nice-to-have**: gap would improve confidence but covers a very
  unlikely or low-impact scenario.
- **1-2 — Optional**: gap is cosmetic or redundant with existing coverage
  in spirit, if not in exact assertion.

## Output Format

```
## Test Coverage Analysis: [Target]

### Summary
- <one-paragraph overview of behavioral coverage quality>

### Critical Gaps (rated 8-10)
1. Location: <file:line or function>
   Criticality: <8-10>
   Gap: <untested behavior/error path/edge case>
   Suggested Test: <what the test should assert>

(repeat per critical gap)

### Important Improvements (rated 5-7)
- Location: <file:line> — Criticality: <5-7> — <gap and suggested test>

### Test Quality Issues
- <existing tests that assert too little, use overly broad mocks, or
  otherwise don't actually verify the behavior they claim to>

### Positive Observations
- <behaviors that are genuinely well-covered, including their error paths>
```

## Finding Routing

- **Findings rated 8-10** — hand off to `/found-issue-ownership`
  (Step 1 — Capture). A gap at this criticality is a plausible path to data
  loss, a security bypass, or a system failure going uncaught in production,
  and must become a durable `FI-NNN` record.
- **Findings rated below 8** — logged inline in the review output only; no
  mandatory hand-off, though they remain useful input to the taskcard's own
  test-completeness assessment.

## Allowed Paths

- The diff/target module and its existing test file(s) — read only
- `.claude/commands/pr-test-analyzer.md` (this file, its own reference
  rubric)
- No report file is written by default — findings are recorded inline in the
  invoking taskcard's evidence

## Forbidden Paths

- **This skill never writes a test file, or any other file.** It is
  read-only end to end: it recommends tests, it does not author them — test
  authorship (when acted on) is delegated to `/add-roundtrip-test`,
  `/test-driven-development`, or the applicable mutation skill.
- `src/**`, `tests/**` — read only, for the purpose of assessing existing
  behavior and coverage; never mutated by this skill
- `.supervisor/skill-registry.yaml`, `registry/found-issue-register.yaml` —
  never written directly; 8-10 rated finding hand-off goes through
  `/found-issue-ownership`, not a direct write from this skill

## Constraints

- Read-only. No writes, no external network calls, no hooks executed, and no
  test file is created by this skill under any circumstance.
- Every suggested test must carry an explicit 1-10 criticality rating — an
  unrated suggestion is an incomplete finding.

## Idempotency Contract

Given the same target diff/module and the same behavioral-coverage
checklist and rubric (this file), the review produces the same gaps and the
same criticality ratings. No randomness; no time-dependent output.

## Governance Note

Per TC-EXT-012 (external-skill-import plan) and TC-EXT-017 (5 read-only
reviewer imports), this skill was cleared by `/skill-scanner` before
registration. It is a pure prompt/methodology spec: no bundled script, no
automated file operations, no hooks, and no external network calls of its
own.
