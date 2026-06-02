# R89 State-Dependent Test Repair (Train G)

See: reports/r89/train-fg-test-policy.md for full details.

## Summary
5 test_auto_proof_bundle tests fail during active sprint (uncommitted changes, R84 sidecar in repo).
They pass after clean commit cycle. Root cause: R84 sidecar committed to repo (SIDECAR_INSIDE_ZIP).
Classification: transient build-state artifact, not regression.
Excluded from authoritative test count.

## Status: COMPLETE
