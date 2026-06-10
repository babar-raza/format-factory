# Sprint Preflight Review
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-ENFORCEMENT-RNEXT
# Run ID: governance-repeatability-enforcement-rnext
# Lane: A (GRE-TC-001)
# Date: 2026-06-08

## Environment

- Python: 3.13.2 (system) / 3.13.2 (.local/venv)
- PYTHON_CMD: python (system) or .local/venv/Scripts/python (venv)
- PYTEST_CMD: .local/venv/Scripts/python -m pytest
- Git HEAD: e382e5fd8e65bc146c0821602cb8fb1ecfab982c
- Platform: Windows 11 Pro, bash shell

## AGENTS.md Compliance Summary

Key rules confirmed:
- AE1: git stash PROHIBITED
- AE2: Rollback must be authorized, exact-path scoped, documented
- AD5: No unauthorized destructive git operations
- P1-P4: No commit/push/merge without explicit authorization

This sprint: NO commits, NO pushes, NO gate approval.

## Prior Sprint Status

Previous sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-LAYER-HARDENING-PILOTS-001
Previous verdict: ACCEPTED_WITH_LIMITATIONS
Previous exit code: 0
Tests: 171/171 passing
Validators implemented but NOT YET wired into autonomous-cycle pipeline.

## Key Files Inspected

### tools/supervisor/governance_validators.py
- EXISTS: 10 validators implemented
- run_all_governance_validators() composite runner present
- Returns {all_pass, blocks_sprint, fail_count, validators, summary}
- NOT yet called from autonomous_cycle.py

### tools/supervisor/autonomous_cycle.py
- Step 2d: adoption compliance (validate_adoption_compliance.py) — ACTIVE
- Step 3b: anti-skip checks — ACTIVE
- Governance validators: NOT CALLED — insertion point is Step 2e

### tools/supervisor/anti_skip_checker.py
- detect_missing_sample_outputs() fires for ALL sprints regardless of item types
- No governance-sprint exemption exists for sample outputs
- Severity: LOW (informational only) — but still appears as violation

### tools/supervisor/grade_declared_work.py
- Governance sprint exemption: IMPLEMENTED (Sprint 2 fix)
- quality_score=0.0 does NOT penalize all-governance sprints

### tools/supervisor/validate_adoption_compliance.py
- GOVERNANCE_ITEM_TYPES constant: IMPLEMENTED (Sprint 2 fix)
- _has_explicit_exemption() checks item_type and exception_classification

## Sprint Scope

### What this sprint does
- Wire governance_validators.py into autonomous_cycle.py Step 2e
- Fix anti-skip sample-output exemption for governance sprints
- Capture 15 raw command logs
- Upgrade evidence quality scoring classification
- Validate adoption compliance through real pipeline
- Validate state machine against real taskcards
- Run 8 pipeline pilots
- Optional: source-mutation governance dry run on test fixture
- Write final evidence declaration + autonomous-cycle

### What this sprint does NOT do
- No product source function implementation
- No git commit or push
- No Gate 8/11 approval
- No external LLM calls
- No Qwen integration
- No broad feature expansion

## Known Issues (AGENTS.md compliance)
- All source changes to tools/supervisor/ are additive (new Step 2e, new exemption)
- No rollback needed (all changes create new code paths, not modify existing)

## Dirty State Classification
EXPECTED_ACCUMULATED_UNCOMMITTED_WORK_NO_FORBIDDEN_PATHS_CHANGED
(Sprint 1+2 governance infrastructure accumulated, no product source changes)
