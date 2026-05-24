# R57 Train F — Format Advancement Report

**Sprint:** FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
**Train:** F — Format Advancement
**Date:** 2026-05-23
**Status:** COMPLETE

---

## Summary

Train F advances CSV from Gate 5 to Gate 6 with a full deterministic oracle test suite.
This is a real code + test advancement, not a status confirmation.

---

## CSV Gate 6 PASS

**Format:** CSV (Comma-Separated Values, RFC 4180)
**Prior gate:** Gate 5 PASS (R56)
**This gate:** Gate 6 PASS (R57)

**Gate 6 test file:** `tests/python/csv/test_csv_gate6_oracle.py`
**Test count:** 26
**Test result:** 26/26 PASS

### Oracle Coverage

| Class | Tests | What it verifies |
|-------|-------|-----------------|
| `TestCsvOracleCorpusSamples` | 9 | Committed sample corpus: exact headers, rows, column counts |
| `TestCsvOracleSynthetic` | 9 | Synthetic edge cases: tab/semicolon delimiters, embedded newlines, doubled-quote escaping, empty fields, BOM stripping, large files |
| `TestCsvOracleErrors` | 4 | Error handling: CsvInputError, safe parse fallback, empty file |
| `TestCsvOracleProbe` | 4 | probe_csv: exists flag, first_line, size_bytes |

### Key Documented Behaviors

1. **Header heuristic requires numeric data:** The parser's `_has_header_heuristic()` only detects a header when at least one of the first 3 data rows contains a numeric field. All-text CSVs return `has_header=False`. This is documented in tests.

2. **Embedded newlines in quoted fields:** The RFC 4180 state-machine parser correctly stitches multi-line quoted fields. The field value contains the embedded newline.

3. **Double-quote escape (RFC 4180 §6):** `""` inside a quoted field yields a literal `"` in the parsed value.

4. **UTF-8 BOM stripping:** The parser reads with `encoding="utf-8-sig"`, stripping the BOM from the first field.

### pack.yaml Updated

`acquisition-packs/csv/pack.yaml` updated with Gate 6 entry:
- `status: pass`
- `sprint: R57`
- `test_count: 26`
- `oracle_strategy: deterministic`

---

## Train F Verdict

TRAIN_F_COMPLETE — CSV advanced from Gate 5 → Gate 6. 26 new oracle tests pass. pack.yaml updated.
