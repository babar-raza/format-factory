# Lane Ownership — Requirement & Capability Authority Layer Production-Blocker Healing

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001

## Lane Model

**6 lanes total: Coordinator (Lane 0) + five execution lanes (A, B, C, D, E)**

| Lane ID | Role | Purpose | Owned Output Files |
|---------|------|---------|-------------------|
| Lane 0 | Coordinator / Evidence | Preflight reads, lane ownership, file map, taskcard-state JSON, validation script, evidence package, scope guard | 00-preflight.md, current-git-status.txt, lane-ownership.md, file-ownership-map.json, overlap-check.md, taskcard-state.json, coordinator-integration-log.md, validate_healing_sprint.py, validation-results.md, validation-results.json, final-git-status.txt, evidence-declaration.yaml (in .local), evidence-manifest.yaml (in .local), review-package-proof.md |
| Lane A | Production Reassessment | Diagnoses why prior plan is not production-ready; documents symptoms, root causes, structural weaknesses; produces preserve/redesign decision matrix | 00-production-blocker-review.md, symptoms-root-causes-structural-weaknesses.md, preserve-redesign-decision-matrix.md |
| Lane B | Proof Graph and Capability Semantics | Defines canonical proof graph (nodes, edges, invariants, storage, queries), claim scope decomposition model, proof sufficiency model by capability type, capability family model per POC target | canonical-capability-proof-graph.md, claim-scope-and-decomposition-model.md, proof-sufficiency-model.md, capability-family-model.md |
| Lane C | Authority Runtime | Specifies lifecycle state machines for all authority objects with transition actors; defines delta/promotion 12-step flow, staleness invalidation triggers and propagation, overclaim remediation per pattern | authority-lifecycle-redesign.md, delta-and-promotion-runtime-model.md, staleness-invalidation-runtime-model.md, overclaim-remediation-model.md |
| Lane D | Migration and Consumer Contracts | Specifies how existing assets are imported as candidates (not authority); defines Mainstream gap queue runtime algorithm; Supervisor verdict packet model; all 6 stream consumer contracts | existing-system-migration-model.md, mainstream-gap-queue-runtime-model.md, supervisor-verdict-packet-model.md, four-stream-consumer-contracts.md |
| Lane E | Regression and MWP Execution Prompt | Defines 25-category regression suite + 6 golden replay packs + determinism test; honest risk/tradeoff assessment; self-contained healed MWP execution prompt (>300 lines, 22 required keywords); adversarial independent verification (22 questions) | regression-and-replay-suite.md, tradeoffs-risks-limits.md, healed-final-single-go-requirement-capability-authority-layer-mwp-execution-prompt.md, final-adversarial-independent-verification.md |

## Coordination Protocol

- Coordinator reads all governance files before work starts (logged in coordinator-integration-log.md)
- Lanes A–E produce output files independently with no cross-lane file dependencies
- Lane E (TC-RCA-FINAL-001) depends on A–E outputs being complete before writing the healed prompt
- TC-RCA-FINAL-002 (adversarial IV) depends on TC-RCA-FINAL-001
- TC-RCA-VALIDATE-001 runs after all lane outputs exist
- TC-RCA-EVIDENCE-001 runs after TC-RCA-VALIDATE-001 PASS

## Governance doc outputs (Coordinator/Lane 0)

- docs/governance/requirement-capability-authority-layer.md
- docs/prompt-templates/requirement-capability-authority-layer-template.md
- docs/prompt-templates/capability-delta-proposal-template.md
- docs/prompt-templates/capability-coverage-validation-template.md
- docs/prompt-templates/mainstream-requirement-backed-handoff-template.md
