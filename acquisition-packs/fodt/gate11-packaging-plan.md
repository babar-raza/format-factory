---
artifact_id: fodt-gate11-packaging-plan
artifact_type: acquisition-pack
path: acquisition-packs/fodt/gate11-packaging-plan.md
format_id: fodt
visibility: internal
generated_by: claude-sonnet-4-6
generated_at: "2026-05-12"
notes: "FODT Gate 11 .NET commercial packaging plan. DEC033-OPTION-B-GATE11-COMMERCIAL-SWARM-001."
---

# FODT Gate 11 — .NET Commercial Packaging Plan

**Format:** FODT (Flat OpenDocument Text)
**Gate:** 11 — Commercial Readiness
**Date:** 2026-05-12
**Status:** SKELETON — not release-ready

## Package Identity

- Package ID: `FormatFactory.Fodt`
- Namespace: `FormatFactory.Fodt`
- Target framework: net10.0 LTS
- Assembly: `FormatFactory.Fodt.dll`
- Initial release version: 0.1.0 (after Gate 11 approval)

## DEC-033 Option B Notes

- Commercial-only .NET package
- No .NET FOSS variant
- Python FOSS package (`format-factory-fodt`, Apache-2.0) is the independent FOSS track

## SDK Note

Current installed SDK: 9.0.200 (cannot target net10.0)
Required SDK: .NET 10 SDK (install from https://aka.ms/dotnet/download)
DOTNET_SDK_BLOCKER: .NET 10 SDK must be installed before builds can be verified

## Algorithm Reference

The .NET implementation should mirror the Python FOSS implementation approach:
- Iterative DFS list traversal (see src/python/fodt/list_traversal.py)
- Iterparse streaming (see src/python/fodt/parser.py)
- Neutral model: schemas/neutral-model/fodt/ (7 entities: Document/Block/List/ListItem/Table/TableRow/TableCell)

## Feature Scope (Target for Gate 11 Approval)

Per tier-map.yaml (acquisition-packs/fodt/tier-map.yaml):

| Tier | Features | Status |
|------|---------|--------|
| Tier 0 | Structural parsing, paragraph enumeration, word count | SKELETON |
| Tier 1 | List traversal, table parsing | NOT STARTED |
| Tier 2 | Heading outline levels, metadata extraction | NOT STARTED |

## Source Structure

```
src/net/fodt/
  FormatFactory.Fodt.csproj   (skeleton — net10.0 target)
  FodtParser.cs                (skeleton — GetParagraphCount() XML validation only)
  README.md                    (this context)
```

## What Remains for Gate 11

1. .NET 10 SDK installation (machine blocker)
2. Full Tier 0 implementation
3. Test project (`tests/net/fodt/`)
4. NuGet package metadata finalized
5. Commercial license confirmed
6. DEC-034 independent verification (separate session)
7. Explicit Gate 11 human approval

PACKAGING_PLAN_STATUS: skeleton_documented
