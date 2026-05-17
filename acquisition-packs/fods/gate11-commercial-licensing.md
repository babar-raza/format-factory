---
artifact_id: fods-gate11-commercial-licensing
artifact_type: acquisition-pack
path: acquisition-packs/fods/gate11-commercial-licensing.md
format_id: fods
visibility: internal
generated_by: claude-sonnet-4-6
generated_at: "2026-05-12"
notes: "FODS Gate 11 commercial licensing note. DEC033-OPTION-B-GATE11-COMMERCIAL-SWARM-001."
---

# FODS Gate 11 — Commercial Licensing

**Format:** FODS (Flat OpenDocument Spreadsheet)
**Gate:** 11 — Commercial Readiness
**Date:** 2026-05-12

## Underlying Spec License

- Spec body: OASIS
- Spec: ODF 1.3 Part 3 (Schema)
- Legal category: 1 — Open Standard (Royalty-Free)
- Patent waived: YES (OASIS RF policy)
- Implementation: Permitted without license fee

## Commercial Product License

- Product: FormatFactory.Fods (NuGet package)
- DEC-033 Option B: .NET Commercial Only
- Proposed commercial license: Proprietary Commercial License
- License decision: PENDING Gate 11 approval (requires legal finalization)
- FOSS track: Python `format-factory-fods` (Apache-2.0) — separate, independent

## Key Points

1. The OASIS ODF 1.3 spec is royalty-free — no patent risk.
2. The commercial .NET product can be licensed under any proprietary commercial
   license chosen by the project lead.
3. The Python FOSS package (format-factory-fods) is Apache-2.0 — independent track.
4. No dual-licensing needed for the .NET product (Option B removes that complexity).

## What Remains Before Gate 11 Approval

- Final commercial license text must be selected and confirmed by project lead
- Legal review of commercial license terms recommended
- License header must be added to all .NET source files before release

## R21 Update

Updated: 2026-05-17, Sprint R21
G11-B Status: planning_level_license_confirmation_complete

Planning-level confirmation:
- OASIS ODF 1.3 RF — no patent risk CONFIRMED
- .NET runtime: MIT license — no commercial conflict CONFIRMED
- Python FOSS track: Apache-2.0 — independent CONFIRMED
- Commercial license for .NET product: Proprietary (choice deferred to Babar Raza)
- Formal legal counsel required before actual product release (not delegated to agent)

STATUS: planning_level_license_confirmation_complete
