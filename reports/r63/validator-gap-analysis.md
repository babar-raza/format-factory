# R63 Work-Ahead W4 — Validator Gap Analysis

**Sprint:** FORMAT-FACTORY-R63-AI-ASSISTED-RC-CLOSURE-AND-WORKAHEAD-MULTI-SPRINT-MEGA-TRAIN-001
**Date:** 2026-05-24
**Purpose:** Identify gaps in validate_evidence_bundle.py for R64 hardening

---

## Current Validator Capabilities (R63)

| Check | Function | Status |
|---|---|---|
| Sidecar required | check_sidecar_required() | PASS — R54 hardened |
| Clean git | check_require_clean_git() | PASS |
| PENDING markers | check_no_pending_markers() | PASS — R57 hardened |
| SHA truncation | check_no_truncated_sha() | PASS — R57 hardened |
| Contract compliance | check_contract_required_files() | PASS |
| Metadata count | check_min_metadata_count() | PASS |
| Artifact inventory | check_artifact_inventory() | PASS |
| Bundle manifest | check_bundle_manifest() | PASS |

---

## Identified Gaps

### GAP-001: No check for AI_NOT_LIVE labeling
- **Issue:** Validator does not check that AI reviewer files declare `ai_not_live: true`
- **Impact:** LOW — fixture mode AI could appear as live AI without labeling
- **R64 Repair:** Add `check_ai_not_live_labeled()` to validator

### GAP-002: No check for INV-007 trigger phrases in all sprint files
- **Issue:** Validator checks final-verdict.md but not other report files
- **Impact:** MEDIUM — trigger phrase could appear in non-verdict files
- **R64 Repair:** Extend check_inv007_trigger() to scan all reports/*.md files

### GAP-003: No API export count validation
- **Issue:** Validator does not verify that installed-wheel API proof matches claim
- **Impact:** HIGH — IV-R62-002/003 root cause (overclaimed without validation)
- **R64 Repair:** Add `check_installed_api_claim_consistency()` — cross-reference final-verdict API claims with api-repair-verification.txt

### GAP-004: Sidecar SHA mismatch between final-verdict and sidecar file
- **Issue:** Validator doesn't cross-check final-verdict SIDECAR_SHA against actual sidecar content
- **Impact:** MEDIUM — IV-R62-007 root cause
- **R64 Repair:** Add `check_sidecar_sha_matches_verdict()` — read sidecar, extract sha256, compare to final-verdict SIDECAR_SHA

---

## Priority for R64

1. GAP-003 (HIGH) — prevents API overclaim recurrence
2. GAP-004 (MEDIUM) — prevents SHA mismatch recurrence
3. GAP-002 (MEDIUM) — extends INV-007 coverage
4. GAP-001 (LOW) — AI labeling check (nice-to-have)

---

VALIDATOR_GAP_ANALYSIS_STATUS: COMPLETE
