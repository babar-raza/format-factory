# R79 Train I — .NET Test Project Verification

**sprint_id:** FORMAT-FACTORY-R79-PACKAGE-SOURCE-SYNC-FIRST-REAL-FODS-PRODUCT-RC-ZST-DEPENDENCY-REPLAY-MEGA-TRAIN-001
**date:** 2026-05-30
**train:** I

## D78-14: .NET No Test Projects — RECLASSIFIED

### R78 IV Finding
> "No `.csproj` test project files found in `src/net/fods/` or `src/net/fodt/`."
> DOTNET_UNTESTED: CONFIRMED — D78-14

### R79 Verification Result

The .NET test project files exist — but in `tests/net/` (not `src/net/`):

| Path | Status |
|---|---|
| `tests/net/fods/FormatFactory.Fods.Tests.csproj` | EXISTS |
| `tests/net/fodt/FormatFactory.Fodt.Tests.csproj` | EXISTS |

Both are xUnit test projects targeting `net10.0` with `ProjectReference` to the
respective source projects in `src/net/fods/` and `src/net/fodt/`.

### Test Files Present

FODS tests (`tests/net/fods/`):
- FodsC7C8RoundtripPreservationTests.cs
- FodsC9ExportConversionReadinessTests.cs
- FodsCsvExporterTests.cs
- FodsDocumentEditTests.cs
- FodsDocumentRoundtripTests.cs
- FodsEditSaveTests.cs
- FodsG11fMalformedXmlGuardTests.cs
- FodsHtmlExporterTests.cs
- FodsJsonExporterTests.cs
- FodsMultiSheetHardeningTests.cs
- FodsParserTests.cs
- FodsR73MergedCellParityTest.cs
- FodsRoundtripOracleTests.cs

FODT tests (`tests/net/fodt/`):
- FodtC7C8RoundtripPreservationTests.cs
- FodtC9ExportConversionReadinessTests.cs
- FodtDocumentEditTests.cs
- FodtDocumentRoundtripTests.cs
- FodtEditSaveTests.cs
- FodtG11fHeadingAndGuardTests.cs
- FodtHtmlExporterTests.cs
- FodtMarkdownExporterTests.cs
- FodtParserTests.cs
- FodtRoundtripOracleTests.cs
- FodtTxtExporterTests.cs
- FodtUnicodeHardeningTests.cs

### R74 Test Count (authoritative)
Per R74 sprint: .NET 306 tests across both projects.

## D78-14 Reclassification

| Status | Before | After |
|---|---|---|
| D78-14 | CONFIRMED | RECLASSIFIED_FALSE_POSITIVE |

**Root cause of false positive:** R78 IV searched `src/net/fods/` and `src/net/fodt/`.
The test projects reside in `tests/net/fods/` and `tests/net/fodt/` per the project's
source layout convention (source in `src/`, tests in `tests/`).

DOTNET_TEST_PROJECTS: VERIFIED_EXIST
D78_14: RECLASSIFIED_FALSE_POSITIVE
TRAIN_I_STATUS: COMPLETE
