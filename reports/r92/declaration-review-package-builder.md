---
sprint: R92
generated_by: r92-worker
---

# Declaration Review Package Builder (Train C)

Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

## Tool

`tools/supervisor/build_declaration_review_package.py`

## What It Packages

- evidence/evidence-declaration.yaml
- evidence/evidence-manifest.yaml
- materialized/materialized-evidence-manifest.yaml
- materialized/missing-evidence-report.md
- materialized/source-change-diffs.patch
- supervisor/work-item-grades.json + .md + .yaml
- supervisor/session-resume.md
- supervisor/next-sprint.md
- supervisor/materialized-evidence-review.md
- state/product-code-change-ledger.json
- state/poc-targets.yaml
- r91-review/r91-work-item-grades.json + .md
- package-manifest.json (metadata)

## Output

- `.local/supervisor/reviews/<run_id>/declaration-review-package.zip`
- `.local/supervisor/reviews/<run_id>/declaration-review-package.sha256.json`

## R91 Test Run Result

```
ZIP SHA-256: ef9a14a01ab334749738ca5a08109f1857b5a4c4a45d22b7787941d67e39d8cc
ZIP size: 22188 bytes
Missing artifacts: 0
BUILD: SUCCESS
```

Command:
```
.local/venv/Scripts/python tools/supervisor/build_declaration_review_package.py \
  --declaration .local/evidences/r91/evidence-declaration.yaml
```

## Status: IMPLEMENTED AND VERIFIED
