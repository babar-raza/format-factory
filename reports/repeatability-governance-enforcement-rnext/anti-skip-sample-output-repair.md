# Anti-Skip Sample-Output Exemption Repair
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-ENFORCEMENT-RNEXT
# Lane: C (GRE-TC-003)
# Date: 2026-06-08

## Problem

Anti-skip checker was emitting `missing_sample_outputs: LOW` violation for every sprint,
including governance-only sprints that have no PRODUCT_SOURCE work items. The sample
output requirement is only meaningful for PRODUCT_SOURCE items that produce new format
functions.

## Root Cause

`detect_missing_sample_outputs()` in `tools/supervisor/anti_skip_checker.py` did not
check `item_type` before checking for sample outputs. It fired on all sprints regardless
of whether any product source work occurred.

## Fix

Added to `tools/supervisor/anti_skip_checker.py`:

1. Three module-level constants:
   - `_GOVERNANCE_ITEM_TYPES` — item types that never need sample outputs
   - `_GOVERNANCE_EXCEPTION_CLASSES` — exception_classification values that exempt
   - `_DRY_RUN_CLASSIFICATIONS` — PRODUCT_SOURCE items with dry-run classification

2. Two helper functions:
   - `_is_governance_only_sprint(declaration)` — True if all items are governance types
   - `_has_product_source_items(declaration)` — True if any non-exempt PRODUCT_SOURCE items

3. Early-return exemption in `detect_missing_sample_outputs()`:
   ```python
   if _is_governance_only_sprint(declaration) or not _has_product_source_items(declaration):
       return {
           "check": "missing_sample_outputs",
           "is_violation": False,
           "exemption": "governance_or_no_product_source",
           "recommendation": "Sample outputs not required: no PRODUCT_SOURCE items..."
       }
   ```

## Exemption Matrix

| Item Type / Classification | Sample Output Required |
|---|---|
| GOVERNANCE_DOC | NO |
| GOVERNANCE_SCHEMA | NO |
| GOVERNANCE_POLICY | NO |
| GOVERNANCE_TASKCARD | NO |
| LEGACY_BACKFILL_METADATA | NO |
| exception_classification: investigation_only | NO |
| exception_classification: legacy_backfill | NO |
| exception_classification: dry_run_fixture | NO |
| PRODUCT_SOURCE (no exemption) | YES |
| Mixed sprint with PRODUCT_SOURCE | YES |

## Backward Compatibility

The fix adds an early-return path only. Existing logic for product-source sprints is
unchanged. The only behavioral change is that governance-only sprints now return
`is_violation=False` with `exemption` field set.

## Tests

File: `tests/supervisor/test_anti_skip_sample_output_exemption.py`
Result: **16/16 PASS**

Tests cover:
- governance-only sprint exempt
- legacy backfill exempt
- dry-run fixture exempt
- product-source sprint still violates
- mixed sprint still violates
- `_is_governance_only_sprint()` helper correct
- `_has_product_source_items()` helper correct
- Real Sprint 2 declaration correctly detected as governance-only

## Before/After for Sprint 2

Before: anti-skip reported 1 LOW violation (`missing_sample_outputs`)
After: anti-skip passes with no sample output violation (0 violations expected)
