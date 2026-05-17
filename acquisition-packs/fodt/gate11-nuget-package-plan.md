---
artifact_id: fodt-gate11-nuget-package-plan
artifact_type: acquisition-pack
path: acquisition-packs/fodt/gate11-nuget-package-plan.md
format_id: fodt
gate: "G11-C"
sprint: FORMAT-FACTORY-R21-FOSS-RELEASE-READINESS-AND-GATE11-COMMERCIAL-PREEXECUTION-TRAIN-001
date: "2026-05-17"
status: package_plan_complete
visibility: internal
---

# FODT Gate 11 G11-C — NuGet Package Plan

## Status

**G11-C: package_plan_complete**

Note: Package names are provisional. Naming authority requires Babar Raza confirmation.
No package built or published. No credentials created.

## Proposed Package Identity

| Field | Provisional Value | Notes |
|-------|------------------|-------|
| Package ID | `FormatFactory.Fodt` | Provisional |
| Namespace | `Aspose.FormatFactory.Fodt` | Or `FormatFactory.Fodt` |
| Version (first preview) | `0.1.0-alpha.1` | semver pre-release |
| TargetFramework | `net8.0`, `net9.0` | Match FODS package |
| License | Proprietary Commercial | See gate11-commercial-licensing.md |

## Package Contents

```
FormatFactory.Fodt/
  src/net/fodt/          (current C4-C6 source)
  FormatFactory.Fodt.csproj
  FormatFactory.Fodt.nuspec (generated)
```

## Version Scheme

- `0.1.0-alpha.1` — first internal preview
- `0.1.0-beta.1` — after G11-E conversion capability (FODT→DOCX or FODT→PDF)
- `1.0.0` — after G11-G final human approval

## Dependencies

- No third-party NuGet packages
- No commercial SDK dependencies

## Build Prerequisites (Not Yet Satisfied)

Same as FODS: G11-E implementation, G11-F CI/CD, G11-G human approval.

## What This Plan Does NOT Authorize

Same as FODS: no dotnet pack/push, no NuGet account, no commercial_product_ready=true.

## G11-C Status

STATUS: package_plan_complete
