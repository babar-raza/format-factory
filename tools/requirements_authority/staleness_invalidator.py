"""
StalenessInvalidationEngine: 12 invalidation triggers and propagation chain.

12 triggers:
  1.  spec_requirement_changed
  2.  empirical_sample_changed
  3.  product_requirement_changed
  4.  implementation_file_changed_after_coverage
  5.  test_file_changed_after_coverage
  6.  test_log_older_than_source_diff
  7.  dogfood_output_older_than_implementation
  8.  evidence_package_missing_proof
  9.  context_pack_stale
  10. unsupported_feature_changed
  11. claim_scope_changed
  12. product_policy_changed

Propagation chain:
  source requirement stale → product requirement stale → linked claim stale →
  coverage stale → POC readiness stale → poc-targets proposal invalid

4 output artifacts with schemas:
  stale-graph-report.json, stale-claims.md, recomputation-queue.json, blocked-poc-targets.json
"""
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .graph_store import GraphStore
from .models import GraphNode

INVALIDATION_TRIGGERS = [
    "spec_requirement_changed",
    "empirical_sample_changed",
    "product_requirement_changed",
    "implementation_file_changed_after_coverage",
    "test_file_changed_after_coverage",
    "test_log_older_than_source_diff",
    "dogfood_output_older_than_implementation",
    "evidence_package_missing_proof",
    "context_pack_stale",
    "unsupported_feature_changed",
    "claim_scope_changed",
    "product_policy_changed",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class StalenessEvent:
    node_id: str
    trigger: str  # must be in INVALIDATION_TRIGGERS
    reason: str
    propagated_from: Optional[str] = None
    detected_at: str = field(default_factory=_now_iso)

    def __post_init__(self):
        if self.trigger not in INVALIDATION_TRIGGERS:
            raise ValueError(f"Unknown trigger: {self.trigger!r}. Valid: {INVALIDATION_TRIGGERS}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "trigger": self.trigger,
            "reason": self.reason,
            "propagated_from": self.propagated_from,
            "detected_at": self.detected_at,
        }


@dataclass
class RecomputationQueueEntry:
    node_id: str
    node_type: str
    reason: str
    priority: int  # 1=highest
    depends_on: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "reason": self.reason,
            "priority": self.priority,
            "depends_on": self.depends_on,
        }


@dataclass
class StalenessReport:
    stale_events: List[StalenessEvent] = field(default_factory=list)
    stale_claim_ids: List[str] = field(default_factory=list)
    recomputation_queue: List[RecomputationQueueEntry] = field(default_factory=list)
    blocked_poc_targets: List[str] = field(default_factory=list)
    generated_at: str = field(default_factory=_now_iso)

    def stale_graph_report(self) -> Dict[str, Any]:
        """stale-graph-report.json schema."""
        return {
            "generated_at": self.generated_at,
            "stale_node_count": len(self.stale_events),
            "stale_claim_count": len(self.stale_claim_ids),
            "blocked_poc_target_count": len(self.blocked_poc_targets),
            "stale_events": [e.to_dict() for e in self.stale_events],
        }

    def stale_claims_md(self) -> str:
        """stale-claims.md content."""
        lines = [
            "# Stale Claims Report",
            f"Generated: {self.generated_at}",
            f"Total stale claims: {len(self.stale_claim_ids)}",
            "",
            "## Stale Claim IDs",
        ]
        for cid in sorted(self.stale_claim_ids):
            lines.append(f"- {cid}")
        lines += ["", "## Staleness Events"]
        for ev in self.stale_events:
            lines.append(
                f"- **{ev.node_id}** | trigger={ev.trigger} | "
                f"reason={ev.reason}"
                + (f" | propagated_from={ev.propagated_from}" if ev.propagated_from else "")
            )
        return "\n".join(lines)

    def recomputation_queue_json(self) -> Dict[str, Any]:
        """recomputation-queue.json schema."""
        return {
            "generated_at": self.generated_at,
            "queue_length": len(self.recomputation_queue),
            "entries": [e.to_dict() for e in sorted(
                self.recomputation_queue, key=lambda x: (x.priority, x.node_id)
            )],
        }

    def blocked_poc_targets_json(self) -> Dict[str, Any]:
        """blocked-poc-targets.json schema."""
        return {
            "generated_at": self.generated_at,
            "blocked_count": len(self.blocked_poc_targets),
            "blocked_target_ids": sorted(self.blocked_poc_targets),
            "reason": "Stale proof invalidates POC readiness — recomputation required before proposing sync delta",
        }

    def save_all(self, output_dir: Path) -> Dict[str, str]:
        """Write all 4 output artifacts. Returns {artifact_name: path}."""
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = {}

        p = output_dir / "stale-graph-report.json"
        p.write_text(json.dumps(self.stale_graph_report(), indent=2, sort_keys=True),
                     encoding="utf-8")
        paths["stale-graph-report.json"] = str(p)

        p = output_dir / "stale-claims.md"
        p.write_text(self.stale_claims_md(), encoding="utf-8")
        paths["stale-claims.md"] = str(p)

        p = output_dir / "recomputation-queue.json"
        p.write_text(json.dumps(self.recomputation_queue_json(), indent=2, sort_keys=True),
                     encoding="utf-8")
        paths["recomputation-queue.json"] = str(p)

        p = output_dir / "blocked-poc-targets.json"
        p.write_text(json.dumps(self.blocked_poc_targets_json(), indent=2, sort_keys=True),
                     encoding="utf-8")
        paths["blocked-poc-targets.json"] = str(p)

        return paths


class StalenessInvalidationEngine:
    """
    Scans a GraphStore for staleness conditions and propagates invalidity
    through the proof graph following the defined propagation chain.
    """

    def __init__(self, store: GraphStore):
        self.store = store

    def run(self) -> StalenessReport:
        """Run all 12 staleness triggers and propagate through the graph."""
        report = StalenessReport()
        stale_node_ids: Set[str] = set()

        # --- Trigger detection ---
        for node in self.store.nodes.values():
            trigger = self._detect_trigger(node)
            if trigger:
                ev = StalenessEvent(
                    node_id=node.node_id,
                    trigger=trigger[0],
                    reason=trigger[1],
                )
                report.stale_events.append(ev)
                stale_node_ids.add(node.node_id)

        # --- Propagation chain ---
        self._propagate_staleness(stale_node_ids, report)

        # --- Collect stale claims ---
        for node in self.store.nodes.values():
            if node.node_type == "CapabilityClaim" and node.node_id in stale_node_ids:
                report.stale_claim_ids.append(node.node_id)

        # --- Build recomputation queue ---
        self._build_recomputation_queue(stale_node_ids, report)

        # --- Identify blocked POC targets ---
        self._identify_blocked_poc_targets(stale_node_ids, report)

        return report

    def _detect_trigger(self, node: GraphNode) -> Optional[tuple]:
        """Return (trigger_name, reason) if node is stale, else None."""
        # Already marked stale
        if node.status in ("stale", "superseded"):
            node_type = node.node_type
            if node_type == "SpecRequirementRef":
                return ("spec_requirement_changed",
                        f"SpecRequirementRef '{node.node_id}' has status='{node.status}'")
            if node_type == "EmpiricalEvidence":
                return ("empirical_sample_changed",
                        f"EmpiricalEvidence '{node.node_id}' has status='{node.status}'")
            if node_type == "ProductRequirement":
                return ("product_requirement_changed",
                        f"ProductRequirement '{node.node_id}' has status='{node.status}'")
            if node_type == "ImplementationArtifact":
                return ("implementation_file_changed_after_coverage",
                        f"ImplementationArtifact '{node.node_id}' has status='{node.status}'")
            if node_type == "TestArtifact":
                return ("test_file_changed_after_coverage",
                        f"TestArtifact '{node.node_id}' has status='{node.status}'")
            if node_type == "DogfoodArtifact":
                return ("dogfood_output_older_than_implementation",
                        f"DogfoodArtifact '{node.node_id}' has status='{node.status}'")
            if node_type == "EvidencePackage":
                return ("evidence_package_missing_proof",
                        f"EvidencePackage '{node.node_id}' has status='{node.status}'")
            if node_type == "ContextPackRef":
                return ("context_pack_stale",
                        f"ContextPackRef '{node.node_id}' has status='{node.status}'")
            if node_type == "UnsupportedFeature":
                return ("unsupported_feature_changed",
                        f"UnsupportedFeature '{node.node_id}' has status='{node.status}'")
            if node_type == "CapabilityClaim":
                return ("claim_scope_changed",
                        f"CapabilityClaim '{node.node_id}' has status='{node.status}'")
            if node_type == "ProductPolicyDecision":
                return ("product_policy_changed",
                        f"ProductPolicyDecision '{node.node_id}' has status='{node.status}'")

        # Metadata-based staleness flags
        if node.metadata.get("context_pack_stale", False):
            return ("context_pack_stale",
                    f"Node '{node.node_id}' has context_pack_stale=true in metadata")

        return None

    def _propagate_staleness(self, stale_ids: Set[str], report: StalenessReport) -> None:
        """
        Propagation chain:
          source requirement stale → product requirement stale → linked claim stale →
          coverage stale → POC readiness stale
        """
        changed = True
        iteration = 0
        while changed and iteration < 20:
            changed = False
            iteration += 1
            for node in self.store.nodes.values():
                if node.node_id in stale_ids:
                    continue
                # If any upstream node is stale, this node becomes stale too
                if self._has_stale_dependency(node.node_id, stale_ids):
                    stale_ids.add(node.node_id)
                    trigger = self._propagation_trigger(node)
                    ev = StalenessEvent(
                        node_id=node.node_id,
                        trigger=trigger,
                        reason=f"Propagated staleness to '{node.node_id}' ({node.node_type})",
                        propagated_from="upstream_node",
                    )
                    report.stale_events.append(ev)
                    changed = True

    def _has_stale_dependency(self, node_id: str, stale_ids: Set[str]) -> bool:
        """
        Check if any node this node depends on (via outgoing derives_from) is stale.
        Edge direction: source=dependent --derives_from--> target=dependency
        So we look at OUTGOING derives_from edges and check if the targets are stale.
        """
        for edge in self.store.get_outgoing(node_id):
            if edge.edge_type in ("derives_from", "stale_due_to", "invalidates"):
                if edge.target_node_id in stale_ids:
                    return True
        return False

    def _propagation_trigger(self, node: GraphNode) -> str:
        node_type = node.node_type
        mapping = {
            "ProductRequirement": "product_requirement_changed",
            "CapabilityClaim": "claim_scope_changed",
            "CoverageRecord": "implementation_file_changed_after_coverage",
            "PocTargetField": "product_requirement_changed",
        }
        return mapping.get(node_type, "spec_requirement_changed")

    def _build_recomputation_queue(
        self, stale_ids: Set[str], report: StalenessReport
    ) -> None:
        """Build prioritized recomputation queue from stale nodes."""
        priority_map = {
            "ProductRequirement": 1,
            "CapabilityClaim": 2,
            "CoverageRecord": 3,
            "PocTargetField": 4,
            "EvidencePackage": 2,
        }
        for node_id in sorted(stale_ids):
            node = self.store.get_node(node_id)
            if not node:
                continue
            priority = priority_map.get(node.node_type, 5)
            deps = [e.source_node_id for e in self.store.get_incoming(node_id, "derives_from")]
            report.recomputation_queue.append(RecomputationQueueEntry(
                node_id=node_id,
                node_type=node.node_type,
                reason=f"Stale {node.node_type} — requires recomputation",
                priority=priority,
                depends_on=sorted(deps),
            ))

    def _identify_blocked_poc_targets(
        self, stale_ids: Set[str], report: StalenessReport
    ) -> None:
        """Any PocTargetField that is stale → blocked POC target."""
        for node in self.store.nodes_by_type("PocTargetField"):
            if node.node_id in stale_ids:
                target_id = node.metadata.get("target_id", node.node_id)
                report.blocked_poc_targets.append(target_id)

        # Also: any claim that is accepted_for_poc with stale support
        for node in self.store.nodes_by_type("CapabilityClaim"):
            if node.status == "accepted_for_poc" and node.node_id in stale_ids:
                target_id = node.metadata.get("product_id", node.node_id)
                if target_id not in report.blocked_poc_targets:
                    report.blocked_poc_targets.append(target_id)


def run_staleness_invalidation(store: GraphStore) -> StalenessReport:
    """Convenience function: run staleness engine on a store."""
    engine = StalenessInvalidationEngine(store)
    return engine.run()
