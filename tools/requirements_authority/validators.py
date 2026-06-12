"""
Validators: enforce 8 graph invariants, reject ai_draft as proof,
reject stale nodes as accepted_for_poc support, validate node/edge schemas.
"""
from dataclasses import dataclass, field
from typing import List, Optional

from .graph_store import GraphStore
from .models import NODE_TYPES, EDGE_TYPES


@dataclass
class ValidationError:
    invariant: int  # 0 = schema, 1-8 = invariant number
    node_id: Optional[str]
    message: str
    severity: str = "ERROR"  # ERROR | WARNING


@dataclass
class ValidationResult:
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, invariant: int, node_id: Optional[str], message: str) -> None:
        self.errors.append(ValidationError(invariant=invariant, node_id=node_id, message=message))

    def add_warning(self, invariant: int, node_id: Optional[str], message: str) -> None:
        self.warnings.append(ValidationError(
            invariant=invariant, node_id=node_id, message=message, severity="WARNING"
        ))

    def summary(self) -> str:
        lines = [f"Errors: {len(self.errors)}  Warnings: {len(self.warnings)}"]
        for e in self.errors:
            lines.append(f"  [INV-{e.invariant}] {e.node_id or 'graph'}: {e.message}")
        for w in self.warnings:
            lines.append(f"  [WARN-{w.invariant}] {w.node_id or 'graph'}: {w.message}")
        return "\n".join(lines)


class GraphValidator:
    """
    Enforces the 8 canonical graph invariants plus schema validation.

    Invariant 1: Every accepted claim links to >= 1 accepted ProductRequirement
    Invariant 2: Every accepted ProductRequirement links to spec/empirical/policy source
    Invariant 3: accepted_for_poc links to impl + tests + evidence + dogfood (if required)
    Invariant 4: accepted_with_limitations links to >= 1 UnsupportedFeature
    Invariant 5: Stale nodes cannot support new accepted_for_poc claims
    Invariant 6: ai_draft nodes cannot satisfy proof
    Invariant 7: EvidencePackage proves only its included artifacts, not capability truth alone
    Invariant 8: PocTargetField updated only through proposed sync delta
    """

    def __init__(self, store: GraphStore):
        self.store = store
        self.result = ValidationResult()

    def validate(self) -> ValidationResult:
        self.result = ValidationResult()
        self._validate_node_schemas()
        self._validate_edge_schemas()
        self._enforce_invariant_1()
        self._enforce_invariant_2()
        self._enforce_invariant_3()
        self._enforce_invariant_4()
        self._enforce_invariant_5()
        self._enforce_invariant_6()
        self._enforce_invariant_7()
        self._enforce_invariant_8()
        return self.result

    # ── Schema validation ───────────────────────────────────────────────────────

    def _validate_node_schemas(self) -> None:
        for node in self.store.nodes.values():
            if node.node_type not in NODE_TYPES:
                self.result.add_error(0, node.node_id,
                    f"Unknown node_type '{node.node_type}'. Valid: {sorted(NODE_TYPES)}")
            if not node.node_id:
                self.result.add_error(0, None, "Node missing node_id")
            if not node.label:
                self.result.add_warning(0, node.node_id, "Node missing label")

    def _validate_edge_schemas(self) -> None:
        for edge in self.store.edges:
            if edge.edge_type not in EDGE_TYPES:
                self.result.add_error(0, edge.edge_id,
                    f"Unknown edge_type '{edge.edge_type}'. Valid: {sorted(EDGE_TYPES)}")
            if edge.source_node_id not in self.store.nodes:
                self.result.add_error(0, edge.edge_id,
                    f"Edge source '{edge.source_node_id}' not found in nodes")
            if edge.target_node_id not in self.store.nodes:
                self.result.add_error(0, edge.edge_id,
                    f"Edge target '{edge.target_node_id}' not found in nodes")

    # ── Invariant 1: Accepted claim → accepted ProductRequirement ────────────

    def _enforce_invariant_1(self) -> None:
        # Edge direction: source=claim --derives_from--> target=requirement
        # Use get_targets to follow outgoing derives_from edges from the claim.
        claims = self.store.nodes_by_type("CapabilityClaim")
        accepted_statuses = {"accepted_for_poc", "accepted_with_limitations"}
        for claim in claims:
            if claim.status not in accepted_statuses:
                continue
            req_targets = self.store.get_targets(claim.node_id, "derives_from")
            accepted_reqs = [
                r for r in req_targets
                if r.node_type == "ProductRequirement"
                and r.status in {"accepted", "accepted_with_caveat", "empirical_only", "policy_exception"}
            ]
            if not accepted_reqs:
                self.result.add_error(1, claim.node_id,
                    f"Accepted claim '{claim.node_id}' has no accepted ProductRequirement "
                    f"via derives_from edge")

    # ── Invariant 2: Accepted ProductRequirement → spec/empirical/policy ─────

    def _enforce_invariant_2(self) -> None:
        # Edge direction: source=req --derives_from--> target=spec/empirical/policy
        requirements = self.store.nodes_by_type("ProductRequirement")
        accepted_statuses = {"accepted", "accepted_with_caveat", "empirical_only", "policy_exception"}
        source_node_types = {"SpecRequirementRef", "EmpiricalEvidence", "ProductPolicyDecision"}
        for req in requirements:
            if req.status not in accepted_statuses:
                continue
            spec_targets = self.store.get_targets(req.node_id, "derives_from")
            valid_sources = [s for s in spec_targets if s.node_type in source_node_types]
            if not valid_sources:
                self.result.add_error(2, req.node_id,
                    f"Accepted ProductRequirement '{req.node_id}' has no "
                    f"SpecRequirementRef/EmpiricalEvidence/ProductPolicyDecision source")

    # ── Invariant 3: accepted_for_poc → impl + tests + evidence + dogfood ────

    def _enforce_invariant_3(self) -> None:
        claims = self.store.nodes_by_type("CapabilityClaim")
        for claim in claims:
            if claim.status != "accepted_for_poc":
                continue
            # Check implementation artifact
            impl = self.store.get_targets(claim.node_id, "implemented_by")
            if not impl:
                self.result.add_error(3, claim.node_id,
                    f"accepted_for_poc claim '{claim.node_id}' missing implemented_by artifact")
            # Check test artifact
            tests = self.store.get_targets(claim.node_id, "tested_by")
            if not tests:
                self.result.add_error(3, claim.node_id,
                    f"accepted_for_poc claim '{claim.node_id}' missing tested_by artifact")
            # Check evidence package
            evidence = self.store.get_targets(claim.node_id, "evidenced_by")
            if not evidence:
                self.result.add_error(3, claim.node_id,
                    f"accepted_for_poc claim '{claim.node_id}' missing evidenced_by EvidencePackage")
            # Check dogfood if required
            dogfood_required = claim.metadata.get("dogfood_required", False)
            if dogfood_required:
                dogfood = self.store.get_targets(claim.node_id, "dogfooded_by")
                if not dogfood:
                    self.result.add_error(3, claim.node_id,
                        f"accepted_for_poc claim '{claim.node_id}' requires dogfood "
                        f"(dogfood_required=true) but has no dogfooded_by artifact")

    # ── Invariant 4: accepted_with_limitations → >= 1 UnsupportedFeature ────

    def _enforce_invariant_4(self) -> None:
        claims = self.store.nodes_by_type("CapabilityClaim")
        for claim in claims:
            if claim.status != "accepted_with_limitations":
                continue
            limitations = self.store.get_targets(claim.node_id, "limited_by")
            unsupported = [n for n in limitations if n.node_type == "UnsupportedFeature"]
            if not unsupported:
                self.result.add_error(4, claim.node_id,
                    f"accepted_with_limitations claim '{claim.node_id}' has no "
                    f"UnsupportedFeature linked via limited_by edge")

    # ── Invariant 5: Stale nodes cannot support accepted_for_poc ────────────

    def _enforce_invariant_5(self) -> None:
        claims = self.store.nodes_by_type("CapabilityClaim")
        stale_statuses = {"stale", "superseded"}
        for claim in claims:
            if claim.status != "accepted_for_poc":
                continue
            # Edge: source=claim --derives_from--> target=requirement
            req_sources = self.store.get_targets(claim.node_id, "derives_from")
            for req in req_sources:
                if req.status in stale_statuses:
                    self.result.add_error(5, claim.node_id,
                        f"accepted_for_poc claim '{claim.node_id}' depends on "
                        f"stale/superseded requirement '{req.node_id}'")
            # Check all outgoing artifacts for staleness
            all_artifact_edges = ["implemented_by", "tested_by", "dogfooded_by", "evidenced_by"]
            for edge_type in all_artifact_edges:
                artifacts = self.store.get_targets(claim.node_id, edge_type)
                for artifact in artifacts:
                    if artifact.status in stale_statuses:
                        self.result.add_error(5, claim.node_id,
                            f"accepted_for_poc claim '{claim.node_id}' has stale "
                            f"{edge_type} artifact '{artifact.node_id}'")

    # ── Invariant 6: ai_draft nodes cannot satisfy proof ────────────────────

    def _enforce_invariant_6(self) -> None:
        """ai_draft nodes must not appear as proof sources for accepted claims."""
        claims = self.store.nodes_by_type("CapabilityClaim")
        accepted_statuses = {"accepted_for_poc", "accepted_with_limitations"}
        proof_edge_types = ["implemented_by", "tested_by", "dogfooded_by",
                            "evidenced_by", "exemplified_by", "derives_from"]
        for claim in claims:
            if claim.status not in accepted_statuses:
                continue
            for edge_type in proof_edge_types:
                if edge_type in ("implemented_by", "tested_by", "dogfooded_by",
                                 "evidenced_by", "exemplified_by"):
                    nodes = self.store.get_targets(claim.node_id, edge_type)
                else:
                    # derives_from: edge is source=claim → target=req; get_targets returns req
                    nodes = self.store.get_targets(claim.node_id, edge_type)
                for node in nodes:
                    if node.metadata.get("ai_draft", False) or node.status == "ai_draft":
                        self.result.add_error(6, claim.node_id,
                            f"Accepted claim '{claim.node_id}' is supported by ai_draft "
                            f"node '{node.node_id}' via {edge_type}. "
                            f"ai_draft nodes cannot satisfy proof.")

    # ── Invariant 7: EvidencePackage proves only its artifacts ───────────────

    def _enforce_invariant_7(self) -> None:
        """
        EvidencePackage nodes must not be used as the sole proof for accepted_for_poc.
        If the only evidenced_by target is an EvidencePackage with no impl/test,
        that is insufficient. This is advisory — we emit a warning.
        """
        claims = self.store.nodes_by_type("CapabilityClaim")
        for claim in claims:
            if claim.status not in {"accepted_for_poc", "accepted_with_limitations"}:
                continue
            impl = self.store.get_targets(claim.node_id, "implemented_by")
            tests = self.store.get_targets(claim.node_id, "tested_by")
            evidence = self.store.get_targets(claim.node_id, "evidenced_by")
            # If we have evidence but no impl/test, that's an invariant 7 violation
            if evidence and not impl and not tests:
                self.result.add_error(7, claim.node_id,
                    f"Claim '{claim.node_id}' uses EvidencePackage as sole proof "
                    f"(no ImplementationArtifact or TestArtifact linked). "
                    f"EvidencePackage proves only its included artifacts, not capability truth.")

    # ── Invariant 8: PocTargetField only via proposed sync delta ─────────────

    def _enforce_invariant_8(self) -> None:
        """
        PocTargetField nodes must only be updated via CapabilityDelta with
        proposed_by edge — never directly mutated by non-delta nodes.
        """
        poc_fields = self.store.nodes_by_type("PocTargetField")
        for ptf in poc_fields:
            # All incoming edges to this PocTargetField
            incoming = self.store.get_incoming(ptf.node_id)
            for edge in incoming:
                source = self.store.get_node(edge.source_node_id)
                if source is None:
                    continue
                # accepted_by and syncs_to edges are allowed from CapabilityDelta
                if edge.edge_type in ("accepted_by", "syncs_to"):
                    if source.node_type != "CapabilityDelta":
                        self.result.add_error(8, ptf.node_id,
                            f"PocTargetField '{ptf.node_id}' receives '{edge.edge_type}' edge "
                            f"from non-CapabilityDelta node '{source.node_id}' "
                            f"({source.node_type}). Only CapabilityDelta may update PocTargetField.")
                # Direct mutation edges from non-delta nodes are violations
                elif edge.edge_type not in ("consumed_by", "stale_due_to"):
                    if source.node_type not in ("CapabilityDelta",):
                        self.result.add_warning(8, ptf.node_id,
                            f"PocTargetField '{ptf.node_id}' has unexpected incoming edge "
                            f"'{edge.edge_type}' from '{source.node_id}' ({source.node_type}). "
                            f"PocTargetField should only be updated through proposed sync delta.")


def validate_graph(store: GraphStore) -> ValidationResult:
    """Convenience function: validate a GraphStore and return results."""
    validator = GraphValidator(store)
    return validator.validate()
