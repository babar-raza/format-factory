---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same target behavior + same 5-step cycle produce the same test-first sequencing (RED before GREEN, GREEN before REFACTOR); read/write is scoped to tests/** directly, with src/** changes delegated to an already-governed mutation skill"
loc_budget: "0 lines of executable code (prompt-driven checklist only; no bundled script)"
test_path: "N/A (prompt-spec skill, no executable code) — verification is the manual scan proof recorded under TC-EXT-014-03"
external_skill_origin: true
external_skill_source: obra/superpowers
external_skill_commit: d884ae04edebef577e82ff7c4e143debd0bbec99
external_skill_license: MIT
risk_level: MEDIUM
created-by: TC-EXT-014-01
product_track: governance
---

# /test-driven-development

Red-Green-Refactor test-first discipline. Enforces the Iron Law — no production
code is written until a failing test exists that requires it — and, unlike the
purely read-only methodology skills in this family, this skill writes real test
files directly and can drive real (delegated) production-code changes. That is
why its `risk_level` is `MEDIUM`, not `LOW`.

## Attribution

This skill adapts the 5-step Red-Green-Refactor cycle (RED, Verify RED, GREEN,
Verify GREEN, REFACTOR) and its 8-item Final Verification Checklist from
`obra/superpowers`'s `test-driven-development` skill (MIT), commit
`d884ae04edebef577e82ff7c4e143debd0bbec99`. The cycle structure, the Iron Law
framing ("NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"), the "delete it,
start over" rule for code written before its test, and the Verification
Checklist are carried over verbatim-adapted from the upstream skill. The
FF-specific `src/**` delegation boundary (replacing upstream's generic
"exceptions require asking the human partner" framing) is original to this
repository. License: MIT — attribution preserved per license terms; no upstream
code is executed, only its documented methodology is adapted into prose.
Cleared by `/skill-scanner` per TC-EXT-012's mandatory gating rule
(TC-EXT-014-03).

## Purpose

Prevent untested production code from entering the repository by making the
failing test the mandatory first artifact of any change, not an afterthought
written to match code that already exists. A test written or adjusted after the
implementation to "make it green" does not count — it proves nothing about
whether the test can actually catch a regression.

## When to Use

- Any change to `tests/**` that is meant to drive or accompany a behavior
  change (new function, new branch, bugfix) — this is the primary invocation
  path.
- As the optional sub-procedure named by `/product-source-task` Steps 2-3,
  `/add-python-api` Steps 6-7, and `/add-dotnet-api` Steps 6-7 when those
  skills' own execution handoff calls for test-first sequencing.
- Any time production code is about to be written "to see if it works" without
  a pre-existing failing test — the Iron Law applies unconditionally, not only
  to features perceived as risky.

## Iron Law

**NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.**

Wrote code before the test existed? **Delete it. Start over.** Upstream is
explicit that this code may not be kept "as reference" while the test is
retrofitted around it — a test written to match existing code is not a test,
it is a tautology. The same rule applies here without dilution.

## Steps (the real 5-step cycle, adapted)

### Step 1 — RED

Write **one** minimal failing test for the next unit of behavior. Not a batch
of tests for the whole feature — one test, for the smallest next increment.
The test must express the expected behavior in terms a reviewer (or a spec
fact, where `spec_qname_required` applies upstream) can check independently of
the implementation.

### Step 2 — Verify RED (mandatory)

Run the test. Confirm it **fails**, and confirm it fails **for the right
reason** — the assertion is reached and does not hold — not because of a typo,
an import error, a missing fixture, or a setup mistake that would make any
test "fail" regardless of the behavior under test. A red bar for the wrong
reason is not RED; fix the test harness first and re-verify.

### Step 3 — GREEN

Write the **minimal** code required to make the failing test pass. No extra
generality, no unrelated cleanup, no additional behavior beyond what the test
demands.

- If the minimal implementation is confined to `tests/**` (a fixture, a test
  helper, a scaffold), write it directly — see Allowed Paths.
- If the minimal implementation requires a `src/**` change, this skill does
  **not** write it directly. Invoke the applicable already-governed mutation
  skill — `/product-source-task`, `/add-python-api`, or `/add-dotnet-api` —
  and hand it the Step 1 failing test as the driving test for its own Steps.
  This skill supplies the RED-before-GREEN discipline; the mutation skill
  retains sole ownership of the `src/**` write surface, per this repository's
  EP-3 rule (CLAUDE.md, "Skill-Driven Architecture"). See FF-Specific Scope
  Limit below — this boundary is not optional and has no local exception path.

### Step 4 — Verify GREEN (mandatory)

Re-run the test. Confirm:
- The previously-failing test now passes.
- The surrounding test suite for the affected module still passes (no
  regressions introduced by the minimal implementation).
- Output is **pristine** — no stray errors, warnings, or skipped tests hiding
  in otherwise-green output.

### Step 5 — REFACTOR

Only after Step 4 is green: clean up naming, remove duplication, simplify
structure. **No new behavior** is introduced during REFACTOR — if new behavior
is needed, that starts a new cycle at Step 1, not a REFACTOR-step addition.

### Repeat

Return to Step 1 for the next minimal increment of behavior.

## Final Verification Checklist (8 items, verbatim-adapted)

Before declaring any cycle (or set of cycles for one change) complete, every
item below must be checkable honestly:

1. Every new function has a test.
2. You watched each test fail before writing its implementation.
3. Each test failed for the **right** reason (not a typo or setup error).
4. You wrote the minimal code needed to pass — no more.
5. All tests pass (the new one and the full surrounding suite).
6. Test output is pristine — no unexplained errors, warnings, or skips.
7. The implementation is real code, not a mock or a hardcoded return matching
   the test's expected value.
8. Edge cases are covered (boundary values, empty/None input, invalid input
   where the unit under test can signal an error).

**Can't check all eight boxes? You skipped TDD. Start over from Step 1.**

## FF-Specific Scope Limit (replaces upstream's "ask the human partner" exceptions)

Upstream `test-driven-development` allows narrow exceptions (throwaway
prototypes, generated code, config files) by discussing them with a human
partner mid-session. This repository has no ambient human partner mid-session
and operates under the Human-Free Autonomy Doctrine (CLAUDE.md), so this skill
does not adopt that escalation path. Instead:

- **The `src/**` delegation boundary in Step 3 is unconditional**, not a
  default that can be waived by classifying a change as a "prototype" or
  "generated code" exception. This skill creates no direct product-source
  mutation pathway of its own — that would itself be an EP-3 violation
  (CLAUDE.md, "Skill-Driven Architecture": agents must not directly edit
  `src/**` without invoking a governed skill).
- **If a genuine throwaway-prototype or generated-code case arises** (code
  that is not going to become tracked production or test source at all — e.g.
  a disposable scratch script outside both `src/**` and `tests/**`), that is
  outside this skill's Allowed Paths entirely; classify it per AGENTS.md
  §AG1-AG2's decision loop rather than granting an ad hoc exception here.
- **Config-file-only changes** (no behavior change, e.g. a YAML/JSON value
  edit) are outside this skill's scope — TDD applies to behavior, not to
  static configuration; use the governed skill that owns that config file.

## Mandatory Validations

- `test_precedes_implementation` — no Step 3 "GREEN" production code exists
  before a Step 1 "RED" failing test has been written and Step 2-verified for
  the same unit of behavior.
- `red_verified` — the RED test was actually executed and observed to fail for
  the correct reason, not merely asserted to fail in prose.
- `green_verified` — the GREEN step's passing run includes the previously
  failing test now passing, the surrounding suite still passing, and pristine
  output; all three, not just the new test.
- `no_direct_src_mutation` — this skill's own write surface never includes
  `src/**`; every `src/**` change originating from a GREEN step is executed by
  invoking `/product-source-task`, `/add-python-api`, or `/add-dotnet-api`, and
  that invocation is recorded in the cycle's evidence.
- `verification_checklist_complete` — all 8 Final Verification Checklist items
  are checked, with evidence, before the cycle is declared closed. A cycle
  closed with any item unchecked is a `claimed_unproven` finding under
  CLAUDE.md's Sprint Audit classification, not `completed_verified`.

## Allowed Paths

- `tests/**` — write directly (new/modified test files, fixtures, scaffolds
  used to drive Steps 1-2 and Step 3's test-only branch)
- Any source, spec, or documentation file relevant to the behavior under test
  — read only, to understand the increment being test-driven
- `reports/`, `.local/evidences/**` — cycle evidence output (write)

## Forbidden Paths

- `src/**` — **no direct write, ever.** A `src/**` change required by Step 3
  must be executed by invoking `/product-source-task`, `/add-python-api`, or
  `/add-dotnet-api`; this skill never creates its own product-source mutation
  pathway (EP-3, CLAUDE.md "Skill-Driven Architecture").
- `registry/found-issue-register.yaml`, `registry/root-cause-register.yaml` —
  written only via `/found-issue-ownership`, not by this skill
- `plans/master-plan.md`, `.local/supervisor/active-plan-lock.json` — never
  touched by a test-drive cycle
- `.supervisor/skill-registry.yaml`, `registry/format-registry.yaml` — this
  skill does not alter governance or gate authority

## Stop Conditions

- Stop and delete-then-restart if production code exists without a preceding
  failing test for it — do not keep it "as reference" while retrofitting a
  test around it (Iron Law).
- Stop if a RED test passes immediately — it is not exercising new behavior;
  revise the test before proceeding to Step 3.
- Stop if a GREEN step would require a `src/**` write with no corresponding
  `/product-source-task`, `/add-python-api`, or `/add-dotnet-api` invocation —
  this is an EP-3 violation, not a shortcut to take and document afterward.
- Stop if any of the 8 Final Verification Checklist items cannot be checked
  honestly — do not declare the cycle complete; return to the step that
  produced the gap.

## Idempotency Contract

Given the same target behavior, the same 5-step cycle (this file), and the
same repository state, re-running the methodology produces the same
sequencing outcome: a RED test precedes its GREEN implementation, which
precedes any REFACTOR. No randomness; the only state that advances across
repeated cycles is the count of behavior increments covered.

## Output Format

A test-drive cycle's evidence should record, per increment:

```
## TDD Cycle: <short behavior description>

### Step 1 — RED
- Test added: <path>
- Behavior asserted: <one sentence>

### Step 2 — Verify RED
- Command run: <test command>
- Failure reason: <verbatim — confirms right-reason failure, not setup error>

### Step 3 — GREEN
- Implementation: <tests/** direct write, OR delegated to <skill> with
  handoff <path/id>>
- Minimal code summary: <what was added, nothing more>

### Step 4 — Verify GREEN
- Command run: <test command>
- New test: PASS
- Surrounding suite: <N/N> PASS
- Output pristine: YES/NO

### Step 5 — REFACTOR
- Changes made: <summary, or "none needed">
- New behavior introduced: NO (must always be NO at this step)

### Final Verification Checklist
1-8: <checked/unchecked per item, with evidence reference>
```

## Governance Note

Per TC-EXT-012 (external-skill-import plan), this skill was cleared by
`/skill-scanner` before registration (TC-EXT-014-03) — the mandatory gating
step for every external-skill import in TC-EXT-013 through TC-EXT-028. This
skill is a prompt/methodology spec with no bundled script and no hooks; its
`risk_level: MEDIUM` (versus `LOW` for the purely read-only methodology
skills in this family) reflects that it writes real test files under
`tests/**` directly and can trigger a delegated `src/**` mutation via an
already-governed skill, rather than only producing prose findings.
