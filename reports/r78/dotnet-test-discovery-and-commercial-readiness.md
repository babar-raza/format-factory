# R78 .NET Test Discovery and Commercial Readiness

**sprint_id:** FORMAT-FACTORY-R78-TRUE-STATE-AND-FIRST-PRODUCT-FINISH-REPRODUCIBILITY-MEGA-TRAIN-001
**date:** 2026-05-30
**train:** M

## .NET Source State

| Format | Source Path | Files | Tests |
|---|---|---|---|
| FODS | src/net/fods/ | FodsDocument.cs, FodsParser.cs, FodsWriter.cs, FodsDocument.csproj | NONE |
| FODT | src/net/fodt/ | FodtDocument.cs, FodtParser.cs, FodtWriter.cs, FodtDocument.csproj | NONE |

## Test Gap Analysis

The .NET FODS and FODT commercial source has NO test projects. This was identified as
D77-12 (MAJOR defect) by the supervisor.

Per DEC-033 (.NET FOSS packaging deferred) and DEC-032 (.NET = commercial/full-feature path),
the .NET track is a commercial product prototype. However, having zero tests for commercial
source is an unacceptable state.

## .NET Test Discovery Assessment

| Item | Status |
|---|---|
| dotnet SDK available | YES (10.0.204) |
| FODS .csproj builds | YES (validated in prior sprints) |
| FODT .csproj builds | YES (validated in prior sprints) |
| FODS test project | MISSING |
| FODT test project | MISSING |
| xUnit installed | Not applicable (no test project) |
| Test runner configured | Not applicable |

## Commercial Readiness State

| Dimension | FODS | FODT |
|---|---|---|
| C# source (Load/Save/Edit) | YES (C4-C6-vertical-slice) | YES (C4-C6-vertical-slice) |
| G11-A through G11-E | COMPLETE (prototype) | COMPLETE (prototype) |
| Unit tests | MISSING | MISSING |
| Integration tests | MISSING | MISSING |
| NuGet package | Local only (.local/package-builds/r23-nuget/) | Local only |
| Gate 11-G (human approval) | NOT_STARTED | NOT_STARTED |
| commercial_product_ready | false | false |

## R78 Action

R78 does NOT create .NET test projects (out of scope for a single train).
This train documents the gap and defines requirements for R79.

Required for R79 (.NET test remediation):
1. Create `src/net/fods/tests/FormatFactory.Fods.Tests.csproj`
2. Add basic xUnit tests: Parse, Edit cell, Write, Round-trip
3. Create `src/net/fodt/tests/FormatFactory.Fodt.Tests.csproj`
4. Add basic xUnit tests: Parse, Edit block, Write, Round-trip
5. Run `dotnet test` and capture raw log

## .NET Raw Log Summary (R78)

Since no .NET test project exists, the .NET raw log for R78 is:
```
DOTNET_TEST_RESULT: NO_TESTS (test project missing)
DOTNET_CSPROJ_BUILD: PASS (csproj files build without errors)
DOTNET_TEST_GAP: MAJOR (gap documented in D77-12)
```

DOTNET_TEST_DISCOVERY: COMPLETE (gap documented)
DOTNET_COMMERCIAL_READINESS: NOT_READY (no tests, Gate 11-G not started)
