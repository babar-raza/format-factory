# R75 Validator Hardening Report

**sprint_id:** FORMAT-FACTORY-R75-FINAL-ARTIFACT-AUTHORITY-REPAIR-RC-SEAL-PRODUCT-ADVANCEMENT-MEGA-TRAIN-001
**date:** 2026-05-29
**train:** C

## R74 Validator Gaps (Confirmed)

Running R74 pass5 bundle through validator with R75-hardened validator now shows:

```
No-PENDING check (FAIL): 1 metadata PENDING
Pass-number drift check (FAIL): proof file references wrong pass number
BUNDLE_VALIDATION: FAIL
```

Previously (R74 validator) both checks showed PASS despite defects. This confirms
the R74 validator gaps were real and are now fixed.

## Changes to validate_evidence_bundle.py

### 1. PENDING_MARKER_PATTERNS additions (R75)

Added:
- `"TO_BE_FILLED_AFTER_BUNDLE_BUILD"` — R74 D01: exact uppercase token in final-iv
- `"PASS_PENDING_BUNDLE_SHA"` — R74 D01: FINAL_IV placeholder value

### 2. CLOSEOUT_HYGIENE_TOKENS additions (R75)

Added (lowercase, for case-insensitive scan):
- `"to_be_filled_after_bundle_build"` — R74 D01: lowercase match
- `"pass_pending_bundle_sha"` — R74 D01: lowercase match

### 3. New check_pass_number_drift() function (R75)

Detects when `final-bundle-validation-proof.txt` claims a different pass number
than the actual bundle under validation.

Logic:
1. Parse `Bundle: <filename>` line from proof file
2. Extract pass number from claimed filename (e.g. `r74-pass4-final.zip` → 4)
3. Extract pass number from actual bundle path (e.g. `r74-pass5-final.zip` → 5)
4. If different: ERROR (PASS_NUMBER_DRIFT)
5. If no `Bundle:` line or no pass number: skip check (older format)

Output line:
```
Pass-number drift check (FAIL): proof file references wrong pass number — R75 guard
```

## Negative Proof Verification

Running R74 pass5 bundle with R75-hardened validator confirms all 3 gaps now caught:
1. PENDING marker: `TO_BE_FILLED_AFTER_BUNDLE_BUILD` in final-independent-verification.txt
2. PASS_NUMBER_DRIFT: proof claims pass4, bundle is pass5
3. Closeout hygiene: `to_be_filled_after_bundle_build` in final-iv

## Test Coverage

17 new tests across 3 files. All PASS.

| File | Tests |
|---|---|
| test_r75_rejects_to_be_filled_after_bundle_build.py | 6 |
| test_r75_detects_pass_number_drift.py | 7 |
| test_r75_final_artifact_authority_model.py | 4 |

## VALIDATOR_HARDENING_STATUS: COMPLETE
