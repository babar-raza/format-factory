# Current State Snapshot

**Formats in registry:** 22
**Latest sprint:** R73 - R73_DELIVERY_PACKAGE_SELF_INSPECTABLE_PRODUCT_ADVANCEMENT_PASS_PUBLICATION_BLOCKED
**Gate 11 approved:** False
**commercial_product_ready:** False

## Generated Requirements
- fods: 6 files
- fodt: 6 files
- pbm: 2 files

## Evidence Contracts
- Total: 163
- ISSUE: r27-ai-platform-full-cycle.yaml: min_metadata_count=10 < 30
- ISSUE: r32-truth-matrix-gate-quality-and-drift-recovery.yaml: min_metadata_count=5 < 30

## Production Blockers
- G11-G_NOT_STARTED: Gate 11 commercial approval requires Babar Raza written approval
- GATE8_AWAITING_HUMAN_APPROVAL: ODS/ODT/QOI/XCF/DIF/PPM Gate 8 security review pending
- PACKAGE_NOT_PUSHED: All POC artifacts are local-only, not pushed to registry
- INV-011: state/current-state.md shows R72 but latest contract is R73
- INV-011: Run state_snapshot.py to update current-state.md
