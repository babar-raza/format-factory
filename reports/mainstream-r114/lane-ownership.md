# Mainstream R114 — Lane Ownership
Sprint: FORMAT-FACTORY-MAINSTREAM-R114-PRODUCT-EXECUTION-DIRTY-STATE-COMMIT-AND-BREADTH-SPRINT-001
Generated: 2026-06-04

## Lane Assignments

| Lane | Owner | Scope | Status |
|------|-------|-------|--------|
| Lane 0 | Coordinator | preflight, overlap check, integration log | IN_PROGRESS |
| Lane A | Dirty State | audit uncommitted src, FODT verification, dotnet build/test | PENDING |
| Lane B | Handoff Repair | fodt-markdown-handoff.yaml, fodt-txt-handoff.yaml, skills-integration-contract.json | PENDING |
| Lane C | Netpbm Pipeline | NetpbmImage.cs Pipeline method, NetpbmR114FlipMergePipelineTests.cs | PENDING |
| Lane D | FODS CSV Dogfood | FodsDocument.cs ExportSheetToCsv, FodsR114ExportToCsvTests.cs (conditional) | PENDING |
| Lane E | Capability Matrix | capability-matrix-proposals.md, refreshed-product-gaps.md | PENDING |
| Lane F | Adversarial Review | adversarial-review.md, build-verification.md | PENDING |
| Lane G | Evidence Closeout | evidence-declaration.yaml, autonomous cycle, review package | PENDING |

## File Ownership Map

### Lane A — READS ONLY (no edits)
- tests/net/fodt/FodtR112MarkdownExportDogfoodTests.cs
- tests/net/fodt/FodtR113TxtDogfoodTests.cs
- src/net/fodt/FodtMarkdownExporter.cs
- src/net/fodt/FodtTxtExporter.cs
- src/net/netpbm/Model/NetpbmImage.cs (pre-check only)
- src/net/fods/FodsDocument.cs (pre-check only)

### Lane B — EDITS
- reports/skills-product-breadth-finalization/fodt-markdown-handoff.yaml
- reports/skills-product-breadth-finalization/fodt-txt-handoff.yaml
- reports/skills-product-breadth-finalization/skills-integration-contract.json

### Lane C — EDITS
- src/net/netpbm/Model/NetpbmImage.cs (Pipeline method addition)
- tests/net/netpbm/NetpbmR114FlipMergePipelineTests.cs (NEW)

### Lane D — CONDITIONAL EDITS
- src/net/fods/FodsDocument.cs (only if NOT_IMPLEMENTED)
- tests/net/fods/FodsR114ExportToCsvTests.cs (only if NOT_IMPLEMENTED)

### Lane E — CREATES
- reports/mainstream-r114/capability-matrix-proposals.md
- reports/mainstream-r114/refreshed-product-gaps.md

### Lane F — CREATES
- reports/mainstream-r114/adversarial-review.md
- reports/mainstream-r114/build-verification.md

### Lane G — CREATES
- .local/evidences/mainstream-r114/evidence-declaration.yaml

## Integration Order
1. Lane 0 first
2. Lane A (depends on Lane 0)
3. Lane B (depends on Lane A findings)
4. Lanes C, D, E in parallel (all depend on Lane A)
5. Lane F (depends on B, C, D, E complete)
6. Lane G (depends on Lane F passing)
