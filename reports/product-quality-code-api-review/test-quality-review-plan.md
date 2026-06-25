# Test Quality Review Plan

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Test Quality Classification (TQ-0 through TQ-5)

| Level | Meaning |
|-------|---------|
| **TQ-0** | No tests |
| **TQ-1** | Smoke only (does it import? does it not crash?) |
| **TQ-2** | Happy path only (one clean input, one expected output) |
| **TQ-3** | Useful behavior tests (multiple inputs, some structure) |
| **TQ-4** | Behavior + edge + error + output tests |
| **TQ-5** | Strong product-confidence suite (comprehensive coverage, roundtrip, security, performance guard) |

---

## Test Quality Dimensions

For each format's test suite, evaluate:

1. **Coverage breadth**: Are all public API methods tested?
2. **Happy path quality**: Do happy path tests use realistic inputs?
3. **Edge case coverage**: Empty input? Single row? Maximum size? Unicode?
4. **Error case coverage**: Malformed input? File not found? Wrong type?
5. **Roundtrip verification**: Load → edit → save → reload → assert?
6. **Output format verification**: Does the test verify the actual output content, not just "no exception"?
7. **Naming clarity**: Can a developer navigate which feature a test covers?
8. **Sprint-naming anti-pattern**: Tests named by sprint (R87, R100) instead of feature?
9. **Test isolation**: Tests self-contained? Or depend on file system state?
10. **Test meaningfulness**: Does the test actually verify product behavior, or does it just call the function and check no exception is thrown?

---

## Known Test Quality Issues

### Issue 1: Sprint-Named Test Files (PQ-017)
```
tests/net/fods/FodsR87ProductDeepening.cs
tests/net/fods/FodsR100AddSheetTests.cs
tests/net/fods/FodsR105SortRowsTests.cs
... (32+ sprint cycles for FODS .NET alone)
```

**Problem:** A developer looking for "sort row tests" must guess which sprint added that feature.
**Impact:** MEDIUM — tests work fine for CI, but poor discoverability for maintenance.
**Fix:** Rename test files to feature names: `FodsSheetSortTests.cs`, `FodsSheetCRUDTests.cs`, etc.

### Issue 2: Scope of Tests vs Claims
- 2962+ test files across the project
- Large volume does NOT guarantee comprehensive behavior coverage
- Many sprint tests verify that the FUNCTION RUNS, not that output is CORRECT
- Need to verify: do roundtrip tests actually reload and assert expected values?

### Issue 3: Happy-Path Bias
- Sprint-driven development adds features and their immediate happy-path tests
- Edge cases (malformed input, unicode, zero-length, maximum size) often added in dedicated "hardening" sprints
- Need to check: are edge cases present for each format or only for high-attention formats?

### Issue 4: Missing Tests for Some Products
- ZST .NET: Only 2 test files (out of the entire project)
- CSV .NET: Only 4 test files
- NDJSON .NET: Only 6 test files
- QOI Python: Only 5 test files estimate
- These thin test suites suggest thin products

---

## Test Directories to Review

### .NET Tests
```
tests/net/fods/        (~73 files)  — highest priority
tests/net/fodt/        (~65 files)  — high priority
tests/net/netpbm/      (~65 files)  — high priority
tests/net/ndjson/      (~6 files)   — thin
tests/net/csv/         (~4 files)   — thin
tests/net/tsv/         (~6 files)   — thin
tests/net/zst/         (~2 files)   — very thin
tests/net/html/        (~1 file)    — minimal
```

### Python Tests
```
tests/python/fods/           tests/python/fodt/
tests/python/ods/            tests/python/odt/
tests/python/pbm/            tests/python/pgm/
tests/python/ppm/            tests/python/qoi/
tests/python/xcf/            tests/python/zst/
tests/python/sylk/           tests/python/dif/
tests/python/csv_format/     tests/python/ndjson/
tests/python/toml_format/    tests/python/tsv/
tests/python/gnumeric/       tests/python/abw/
tests/python/fodg/           tests/python/fodp/
```

---

## Test Quality Scoring Method

For each product test suite:

**Step 1: Count test files**
- How many test files? How many test methods (estimate)?

**Step 2: Classify test file names**
- How many are sprint-named (R87, R100, R115, etc.)?
- How many are feature-named (FodsSheetCRUDTests, etc.)?
- Sprint-name ratio = sprint_named / total

**Step 3: Sample test quality**
- Pick 3 random test files
- Classify each test: smoke/happy-path/edge/error/roundtrip
- What fraction are merely "call function, assert no exception"?

**Step 4: Check roundtrip tests**
- Load → edit → save → reload → assert value?
- Are roundtrip tests present for EVERY major edit operation?

**Step 5: Check error tests**
- Are there tests for: malformed input, empty input, file not found, wrong type?
- Do error tests assert the SPECIFIC exception type (FodsDocumentException, not just Exception)?

**Step 6: Score TQ**
- TQ-0: no tests
- TQ-1: < 5 test methods, smoke only
- TQ-2: happy path tests only, no edge/error
- TQ-3: happy + some edge OR error cases
- TQ-4: happy + edge + error + at least one roundtrip
- TQ-5: all of TQ-4 + feature-named tests + output verification + security tests

---

## Test Quality Estimates

| Product | Test Files Est. | Sprint-Named? | Roundtrip? | Edge Cases? | Error Tests? | TQ Estimate |
|---------|----------------|--------------|------------|-------------|--------------|-------------|
| FODS .NET | 73 | Mostly | Yes | Some | Yes | TQ-3-4 |
| FODT .NET | 65 | Mostly | Yes | Some | Yes | TQ-3-4 |
| NetPBM .NET | 65 | Mostly | Yes | Some | Yes | TQ-3-4 |
| NDJSON .NET | 6 | Mixed | Unknown | Minimal | Minimal | TQ-2-3 |
| CSV .NET | 4 | Mixed | Unknown | Minimal | Minimal | TQ-2 |
| TSV .NET | 6 | Mixed | Unknown | Minimal | Minimal | TQ-2 |
| ZST .NET | 2 | Unknown | No | Minimal | Minimal | TQ-2 |
| FODS Python | Many | Some | Yes | Some | Some | TQ-3-4 |
| FODT Python | Many | Some | Yes | Some | Some | TQ-3-4 |
| PBM Python | ~10 | No | Unknown | Yes | Yes (hierarchy) | TQ-4 |
| FODP Python | ~5 | No | No | Minimal | Minimal | TQ-2 |
| QOI Python | ~5 | No | Unknown | Minimal | Minimal | TQ-2 |

---

## Test Naming Classification Examples

**Sprint-named (anti-pattern):**
- `FodsR87ProductDeepening.cs` — what features does this test? Unknown without reading.
- `FodsR100AddSheetTests.cs` — sprint 100 added sheets. OK but "AddSheet" is in the name.
- `FodsR105SortRowsTests.cs` — sprint 105 added sorting. Partially informative.
- `test_r115_sylk_write_roundtrip.py` — informative despite sprint prefix.

**Feature-named (preferred):**
- `FodsDocumentEditTests.cs` — clearly tests document editing
- `FodsSheetCrudTests.cs` — tests sheet CRUD
- `NetpbmR117DocumentTests.cs` — mixed (sprint + feature)

**Assessment:** Most test files are sprint-named. This is a navigation problem for developers discovering what's tested.
