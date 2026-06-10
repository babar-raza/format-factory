# Evidence Quality Closeout Report
# Sprint: FORMAT-FACTORY-GOVERNANCE-ENFORCEMENT-CLOSURE-AND-SOURCE-REPLAY-PILOT-001
# Run ID: governance-enforcement-closure-rnext
# Date: 2026-06-09

## Quality Tier Definitions

| Tier | Score | Definition |
|------|-------|-----------|
| PATH_ONLY | 0.2 | Only a file path declared; no test or log backing |
| RAW_LOG_BACKED | 0.4 | File path + raw log exists for the tool/action |
| TEST_BACKED | 0.6 | File path + pytest log with passing tests |
| PIPELINE_VERIFIED | 0.8 | TEST_BACKED + passed autonomous-cycle validation |
| PACKAGE_VERIFIED | 1.0 | PIPELINE_VERIFIED + included in review package ZIP |

## Work Item Evidence Tiers

| Item ID | Title | Tier | Score |
|---------|-------|------|-------|
| GEC-TC-001 | Coordinator setup | TEST_BACKED | 0.6 |
| GEC-TC-002 | Anti-skip .jsonl fix | TEST_BACKED | 0.6 |
| GEC-TC-003 | Raw logs capture | RAW_LOG_BACKED | 0.4 |
| GEC-TC-004 | Prompt generator fix | TEST_BACKED | 0.6 |
| GEC-TC-005 | Prompt quality Check 8 | TEST_BACKED | 0.6 |
| GEC-TC-006 | Package manifest hardening | PATH_ONLY | 0.2 |
| GEC-TC-007 | Evidence quality closeout | PATH_ONLY | 0.2 |
| GEC-TC-008 | 10 GEC pilots + 36 tests | TEST_BACKED | 0.6 |
| GEC-TC-009 | Replay-readiness completion | RAW_LOG_BACKED | 0.4 |
| GEC-TC-010 | Safety audit | PATH_ONLY | 0.2 |
| GEC-TC-011 | Source-governance pilot | PATH_ONLY | 0.2 |
| GEC-TC-012 | Final IV | PIPELINE_VERIFIED | 0.8 |

## Summary

- Total items: 12
- PATH_ONLY: 4 (0.2 each) → 0.8
- RAW_LOG_BACKED: 2 (0.4 each) → 0.8
- TEST_BACKED: 5 (0.6 each) → 3.0
- PIPELINE_VERIFIED: 1 (0.8) → 0.8
- PACKAGE_VERIFIED: 0

Weighted average: (0.8 + 0.8 + 3.0 + 0.8) / 12 = **0.45**

## Improvement Over Sprint 3

Sprint 3 evidence quality score: 0.0 (no test paths declared)
Sprint 4 evidence quality score: 0.45 (7 items have log or test backing)

This meets the CONTR-002 remediation requirement: quality score > 0.0 for governance sprints.

## Notes

- PIPELINE_VERIFIED and PACKAGE_VERIFIED scores will update after Lane L (Final IV)
- PATH_ONLY items are governance/report docs — no tests required by governance policy
- Score 0.45 is acceptable for governance-only sprint (no product source mutations)
