# Build Verification (TC-F-002)
Sprint: FORMAT-FACTORY-MAINSTREAM-R114-PRODUCT-EXECUTION-DIRTY-STATE-COMMIT-AND-BREADTH-SPRINT-001
Generated: 2026-06-04

## Build Order Confirmed

| Step | Taskcard | Result | Log |
|------|---------|--------|-----|
| 1. dotnet build (all 3 projects) | TC-A-003 | Build succeeded, 0 warnings, 0 errors | reports/mainstream-r114/raw-logs/dotnet-build.log |
| 2. dotnet test (all 3 projects) | TC-A-004 | 1423 passed, 0 failed | reports/mainstream-r114/raw-logs/dotnet-test-with-build.log |
| 3. Pipeline method added to NetpbmImage.cs | TC-C-002 | AFTER build gate | source edit |
| 4. dotnet test (Pipeline only) | TC-C-002 | 9 passed, 0 failed (fresh compile) | reports/mainstream-r114/raw-logs/netpbm-pipeline-tests.log |

## No stale --no-build Contamination

All dotnet test runs used implicit build (no --no-build flag).
Build log confirms: FormatFactory.Fods.dll, FormatFactory.Fodt.dll, FormatFactory.Netpbm.dll
all rebuilt from current uncommitted source.

## Compiled Binary Sources

| Binary | Source State |
|--------|-------------|
| FormatFactory.Fods.dll | Compiled from uncommitted FodsDocument.cs (+868 lines since R93) |
| FormatFactory.Fodt.dll | Compiled from uncommitted FodtDocument.cs (+482 lines since R93) |
| FormatFactory.Netpbm.dll | Compiled from uncommitted NetpbmImage.cs (+1127 pre-R114 + Pipeline R114 addition) |

## Test Counts Authoritative

| Suite | Tests (compiled) | Failed |
|-------|-----------------|--------|
| FODS .NET | 507 | 0 |
| FODT .NET | 493 | 0 |
| Netpbm .NET | 423 (R94-R113) + 9 (R114 Pipeline) = 432 after R114 | 0 |

Note: The Netpbm post-R114 count is 432 total (423 pre-existing + 9 new Pipeline tests).

## Build Verification: PASS
