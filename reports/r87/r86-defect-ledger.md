# R86 Defect Ledger

## D87-R86-01: Uploaded artifact was inner evidence bundle
Severity: CRITICAL
Status: CONFIRMED_CARRIED_TO_R87
Detail: r86-pass2.zip (inner evidence ZIP) was uploaded instead of r86-supervisor-review-package.zip.
Fix: R87 Train B — final artifact selector enforcement.

## D87-R86-02: Validator fails without sidecar
Severity: CRITICAL
Status: CONFIRMED_CARRIED_TO_R87
Detail: Contract has sidecar_required: true but r86-pass2.zip was validated/submitted without --sidecar-proof.
Fix: R87 Train C — sidecar inclusion in review package.

## D87-R86-03: Missing AUTHORITATIVE_TEST_RESULT exact token
Severity: HIGH
Status: CONFIRMED_CARRIED_TO_R87
Detail: P-EVID-003 violation. Metadata file authoritative-test-result.txt has freeform text instead of exact AUTHORITATIVE_TEST_RESULT: N passed, M failed, K skipped.
Fix: R87 Train C — exact token metadata.

## D87-R86-04: Shallow metadata files
Severity: LOW
Status: CONFIRMED_CARRIED_TO_R87
Detail: test-file-inventory.txt (39 bytes) and zst-status.txt (37 bytes) below 50-byte minimum.
Fix: R87 metadata generation — ensure all files exceed minimum.

## D87-R86-05: Bundled supervisor outputs are stale R85
Severity: CRITICAL
Status: CONFIRMED_CARRIED_TO_R87
Detail: All reports/supervisor/ files in the bundle reference R85 sprint ID.
Fix: R87 Train E — fresh supervisor outputs from final artifact.

## D87-R86-06: state/current-state.md says R85
Severity: HIGH
Status: CONFIRMED_CARRIED_TO_R87
Detail: current-state.md: "Latest sprint: R85 - no_final_verdict"
Fix: R87 Train D — state closure.

## D87-R86-07: state/current-state.json says R85
Severity: HIGH
Status: CONFIRMED_CARRIED_TO_R87
Detail: current-state.json: latest_sprint_number=R85, verdict=no_final_verdict
Fix: R87 Train D — state closure.

## D87-R86-08: installed_artifact_policy: none
Severity: MEDIUM
Status: EXPLAINED_NOT_DEFECT
Detail: R86 contract intentionally used none because R86 focused on supervisor truth repair, not package proof. R87 will use wheel_and_sdist.

## D87-R86-09: No physical package artifacts in bundle
Severity: MEDIUM
Status: EXPLAINED_NOT_DEFECT
Detail: Consistent with installed_artifact_policy: none. R87 will include package-artifacts/.

## D87-R86-10: No final artifact authority JSON delivered
Severity: LOW
Status: EXPLAINED_NOT_DEFECT
Detail: r86-delivery-final-artifact-authority.json was built locally but inner bundle correctly uses delegation labels. The review package did include it.

## D87-R86-11: Next-sprint generator becomes repair-only
Severity: MEDIUM
Status: CONFIRMED_CARRIED_TO_R87
Detail: When critical contradictions exist, generated next-sprint has only repair tasks, no product lanes.
Fix: R87 Train F — broad next-sprint under repair conditions.

## D87-R86-12: poc-targets.yaml dated R85
Severity: LOW
Status: CONFIRMED_CARRIED_TO_R87
Detail: Still R85-dated and may overclaim.
Fix: R87 Train D/T — update POC matrix.
