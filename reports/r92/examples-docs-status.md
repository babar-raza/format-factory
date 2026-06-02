---
sprint: R92
generated_by: r92-worker
---

# Examples/Docs Status (Train U)

Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

## New APIs (R92)

| API | Skill | Example Coverage |
|-----|-------|-----------------|
| `FodsDocument.GetSheetNames()` | /add-dotnet-api | 8 unit tests in FodsR92GetSheetNamesTests.cs |
| `FodtDocument.GetHeadingParagraphs()` | /add-dotnet-api | 8 unit tests in FodtR92GetHeadingParagraphsTests.cs |
| `NetpbmImage.FillRegion()` | /add-dotnet-api | 8 unit tests in NetpbmR92FillRegionTests.cs |

## Standalone Example Status

- `examples/net/` directory exists (created in prior sprint)
- New standalone examples for GetSheetNames/GetHeadingParagraphs/FillRegion deferred to R93
  - Reason: `/add-installed-package-example` skill requires installed .NET package; NuGet packaging not yet in place
  - Unit tests serve as executable examples for now

## Documentation

- API behaviors documented in source XML comments (`/// <summary>` blocks)
- Skill execution proofs: `reports/r92/skill-driven-execution-proof.md` (Train K)
- Governed product work reports: Trains L, M, N

## Status: UNIT TESTS AS EXAMPLES — STANDALONE EXAMPLES DEFERRED TO R93
