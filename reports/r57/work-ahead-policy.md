# R57 Work-Ahead Policy

**Sprint:** FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
**Date:** 2026-05-23

---

## Policy

Any train that completes ahead of schedule must look for safe adjacent work before
declaring itself idle. Candidate adjacent work items are listed below.

## Auto-Expansion Candidates

| If this lane finishes early... | Safe adjacent work |
|-------------------------------|-------------------|
| B (validator repair) | Add test for `BUNDLE_VALIDATION_PASS_1_SHA: PENDING` pattern |
| C (package replay) | Verify CSV/TSV test paths also use discovery, not hardcoded .local/ |
| D (hash enforcement) | Add full-SHA to sidecar proof fields in write_sidecar_proof.py |
| E (product deepening) | Check if _matrix.yaml needs FODS unsupported_capabilities update |
| F (format advancement) | Consider advancing SYLK to Gate 10 if PGM/PBM/TSV/CSV done |
| G (phase audit) | Generate per-format Phase 8 readiness cards |
| I (spec-cache repair) | Add CSV/TSV spec-cache entries if repair of ABW/Gnumeric complete |
| J (AI/telemetry) | Verify fixture mode passes on all existing AI test files |

## Hard Prohibitions

- Do NOT modify Gate 11 status (human approval required)
- Do NOT push to remote repo
- Do NOT change `commercial_product_ready: false`
- Do NOT publish any package to PyPI
- Do NOT modify test files that already pass without running them first

---

**STATUS: WORK_AHEAD_POLICY_DEFINED**
