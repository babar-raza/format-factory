# R66 Final State Ordering Proof

## Ordering Policy (R66)

The correct build order for a delivery package is:
1. All source/product changes committed
2. All state/taskcard/docs updates committed
3. All metadata proof files written with final values (NO placeholders)
4. Run invariants and capture output
5. Update state/current-state.md with final verdict (NOT IN_PROGRESS)
6. Update reports/rXX/final-verdict.md with final SHA values
7. Commit state + verdict
8. Build inner evidence ZIP
9. Generate external sidecar
10. Validate with sidecar → BUNDLE_VALIDATION: PASS
11. Validate without sidecar → FAIL (SIDECAR_REQUIRED)
12. Validate with wrong sidecar → FAIL (SHA_MISMATCH)
13. Build outer delivery package
14. Validate delivery package extraction

## R65 Defect (IV-R65-009)

R65 wrote placeholder metadata → built ZIP → updated metadata → did not rebuild ZIP.
This caused bundled state to say R65_IN_PROGRESS and bundled proofs to say "to be completed."

## R66 Compliance

R66 follows the ordering policy above. All metadata proofs are final before ZIP build.
State says final verdict, not IN_PROGRESS. Sidecar git_head matches actual final commit.

FINAL_STATE_ORDERING_PROOF: COMPLETE
