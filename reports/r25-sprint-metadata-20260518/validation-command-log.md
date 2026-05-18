# R25 Sprint Validation Command Log (Sprint Metadata Copy)
# Sprint: FORMAT-FACTORY-R25-AI-PHASE1-GATE4-FORWARD-TRAIN-AND-R24-METADATA-SYNC-001
# Date: 2026-05-18
# Source: reports/testing/r25-validation-command-log-20260518.md

## Python Full Suite
```
PYTHONPATH=/c/Users/prora/AppData/Roaming/Python/Python313/site-packages:. \
  python -m pytest tests/ --ignore=tests/net -q --tb=no
```
Result: 2039 passed, 13 skipped, 0 failed (471.47s)

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

AUTHORITATIVE_TEST_RESULT: 2267 passed, 13 skipped, 0 failed
DOTNET_FODS_RESULT: 120/120 PASS
DOTNET_FODT_RESULT: 108/108 PASS
