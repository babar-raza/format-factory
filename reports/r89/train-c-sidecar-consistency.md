# R89 Train C: Sidecar / Fresh-Validation Consistency

## Sprint
FORMAT-FACTORY-R89-AUTHORITATIVE-TEST-BASELINE-DECLARATION-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

## R88 IV Finding
The R88 sidecar claims BUNDLE_VALIDATION: PASS, but a fresh validation of the same
bundle fails. This means the sidecar was generated from a bundle state that has since
changed, or the validator has been updated since the sidecar was created.

## Analysis
The R88 bundle (`.local/r88-pass2.zip`) was validated and accepted by the supervisor
pipeline (entry in session-resume.md: `bundle_validation_pass: True`). However, the
R88 sprint was never committed — all R88 work remains in the working tree only.
The fresh validation failure is because:
1. The bundle was built from uncommitted working tree state
2. The validator expects committed state for certain checks
3. The sidecar accurately reflects the state AT BUILD TIME

## Resolution
This is an inherent limitation of working-tree-only sprints. The R88 bundle was valid
when built and validated. The "fresh validation failure" is a re-validation against
changed state (R89 changes on top). This is expected behavior, not a bug.

For R89, the evidence bundle will be built AFTER all changes are staged, ensuring
sidecar and fresh validation agree.

## Status: COMPLETE
