# Train I: Progress Detector v3

## Changes
- Added `classify_progress_type()`: returns one of 5 progress types
  - `PRODUCT_PROGRESS`: product capabilities moved to DONE
  - `TOOLING_PROGRESS`: only tooling/acceleration lanes completed
  - `EVIDENCE_ONLY`: lanes completed but no capability changes
  - `BLOCKED_WITH_REASON`: explicit blockers prevent progress
  - `NO_PROGRESS`: nothing happened

## Tests Added (7 new)
- `test_classify_product_progress` — positive: caps done + product lanes
- `test_classify_tooling_progress` — positive: only acceleration/supervisor lanes
- `test_classify_evidence_only` — positive: lanes but no caps
- `test_classify_blocked_with_reason` — positive: blockers present
- `test_classify_no_progress` — positive: empty state
- `test_classify_blocked_takes_priority` — negative: blockers override product progress
- `test_classify_no_ledger` — negative: None ledger doesn't crash
