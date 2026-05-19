# R29 Lane A: R28 Metadata Refresh and Commit Consistency Report
# Sprint: FORMAT-FACTORY-R29-MAIN-TRACK-MEGA-TRAIN-GATE6-GATE8-XCF-DIF-PPM-G11-PUBLICATION-CANDIDATES-001
# Date: 2026-05-19

## Classification: R28_METADATA_CONSISTENT

### Required Commits Verification

| SHA | Expected | Found | Subject |
|-----|----------|-------|---------|
| 1ecab67 | Yes | Yes | feat(r28): Gate 5 neutral model, Gate 6/7 initial, XCF G4, DIF/PPM candidates, C9 tests |
| 33d12c7 | Yes | Yes | chore(metadata): update R27 gate4 sprint-overview with BUNDLE_VALIDATION: PASS |
| 979a39d | Yes | Yes | fix(evidence): set min_metadata_count=30 for R27 gate4 evidence contract |
| 745c9d5 | Yes | Yes | fix(evidence): set min_metadata_count=5 for R27 gate4 evidence contract |
| 6da1db8 | Yes | Yes | chore(metadata): update R27 gate4 verdict with commit SHA 684c4a7 |
| 684c4a7 | Yes | Yes | feat(train): run R27 Gate4 prototypes and publication blocker reduction |
| 8f585ff | Check | Yes | chore(r28): update final-verdict with commit SHA and evidence bundle path |

### 8f585ff Status
- Present in live git log: YES
- Absent from uploaded R28 bundle: Expected -- bundle was built before this post-commit refresh
- Classification: Normal post-commit refresh pattern (bundle built at 1ecab67, refresh committed as 8f585ff)

### Live Metadata State
- reports/r28/final-verdict-gate5-prototypes-20260519.md: COMMIT_SHA=1ecab67, EVIDENCE_BUNDLE set
- reports/r28-gate5-sprint-metadata-20260519/sprint-overview.md: Commit SHA=1ecab67, BUNDLE_VALIDATION=PASS
- No PENDING values found in live repo

### Post-R28 Commits
- 2956213: feat(r28): AI platform hardening, E2E pilot, requirements pipeline, evidence automation
- 408fb27: chore(metadata): update R28 full-throttle sprint-overview with BUNDLE_VALIDATION: PASS
- These are from the concurrent R28 AI agent -- classified as OUT_OF_SCOPE for this non-AI sprint

### Conclusion
R28 metadata is fully consistent. No repair needed. 8f585ff exists and represents the expected post-commit refresh pattern.
