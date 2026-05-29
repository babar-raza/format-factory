# R74 Defect Ledger

**sprint_id:** FORMAT-FACTORY-R74-R73-CLEAN-CLOSURE-VALIDATOR-HARDENING-PRODUCT-READINESS-MEGA-TRAIN-001
**ledger_date:** 2026-05-29
**ledger_author:** R75 Train A

## Summary

| Defect | Severity | Category | R75 Fix |
|---|---|---|---|
| D01 | RC-BLOCKING | Unresolved placeholders in final-iv | Train C + E |
| D02 | RC-BLOCKING | Pass-number drift in proof file | Train C + E |
| D03 | RC-BLOCKING | Wrong delivery SHA in validation summary | Train E |
| D04 | RC-BLOCKING | Wrong sidecar SHA in sidecar summary | Train E |
| D05 | RC-BLOCKING | Missing standalone SHA file | Train D |
| D06 | RC-BLOCKING | Missing artifact authority JSON | Train D |
| D07 | VALIDATOR-GAP | Validator missed TO_BE_FILLED_AFTER_BUNDLE_BUILD | Train C |
| D08 | VALIDATOR-GAP | Validator missed PASS_PENDING_BUNDLE_SHA | Train C |
| D09 | VALIDATOR-GAP | No pass-number drift detection | Train C |

Total: 9 defects (6 RC-blocking, 3 validator gaps)

## Defect Details

### D01 — Unresolved TO_BE_FILLED placeholders

File: bundle-metadata/final-independent-verification.txt (inside r74-pass5-final.zip)

The file contained:
```
BUNDLE_VALIDATION_PASS_1_SHA: TO_BE_FILLED_AFTER_BUNDLE_BUILD
BUNDLE_VALIDATION_PASS_2_SHA: TO_BE_FILLED_AFTER_BUNDLE_BUILD
SIDECAR_SHA: TO_BE_FILLED_AFTER_BUNDLE_BUILD
FINAL_IV: PASS_PENDING_BUNDLE_SHA
```

Root cause: File was a template written before bundle builds. Inner ZIP cannot record its
own SHA (circular dependency) but must not use placeholder text. R75 uses
`delegated_to_final_artifact_authority_json` as the semantic delegation label.

R75 fix: Validator now catches these patterns. Metadata template uses delegation labels.

### D02 — Pass-number drift in final-bundle-validation-proof.txt

File: bundle-metadata/final-bundle-validation-proof.txt (inside r74-pass5-final.zip)

The file claimed:
```
Bundle: r74-pass4-final.zip
SHA-256: 4cfd346c81609d00b1a312b32eec2749eaef8cebcddb7ff78f9f08a500f1c703
```

But actual delivery bundle was r74-pass5-final.zip (SHA: e41599fa...).

Root cause: Proof file was written at Pass 4 and not updated when Pass 5 was built.

R75 fix: New check_pass_number_drift() in validator catches pass-number mismatches.

### D03 — Wrong delivery SHA in delivery-package-validation-summary.txt

File claims DELIVERY_PACKAGE_SHA: 755faa81...
Actual delivery SHA: b55f5a1b...

Root cause: Summary was written for Pass 4 delivery, not Pass 5.
R75 fix: Two-authority model — summary uses delegation label instead of SHA.

### D04 — Wrong sidecar SHA in external-sidecar-proof-summary.txt

File claims sidecar_sha256: 22902f76... (pass4 sidecar)
Actual sidecar SHA: c888730d... (pass5 sidecar)

Root cause: Summary was written for Pass 4 sidecar.
R75 fix: Summary uses delegation label. Authority JSON holds actual sidecar SHA.

### D05 — Missing r74-delivery-package.sha256.txt

No standalone SHA file for outer delivery package.
R75 fix: build_delivery_package.py now generates .sha256.txt alongside output.

### D06 — Missing r74-final-artifact-authority.json

No cross-layer SHA authority record.
R75 fix: build_delivery_package.py now generates final-artifact-authority.json.

### D07 — Validator missed TO_BE_FILLED_AFTER_BUNDLE_BUILD

PENDING_MARKER_PATTERNS did not include this token.
R75 fix: Added to PENDING_MARKER_PATTERNS and CLOSEOUT_HYGIENE_TOKENS.

### D08 — Validator missed PASS_PENDING_BUNDLE_SHA

Neither PENDING_MARKER_PATTERNS nor CLOSEOUT_HYGIENE_TOKENS included this.
R75 fix: Added to both pattern lists.

### D09 — No pass-number drift detection

Only a SHA mismatch WARNING was issued; no ERROR for wrong pass number.
R75 fix: New check_pass_number_drift() function returns ERROR not WARNING.

## Reclassification

R74: R74_VALIDATOR_AND_DELIVERY_PROGRESS_ACCEPTED_SELF_INSPECTABLE_RC_REJECTED_BUILD_ORDER_STILL_BROKEN
