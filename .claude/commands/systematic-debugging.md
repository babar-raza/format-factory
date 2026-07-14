---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same observed defect + same 4-phase checklist produce the same investigation path (root cause before fix, single hypothesis before test); read/write is scoped to the files under repair plus found-issue-ownership hand-off registers"
loc_budget: "0 lines of executable code (prompt-driven checklist only; no bundled script)"
test_path: "N/A (prompt-spec skill, no executable code) — verification is the manual scan proof recorded under TC-EXT-013-03"
external_skill_origin: true
external_skill_source: obra/superpowers
external_skill_commit: d884ae04edebef577e82ff7c4e143debd0bbec99
external_skill_license: MIT
risk_level: LOW
created-by: TC-EXT-013-01
product_track: governance
---

# /systematic-debugging

Root-cause-first debugging methodology. Enforces the Iron Law — no fix is applied
until the root cause has been investigated and a single hypothesis has been formed
and verified — and replaces upstream's "discuss with human partner" escalation with
a hand-off into this repository's own `/found-issue-ownership` workflow.

## Attribution

This skill adapts the 4-phase root-cause-first debugging methodology (Root Cause
Investigation, Pattern Analysis, Hypothesis and Testing, Implementation) and its
Iron Law from `obra/superpowers`'s `systematic-debugging` skill (MIT), commit
`d884ae04edebef577e82ff7c4e143debd0bbec99`. The phase structure, the Iron Law
framing, and the "≥3 failed fixes → question architecture" stop rule are carried
over verbatim-adapted from the upstream skill; the FF-specific escalation target
(`/found-issue-ownership`, replacing upstream's "discuss with human partner" step)
and the `found_issue_id_provided` mandatory validation are original to this
repository. License: MIT — attribution preserved per license terms; no upstream
code is executed, only its documented methodology is adapted into prose. Cleared
by `/skill-scanner` per TC-EXT-012's mandatory gating rule (TC-EXT-013-03).

## Purpose

Prevent guess-and-check "fixes" that patch a symptom without understanding why it
occurs — the single largest source of `completed_but_weakly_verified` and
`risk_not_reduced` sprint-audit findings (CLAUDE.md Sprint Audit classifications).
Every fix produced under this skill has a documented root cause, a single tested
hypothesis, and — when the defect is confirmed — a durable `FI-NNN` record instead
of an unrecorded narrative claim.

## When to Use

- A test fails, a governance validator reports FAIL/WARN, or behavior does not
  match the expected/spec-documented behavior.
- Before writing any fix in response to an error message, stack trace, or
  contradiction — the Iron Law applies unconditionally, not only to "hard" bugs.
- When a previous fix attempt did not resolve the issue (see the ≥3-attempts stop
  rule under Phase 4).
- Any of `/found-issue-ownership`'s own Trigger Conditions apply — this skill is
  the investigation methodology that precedes that skill's Step 3 (Root Cause).

## Iron Law

**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.**

A fix that is not preceded by root cause investigation is not a fix — it is an
unverified guess. Do not edit code to "see if that helps." Do not apply a fix
found by pattern-matching an error string against a search engine without first
tracing why *this* codebase produces that error.

## Steps (the real 4-phase methodology, adapted)

### Phase 1 — Root Cause Investigation

1. **Read Error Messages Carefully** — the full message, stack trace, and any
   surrounding log context; do not truncate or skim past the actual failure line.
2. **Reproduce Consistently** — establish a reliable repro before touching any
   code. If the defect cannot be reproduced, say so explicitly (do not fabricate
   a fix for an unreproduced symptom).
3. **Check Recent Changes** — `git log`/`git diff` / `git blame` on the affected
   paths; a regression usually has a recent, identifiable cause.
4. **Gather Evidence in Multi-Component Systems** — when the failure crosses a
   component boundary (e.g. codec → object model, or generator → product source),
   add diagnostic instrumentation at *each* boundary crossed, not just at the
   outermost symptom, so the failing boundary is identified by evidence rather
   than assumption.
5. **Trace Data Flow** — follow the actual value(s) involved from input to the
   point of failure; confirm at which step the value diverges from expectation.

### Phase 2 — Pattern Analysis

1. **Find Working Examples** — locate a comparable code path, format, or test
   that behaves correctly.
2. **Compare Against References** — diff the failing path against the working
   example structurally (imports, call order, argument shapes, spec_qname
   mapping, etc.).
3. **Identify Differences** — enumerate every concrete difference found, not
   just the first one noticed.
4. **Understand Dependencies** — confirm which of those differences are
   load-bearing (actually explain the failure) versus incidental.

### Phase 3 — Hypothesis and Testing

1. **Form Single Hypothesis** — state one specific, falsifiable explanation for
   the root cause. Do not carry multiple competing hypotheses forward at once.
2. **Test Minimally** — design the smallest possible check that would confirm or
   refute the hypothesis (a targeted print/assert/unit test), not a full fix.
3. **Verify Before Continuing** — do not proceed to Phase 4 until the minimal
   test confirms the hypothesis. If refuted, return to Phase 1 or Phase 2 with
   the new evidence — do not silently patch around the disproven hypothesis.
4. **When You Don't Know** — say so explicitly. See FF-Specific Escalation below
   for what "say so" means in this repository (it is never a silent stop).

### Phase 4 — Implementation

1. **Create Failing Test Case** — defer to Test-Driven Development where a TDD
   skill/process is available in this repository; the failing test encodes the
   confirmed root cause, not just the surface symptom.
2. **Implement Single Fix** — the smallest change that addresses the confirmed
   root cause. Do not bundle unrelated cleanup into the same fix.
3. **Verify Fix** — run the failing test (now passing) plus the surrounding
   test suite for the affected module; confirm no new failures were introduced.
4. **If Fix Doesn't Work** — count attempts.
   - **Attempts < 3**: this is a failed hypothesis, not a failed architecture —
     return to Phase 1 with the new evidence from the failed attempt.
   - **Attempts ≥ 3**: **STOP. Question the architecture.** This is NOT a failed
     hypothesis anymore — it is a signal that the surrounding design is wrong.
     Do not attempt a 4th narrow patch. See FF-Specific Escalation below.

## FF-Specific Escalation (replaces upstream's "discuss with human partner")

Upstream `systematic-debugging` escalates the "When You Don't Know" (Phase 3) and
"≥3 failed fixes" (Phase 4) cases by discussing with a human partner. This
repository has no ambient human partner mid-session, so both cases route into the
governed `/found-issue-ownership` workflow instead of an unstructured stop:

- **Root cause confirmed (Phase 3 "Verify Before Continuing" succeeds)**: hand off
  to `/found-issue-ownership` **Step 3 — Root Cause**. Capture the confirmed root
  cause in `registry/root-cause-register.yaml` and set `root_cause_id` on the
  originating issue before proceeding to Phase 4 Implementation. This makes the
  root cause a durable record, not a transient chat-only conclusion.
- **≥3 failed fix attempts (Phase 4 architecture-question stop)**: this is not a
  vague "needs human" escape hatch. Open (or update) a
  `/found-issue-ownership` entry that reflects the architecture-level nature of
  the finding, and explicitly consider Step 8's disposition set rather than
  abandoning the investigation silently:
  - `INVALID_FINDING_WITH_PROOF` — if further investigation shows the "failure"
    is actually correct behavior.
  - `VALID_GOVERNED_EXCLUSION` — if the architecture gap is an intentionally
    unsupported case, documented as such.
  - `BLOCKED_TRUE_EXTERNAL_DEPENDENCY` — if resolving the architecture question
    requires an external party.
  - `WAITING_VALID_GATE_11_AUTHORIZATION` — if the architecture change requires
    Babar Raza's Gate 11 business sign-off.
  - Any other disposition in `/found-issue-ownership`'s Step 8 table, chosen on
    the evidence — never one of the invalid dispositions
    (`pre_existing`, `unrelated`, `not_caused_by_me`, `ignored`,
    `outside_current_task`).
- **"Say so" (Phase 3, "When You Don't Know")**: say so in the current session's
  evidence/output *and* open a `/found-issue-ownership` entry at `status:
  discovered` so the open question is tracked as a governed record instead of a
  prose-only aside.

## Mandatory Validations

- `root_cause_precedes_fix` — no Phase 4 "Implement Single Fix" step is taken
  before Phase 1 root cause investigation and Phase 3 hypothesis verification
  have both completed for the defect at hand.
- `single_hypothesis_tested` — Phase 3 records exactly one hypothesis tested at a
  time; competing hypotheses are not tested simultaneously.
- `fix_attempt_count_tracked` — each Phase 4 iteration on the same defect
  increments a visible attempt counter so the ≥3-attempts stop rule is
  enforceable rather than informally tracked.
- `found_issue_id_provided` — **mandatory** whenever this skill's investigation
  produces a confirmed defect: either a root cause confirmed under Phase 3 (see
  FF-Specific Escalation, Step 3 hand-off) or a ≥3-failed-fix architecture
  question (Step 8 hand-off). The resulting `FI-NNN` from
  `registry/found-issue-register.yaml` must be referenced in the session's
  evidence. A confirmed defect closed without a `found_issue_id_provided`
  reference is a `claimed_unproven` finding under CLAUDE.md's Sprint Audit
  classification, not a `completed_verified` one.

## Allowed Paths

- Any source, test, or configuration file relevant to the defect under
  investigation (Phase 1-4 read/edit as required to reproduce, trace, and fix)
- `registry/found-issue-register.yaml`, `registry/root-cause-register.yaml` —
  written only via `/found-issue-ownership`, not directly by this skill
- Diagnostic/instrumentation additions temporary to the investigation (Phase 1
  step 4) — removed or converted to a permanent test before Phase 4 closes

## Forbidden Paths

- No direct write to `registry/found-issue-register.yaml` or
  `registry/root-cause-register.yaml` outside of invoking `/found-issue-ownership`
  — this skill hands off, it does not duplicate that skill's write surface
- `plans/master-plan.md`, `.local/supervisor/active-plan-lock.json` — never
  touched by a debugging investigation

## Stop Conditions

- Stop and hand off per FF-Specific Escalation if root cause cannot be confirmed
  after a genuine Phase 1-2 pass (do not fabricate a root cause to proceed)
- Stop at ≥3 failed fix attempts on the same defect — do not attempt a 4th narrow
  patch; escalate per FF-Specific Escalation instead

## Idempotency Contract

Given the same observed defect, the same 4-phase checklist (this file), and the
same repository state, re-running the methodology reaches the same root cause and
the same hypothesis-verification outcome. No randomness; the attempt counter is
the only state that advances across repeated Phase 4 iterations on one defect.

## Output Format

A debugging session's evidence should record, per defect:

```
## Systematic Debugging: <short defect description>

### Phase 1 — Root Cause Investigation
- Error message: <verbatim>
- Reproduction: <confirmed steps, or "not reproducible" + why>
- Recent changes checked: <git log/diff summary>
- Evidence at each component boundary: <list>
- Data flow trace: <where the value diverges>

### Phase 2 — Pattern Analysis
- Working example compared: <path/reference>
- Differences identified: <list>
- Load-bearing dependency: <which difference actually explains the failure>

### Phase 3 — Hypothesis and Testing
- Hypothesis: <single, falsifiable statement>
- Minimal test: <what was run>
- Verified: YES/NO — if NO, returned to Phase <1 or 2> with <new evidence>

### Phase 4 — Implementation
- Failing test case: <path>
- Fix applied: <summary>
- Verification: <test suite result>
- Attempt count: <N> — if ≥3, escalated per FF-Specific Escalation
  (found_issue_id: FI-NNN)
```

## Governance Note

Per TC-EXT-012 (external-skill-import plan), this skill was cleared by
`/skill-scanner` before registration (TC-EXT-013-03) — the mandatory gating step
for every external-skill import in TC-EXT-013 through TC-EXT-028. This skill is a
pure prompt/methodology spec: no bundled script, no automated file operations, no
hooks, and no external network calls of its own.
