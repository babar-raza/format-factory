# R84 Train A — R83 Defect Ledger

**Sprint:** FORMAT-FACTORY-R84
**Date:** 2026-05-31
**Source:** Supervisor inspection of r83-supervisor-review-package.zip

## Defect Classification Key

- CONFIRMED_REPAIRED — fixed in R84
- CONFIRMED_CARRIED_TO_R84 — active defect being fixed now
- EXPLAINED_NOT_DEFECT — false positive with explanation
- NOT_REPRODUCIBLE_WITH_EVIDENCE — cannot reproduce

## Defects

### D83-01: Review package not top-level self-contained

**Supervisor finding:** package-artifacts/, raw-test-logs/, raw-package-install-logs/, raw-negative-proof-logs/, raw-dotnet-logs/, product-capability-matrix/, gate-readiness/, publication-readiness/, examples-docs-readiness/ not at top level of review package.
**Classification:** CONFIRMED_CARRIED_TO_R84
**R84 repair:** Train B — modify build_supervisor_review_package.py to include top-level directories.

### D83-02: Inner final-verdict PENDING_TEST_RUN

**Supervisor finding:** `repo/reports/r83/final-verdict.md` inside inner ZIP has `Python: PENDING_TEST_RUN`.
**Classification:** CONFIRMED_CARRIED_TO_R84
**Root cause:** Pass 2 bundle was built before final-verdict was updated with real test result.
**R84 repair:** Train C — 3-pass build protocol ensures committed values before final build.

### D83-03: Inner final-verdict Pass 2 SHA delegated

**Supervisor finding:** `Pass 2 SHA-256: delegated_to_final_artifact_authority_json` in inner final-verdict.
**Classification:** CONFIRMED_CARRIED_TO_R84
**Root cause:** Pass 2 SHA is circular — cannot be in the ZIP that IS Pass 2.
**R84 repair:** Train C — 3-pass protocol: Pass 3 bundle has Pass 1+Pass 2 SHAs filled in final-verdict.

### D83-04: Inner final-verdict Sidecar SHA delegated

**Supervisor finding:** `Sidecar SHA-256: delegated_to_final_artifact_authority_json`.
**Classification:** CONFIRMED_CARRIED_TO_R84
**R84 repair:** Train C — same as D83-03, covered by 3-pass protocol.

### D83-05: Inner final-verdict SIDECAR_PROOF_VALIDATION: PENDING

**Supervisor finding:** `SIDECAR_PROOF_VALIDATION: PENDING` in inner final-verdict.
**Classification:** CONFIRMED_CARRIED_TO_R84
**R84 repair:** Train C — commit `SIDECAR_PROOF_VALIDATION: PASS` before final bundle build.

### D83-06: delivery-package-validation-summary.txt PENDING_BUILD

**Supervisor finding:** `STATUS: PENDING_BUILD` in bundle metadata.
**Classification:** CONFIRMED_CARRIED_TO_R84
**R84 repair:** Train C — finalize all metadata with real values before bundle build.

### D83-07: delivery-package-validation-summary.txt SHA: PENDING

**Supervisor finding:** `SHA: PENDING` in delivery summary.
**Classification:** CONFIRMED_CARRIED_TO_R84
**R84 repair:** Train C — same as D83-06.

### D83-08: external-sidecar-proof-summary.txt PENDING_BUILD

**Supervisor finding:** `STATUS: PENDING_BUILD`, `EXTERNAL_SIDECAR: DOCUMENTED_PRE_BUILD`.
**Classification:** CONFIRMED_CARRIED_TO_R84
**R84 repair:** Train C — finalize sidecar summary with real SHA before bundle build.

### D83-09: final-artifact-authority-summary.txt says "will be populated after build"

**Supervisor finding:** Pre-build placeholder language in authority summary.
**Classification:** CONFIRMED_CARRIED_TO_R84
**R84 repair:** Train C — write authority summary with real values after delivery package built, THEN rebuild inner bundle.

### D83-10: final-bundle-validation-proof.txt stale size

**Supervisor finding:** Size 5,794,220 bytes but actual is 6,022,869 bytes.
**Classification:** CONFIRMED_CARRIED_TO_R84
**Root cause:** Proof file not updated when new metadata files were added to bundle.
**R84 repair:** Train C — update proof after each bundle build.

### D83-11: final-bundle-validation-proof.txt stale entry count

**Supervisor finding:** 3380 entries but actual is 3402.
**Classification:** CONFIRMED_CARRIED_TO_R84
**R84 repair:** Train C — same as D83-10.

### D83-12: final-bundle-validation-proof.txt stale SHA

**Supervisor finding:** SHA in proof does not match actual uploaded inner ZIP SHA.
**Classification:** CONFIRMED_CARRIED_TO_R84
**R84 repair:** Train C — same as D83-10.

### D83-13: state/current-state.md no_final_verdict

**Supervisor finding:** `Latest sprint: R83 - no_final_verdict`.
**Classification:** CONFIRMED_CARRIED_TO_R84
**Root cause:** State captured before final-verdict.md was complete.
**R84 repair:** Train V — run state_snapshot.py after all SHAs committed.

### D83-14: state/current-state.json no_final_verdict

**Supervisor finding:** JSON state reports no_final_verdict for R83.
**Classification:** CONFIRMED_CARRIED_TO_R84
**R84 repair:** Train V — same as D83-13.

### D83-15: master-plan.md stale

**Supervisor finding:** Old version text, stale historical authority material.
**Classification:** CONFIRMED_CARRIED_TO_R84
**R84 repair:** Train V — update master-plan after final R84 validation.

### D83-16: Raw install logs absent from review package

**Supervisor finding:** raw-package-install-log-summary.txt points to .local/ paths not in review package.
**Classification:** CONFIRMED_CARRIED_TO_R84
**R84 repair:** Train D + Train B — physically include raw install logs at top level of review package.

### D83-17: Raw negative proof logs absent from review package

**Supervisor finding:** raw-negative-proof-summary.txt points to .local/ paths not in review package.
**Classification:** CONFIRMED_CARRIED_TO_R84
**R84 repair:** Train D + Train B — same as D83-16.

### D83-18: ZST no-network install fails without dependency artifacts

**Supervisor finding:** zstandard>=0.21.0 required but no dependency-artifacts/ folder present.
**Classification:** CONFIRMED_CARRIED_TO_R84
**R84 repair:** Train J — classify ZST as DEPENDENCY_RESOLUTION_REQUIRED, include raw failing log.

### D83-19: .NET proof inherited from R82

**Supervisor finding:** .NET result says R82 source / no .NET changes in R83.
**Classification:** CONFIRMED_CARRIED_TO_R84
**R84 repair:** Train K — run fresh .NET tests and save to raw-dotnet-logs/.

### D83-20: Next-format advancement only HOLD

**Supervisor finding:** Netpbm HOLD_PRIMARY_FORMAT_PRIORITY, SYLK/DIF HOLD_PRIMARY_FORMAT_PRIORITY.
**Classification:** CONFIRMED_CARRIED_TO_R84
**R84 repair:** Trains M+N — real source improvements with tests.

## Summary

| Count | Classification |
|-------|----------------|
| 20 | CONFIRMED_CARRIED_TO_R84 |
| 0 | EXPLAINED_NOT_DEFECT |
| 0 | NOT_REPRODUCIBLE_WITH_EVIDENCE |

**DEFECT_LEDGER: COMPLETE**
