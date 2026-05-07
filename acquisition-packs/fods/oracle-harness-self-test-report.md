---
artifact_id: oracle-harness-self-test-report-fods
artifact_type: acquisition-pack
path: acquisition-packs/fods/oracle-harness-self-test-report.md
format_id: fods
visibility: internal
publish_allowed: false
notes: "HARNESS_SELF_TEST_ONLY — not Gate 6 evidence. Created run038 (2026-05-07)."
---

# Oracle Harness Self-Test Report — FODS

**HARNESS_SELF_TEST_ONLY**

**This report is NOT Gate 6 oracle evidence.**
**It does NOT change Gate 6 status.**
**It does NOT create TC-0027 readiness.**

**Date:** 2026-05-07
**Run:** run038
**Purpose:** Validate compare/summarize plumbing using synthetic fixtures without LibreOffice.

---

## Result

**ORACLE_HARNESS_SELF_TEST: PASS**

4/4 samples PASS (synthetic CSV created, sample file exists, comparison logic ran)

---

## What Was Tested

| Sample | Synthetic CSV Created | Sample Exists | Parser Ran | Status |
|---|---|---|---|---|
| minimal-spreadsheet.fods | YES | YES | NO | SELF_TEST_PASS |
| multi-sheet-basic.fods | YES | YES | NO | SELF_TEST_PASS |
| typed-values-basic.fods | YES | YES | NO | SELF_TEST_PASS |
| formula-basic.fods | YES | YES | NO | SELF_TEST_PASS |

---

## What Was NOT Tested

- Real LibreOffice export (requires LibreOffice installed)
- Actual CSV output format from LibreOffice headless
- Real cell-by-cell comparison against oracle exports
- Gate 6 evidence quality

---

## Gate 6 Status

Gate 6 remains: **oracle_blocked_missing_tool**

LibreOffice must be installed before real Gate 6 oracle comparison can run.
See `acquisition-packs/fods/oracle-operator-handoff.md` for installation instructions.

---

## Confidence Gained

This self-test confirms:
1. Sample files exist and are parseable by the prototype parser.
2. Synthetic CSV export directories can be created in the expected path structure.
3. Comparison logic in `compare_fods_oracle.py` can operate when CSV exports are present.
4. Formula representation difference handling is in place (parser stores raw; oracle exports evaluated value).
5. Once LibreOffice is installed and real CSV exports are produced, the compare/summarize pipeline is ready to run without further code changes.

---

## Local-Only Outputs (Not in Evidence Bundle)

Raw self-test outputs are at `.local/oracle/fods/self-test/` (gitignored).
Do NOT commit these files.
