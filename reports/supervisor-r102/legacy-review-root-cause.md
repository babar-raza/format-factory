# Root Cause: Legacy Review Overwrite of Declaration-Driven Evidence

## Problem Statement
After every autonomous-cycle, `reports/supervisor/evidence-review.json` shows
`BLOCKED_MISSING_FINAL_VERDICT` with sprint_id `unknown`, contradicting the
`latest-cycle-summary.md` which correctly shows ACCEPTED.

## Root Cause Chain

### RC-1: Legacy validator applied to declaration-review packages
`validate_evidence_for_supervisor.py` expects a legacy ZIP bundle with:
- `final-verdict.md`
- `bundle-metadata/` directory
- `repo/` directory
- R90 contract `required_repo_files` (19 files)
- `git-status-final.txt`
- Sidecar proof

Declaration-review packages have none of these. They have:
- `evidence/` (declaration + manifest)
- `materialized/` (inspected artifacts)
- `supervisor/` (grades, review, cycle-manifest)
- `package-manifest.json`

Result: BUNDLE_VALIDATION: FAIL, sprint_id: unknown, 0 tests.

### RC-2: evidence-review.json gets overwritten after bridge
1. `autonomous_cycle.py::bridge_to_legacy_format()` writes correct evidence-review.json
2. `cmd_autonomous_cycle` in supervisor_loop.py calls `cmd_next()` which reads it
3. Later: something calls `validate_evidence_for_supervisor.py` on the declaration-review-package.zip
4. This overwrites evidence-review.json with the BLOCKED result

### RC-3: compare_goal_to_evidence.py checks are legacy-only
The contradiction detector checks:
- `check_missing_final_verdict()` — always fails for declaration packages
- `check_bundle_validation_fail()` — always fails for declaration packages
- `check_sprint_id_mismatch()` — sprint_id "unknown" from legacy validator

These checks are appropriate for legacy bundles but false positives for
declaration-driven evidence.

### RC-4: No declaration-source marker in evidence-review.json
The bridged evidence-review.json from autonomous_cycle.py doesn't flag itself
as declaration-sourced, so there's no way for downstream code to skip
inappropriate legacy checks.

## Fix Plan

### Fix 1: Add `_declaration_sourced` marker to bridge output
In `autonomous_cycle.py::bridge_to_legacy_format()`, add:
```python
evidence_review["_declaration_sourced"] = True
```

### Fix 2: Make compare_goal_to_evidence.py skip legacy checks for declaration-sourced reviews
When `review.get("_declaration_sourced")`, skip:
- `check_missing_final_verdict()`
- `check_bundle_validation_fail()`

### Fix 3: Make validate_evidence_for_supervisor.py detect declaration-review packages
If the ZIP contains `evidence/evidence-declaration.yaml`, skip legacy contract
validation and report that it's a declaration-review package.

### Fix 4: Protect bridge output from overwrite
The bridge output should have a timestamp/source check — if evidence-review.json
was written by bridge_to_legacy_format more recently than the legacy validator,
the legacy validator should not overwrite it.
