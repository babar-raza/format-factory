"""
Data models for the Canonical Capability Proof Graph.

The legacy POC vocabulary remains readable, while the production vocabulary
binds authorities, obligations, source, executed evidence, packages, and
release artifacts in the same graph.  The production types are additive so
historical graphs can be migrated without being mistaken for current proof.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


# ── Node type enum values ──────────────────────────────────────────────────────
NODE_TYPES = [
    "ProductRequirement", "CapabilityClaim", "ImplementationArtifact",
    "TestArtifact", "ExampleArtifact", "DogfoodArtifact", "EvidencePackage",
    "UnsupportedFeature", "EmpiricalEvidence", "SpecRequirementRef",
    "ProductPolicyDecision", "ContextPackRef", "CoverageRecord",
    "CapabilityDelta", "PocTargetField", "StreamHandoff",
    "UsageRecord", "StalenessEvent",
    # Production proof vocabulary.
    "AuthorityArtifact", "NormativeObligation", "PublicCapability",
    "SourceSymbol", "CorpusArtifact", "ExecutedTestResult",
    "ExternalOracleResult", "BuiltPackage", "InstalledPackageResult",
    "QualityResult", "Certification", "Promotion", "ReleaseArtifact",
]

# ── Edge type enum values ──────────────────────────────────────────────────────
EDGE_TYPES = [
    "derives_from", "claims_support_for", "implemented_by", "tested_by",
    "exemplified_by", "dogfooded_by", "evidenced_by", "limited_by",
    "blocked_by", "supersedes", "invalidates", "proposed_by",
    "accepted_by", "syncs_to", "consumed_by", "stale_due_to",
    "narrows", "broadens", "conflicts_with",
    # Production proof relationships.
    "defines", "satisfies", "depends_on", "verified_by", "produced_by",
    "packaged_as", "installed_as", "certifies", "promotes", "released_as",
]

PRODUCTION_PROMOTION_STATES = [
    "UNASSESSED",
    "CONTRACT_READY",
    "IMPLEMENTATION_IN_PROGRESS",
    "IMPLEMENTATION_VERIFIED",
    "RELEASE_CANDIDATE",
    "RELEASED",
    "INVALIDATED",
]

# ── Claim status progression ───────────────────────────────────────────────────
CLAIM_STATUSES = [
    "candidate", "requirement_linked", "implementation_present",
    "tests_present", "examples_present", "dogfood_present",
    "coverage_validated", "accepted_for_poc", "accepted_with_limitations",
    "stale", "rejected", "blocked", "superseded",
]

# ── Proof sufficiency levels (ordered) ────────────────────────────────────────
PROOF_LEVELS = [
    "NO_PROOF", "REQUIREMENT_ONLY", "IMPLEMENTATION_ONLY", "TESTED",
    "EXAMPLED", "DOGFOODED", "COVERAGE_VALIDATED",
    "ACCEPTED_FOR_POC", "ACCEPTED_WITH_LIMITATIONS", "REJECTED_OR_BLOCKED",
]

# ── Operations ─────────────────────────────────────────────────────────────────
OPERATIONS = [
    "load", "parse", "inspect", "edit", "save", "write",
    "export", "import", "roundtrip", "validate", "package", "dogfood",
]

# ── Directions ─────────────────────────────────────────────────────────────────
DIRECTIONS = [
    "read_only", "write_only", "read_write",
    "export_only", "import_only", "transform",
]

# ── Fidelity values ────────────────────────────────────────────────────────────
FIDELITY_VALUES = [
    "structure_only", "content_only", "metadata_only",
    "formatting_partial", "formatting_preserved", "lossless",
    "lossy", "declared_limited",
]

# ── Supervisor decision values ─────────────────────────────────────────────────
SUPERVISOR_DECISIONS = [
    "ACCEPT_PRODUCT_PROGRESS", "ACCEPT_WITH_LIMITATIONS",
    "REJECT_OVERCLAIM", "BLOCK_MISSING_DOGFOOD",
    "BLOCK_MISSING_REQUIREMENT", "BLOCK_STALE_PROOF",
    "CONTINUE_MAINSTREAM_WITH_GAP_QUEUE", "CONTINUE_WITH_REROUTE",
    "NEEDS_POLICY_DECISION",
]

# ── POC targets ────────────────────────────────────────────────────────────────
POC_TARGETS = ["fods", "fodt", "netpbm-net", "zst", "netpbm-py", "sylk", "dif", "gnumeric"]

# Netpbm must be retained; SVG must not replace Netpbm
REQUIRED_TARGETS = {"fods", "fodt", "netpbm-net", "zst", "netpbm-py", "sylk"}
PROHIBITED_REPLACEMENTS = {"svg": "netpbm-net"}  # SVG must not replace Netpbm


@dataclass
class GraphNode:
    """
    A node in the Canonical Capability Proof Graph.

    Supports both:
    - Flat field access: node.status, node.label, node.metadata
    - JSONL serialization via to_dict() / from_dict()
    """
    node_id: str
    node_type: str
    label: str = ""
    status: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""

    # Legacy compat aliases (kept for round-trip with older JSONL files)
    # recorded_at is stored in metadata["recorded_at"] if present

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "node_id": self.node_id,
            "node_type": self.node_type,
        }
        if self.label:
            d["label"] = self.label
        if self.status is not None:
            d["status"] = self.status
        if self.created_at:
            d["created_at"] = self.created_at
        if self.metadata:
            d["metadata"] = self.metadata
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "GraphNode":
        # Support both new-style (metadata dict) and old-style (flat fields)
        metadata = d.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}

        # Migrate old flat fields into metadata if not already present
        _flat_fields = [
            "format_id", "product_id", "operation", "direction", "fidelity",
            "variant", "poc_scope", "dogfood_required", "description",
            "artifact_path", "checksum", "materialized", "severity",
            "feature_name", "decision_id", "import_status", "missing_proof_types",
            "ai_draft", "recorded_at", "imported_from", "target_id",
        ]
        for ff in _flat_fields:
            if ff in d and ff not in metadata:
                metadata[ff] = d[ff]

        created_at = (
            d.get("created_at")
            or d.get("recorded_at")
            or metadata.get("recorded_at", "")
        )
        label = d.get("label") or d.get("description") or ""

        return cls(
            node_id=d["node_id"],
            node_type=d["node_type"],
            label=label,
            status=d.get("status"),
            metadata=metadata,
            created_at=created_at,
        )


@dataclass
class GraphEdge:
    """An edge in the Canonical Capability Proof Graph."""
    edge_id: str
    edge_type: str
    source_node_id: str
    target_node_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "edge_id": self.edge_id,
            "edge_type": self.edge_type,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
        }
        if self.created_at:
            d["created_at"] = self.created_at
        if self.metadata:
            d["metadata"] = self.metadata
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "GraphEdge":
        metadata = d.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        # Migrate old recorded_at
        created_at = d.get("created_at") or d.get("recorded_at", "")
        return cls(
            edge_id=d["edge_id"],
            edge_type=d["edge_type"],
            source_node_id=d["source_node_id"],
            target_node_id=d["target_node_id"],
            metadata=metadata,
            created_at=created_at,
        )
