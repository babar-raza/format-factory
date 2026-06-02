---
sprint: R91
generated_by: r91-worker
---

# SYLK / DIF Reduced FOSS Product Hardening

## Summary

SYLK R91 hardening adds malformed row diagnostics via a new `sylk_parse_with_diagnostics` function. The R89 shadow fix for `sylk_to_csv` is verified passing. DIF remains at Gate 10 with no changes needed in R91.

## SYLK Baseline Verification

`sylk_to_csv` is functional:
- CSV export tests pass
- R89 csv-shadow fix verified (no shadow import, uses real stdlib csv writer)

No changes to the existing `sylk_to_csv` function in R91.

## R91 Addition: Malformed Row Diagnostics

Skill used: `/add-python-object-model-feature`

Ledger entry: `R91-GOVERNED-SYLK-PY-MALFORMED-ROW-DIAGNOSTICS-001`

Function added to `src/python/sylk/sylk_parse.py`:

```python
def sylk_parse_with_diagnostics(data: bytes) -> dict:
    """
    Parse a SYLK file and return both parsed content and a diagnostic list.

    Returns:
      {
        "workbook": {...},
        "errors": [
          {"row": int, "field": str, "message": str}
        ]
      }

    Rows with missing mandatory fields (ID;, B;, C;, E;) are included
    in the workbook as partial rows and listed in errors[].
    """
```

## 5 New Tests

File: `tests/python/sylk/test_r91_sylk_malformed_row_diagnostics.py`

Tests:
1. `test_valid_sylk_produces_empty_error_list` — clean file: errors == []
2. `test_missing_id_field_produces_error` — row without ID; → error entry
3. `test_missing_bounds_produces_error` — B record without required field → error entry
4. `test_multiple_errors_all_reported` — multiple bad rows: all reported, none silently dropped
5. `test_partial_parse_still_returns_workbook` — malformed rows do not prevent well-formed rows from being returned

All 5 tests pass.

## FOSS Matrix Update

```yaml
sylk:
  gate_status: gate_10_local_rc_ready
  csv_export_status: IMPLEMENTED
  malformed_row_diagnostics: IMPLEMENTED
  r91_hardening: complete

dif:
  gate_status: gate_10_local_rc_ready
  csv_export_status: IMPLEMENTED
  r91_hardening: no_changes_needed
```

## DIF Status

DIF CSV export via `dif_to_csv` is functional and tested (R84). No new work needed for DIF in R91. Gate 10 status maintained.

## Evidence Artifacts

- `src/python/sylk/sylk_parse.py` — updated with `sylk_parse_with_diagnostics`
- `tests/python/sylk/test_r91_sylk_malformed_row_diagnostics.py` — 5 passing tests
- `product-capability-matrix/foss-matrix.yaml` — updated entries
- `tools/evidence/product-code-ledger.yaml` — `R91-GOVERNED-SYLK-PY-MALFORMED-ROW-DIAGNOSTICS-001` entry
