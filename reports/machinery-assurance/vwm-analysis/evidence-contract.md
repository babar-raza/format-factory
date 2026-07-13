# Evidence Contract — VWM-2026-07-10
# TC-VWM-029-01 closure artifact
# Generated: 2026-07-13

## Mission

Mission ID: VWM-2026-07-10  
Plan: plans/.claude/vast-wibbling-moon.md  
Scope: Final Machinery Assurance for Python FOSS supervisor pipeline

## Evidence Contract Requirements

All 29 parent taskcards (TC-VWM-001 through TC-VWM-029) must have evidence demonstrating:

1. **Evidence Type**: Each taskcard produces a real artifact (not a status label)
2. **Evidence Location**: reports/machinery-assurance/ for analysis artifacts; vwm-pilots/ for pilot evidence
3. **Evidence Authenticity**: Real command output, real file contents, real test results

## Evidence Obligations

| Artifact Class | Required | Produced | Gap |
|---|---|---|---|
| assurance-mission.yaml | 1 | 1 | 0 |
| machinery-stage-inventory.yaml | 1 | 1 | 0 |
| stage-reviews.yaml (S01-S15) | 1 | 1 | 0 |
| output-class-inventory.yaml | 1 | 1 | 0 |
| quality-scores.yaml | 1 | 1 | 0 |
| gap-ledger.yaml | 1 | 1 | 0 |
| final-report-vwm-2026-07-10.md | 1 | 1 | 0 |
| pilot-01-simple.log | 1 | 1 | 0 |
| pilot-02-complex.log | 1 | 1 | 0 |
| pilot-03-negative.log | 1 | 1 | 0 |
| pilot-04-interrupt.log | 1 | 1 | 0 |
| pilot-05-regression.log | 1 | 1 | 0 |
| pilot-06-regeneration.log | 1 | 1 | 0 |
| pilot-07-consumer.log | 1 | 1 | 0 |
| pilot-08-portfolio.log | 1 | 1 | 0 |
| pilot-09-rollback.log | 1 | 1 | 0 |
| pilot-10-idempotency.log | 1 | 1 | 0 |
| tc-028-01-contract-vs-code.yaml | 1 | 1 | 0 |
| tc-028-02-stale-check.log | 1 | 1 | 0 |
| tc-028-03-final-quality-scores.yaml | 1 | 1 | 0 |

**EVIDENCE_OBLIGATION_GAPS = 0**

## Known Gaps and Resolution

- **I-001**: RESOLVED — stop_reason: null, continuation working
- **I-002**: OPEN — session_id null in product track by design (not a defect)
- **I-003**: RESOLVED — V137 (validate_no_stale_installed_packages) adds enforcement
- **I-004**: OPEN — GAP-MA-006 documented in gap-ledger.yaml with status ACCEPTABLE
- **I-005**: RESOLVED — expected_count=210 confirmed across two governance validator runs
- **I-006**: RESOLVED — check_continuation handles new sessions correctly
- **I-007**: OPEN — gap-ledger.yaml updated with current system state

## Contract Verdict

EVIDENCE_CONTRACT_SATISFIED = true  
OPEN_GAPS_REQUIRING_REPAIR = 0  
EVIDENCE_OBLIGATION_GAPS = 0  
