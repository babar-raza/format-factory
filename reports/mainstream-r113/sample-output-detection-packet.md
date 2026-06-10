# Sample-Output Detection Packet

## Sprint: mainstream-r113
## Target: Acceleration stream anti-skip validator

## Problem
The `missing_sample_outputs` check reports 0 sample outputs found, but 5 sample files exist at `reports/mainstream-r112/sample-outputs/`.

## Root Cause
The anti-skip check searches for sample outputs only under `evidence_root` (`.local/evidences/<run_id>/`) or specific field names in the declaration. It does not search:
1. `reports/<run_id>/sample-outputs/` directory
2. `evidence_artifacts` entries with `type: sample`
3. `reports_created` entries containing `sample-outputs/`

## Existing Sample Outputs (R112)
| File | Path | Size |
|------|------|------|
| Product proof matrix | reports/mainstream-r112/sample-outputs/sample-product-proof-matrix.json | 1345 B |
| Source ledger entry | reports/mainstream-r112/sample-outputs/sample-source-ledger-entry.json | 1109 B |
| Mainstream next prompt | reports/mainstream-r112/sample-outputs/sample-mainstream-next-prompt.md | 1682 B |
| Prompt-quality classification | reports/mainstream-r112/sample-outputs/sample-prompt-quality-classification.json | 1379 B |
| Dogfood proof | reports/mainstream-r112/sample-outputs/sample-dogfood-proof.json | 822 B |

## Proposed Fix (for Acceleration stream)
The `missing_sample_outputs` check should also search:
1. `reports/<run_id>/sample-outputs/` directory
2. `evidence_artifacts` where `type == "sample"`
3. Paths in `reports_created` matching `*/sample-outputs/*`
