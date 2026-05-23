# R55 Risk Register

**Sprint:** FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
**Date:** 2026-05-23

## Active Risks

### RISK-R55-001: FODT inline span parser change may break existing tests
**Severity:** Medium
**Probability:** Low
**Detail:** Adding `text:span` capture to fodt/parser.py changes the block dict structure.
Existing tests that check block content may fail if span runs are extracted into a `runs` key.
**Mitigation:** Read parser.py before modifying; add runs as additive field; run full test suite
after each parser change; fix any regressions immediately.
**Owner:** Train B

### RISK-R55-002: FODT document ordering fix may break list/table tests from R54
**Severity:** High
**Probability:** Medium
**Detail:** R54 tests for list/table emission assume separate sequences. If document ordering
changes the neutral model structure, those 21 tests may fail.
**Mitigation:** Understand current neutral model structure first; change ordering in a
backward-compatible way (maintain separate lists as deprecated, add unified sequence).
**Owner:** Train B

### RISK-R55-003: Python wheel rebuild may fail if packaging infra changed since R51
**Severity:** Medium
**Probability:** Low
**Detail:** build-local-packages.py was last run in R51. R52/R53/R54 source changes may
have introduced pyproject.toml incompatibilities or missing dependencies.
**Mitigation:** Run builder in verbose mode; fix any pyproject.toml issues; test with
specific Python 3.13.2 version used in project.
**Owner:** Train D

### RISK-R55-004: Binary Netpbm files may not be available in samples/
**Severity:** Medium
**Probability:** Medium
**Detail:** P5/P4/P6 binary Netpbm tests require binary sample files. Existing samples/
may only have ASCII variants.
**Mitigation:** Generate binary samples programmatically in test fixtures (struct.pack);
do not depend on existing corpus.
**Owner:** Train F

### RISK-R55-005: CSV/TSV parser may duplicate stdlib csv module semantics
**Severity:** Low
**Probability:** High
**Detail:** Python stdlib has a csv module. Creating src/python/csv/csv_parser.py risks
being a thin wrapper with no additional value.
**Mitigation:** Focus on format-factory neutral model integration (CsvDocument/CsvRow/CsvCell
dataclasses) and security guards (64MB limit, max-column/row caps). This is Gate 4 work only.
**Owner:** Train H

### RISK-R55-006: test_build_report_all_built count fix may expose other test failures
**Severity:** Low
**Probability:** Low
**Detail:** Changing the hardcoded count from 5 to 7 fixes the test but may reveal the
actual build report has a different structure than expected.
**Mitigation:** Read the test and the actual build report before changing the count.
**Owner:** Train E

### RISK-R55-007: INV-011..014 design may conflict with existing invariant structure
**Severity:** Low
**Probability:** Low
**Detail:** New invariants must be non-overlapping with INV-001..010 and must not depend
on live network calls or external tools.
**Mitigation:** Follow same pattern as INV-006..010: pure filesystem/git checks only.
**Owner:** Train A

## Inherited Risks (from R54)

| Risk ID | Description | Status |
|---------|-------------|--------|
| RISK-003 | Inline runs/tables/lists lost on Python FODT write | ACTIVE — Train B addressing |
| G11-G_NOT_STARTED | Gate 11 approval pending human decision | UNCHANGED |
| GATE8_HUMAN_APPROVAL | ODS/ODT/QOI/XCF/DIF/PPM Gate 8 pending | UNCHANGED |
| PACKAGE_NOT_PUSHED | All artifacts local-only | ACTIVE — Train D for local RC only |

## Closed Risks (R54)

| Risk ID | Description | Resolution |
|---------|-------------|-----------|
| SIDECAR_NOT_ENFORCED | Sidecar proof was optional | CLOSED: fail-closed enforcement (R54 Lane 2) |
| TC_MISLABELING | TC-0057/0058/0059 identities confused | CLOSED: Phase Audit 4 truth repair (R54 Lane 4) |
| FORMULA_LOSS | FODS formulas lost on Python write | CLOSED: TC-0054 CLOSED_VERIFIED (R53/R54 Lane 5) |
