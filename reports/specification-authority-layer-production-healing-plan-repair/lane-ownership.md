# Lane Ownership
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-HEALING-PLAN-REPAIR-001

## Lane Table

| Lane | Owner | Taskcards | Output Files |
|------|-------|-----------|-------------|
| 0 | Coordinator | TC-REPAIR-000, TC-REPAIR-013b | lane-ownership.md, file-ownership-map.json, overlap-check.md, taskcard-state.json, coordinator-integration-log.md, review-package-proof.md, evidence-declaration.yaml, evidence-manifest.yaml |
| A | Review agent | TC-REPAIR-001, TC-HARD-001 | 00-review.md, final-plan-hardening-review.md |
| B | Repair agent | TC-REPAIR-002..010, TC-HARD-002..010 | gap-analysis.md, repair-decision-log.md, final-plan-hardening-diff.md |
| C | Prompt/Validation agent | TC-REPAIR-011, TC-REPAIR-012, TC-REPAIR-013a, TC-HARD-011, TC-HARD-012 | repaired-final-single-go-execution-prompt.md, final-adversarial-independent-verification.md, validation-results.md, final-git-status.txt, final-ready-to-send-execution-prompt.md, final-plan-validation.md |

## All Output Files by Lane

### Lane 0 (Coordinator)
- reports/specification-authority-layer-production-healing-plan-repair/lane-ownership.md
- reports/specification-authority-layer-production-healing-plan-repair/file-ownership-map.json
- reports/specification-authority-layer-production-healing-plan-repair/overlap-check.md
- reports/specification-authority-layer-production-healing-plan-repair/taskcard-state.json
- reports/specification-authority-layer-production-healing-plan-repair/coordinator-integration-log.md
- reports/specification-authority-layer-production-healing-plan-repair/review-package-proof.md
- .local/evidences/specification-authority-layer-production-healing-plan-repair/evidence-declaration.yaml
- .local/evidences/specification-authority-layer-production-healing-plan-repair/evidence-manifest.yaml
- .local/supervisor/reviews/specification-authority-layer-production-healing-plan-repair/declaration-review-package.zip

### Lane A (Review)
- reports/specification-authority-layer-production-healing-plan-repair/00-review.md
- reports/specification-authority-layer-production-healing-plan-repair/final-plan-hardening-review.md

### Lane B (Repair)
- reports/specification-authority-layer-production-healing-plan-repair/gap-analysis.md
- reports/specification-authority-layer-production-healing-plan-repair/repair-decision-log.md
- reports/specification-authority-layer-production-healing-plan-repair/final-plan-hardening-diff.md

### Lane C (Prompt + Validation)
- reports/specification-authority-layer-production-healing-plan-repair/repaired-final-single-go-execution-prompt.md
- reports/specification-authority-layer-production-healing-plan-repair/final-adversarial-independent-verification.md
- reports/specification-authority-layer-production-healing-plan-repair/validation-results.md
- reports/specification-authority-layer-production-healing-plan-repair/final-git-status.txt
- reports/specification-authority-layer-production-healing-plan-repair/final-ready-to-send-execution-prompt.md
- reports/specification-authority-layer-production-healing-plan-repair/final-plan-validation.md

### Preflight (not a lane — generated before lane work)
- reports/specification-authority-layer-production-healing-plan-repair/00-preflight.md
- reports/specification-authority-layer-production-healing-plan-repair/current-git-status.txt

## Evidence Root Labels

- REPAIR_SPRINT_EVIDENCE_ROOT: .local/evidences/specification-authority-layer-production-healing-plan-repair/
- HEALING_SPRINT_EVIDENCE_ROOT: .local/evidences/specification-authority-layer-production-healing/ (NOT YET CREATED)
- REPAIR_SPRINT_REVIEW_ROOT: .local/supervisor/reviews/specification-authority-layer-production-healing-plan-repair/
- HEALING_SPRINT_REVIEW_ROOT: .local/supervisor/reviews/specification-authority-layer-production-healing/ (NOT YET CREATED)
