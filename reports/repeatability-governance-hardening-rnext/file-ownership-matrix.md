# File Ownership Matrix
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-LAYER-HARDENING-PILOTS-001
# Run ID: governance-repeatability-hardening-rnext
# Date: 2026-06-08

## Rules
- No lane edits files owned by another lane without a coordinator state-ledger entry
- Every file appears exactly once in this matrix
- Every GRH-TC taskcard maps to one lane

## Lane A: Coordinator
Owns:
- reports/repeatability-governance-hardening-rnext/00-preflight.md
- reports/repeatability-governance-hardening-rnext/file-ownership-matrix.md
- reports/repeatability-governance-hardening-rnext/state-ledger.jsonl
- .local/evidences/governance-repeatability-hardening-rnext/evidence-declaration.yaml
- taskcards/governance-repeatability-hardening/GRH-TC-001.yaml through GRH-TC-015.yaml

## Lane B: Manifest Consistency Repair (GRH-TC-002, GRH-TC-014)
Owns:
- reports/repeatability-governance-hardening-rnext/manifest-consistency-repair.md
- tests/supervisor/test_manifest_consistency.py

## Lane C: Evidence Quality Scoring Repair (GRH-TC-003)
Owns (source modification only):
- tools/supervisor/grade_declared_work.py (governance-exempt logic only)
- tests/supervisor/test_evidence_quality_governance_exempt.py

## Lane D: Adoption Compliance Repair (GRH-TC-004)
Owns (source modification only):
- tools/supervisor/validate_adoption_compliance.py (governance item type exemption only)
- tests/supervisor/test_adoption_compliance_governance_exempt.py

## Lane E: Validator Implementation (GRH-TC-005, GRH-TC-015)
Owns:
- tools/supervisor/governance_validators.py (new file)
- tests/supervisor/test_governance_validators.py (new file)
- tests/supervisor/test_governance_validators_integration.py (new file)

## Lane F: State Machine Enforcement (GRH-TC-006)
Owns:
- tests/supervisor/test_taskcard_state_machine.py (new file)
(governance_validators.py shared with Lane E)

## Lane G: Backfill Verification (GRH-TC-007)
Owns:
- taskcards/governance-repeatability/GR-REPLAY-001.yaml
- taskcards/governance-repeatability/GR-REPLAY-002.yaml
- taskcards/governance-repeatability/GR-REPLAY-003.yaml
- taskcards/governance-repeatability/GR-REPLAY-004.yaml

## Lane H: Governance Pilots (GRH-TC-008)
Owns:
- tests/supervisor/fixtures/governance-pilots/ (directory + 6 YAML fixtures)
- reports/repeatability-governance-hardening-rnext/pilot-results.md

## Lane I: Raw Logs + Sample Output Policy (GRH-TC-009)
Owns:
- reports/repeatability-governance-hardening-rnext/raw-logs/validator-tests.log
- reports/repeatability-governance-hardening-rnext/sample-output-policy.md

## Lane J: Product Safety Audit (GRH-TC-010)
Owns:
- reports/repeatability-governance-hardening-rnext/safety-audit.md

## Lane K: Prompt Quality Repair (GRH-TC-011)
Owns:
- reports/repeatability-governance-hardening-rnext/prompt-quality-report.md

## Lane L: Autonomy Boundary Contract (GRH-TC-012)
Owns:
- .supervisor/autonomy-boundary-contract.yaml (new file)

## Lane M: Final IV (GRH-TC-013)
Owns:
- .local/evidences/governance-repeatability-hardening-rnext/evidence-declaration.yaml
- (ZIP path: .local/supervisor/reviews/governance-repeatability-hardening-rnext/declaration-review-package.zip)
