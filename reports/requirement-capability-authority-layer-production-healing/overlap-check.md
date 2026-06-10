# Overlap Check — File Ownership Map

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001

## Method

Each output path in file-ownership-map.json was checked to confirm it appears exactly once
across all lane assignments.

## Path Audit

| Output Path | Assigned Lane | Appears Once? |
|-------------|--------------|--------------|
| reports/.../00-preflight.md | Lane0 | YES |
| reports/.../current-git-status.txt | Lane0 | YES |
| reports/.../lane-ownership.md | Lane0 | YES |
| reports/.../file-ownership-map.json | Lane0 | YES |
| reports/.../overlap-check.md | Lane0 | YES |
| reports/.../taskcard-state.json | Lane0 | YES |
| reports/.../coordinator-integration-log.md | Lane0 | YES |
| reports/.../validate_healing_sprint.py | Lane0 | YES |
| reports/.../validation-results.md | Lane0 | YES |
| reports/.../validation-results.json | Lane0 | YES |
| reports/.../final-git-status.txt | Lane0 | YES |
| reports/.../review-package-proof.md | Lane0 | YES |
| docs/governance/requirement-capability-authority-layer.md | Lane0 | YES |
| docs/prompt-templates/requirement-capability-authority-layer-template.md | Lane0 | YES |
| docs/prompt-templates/capability-delta-proposal-template.md | Lane0 | YES |
| docs/prompt-templates/capability-coverage-validation-template.md | Lane0 | YES |
| docs/prompt-templates/mainstream-requirement-backed-handoff-template.md | Lane0 | YES |
| .local/evidences/.../evidence-declaration.yaml | Lane0 | YES |
| .local/evidences/.../evidence-manifest.yaml | Lane0 | YES |
| reports/.../00-production-blocker-review.md | LaneA | YES |
| reports/.../symptoms-root-causes-structural-weaknesses.md | LaneA | YES |
| reports/.../preserve-redesign-decision-matrix.md | LaneA | YES |
| reports/.../canonical-capability-proof-graph.md | LaneB | YES |
| reports/.../claim-scope-and-decomposition-model.md | LaneB | YES |
| reports/.../proof-sufficiency-model.md | LaneB | YES |
| reports/.../capability-family-model.md | LaneB | YES |
| reports/.../authority-lifecycle-redesign.md | LaneC | YES |
| reports/.../delta-and-promotion-runtime-model.md | LaneC | YES |
| reports/.../staleness-invalidation-runtime-model.md | LaneC | YES |
| reports/.../overclaim-remediation-model.md | LaneC | YES |
| reports/.../existing-system-migration-model.md | LaneD | YES |
| reports/.../mainstream-gap-queue-runtime-model.md | LaneD | YES |
| reports/.../supervisor-verdict-packet-model.md | LaneD | YES |
| reports/.../four-stream-consumer-contracts.md | LaneD | YES |
| reports/.../regression-and-replay-suite.md | LaneE | YES |
| reports/.../tradeoffs-risks-limits.md | LaneE | YES |
| reports/.../healed-final-single-go-...prompt.md | LaneE | YES |
| reports/.../final-adversarial-independent-verification.md | LaneE | YES |

## Result

CLEAN — All 39 output paths appear exactly once across all lane assignments.
No conflicts detected.
