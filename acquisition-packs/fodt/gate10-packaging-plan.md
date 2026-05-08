---
artifact_id: fodt-gate10-packaging-plan
artifact_type: acquisition-pack
path: acquisition-packs/fodt/gate10-packaging-plan.md
format_id: fodt
visibility: internal
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
notes: "FODT Gate 10 packaging plan. run050."
---

# FODT Gate 10 -- Packaging Plan

**Package name (proposed):** format-factory-fodt
**Version:** v0.1.0
**Run:** run050 (2026-05-08)

---

## Packaging Requirements

1. Package: format-factory-fodt
2. Version: v0.1.0 (first release)
3. License: Apache-2.0
4. Python: 3.11+
5. Dependencies: none required; defusedxml optional (recommended)
6. Entry point: parse_fodt(filepath) in format_factory_fodt.parser
7. Test suite: pytest with Gate 3 samples + Gate 7 malformed fixtures
8. Documentation: README with usage examples
9. Security notes: file size guard, no network, no writes

## Release Blockers

1. Phase 4 Python implementation execution prompt required (not yet issued)
2. Iterative list traversal (TC-7) must be implemented (IR-FODT-003)
3. iterparse migration required (IR-FODT-014, TC-6)
4. Test suite must pass against all Gate 3 samples
5. No .github/workflows/ until explicitly authorized

## Out of Scope for v0.1.0

- Text spans, footnotes, sections
- Layout, images, tracked changes
- .NET implementation (DEC-033 pending)
- NuGet package (pending DEC-033)
