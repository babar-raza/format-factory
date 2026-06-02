---
sprint: R92
generated_by: r92-worker
---

# Evidence Materializer (Train B)

Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

## Tool

`tools/supervisor/materialize_declared_evidence.py`

## What It Does

1. Reads evidence-declaration.yaml
2. Verifies every declared evidence path and changed file against the repo
3. Computes SHA-256 for every verified artifact
4. Captures git diff for declared source changes (working tree or HEAD)
5. Captures product-code ledger entry count
6. Captures POC matrix snapshot
7. Grades each declared work item (ACCEPTED / ACCEPTED_WITH_WARNINGS / INSUFFICIENT_EVIDENCE / etc.)
8. Produces materialized-evidence-manifest.yaml, missing-evidence-report.md, source-change-diffs.patch
9. Writes reports/supervisor/materialized-evidence-review.md

## Outputs

- `.local/supervisor/materialized/<run_id>/materialized-evidence-manifest.yaml`
- `.local/supervisor/materialized/<run_id>/missing-evidence-report.md`
- `.local/supervisor/materialized/<run_id>/source-change-diffs.patch`
- `reports/supervisor/materialized-evidence-review.md`

## Exit Codes

- 0 — all declared artifacts verified
- 2 — some artifacts missing (partial; grades still generated)
- 9 — unexpected error

## R91 Test Run Result

```
Artifacts verified: 23
Artifacts missing: 0
Work item grades: 12
MATERIALIZATION: COMPLETE (all artifacts verified)
```

Command:
```
.local/venv/Scripts/python tools/supervisor/materialize_declared_evidence.py \
  --declaration .local/evidences/r91/evidence-declaration.yaml
```

## Status: IMPLEMENTED AND VERIFIED
