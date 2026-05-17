---
artifact_id: fods-gate11-nuget-package-plan
artifact_type: acquisition-pack
path: acquisition-packs/fods/gate11-nuget-package-plan.md
format_id: fods
gate: "G11-C"
sprint: FORMAT-FACTORY-R21-FOSS-RELEASE-READINESS-AND-GATE11-COMMERCIAL-PREEXECUTION-TRAIN-001
date: "2026-05-17"
status: package_plan_complete
visibility: internal
---

# FODS Gate 11 G11-C — NuGet Package Plan

## Status

**G11-C: package_plan_complete**

Note: Package names below are provisional. Final naming authority requires Babar Raza confirmation.
No package has been built or published. No credentials created. No version tags.

## Proposed Package Identity

| Field | Provisional Value | Notes |
|-------|------------------|-------|
| Package ID | `FormatFactory.Fods` | Provisional — awaits naming authority |
| Namespace | `Aspose.FormatFactory.Fods` | Or `FormatFactory.Fods` without Aspose prefix |
| Version (first preview) | `0.1.0-alpha.1` | semver pre-release |
| TargetFramework | `net8.0`, `net9.0` | Match existing .NET SDK |
| License | Proprietary Commercial | See gate11-commercial-licensing.md |

## Package Contents

```
FormatFactory.Fods/
  src/net/fods/          (current C4-C6 source)
  FormatFactory.Fods.csproj
  FormatFactory.Fods.nuspec (generated)
```

## Version Scheme

- `0.1.0-alpha.1` — first internal preview (G11-D demonstrated, G11-E not yet implemented)
- `0.1.0-beta.1` — after G11-E conversion capability implemented
- `1.0.0` — after G11-G final human approval and G11-F packaging complete

## Dependencies

- No third-party NuGet packages
- No commercial SDK dependencies
- .NET runtime: MIT license (compatible with proprietary commercial product)

## Build Prerequisites (Not Yet Satisfied)

1. G11-E: C7+ conversion capability must be implemented (NOT yet authorized)
2. G11-F: CI/CD pipeline and NuGet pack automation
3. G11-G: Final human approval (Babar Raza)
4. License header in all .NET source files

## What This Plan Does NOT Authorize

- No `dotnet pack` or `dotnet nuget push`
- No NuGet.org account creation
- No package signing
- No commercial_product_ready=true
- commercial_product_ready remains false

## G11-C Status

STATUS: package_plan_complete
