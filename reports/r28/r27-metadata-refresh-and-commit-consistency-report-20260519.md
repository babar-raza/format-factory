# R27 Metadata Refresh and Commit Consistency Report
# Sprint: FORMAT-FACTORY-R28-GATE5-GATE7-ORACLE-FUZZ-XCF-ZPAQ-G11-C9-PUBLICATION-HARDENING-001
# Date: 2026-05-19

## Classification: R27_METADATA_CONSISTENT

## R27 Gate 4 Sprint (Non-AI)
- Sprint ID: FORMAT-FACTORY-R27-GATE4-PROTOTYPES-G11-C7-C8-HARDENING-PUBLICATION-PACKET-AND-METADATA-SYNC-001
- Verdict: R27_COMPLETE
- Primary commit: 684c4a7
- Post-commit refresh: 33d12c7 (updates PENDING to PASS in sprint-overview.md)
- BUNDLE_VALIDATION: PASS
- Evidence bundle: .local/evidence-bundles/r27-gate4/bundle.zip
- Evidence contract: tools/evidence/contracts/r27-gate4-prototypes-g11-c7-c8-publication.yaml
- Required repo files: 33 (all present at commit 684c4a7)

## R27 AI Sprint
- Sprint ID: FORMAT-FACTORY-R27-AI-PLATFORM-FULL-GOVERNED-IMPLEMENTATION-CYCLE-001
- Commits: cb7e05c, da4bcde, 69c4c18
- BUNDLE_VALIDATION: PASS
- Evidence bundle: .local/evidence-bundles/r27-ai-platform-full-cycle-20260519.zip

## Commit Consistency Note
- R27_METADATA_HAS_NONBLOCKING_COMMIT_NOTE: 33d12c7 is not in the R27 evidence bundle because it was the post-bundle refresh commit. The bundle was built at commit 684c4a7 (standard pattern per evidence hygiene P-EVID-001). This is a known and expected pattern.
- 33d12c7 is present in live git log (verified during R28 preflight).

## Test Baselines Inherited
- Python (non-AI): 2013 passed, 13 skipped, 0 failed
- .NET FODS: 136/136 PASS
- .NET FODT: 124/124 PASS
- tests/ai: 202 passed
- tests/evidence: 122 passed
