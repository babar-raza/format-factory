# Current State Snapshot

**Formats in registry:** 22
**Latest sprint:** R66 - R66_CLEAN_DELIVERY_RC_REPEATABLE_PHASE17_PASS
**Gate 11 approved:** False
**commercial_product_ready:** False

## Generated Requirements
- fods: 6 files
- fodt: 6 files

## Evidence Contracts
- Total: 156
- ISSUE: r27-ai-platform-full-cycle.yaml: min_metadata_count=10 < 30
- ISSUE: r32-truth-matrix-gate-quality-and-drift-recovery.yaml: min_metadata_count=5 < 30

## Production Blockers
- G11-G_NOT_STARTED: Gate 11 commercial approval requires Babar Raza written approval
- GATE8_AWAITING_HUMAN_APPROVAL: ODS/ODT/QOI/XCF/DIF/PPM Gate 8 security review pending
- PACKAGE_NOT_PUSHED: All POC artifacts are local-only, not pushed to registry
- physical_invariant_check_error: REPAIRED_R65 (check_repo_invariants.py handles dict-format required_repo_files)
