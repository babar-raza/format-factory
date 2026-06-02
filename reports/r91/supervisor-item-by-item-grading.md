---
sprint: R91
generated_by: r91-worker
---

# Supervisor Item-by-Item Grading

## Summary

Supervisor now produces per-item grades for every declared work item. Output files are written to `reports/supervisor/work-item-grades.md` and `reports/supervisor/work-item-grades.json`.

## Implementation

File: `tools/supervisor/grade_work_items.py`

Called by: `autonomous_cycle.py` Step 3 (after declaration validation, after test verification).

## Per-Item Grade Record

Each item graded produces a record with these fields:

| Field | Description |
|---|---|
| work_item_id | Matches declared item_id |
| claim | Worker's stated status for this item |
| evidence_found | yes/no — evidence_paths exist and are non-empty |
| tests_verified | yes/no — tests_supporting names found in test output |
| code_review_result | PASS / FAIL / NOT_APPLICABLE |
| status | See status values below |
| reason | Human-readable grading rationale |
| rework_instruction | Specific instruction if REWORK_REQUIRED or OVERCLAIMED |
| may_continue_parallel_work | true/false — safe lanes can proceed even if this item needs rework |

## Status Values

| Status | Meaning |
|---|---|
| ACCEPTED | All criteria met, evidence verified, tests pass |
| REWORK_REQUIRED | Claim made but specific deficiency found — exact repair instruction provided |
| OVERCLAIMED | Worker claimed more than evidence supports — scope must be narrowed |
| INSUFFICIENT_EVIDENCE | Work may have been done but evidence files missing or empty |
| BLOCKED_EXTERNAL_GATE | Cannot be graded because it requires human gate approval |
| DEFERRED_WITH_REASON | Intentionally deferred — not a failure, carries forward with documented reason |

## Global Verdict Derivation

Global verdict is derived from individual grades using this logic:

1. Any OVERCLAIMED item → global = CRITICAL_REWORK (exit 3)
2. Any REWORK_REQUIRED item with `may_continue_parallel_work=false` → global = REWORK_REQUIRED (exit 3)
3. Any REWORK_REQUIRED items with `may_continue_parallel_work=true` → global = PARTIAL_REWORK_SAFE_LANES_CONTINUE (exit 0 with rework lanes in next sprint)
4. All ACCEPTED or DEFERRED_WITH_REASON or BLOCKED_EXTERNAL_GATE → global = ACCEPTED (exit 0)

## Output Files

### reports/supervisor/work-item-grades.json

Machine-readable grades used by `generate_next_sprint.py` to build rework and new-work lanes.

```json
{
  "sprint_id": "...",
  "graded_at": "ISO-8601",
  "global_status": "ACCEPTED|PARTIAL_REWORK_SAFE_LANES_CONTINUE|REWORK_REQUIRED|CRITICAL_REWORK",
  "items": [
    {
      "work_item_id": "...",
      "status": "ACCEPTED",
      "evidence_found": true,
      "tests_verified": true,
      "may_continue_parallel_work": true,
      "rework_instruction": null
    }
  ]
}
```

### reports/supervisor/work-item-grades.md

Human-readable summary table with one row per item plus global verdict block at the bottom.

## Integration with autonomous_cycle.py

Step 3 of autonomous_cycle.py calls `grade_work_items.grade_all(declaration, test_log)` and writes both output files. If global_status is CRITICAL_REWORK, the cycle exits with code 3. Otherwise grading results are passed to `generate_next_sprint.py`.
