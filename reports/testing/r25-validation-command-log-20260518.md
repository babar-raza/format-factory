# R25 Validation Command Log
# Sprint: FORMAT-FACTORY-R25-AI-PHASE1-GATE4-FORWARD-TRAIN-AND-R24-METADATA-SYNC-001
# Date: 2026-05-18
# Gate: 8 — Full validation

## Commands Executed

### Python Full Suite (all tests including AI, evidence, packaging)
```
PYTHONPATH=/c/Users/prora/AppData/Roaming/Python/Python313/site-packages:. \
  python -m pytest tests/ --ignore=tests/net -q --tb=no
```
Result: **2039 passed, 13 skipped, 0 failed** (471.47s)

### Python AI + Evidence (spot check)
```
PYTHONPATH=... python -m pytest tests/ai/ tests/evidence/ -q --tb=short
```
Result: 192 passed, 29 warnings

### .NET FODS Tests
```
dotnet test tests/net/fods/
```
Result: **Failed: 0, Passed: 120, Skipped: 0, Total: 120** (108 ms)
(+8 new: FodsG11fMalformedXmlGuardTests)

### .NET FODT Tests
```
dotnet test tests/net/fodt/
```
Result: **Failed: 0, Passed: 108, Skipped: 0, Total: 108** (100 ms)
(+8 new: FodtG11fHeadingAndGuardTests)

## Summary Table

| Suite | Tests | Status |
|-------|-------|--------|
| Python full (all) | 2039 | 2039/2039 PASS (13 skip) |
| tests/ai | 70 | 70/70 PASS |
| tests/evidence | 122 | 122/122 PASS |
| tests/packaging | 68 | 68/68 PASS |
| .NET FODS | 120 | 120/120 PASS |
| .NET FODT | 108 | 108/108 PASS |
| **TOTAL (Python+.NET)** | **2267** | **2267/2267 PASS** |

## Delta From R24 Baseline

| Suite | R24 | R25 | Delta |
|-------|-----|-----|-------|
| Python full | 2039 | 2039 | 0 (same suite scope) |
| tests/ai | 70 | 70 | 0 (pre-existing) |
| tests/evidence | 122 | 122 | 0 |
| tests/packaging | 68 | 68 | 0 |
| .NET FODS | 112 | 120 | +8 (G11-F guard) |
| .NET FODT | 100 | 108 | +8 (G11-F heading+guard) |

AUTHORITATIVE_TEST_RESULT: 2267 passed, 13 skipped, 0 failed
DOTNET_FODS_RESULT: 120/120 PASS
DOTNET_FODT_RESULT: 108/108 PASS
AI_TEST_RESULT: 70/70 PASS
EVIDENCE_TEST_RESULT: 122/122 PASS
PACKAGING_TEST_RESULT: 68/68 PASS
PYTHON_FULL_RESULT: 2039/2039 PASS (13 skipped)

**Gate 8 — PASS**
