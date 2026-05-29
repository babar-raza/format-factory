# R73 Independent Verification

**Sprint:** FORMAT-FACTORY-R74-R73-CLEAN-CLOSURE-VALIDATOR-HARDENING-PRODUCT-READINESS-MEGA-TRAIN-001
**Date:** 2026-05-29
**Subject:** R73 — FORMAT-FACTORY-R73-DELIVERY-PACKAGE-TRUTH-PRODUCT-ADVANCEMENT-GATE-READINESS-MEGA-TRAIN-001

---

## Artifact Verification

### Local Artifact SHAs (confirmed by direct computation)

| Artifact | SHA-256 | Size |
|---|---|---|
| .local/r73-pass2-final.zip (inner evidence ZIP) | ffa23117339ec309161305cf91de8af3bece848db301f919c6b09051a45111a5 | 8,101,836 |
| .local/r73-pass2-final.sha256-proof.json (sidecar) | 12ecae49ff66109f32605d7883e331b01b93712f90613aa4365728533b688e5d | 875 |
| .local/r73-delivery-package.zip (outer delivery package) | 0733856fdc40c604e87bae1334d46641bf129efdd5f7a42f0232cd48e2022081 | 7,673,804 |

### Delivery Package Structure (confirmed)

Outer package entries: 4
- r73-pass2-final.zip
- r73-pass2-final.sha256-proof.json
- r73-delivery-manifest.json
- r73-supervisor-inspection-readme.md

Manifest values:
- evidence_zip_sha256: ffa23117339ec309161305cf91de8af3bece848db301f919c6b09051a45111a5 ✓ matches
- sidecar_sha256: 12ecae49ff66109f32605d7883e331b01b93712f90613aa4365728533b688e5d ✓ matches
- sidecar_claimed_bundle_sha256: ffa23117339ec309161305cf91de8af3bece848db301f919c6b09051a45111a5 ✓ matches

**Supervisor-reported outer package SHA matches local:** 0733856f ✓
**Supervisor-reported inner ZIP SHA matches local:** ffa23117 ✓
**Supervisor-reported sidecar SHA matches local:** 12ecae49 ✓

---

## Defect Confirmation

### IV-R74-001 (RC-BLOCKING): Stale SHAs inside inner evidence ZIP

**Confirmed locally.**

The inner evidence ZIP (ffa23117...) contains `repo/reports/r73/final-verdict.md` with stale SHA values:
- BUNDLE_VALIDATION_PASS_2_SHA: e4784a0f... (stale — should be ffa23117...)
- SIDECAR_SHA: fdff3bb9... (stale — should be 12ecae49...)
- DELIVERY_PACKAGE_RECORDED_SHA: 4f2b2917... (stale — should be 0733856f...)

Root cause: The inner ZIP was built from commit f2d0c6b state. After that, commits b7cc298 and
72c620f updated final-verdict.md with correct SHAs. The "final rebuild" in the R73 session did not
produce a new inner ZIP containing the updated verdict. The ZIP on disk retained the pre-b7cc298 state.

Classification: CONFIRMED_CARRIED_TO_R74 → Repair in R74 Train C (build-order protocol)

### IV-R74-002 (RC-BLOCKING): PENDING_BUNDLE_BUILD in external-sidecar-proof-summary.txt

**Confirmed.**

File `.local/r73-metadata/external-sidecar-proof-summary.txt` contains:
`EXTERNAL_SIDECAR_PROOF_SUMMARY: PENDING_BUNDLE_BUILD`

This is a placeholder never updated after the sidecar was generated.

Validator miss: `PENDING_BUNDLE_BUILD` is not in PENDING_MARKER_PATTERNS.

Classification: CONFIRMED_CARRIED_TO_R74 → Repair in R74 (metadata + validator hardening)

### IV-R74-003 (RC-BLOCKING): "full suite -> PENDING" in validation-command-log.txt

**Confirmed.**

File `.local/r73-metadata/validation-command-log.txt` line 24:
`-> PENDING`

This indicates the full test suite result was written as a placeholder and never updated.

Validator miss: `-> PENDING` not in PENDING_MARKER_PATTERNS.

Classification: CONFIRMED_CARRIED_TO_R74 → Repair in R74 (metadata + validator hardening)

### IV-R74-004 (RC-BLOCKING): [to be filled] placeholders in final-independent-verification.txt

**Confirmed.**

File `.local/r73-metadata/final-independent-verification.txt` contains:
- `[to be filled after Pass 1 build]`
- `[to be filled after Pass 2 build]`
- `[to be filled after sidecar generation]`

Validator miss: CLOSEOUT_HYGIENE_REPORT_FILES checks `final-independent-verification.md` (`.md`)
but the actual file is `final-independent-verification.txt` (`.txt`). Extension mismatch.
Also missing from CLOSEOUT_HYGIENE_TOKENS: `[to be filled after`.

Classification: CONFIRMED_CARRIED_TO_R74 → Repair in R74 (metadata + validator hardening)

### IV-R74-005 (RC-BLOCKING): Validator passed despite stale placeholders

**Confirmed.**

Running `validate_evidence_bundle.py --check-no-pending` against R73 bundle returns PASS despite
IV-R74-002, 003, 004 being present. Root cause: gaps in PENDING_MARKER_PATTERNS and
CLOSEOUT_HYGIENE_REPORT_FILES (as documented in IV-R74-002..004).

Classification: CONFIRMED_CARRIED_TO_R74 → Repair in R74 Train B

### IV-R74-006 (MODERATE): Missing-sidecar negative proof lacks actual failing command

**Confirmed.**

File `.local/r73-metadata/missing-sidecar-negative-proof.txt` only references test names and
results. It does not include an actual command, its output, and an actual FAIL marker from
running `validate_evidence_bundle.py` against a sidecar-less bundle.

Classification: CONFIRMED_CARRIED_TO_R74 → Repair in R74 Train K

### IV-R74-007 (MODERATE): Wrong-sidecar negative proof lacks actual failing command

**Confirmed.**

Same pattern as IV-R74-006: references test names only, no actual command + exit code + fail output.

Classification: CONFIRMED_CARRIED_TO_R74 → Repair in R74 Train K

### IV-R74-008 (RC-BLOCKING): Authoritative test result has 1 failure

**Confirmed.**

`tests/examples/test_python_examples_smoke.py::test_zst_example_runs_without_crash` fails due to
UnicodeEncodeError (Windows cp1252, `→` character in compress_decompress_file.py line ~43).

This was classified as "pre-existing" but clean RC requires 0 failures. Must be fixed.

Classification: CONFIRMED_CARRIED_TO_R74 → Repair in R74 Train D

### IV-R74-009 (MODERATE): INV-011 stale reference in state/current-state.md

**Confirmed.**

state/current-state.md Production Blockers section still lists:
```
- INV-011: state/current-state.md shows R72 but latest contract is R73
- INV-011: Run state_snapshot.py to update current-state.md
```
The file's header now shows "Latest sprint: R73" (correct), but the blocker text still says "shows R72".
This is a stale invariant blocker reference that was never cleaned up.

Classification: CONFIRMED_CARRIED_TO_R74 → Repair in R74 Train I

---

## Summary

| Defect | Severity | Classification |
|---|---|---|
| IV-R74-001: Stale SHAs in inner ZIP final-verdict | RC-BLOCKING | CONFIRMED_CARRIED_TO_R74 |
| IV-R74-002: PENDING_BUNDLE_BUILD in sidecar summary | RC-BLOCKING | CONFIRMED_CARRIED_TO_R74 |
| IV-R74-003: full suite -> PENDING in cmd log | RC-BLOCKING | CONFIRMED_CARRIED_TO_R74 |
| IV-R74-004: [to be filled] in final-iv.txt | RC-BLOCKING | CONFIRMED_CARRIED_TO_R74 |
| IV-R74-005: Validator passed stale placeholders | RC-BLOCKING | CONFIRMED_CARRIED_TO_R74 |
| IV-R74-006: Missing-sidecar proof stub | MODERATE | CONFIRMED_CARRIED_TO_R74 |
| IV-R74-007: Wrong-sidecar proof stub | MODERATE | CONFIRMED_CARRIED_TO_R74 |
| IV-R74-008: ZST Unicode example failure | RC-BLOCKING | CONFIRMED_CARRIED_TO_R74 |
| IV-R74-009: INV-011 stale state blocker text | MODERATE | CONFIRMED_CARRIED_TO_R74 |

R73 CLASSIFICATION: R73_DELIVERY_PACKAGE_CONVENTION_PROGRESS_ACCEPTED_SELF_INSPECTABLE_CLOSURE_REJECTED_PRODUCT_PROGRESS_PARTIAL

R73_IV_RESULT: 9 defects (5 RC-blocking proof contradictions, 4 moderate)
