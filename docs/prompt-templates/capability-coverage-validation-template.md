# Capability Coverage Validation Template

**Purpose:** Records the output of CapabilityCoverageEvaluator for a specific CapabilityClaim.
**Consumer:** SupervisorVerdictPacketGenerator, PocReadinessComputer, MainstreamGapQueueGenerator
**Produced by:** CapabilityCoverageEvaluator (automated tool: tools/requirements_authority/run_coverage_evaluator.py)
**Not produced by:** Mainstream, Acceleration, or any prose-based report

---

## Coverage Record Header

- record_id: (auto-assigned)
- claim_id: (the claim being evaluated)
- evaluated_at: (ISO8601 datetime)
- source_graph_hash: (SHA-256 of graph snapshot used for this evaluation)
- evaluator_version: (tool version or git commit)

## Proof Class Evaluation

For each required proof class for this capability type:

| Proof Class | Status | Missing or Blocker |
|-------------|--------|-------------------|
| RequirementProof | PASS / FAIL | (node_id or reason if FAIL) |
| ImplementationProof | PASS / FAIL | |
| TestProof | PASS / FAIL | |
| ExampleProof | N/A / PASS / FAIL | |
| DogfoodProof | N/A / PASS / FAIL | |
| EvidencePackageProof | N/A / PASS / FAIL | |
| LimitationProof | N/A / PASS / FAIL | |
| FreshnessProof | PASS / FAIL | |

## Staleness Check

- stale_events_present: (true / false)
- stale_event_ids: (list; empty if none)
- staleness_verdict: CLEAN / STALE

## Overclaim Check

- overclaim_detected: (true / false)
- overclaim_pattern: (1-10 or null)
- recommended_remediation: (enum value or null)

## Coverage Record Status

coverage_status: (one of)
- clean
- partial_with_known_limitations
- blocked_missing_requirement
- blocked_missing_implementation
- blocked_missing_test
- blocked_missing_example
- blocked_missing_dogfood
- blocked_stale_requirement
- blocked_overclaim
- blocked_missing_evidence
- requires_policy_decision

## Missing Proof Types

missing_proof_types: (list of proof class names that returned FAIL; empty if clean)

## Evaluator Output

coverage_verdict: COVERAGE_CLEAN | COVERAGE_PARTIAL | COVERAGE_BLOCKED_{REASON}
