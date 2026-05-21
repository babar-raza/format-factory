# R40 Lane G: E2E Product Pipeline Proof Matrix

**Sprint:** R40
**Date:** 2026-05-21

## Product Track Matrix

| Track | Format | Tests | Result | Package Artifact | Smoke Test |
|-------|--------|-------|--------|-----------------|------------|
| Python FOSS | FODS | 181 pass, 4 skip | PASS | aspose_format_factory_fods-0.1.0.dev0.whl (10,696B) | PASS (import + __version__=0.1.0) |
| Python FOSS | FODT | 181 pass, 4 skip | PASS | aspose_format_factory_fodt-0.1.0.dev0.whl (12,290B) | PASS (import + __version__=0.1.0) |
| .NET Commercial | FODS | 157/157 | PASS | FormatFactory.Fods.0.1.0-tier0.nupkg (25,600B DLL) | PASS (FodsDocumentException on bad path) |
| .NET Commercial | FODT | 145/145 | PASS | FormatFactory.Fodt.0.1.0-tier0.nupkg (23,552B DLL) | PASS (FodtDocumentException on bad path) |

All 4 product-track cells: GREEN.

## Full Test Suite Summary (R40)

| Suite | Passed | Failed | Skipped | Notes |
|-------|--------|--------|---------|-------|
| tests/ (all excl. AI, evidence) | 2452 | 2 | 13 | 2 failures pre-existing (dif/ppm test_probe_nonexistent) |
| tests/evidence/ | 613 | 0 | 26w | - |
| tests/ai/ | 617 | 0 | 0 | - |
| tests/net/fods | 157 | 0 | 0 | - |
| tests/net/fodt | 145 | 0 | 0 | - |
| **TOTAL** | **3984** | **2 (pre-existing)** | **13** | |

AUTHORITATIVE_TEST_RESULT: 3984 passed, 2 pre-existing failed, 13 skipped.

## Compared to R38 Baseline

- R38 baseline: 2215 passed, 4 skipped
- R40: 3984 passed (+1769), 13 skipped
- Growth includes skills suite, AI runner, evidence guards, and fods/fodt suite additions

## Gate Status

- FODS Python: Gates 1-10 PASSED. Gate 11 G11-G NOT_STARTED (awaiting Babar Raza).
- FODT Python: Gates 1-10 PASSED. Gate 11 G11-G NOT_STARTED (awaiting Babar Raza).
- FODS .NET: Gate 11 G11-E complete, G11-F in_progress, G11-G NOT_STARTED.
- FODT .NET: Gate 11 G11-E complete, G11-F in_progress, G11-G NOT_STARTED.

commercial_product_ready: false (all formats — G11-G approval required).
