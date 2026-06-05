---
version: "1.1"
last-updated: "2026-06-03"
phase-available: "3+"
gate-required: null
generated_by: claude
visibility: generated
---

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

## Allowed Paths

- `tests/python/<format>/` (test creation)
- `docs/export/` (status documentation)
- `product-capability-matrix/poc-targets.yaml` (dogfood status update only)
- `src/python/<format>/` (only if new code needed for export path)

## Forbidden Paths

- `registry/format-registry.yaml` (gate authority)
- `plans/master-plan.md` (operational authority)
- External imaging backends (PIL, OpenCV, openpyxl)

## Rollback

1. Remove test file `tests/python/<format>/test_r<n>_<feature>_dogfood.py`
2. If src changes were made, revert and remove ledger entry
3. Revert dogfood_status in `product-capability-matrix/poc-targets.yaml`
4. Re-run `python tools/supervisor/validate_product_code_ledger.py` to confirm PASS

## Validation

Complete when: export test passes, dogfood status is evidence-backed, and no external imaging backends detected.

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
with: skill_id, source_format, target_format, dogfood_status, test_file, test_results, verdict.

## Changelog

- 1.0 (2026-06-02): Initial version
- 1.1 (2026-06-03): Added frontmatter, allowed/forbidden paths, rollback, changelog (Skills R99)
- 1.2 (2026-06-03): Added validation, transcript requirement (Skills R101).
