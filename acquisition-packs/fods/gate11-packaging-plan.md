---
artifact_id: fods-gate11-packaging-plan
artifact_type: acquisition-pack
path: acquisition-packs/fods/gate11-packaging-plan.md
format_id: fods
visibility: internal
generated_by: claude-sonnet-4-6
generated_at: "2026-05-12"
notes: "FODS Gate 11 .NET commercial packaging plan. DEC033-OPTION-B-GATE11-COMMERCIAL-SWARM-001."
---

# FODS Gate 11 — .NET Commercial Packaging Plan

**Format:** FODS (Flat OpenDocument Spreadsheet)
**Gate:** 11 — Commercial Readiness
**Date:** 2026-05-12
**Status:** SKELETON — not release-ready

## Package Identity

- Package ID: `FormatFactory.Fods`
- Namespace: `FormatFactory.Fods`
- Target framework: net10.0 LTS
- Assembly: `FormatFactory.Fods.dll`
- Initial release version: 0.1.0 (after Gate 11 approval)

## DEC-033 Option B Notes

- Commercial-only .NET package
- No .NET FOSS variant
- Python FOSS package (`format-factory-fods`, Apache-2.0) is the independent FOSS track

## SDK Note

Current installed SDK: 9.0.200 (cannot target net10.0)
Required SDK: .NET 10 SDK (install from https://aka.ms/dotnet/download)
DOTNET_SDK_BLOCKER: .NET 10 SDK must be installed before builds can be verified

## Feature Scope (Target for Gate 11 Approval)

Per tier-map.yaml (acquisition-packs/fods/tier-map.yaml):

| Tier | Features | Status |
|------|---------|--------|
| Tier 0 | Structural parsing, sheet enumeration, cell access | SKELETON (not implemented) |
| Tier 1 | Formula metadata, named ranges | NOT STARTED |
| Tier 2 | Styles metadata, chart metadata | NOT STARTED |

Gate 11 minimum scope: Tier 0 complete + basic test suite

## Source Structure

```
src/net/fods/
  FormatFactory.Fods.csproj   (skeleton — net10.0 target)
  FodsParser.cs                (skeleton — GetSheetNames() XML validation only)
  README.md                    (this context)
```

## CI/CD Plan (Phase 4+)

- NuGet package build via `dotnet pack`
- GitHub Actions workflow (Phase 4+ authorization required)
- .NET 10 SDK required for CI agent

## What Remains for Gate 11

1. .NET 10 SDK installation (machine blocker)
2. Full Tier 0 implementation
3. Test project (`tests/net/fods/`)
4. NuGet package metadata finalized
5. Commercial license confirmed
6. DEC-034 independent verification (separate session)
7. Explicit Gate 11 human approval

PACKAGING_PLAN_STATUS: skeleton_documented
