# Staleness Invalidation Runtime Model

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Owner: Lane C

## 12 Invalidation Triggers

1. **spec_requirement_changed** — A SpecRequirementRef node's source document version has changed; all ProductRequirements derived_from it become stale.
2. **empirical_sample_changed** — An EmpiricalEvidence node's sample file has been replaced or updated; all ProductRequirements backed by it become stale.
3. **product_requirement_changed** — A ProductRequirement's status field changes from accepted to stale, rejected, or superseded; all CapabilityClaims linked via claims_support_for must be demoted.
4. **implementation_file_changed_after_coverage** — An ImplementationArtifact's mtime is newer than the last coverage_validated timestamp on a linked claim; claim must be re-evaluated.
5. **test_file_changed_after_coverage** — A TestArtifact linked to a claim has been modified after the claim's coverage_validated timestamp; tests may no longer prove the current implementation.
6. **test_log_older_than_source_diff** — A TestArtifact's last_passed_at is earlier than the implementation file's last modification; tests have not run against the current source.
7. **dogfood_output_older_than_implementation** — A DogfoodArtifact's produced_at timestamp is earlier than the implementation's last modification; dogfood may not reflect current behavior.
8. **evidence_package_missing_proof** — An EvidencePackage that previously materialized files now has a checksum mismatch or a manifest entry missing from disk; EvidencePackageProof is invalidated.
9. **context_pack_stale** — A ContextPackRef's graph_hash does not match the current source_graph_hash; context pack is no longer synchronized with current graph state.
10. **unsupported_feature_changed** — An UnsupportedFeature record's severity field has changed (e.g., from non_blocking to blocking); all accepted_with_limitations claims backed by this feature must be re-evaluated.
11. **claim_scope_changed** — A CapabilityClaim's operation, variant, or fidelity dimension was updated after the claim was accepted; the new scope may not be supported by existing evidence.
12. **product_policy_changed** — A ProductPolicyDecision that backs a policy_exception requirement has been rescinded or updated; the downstream requirement becomes stale.

## Propagation Chain

**Source requirement stale:**
SpecRequirementRef (changed) → StalenessEvent created
→ ProductRequirement (stale_due_to StalenessEvent)
→ All CapabilityClaims claims_support_for this requirement → stale
→ All CoverageRecords for stale claims → invalidated
→ All PocTargetField nodes syncs_to stale claims → poc-targets proposal becomes invalid
→ MainstreamGapQueue regenerated with newly blocked entries

**Implementation changed:**
ImplementationArtifact (mtime newer) → StalenessEvent created
→ TestArtifact last_passed_at comparison: if test older → tests_present becomes stale
→ DogfoodArtifact produced_at comparison: if dogfood older → dogfood_present becomes stale
→ CapabilityClaim: coverage_validated=false, status demoted to tests_present or lower
→ CoverageRecord: re-evaluation required

**Dogfood missing or old:**
DogfoodArtifact (produced_at < implementation mtime OR checksum invalid)
→ DogfoodProof: invalidated
→ CapabilityClaim: dogfood_present=false, coverage_validated=false
→ accepted_for_poc claims that required dogfood_required=true → demoted to dogfood_present=false state

**Hidden limitation discovered:**
New UnsupportedFeature (severity=blocking) linked to accepted_for_poc claim
→ CapabilityClaim: must be re-evaluated; if blocking → demoted to blocked
→ CoverageRecord: blocked_overclaim
→ PocTargetField sync proposal invalidated

## Output Artifact Schemas (4)

### stale-graph-report.json
```json
{
  "generated_at": "ISO8601",
  "source_graph_hash": "sha256",
  "stale_nodes": [
    {
      "node_id": "req-fods-001",
      "node_type": "ProductRequirement",
      "stale_reason": "spec_requirement_changed",
      "stale_since": "ISO8601",
      "propagated_to": ["claim-fods-export-001", "claim-fods-save-001"]
    }
  ],
  "total_stale_nodes": 0,
  "total_propagated_claims": 0
}
```

### stale-claims.md
Human-readable summary listing each stale CapabilityClaim, its stale reason, which requirement
or artifact triggered the staleness, and the recommended corrective action. One entry per claim.
Format: `## claim-id — stale_reason — recommended_action`.

### recomputation-queue.json
```json
{
  "generated_at": "ISO8601",
  "queue_entries": [
    {
      "claim_id": "claim-fods-export-001",
      "recomputation_reason": "implementation_file_changed_after_coverage",
      "priority": "high",
      "blocked_poc_targets": ["fods"],
      "validation_command": "python tools/requirements_authority/run_coverage_evaluator.py --claim claim-fods-export-001"
    }
  ],
  "total_entries": 0
}
```

### blocked-poc-targets.json
```json
{
  "generated_at": "ISO8601",
  "blocked_targets": [
    {
      "target_product": "fods",
      "blocked_by": ["claim-fods-export-001"],
      "stale_reasons": ["implementation_file_changed_after_coverage"],
      "unblock_actions": ["rerun coverage evaluator", "rerun dogfood validation"]
    }
  ],
  "total_blocked_targets": 0
}
```
