# Format Factory — Final Certification Audit Report

**Mission:** CERT-EXHAUST-HEAL-20260703
**Audit Date:** 2026-07-03
**Auditor:** Autonomous certification pipeline (Claude Sonnet 4.6)
**Plan:** plans/.claude/whimsical-gathering-toucan.md

---

## Executive Summary

All 20 Python FOSS formats are **CERTIFIED**. All 7 certification sprints completed.
**UNKNOWN_MATERIAL_BEHAVIOR = 0**

---

## Per-Dimension Results

### D1 — Format Certification (20/20 CERTIFIED)

| Dimension | Result |
|-----------|--------|
| Total formats | 20 |
| CERTIFIED | 20 |
| WITH_GAPS | 0 |
| NOT_CERTIFIED | 0 |
| Material stubs | 0 |
| Weak assertions | 0 |
| Uncovered exceptions | 0 |

Source: `reports/certification/portfolio-certification-matrix.json` (regenerated 2026-07-03)

### D2 — Mutation Testing

| Format | Kill Rate | Verdict |
|--------|-----------|---------|
| fods | 100.0% | STRONG |
| csv | 100.0% | STRONG |
| zst | 100.0% | STRONG |

FODS was at 50% before TC-MUT-001. Hardened via 16 targeted tests in
`tests/python/fods/test_parser_mutation_hardening.py` using a new sample
`samples/by-format/fods/valid/mutation-coverage.fods`.

Source: `reports/certification/{fods,csv,zst}/mutation-baseline.json`

### D3 — Test Collection Errors

| Suite | Collection Errors |
|-------|-------------------|
| tests/python/fods/ | 0 |

32 stale ledger entries (R258–R286 range) removed from `registry/known-failure-ledger.yaml`.
1565 FODS tests now collect cleanly.

### D4 — Security Audits (20/20 formats)

| Coverage | Count |
|----------|-------|
| PASS | 1 (csv) + 9 XML formats (pre-existing) |
| NOT_APPLICABLE | 10 (non-XML formats) |
| Missing | 0 |

All 20 formats now have `security-audit.json`. Non-XML formats documented as NOT_APPLICABLE.
CSV documents MAX_FILE_SIZE=64MiB, MAX_ROWS=1,000,000 limits.

### D5 — Property-Based Testing (3 pilot formats)

| Format | Tests | Status |
|--------|-------|--------|
| fods | 6 | PASS |
| csv | 5 | PASS |
| zst | 5 | PASS |

Total: 16 Hypothesis-backed property tests across 3 formats.
Source: `reports/certification/{fods,csv,zst}/property-test-report.json`

### D6 — Cross-Language Behavioral Parity

| Format | Samples | Verdict |
|--------|---------|---------|
| csv | 2 | PASS |
| fods | 1 | PASS |
| tsv | 1 | PASS |

Python and .NET parsers produce equivalent `row_count`, `column_count`, and `sheet_count`
for all tested samples. Tool: `tools/certification/cross_language_parity_checker.py`.
Source: `reports/certification/{csv,fods,tsv}/cross-impl-parity.json`

### D7 — CI Certification Gate

Gate tool created at `tools/certification/ci_certification_gate.py`.
Baseline locked at `reports/certification/certification-baseline.json`.

- Exit 0 on clean repo: **VERIFIED**
- Exit 1 with specific message on simulated regression: **VERIFIED**

---

## Behavioral Divergence Notes

### CSV header detection
Python's `parse_csv` uses an auto-detection heuristic (`_has_header_heuristic`).
The .NET `CsvDocument.Load` requires an explicit `hasHeaders` parameter.
This is a documented design difference, not a defect. The parity checker
calls .NET with `hasHeaders: true` for samples with text headers.

---

## Final Verdict

| Dimension | Status |
|-----------|--------|
| 20 formats CERTIFIED | YES |
| Material stubs | 0 |
| Weak assertions | 0 |
| Uncovered exceptions | 0 |
| FODS mutation kill rate | 100% |
| CSV/ZST mutation kill rate | 100% |
| FODS collection errors | 0 |
| Security audits complete | YES (20/20) |
| Property tests | 16 PASS |
| Cross-language parity | PASS (3 formats) |
| CI gate operational | YES |

**UNKNOWN_MATERIAL_BEHAVIOR = 0**

**FINAL VERDICT: CERTIFIED — All 7 certification sprints complete. No material behavioral unknowns remain.**
