# Test Meaningfulness Rubric

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Purpose

Scores the quality and meaningfulness of the test suite — not just coverage metrics but
whether tests prove the product works in ways users actually care about.

---

## Test Quality Levels (TQ-0 through TQ-5)

| Level | Label | Description |
|-------|-------|-------------|
| **TQ-0** | No tests | Test files absent or empty |
| **TQ-1** | Smoke only | Import test; basic instantiation; no behavior verified |
| **TQ-2** | Happy path only | Tests prove the feature works for one clean example |
| **TQ-3** | Behavioral tests | Tests prove behavior for multiple scenarios; error cases included |
| **TQ-4** | Product-proving | Roundtrip tests; edge cases; malformed input; integration |
| **TQ-5** | Product-confident | Full property coverage; performance; regression suite; installed-package tests |

---

## Test Quality Dimensions

### TQ-D1: Test Organization

How easy is it to understand what is being tested from test file and method names?

| Score | Criteria |
|-------|---------|
| 0 | No tests |
| 1 | Tests named by sprint (R87, R100) — no feature visibility |
| 2 | Mix of sprint-named and feature-named |
| 3 | Mostly feature-named (e.g. SheetCrudTests, CellStyleTests) |
| 4 | Feature-organized; methods follow Given_When_Then or test_feature_condition pattern |
| 5 | Test suite reads as executable specification; fully navigable |

### TQ-D2: Test Scenario Coverage

What percentage of documented features have at least one test?

| Score | Criteria |
|-------|---------|
| 0 | 0% |
| 1 | < 25% of features tested |
| 2 | 25–50% |
| 3 | 50–75% |
| 4 | 75–90% |
| 5 | > 90% |

### TQ-D3: Error Path Coverage

Do tests exercise failure modes (malformed input, file not found, wrong type, null)?

| Score | Criteria |
|-------|---------|
| 0 | No error path tests |
| 1 | One or two error cases; not systematic |
| 2 | Common error cases covered |
| 3 | All documented error modes tested |
| 4 | Error tests use expected-exception assertions; messages verified |
| 5 | Security/fuzz tests; malformed XML/binary; oversized input; encoding attacks |

### TQ-D4: Roundtrip Tests

Do tests verify load → edit → save → reload produces identical results?

| Score | Criteria |
|-------|---------|
| 0 | No roundtrip tests |
| 1 | Save-only test (no reload) |
| 2 | Save + reload; equality checked for a single value |
| 3 | Full roundtrip with multiple assertions |
| 4 | Roundtrip for multiple features (cells, styles, formulas, sheets) |
| 5 | Roundtrip for all features; binary-identical output where format allows |

### TQ-D5: Public API Dogfooding

Do tests use the public API surface (not internal implementation details)?

| Score | Criteria |
|-------|---------|
| 0 | Tests import private classes directly |
| 1 | Tests mix public and private access |
| 2 | Tests mostly use public API |
| 3 | Tests use only public API; no reflection or private access |
| 4 | Tests match what a real user would write |
| 5 | Tests can be published as example code; they ARE the documentation |

---

## Test Meaningfulness Scores

### .NET Products

| Product | TQ-D1 | TQ-D2 | TQ-D3 | TQ-D4 | TQ-D5 | TQ Level |
|---------|-------|-------|-------|-------|-------|----------|
| FODS | 2 | 4 | 4 | 4 | 4 | TQ-3 |
| FODT | 2 | 4 | 4 | 4 | 4 | TQ-3 |
| NetPBM | 2 | 4 | 4 | 4 | 4 | TQ-3 |
| NDJSON | 3 | 3 | 2 | 2 | 3 | TQ-2 |
| CSV | 3 | 2 | 1 | 1 | 3 | TQ-2 |
| TSV | 3 | 2 | 2 | 1 | 3 | TQ-2 |
| ZST | 3 | 2 | 2 | 0 | 3 | TQ-2 |

### Python Products

| Product | TQ-D1 | TQ-D2 | TQ-D3 | TQ-D4 | TQ-D5 | TQ Level |
|---------|-------|-------|-------|-------|-------|----------|
| FODS | 3 | 4 | 3 | 3 | 3 | TQ-3 |
| FODT | 3 | 4 | 3 | 3 | 3 | TQ-3 |
| PBM | 4 | 4 | 5 | 3 | 4 | TQ-4 |
| ODS | 3 | 3 | 2 | 3 | 3 | TQ-3 |
| ZST | 3 | 3 | 2 | 3 | 3 | TQ-3 |
| NDJSON | 3 | 3 | 2 | 2 | 3 | TQ-3 |
| FODP | 2 | 2 | 1 | 0 | 2 | TQ-1 |

---

## Key Test Quality Issues

### Issue 1: Sprint-Named Test Files (FODS .NET, FODT .NET, NetPBM .NET)

Files like `FodsR87ProductDeepening.cs`, `FodsR100AddSheetTests.cs` are sprint artifacts.
**Impact:** A developer wanting to find "all tests for cell merge" cannot navigate the suite.
**Fix:** Rename to `FodsSheetCrudTests.cs`, `FodsCellMergeTests.cs`, etc.
**Effort:** L (100+ test files, refactor risk)

### Issue 2: No ZST .NET Roundtrip Tests

ZST .NET has no compress capability, so roundtrip tests are impossible.
**Fix:** Add ZstWriter (Phase E pilot), then add roundtrip tests.

### Issue 3: FODP Python Tests Are Smoke-Only

FODP is read-only. Tests verify `get_page_count()` returns a number.
No error path tests. No format validation.
**Fix:** Add malformed file test, empty file test, binary corruption test.

### Issue 4: Test Suite Volume vs Test Meaningfulness

FODS .NET has 638 tests across 73 files — but many are sprint-incremental variations
of the same scenario. High volume does not equal high coverage.
**Recommendation:** Audit for test deduplication; remove trivially redundant tests.

---

## Test Meaningfulness Bands

| TQ Level | Band |
|----------|------|
| TQ-0 | No confidence |
| TQ-1 | Smoke confidence only |
| TQ-2 | Happy-path confidence |
| TQ-3 | Behavioral confidence |
| TQ-4 | Product-level confidence |
| TQ-5 | Commercial-grade confidence |
