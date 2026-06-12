"""
CapabilityCoverageEvaluator: binary PASS/FAIL per claim based on proof sufficiency.

Proof sufficiency levels (ordered):
  NO_PROOF → REQUIREMENT_ONLY → IMPLEMENTATION_ONLY → TESTED → EXAMPLED →
  DOGFOODED → COVERAGE_VALIDATED → ACCEPTED_FOR_POC → ACCEPTED_WITH_LIMITATIONS →
  REJECTED_OR_BLOCKED

Minimum proof per capability type:
  load/parse:    TESTED (impl + tests + requirement)
  inspect:       TESTED
  edit:          DOGFOODED (impl + tests + dogfood + requirement)
  save/write:    DOGFOODED
  export:        TESTED (but dogfood unlocks COVERAGE_VALIDATED)
  dogfood:       COVERAGE_VALIDATED (impl + tests + dogfood + evidence + requirement)
  package/import: TESTED + evidence package
  roundtrip:     DOGFOODED + evidence package
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .graph_store import GraphStore
from .models import GraphNode, PROOF_LEVELS

# Minimum proof level required per operation
OPERATION_MIN_PROOF: Dict[str, str] = {
    "load":      "TESTED",
    "parse":     "TESTED",
    "inspect":   "TESTED",
    "edit":      "DOGFOODED",
    "save":      "DOGFOODED",
    "write":     "DOGFOODED",
    "export":    "TESTED",
    "import":    "TESTED",
    "roundtrip": "DOGFOODED",
    "validate":  "TESTED",
    "package":   "TESTED",
    "dogfood":   "COVERAGE_VALIDATED",
}


@dataclass
class CoverageRecord:
    claim_id: str
    claim_label: str
    coverage_status: str  # see 12 status values from schema
    coverage_verdict: str  # PASS | FAIL | PARTIAL | BLOCKED | REQUIRES_POLICY
    proof_level: str       # current proof level achieved
    min_required_level: str
    missing_proof_types: List[str]
    blocking_reasons: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "claim_label": self.claim_label,
            "coverage_status": self.coverage_status,
            "coverage_verdict": self.coverage_verdict,
            "proof_level": self.proof_level,
            "min_required_level": self.min_required_level,
            "missing_proof_types": self.missing_proof_types,
            "blocking_reasons": self.blocking_reasons,
            "metadata": self.metadata,
        }


def _level_index(level: str) -> int:
    levels = list(PROOF_LEVELS)
    try:
        return levels.index(level)
    except ValueError:
        return -1


class CapabilityCoverageEvaluator:
    """
    Evaluates coverage for all CapabilityClaim nodes in a GraphStore.
    Returns CoverageRecord per claim with binary PASS/FAIL verdict.
    """

    def __init__(self, store: GraphStore):
        self.store = store

    def evaluate_all(self) -> List[CoverageRecord]:
        """Evaluate all CapabilityClaim nodes."""
        claims = self.store.nodes_by_type("CapabilityClaim")
        return [self.evaluate_claim(claim) for claim in
                sorted(claims, key=lambda c: c.node_id)]

    def evaluate_claim(self, claim: GraphNode) -> CoverageRecord:
        """Evaluate a single CapabilityClaim and return a CoverageRecord."""
        missing_proof: List[str] = []
        blocking_reasons: List[str] = []

        # Determine operation
        operation = claim.metadata.get("operation", "load")
        min_level = OPERATION_MIN_PROOF.get(operation, "TESTED")

        # Check requirement backing
        # Edge: source=claim --derives_from--> target=requirement
        req_sources = self.store.get_targets(claim.node_id, "derives_from")
        accepted_req_statuses = {"accepted", "accepted_with_caveat", "empirical_only", "policy_exception"}
        has_requirement = any(
            r.node_type == "ProductRequirement" and r.status in accepted_req_statuses
            for r in req_sources
        )
        if not has_requirement:
            missing_proof.append("RequirementProof")
            blocking_reasons.append("No accepted ProductRequirement linked via derives_from")

        # Check implementation
        impl_targets = self.store.get_targets(claim.node_id, "implemented_by")
        non_draft_impl = [n for n in impl_targets if not n.metadata.get("ai_draft", False)
                          and n.status != "stale"]
        has_implementation = bool(non_draft_impl)
        if not has_implementation:
            missing_proof.append("ImplementationProof")
            blocking_reasons.append("No non-stale, non-ai_draft ImplementationArtifact")

        # Check tests
        test_targets = self.store.get_targets(claim.node_id, "tested_by")
        non_draft_tests = [n for n in test_targets if not n.metadata.get("ai_draft", False)
                           and n.status != "stale"]
        has_tests = bool(non_draft_tests)
        if not has_tests:
            missing_proof.append("TestProof")
            blocking_reasons.append("No TestArtifact linked via tested_by (or all stale/ai_draft)")

        # Check examples (optional for some types)
        example_targets = self.store.get_targets(claim.node_id, "exemplified_by")
        has_example = bool(example_targets)

        # Check dogfood
        dogfood_targets = self.store.get_targets(claim.node_id, "dogfooded_by")
        non_draft_dogfood = [n for n in dogfood_targets if not n.metadata.get("ai_draft", False)
                             and n.status != "stale"]
        has_dogfood = bool(non_draft_dogfood)
        dogfood_required = claim.metadata.get("dogfood_required", False)
        if dogfood_required and not has_dogfood:
            missing_proof.append("DogfoodProof")
            blocking_reasons.append("dogfood_required=true but no DogfoodArtifact linked")

        # Check evidence package
        evidence_targets = self.store.get_targets(claim.node_id, "evidenced_by")
        has_evidence = bool(evidence_targets)
        needs_evidence = operation in ("package", "roundtrip", "dogfood")
        if needs_evidence and not has_evidence:
            missing_proof.append("EvidencePackageProof")
            blocking_reasons.append(f"operation='{operation}' requires EvidencePackage")

        # Check UnsupportedFeature for accepted_with_limitations
        if claim.status == "accepted_with_limitations":
            limitations = self.store.get_targets(claim.node_id, "limited_by")
            has_limitation = any(n.node_type == "UnsupportedFeature" for n in limitations)
            if not has_limitation:
                missing_proof.append("LimitationProof")
                blocking_reasons.append("accepted_with_limitations requires UnsupportedFeature node")

        # Check freshness (stale requirement → FreshnessProof violation)
        stale_statuses = {"stale", "superseded"}
        stale_reqs = [r for r in req_sources if r.status in stale_statuses]
        if stale_reqs:
            missing_proof.append("FreshnessProof")
            blocking_reasons.append(f"Supporting requirement(s) stale: {[r.node_id for r in stale_reqs]}")

        # Compute achieved proof level
        achieved_level = self._compute_proof_level(
            has_requirement, has_implementation, has_tests,
            has_example, has_dogfood, has_evidence, claim
        )

        # Determine verdict
        if blocking_reasons:
            coverage_status = self._blocking_status(missing_proof)
            verdict = "BLOCKED"
        elif _level_index(achieved_level) >= _level_index(min_level):
            coverage_status = "clean"
            verdict = "PASS"
        else:
            coverage_status = "partial_with_known_limitations"
            verdict = "PARTIAL"

        # Policy exception required?
        if "policy_decision_required" in claim.metadata.get("flags", []):
            coverage_status = "requires_policy_decision"
            verdict = "REQUIRES_POLICY"

        return CoverageRecord(
            claim_id=claim.node_id,
            claim_label=claim.label,
            coverage_status=coverage_status,
            coverage_verdict=verdict,
            proof_level=achieved_level,
            min_required_level=min_level,
            missing_proof_types=missing_proof,
            blocking_reasons=blocking_reasons,
            metadata={
                "operation": operation,
                "dogfood_required": dogfood_required,
                "has_requirement": has_requirement,
                "has_implementation": has_implementation,
                "has_tests": has_tests,
                "has_dogfood": has_dogfood,
                "has_evidence": has_evidence,
            },
        )

    def _compute_proof_level(
        self, has_req: bool, has_impl: bool, has_tests: bool,
        has_example: bool, has_dogfood: bool, has_evidence: bool,
        claim: GraphNode,
    ) -> str:
        """Return the highest proof level achieved."""
        if not has_req and not has_impl:
            return "NO_PROOF"
        if has_req and not has_impl:
            return "REQUIREMENT_ONLY"
        if has_impl and not has_tests:
            return "IMPLEMENTATION_ONLY"
        if has_tests and not has_example and not has_dogfood and not has_evidence:
            return "TESTED"
        if has_example and not has_dogfood and not has_evidence:
            return "EXAMPLED"
        if has_dogfood and not has_evidence:
            return "DOGFOODED"
        if has_evidence:
            status = claim.status
            if status == "accepted_for_poc":
                return "ACCEPTED_FOR_POC"
            if status == "accepted_with_limitations":
                return "ACCEPTED_WITH_LIMITATIONS"
            if status in ("rejected", "blocked"):
                return "REJECTED_OR_BLOCKED"
            return "COVERAGE_VALIDATED"
        return "TESTED"

    def _blocking_status(self, missing: List[str]) -> str:
        if "RequirementProof" in missing:
            return "blocked_missing_requirement"
        if "ImplementationProof" in missing:
            return "blocked_missing_implementation"
        if "TestProof" in missing:
            return "blocked_missing_test"
        if "DogfoodProof" in missing:
            return "blocked_missing_dogfood"
        if "EvidencePackageProof" in missing:
            return "blocked_missing_evidence"
        if "FreshnessProof" in missing:
            return "blocked_stale_requirement"
        if "LimitationProof" in missing:
            return "blocked_overclaim"
        return "blocked_missing_requirement"

    def compute_summary(self, records: List[CoverageRecord]) -> Dict[str, Any]:
        """Return aggregated summary across all records."""
        total = len(records)
        passed = sum(1 for r in records if r.coverage_verdict == "PASS")
        blocked = sum(1 for r in records if r.coverage_verdict == "BLOCKED")
        partial = sum(1 for r in records if r.coverage_verdict == "PARTIAL")
        policy = sum(1 for r in records if r.coverage_verdict == "REQUIRES_POLICY")
        return {
            "total_claims": total,
            "passed": passed,
            "blocked": blocked,
            "partial": partial,
            "requires_policy": policy,
            "coverage_pct": round(100 * passed / total, 1) if total else 0.0,
            "overall_verdict": "COVERAGE_CLEAN" if blocked == 0 and total > 0 and passed > 0
                               else ("COVERAGE_PARTIAL_WITH_CAVEATS" if partial > 0
                                     else "COVERAGE_BLOCKED"),
        }


def evaluate_coverage(store: GraphStore) -> List[CoverageRecord]:
    """Convenience function: evaluate all claims in a store."""
    evaluator = CapabilityCoverageEvaluator(store)
    return evaluator.evaluate_all()
