"""
Tests for GraphValidator: schema validation and 8 graph invariants.
Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-MWP-001
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from tools.requirements_authority.models import GraphNode, GraphEdge
from tools.requirements_authority.graph_store import GraphStore
from tools.requirements_authority.validators import GraphValidator, validate_graph


def _store_with_clean_fods_export():
    """Minimal clean FODS export claim — all invariants satisfied."""
    store = GraphStore()
    # Spec
    store.add_node(GraphNode("spec:fods:ods", "SpecRequirementRef",
                             label="ODF spec", status="accepted",
                             metadata={"product_id": "fods"}))
    # Requirement
    store.add_node(GraphNode("req:fods:export", "ProductRequirement",
                             label="FODS req", status="accepted",
                             metadata={"product_id": "fods"}))
    store.add_edge(GraphEdge("e:req:spec", "derives_from", "req:fods:export", "spec:fods:ods"))

    # Claim
    store.add_node(GraphNode("claim:fods:export", "CapabilityClaim",
                             label="FODS export claim", status="accepted_for_poc",
                             metadata={"product_id": "fods", "operation": "export",
                                       "dogfood_required": True}))
    store.add_edge(GraphEdge("e:claim:req", "derives_from", "claim:fods:export", "req:fods:export"))

    # Artifacts
    store.add_node(GraphNode("impl:fods", "ImplementationArtifact", label="Impl",
                             status="candidate", metadata={}))
    store.add_node(GraphNode("test:fods", "TestArtifact", label="Test",
                             status="candidate", metadata={}))
    store.add_node(GraphNode("dogfood:fods", "DogfoodArtifact", label="Dogfood",
                             status="candidate", metadata={}))
    store.add_node(GraphNode("evpkg:fods", "EvidencePackage", label="Evidence",
                             status="candidate", metadata={}))

    store.add_edge(GraphEdge("e:impl", "implemented_by", "claim:fods:export", "impl:fods"))
    store.add_edge(GraphEdge("e:test", "tested_by", "claim:fods:export", "test:fods"))
    store.add_edge(GraphEdge("e:dogfood", "dogfooded_by", "claim:fods:export", "dogfood:fods"))
    store.add_edge(GraphEdge("e:evpkg", "evidenced_by", "claim:fods:export", "evpkg:fods"))
    return store


class TestSchemaValidation:
    def test_invalid_node_type(self):
        store = GraphStore()
        store.add_node(GraphNode("n:1", "InvalidType", label="Bad", status="candidate",
                                  metadata={}))
        result = validate_graph(store)
        assert not result.is_valid
        assert any("Unknown node_type" in e.message for e in result.errors)

    def test_edge_to_missing_node(self):
        store = GraphStore()
        store.add_node(GraphNode("n:1", "ProductRequirement", label="R", status="accepted",
                                  metadata={}))
        store.add_edge(GraphEdge("e:1", "derives_from", "n:1", "nonexistent"))
        result = validate_graph(store)
        assert not result.is_valid
        assert any("not found in nodes" in e.message for e in result.errors)

    def test_invalid_edge_type(self):
        store = GraphStore()
        store.add_node(GraphNode("n:1", "ProductRequirement", label="R", status="accepted",
                                  metadata={}))
        store.add_node(GraphNode("n:2", "CapabilityClaim", label="C", status="candidate",
                                  metadata={}))
        store.add_edge(GraphEdge("e:1", "made_up_edge_type", "n:1", "n:2"))
        result = validate_graph(store)
        assert not result.is_valid
        assert any("Unknown edge_type" in e.message for e in result.errors)


class TestInvariant1:
    def test_accepted_claim_without_requirement_fails(self):
        store = GraphStore()
        store.add_node(GraphNode("claim:1", "CapabilityClaim", label="C",
                                  status="accepted_for_poc", metadata={}))
        result = validate_graph(store)
        assert not result.is_valid
        assert any(e.invariant == 1 for e in result.errors)

    def test_accepted_claim_with_requirement_passes(self):
        store = _store_with_clean_fods_export()
        result = validate_graph(store)
        assert not any(e.invariant == 1 for e in result.errors)


class TestInvariant4:
    def test_accepted_with_limitations_without_unsupported_feature_fails(self):
        store = GraphStore()
        # Requirement + spec
        store.add_node(GraphNode("spec:1", "SpecRequirementRef", label="S", status="accepted",
                                  metadata={}))
        store.add_node(GraphNode("req:1", "ProductRequirement", label="R", status="accepted",
                                  metadata={}))
        store.add_edge(GraphEdge("e:r:s", "derives_from", "req:1", "spec:1"))
        # Claim with limitations but no UnsupportedFeature
        store.add_node(GraphNode("claim:1", "CapabilityClaim", label="C",
                                  status="accepted_with_limitations", metadata={}))
        store.add_edge(GraphEdge("e:c:r", "derives_from", "claim:1", "req:1"))
        store.add_node(GraphNode("impl:1", "ImplementationArtifact", label="I", status="candidate", metadata={}))
        store.add_node(GraphNode("test:1", "TestArtifact", label="T", status="candidate", metadata={}))
        store.add_node(GraphNode("evpkg:1", "EvidencePackage", label="E", status="candidate", metadata={}))
        store.add_edge(GraphEdge("e:impl", "implemented_by", "claim:1", "impl:1"))
        store.add_edge(GraphEdge("e:test", "tested_by", "claim:1", "test:1"))
        store.add_edge(GraphEdge("e:ev", "evidenced_by", "claim:1", "evpkg:1"))
        result = validate_graph(store)
        assert any(e.invariant == 4 for e in result.errors)


class TestInvariant6:
    def test_ai_draft_node_as_proof_fails(self):
        store = GraphStore()
        store.add_node(GraphNode("spec:1", "SpecRequirementRef", label="S", status="accepted",
                                  metadata={}))
        store.add_node(GraphNode("req:1", "ProductRequirement", label="R", status="accepted",
                                  metadata={}))
        store.add_edge(GraphEdge("e:r:s", "derives_from", "req:1", "spec:1"))
        store.add_node(GraphNode("claim:1", "CapabilityClaim", label="C",
                                  status="accepted_for_poc", metadata={"dogfood_required": False}))
        store.add_edge(GraphEdge("e:c:r", "derives_from", "claim:1", "req:1"))
        # ai_draft implementation
        store.add_node(GraphNode("impl:ai", "ImplementationArtifact", label="AI impl",
                                  status="candidate", metadata={"ai_draft": True}))
        store.add_node(GraphNode("test:1", "TestArtifact", label="T", status="candidate", metadata={}))
        store.add_node(GraphNode("evpkg:1", "EvidencePackage", label="E", status="candidate", metadata={}))
        store.add_edge(GraphEdge("e:impl", "implemented_by", "claim:1", "impl:ai"))
        store.add_edge(GraphEdge("e:test", "tested_by", "claim:1", "test:1"))
        store.add_edge(GraphEdge("e:ev", "evidenced_by", "claim:1", "evpkg:1"))
        result = validate_graph(store)
        assert any(e.invariant == 6 for e in result.errors)


class TestCleanGraphPasses:
    def test_clean_fods_export_no_invariant_errors(self):
        store = _store_with_clean_fods_export()
        result = validate_graph(store)
        invariant_errors = [e for e in result.errors if e.invariant > 0]
        assert not invariant_errors, f"Unexpected invariant errors: {invariant_errors}"
