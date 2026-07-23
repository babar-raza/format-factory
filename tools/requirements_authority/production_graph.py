"""Content-addressed production proof graph.

This module is the production projection over the existing canonical graph
store.  It deliberately has no mutable readiness field: readiness is derived
from live, digest-bound proof every time it is requested.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .graph_store import GraphStore
from .models import GraphEdge, GraphNode


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PromotionDecision:
    format_id: str
    state: str
    unmet_obligations: tuple[str, ...]
    invalidated_nodes: tuple[str, ...]
    reasons: tuple[str, ...]


class ProductionProofGraph:
    """Build and evaluate digest-complete proof in a :class:`GraphStore`."""

    def __init__(self, store: GraphStore | None = None):
        self.store = store or GraphStore()

    def add_content_node(
        self,
        node_type: str,
        identity: str,
        payload: Mapping[str, Any],
        *,
        input_digests: Mapping[str, str] | None = None,
        status: str | None = None,
    ) -> GraphNode:
        inputs = dict(sorted((input_digests or {}).items()))
        material = {
            "node_type": node_type,
            "identity": identity,
            "payload": payload,
            "input_digests": inputs,
        }
        digest = content_digest(material)
        node = GraphNode(
            node_id=f"{node_type}:{identity}:{digest[:20]}",
            node_type=node_type,
            label=identity,
            status=status,
            metadata={
                "identity": identity,
                "payload": dict(payload),
                "input_digests": inputs,
                "content_digest": digest,
            },
        )
        self.store.add_node(node)
        return node

    def add_dependency(
        self,
        dependent: GraphNode,
        dependency: GraphNode,
        *,
        edge_type: str = "depends_on",
    ) -> GraphEdge:
        material = {
            "edge_type": edge_type,
            "source": dependent.node_id,
            "target": dependency.node_id,
        }
        edge = GraphEdge(
            edge_id=f"{edge_type}:{content_digest(material)[:24]}",
            edge_type=edge_type,
            source_node_id=dependent.node_id,
            target_node_id=dependency.node_id,
        )
        self.store.add_edge(edge)
        return edge

    def validate_content_closure(self) -> list[str]:
        errors: list[str] = []
        for edge in self.store.dangling_edges():
            errors.append(f"dangling edge {edge.edge_id}")
        for node in self.store.nodes.values():
            metadata = node.metadata
            if "content_digest" not in metadata:
                # Legacy nodes are historical inputs and cannot become current
                # proof merely by being present.
                continue
            material = {
                "node_type": node.node_type,
                "identity": metadata.get("identity"),
                "payload": metadata.get("payload", {}),
                "input_digests": metadata.get("input_digests", {}),
            }
            actual = content_digest(material)
            if actual != metadata["content_digest"]:
                errors.append(f"content digest mismatch for {node.node_id}")
        return sorted(errors)

    def invalidated_nodes(
        self, current_identity_digests: Mapping[str, str]
    ) -> set[str]:
        """Return directly stale nodes and every node that depends on them."""
        invalid: set[str] = set()
        for node in self.store.nodes.values():
            inputs = node.metadata.get("input_digests", {})
            if not isinstance(inputs, dict):
                continue
            for identity, recorded in inputs.items():
                current = current_identity_digests.get(identity)
                if current is None or current != recorded:
                    invalid.add(node.node_id)
                    break

        changed = True
        while changed:
            changed = False
            for edge in self.store.edges:
                if edge.edge_type != "depends_on":
                    continue
                if edge.target_node_id in invalid and edge.source_node_id not in invalid:
                    invalid.add(edge.source_node_id)
                    changed = True
        return invalid

    def compute_promotion(
        self,
        format_id: str,
        *,
        current_identity_digests: Mapping[str, str],
    ) -> PromotionDecision:
        invalid = self.invalidated_nodes(current_identity_digests)
        errors = self.validate_content_closure()
        relevant = [
            node
            for node in self.store.nodes.values()
            if node.metadata.get("payload", {}).get("format_id") == format_id
        ]
        if invalid.intersection(node.node_id for node in relevant) or errors:
            return PromotionDecision(
                format_id,
                "INVALIDATED",
                (),
                tuple(sorted(invalid)),
                tuple(errors or ["one or more proof inputs changed"]),
            )

        obligations = [
            node
            for node in relevant
            if node.node_type == "NormativeObligation"
            and node.metadata.get("payload", {}).get("level") == "MUST"
        ]
        authorities = [node for node in relevant if node.node_type == "AuthorityArtifact"]
        sources = [node for node in relevant if node.node_type == "SourceSymbol"]
        packages = [node for node in relevant if node.node_type == "BuiltPackage"]
        installed = [node for node in relevant if node.node_type == "InstalledPackageResult"]
        releases = [node for node in relevant if node.node_type == "ReleaseArtifact"]

        unmet: list[str] = []
        for obligation in obligations:
            results = [
                node
                for edge in self.store.get_incoming(obligation.node_id, "verified_by")
                if (node := self.store.get_node(edge.source_node_id)) is not None
                and node.node_type in {"ExecutedTestResult", "ExternalOracleResult"}
                and node.metadata.get("payload", {}).get("outcome") == "PASS"
                and node.metadata.get("payload", {}).get("executed") is True
            ]
            obligation_kind = obligation.metadata.get("payload", {}).get("kind", "positive")
            required_polarity = "negative" if obligation_kind == "rejection" else "positive"
            if not any(
                result.metadata.get("payload", {}).get("polarity", "positive")
                == required_polarity
                for result in results
            ):
                unmet.append(obligation.metadata.get("identity", obligation.node_id))

        if not authorities or any(
            node.metadata.get("payload", {}).get("acquired") is not True
            for node in authorities
        ):
            state = "UNASSESSED"
            reasons = ("pinned authority artifacts are incomplete",)
        elif not obligations:
            state = "CONTRACT_READY"
            reasons = ("no mandatory obligations compiled",)
        elif sources and not unmet:
            state = "IMPLEMENTATION_VERIFIED"
            reasons = ()
        elif sources:
            state = "IMPLEMENTATION_IN_PROGRESS"
            reasons = ("mandatory obligations lack executed proof",)
        else:
            state = "CONTRACT_READY"
            reasons = ("no source symbols are bound to the contract",)

        if state == "IMPLEMENTATION_VERIFIED" and packages and installed:
            state = "RELEASE_CANDIDATE"
        if state == "RELEASE_CANDIDATE" and releases:
            state = "RELEASED"

        return PromotionDecision(
            format_id,
            state,
            tuple(sorted(unmet)),
            (),
            reasons,
        )

    def graph_digest(self) -> str:
        return self.store.compute_graph_hash()

    def add_dependencies(
        self, dependent: GraphNode, dependencies: Iterable[GraphNode]
    ) -> None:
        for dependency in dependencies:
            self.add_dependency(dependent, dependency)
