# Prompt Quality Report
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-LAYER-HARDENING-PILOTS-001
# Lane: K (GRH-TC-013)
# Date: 2026-06-08

## Purpose

This report grades the execution prompt for Sprint 2 (governance hardening) on key
quality dimensions, with lessons for improving future governance sprint prompts.

## Prompt Evaluated

Sprint 2 execution prompt found at:
`reports/repeatability-governance-hardening-rnext/00-preflight.md`
and the task description provided at session start.

## Quality Assessment

### Dimension 1: Scope Clarity (Grade: A)

The sprint scope was clearly defined:
- 13 named lanes with explicit deliverables per lane
- "Forbidden" list explicitly states: no commits, no pushes, no gate approval, no
  external LLM calls, no product source implementation, no autonomy improvement
- Contradictions from Sprint 1 listed by name with expected fix actions

### Dimension 2: State Machine Accuracy (Grade: A-)

The 15-state machine definition was accurate and consistent with the Sprint 1 contracts.
The FORBIDDEN_JUMPS_PRODUCT_ONLY distinction (applies only to PRODUCT_SOURCE, not to
GOVERNANCE_DOC) was specified correctly in the requirements.

Deduction: The prompt did not explicitly state which validators are in scope for
`run_all_governance_validators()` — the implementation correctly inferred 10 validators
from the validator-hardening-plan.md, but the prompt should have been explicit.

### Dimension 3: Evidence Requirements Clarity (Grade: A)

Requirements were clear:
- Evidence declaration run_id: `governance-repeatability-hardening-rnext`
- Governance items use `exception_classification: investigation_only`
- Legacy backfill items use `exception_classification: legacy_backfill`
- Tests use `.py` file paths in `tests_supporting`

### Dimension 4: Dependency Ordering (Grade: B+)

Dependencies were mostly explicit (e.g., GRH-TC-010 depends on GRH-TC-005 for pilots
to have validators to test). However, the prompt did not explicitly state that Lane G
(backfill verification / GR-REPLAY taskcards) depends on Lane E (validators, specifically
on `ALLOWED_TRANSITIONS` and `CLOSE_ELIGIBLE_STATES` being defined before replay state
can be validated).

Improvement: Future prompts should include a dependency DAG or explicit ordering matrix.

### Dimension 5: Contradiction Resolution Guidance (Grade: A)

The 3 contradictions from Sprint 1 were precisely described:
- CONTR-001: Manifest count mismatch (16 vs 32 vs 33) — root cause documented
- CONTR-002: Evidence quality score (supervisor=0.0 vs anti-skip=1.0) — fix location identified
- CONTR-003: Adoption compliance false FAIL — affected item types listed

Each contradiction had a named fix location (file, function, line range), making
execution straightforward.

### Dimension 6: Rollback Instructions (Grade: A)

AGENTS.md AE2 compliance was explicitly required. The prompt did not include any
prohibited git commands (`git checkout --`, `git reset`, etc.). Compliant rollback
alternative (delete created files) was implicit from Sprint 1 contracts.

### Dimension 7: Verification Commands (Grade: B)

The prompt specified JSON/YAML validation commands for schemas and taskcards.
However, it did not specify exact pytest invocation commands for the new validator tests.

Improvement: Future prompts should specify:
```
pytest tests/supervisor/test_governance_validators.py -v
pytest tests/supervisor/test_governance_validators_integration.py -v
pytest tests/supervisor/test_governance_pilots.py -v
```
explicitly rather than leaving test discovery to the execution agent.

### Dimension 8: File Ownership Clarity (Grade: A)

The 13-lane file ownership matrix was created in `file-ownership-matrix.md` with
explicit per-lane ownership. No ambiguity about which lane owns which files.

### Dimension 9: Anti-Skip Compliance Guidance (Grade: B+)

The prompt was aware of anti-skip requirements and specified governance exemptions.
However, it did not explicitly state that all test work items must include `.py` file
paths (not directory paths) in `evidence_paths`. This was discovered during Sprint 1
and documented in the sample-output-policy.md (this sprint).

Improvement: Add to standard prompt template: "All test evidence_paths must point to
individual `.py` files, never to directory paths."

### Dimension 10: Handoff Boundary (Grade: A)

The `handoff_to_autonomy_sprint: true` items were clearly identified in each GRH-TC
taskcard. The autonomy boundary contract (Lane L) was explicitly scoped to document
the boundary, not to implement anything beyond it.

## Overall Grade: A- (90/100)

| Dimension | Grade | Score |
|-----------|-------|-------|
| Scope clarity | A | 95 |
| State machine accuracy | A- | 90 |
| Evidence requirements | A | 95 |
| Dependency ordering | B+ | 88 |
| Contradiction resolution | A | 95 |
| Rollback instructions | A | 95 |
| Verification commands | B | 85 |
| File ownership | A | 95 |
| Anti-skip compliance | B+ | 88 |
| Handoff boundary | A | 95 |
| **Overall** | **A-** | **92** |

## Lessons for Future Governance Sprints

1. **Include explicit pytest invocations** in the verification section, not just
   "run tests for lane X". Name exact test files.

2. **Add a dependency DAG** for lanes that have non-obvious ordering constraints.

3. **Specify `.py` file path requirement** for test evidence artifacts explicitly in
   every sprint prompt template.

4. **Document `run_all_governance_validators()` contract** in the prompt — specify
   how many validators it must run and what structure it returns.

5. **Explicit validator count** — state "implement exactly 10 validators numbered 1-10"
   rather than referencing the validator-hardening-plan.md by name alone.
