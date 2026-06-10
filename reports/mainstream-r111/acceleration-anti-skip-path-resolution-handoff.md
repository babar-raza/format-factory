# Acceleration Anti-Skip Path Resolution Handoff

## From: Mainstream Stream (R111)
## To: Acceleration Stream
## Date: 2026-06-03

## Problem Statement
The anti-skip checker searches for lane-execution-ledger.json and sample-outputs under the
evidence_root (`.local/evidences/<run_id>/`), but R110 places these under
`reports/mainstream-r110/`. This path mismatch causes false-negative violations.

## Observed False Negatives

### 1. missing_lane_ledger
- **Expected path (anti-skip):** `.local/evidences/mainstream-r110/lane-execution-ledger.json`
- **Actual path:** `reports/mainstream-r110/lane-execution-ledger.json`
- **File exists:** Yes (17 lanes, all completed)

### 2. missing_sample_outputs
- **Expected path (anti-skip):** `.local/evidences/mainstream-r110/sample-outputs/`
- **Actual path:** `reports/mainstream-r110/sample-outputs/` (3 files)
- **Files exist:** Yes

## Root Cause
`autonomous_cycle.py:193` computes:
```python
sample_outputs_dir = evidence_root / "sample-outputs"
```
The `evidence_root` comes from the declaration's `evidence_root` field (`.local/evidences/mainstream-r110/`).
The anti-skip checker only searches under this root, not under `reports/<sprint>/`.

## Proposed Fix
The anti-skip checker should search multiple locations:
1. `evidence_root / "lane-execution-ledger.json"` (current)
2. `reports/<sprint_id>/lane-execution-ledger.json` (new)
3. Worker-declared paths from evidence_paths (new)

Similarly for sample-outputs.

## Expected Corrected Anti-Skip
After fix, R110 should have:
- missing_lane_ledger: False
- missing_sample_outputs: False
- All anti-skip checks should pass

## Tests to Add
1. Test anti-skip with lane ledger under reports/ (not evidence_root)
2. Test anti-skip with sample outputs under reports/ (not evidence_root)
3. Test anti-skip respects declared evidence_paths for artifact location
