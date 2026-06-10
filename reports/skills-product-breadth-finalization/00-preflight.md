# Skills Product Breadth Handoff Finalization — Preflight
Sprint: FORMAT-FACTORY-SKILLS-PRODUCT-BREADTH-HANDOFF-FINALIZATION-001
Generated: 2026-06-04T14:00:00Z

## Git State
Branch: main | HEAD: 3a86a05
Dirty state: Pre-existing R93 modifications only — no product changes from this sprint.

## No Product Source Changes
- git diff --diff-filter=A -- src/net: EMPTY
- git diff --diff-filter=A -- src/python: EMPTY

## No Plugin Install
- .claude-plugin/: DOES NOT EXIST

## Context from Previous Sprints
- skills-product-first: SKILLS_PRODUCT_FIRST_GOVERNED_EXECUTION_PASS (72 tests)
- skills-governed-execution-hardening: SKILLS_GOVERNED_EXECUTION_HARDENED_INDEPENDENTLY_VERIFIED (75 tests)
- Current Skills status: SKILLS_CONSUMABLE_WITH_LIMITATIONS
- Gap: FODS full packet ready; FODT/Netpbm shells need full handoffs

## Source Path Discovery
- FODT source: src/net/fodt/FodtDocument.cs, FodtMarkdownExporter.cs, FodtTxtExporter.cs
- Netpbm source: src/net/netpbm/Model/NetpbmImage.cs, NetpbmExporter.cs
- Last FODT R-test: FodtR113TxtDogfoodTests.cs → next: R114
- Last Netpbm R-test: NetpbmR113TileTests.cs → next: R114

## This Sprint Scope
- Convert FODT/Netpbm shells to full governed handoffs
- Create Skills Integration Contract for tri-lane consumption
- Schema compatibility maps for Supervisor/Acceleration
- Test suite + evidence closeout
