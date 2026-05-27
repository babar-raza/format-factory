# R67 Work-Ahead W4 — Closeout Pipeline Automation

Sprint: FORMAT-FACTORY-R67-CLEAN-LOCAL-RC-PACKAGE-REPLAY-FINALITY-WORKAHEAD-MEGA-TRAIN-001

## Status

A closeout pipeline script was not fully implemented in R67 (scope would require
significant new tooling). The R67 closeout was executed manually following the
documented ordering policy.

## Ordering Policy (Canonical)

1. Finish source/test/tool changes
2. Run tests
3. Finalize manifests (final_git_head = current HEAD at pass 1)
4. Finalize state
5. Finalize final verdict (pass 1 SHA)
6. Run invariant/state tools
7. Generate metadata proofs
8. Build inner evidence ZIP
9. Generate external sidecar
10. Build outer delivery package
11. Validate delivery package extraction
12. Validate sidecar (pass/missing/wrong)
13. Re-extract and replay package tests
14. Update final_git_head to final commit SHA
15. Build pass 2 ZIP + sidecar
16. Build pass 2 delivery package

## Deferred to R68

Full `tools/evidence/run_closeout_pipeline.py` implementation.

W4_CLOSEOUT_PIPELINE: PARTIAL_DOCUMENTED
