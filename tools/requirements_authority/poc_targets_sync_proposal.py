"""
PocTargetsSyncProposalGenerator: propose poc-targets.yaml delta — never apply directly.

Critical rule: PocTargetField updated only through proposed sync delta.
  - This tool NEVER modifies poc-targets.yaml directly.
  - It emits a proposed delta JSON file for human/Supervisor review.
  - No direct mutation of poc-targets.yaml or any authority file.
"""
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from .graph_store import GraphStore
from .poc_readiness import PocReadinessResult, TargetReadiness


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SyncDeltaEntry:
    """One proposed change for a POC target field."""
    target_id: str
    current_status: str       # imported from poc-targets.yaml (candidate — not authority)
    proposed_status: str      # computed from proof graph
    delta_type: str           # SET | UPGRADE | DOWNGRADE | NO_CHANGE
    justification: str
    required_claim_ids: List[str]
    evidence_package_refs: List[str]
    limitations: List[str]
    proposed_by: str = "PocTargetsSyncProposalGenerator"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_id": self.target_id,
            "current_status": self.current_status,
            "proposed_status": self.proposed_status,
            "delta_type": self.delta_type,
            "justification": self.justification,
            "required_claim_ids": self.required_claim_ids,
            "evidence_package_refs": self.evidence_package_refs,
            "limitations": self.limitations,
            "proposed_by": self.proposed_by,
        }


@dataclass
class SyncProposal:
    """
    Proposed poc-targets.yaml delta.
    NEVER applied directly — must be reviewed and approved before any file is changed.
    """
    proposal_id: str
    generated_at: str
    source_graph_hash: str
    entries: List[SyncDeltaEntry] = field(default_factory=list)
    prohibition_note: str = (
        "PROHIBITION: This proposal must NOT be applied directly to poc-targets.yaml. "
        "It must be reviewed by a human or Supervisor before any authority file is changed. "
        "PocTargetField nodes are updated only through approved CapabilityDelta sync. "
        "Invariant 8: PocTargetField updated only via proposed sync delta, never direct mutation."
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "generated_at": self.generated_at,
            "source_graph_hash": self.source_graph_hash,
            "prohibition_note": self.prohibition_note,
            "entry_count": len(self.entries),
            "entries": [e.to_dict() for e in self.entries],
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )


class PocTargetsSyncProposalGenerator:
    """
    Generates a proposed poc-targets.yaml delta from proof graph state.
    NEVER modifies poc-targets.yaml or any authority file.
    """

    PROOF_STATUS_TO_POC_STATUS = {
        "READY_FOR_POC": "poc_ready",
        "PARTIAL_WITH_CAVEATS": "partial_poc_ready",
        "BLOCKED_MISSING_PROOF": "not_ready",
        "BLOCKED_STALE": "stale",
        "BLOCKED_OVERCLAIM": "overclaim_blocked",
        "NOT_STARTED": "not_started",
        "STRETCH_TARGET": "stretch_not_ready",
    }

    def __init__(self, store: GraphStore):
        self.store = store

    def generate(self, readiness_result: PocReadinessResult) -> SyncProposal:
        graph_hash = self.store.compute_graph_hash()
        proposal_id = f"sync-proposal:{graph_hash[:12]}:{_now_iso()}"

        proposal = SyncProposal(
            proposal_id=proposal_id,
            generated_at=_now_iso(),
            source_graph_hash=graph_hash,
        )

        for target in readiness_result.targets:
            entry = self._build_entry(target)
            proposal.entries.append(entry)

        return proposal

    def _build_entry(self, target: TargetReadiness) -> SyncDeltaEntry:
        proposed_status = self.PROOF_STATUS_TO_POC_STATUS.get(
            target.verdict, "unknown"
        )

        # Get current status from PocTargetField node (imported, not authoritative)
        ptf_nodes = [
            n for n in self.store.nodes_by_type("PocTargetField")
            if n.metadata.get("target_id") == target.target_id
        ]
        current_status = (
            ptf_nodes[0].metadata.get("original_status", "unknown")
            if ptf_nodes else "unknown"
        )

        # Determine delta type
        if current_status == proposed_status:
            delta_type = "NO_CHANGE"
        elif current_status == "unknown" or current_status == "not_started":
            delta_type = "SET"
        elif proposed_status in ("poc_ready", "partial_poc_ready"):
            delta_type = "UPGRADE"
        else:
            delta_type = "DOWNGRADE"

        # Collect supporting claim IDs
        claims = [
            c for c in self.store.nodes_by_type("CapabilityClaim")
            if c.metadata.get("product_id") == target.target_id
            and c.status in ("accepted_for_poc", "accepted_with_limitations")
        ]
        claim_ids = sorted(c.node_id for c in claims)

        # Collect evidence package refs
        evpkg_refs = []
        for claim in claims:
            evidence_nodes = self.store.get_targets(claim.node_id, "evidenced_by")
            for ev in evidence_nodes:
                if ev.node_id not in evpkg_refs:
                    evpkg_refs.append(ev.node_id)

        # Build justification
        justification = (
            f"Proof graph state: {target.verdict}. "
            f"Proven capabilities: {sorted(target.proven_capabilities)}. "
            f"Missing capabilities: {target.missing_capabilities}."
        )
        if target.override_notes:
            justification += " Override notes: " + "; ".join(target.override_notes)

        limitations = []
        if target.verdict == "PARTIAL_WITH_CAVEATS":
            limitations.append("Accepted_with_limitations — not full poc_ready")
        if target.is_stretch_target:
            limitations.append("Stretch target — not required for POC gate")

        return SyncDeltaEntry(
            target_id=target.target_id,
            current_status=current_status,
            proposed_status=proposed_status,
            delta_type=delta_type,
            justification=justification,
            required_claim_ids=claim_ids,
            evidence_package_refs=sorted(evpkg_refs),
            limitations=limitations,
        )


def generate_sync_proposal(
    store: GraphStore, readiness_result: PocReadinessResult
) -> SyncProposal:
    """Convenience function: generate poc-targets sync proposal. Never applies directly."""
    generator = PocTargetsSyncProposalGenerator(store)
    return generator.generate(readiness_result)
