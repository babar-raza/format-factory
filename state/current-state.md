# Current State Snapshot

**Formats in registry:** 22
**Latest sprint:** R85 - no_final_verdict
**Gate 11 approved:** False
**commercial_product_ready:** False

## Generated Requirements
- fods: 6 files
- fodt: 6 files
- pbm: 2 files

## Evidence Contracts
- Total: 175
- ISSUE: r27-ai-platform-full-cycle.yaml: min_metadata_count=10 < 30
- ISSUE: r32-truth-matrix-gate-quality-and-drift-recovery.yaml: min_metadata_count=5 < 30

## Production Blockers
- G11-G_NOT_STARTED: Gate 11 commercial approval requires Babar Raza written approval
- GATE8_AWAITING_HUMAN_APPROVAL: ODS/ODT/QOI/XCF/DIF/PPM Gate 8 security review pending
- PACKAGE_NOT_PUSHED: All POC artifacts are local-only, not pushed to registry
- INV-006: Sidecar .sha256-proof.json is git-tracked (must be gitignored): reports/r84/r84-pass3-final.sha256-proof.json
- INV-014: reports/r84/final-verdict.md: claims BUNDLE_VALIDATION: PASS but no 'Pass 1 SHA-256' line found
