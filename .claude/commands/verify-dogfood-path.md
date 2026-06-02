# /verify-dogfood-path

Verify that a dogfood export path works end-to-end using an installed Format Factory library.

## Usage

```
/verify-dogfood-path
```

## What This Skill Does

1. **Select path**: Reads `docs/export/dogfood-export-strategy.md` and picks an unverified dogfood lane
2. **Check library**: Verifies the Format Factory library is installed (`import <format>` works)
3. **Write export test**: Creates `tests/python/<format>/test_r<n>_<format>_dogfood_<target>.py`
4. **Run test**: Runs the export test using the installed library
5. **Update matrix**: Updates `reports/r<n>/dogfood-export-status.md` with IMPLEMENTED or GAP result
6. **Ledger**: If any `src/` changes were needed, adds ledger entry

## Constraints

- Must use an installed Format Factory library (not PYTHONPATH hack)
- Must produce actual output (CSV, TXT, etc.) and verify it non-empty
- If library not installed, report GAP and stop (do not fabricate IMPLEMENTED)
- If dogfood path already IMPLEMENTED, verify it still works and document

## Evidence Required

- Library import succeeds
- Test file path and name
- Test output: N passed, 0 failed
- Dogfood matrix status: IMPLEMENTED | GAP_LIBRARY_NOT_INSTALLED | GAP_MISSING_FEATURE

## Common Dogfood Paths

- FODS → CSV (fods.workbook_to_csv)
- FODT → TXT (fodt.document_to_text)
- PPM → PGM (ppm.ppm_to_pgm)
- SYLK → CSV (sylk.sylk_to_csv)
