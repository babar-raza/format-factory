---
sprint: R91
generated_by: r91-worker
---

# Product Code Ledger Enforcement Hardening

## Summary

The product-code ledger validator has been hardened so that any `src/` change without a corresponding ledger entry fails validation. R90 ledger validated as PASS. R91 src changes are governed.

## R90 Ledger Validation

Result: PASS

All R90 src changes (`src/net/fods/FodsCsvExporter.cs`, `src/net/fodt/FodtDocument.cs`, `src/net/netpbm/Model/NetpbmImage.cs`) were present in the ledger with valid item_ids and sprint references. No ungoverned src changes detected.

## R91 Enforcement: validate_product_code_ledger.py

`tools/supervisor/validate_product_code_ledger.py` updated with:

1. **Git diff scan**: The validator now runs `git diff HEAD -- src/` and parses changed file paths from the diff output.
2. **Ledger cross-reference**: Each changed `src/` file is checked against all ledger entries. If no ledger entry references the file, validation fails.
3. **Error output**: Reports the exact file path and the missing ledger entry item_id pattern that would satisfy it.
4. **Exit code**: Returns exit code 2 (validation failed) when ungoverned src changes are found.

## Backfilled Entries Policy

R89 entries that were backfilled (marked `BACKFILLED_PRE_GOVERNANCE`) remain in the ledger as historical record. They:
- Are accepted as valid entries for their specific files
- CANNOT authorize new changes to those same files (a new ledger entry is required)
- Are flagged in validator output as `historical_only: true`

## R91 Governed Src Changes

The following R91 src changes require ledger entries to be written before source edit:

| Source File | Ledger Entry ID | Feature |
|---|---|---|
| `src/net/fods/FodsDocument.cs` | `R91-GOVERNED-FODS-NET-SETCELLVALUE-001` | SetCellValue API |
| `src/net/fodt/FodtDocument.cs` | `R91-GOVERNED-FODT-NET-SAVETOFILE-001` | SaveToFile API |
| `src/net/netpbm/Model/NetpbmImage.cs` | `R91-GOVERNED-NETPBM-NET-SETPIXELCOLOR-001` | SetPixelColor API |

Each ledger entry is written to `tools/evidence/product-code-ledger.yaml` before the corresponding src edit. The autonomous-cycle validator checks the ledger before accepting the declaration.

## Validator Integration

`autonomous_cycle.py` Step 2 calls `validate_product_code_ledger.validate(declaration)`. If any ungoverned src change is found, the cycle exits with code 1 (declaration invalid).

## No False Positives for Test Files

The validator scans only paths matching `src/` prefix. Files under `tests/`, `reports/`, `examples/`, `.supervisor/`, and `tools/` are excluded from ledger requirements.
