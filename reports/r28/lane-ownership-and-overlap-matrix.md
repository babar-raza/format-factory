# R28 Lane Ownership and Overlap Matrix
# Sprint: FORMAT-FACTORY-R28-FULL-THROTTLE-AI-FORMAT-COMMERCIAL-PUBLICATION-AND-EVIDENCE-TRAIN-001

## Lane Definitions

| Lane | Owner | Scope | Dependencies |
|------|-------|-------|-------------|
| A | Coordinator | R27 closure/evidence repair | None (first) |
| B | Coordinator | AI taskcard state repair | Lane A (needs reconciled state) |
| C | AI | AI production hardening (deeper modules + tests) | None |
| D | AI | AI end-to-end pilot (fixture mode) | Lane C (needs hardened modules) |
| E | AI | AI-generated requirements pipeline | Lane C, D |
| F | Format | ODS/ODT/QOI Gate 4 hardening | None |
| G | Format | Next format train (XCF/ZPAQ + new) | None |
| H | .NET | FODS/FODT commercial C7/C8/C9 hardening | None |
| I | Packaging | Python FOSS publication packet hardening | None |
| J | Evidence | Evidence/bundle automation hardening | None |
| K | Validation | Full test suite execution | All implementation lanes |
| L | Governance | Independent verification | Lane K |
| M | Coordinator | Documentation/memory/registry sync | All lanes |

## Overlap Rules

- Lanes C, F, G, H, I, J are fully independent — can execute in parallel
- Lane D depends on Lane C completion
- Lane E depends on Lanes C and D
- Lane K must run after all implementation lanes
- Lane L must run after Lane K
- Lane M must run after Lane L
- Lane A runs first (unblocks B)
- Lane B runs after A

## Shared File Ownership

| File | Owner Lane | Other Lanes Read-Only |
|------|-----------|----------------------|
| registry/format-registry.yaml | M | F, G, H |
| memory/00-index.md | M | All |
| ROADMAP.md | M | G |
| plans/master-plan.md | M (if needed) | All |
| tools/evidence/contracts/*.yaml | J, M | A |
| taskcards/AI-*.md | B | C, D, E |
