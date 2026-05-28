# R70 Independent Verification Report

**Sprint:** FORMAT-FACTORY-R71-PROOF-MODEL-RESET-LOCAL-RC-SEAL-AND-WORKAHEAD-001
**Date:** 2026-05-27
**Verifier:** R71 automated IV train

---

## R70 Artifact SHA Verification

| Artifact | SHA | Status |
|---|---|---|
| Outer delivery package | `0e6016b876863fe40b1ac9f69f11a2813e609b53a0f0fd285fab95ea51a7ec97` | VERIFIED |
| Inner evidence ZIP | `1e600e73ab16b9917dd5476e3769e93669da75d7a780265310bde1b5f4984c64` | VERIFIED |
| Sidecar file | `671f4f45b6593756fc72e5145d095a1399d1087bc186d839a3c992e297fcee0b` | VERIFIED |
| Sidecar-claimed inner ZIP | `1e600e73ab16b9917dd5476e3769e93669da75d7a780265310bde1b5f4984c64` | MATCHES INNER ZIP |
| Manifest evidence_zip_sha256 | `1e600e73...` | MATCHES INNER ZIP |
| Manifest sidecar_sha256 | `671f4f45...` | MATCHES SIDECAR FILE |

Delivery package structure: VALID (3 files: inner ZIP + sidecar + manifest)

---

## R70 Defects Found

### IV-R71-001 (RC-blocking): Inner final-verdict has stale BUNDLE_VALIDATION_PASS_2_SHA

**File inside inner ZIP:** `repo/reports/r70/final-verdict.md`
**Found:** `BUNDLE_VALIDATION_PASS_2_SHA: af7c9b76abe7d80f66e55c4b457cb433569612aa48c3f114775da4a953996372`
**Correct:** `1e600e73ab16b9917dd5476e3769e93669da75d7a780265310bde1b5f4984c64`
**Root cause:** The inner ZIP was built from a commit (a5feedd) where final-verdict.md still had the pre-sidecar-correction SHA. The correction was committed AFTER the bundle was built.

### IV-R71-002 (RC-blocking): Inner final-verdict has DELIVERY_PACKAGE_SHA: PENDING

**File inside inner ZIP:** `repo/reports/r70/final-verdict.md`
**Found:** `DELIVERY_PACKAGE_SHA: PENDING`
**Root cause:** The outer delivery package cannot be known inside the inner ZIP because it is built after the inner ZIP. This is a proof model violation — inner artifacts must not claim to know the outer package SHA.

### IV-R71-003 (RC-blocking): R70 final-delivery tests skip in extracted bundle context

**Tests:** `test_r70_final_delivery_mode_no_required_skips.py` and related
**When run from source tree (with .local/):** 23 passed
**When run from extracted bundle (no .local/):** All skip (depend on .local/ artifacts)
**Root cause:** Tests use `.local/` path fallback but don't accept an external delivery package path.

### IV-R71-004 (hygiene): Package manifest final_git_head semantics ambiguous

| Field | Value | Meaning |
|---|---|---|
| PAM final_git_head | `2f74eefb8d...` (R69 final commit) | R69 final, not R70 |
| DNM final_git_head | `26ba79919...` (R68 pass-1) | R68 pass-1, carries stale value |
| Sidecar git_head | `a5feedd...` (R70 commit between pass2 builds) | Not the bundle-build commit |
| Manifest git_head | `1d21384...` (R70 pass2 authoritative SHA commit) | Delivery manifest gen commit |

`final_git_head` is ambiguous — refers to different things in different manifests.

### IV-R71-005 (proof model): Validator does not enforce layered proof authority

**Problem:** Validator accepts inner final verdict with concrete outer delivery package SHA.
**Correct:** Inner final verdict must use `external_delivery_manifest_authoritative` not a concrete SHA for outer package fields.

---

## Classification

R70 classified as: **R70_DELIVERY_PACKAGE_VALID_BUT_PROOF_MODEL_WRONG**

Accepted:
- Outer delivery package structure: VALID
- Inner ZIP + sidecar + manifest all present
- Delivery manifest sidecar_sha256 = sidecar FILE sha: CORRECT
- Sidecar claims inner ZIP SHA: CORRECT
- Bundle validation with sidecar: PASS

Rejected:
- Inner final-verdict has stale/PENDING SHA fields (IV-R71-001, IV-R71-002)
- Final-delivery tests skip in extracted context (IV-R71-003)
- Manifest git-head semantics ambiguous (IV-R71-004)
- Validator doesn't enforce layered proof model (IV-R71-005)
