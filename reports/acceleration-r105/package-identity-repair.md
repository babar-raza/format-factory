# Package Identity Repair — R105

## Root Cause
build_declaration_review_package.py copied global supervisor state files (reports/supervisor/latest-cycle-summary.md, evidence-review.md, contradictions.md) directly into the package under `supervisor/` and `state/`. These files reflect whichever stream ran the autonomous-cycle last (Mainstream R106 in R104's case), NOT the declaring acceleration stream.

## Fix (R105)
1. **Stream-scoped supervisor outputs**: The builder now tries the run_id's own review directory first (`reviews/<run_id>/work-item-grades.json`, etc.). These are always stream-correct because they were generated specifically for that run.

2. **Global state relabeled**: Global supervisor state that may reference any stream is now packaged under `global-state/` instead of `supervisor/` or `state/`. This makes it clear these are cross-stream context, not primary identity files.

3. **Package identity validator**: New tool `validate_package_identity.py` checks 7 identity points in the ZIP:
   - evidence-declaration.yaml run_id and sprint_id
   - latest-cycle-summary.md stream
   - evidence-review.md stream
   - contradictions.md stream
   - context-pack.yaml latest_sprint stream
   - selected-product-gaps.json freshness

## Changed Files
- tools/supervisor/build_declaration_review_package.py (restructured packaging paths)
- tools/supervisor/validate_package_identity.py (NEW)
- tests/supervisor/acceleration/test_package_identity_validator.py (NEW, 16 tests)

## Test Results
16 tests passed, 0 failed
