# Final Adversarial Independent Verification

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Owner: Lane E
Mode: Adversarial — answer as a reviewer who is trying to find flaws

## 22 Questions

### (1) Does this healing sprint solve a real production problem?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/00-production-blocker-review.md
Rationale: The production problem is documented in 10 questions. Prior plan could not prevent false PASS, gap selection was ad hoc, Supervisor read heterogeneous prose, and staleness did not propagate. All these are structural defects, not cosmetic ones. The healing sprint explicitly addresses all 10.

### (2) Does the plan go beyond file and taskcard generation?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/canonical-capability-proof-graph.md; delta-and-promotion-runtime-model.md; authority-lifecycle-redesign.md
Rationale: The plan defines a proof graph with 18 node types, 19 edge types, and 8 invariants. It defines 4 state machines with named actors. It defines a 12-step delta promotion flow. It defines a 12-trigger staleness engine. These are operational system specifications, not artifact lists.

### (3) Does the plan define a canonical proof graph?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/canonical-capability-proof-graph.md
Rationale: 18 node types defined. 19 edge types defined. 8 numbered invariants. Storage model (JSONL). 4 query patterns with concrete examples. The graph is defined as deterministically recomputable from registries and imports.

### (4) Does the plan define claim-scope decomposition?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/claim-scope-and-decomposition-model.md
Rationale: 12 claim dimensions defined. 12 operation values. 6 direction values. 8 fidelity values. 8 decomposition rules. 7 product-specific examples (FODS, FODT, Netpbm, ZST, Python Netpbm, SYLK, DIF). Both LOAD_EXPORT and declared_limited are present in the model.

### (5) Does the plan define proof sufficiency by capability type?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/proof-sufficiency-model.md
Rationale: 9 proof classes with required fields, accepted sources, rejection cases, freshness rules, and relation to claim status. 10 sufficiency levels in order from NO_PROOF to REJECTED_OR_BLOCKED. 8 capability types with minimum proof specification. FreshnessProof and DOGFOODED both present.

### (6) Does the plan define lifecycle transitions with named actors?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/authority-lifecycle-redesign.md
Rationale: ProductRequirement (10 states), CapabilityClaim (13 states), CapabilityDelta (8 states), CoverageRecord (12 states) — all with state definitions, transition events, and named actor (Mainstream, Supervisor, StalenessInvalidationEngine, CapabilityCoverageEvaluator, Specification Authority). Acceleration is labeled ai_draft only.

### (7) Does the plan define the delta promotion runtime?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/delta-and-promotion-runtime-model.md
Rationale: 12 steps defined from Mainstream work to Supervisor verdict. 11 rejection reasons. "never direct mutation" for poc-targets. PocTargetsSyncProposalGenerator named in step 11.

### (8) Does the plan define staleness and invalidation propagation?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/staleness-invalidation-runtime-model.md
Rationale: 12 triggers numbered. Full propagation chain documented (source requirement → claim → coverage → poc target). 4 output artifact schemas with JSON examples including recomputation-queue.json.

### (9) Does the plan define overclaim remediation, not just detection?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/overclaim-remediation-model.md
Rationale: 10 overclaim patterns with specific remediation actions per pattern. Remediation enum includes narrow_claim and split_claim. 5 product examples. Remediation default is decomposition, not rejection.

### (10) Does the plan define migration from existing systems?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/existing-system-migration-model.md
Rationale: 13 input sources. 9 importer output types. 5 import rules including declared_not_verified and poc-targets-as-candidate-not-authority. 6 migration phases (Phase 0 through Phase 5). declared_not_verified and Phase 0 both present.

### (11) Does the plan preserve poc-targets.yaml as a dashboard?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/preserve-redesign-decision-matrix.md; four-stream-consumer-contracts.md
Rationale: poc-targets.yaml is in the Preserve column: "Read-only for queries; write only via proposed sync delta." The supervisor contract explicitly states Supervisor cannot directly mutate poc-targets.yaml. The delta runtime model confirms PocTargetsSyncProposalGenerator is required for any update.

### (12) Does the plan prevent direct poc-targets authority mutation?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/delta-and-promotion-runtime-model.md; regression-and-replay-suite.md (test category 25); healed-final-single-go-...prompt.md
Rationale: Step 11 of the delta runtime: "never direct mutation." Test category 25 verifies no direct poc-targets.yaml write. All consumer contracts explicitly state they cannot mutate poc-targets.yaml directly. Healed prompt includes this in hard prohibitions.

### (13) Does the plan produce a Mainstream gap queue from proof state?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/mainstream-gap-queue-runtime-model.md
Rationale: 11-step deterministic algorithm. 10 priority scoring fields. 15 queue entry fields. 6 product examples. dogfood_unlock_score and estimated_unlock both present. Algorithm is deterministic (same graph state → same queue order).

### (14) Does the plan produce a Supervisor verdict packet?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/supervisor-verdict-packet-model.md
Rationale: 16 packet fields specified with type, description, and required status. 9 supervisor decision values. ≥4 false pass risk cases. ≥3 false stop risk cases. source_graph_hash and false_stop_risks both present.

### (15) Does the plan protect against AI drafts as authority?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/canonical-capability-proof-graph.md (invariant 6); authority-lifecycle-redesign.md (Acceleration labeled ai_draft only); healed-final-single-go-...prompt.md (ai_draft rejected as proof)
Rationale: Graph invariant 6 explicitly states ai_draft nodes are excluded from evaluator traversal. The Acceleration consumer contract states all outputs are advisory; ai_draft=true on all Acceleration-produced nodes. Test category 13 verifies ai_draft is rejected as proof.

### (16) Does the plan handle empirical evidence with caveats?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/proof-sufficiency-model.md; tradeoffs-risks-limits.md; regression-and-replay-suite.md (fixture pack F); capability-family-model.md
Rationale: EmpiricalEvidence is a valid RequirementProof source. ProductRequirement can have status=empirical_only with caveat. Fixture pack F demonstrates accepted DIF empirical-only claim with visible caveat. Tradeoffs explicitly states empirical evidence is allowed but must be marked.

### (17) Does the plan handle accepted_with_limitations visibly?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/canonical-capability-proof-graph.md (invariant 4); supervisor-verdict-packet-model.md (unsupported_features field); four-stream-consumer-contracts.md
Rationale: Graph invariant 4 requires UnsupportedFeature records for accepted_with_limitations. The SupervisorVerdictPacket field 8 (unsupported_features) is a required array. All consumer contracts state they must receive UnsupportedFeature records. The tradeoffs section states accepted_with_limitations must be visible downstream.

### (18) Does the plan include golden replay regression packs?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/regression-and-replay-suite.md; healed-final-single-go-...prompt.md
Rationale: 25 test categories numbered. 6 fixture packs defined (A: FODS clean, B: FODT overclaim, C: Netpbm variant, D: ZST empirical, E: SYLK missing dogfood, F: DIF caveated). Determinism test defined (3 reruns, hash must match). healed prompt includes all 6 fixture pack definitions.

### (19) Does the plan avoid evidence metadata as a sprint goal?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/tradeoffs-risks-limits.md (balanced rule 4); preserve-redesign-decision-matrix.md (Remove/avoid section)
Rationale: Balanced rule 4 explicitly states: "Evidence repair is not product progress unless it affects proof validity." The remove/avoid section lists "evidence metadata polishing as sprint goal" in the Remove/avoid group. Non-blocking cosmetic evidence repair must not count as product progress.

### (20) Does the plan provide a self-contained MWP execution prompt?

PASS
Evidence: reports/requirement-capability-authority-layer-production-healing/healed-final-single-go-requirement-capability-authority-layer-mwp-execution-prompt.md (333 lines)
Rationale: 333 lines (> 300 required). All 22 required keywords present (verified by grep). All 13 tool paths listed. 6 golden replay fixture packs defined. Final response contract defined with 3 allowed verdict values. PYTHON fallback and REPO_ROOT resolution embedded. Hard prohibitions, MWP goals, product targets, and authority boundary reminders all self-contained.

### (21) Does the plan keep product implementation out of the healing sprint?

PASS
Evidence: 00-preflight.md (dirty state classification); coordinator-integration-log.md (forbidden paths); all taskcard allowed_paths fields
Rationale: Every taskcard has forbidden_paths: src/net/**, src/python/**, tests/net/**, tests/python/**. The healing sprint writes only to reports/requirement-capability-authority-layer-production-healing/, docs/governance/, docs/prompt-templates/, and .local/evidences/. No product source was modified. The git status at sprint close will confirm no forbidden-path changes.

### (22) Is the next sprint capable of building the operational MWP?

PASS
Evidence: healed-final-single-go-requirement-capability-authority-layer-mwp-execution-prompt.md; all Lane A–E design documents
Rationale: The healed prompt is self-contained with: embedded proof graph model, claim decomposition rules, proof sufficiency by type, 13 required tools with exact paths, 13 required output artifacts with exact paths, 6 golden replay fixture definitions, migration protocol, delta flow summary, staleness summary, overclaim remediation summary, final response contract with 3 allowed verdict values. An execution agent can begin building immediately from this prompt without reading other documents.

---

## Verdict Summary

| Range | Count |
|-------|-------|
| PASS | 22 |
| PARTIAL | 0 |
| FAIL | 0 |

Overall: REQUIREMENT_CAPABILITY_AUTHORITY_LAYER_PLAN_HEALED_READY_FOR_MWP_EXECUTION
