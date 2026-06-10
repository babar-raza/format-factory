# File Ownership Matrix
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-IDEMPOTENCY-CONTRACTS-001
# Date: 2026-06-08

## Rules
- No lane edits files owned by another lane without a coordinator state-ledger entry
- Coordinator runs final overlap check before evidence declaration
- Every file appears exactly once in this matrix
- Every GR-TC taskcard maps to one lane

## Coordinator Lane
Owns (created by coordinator):
- reports/repeatability-governance-plan-healing/repaired-plan.md
- reports/repeatability-governance-plan-healing/state-ledger.jsonl
- reports/repeatability-governance-plan-healing/file-ownership-matrix.md
- .local/evidences/governance-repeatability-contracts-001/evidence-declaration.yaml
- .local/evidences/governance-repeatability-contracts-001/evidence-manifest.yaml

## Governance Contracts Lane (GR-TC-002, 003, 004)
Owns:
- docs/governance/execution-method-taxonomy.md
- docs/governance/repeatability-contract.md
- docs/governance/idempotency-contract.md
- docs/governance/legacy-manual-backfill-policy.md

## Schema Lane (GR-TC-005, 007-schema)
Owns:
- schemas/governance/execution-method-taxonomy.schema.json
- schemas/governance/product-mutation-evidence.schema.json
- schemas/governance/product-mutation-taskcard-state-machine.schema.json

## Taskcard + State Machine Lane (GR-TC-007, GR-TC-001 through 010 files)
Owns:
- docs/governance/product-mutation-taskcard-state-machine.md
- taskcards/governance-repeatability/GR-TC-001.yaml
- taskcards/governance-repeatability/GR-TC-002.yaml
- taskcards/governance-repeatability/GR-TC-003.yaml
- taskcards/governance-repeatability/GR-TC-004.yaml
- taskcards/governance-repeatability/GR-TC-005.yaml
- taskcards/governance-repeatability/GR-TC-006.yaml
- taskcards/governance-repeatability/GR-TC-007.yaml
- taskcards/governance-repeatability/GR-TC-008.yaml
- taskcards/governance-repeatability/GR-TC-009.yaml
- taskcards/governance-repeatability/GR-TC-010.yaml

## Legacy Backfill Lane (GR-TC-006)
Owns:
- .local/attribution/gnumeric/gnumeric_codec.py.attribution.yaml
- .local/attribution/tsv/tsv_parser.py.attribution.yaml
- .local/attribution/abw/abw_codec.py.attribution.yaml
- .local/attribution/ndjson/ndjson_codec.py.attribution.yaml
- .local/evidences/autonomous-execution-spine/evidence-declaration.yaml (add fields only)
- .supervisor/project-memory.md (governance_backfill_note field only)

## Validator Planning Lane (GR-TC-008)
Owns:
- reports/repeatability-governance-plan-healing/validator-hardening-plan.md

## Autonomy Boundary Lane (GR-TC-009)
Owns:
- reports/repeatability-governance-plan-healing/autonomy-boundary-handoff.md

## Execution Handoff Lane (GR-TC-010)
Owns:
- reports/repeatability-governance-plan-healing/final-single-go-execution-prompt.md

## Support Docs (Coordinator)
- reports/repeatability-governance-plan-healing/preflight-repo-workflow-review.md
- reports/repeatability-governance-plan-healing/adaptation-log.md
- reports/repeatability-governance-plan-healing/state-ledger-template.jsonl
- reports/repeatability-governance-plan-healing/plan-quality-review.md
- reports/repeatability-governance-plan-healing/healed-plan.md
