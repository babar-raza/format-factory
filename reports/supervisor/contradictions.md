# Contradiction Detection Report
Sprint ID: unknown
Timestamp: 2026-06-02T14:25:12.551542
Overall: CRITICAL_CONTRADICTIONS
Autonomous continue: False
Critical: 2 | Warning: 1

## Contradictions

### [CRITICAL] 1. No final-verdict.md found in evidence bundle
Detail: Evidence bundles must contain a final-verdict.md

### [CRITICAL] 2. BUNDLE_VALIDATION: FAIL — evidence bundle did not pass validation
Detail: Existing validator (validate_evidence_bundle.py) reported BUNDLE_VALIDATION: FAIL. Sidecar proof is required but was not supplied.

### [WARNING] 3. Sprint ID not found in evidence bundle
Detail: Cannot verify sprint identity match with contract

## CRITICAL: Autonomous loop stopped.
CRITICAL contradictions require human review before continuing.
