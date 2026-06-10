# Delta and Promotion Runtime Model

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Owner: Lane C

## 12-Step End-to-End Flow

**Step 1:** Mainstream completes implementation, test, and dogfood work for a capability.
Mainstream records what was done: source file(s) changed, test file(s) added or updated,
dogfood output file(s) produced. Mainstream does NOT accept the capability claim; instead,
it assembles evidence references and proceeds to Step 2.

**Step 2:** Mainstream creates a CapabilityDelta proposal document using the
capability-delta-proposal-template. The delta references: claim_id, operation, format_id,
product_id, changed_source_files, new_test_files, dogfood_artifact_path, evidence_package_ref.
Delta status transitions to: proposed.

**Step 3:** Delta schema validation runs automatically. The delta document is validated
against the capability-delta-proposal-template schema. All required fields must be present;
no unfilled template tokens (e.g., {{PLACEHOLDER}}) are allowed. On pass: status →
schema_validated. On fail: status → rejected; blocker reason recorded.

**Step 4:** EvidenceGraphImporter runs. It reads all artifact references in the delta and
attempts to resolve them to graph nodes: source files → ImplementationArtifact nodes,
test files → TestArtifact nodes, dogfood file → DogfoodArtifact node, evidence package →
EvidencePackage node. Unresolvable references → rejected(missing_artifact). On pass:
graph edges created; status → evidence_imported.

**Step 5:** Proof graph is recomputed. With new nodes and edges from Step 4, the graph
evaluator recomputes all paths from the target CapabilityClaim to its roots
(ProductRequirement → SpecRequirementRef or source). The new source_graph_hash is recorded.

**Step 6:** CapabilityCoverageEvaluator runs on the CapabilityClaim referenced by the delta.
It evaluates all required proof classes for the claim's capability type (per proof-sufficiency-model).
For each proof class: PASS or FAIL. Aggregate result: COVERAGE_CLEAN or COVERAGE_BLOCKED_{reason}.
CoverageRecord is written. Status → coverage_computed.

**Step 7:** OverclaimDetector runs on the claim. It checks all 10 overclaim patterns
(see overclaim-remediation-model). If an overclaim is detected: decomposition action is
recommended. Claim may be split/narrowed before proceeding. If overclaim is blocking:
delta → rejected(overclaim). If overclaim is non-blocking: flag recorded; proceeds.

**Step 8:** StalenessInvalidationEngine runs for the delta's claim and all its dependency nodes.
It checks: are any linked ProductRequirements stale? Are TestArtifact last_passed_at fields
older than ImplementationArtifact mtime? Is DogfoodArtifact produced_at older than implementation?
If any staleness found: delta → rejected(stale_evidence). If clean: proceeds.

**Step 9:** Delta outcome:
- accepted → all checks passed; coverage_computed = COVERAGE_CLEAN; no overclaim; no staleness
- rejected → one or more checks failed; rejection_reason set (see 11 rejection reasons below)
- needs_rework → evaluator returned partial pass; Supervisor identifies corrective action; delta returned to Mainstream

**Step 10:** Accepted delta updates authority registries:
- CapabilityClaim status updated to coverage_validated or accepted_for_poc (pending Supervisor)
- CoverageRecord finalized
- New graph nodes and edges committed to capability-graph-nodes.jsonl and capability-graph-edges.jsonl
- Accepted delta itself becomes a graph node (CapabilityDelta status=accepted)

**Step 11:** PocTargetsSyncProposalGenerator emits a proposed update to poc-targets.yaml as a
structured delta artifact — **never direct mutation**. The proposal specifies: which field to
update, the new value, the claim_id backing the change, and the accepted delta reference.
Supervisor reviews the proposal and may accept or reject the sync. Only an accepted sync delta
causes the PocTargetField node to update its syncs_to edge.

**Step 12:** Supervisor consumes the normalized SupervisorVerdictPacket (16-field JSON, see
supervisor-verdict-packet-model) that includes the coverage record, claim status, delta
acceptance, any overclaim flags, and recommended decision. Supervisor verdict: one of 9 allowed
decision values (see supervisor-verdict-packet-model).

## 11 Rejection Reasons

1. **missing_requirement** — No accepted ProductRequirement is graph-linked to the claim
2. **missing_implementation** — No ImplementationArtifact graph-linked to the claim; or artifact is a stub
3. **missing_test** — No TestArtifact graph-linked to the claim
4. **missing_dogfood** — dogfood_required=true for capability type but no DogfoodArtifact linked or validated
5. **stale_evidence** — One or more dependency nodes (requirement, test, dogfood) are stale relative to implementation
6. **overclaim** — OverclaimDetector found an overbroad claim that requires decomposition before acceptance
7. **hidden_unsupported_feature** — A blocking UnsupportedFeature was detected but not declared in the delta
8. **ai_draft_proof** — An artifact in the delta has ai_draft=true; ai_draft nodes cannot satisfy proof
9. **evidence_missing_artifact** — EvidencePackage manifest lists an artifact that does not materialize
10. **claim_too_broad** — Claim scope dimensions (operation, variant, fidelity) are broader than evidence supports
11. **policy_decision_required** — Claim requires ProductPolicyDecision that has not been recorded
