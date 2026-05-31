# R85 Train N — SYLK Reduced/FOSS Product

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## Choice: SYLK selected over DIF

SYLK chosen because:
- sylk_to_csv implemented R84 (export working)
- DIF also has dif_to_csv but overlaps with SYLK
- SYLK is slightly more common in legacy spreadsheet interchange
- DIF: HOLD until SYLK POC complete

## Current Status

| Capability | Status |
|-----------|--------|
| Parse SYLK | PASS |
| sylk_to_csv | PASS (R84) |
| Write SYLK | NOT_IMPLEMENTED |
| Installed workflow | PARTIAL (no example yet) |

## Scope

SYLK scope: READ + EXPORT_ONLY

No SYLK writer is implemented. This is documented as the product scope, not a bug.
The FOSS value proposition: parse SYLK → export to CSV (standard format).

## Dogfooding

dogfood_status: IMPLEMENTED
SYLK→CSV: sylk_to_csv uses Format Factory SYLK parser (no external lib)

## Tests

tests/python/sylk/ — present with sylk_to_csv tests
R84 added 6 test_r84_sylk_to_csv.py tests (all pass in isolation)

## R85 Finding

No new code needed. SYLK read+CSV export is complete.
Gap: no installed example yet (target for next sprint).

## TRAIN_N_STATUS: COMPLETE (audit only)
