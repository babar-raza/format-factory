# R73 + R74 Sprint Summary (2026-05-29)

## R73 Sprint: FORMAT-FACTORY-R73-DELIVERY-PACKAGE-TRUTH-PRODUCT-ADVANCEMENT-GATE-READINESS-MEGA-TRAIN-001

**Classification:** R73_DELIVERY_PACKAGE_CONVENTION_PROGRESS_ACCEPTED_SELF_INSPECTABLE_CLOSURE_REJECTED_PRODUCT_PROGRESS_PARTIAL

**IV Findings (from R74 Train A):**
- IV-R74-001: Stale SHA in inner ZIP (CRITICAL) — ZIP built before final SHA commits; internal final-verdict.md has e4784a0f, expected ffa23117
- IV-R74-002: PENDING_BUNDLE_BUILD in external-sidecar-proof-summary.txt not caught by validator
- IV-R74-003: `-> PENDING` in validation-command-log.txt not caught by validator
- IV-R74-004: Placeholder `[to be filled]` in final-independent-verification.txt not caught by validator
- IV-R74-005: missing-sidecar-negative-proof.txt is a stub (no real command evidence)
- IV-R74-006: wrong-sidecar-negative-proof.txt is a stub (no real command evidence)

**R73 Bundle SHAs:**
- Inner ZIP (ffa23117...): contains stale final-verdict (IV-R74-001)
- Sidecar: 12ecae49...
- Outer delivery: 0733856f...

**R73 Product Advancement (real, tested):**
- FODS: merged-cell col_span/row_span, WARN_FORMULA_CELL
- FODT: footnote/endnote detection warning, table cell span
- PBM: image_pixel_stats() API
- PGM: image_pixel_stats() API
- SYLK/ZST/DIF: 36 new advancement tests

**R73 authoritative test result:** 6054 passed, 1 failed (ZST Unicode), 29 skipped

---

## R74 Sprint: FORMAT-FACTORY-R74-R73-CLEAN-CLOSURE-VALIDATOR-HARDENING-PRODUCT-READINESS-MEGA-TRAIN-001

**Target:** 0 failures, self-inspectable delivery with real command evidence

**Completed Trains A-J:**
- Train A: R73 IV + defect ledger (6 defects classified)
- Train B: Validator hardening — PENDING_BUNDLE_BUILD, -> PENDING, [to be filled after], stale-SHA patterns; 35 new tests; check_negative_proof_quality()
- Train C: Build-order repair — two-layer protocol (inner ZIP must be rebuilt AFTER final SHA commits)
- Train D: ZST Unicode fix — replaced U+2192 `→` with ASCII `->` in 4 print statements; test now PASS
- Train E: R73 product advancement verified — 72 tests PASS, 0 regressions
- Train F: All 10 packages rebuilt; 6-package installed smoke PASS; PBM/PGM now include image_pixel_stats
- Train G: .NET 161 FODS + 145 FODT = 306 tests PASS
- Train H: Gate 8/11 re-verified; no regressions; G11-G still NOT_STARTED
- Train I: State snapshot PASS, 14/14 invariants PASS, memory updated
- Train J: AI telemetry truth (fixture mode confirmed)

**Train K (pending):** Final adversarial IV + evidence bundle build

**R74 evidence contract:** tools/evidence/contracts/r74-r73-clean-closure-validator-hardening-product-readiness.yaml

**Key build protocol policy (from Train C):**
1. Commit source → run tests → update final-verdict → pass1 build → commit pass1 SHA
2. Build pass2 → generate sidecar → commit pass2 SHA + sidecar SHA (DELIVERY_PACKAGE_RECORDED_SHA = semantic label)
3. Build PASS 3 ZIP from this final committed HEAD → THIS ZIP has correct SHAs inside
4. Build outer delivery from pass3 ZIP + sidecar + manifest
5. Record outer SHA in delivery-package-validation-summary.txt (NOT in final-verdict)
