---
artifact_id: fodt-gate11-commercial-licensing
artifact_type: acquisition-pack
path: acquisition-packs/fodt/gate11-commercial-licensing.md
format_id: fodt
visibility: internal
generated_by: claude-sonnet-4-6
generated_at: "2026-05-12"
notes: "FODT Gate 11 commercial licensing note. DEC033-OPTION-B-GATE11-COMMERCIAL-SWARM-001."
---

# FODT Gate 11 — Commercial Licensing

**Format:** FODT (Flat OpenDocument Text)
**Gate:** 11 — Commercial Readiness
**Date:** 2026-05-12

## Underlying Spec License

- Spec body: OASIS
- Spec: ODF 1.3 Part 3 (Schema)
- Legal category: 1 — Open Standard (Royalty-Free)
- Patent waived: YES (OASIS RF policy)
- Implementation: Permitted without license fee

## Commercial Product License

- Product: FormatFactory.Fodt (NuGet package)
- DEC-033 Option B: .NET Commercial Only
- Proposed commercial license: Proprietary Commercial License
- License decision: PENDING Gate 11 approval (requires legal finalization)
- FOSS track: Python `format-factory-fodt` (Apache-2.0) — separate, independent

## Key Points

1. The OASIS ODF 1.3 spec is royalty-free — no patent risk.
2. The commercial .NET product can be licensed under any proprietary commercial
   license chosen by the project lead.
3. The Python FOSS package (format-factory-fodt) is Apache-2.0 — independent track.
4. FODT implementation notes: iterative DFS list traversal + iterparse streaming
   (see src/python/fodt/list_traversal.py for reference algorithm).

## What Remains Before Gate 11 Approval

- Final commercial license text must be selected and confirmed by project lead
- Legal review recommended
- License header must be added to all .NET source files before release

STATUS: pending_legal_finalization
