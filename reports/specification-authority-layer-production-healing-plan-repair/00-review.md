# Plan Review — Specification Authority Layer Production Blocker Healing Plan
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-HEALING-PLAN-REPAIR-001
Reviewed: 2026-06-04

## Scope

This review assesses the original Specification Authority Layer Production Blocker Healing plan
(FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001) across 8
dimensions before repair begins.

---

## Dimension 1 — Technical Correctness

**Question:** Does the plan correctly describe the 11 subsystems, 13 lifecycle states, and
deterministic context-pack contract?

**Finding:** YES

The plan correctly identifies all 11 subsystems in order:
  SpecSourceRegistry → SpecVault → SpecParser → SpecNormalizer → SpecIndexer →
  SpecDigestor → RequirementExtractor → SpecVerifier → RequirementGraph →
  ContextPackBuilder → SpecGovernanceRuntime

It correctly identifies all 13 lifecycle states (A–M):
  source_candidate → registered_source → raw_snapshot → parsed_artifact →
  normalized_artifact → indexed_artifact → digest_artifact → candidate_requirement →
  verified_requirement → context_pack → usage_record → coverage_record → refresh_event

The deterministic context-pack contract (same source + same request + same index version →
same manifest.sha256) is correctly described with a 17-step retrieval algorithm and 8 output
files per pack.

**Verdict:** CORRECT

---

## Dimension 2 — Production Safety

**Question:** Does the plan prevent unsafe actions (product source edits, commits, pushes)?

**Finding:** PARTIAL

Hard prohibitions are explicitly listed and correct:
- No edits to src/net/**, src/python/**, tests/net/**, tests/python/**
- No git commit, no git push
- No Gate 8 or Gate 11 approval

However: Python portability is NOT addressed. All Python commands use bare `python` which
fails on Windows with a virtual environment where `python` is not the venv interpreter.
This is a production safety issue because it causes silent failure of critical commands.

**Verdict:** PARTIAL — hard prohibitions correct; Python portability missing

---

## Dimension 3 — Governance Alignment

**Question:** Does the plan use the project's declared evidence schema, taskcard lifecycle,
and verdict naming?

**Finding:** PARTIAL

Issues identified:
- Evidence declaration pre-fills `worker_self_verdict: PASS` before validation runs.
  The supervisor schema requires this to be determined after validation, not pre-assumed.
- No `autonomous-cycle --declaration` step is present in the closeout sequence.
  The autonomous-cycle is the mandatory supervisor grading step; without it, the sprint
  cannot be graded.
- Taskcard lifecycle is partially correct in structure but initialization is wrong
  (see Dimension 6).

**Verdict:** PARTIAL — schema compliance issues; autonomous-cycle missing

---

## Dimension 4 — Path Safety

**Question:** Are all output paths within allowed boundaries?

**Finding:** PARTIAL

The plan writes to:
- `reports/specification-authority-layer-production-healing/**` ✓ allowed
- `.local/evidences/specification-authority-layer-production-healing/**` ✓ allowed

However, the `build_declaration_review_package.py` tool writes to:
- `.local/supervisor/reviews/specification-authority-layer-production-healing/**`
  This path is NOT listed in the plan's allowed paths. A strict execution agent would refuse
  to write there.

**Verdict:** PARTIAL — review package path unlisted

---

## Dimension 5 — Evidence Closeout

**Question:** Does the plan require autonomous-cycle? Does it require review package?

**Finding:** PARTIAL

- autonomous-cycle: NO — not mentioned anywhere in the closeout sequence. This is the most
  critical missing element. The supervisor pipeline requires this step to grade the sprint.
  Exit codes 0/3/other must be handled explicitly.

- review package: PARTIAL — `build_declaration_review_package.py` is mentioned implicitly
  via ZIP creation instructions, but `review-package-proof.md` as a mandatory declared
  artifact with absolute path + SHA-256 + byte size + file count is NOT required.

**Verdict:** NO for autonomous-cycle; PARTIAL for review package

---

## Dimension 6 — Taskcard State

**Question:** Are taskcards initialized correctly as READY?

**Finding:** NO

The plan initializes all taskcards with `"status": "IN_PROGRESS"`. This is incorrect.
A taskcard is only `IN_PROGRESS` when actively being worked. Initializing all taskcards
to `IN_PROGRESS` simultaneously makes it impossible to identify which taskcard is actually
active and breaks lifecycle tracing.

Correct initialization: all taskcards must start as `READY`. Only the active taskcard is
set to `IN_PROGRESS`. Transitions: `READY → IN_PROGRESS → CLOSED_VERIFIED`.

**Verdict:** NO — incorrect initialization

---

## Dimension 7 — Validation Quality

**Question:** Does validation rely on hardcoded counts that could become wrong?

**Finding:** YES (hardcoded counts present — this is a defect)

The validation section asserts:
- "exactly 19 taskcards"
- "exactly 25 output files"
- "exactly 20 Markdown files"

These counts were written at plan time. If any taskcard is added, removed, or a file changes
type during execution, validation fails with a confusing mismatch that is not actually a
problem. This makes validation fragile and error-prone.

The fix is declared-vs-materialized: use `taskcard-state.json` as the source of truth for
taskcard count and `file-ownership-map.json` as the source of truth for output files.

**Verdict:** YES — hardcoded counts present (defect)

---

## Dimension 8 — Final Verdict Consistency

**Question:** Does the plan use project-standard verdict strings?

**Finding:** PARTIAL

The plan's "Final Response Format" section uses the template:
  `VERDICT: COMPLETE | BLOCKED | PARTIAL`

These are generic template strings, not project-standard verdict strings. The supervisor
grading pipeline looks for the specific macro verdict strings that are declared in the
evidence. For the healing sprint, the correct verdicts are:
  SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_READY_FOR_MWP_EXECUTION
  SPECIFICATION_AUTHORITY_LAYER_PLAN_HEALED_WITH_LIMITATIONS
  SPECIFICATION_AUTHORITY_LAYER_PLAN_STILL_BLOCKED

**Verdict:** PARTIAL — generic template not replaced with project-specific macros

---

## Defect Summary

| # | Defect | Dimension | Severity |
|---|--------|-----------|---------|
| 1 | No autonomous-cycle --declaration closeout | 5 | CRITICAL |
| 2 | .local/supervisor/reviews/... path not in allowed paths | 4 | HIGH |
| 3 | Hardcoded brittle counts (19 taskcards, 25 files, 20 Markdown) | 7 | MEDIUM |
| 4 | Taskcards initialized as IN_PROGRESS | 6 | HIGH |
| 5 | Evidence declaration pre-filled as PASS | 3 | HIGH |
| 6 | Python commands use raw python (not portable on Windows venv) | 2 | HIGH |
| 7 | Machine-specific C:\Users\prora\ input path | 2 | MEDIUM |
| 8 | Generic COMPLETE/BLOCKED/PARTIAL final verdict | 8 | MEDIUM |
| 9 | No review-package-proof.md artifact | 5 | HIGH |

All 9 known defects identified. 8/8 dimensions assessed. Defects span dimensions 2, 3, 4, 5, 6, 7, 8.

---

## Final Verdict

PLAN_NEEDS_REPAIR
