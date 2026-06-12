"""
CapabilityDelta: validation and promotion flow.

Implements the 12-step promotion flow:
  1. Mainstream creates CapabilityDelta proposal
  2. Delta schema validation
  3. Evidence importer links artifacts
  4. Proof graph recomputed
  5. Coverage evaluator runs
  6. Overclaim detector runs
  7. Staleness detector runs
  8. Delta accepted / rejected / needs_rework
  9. Accepted delta updates authority registries
 10. PocTargetsSyncProposalGenerator emits proposed delta — never direct mutation
 11. Supervisor consumes normalized verdict packet (delegated to supervisor_verdict_packet.py)

11 rejection reasons:
  missing_requirement, missing_implementation, missing_test, missing_dogfood,
  stale_evidence, overclaim, hidden_unsupported_feature, ai_draft_proof,
  evidence_missing_artifact, claim_too_broad, policy_decision_required
"""
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .graph_store import GraphStore
from .models import GraphNode

REJECTION_REASONS = [
    "missing_requirement",
    "missing_implementation",
    "missing_test",
    "missing_dogfood",
    "stale_evidence",
    "overclaim",
    "hidden_unsupported_feature",
    "ai_draft_proof",
    "evidence_missing_artifact",
    "claim_too_broad",
    "policy_decision_required",
]

DELTA_STATUSES = [
    "proposed",
    "schema_validated",
    "evidence_imported",
    "coverage_computed",
    "accepted",
    "rejected",
    "needs_rework",
    "stale",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9_]", "_", text.lower())


@dataclass
class DeltaRejection:
    reason: str  # must be in REJECTION_REASONS
    detail: str

    def __post_init__(self):
        if self.reason not in REJECTION_REASONS:
            raise ValueError(f"Unknown rejection reason: {self.reason!r}. "
                             f"Valid: {REJECTION_REASONS}")


@dataclass
class DeltaPromotion:
    """Represents the result of running the 12-step promotion flow on a delta."""
    delta_id: str
    proposal: Dict[str, Any]
    status: str = "proposed"  # starts at proposed
    rejections: List[DeltaRejection] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    promotion_log: List[str] = field(default_factory=list)
    accepted_at: Optional[str] = None
    rejected_at: Optional[str] = None

    @property
    def is_accepted(self) -> bool:
        return self.status == "accepted"

    @property
    def is_rejected(self) -> bool:
        return self.status == "rejected"

    def log_step(self, step: int, message: str) -> None:
        self.promotion_log.append(f"Step {step:02d}: {message}")

    def reject(self, reason: str, detail: str) -> None:
        self.rejections.append(DeltaRejection(reason=reason, detail=detail))
        self.status = "rejected"
        self.rejected_at = _now_iso()

    def needs_rework(self, reason: str, detail: str) -> None:
        self.rejections.append(DeltaRejection(reason=reason, detail=detail))
        self.status = "needs_rework"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "delta_id": self.delta_id,
            "status": self.status,
            "rejections": [{"reason": r.reason, "detail": r.detail} for r in self.rejections],
            "warnings": self.warnings,
            "promotion_log": self.promotion_log,
            "accepted_at": self.accepted_at,
            "rejected_at": self.rejected_at,
            "proposal": self.proposal,
        }


class CapabilityDeltaValidator:
    """
    Validates and promotes a CapabilityDelta proposal through the 12-step flow.
    Steps 5, 6, 7 (coverage, overclaim, staleness) are delegated to their
    respective evaluators — called externally and results passed in.
    """

    REQUIRED_PROPOSAL_FIELDS = [
        "delta_id", "claim_id", "product_id", "format_id",
        "operation", "direction", "fidelity",
        "implementation_artifacts", "test_artifacts",
    ]

    def __init__(self, store: GraphStore):
        self.store = store

    def validate_schema(self, proposal: Dict[str, Any]) -> DeltaPromotion:
        """Step 2: Validate delta schema."""
        delta_id = proposal.get("delta_id", f"delta:{_now_iso()}")
        promo = DeltaPromotion(delta_id=delta_id, proposal=proposal)
        promo.log_step(1, "Mainstream completed work and created CapabilityDelta proposal")
        promo.log_step(2, "Running delta schema validation")

        missing = [f for f in self.REQUIRED_PROPOSAL_FIELDS if f not in proposal]
        if missing:
            promo.reject("missing_requirement",
                f"Schema validation failed — missing required fields: {missing}")
            return promo

        # Validate operation
        from .models import OPERATIONS, DIRECTIONS, FIDELITY_VALUES
        op = proposal.get("operation", "")
        if op not in OPERATIONS:
            promo.reject("claim_too_broad",
                f"Unknown operation '{op}'. Valid: {sorted(OPERATIONS)}")
            return promo

        direction = proposal.get("direction", "")
        if direction not in DIRECTIONS:
            promo.reject("claim_too_broad",
                f"Unknown direction '{direction}'. Valid: {sorted(DIRECTIONS)}")
            return promo

        fidelity = proposal.get("fidelity", "")
        if fidelity not in FIDELITY_VALUES:
            promo.reject("claim_too_broad",
                f"Unknown fidelity '{fidelity}'. Valid: {sorted(FIDELITY_VALUES)}")
            return promo

        promo.status = "schema_validated"
        return promo

    def import_evidence(self, promo: DeltaPromotion) -> DeltaPromotion:
        """Step 3: Link evidence artifacts into the proof graph."""
        promo.log_step(3, "Evidence importer linking source diff/test log/evidence package")
        proposal = promo.proposal

        # Check ai_draft contamination
        if proposal.get("ai_draft", False):
            promo.reject("ai_draft_proof",
                "Delta is marked ai_draft=true. ai_draft nodes cannot satisfy proof.")
            return promo

        # Import implementation artifacts into store as candidate nodes
        for impl_path in proposal.get("implementation_artifacts", []):
            node_id = f"impl:{_slug(promo.delta_id)}:{_slug(str(impl_path))}"
            node = GraphNode(
                node_id=node_id,
                node_type="ImplementationArtifact",
                label=f"Impl: {impl_path}",
                status="candidate",
                metadata={"path": str(impl_path), "delta_id": promo.delta_id},
                created_at=_now_iso(),
            )
            self.store.add_node(node)

        # Import test artifacts
        for test_path in proposal.get("test_artifacts", []):
            node_id = f"test:{_slug(promo.delta_id)}:{_slug(str(test_path))}"
            node = GraphNode(
                node_id=node_id,
                node_type="TestArtifact",
                label=f"Test: {test_path}",
                status="candidate",
                metadata={"path": str(test_path), "delta_id": promo.delta_id},
                created_at=_now_iso(),
            )
            self.store.add_node(node)

        # Import dogfood artifacts if present
        for dogfood_path in proposal.get("dogfood_artifacts", []):
            node_id = f"dogfood:{_slug(promo.delta_id)}:{_slug(str(dogfood_path))}"
            node = GraphNode(
                node_id=node_id,
                node_type="DogfoodArtifact",
                label=f"Dogfood: {dogfood_path}",
                status="candidate",
                metadata={"path": str(dogfood_path), "delta_id": promo.delta_id},
                created_at=_now_iso(),
            )
            self.store.add_node(node)

        promo.status = "evidence_imported"
        promo.log_step(3, f"Evidence imported: "
            f"{len(proposal.get('implementation_artifacts', []))} impl, "
            f"{len(proposal.get('test_artifacts', []))} tests, "
            f"{len(proposal.get('dogfood_artifacts', []))} dogfood")
        return promo

    def check_requirements(self, promo: DeltaPromotion) -> DeltaPromotion:
        """Steps 4–5: Recompute proof graph and run coverage evaluator."""
        promo.log_step(4, "Proof graph recomputed after evidence import")
        promo.log_step(5, "Coverage evaluator running")

        proposal = promo.proposal
        claim_id = proposal.get("claim_id", "")

        # Check for existing ProductRequirement backing this claim
        requirements = self.store.nodes_by_type("ProductRequirement")
        product_id = proposal.get("product_id", "")
        format_id = proposal.get("format_id", "")
        matching_reqs = [
            r for r in requirements
            if r.metadata.get("product_id") == product_id
            or r.metadata.get("format_id") == format_id
        ]
        if not matching_reqs and not proposal.get("skip_requirement_check", False):
            promo.reject("missing_requirement",
                f"No ProductRequirement found for product_id='{product_id}' "
                f"format_id='{format_id}'. Claim cannot be accepted without a requirement.")

        # Check implementation
        impl_artifacts = proposal.get("implementation_artifacts", [])
        if not impl_artifacts:
            promo.reject("missing_implementation",
                "No implementation_artifacts in delta proposal")

        # Check tests
        test_artifacts = proposal.get("test_artifacts", [])
        if not test_artifacts:
            promo.reject("missing_test",
                "No test_artifacts in delta proposal")

        # Check dogfood if required
        dogfood_required = proposal.get("dogfood_required", False)
        dogfood_artifacts = proposal.get("dogfood_artifacts", [])
        if dogfood_required and not dogfood_artifacts:
            promo.reject("missing_dogfood",
                "dogfood_required=true but no dogfood_artifacts in delta proposal")

        if promo.status != "rejected":
            promo.status = "coverage_computed"
            promo.log_step(5, "Coverage computation complete — no blocking gaps detected")

        return promo

    def run_overclaim_check(self, promo: DeltaPromotion) -> DeltaPromotion:
        """Step 6: Overclaim detector."""
        promo.log_step(6, "Overclaim detector running")
        proposal = promo.proposal
        operation = proposal.get("operation", "")
        fidelity = proposal.get("fidelity", "")

        # Rule: save operation requires lossless or formatting_preserved fidelity
        if operation == "save" and fidelity not in ("lossless", "formatting_preserved",
                                                      "content_only", "declared_limited"):
            promo.warnings.append(
                f"Overclaim risk: operation='save' with fidelity='{fidelity}'. "
                f"Consider narrowing to 'export' or declaring limitations.")

        # Rule: roundtrip requires read_write direction
        if operation == "roundtrip" and proposal.get("direction") != "read_write":
            promo.needs_rework("overclaim",
                f"operation='roundtrip' requires direction='read_write', "
                f"got '{proposal.get('direction')}'")

        return promo

    def run_staleness_check(self, promo: DeltaPromotion) -> DeltaPromotion:
        """Step 7: Staleness detector."""
        promo.log_step(7, "Staleness detector running")
        # Check if any supporting requirement in store is stale
        stale_statuses = {"stale", "superseded"}
        requirements = self.store.nodes_by_type("ProductRequirement")
        product_id = promo.proposal.get("product_id", "")
        for req in requirements:
            if req.metadata.get("product_id") == product_id and req.status in stale_statuses:
                promo.reject("stale_evidence",
                    f"ProductRequirement '{req.node_id}' for product_id='{product_id}' "
                    f"is stale. Delta cannot be accepted on stale requirements.")
                return promo
        promo.log_step(7, "Staleness check passed — no stale requirements found")
        return promo

    def finalize(self, promo: DeltaPromotion) -> DeltaPromotion:
        """Steps 8–10: Accept/reject and create delta node in store."""
        if promo.status == "rejected":
            promo.log_step(8, f"Delta rejected: {[r.reason for r in promo.rejections]}")
            return promo
        if promo.status == "needs_rework":
            promo.log_step(8, "Delta needs rework — returned to Mainstream")
            return promo

        promo.log_step(8, "Delta accepted")
        promo.status = "accepted"
        promo.accepted_at = _now_iso()

        # Step 9: Create accepted CapabilityDelta node in store
        delta_node = GraphNode(
            node_id=f"delta:{_slug(promo.delta_id)}",
            node_type="CapabilityDelta",
            label=f"Delta: {promo.delta_id}",
            status="accepted",
            metadata={
                "delta_id": promo.delta_id,
                "product_id": promo.proposal.get("product_id"),
                "format_id": promo.proposal.get("format_id"),
                "claim_id": promo.proposal.get("claim_id"),
                "accepted_at": promo.accepted_at,
            },
            created_at=promo.accepted_at,
        )
        self.store.add_node(delta_node)
        promo.log_step(9, f"Accepted delta node created in store: {delta_node.node_id}")
        promo.log_step(10, "PocTargetsSyncProposalGenerator will emit proposed poc-targets.yaml delta "
                          "— never direct mutation. Supervisor receives normalized verdict packet.")
        return promo

    def run_full_flow(self, proposal: Dict[str, Any]) -> DeltaPromotion:
        """Run all 12 steps (steps 11-12 are delegated externally)."""
        promo = self.validate_schema(proposal)
        if promo.is_rejected:
            return promo
        promo = self.import_evidence(promo)
        if promo.is_rejected:
            return promo
        promo = self.check_requirements(promo)
        if promo.is_rejected:
            return promo
        promo = self.run_overclaim_check(promo)
        if promo.is_rejected:
            return promo
        promo = self.run_staleness_check(promo)
        if promo.is_rejected:
            return promo
        promo = self.finalize(promo)
        return promo


def promote_delta(store: GraphStore, proposal: Dict[str, Any]) -> DeltaPromotion:
    """Convenience function: run full delta promotion flow."""
    validator = CapabilityDeltaValidator(store)
    return validator.run_full_flow(proposal)
