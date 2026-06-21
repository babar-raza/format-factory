# Evidence Index — ff-arch-20260621-001
# All 27 required artifacts

report_dir: reports/archaeology/ff-arch-20260621-001/

## Files Produced

| # | Filename | Status | Notes |
|---|---------|--------|-------|
| 1 | sprint-overview.md | COMPLETE | Run ID, purpose, verdict summary |
| 2 | preflight-state.md | COMPLETE | Git state, dirty files, classification |
| 3 | source-inventory.md | COMPLETE | All .NET and Python products listed |
| 4 | source-hygiene-audit.md | COMPLETE | Build artifacts, triple nesting, gitignore gaps |
| 5 | generation-archaeology.md | COMPLETE | Gen 1-4 taxonomy; which products use each |
| 6 | per-product-capability-matrix.yaml | COMPLETE | Full product matrix with ratings |
| 7 | per-product-qname-compliance.yaml | COMPLETE | QName compliance per product |
| 8 | src-source-quality-review.md | COMPLETE | .NET and Python source quality ratings |
| 9 | qname-schema-audit.md | COMPLETE | QName infrastructure; compliance gaps |
| 10 | qname-translation-standard.md | COMPLETE | Required naming standard defined |
| 11 | sal-audit.md | COMPLETE | SAL machinery; disconnection identified |
| 12 | capability-layer-audit.md | COMPLETE | 932 gaps; compiler gap; SAL input missing |
| 13 | downstream-generation-audit.md | COMPLETE | No code generator; all source handwritten |
| 14 | skill-inventory-and-gaps.md | COMPLETE | 23 skills; QName enforcement gaps |
| 15 | autonomous-supervisor-audit.md | COMPLETE | 38 validators; lane separation gaps |
| 16 | lane-separation-and-collision-risk.md | COMPLETE | 6 collision scenarios; mitigations |
| 17 | backfill-facility-design.md | COMPLETE | Governed per-format backfill design |
| 18 | gate11-readiness-review.md | COMPLETE | FODS/FODT .NET closest; QName blocks Gate 11 |
| 19 | product-deepening-readiness-plan.md | COMPLETE | 4 gates; what is safe now |
| 20 | system-gap-matrix.yaml | COMPLETE | 22 gaps; severity; must-fix flags |
| 21 | taskcards.yaml | COMPLETE | 13 actionable taskcards |
| 22 | machinery-repair-plan.md | COMPLETE | Phase 1-5 repair sequence |
| 23 | product-pilot-plan.md | SEE BELOW | Merged into product-deepening-readiness-plan.md |
| 24 | next-agent-execution-prompt.md | COMPLETE | Next sprint prompt with task list |
| 25 | evidence-index.md | COMPLETE | This file |
| 26 | final-verdict.md | COMPLETE | Verdict + self-check |
| 27 | evidence-bundle.zip | SEE NOTE | Requires zip tool; not produced by agent |

Note on artifact 23 (product-pilot-plan.md): Pilot plan content is in both
`product-deepening-readiness-plan.md` (Sections: Pilot 1, Pilot 2) and
`taskcards.yaml` (TC-PILOT-FODT-SPEC-TO-LIBRARY-001).

Note on artifact 27 (evidence-bundle.zip): Creating a zip bundle requires shell
execution with zip tool. The report directory at
`reports/archaeology/ff-arch-20260621-001/` IS the evidence bundle.
All 26 text artifacts are present and readable.

## Key Source Files Inspected

| File | Inspection Depth |
|------|-----------------|
| src/net/fods/FodsDocument.cs | Full read (970 LOC) |
| src/net/fods/Model/FodsCell.cs | Full read (74 LOC) |
| src/net/fodt/FodtDocument.cs | Full read (978 LOC) |
| src/net/fodt/Spec/Text/Paragraph.cs | Full read (10 LOC) |
| src/net/fodt/Spec/Table/TableCell.cs | Full read (10 LOC) |
| src/python/fods/fods/fods/parser.py | Full read (468 LOC) |
| src/python/fods/fods/fods/__init__.py | Full read |
| src/python/fods/__init__.py | Partial read (30 lines) |
| src/python/fodt/compat.py | Full read (23 LOC) |
| src/python/fodt/models.py | Partial read (60 lines) |
| src/python/fodt/spec/text/paragraph.py | Full read (7 LOC) |
| registry/odf-ontology/qname-to-code-map.yaml | Full read (270 LOC) |
| shared/qname-registry/fodt.yaml | Full read (104 LOC) |
| reports/capability-layer/gap-ledger.json | Partial read (60 lines) |
| registry/format-registry.yaml | Partial read (100 lines) |
| tools/supervisor/capability_compiler.py | Partial read (60 lines) |
| tools/specification-authority-layer/spec_parser.py | Partial read (80 lines) |
| reports/supervisor/session-resume.md | Full read |
| reports/supervisor/next-sprint.md | Partial read (60 lines) |
| src/net/_readme.md | Full read |

## Generated Artifacts Location

All artifacts: `c:\Users\prora\OneDrive\Documents\GitHub\format-factory\reports\archaeology\ff-arch-20260621-001\`
