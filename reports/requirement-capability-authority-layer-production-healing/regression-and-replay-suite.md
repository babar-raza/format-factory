# Regression and Golden Replay Suite Specification

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Owner: Lane E

## 25 Numbered Test Categories

1. **clean_proof_graph** — Given a graph with all required proof classes present and no stale events: CapabilityCoverageEvaluator returns COVERAGE_CLEAN. Expected CoverageRecord status: clean.

2. **missing_requirement** — Graph has CapabilityClaim with no claims_support_for edge to any ProductRequirement. Expected CoverageRecord status: blocked_missing_requirement.

3. **missing_implementation** — Graph has CapabilityClaim with requirement_linked but no implemented_by edge. Expected CoverageRecord status: blocked_missing_implementation.

4. **missing_test** — Graph has CapabilityClaim with implementation_present but no tested_by edge. Expected CoverageRecord status: blocked_missing_test.

5. **missing_dogfood** — Graph has CapabilityClaim in capability family with dogfood_required=true; no dogfooded_by edge. Expected CoverageRecord status: blocked_missing_dogfood.

6. **stale_implementation_after_coverage** — Graph has CapabilityClaim with coverage_validated; then StalenessEvent created because ImplementationArtifact mtime > coverage_validated timestamp. Expected: claim demoted to stale; CoverageRecord invalidated.

7. **stale_dogfood** — DogfoodArtifact produced_at is older than ImplementationArtifact last modification. Expected StalenessEvent created; dogfood_present demoted to false; CoverageRecord: blocked_missing_dogfood.

8. **hidden_unsupported_feature** — Claim is accepted_for_poc but a blocking UnsupportedFeature node exists without a blocked_by edge. OverclaimDetector must flag this. Expected: delta rejected(hidden_unsupported_feature).

9. **declared_non_blocking_unsupported_feature** — Claim has UnsupportedFeature with severity=non_blocking; linked via limited_by. Expected: claim accepted_with_limitations; CoverageRecord: partial_with_known_limitations.

10. **overbroad_full_support_claim** — Claim scope=full_support; only parse proof linked. OverclaimDetector flags pattern 1. Expected: delta rejected(overclaim); decomposition recommended (split_claim: PARSE accepted + SAVE blocked).

11. **parse_only_correctly_accepted_as_parse_only** — Claim scope=parse; parse TestArtifact linked; no save artifact. OverclaimDetector does not flag. Expected: CoverageRecord clean; claim accepted at parse scope.

12. **export_not_accepted_as_save** — Claim scope=save; only DogfoodArtifact in different format linked. OverclaimDetector flags pattern 2. Expected: delta rejected(overclaim); downgrade to export claim recommended.

13. **ai_draft_rejected_as_proof** — TestArtifact node has ai_draft=true. CapabilityCoverageEvaluator excludes it from TestProof evaluation. Expected: CoverageRecord blocked_missing_test (ai_draft test does not count).

14. **empirical_only_with_caveat** — ProductRequirement derived_from EmpiricalEvidence only (no SpecRequirementRef). Requirement accepted as empirical_only. Expected: downstream CapabilityClaim accepted_with_limitations with caveat "empirical_only source".

15. **policy_exception_requires_decision_id** — CapabilityClaim needs ProductPolicyDecision but decision_id is null. Expected: CoverageRecord: requires_policy_decision; delta rejected(policy_decision_required).

16. **evidence_declares_file_not_materialized** — EvidencePackage in graph has materialized=false (declared but ZIP not built). Expected: EvidencePackageProof invalid; CoverageRecord blocked_missing_evidence.

17. **poc_targets_imported_status_not_accepted_as_authority** — poc-targets.yaml imported with status=PASS for a target. No CapabilityDelta or CoverageRecord exists for the backing claim. Expected: claim status=candidate; PocTargetField syncs_to edge not created; PASS not propagated.

18. **delta_accepted** — Full delta flow: Step 1–12 all pass. Expected: CapabilityDelta status=accepted; CapabilityClaim status=accepted_for_poc; CoverageRecord=clean; PocTargetsSyncProposalGenerator emits proposal.

19. **delta_rejected** — Delta submitted with missing_test. Step 6 (coverage evaluator) returns COVERAGE_BLOCKED_missing_test. Expected: CapabilityDelta status=rejected; rejection_reason=missing_test; claim remains at prior state.

20. **supervisor_verdict_packet_generated** — SupervisorVerdictPacketGenerator runs on a graph with 3 claims (1 clean, 1 blocked, 1 stale). Expected: packet has 16 fields; claims_checked=3; recommended_supervisor_decision computed.

21. **gap_queue_deterministic** — MainstreamGapQueueGenerator run twice on the same graph snapshot (same source_graph_hash). Expected: both runs produce identical gap_id order and priority_score values.

22. **same_inputs_same_graph_hash** — Given identical capability-graph-nodes.jsonl and capability-graph-edges.jsonl content across 3 reruns: source_graph_hash must be identical in all 3. Expected: hash=IDENTICAL across all runs.

23. **stale_chain_invalidates_readiness** — SpecRequirementRef changes version → ProductRequirement stale → CapabilityClaim stale → CoverageRecord invalidated → PocTargetField sync proposal blocked. Expected: full propagation chain verified end-to-end.

24. **accepted_with_limitations_requires_unsupported_feature** — CapabilityDelta submitted with accepted_with_limitations target but no UnsupportedFeature node linked. Expected: delta rejected(hidden_unsupported_feature); evaluator requires at least one limited_by edge.

25. **no_direct_poc_targets_mutation** — PocTargetsSyncProposalGenerator emits proposal but no tool directly writes poc-targets.yaml. Expected: poc-targets.yaml content unchanged until Supervisor explicitly accepts the proposal and authorizes the sync write.

## 6 Golden Replay Fixture Packs

Each fixture pack contains: input spec (nodes.jsonl + edges.jsonl) and expected output (CoverageRecord + verdict).

### Fixture Pack A: Clean FODS Export Claim
**Input nodes:** ProductRequirement(req-fods-export-001, accepted, derives_from spec-odf-1.3), CapabilityClaim(claim-fods-export-001, coverage_validated), ImplementationArtifact(fods-impl-001), TestArtifact(fods-test-001, last_passed_at=2026-06-01), DogfoodArtifact(fods-dog-001, checksum=abc123, produced_at=2026-06-01)
**Input edges:** derives_from(req-fods-export-001 → spec-odf-1.3), claims_support_for(claim-fods-export-001 → req-fods-export-001), implemented_by, tested_by, dogfooded_by (all linked)
**Expected CoverageRecord:** status=clean, missing_proof_types=[]
**Expected verdict:** ACCEPT_PRODUCT_PROGRESS

### Fixture Pack B: FODT Export-Only-Not-Save Overclaim
**Input nodes:** CapabilityClaim(claim-fodt-save-001, operation=save), TestArtifact with DogfoodArtifact in CSV format (different format output)
**Input edges:** implemented_by, tested_by, dogfooded_by (DogfoodArtifact is CSV, not FODT)
**Expected CoverageRecord:** status=blocked_overclaim
**Expected verdict:** REJECT_OVERCLAIM; remediation=downgrade_status (create export claim instead of save)

### Fixture Pack C: Netpbm Partial Variant Coverage
**Input nodes:** CapabilityClaim(claim-netpbm-all-variants, variant=all_variants), TestArtifact covering P3 only
**Input edges:** tested_by(claim → test-P3); no test for P6
**Expected CoverageRecord:** status=blocked_overclaim (variant=all_variants overbroad)
**Expected verdict:** REJECT_OVERCLAIM; remediation=split_claim (P3 accepted, P6 blocked)

### Fixture Pack D: ZST Roundtrip Clean
**Input nodes:** ProductRequirement(req-zst-roundtrip, empirical_only), CapabilityClaim(claim-zst-roundtrip, operation=roundtrip), ImplementationArtifact, TestArtifact (last_passed_at fresh), DogfoodArtifact (byte-identical output verified)
**Input edges:** All required edges present; empirical_only requirement accepted
**Expected CoverageRecord:** status=partial_with_known_limitations (empirical_only source caveat)
**Expected verdict:** ACCEPT_WITH_LIMITATIONS

### Fixture Pack E: SYLK Missing Dogfood
**Input nodes:** ProductRequirement(accepted), CapabilityClaim(claim-sylk-csv-export, dogfood_required=true), ImplementationArtifact(present), TestArtifact(present), no DogfoodArtifact
**Input edges:** implemented_by and tested_by present; no dogfooded_by edge
**Expected CoverageRecord:** status=blocked_missing_dogfood
**Expected verdict:** BLOCK_MISSING_DOGFOOD

### Fixture Pack F: DIF Empirical-Only Caveated
**Input nodes:** ProductRequirement(req-dif-parse, empirical_only=true, accepted_with_caveat), CapabilityClaim(claim-dif-parse, operation=parse), ImplementationArtifact, TestArtifact (linked); DogfoodArtifact with validator_used="manual format inspection"
**Input edges:** All required; derives_from links to EmpiricalEvidence (no SpecRequirementRef)
**Expected CoverageRecord:** status=partial_with_known_limitations (caveat: empirical_only_source)
**Expected verdict:** ACCEPT_WITH_LIMITATIONS (with visible empirical caveat in unsupported_features)

## Determinism Test Definition

**Name:** graph_hash_determinism
**Method:** Given the same capability-graph-nodes.jsonl and capability-graph-edges.jsonl fixture files (byte-identical), run CapabilityCoverageEvaluator 3 times independently (separate process, separate call). Compare source_graph_hash across all 3 runs.
**Pass condition:** source_graph_hash is identical across all 3 runs.
**Fail condition:** Any difference in source_graph_hash between runs.
**Additional check:** coverage_records array contents must also be identical across all 3 runs for the same input.
**Scope:** Applies to all 6 fixture packs above. Each pack must produce the same hash and the same verdict on every run.
