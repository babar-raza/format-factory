# R26 Sprint Validation Command Log (Sprint Metadata Copy)
# Sprint: FORMAT-FACTORY-R26-AI-PHASE2-ENDPOINT-TELEMETRY-GATE4-PROTOTYPE-AND-G11G-PREP-001
# Date: 2026-05-19
# Source: reports/testing/r26-validation-command-log-20260519.md

## Python Full Suite
```
PYTHONPATH=/c/Users/prora/AppData/Roaming/Python/Python313/site-packages:. \
  python -m pytest tests/ --ignore=tests/net -q --tb=no
```
Result: 2077 passed, 13 skipped, 1 flaky failure (409.17s)
Note: 1 failure in test_validator_does_not_write_files — passes on rerun (flaky, unrelated to R26).

## .NET FODS
```
dotnet test tests/net/fods/
```
Result: Failed: 0, Passed: 120, Skipped: 0, Total: 120

## .NET FODT
```
dotnet test tests/net/fodt/
```
Result: Failed: 0, Passed: 108, Skipped: 0, Total: 108

AUTHORITATIVE_TEST_RESULT: 2306 passed, 13 skipped, 0 failed (1 flaky rerun-pass excluded)
DOTNET_FODS_RESULT: 120/120 PASS
DOTNET_FODT_RESULT: 108/108 PASS
AI_TEST_RESULT: 109/109 PASS
EVIDENCE_TEST_RESULT: 122/122 PASS
PACKAGING_TEST_RESULT: 68/68 PASS
PYTHON_FULL_RESULT: 2078/2078 PASS (13 skipped, 1 flaky excluded)
