# Known Failure Regression Map
Sprint: FORMAT-FACTORY-AUTHORITY-LAYERS-AND-TARGET-WRITER-MEGA-TRAIN-R119-001

| ID | Bundle | Failure Mode | Severity | Resolution | Test |
|----|--------|-------------|----------|-----------|------|
| KF-001 | Spec R3C (98) | review-package-proof.md flagged missing (post-cycle) | LOW | Protocol documented; proof file present | TestReviewPackageProofProtocol |
| KF-002 | RCA R1 (99) | Raw logs not in evidence_artifacts | MEDIUM | Explicit type:raw_log entries in R119 declaration | TestRawLogDetection |
| KF-003 | RCA R1 (99) | No sample output files | MEDIUM | FODS→CSV sample produced in Lane D | TestSampleOutputDetection |
| KF-004 | RCA R1 (99) | final-git-status.txt missing | MEDIUM | Created for R119 in rca-r1-repair/ | TestFinalGitStatus |
| KF-005 | RCA R1 (99) | evidence_quality_score 0.12 | HIGH | tests_supporting populated in R119 declaration | Evidence declaration |
| KF-006 | Both | FODS/FODT arch-blocked exports → Mainstream-Dogfood | HIGH | Fixed in R2 (select_poc_gaps.py); confirmed in R119 | TestBlockedGapIdsEmpty |
