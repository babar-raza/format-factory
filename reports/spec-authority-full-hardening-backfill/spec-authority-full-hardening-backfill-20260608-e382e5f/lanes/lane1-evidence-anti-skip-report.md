# Lane 1 — Evidence and Anti-Skip Hardening
Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-FULL-HARDENING-BACKFILL-AND-PILOT-MEGA-TRAIN-001
Run ID: spec-authority-full-hardening-backfill-20260608-e382e5f
Generated: 2026-06-08T17:45:00Z

## Root Cause of missing_sample_outputs

`anti_skip_checker.detect_missing_sample_outputs()` searches:
1. `evidence_root/sample-outputs/` (= `.local/evidences/<run_id>/sample-outputs/`)
2. `declaration.evidence_artifacts[].type == "sample_output"`
3. `evidence-manifest.yaml` artifacts with `type: sample_output`

Prior sprints put outputs in `reports/<run>/sample-outputs/` — NOT in `evidence_root/sample-outputs/`.
Anti-skip could not find them → `missing_sample_outputs` violation persisted.

## Fix Applied

1. Created `.local/evidences/spec-authority-full-hardening-backfill-20260608-e382e5f/sample-outputs/`
2. Generated 8 sample outputs directly in evidence_root/sample-outputs/:
   - authority-gate-fods-p6.json
   - authority-gate-zst-p6.json
   - authority-gate-csv-p3.json
   - authority-gate-gnumeric-p1.json
   - authority-gate-fodt-p0.json
   - authority-conveyor-fods-target6.json
   - authority-conveyor-zst-target6.json
   - authority-conveyor-csv-target4.json
3. Also copied to reports/<run>/sample-outputs/ for documentation
4. Evidence declaration uses `type: sample_output` for these artifacts

## Regression Tests Added
File: `tests/supervisor/test_anti_skip_sample_output_regression.py`
Tests: 11/11 PASS
Coverage:
- Evidence root directory detection
- Declaration artifact type detection
- Non-sample-output types do NOT satisfy check
- Current sprint passes
- Prior sprint pattern (reports-only) fails correctly

## Anti-Skip Result
`detect_missing_sample_outputs(evidence_root)`:
- outputs_found: 8
- is_violation: False
- ✓ FIXED

## Standing Pattern (all future sprints must follow)
```
# At sprint start, generate real outputs into:
.local/evidences/<run_id>/sample-outputs/

# In evidence declaration:
evidence_artifacts:
  - path: <path>
    type: sample_output   # THIS type is required, not proof_graph/authority_matrix
```

## Verdict: LANE1_ANTI_SKIP_FIXED
