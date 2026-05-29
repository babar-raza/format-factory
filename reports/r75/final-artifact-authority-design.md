# Final Artifact Authority Design

**sprint_id:** FORMAT-FACTORY-R75-FINAL-ARTIFACT-AUTHORITY-REPAIR-RC-SEAL-PRODUCT-ADVANCEMENT-MEGA-TRAIN-001
**date:** 2026-05-29
**train:** B

## Problem Statement

The inner evidence ZIP cannot record its own SHA — this is a physical constraint:
a file inside a ZIP is created when the ZIP is built; the ZIP's SHA can only be
computed after all bytes are written. Putting the ZIP's SHA inside the ZIP requires
knowing the answer before computing it — a circular dependency.

Previous sprints used `TO_BE_FILLED_AFTER_BUNDLE_BUILD` as a placeholder, which:
1. Left unresolved tokens in the delivered artifact
2. Was not caught by the validator (R74 defects D07/D08)
3. Made the inner ZIP self-inconsistent

## Two-Authority Model

### Layer 1 — Source Evidence Authority (inner ZIP + committed repo)

**Scope:** Everything that can be proven before bundle builds begin
- Source code, test results, package artifacts, gate status
- Pass-1 SHA (computed before Pass-2 is built)
- Test pass/fail counts
- Sprint metadata

**Cannot claim:**
- Its own final SHA (inner ZIP SHA — circular)
- Sidecar SHA (sidecar is built after final ZIP)
- Outer delivery package SHA (circular, built after sidecar)

**What it says instead:**
- `BUNDLE_VALIDATION_PASS_2_SHA: delegated_to_final_artifact_authority_json`
- `SIDECAR_SHA: delegated_to_final_artifact_authority_json`
- `FINAL_IV: PASS_SEE_FINAL_ARTIFACT_AUTHORITY`

### Layer 2 — Final Artifact Authority (external JSON)

**Scope:** Generated AFTER all ZIPs are built. Lives alongside the delivery package.
- Inner ZIP SHA (now computable)
- Sidecar SHA
- Outer delivery package SHA
- Cross-layer consistency validation
- Standalone SHA file reference

**Location:** `.local/r75-final-artifact-authority.json` (alongside delivery package)
Also referenced in: `reports/r75/final-verdict.md`

## Schema

Schema defined at: `schemas/evidence/final-artifact-authority.schema.yaml`

Key structure:
```json
{
  "schema_version": "1.0",
  "sprint_id": "FORMAT-FACTORY-R75-...",
  "authority_model": "two_layer",
  "source_evidence_authority": {
    "inner_zip_sha256": "<sha of inner ZIP>",
    "sidecar_sha256": "<sha of sidecar file>",
    "sidecar_validates_inner_zip": true
  },
  "final_artifact_authority": {
    "delivery_package_sha256": "<sha of outer delivery ZIP>",
    "standalone_sha_file": "r75-delivery-package.sha256.txt"
  },
  "cross_layer_validation": {
    "all_sha_fields_non_circular": true,
    "sidecar_proves_inner_zip": true,
    "delivery_contains_inner_zip_and_sidecar": true
  }
}
```

## Standalone SHA File

Format: `<sha256>  <filename>` (sha256sum compatible)

Example:
```
abc123def456...  r75-delivery-package.zip
```

Location: `.local/r75-delivery-package.sha256.txt`
Also available at: `reports/r75/` (copied after build)

## Builder Changes

`tools/evidence/build_delivery_package.py` updated to:
1. Compute outer delivery package SHA after building
2. Write `<run>-delivery-package.sha256.txt` (standalone SHA)
3. Write `<run>-final-artifact-authority.json` (cross-layer authority)
4. Return paths in manifest dict

## Validator Changes

`tools/evidence/validate_evidence_bundle.py` updated with:
1. `TO_BE_FILLED_AFTER_BUNDLE_BUILD` in PENDING_MARKER_PATTERNS
2. `PASS_PENDING_BUNDLE_SHA` in PENDING_MARKER_PATTERNS
3. Lowercase variants in CLOSEOUT_HYGIENE_TOKENS
4. New `check_pass_number_drift()` function (errors on pass-number mismatch)

## Tests

- `tests/evidence/test_r75_rejects_to_be_filled_after_bundle_build.py` (6 tests)
- `tests/evidence/test_r75_detects_pass_number_drift.py` (7 tests)
- `tests/evidence/test_r75_final_artifact_authority_model.py` (4 tests)
- All 17 tests PASS

## DESIGN_STATUS: IMPLEMENTED_AND_TESTED
