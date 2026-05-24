# R56 Defect Ledger — R57 Train A

**Sprint:** FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
**Source sprint:** R56
**Date:** 2026-05-23
**Total defects:** 10

---

| ID | Defect | Severity | Root Cause | R57 Fix | Status |
|----|--------|----------|-----------|---------|--------|
| IV-R56-001 | No top-level sidecar proof uploaded for r56-pass2-final.zip | BLOCKING | Sidecar created in gitignored .local/; not committed to repo | Store sidecar in reports/r57/; require top-level proof location | OPEN → R57 Train L |
| IV-R56-002 | Contract r56 missing sidecar_required and final_proof_policy | MAJOR | Contract authored before policy was finalized | Add both fields to r57 contract from the start | OPEN → R57 Train B |
| IV-R56-003 | final-verdict.md temporarily had BUNDLE_VALIDATION_PASS_2_SHA: PENDING | MAJOR | SHA not known when verdict was first written | Validator must catch this pattern | OPEN → R57 Train B |
| IV-R56-004 | Validator PENDING patterns do not include SHA-keyed PENDING | MAJOR | Pattern was added after R56 contract written | Add BUNDLE_VALIDATION_PASS_2_SHA/PASS_1_SHA: PENDING to PENDING_MARKER_PATTERNS | OPEN → R57 Train B |
| IV-R56-005 | test_r56_package_rc.py uses hardcoded .local/ path | MAJOR | Tests written assuming local build environment | Use discovery function; skip when dir absent | OPEN → R57 Train C |
| IV-R56-006 | package-artifact-manifest.yaml wheel_sha256 values are 32 chars (MD5) | MAJOR | SHA computed with md5 instead of sha256 | Recompute with SHA-256; write full 64-char values | OPEN → R57 Train D |
| IV-R56-007 | Validator silently skips non-64-char SHA values in manifest | MAJOR | Validator regex requires exactly 64 chars; truncated values never parsed | Add explicit length enforcement check | OPEN → R57 Train D |
| IV-R56-008 | final-bundle-validation-proof.txt missing bundle filename/SHA/size/entries/sidecar/exitcode | MAJOR | Proof written manually without template | R57 proof must include all required self-verifying fields | OPEN → R57 Train L |
| IV-R56-009 | R56 overstated format advancement (5 formats: status confirmation, no code/tests) | MINOR | Train F report included PPM/DIF/SYLK/PGM/PBM status without new work | R57 Train F must use only actual advancement (code + tests) | DOCUMENTED |
| IV-R56-010 | fods.yaml unsupported_capabilities "Cell style/formatting preservation" conflicts with TC-0055 | MINOR | TC-0055 closed style metadata preservation in R55 but manifest not updated | Split into visual fidelity (unsupported) and XML passthrough (supported) | OPEN → R57 Train E |

---

## Defect Categories

| Category | Count |
|----------|-------|
| Evidence protocol gap | 2 (001, 008) |
| Contract incompleteness | 1 (002) |
| Validator gap | 2 (003/004) |
| Test portability | 1 (005) |
| Evidence integrity | 2 (006/007) |
| Overclaim | 1 (009) |
| Release manifest accuracy | 1 (010) |
| **Total** | **10** |

---

**LEDGER_STATUS: COMPLETE — 10 defects documented, all assigned to R57 trains**
