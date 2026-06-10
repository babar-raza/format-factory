# Canonical Capability Proof Graph

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Owner: Lane B

## Node Types (18)

The Canonical Capability Proof Graph contains exactly 18 node types:

1. **ProductRequirement** — A capability requirement derived from spec, empirical evidence, or product policy. Has status: candidate | source_linked | accepted | accepted_with_caveat | empirical_only | policy_exception | stale | rejected | superseded
2. **CapabilityClaim** — A claim that a product supports a capability. Has status: candidate | requirement_linked | implementation_present | tests_present | examples_present | dogfood_present | coverage_validated | accepted_for_poc | accepted_with_limitations | stale | rejected | blocked | superseded
3. **ImplementationArtifact** — A source file or function that provides the implementation. References: file path, git commit hash, last_modified
4. **TestArtifact** — A test file or test function that validates the implementation. References: file path, test_id, last_passed_at
5. **ExampleArtifact** — An example file demonstrating usage. References: file path, format_id, example_type
6. **DogfoodArtifact** — A file produced by actually running the format operation end-to-end. References: file path, checksum, produced_at, validator_used
7. **EvidencePackage** — A ZIP bundle containing a manifest and materialized artifacts. References: zip_path, sha256, declared_at, materialized: true|false
8. **UnsupportedFeature** — A declared limitation or unsupported aspect of a capability claim. Fields: feature_name, severity (blocking|non_blocking), claim_id, discovered_at
9. **EmpiricalEvidence** — A file, sample, or observation used in lieu of a formal spec. References: source, sample_path, observation_date
10. **SpecRequirementRef** — A reference to a formal specification document or section. Fields: spec_name, version, section, url_or_path
11. **ProductPolicyDecision** — A recorded product decision that overrides or supplements spec requirements. Fields: decision_id, decision_text, decided_by, decided_at
12. **ContextPackRef** — A reference to a context pack snapshot used for cross-sprint reference. Fields: context_pack_id, graph_hash, generated_at
13. **CoverageRecord** — A record of coverage evaluation result for a capability claim. Fields: claim_id, evaluation_status, missing_proof_types, evaluated_at
14. **CapabilityDelta** — A proposed change to capability authority state, submitted by Mainstream. Status: proposed | schema_validated | evidence_imported | coverage_computed | accepted | rejected | needs_rework | stale
15. **PocTargetField** — A field in poc-targets.yaml representing current dashboard status. Updated only through proposed sync delta, never directly.
16. **StreamHandoff** — A governed handoff artifact produced by Skills stream. Fields: handoff_id, required_claim_ids, transcript_path, verdict
17. **UsageRecord** — A record of actual usage of the format capability in downstream context. Fields: usage_id, context, verified_at
18. **StalenessEvent** — An event recording that a node was detected as stale. Fields: event_id, stale_node_id, stale_reason, detected_at, propagated_to

## Edge Types (19)

1. **derives_from** — ProductRequirement derives_from SpecRequirementRef or EmpiricalEvidence or ProductPolicyDecision
2. **claims_support_for** — CapabilityClaim claims_support_for ProductRequirement
3. **implemented_by** — CapabilityClaim implemented_by ImplementationArtifact
4. **tested_by** — CapabilityClaim tested_by TestArtifact
5. **exemplified_by** — CapabilityClaim exemplified_by ExampleArtifact
6. **dogfooded_by** — CapabilityClaim dogfooded_by DogfoodArtifact
7. **evidenced_by** — CapabilityClaim evidenced_by EvidencePackage; EvidencePackage evidenced_by individual artifact nodes
8. **limited_by** — CapabilityClaim limited_by UnsupportedFeature
9. **blocked_by** — CapabilityClaim blocked_by UnsupportedFeature (blocking severity)
10. **supersedes** — CapabilityClaim supersedes prior CapabilityClaim (when claim is upgraded or replaced)
11. **invalidates** — StalenessEvent invalidates any node it affects
12. **proposed_by** — CapabilityDelta proposed_by StreamHandoff or Mainstream work item reference
13. **accepted_by** — CapabilityDelta accepted_by Supervisor verdict with validation output
14. **syncs_to** — PocTargetField syncs_to CapabilityClaim (via accepted sync delta only)
15. **consumed_by** — CoverageRecord consumed_by SupervisorVerdictPacket; MainstreamGapQueue consumed_by Mainstream sprint
16. **stale_due_to** — CapabilityClaim or CoverageRecord stale_due_to StalenessEvent
17. **narrows** — CapabilityDelta narrows CapabilityClaim (decomposition result: narrowing scope)
18. **broadens** — CapabilityDelta broadens CapabilityClaim (claims broader scope — triggers overclaim check)
19. **conflicts_with** — CapabilityClaim conflicts_with another CapabilityClaim or UnsupportedFeature

## Graph Invariants (8)

(1) Every accepted CapabilityClaim must link via claims_support_for to at least one accepted ProductRequirement. A claim without an accepted requirement cannot be accepted_for_poc.

(2) Every accepted ProductRequirement must link via derives_from to at least one of: SpecRequirementRef, EmpiricalEvidence, or ProductPolicyDecision. A ProductRequirement without a source cannot be accepted.

(3) A CapabilityClaim in state accepted_for_poc must link to: at least one ImplementationArtifact (implemented_by), at least one TestArtifact (tested_by), at least one EvidencePackage with materialized=true (evidenced_by), and if dogfood_required=true for its capability family then at least one DogfoodArtifact (dogfooded_by).

(4) A CapabilityClaim in state accepted_with_limitations must link via limited_by to at least one UnsupportedFeature with severity=non_blocking. All non-blocking limitations must be declared; no hidden limitations are permitted.

(5) A node in state stale cannot support new accepted_for_poc transitions. If a ProductRequirement is stale, all CapabilityClaims it backs must be demoted to stale or needs_revalidation before any new accepted_for_poc is recorded.

(6) Nodes produced by ai_draft sources (ai_draft=true field on any artifact node) cannot satisfy any proof class requirement. ai_draft nodes may exist in the graph as advisory; they must not be traversed when evaluating proof sufficiency.

(7) An EvidencePackage proves only the artifacts it includes (listed in its manifest) and only when checksums match the declared values and the artifacts are graph-linked to a CapabilityClaim. An EvidencePackage does not prove capability truth in isolation.

(8) A PocTargetField must only be updated through a CapabilityDelta that is in state accepted, not through any direct write. The PocTargetsSyncProposalGenerator emits the proposed delta; the Supervisor accepts it; only then can the sync_to edge be recorded.

## Storage Model

Nodes are stored as JSONL (one JSON object per line) in `capability-graph-nodes.jsonl`.
Edges are stored as JSONL (one JSON object per line) in `capability-graph-edges.jsonl`.
The graph is deterministically recomputable from the authority registries and imported artifacts.
A graph hash (SHA-256 of the sorted nodes+edges content) is computed after each recomputation
and stored as `source_graph_hash` in the SupervisorVerdictPacket.

Node schema example:
```json
{"node_id": "req-fods-001", "node_type": "ProductRequirement", "status": "accepted", "format_id": "fods", "description": "...", "derives_from": ["spec-odf-1.3-section-5"], "ai_draft": false, "recorded_at": "2026-06-04"}
```

Edge schema example:
```json
{"edge_id": "e-001", "edge_type": "claims_support_for", "source_node_id": "claim-fods-export-001", "target_node_id": "req-fods-001", "recorded_at": "2026-06-04"}
```

## Query Patterns (4)

**Query 1: "Why is claim X not POC-ready?"**
Traverse: claim-fods-export-001 → claims_support_for → ProductRequirement (status?) → derives_from → SpecRequirementRef (exists?) → implemented_by → ImplementationArtifact (exists?) → tested_by → TestArtifact (linked?) → dogfooded_by → DogfoodArtifact (if required) → evidenced_by → EvidencePackage (materialized?). Return the first missing or stale link as the blocking reason.

**Query 2: "Which next artifact unblocks POC target FODS export?"**
Traverse: PocTargetField(fods, export) → syncs_to → CapabilityClaim → evaluate coverage: if missing tested_by → return "add TestArtifact linked to claim-fods-export-001". If missing dogfooded_by → return "add DogfoodArtifact for fods export operation".

**Query 3: "Which claims are stale?"**
SELECT all CapabilityClaim nodes where status = stale OR any incoming stale_due_to edge from a StalenessEvent. Return: claim_id, stale_reason, blocked_poc_targets.

**Query 4: "Which claims are overbroad?"**
SELECT all CapabilityClaim nodes where: claim operation dimension = 'roundtrip' but no DogfoodArtifact linked, OR operation = 'save' but only ExportArtifact linked, OR scope = 'all_variants' but TestArtifacts cover only one variant. Return: claim_id, overclaim_pattern, recommended_decomposition.
