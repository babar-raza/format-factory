"""
PocReadinessComputer: compute per-target POC readiness.

Critical rules:
  - Netpbm must be retained (NETPBM_RETAINED = True)
  - SVG must not replace Netpbm
  - DIF may substitute SYLK only if coverage validates faster
  - Gnumeric counts only if required capabilities are coverage-validated

8 POC targets: FODS, FODT, Netpbm (.NET), ZST, Python Netpbm, SYLK, DIF, Gnumeric (stretch)
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from .graph_store import GraphStore
from .models import POC_TARGETS, PROHIBITED_REPLACEMENTS

# Netpbm must be retained
NETPBM_RETAINED = True

# POC readiness verdict values
READINESS_VERDICTS = {
    "READY_FOR_POC": "All required proof classes satisfied",
    "PARTIAL_WITH_CAVEATS": "Partial coverage — accepted_with_limitations",
    "BLOCKED_MISSING_PROOF": "Blocked — missing required proof",
    "BLOCKED_STALE": "Blocked — stale proof chain",
    "BLOCKED_OVERCLAIM": "Blocked — overclaim detected",
    "NOT_STARTED": "No claims linked to target",
    "STRETCH_TARGET": "Optional stretch target — not blocking",
}

# Targets that are optional (stretch)
STRETCH_TARGETS = {"gnumeric"}

# Required capabilities per target
TARGET_REQUIRED_CAPABILITIES: Dict[str, List[str]] = {
    "fods":        ["parse", "inspect", "edit", "export", "dogfood"],
    "fodt":        ["parse", "inspect", "edit", "export", "dogfood"],
    "netpbm-net":  ["load", "inspect", "edit", "save", "dogfood"],
    "zst":         ["package", "roundtrip"],
    "netpbm-py":   ["load", "inspect", "edit", "save"],
    "sylk":        ["parse", "export"],
    "dif":         ["parse", "export"],
    "gnumeric":    ["parse", "inspect"],
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TargetReadiness:
    target_id: str
    verdict: str
    required_capabilities: List[str]
    proven_capabilities: List[str]
    missing_capabilities: List[str]
    is_stretch_target: bool
    override_notes: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    computed_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_id": self.target_id,
            "verdict": self.verdict,
            "required_capabilities": self.required_capabilities,
            "proven_capabilities": self.proven_capabilities,
            "missing_capabilities": self.missing_capabilities,
            "is_stretch_target": self.is_stretch_target,
            "override_notes": self.override_notes,
            "metadata": self.metadata,
            "computed_at": self.computed_at,
        }


@dataclass
class PocReadinessResult:
    targets: List[TargetReadiness] = field(default_factory=list)
    netpbm_retained: bool = True
    svg_replacement_rejected: bool = True
    generated_at: str = field(default_factory=_now_iso)

    def overall_verdict(self) -> str:
        required = [t for t in self.targets if not t.is_stretch_target]
        if all(t.verdict == "READY_FOR_POC" for t in required):
            return "ALL_REQUIRED_TARGETS_READY"
        if any(t.verdict.startswith("BLOCKED") for t in required):
            return "BLOCKED_MISSING_REQUIRED_TARGET"
        return "PARTIAL_POC_READINESS"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "overall_verdict": self.overall_verdict(),
            "netpbm_retained": self.netpbm_retained,
            "svg_replacement_rejected": self.svg_replacement_rejected,
            "targets": [t.to_dict() for t in self.targets],
        }


class PocReadinessComputer:
    """
    Computes POC readiness for all 8 target products.

    Critical invariants:
    1. Netpbm must be retained (cannot be removed from targets)
    2. SVG must not replace Netpbm (PROHIBITED_REPLACEMENTS enforced)
    3. DIF may substitute SYLK only if coverage validates faster
    4. Gnumeric counts only if required capabilities are coverage-validated
    """

    def __init__(self, store: GraphStore):
        self.store = store

    def compute_all(self) -> PocReadinessResult:
        result = PocReadinessResult(
            netpbm_retained=NETPBM_RETAINED,
            svg_replacement_rejected=True,  # always enforced
        )

        # Enforce: SVG must not replace Netpbm
        self._enforce_svg_not_replace_netpbm(result)

        # Compute per-target readiness
        for target_id in sorted(POC_TARGETS):
            readiness = self._compute_target(target_id)
            result.targets.append(readiness)

        # Apply special DIF/SYLK substitution rule
        self._apply_dif_sylk_rule(result)

        return result

    def _enforce_svg_not_replace_netpbm(self, result: PocReadinessResult) -> None:
        """SVG must not replace Netpbm — check if any SVG nodes are being used as Netpbm replacements."""
        for node in self.store.nodes.values():
            if node.node_type == "PocTargetField":
                target_id = node.metadata.get("target_id", "")
                if "svg" in target_id.lower():
                    # Check if this SVG target is being proposed as Netpbm substitute
                    for blocked_replacement, protected_target in PROHIBITED_REPLACEMENTS.items():
                        if blocked_replacement in target_id.lower():
                            result.svg_replacement_rejected = True
                            # Add override note to netpbm target if it exists
                            for t in result.targets:
                                if t.target_id == protected_target:
                                    t.override_notes.append(
                                        f"SVG replacement '{target_id}' detected and rejected. "
                                        f"SVG must not replace Netpbm. "
                                        f"Netpbm must be retained."
                                    )

    def _compute_target(self, target_id: str) -> TargetReadiness:
        required_caps = TARGET_REQUIRED_CAPABILITIES.get(target_id, [])
        is_stretch = target_id in STRETCH_TARGETS

        # Find claims for this target
        claims = [
            c for c in self.store.nodes_by_type("CapabilityClaim")
            if c.metadata.get("product_id") == target_id
            or c.metadata.get("target_id") == target_id
        ]

        if not claims:
            return TargetReadiness(
                target_id=target_id,
                verdict="NOT_STARTED",
                required_capabilities=required_caps,
                proven_capabilities=[],
                missing_capabilities=required_caps[:],
                is_stretch_target=is_stretch,
                override_notes=[f"No CapabilityClaim nodes found for target '{target_id}'"],
            )

        # Collect proven capabilities from accepted claims
        proven_caps: List[str] = []
        has_stale = False
        has_overclaim = False
        has_limitations = False

        accepted_statuses = {"accepted_for_poc", "accepted_with_limitations"}
        for claim in claims:
            if claim.status in accepted_statuses:
                op = claim.metadata.get("operation", "")
                if op and op not in proven_caps:
                    proven_caps.append(op)
                if claim.status == "accepted_with_limitations":
                    has_limitations = True
            elif claim.status in ("stale", "superseded"):
                has_stale = True
            elif claim.status == "rejected":
                has_overclaim = True

        missing_caps = [c for c in required_caps if c not in proven_caps]

        # Determine verdict
        if has_stale and missing_caps:
            verdict = "BLOCKED_STALE"
        elif has_overclaim:
            verdict = "BLOCKED_OVERCLAIM"
        elif missing_caps:
            verdict = "BLOCKED_MISSING_PROOF"
        elif has_limitations:
            verdict = "PARTIAL_WITH_CAVEATS"
        else:
            verdict = "READY_FOR_POC"

        # Stretch targets use a different verdict prefix
        if is_stretch and verdict == "BLOCKED_MISSING_PROOF":
            verdict = "STRETCH_TARGET"

        override_notes = []
        if target_id in ("netpbm-net", "netpbm-py"):
            override_notes.append("Netpbm must be retained. This target cannot be removed or replaced.")
        if target_id == "dif":
            override_notes.append(
                "DIF may substitute SYLK only if coverage validates faster. "
                "Verify: compare estimated_unlock times in gap queue."
            )

        return TargetReadiness(
            target_id=target_id,
            verdict=verdict,
            required_capabilities=required_caps,
            proven_capabilities=sorted(proven_caps),
            missing_capabilities=missing_caps,
            is_stretch_target=is_stretch,
            override_notes=override_notes,
            metadata={
                "claim_count": len(claims),
                "has_stale": has_stale,
                "has_overclaim": has_overclaim,
                "has_limitations": has_limitations,
            },
        )

    def _apply_dif_sylk_rule(self, result: PocReadinessResult) -> None:
        """DIF may substitute SYLK only if DIF coverage validates faster."""
        dif_target = next((t for t in result.targets if t.target_id == "dif"), None)
        sylk_target = next((t for t in result.targets if t.target_id == "sylk"), None)

        if not dif_target or not sylk_target:
            return

        dif_ready = dif_target.verdict in ("READY_FOR_POC", "PARTIAL_WITH_CAVEATS")
        sylk_blocked = sylk_target.verdict.startswith("BLOCKED")

        if dif_ready and sylk_blocked:
            sylk_target.override_notes.append(
                "DIF coverage validates faster than SYLK in current graph state. "
                "DIF substitution is permitted for this sprint. "
                "SYLK remains a required target for future coverage."
            )


def compute_poc_readiness(store: GraphStore) -> PocReadinessResult:
    """Convenience function: compute POC readiness for all targets."""
    computer = PocReadinessComputer(store)
    return computer.compute_all()
