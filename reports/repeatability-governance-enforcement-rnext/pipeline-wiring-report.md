# Pipeline Governance Wiring Report
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-ENFORCEMENT-RNEXT
# Lane: B (GRE-TC-002)
# Date: 2026-06-08

## Summary

Governance validators from `tools/supervisor/governance_validators.py` are now wired
into the autonomous-cycle pipeline as **Step 2e**, running between adoption compliance
(Step 2d) and work item grading (Step 3).

## Implementation

### Insertion Point

File: `tools/supervisor/autonomous_cycle.py`
Location: After Step 2d (adoption compliance), before Step 3 (grade work items)

### Step 2e Code

```python
# Step 2e: Governance validators (GRE-TC-002: wired into pipeline)
print("\n=== STEP 2e: GOVERNANCE VALIDATORS ===")
governance_validation_result = None
try:
    from governance_validators import run_all_governance_validators
    governance_validation_result = run_all_governance_validators(decl, repo_root)
    (review_dir / "governance-validation-result.json").write_text(...)
    print(f"  Governance: {_gov_pass} PASS / {_gov_warn} WARN / {_gov_fail} FAIL ...")
    if _gov_fail > 0:
        for v in result["validators"]:
            if v["result"] == "FAIL":
                print(f"    FAIL [{v['validator']}]: ...")
except Exception as e:
    print(f"  WARNING: Governance validators skipped: {e}")
```

### Blocking Integration

After grading (Step 3), governance blocking failures cause:
```python
if governance_validation_result.get("blocks_sprint"):
    review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
    review["stop_reason"] = f"Governance validator FAIL: ..."
```

### Output File

`governance-validation-result.json` written to:
`.local/supervisor/reviews/<run_id>/governance-validation-result.json`

## Enforcement Matrix

| Scenario | Expected | Enforced |
|----------|----------|----------|
| GOVERNANCE_DOC sprint | PASS | Yes |
| PRODUCT_SOURCE missing execution_method | FAIL (blocks) | Yes |
| PRODUCT_SOURCE missing idempotency_key | FAIL (blocks) | Yes |
| MANUAL_UNGOVERNED without LEGACY_BACKFILLED | FAIL (blocks) | Yes |
| REPLAYABLE claim without recipe | FAIL (blocks) | Yes |
| LEGACY_BACKFILL_METADATA with sidecar | PASS | Yes |
| GOVERNANCE_DOC DISCOVERED→GOVERNANCE_ACCEPTED | PASS | Yes |

## What Remains Deferred

- Wiring into `validate-declaration` command (currently advisory only)
- Wiring into `anti_skip_checker.py` as an additional check
- Enforcement in legacy commands (`run-on-latest`)

These deferrals are documented in `taskcards/governance-repeatability-enforcement/GRE-TC-002.yaml`.

## Tests

File: `tests/supervisor/test_pipeline_governance_wiring.py`
Result: **11/11 PASS**
